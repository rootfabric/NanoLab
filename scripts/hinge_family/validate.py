"""Orchestration: digest gate -> strict parsing -> structural checks -> report.

Deterministic by construction: the report contains no wall-clock data, uses
sorted keys, fixed float rounding, and derives every number from the input
bytes and the frozen pins registry.
"""
from __future__ import annotations

import sys
from pathlib import Path

from .canonical import canonical_json
from .cadnano_design import Design, DesignError
from .oxdna_conf import ConfError, Configuration, configuration_facts
from .oxdna_topology import Topology, TopologyError, topology_facts
from .pins import PinsError, load_pins, variant_surface, verify_source_file
from .sim_input import SimInputError, check_preregistered, parse_sim_input

TOOL_REVISION = "HINGE-FAMILY-R1"

DEFAULT_SURFACE_ROLES = ("topology", "configuration", "design", "sim_input_cpu")


class ValidationOutcome:
    def __init__(self, report: dict, ok: bool):
        self.report = report
        self.ok = ok

    @property
    def text(self) -> str:
        return canonical_json(self.report)


def _run(pins_path: Path, source_dir: Path, variant: str) -> ValidationOutcome:
    report = {
        "tool_revision": TOOL_REVISION,
        "variant": variant,
        "registry_id": None,
        "source": None,
        "surface": None,
        "digest_verification": {},
        "checks": [],
        "observations": [],
        "facts": {},
    }

    def check(check_id: str, ok: bool, detail: str) -> bool:
        report["checks"].append({"id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail})
        return ok

    def observe(observe_id: str, detail) -> None:
        report["observations"].append({"id": observe_id, "detail": detail})

    # ---- pins registry (fail-closed) ----
    try:
        pins = load_pins(pins_path)
    except PinsError as exc:
        check("pins_registry_contract", False, str(exc))
        return ValidationOutcome(report, False)
    report["registry_id"] = pins["registry_id"]
    report["source"] = {k: pins["source"][k] for k in ("repository", "commit", "tree", "rights", "mode")}
    if not check("pins_registry_contract", True, "registry satisfies the fail-closed contract"):
        return ValidationOutcome(report, False)

    try:
        surface = variant_surface(pins, variant)
    except PinsError as exc:
        check("variant_registered", False, str(exc))
        return ValidationOutcome(report, False)
    report["surface"] = {role: surface[role] for role in DEFAULT_SURFACE_ROLES}
    check(
        "variant_registered",
        True,
        f"variant {variant} registered with role {surface['role']}",
    )

    # ---- digest gate ----
    digest_ok = True
    for role in DEFAULT_SURFACE_ROLES:
        rel = surface[role]
        entry = pins["files"][rel]
        result = verify_source_file(source_dir / Path(rel).name, entry)
        ok = result["size_ok"] and result["blob_sha1_ok"] and result["sha256_ok"] is not False
        if "read_error" in result:
            ok = False
        digest_ok = digest_ok and ok
        report["digest_verification"][role] = {
            "path": rel,
            "size_ok": result["size_ok"],
            "blob_sha1_ok": result["blob_sha1_ok"],
            "sha256_ok": result["sha256_ok"],
            "observed": result.get("observed", {}),
            "read_error": result.get("read_error"),
        }
    check(
        "source_digests_match_pins",
        digest_ok,
        "size, sha256 (where pinned) and git blob SHA-1 of every surface file match the frozen registry"
        if digest_ok
        else "at least one surface file deviates from the frozen registry (see digest_verification)",
    )
    if not digest_ok:
        return ValidationOutcome(report, False)

    all_ok = True

    # ---- topology ----
    try:
        topology = Topology.from_file(source_dir / Path(surface["topology"]).name)
        facts = topology_facts(topology)
        report["facts"]["topology"] = facts
        all_ok = check("topology_structure", True, "header/rows/base letters/strand runs/chain integrity all consistent") and all_ok
    except TopologyError as exc:
        all_ok = check("topology_structure", False, str(exc)) and all_ok
        return ValidationOutcome(report, all_ok)

    # ---- configuration ----
    try:
        conf = Configuration.from_file(source_dir / Path(surface["configuration"]).name)
        if len(conf.particles) != topology.nucleotides:
            raise ConfError(
                f"configuration has {len(conf.particles)} particles, topology declares {topology.nucleotides}"
            )
        orientation = conf.check_orientation()
        conf.check_positions_in_box()
        bonded = conf.bonded_distance_stats(topology)
        report["facts"]["configuration"] = configuration_facts(conf, orientation, bonded)
        all_ok = check("configuration_structure", True, "particle count matches topology; 15 finite columns; orientations unit+orthogonal; positions inside box") and all_ok
    except ConfError as exc:
        all_ok = check("configuration_structure", False, str(exc)) and all_ok
        return ValidationOutcome(report, all_ok)

    # ---- design ----
    try:
        design = Design.from_file(source_dir / Path(surface["design"]).name)
        design_facts = design.structural_facts()
        report["facts"]["design"] = design_facts
        if design_facts["total_bases"] != topology.nucleotides:
            raise DesignError(
                f"design has {design_facts['total_bases']} bases, topology declares {topology.nucleotides} nucleotides"
            )
        all_ok = check("design_structure", True, "vstrand routing bidirectionally consistent; path walk covers every used cell") and all_ok
        all_ok = check(
            "design_bases_equal_topology_nucleotides",
            True,
            f"design total bases {design_facts['total_bases']} == topology nucleotides {topology.nucleotides}",
        ) and all_ok
    except DesignError as exc:
        all_ok = check("design_structure", False, str(exc)) and all_ok

    # ---- sim input ----
    try:
        values = parse_sim_input((source_dir / Path(surface["sim_input_cpu"]).name).read_text(encoding="utf-8"))
        confirmed = check_preregistered(values)
        report["facts"]["sim_input"] = confirmed
        all_ok = check("sim_input_preregistered_values", True, "engine/model values machine-confirm E2-SETUP-R1 section 5 OBSERVED facts") and all_ok
    except (SimInputError, OSError) as exc:
        all_ok = check("sim_input_preregistered_values", False, str(exc)) and all_ok

    # ---- observations (facts recorded, not pass/fail) ----
    config_facts = report["facts"]["configuration"]
    bonded = config_facts["bonded_distances"]
    if "design" in report["facts"]:
        crossovers = report["facts"]["design"]["crossover_steps"]
        total_crossovers = crossovers["scaffold"] + crossovers["staple"]
        observe(
            "long_bonds_approx_design_crossover_steps",
            {
                "long_bond_count": bonded["long_bond_count"],
                "long_bond_threshold": bonded["long_bond_threshold"],
                "design_crossover_steps": total_crossovers,
                "note": (
                    "within-strand bonded distances beyond the threshold are numerically close to the "
                    "design crossover-step count; consistent with crossover-continuous chain encoding in "
                    "the author topology. Recorded as an observation, not an acceptance criterion."
                ),
            },
        )
        observe(
            "strand_count_correspondence_pending",
            {
                "design_paths": report["facts"]["design"]["scaffold_paths"] + report["facts"]["design"]["staple_paths"],
                "topology_strands": facts["strands"],
                "note": (
                    "exact design-path-to-topology-strand mapping is conversion-pipeline dependent and is "
                    "NOT decomposed in this revision; the author Init_Hinges pipeline is REFERENCE_ONLY and "
                    "the design carries no sequences. Assigned to the pre-E2 compatibility audit."
                ),
            },
        )
        observe("ssdna_runs", report["facts"]["design"]["ssdna_run_histogram"])
        observe(
            "ssdna_spring_layer_machine_check_inconclusive",
            "REPORTED spring layers (E2-SETUP-R1 section 7) cannot be attributed to specific ssDNA runs "
            "without the paper SI angle/geometry definitions; design name corroborates the 0-insertion side of variant 0b",
        )
    observe(
        "sim_input_defaults_to_74b",
        {
            "default_topology": report["facts"].get("sim_input", {}).get("default_topology"),
            "default_conf_file": report["facts"].get("sim_input", {}).get("default_conf_file"),
            "note": "the author CPU input points at 74b surfaces; running 0b requires pointing topology/conf at the 0b files - a substitution that E2-SETUP-R1 requires to be explicit, never silent",
        },
    )
    observe(
        "conf_column_semantics_interpretation",
        "columns 3:9 are two exact unit mutually orthogonal triples; columns 9:15 are bounded velocity-like triples; semantic labels follow oxDNA configuration conventions and await the pre-E2 engine-input check",
    )

    return ValidationOutcome(report, all_ok)


def run_validation(pins_path: Path, source_dir: Path, variant: str = "0b") -> ValidationOutcome:
    return _run(Path(pins_path), Path(source_dir), variant)


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m hinge_family",
        description=(
            "Digest-gated structural reproduction check for the Shi-Castro-Arya hinge family "
            "(REFERENCE_ONLY source; bytes stay outside Git)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("validate", help="validate one variant surface from a user-side source directory")
    run_parser.add_argument("--source-dir", required=True, help="directory holding the downloaded source files (flat names)")
    run_parser.add_argument("--variant", default="0b", help="registered variant to validate (default: 0b)")
    run_parser.add_argument("--pins", default=None, help="alternative pins registry JSON (default: bundled source_pins.json)")
    run_parser.add_argument("--report", default=None, help="write the canonical JSON report to this path ('-' for stdout)")
    args = parser.parse_args(argv)

    pins_path = Path(args.pins) if args.pins else Path(__file__).resolve().parent / "source_pins.json"
    try:
        outcome = run_validation(pins_path, Path(args.source_dir), args.variant)
    except PinsError as exc:
        print(f"pins error: {exc}", file=sys.stderr)
        return 2
    if args.report and args.report != "-":
        Path(args.report).write_text(outcome.text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(outcome.text)
    return 0 if outcome.ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
