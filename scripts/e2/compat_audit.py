"""Compatibility audit: author sim-input vs pinned engine option registry.

Machine-check of every key of an oxDNA input file against the frozen option
registry extracted from the pinned engine documentation
(``engine_options.json``, oxDNA @ 00dc7fb9). Unknown keys are gaps, never
warnings. The preregistered E2-SETUP-R1 values are confirmed on every run.

Byte-deterministic JSON report; no wall-clock data.
"""
from __future__ import annotations

import argparse
import json
import os

try:
    from .canonical import canonical_json
    from .digests import sha256_text
except ImportError:
    from canonical import canonical_json
    from digests import sha256_text

from hinge_family.sim_input import check_preregistered, parse_sim_input

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "engine_options.json")

# Keys the pinned engine demonstrably consumes but that are absent from
# input_options.md @ 00dc7fb9 (registry documentation gap, U-compat-1):
# both are used by the author's pinned pro_CPU.in (preregistered OBSERVED
# facts, NL0-001) and by the accepted E1 fixture runs against this engine
# build (E1-R1 evidence).
KNOWN_UNDOCUMENTED = {
    "topology": "standard input key consumed by the engine (author pro_CPU.in, E1-R1 fixture runs); absent from input_options.md @ 00dc7fb9 (U-compat-1)",
    "energy_file": "standard input key consumed by the engine (author pro_CPU.in, E1-R1 fixture runs); absent from input_options.md @ 00dc7fb9 (U-compat-1)",
}

FORCE_SEMANTICS = {
    "external_forces": (
        "PRODUCTION_EXTERNAL_FORCES: when true, an external forces file is loaded "
        "and applied during the run (per pinned engine docs); any per-force init/end "
        "scoping inside that file is an open question (U-rest-1)"
    ),
    "external_forces_file": "PRODUCTION companion key of external_forces",
}


def load_registry(path: str = REGISTRY_PATH) -> dict:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return json.load(handle)


def audit(text: str, registry: dict) -> dict:
    values = parse_sim_input(text)
    try:
        pre = check_preregistered(values)
        preregistered_status = "CONFIRMED"
        preregistered_error = None
    except Exception as exc:  # SimInputError or subclass mismatch
        pre = {"confirmed_keys": [], "error": str(exc)}
        preregistered_status = "MISMATCH"
        preregistered_error = str(exc)

    options = registry["options"]
    keys = {}
    unknown = []
    undocumented = []
    for key in sorted(values):
        if key in options:
            keys[key] = {
                "value": values[key],
                "known": True,
                "documented": True,
                "optional": options[key]["optional"],
                "section": options[key]["section"],
            }
        elif key in KNOWN_UNDOCUMENTED:
            undocumented.append(key)
            keys[key] = {"value": values[key], "known": True, "documented": False, "note": KNOWN_UNDOCUMENTED[key]}
        else:
            unknown.append(key)
            keys[key] = {"value": values[key], "known": False}

    force_related = {}
    for key in sorted(values):
        if key in FORCE_SEMANTICS:
            force_related[key] = {"value": values[key], "semantics": FORCE_SEMANTICS[key]}
        elif any(token in key.lower() for token in ("trap", "force")) and key not in FORCE_SEMANTICS:
            force_related[key] = {
                "value": values[key],
                "semantics": "SUSPECT (name contains 'trap'/'force'; not in frozen semantics table; classify manually)",
            }

    external_active = values.get("external_forces", "0").lower() in ("1", "true", "yes")
    if external_active:
        conclusion = "EXTERNAL_FORCES_ACTIVE (production input declares external forces; inspect the forces file before any E2 run)"
    elif force_related:
        conclusion = "FORCE_RELATED_KEYS_PRESENT (no active external_forces switch, but force-named keys present)"
    else:
        conclusion = "NO_EXTERNAL_FORCES_DECLARED"

    return {
        "schema_version": 1,
        "kind": "sim_input_compat_audit",
        "engine_commit": registry["engine_commit"],
        "registry_source_sha256": registry["source_sha256"],
        "registry_option_count": registry["option_count"],
        "input_sha256": sha256_text(text),
        "input_keys_total": len(values),
        "keys": keys,
        "unknown_keys": unknown,
        "undocumented_keys": undocumented,
        "force_related_keys": force_related,
        "preregistered_values": {
            "status": preregistered_status,
            "confirmed_keys": pre.get("confirmed_keys", []),
            "error": preregistered_error,
            "default_topology": values.get("topology"),
            "default_conf_file": values.get("conf_file"),
        },
        "conclusion": conclusion,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="audit an oxDNA input file against the pinned engine registry")
    parser.add_argument("input_path")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    with open(args.input_path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    report = audit(text, load_registry())
    rendered = canonical_json(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    print(rendered, end="")
    return 0 if not report["unknown_keys"] and report["preregistered_values"]["status"] == "CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
