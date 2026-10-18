"""AssemblySpec v1 — executable contract + minimal fail-closed two-component assembler.

WO-PREP-S17-R3 stage C. First executable implementation of the AssemblySpec v1
requirements in ``docs/DATA_CONTRACTS.md`` (AssemblySpec v1 row) and
``docs/control/LITERATURE_TO_MECHANISM_ROUTE_R1.md``.

Scope (narrow by design):

* exactly **two** DNA components per assembly (driver + follower roles);
* one supported connection chemistry: ``SS_DNA_OVERHANG_HYBRIDIZATION`` — a
  **non-covalent** record backed by reverse-complement sequence evidence.
  Hybridization never creates a phosphodiester bond: backbone topology edits
  (``BACKBONE_CONTINUATION`` n3/n5 terminal rewires) are a separate, explicitly
  declared, allow-listed operation;
* static file operations only: deterministic topology/config concatenation,
  index-space offsetting, rigid-body transforms, coarse geometric sanity
  checks. No dynamics, relaxation, or simulation is performed or implied.

Modes:
  SOURCE_VERIFIED — only when a pinned, SOURCE_CONFIRMED interface recipe
      exists and every assembled fact is covered by it.
  CANDIDATE_DESIGN — an explicitly-marked hypothetical construction; useful as
      a software test case; it never raises a scientific claim and is never
      reported as source-verified.

Fail-closed discipline: missing coordinates, unknown sequences, incompatible
complementarity, inconsistent units, unproven recipes, tampered inputs, wrong
polarity, ID reuse, backbone corruption, geometry conflicts — every invalid
case produces a deterministic refusal receipt (never a silent guess). The
coarse geometric check can never exclude steric conflicts; outcomes therefore
carry ``GEOMETRY_UNVERIFIED`` instead of an unqualified PASS.

Claim ceiling: ``ASSEMBLED_STATIC_ONLY`` refers to deterministic file-level
construction. It is never ``ASSEMBLY_VALIDATED``, never evidence of
hybridization occurring, of motion transfer, of functionality, or of wet-lab
fabricability.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from hinge_family.oxdna_conf import Configuration, ConfError
from hinge_family.oxdna_topology import Topology, TopologyError
from knowledge_pack.contract import CLAIM_LEVELS_V1, FORBIDDEN_CLAIM_LEVELS
from knowledge_pack.mechanical_component_spec import (
    ASSEMBLER_SUPPORTED_INTERFACE_TYPES,
    ComponentSpecError,
    SHA256_RE,
    validate_component_spec,
)
from knowledge_pack.s17_index_map import load_topology_verified

SCHEMA_VERSION = 1
SPEC_KIND = "assembly_spec"
SPEC_VERSION = "v1"

ASSEMBLY_MODES = ("SOURCE_VERIFIED", "CANDIDATE_DESIGN")
DESIGN_BASES = ("PUBLISHED_SOURCE", "HYPOTHESIS")
COMPONENT_ROLES = ("driver", "follower")
CONNECTION_KINDS = ("SS_DNA_OVERHANG_HYBRIDIZATION", "BACKBONE_CONTINUATION")
EVIDENCE_STATUSES = ("SOURCE_CONFIRMED", "INFERRED_CANDIDATE", "UNVERIFIED", "UNKNOWN")

ASSEMBLY_STATUSES = (
    "ASSEMBLED_STATIC_ONLY",
    "NOT_RECONSTRUCTED",
    "BLOCKED_SOURCE",
    "BLOCKED_INFERRED_INTERFACE",
    "BLOCKED_SPEC",
    "BLOCKED_GEOMETRY",
    "BLOCKED_INPUT",
)
GEOMETRY_STATUSES = (
    "NOT_PERFORMED",
    "GEOMETRY_UNVERIFIED",
    "GEOMETRIC_CONFLICT",
)

MIN_HYBRIDIZATION_MATCH_NT = 12

TOP_LEVEL_KEYS = (
    "schema_version",
    "kind",
    "spec_version",
    "assembly_id",
    "mode",
    "design_basis",
    "claim_level",
    "knowledge_pack_ref",
    "components",
    "interface_recipe_ref",
    "coordinate_transforms",
    "unit_conversion",
    "connections",
    "allowed_backbone_edits",
    "geometry",
    "assembly_box",
    "expected_units",
    "notes",
)
REQUIRED_TOP_LEVEL = (
    "schema_version",
    "kind",
    "spec_version",
    "assembly_id",
    "mode",
    "design_basis",
    "claim_level",
    "knowledge_pack_ref",
    "components",
    "connections",
    "allowed_backbone_edits",
    "geometry",
    "expected_units",
)


class AssemblySpecError(Exception):
    """Raised on fail-closed assembly-spec violations."""


# --------------------------------------------------------------------------
# sequence helpers (deterministic, offline)
# --------------------------------------------------------------------------

def strip_lna(sequence: str) -> str:
    """Replace (LX) locked-nucleic-acid notation with the plain base X."""
    out = []
    i = 0
    while i < len(sequence):
        if sequence[i] == "(" and i + 3 < len(sequence) and sequence[i + 1] == "L" and sequence[i + 3] == ")":
            out.append(sequence[i + 2])
            i += 4
        else:
            out.append(sequence[i])
            i += 1
    return "".join(out).replace(" ", "").upper()


def reverse_complement(sequence: str) -> str:
    return sequence[::-1].translate(str.maketrans("ACGT", "TGCA"))


def max_complementary_match(a: str, b: str) -> int:
    """Length of the longest exact match between ``a`` and rc(b) over full strings."""
    rb = reverse_complement(b)
    best = 0
    for i in range(len(a)):
        for j in range(len(rb)):
            k = 0
            while i + k < len(a) and j + k < len(rb) and a[i + k] == rb[j + k]:
                k += 1
            if k > best:
                best = k
    return best


# --------------------------------------------------------------------------
# AssemblySpec validation
# --------------------------------------------------------------------------

def validate_assembly_spec(spec: object, component_specs: dict[str, dict]) -> list[str]:
    """Strict validation of the assembly spec against the two component specs."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return ["assembly spec must be a JSON object"]
    for key in REQUIRED_TOP_LEVEL:
        if key not in spec:
            errors.append(f"missing required field {key}")
    if errors:
        return errors
    extra = sorted(set(spec) - set(TOP_LEVEL_KEYS))
    if extra:
        errors.append(f"unknown top-level fields: {extra}")
    if spec["schema_version"] != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if spec["kind"] != SPEC_KIND:
        errors.append(f"kind must be {SPEC_KIND!r}")
    if spec["spec_version"] != SPEC_VERSION:
        errors.append(f"spec_version must be {SPEC_VERSION!r}")
    if not isinstance(spec["assembly_id"], str) or not spec["assembly_id"].strip():
        errors.append("assembly_id must be a non-empty string")
    claim = spec["claim_level"]
    if claim in FORBIDDEN_CLAIM_LEVELS:
        errors.append(f"claim_level {claim!r} exceeds the v1 ceiling")
    elif claim not in CLAIM_LEVELS_V1:
        errors.append(f"claim_level must be one of {sorted(CLAIM_LEVELS_V1)}")
    if spec["mode"] not in ASSEMBLY_MODES:
        errors.append(f"mode must be one of {ASSEMBLY_MODES}")
    if spec["design_basis"] not in DESIGN_BASES:
        errors.append(f"design_basis must be one of {DESIGN_BASES}")
    if spec["mode"] == "SOURCE_VERIFIED" and spec["design_basis"] != "PUBLISHED_SOURCE":
        errors.append("mode SOURCE_VERIFIED requires design_basis PUBLISHED_SOURCE")
    if spec["mode"] == "CANDIDATE_DESIGN" and spec["design_basis"] != "HYPOTHESIS":
        errors.append("mode CANDIDATE_DESIGN requires design_basis HYPOTHESIS")

    kpr = spec["knowledge_pack_ref"]
    if not isinstance(kpr, dict) or not all(
        k in kpr for k in ("pack_id", "pack_path", "pack_sha256")
    ):
        errors.append("knowledge_pack_ref must carry pack_id/pack_path/pack_sha256")
    elif not isinstance(kpr.get("pack_sha256"), str) or not SHA256_RE.match(kpr["pack_sha256"]):
        errors.append("knowledge_pack_ref.pack_sha256 must be a 64-hex sha256")

    components = spec["components"]
    if not isinstance(components, list) or len(components) != 2:
        errors.append("components must be a list of exactly 2 entries")
        return errors
    roles = [c.get("role") for c in components if isinstance(c, dict)]
    if sorted(roles) != sorted(COMPONENT_ROLES):
        errors.append(f"component roles must be exactly {sorted(COMPONENT_ROLES)}")
    COMPONENT_ENTRY_KEYS = (
        "role", "component_id", "version", "topology_sha256", "configuration_sha256", "port_geometry",
    )
    for i, comp in enumerate(components):
        if not isinstance(comp, dict):
            errors.append(f"components[{i}] must be an object")
            continue
        extra = sorted(set(comp) - set(COMPONENT_ENTRY_KEYS))
        if extra:
            errors.append(f"components[{i}] has unknown fields: {extra}")
        for key in ("role", "component_id", "version", "topology_sha256"):
            if key not in comp:
                errors.append(f"components[{i}] missing {key}")
        geometry = comp.get("port_geometry", [])
        if not isinstance(geometry, list):
            errors.append(f"components[{i}].port_geometry must be a list")
        else:
            for j, pg in enumerate(geometry):
                if not isinstance(pg, dict):
                    errors.append(f"components[{i}].port_geometry[{j}] must be an object")
                    continue
                if "port_id" not in pg or "anchor_position" not in pg:
                    errors.append(
                        f"components[{i}].port_geometry[{j}] requires port_id and anchor_position"
                    )
                elif (
                    not isinstance(pg["anchor_position"], list) or len(pg["anchor_position"]) != 3
                ):
                    errors.append(
                        f"components[{i}].port_geometry[{j}].anchor_position must be [x, y, z]"
                    )
        cs = component_specs.get(comp.get("role"))
        if cs is None:
            continue
        if comp.get("component_id") != cs.get("component_id"):
            errors.append(
                f"components[{i}].component_id {comp.get('component_id')!r} does not match the "
                f"component spec {cs.get('component_id')!r} (incompatible identity)"
            )
        if comp.get("version") != cs.get("version"):
            errors.append(
                f"components[{i}].version {comp.get('version')!r} does not match the component "
                f"spec version {cs.get('version')!r} (incompatible versions)"
            )
        # unit discipline: every component must already be in the expected units
        # unless an explicit unit_conversion covers it. A component whose units
        # are UNKNOWN is only an error when its topology is concrete (i.e. it
        # could actually be assembled); a structure-less component is rejected
        # later with the more precise NOT_RECONSTRUCTED reason.
        expected_len = (spec.get("expected_units") or {}).get("length_unit")
        comp_len = (cs.get("model_and_units") or {}).get("length_unit")
        top_block = cs.get("topology") or {}
        topology_concrete = isinstance(top_block, dict) and top_block.get("status") not in (
            None, "UNKNOWN",
        )
        conversion = spec.get("unit_conversion") or {}
        converted = conversion.get("component") == comp.get("role")
        if expected_len and comp_len and comp_len != expected_len and not converted:
            if comp_len == "UNKNOWN" and topology_concrete:
                errors.append(
                    f"components[{i}]: component length_unit is UNKNOWN but its topology is "
                    "concrete - a structure with unknown units can never be assembled "
                    "(inconsistent units)"
                )
            elif comp_len != "UNKNOWN":
                errors.append(
                    f"components[{i}]: component length_unit {comp_len!r} differs from expected "
                    f"{expected_len!r} without a declared unit_conversion (inconsistent units)"
                )
        if converted and comp_len != conversion.get("from_unit"):
            errors.append(
                f"components[{i}]: unit_conversion.from_unit {conversion.get('from_unit')!r} does "
                f"not match the component length_unit {comp_len!r}"
            )
        if converted and conversion.get("to_unit") != expected_len:
            errors.append(
                f"components[{i}]: unit_conversion.to_unit {conversion.get('to_unit')!r} does not "
                f"match expected_units.length_unit {expected_len!r}"
            )
        top_block = cs.get("topology", {})
        expected = top_block.get("sha256") if isinstance(top_block, dict) else "UNKNOWN"
        declared = comp.get("topology_sha256")
        if expected == "UNKNOWN" or expected is None:
            if declared != "UNKNOWN":
                errors.append(
                    f"components[{i}].topology_sha256 must be UNKNOWN: the component spec has no "
                    "pinned topology (a structure that does not exist can never be assembled)"
                )
        elif declared != expected:
            errors.append(
                f"components[{i}].topology_sha256 {declared!r} does not match the pinned "
                f"component topology {expected!r}"
            )

    # interface recipe gate.
    if spec["mode"] == "SOURCE_VERIFIED":
        ref = spec.get("interface_recipe_ref")
        if not isinstance(ref, dict):
            errors.append("mode SOURCE_VERIFIED requires interface_recipe_ref")
        else:
            for key in ("path", "sha256", "status"):
                if key not in ref:
                    errors.append(f"interface_recipe_ref missing {key}")
            sha = ref.get("sha256")
            if sha is not None and not (isinstance(sha, str) and SHA256_RE.match(sha)):
                errors.append("interface_recipe_ref.sha256 must be a 64-hex sha256")
            if ref.get("status") != "SOURCE_CONFIRMED":
                errors.append(
                    "mode SOURCE_VERIFIED requires interface_recipe_ref.status SOURCE_CONFIRMED; "
                    "a recipe without published proof is BLOCKED_INFERRED_INTERFACE"
                )

    # transforms.
    transforms = spec.get("coordinate_transforms", [])
    if not isinstance(transforms, list):
        errors.append("coordinate_transforms must be a list")
    else:
        seen_roles = set()
        for i, tr in enumerate(transforms):
            if not isinstance(tr, dict):
                errors.append(f"coordinate_transforms[{i}] must be an object")
                continue
            for key in ("component", "translation"):
                if key not in tr:
                    errors.append(f"coordinate_transforms[{i}] missing {key}")
            role = tr.get("component")
            if role in COMPONENT_ROLES:
                if role in seen_roles:
                    errors.append(f"coordinate_transforms[{i}]: duplicate transform for {role!r}")
                seen_roles.add(role)
            else:
                errors.append(f"coordinate_transforms[{i}].component must be one of {COMPONENT_ROLES}")
            if "translation" in tr and (
                not isinstance(tr["translation"], list) or len(tr["translation"]) != 3
            ):
                errors.append(f"coordinate_transforms[{i}].translation must be [x, y, z]")

    # unit conversion + expected units consistency.
    expected_units = spec["expected_units"]
    if not isinstance(expected_units, dict) or "length_unit" not in expected_units:
        errors.append("expected_units must carry length_unit")
    conversion = spec.get("unit_conversion")
    if conversion is not None:
        if not isinstance(conversion, dict):
            errors.append("unit_conversion must be an object")
        else:
            for key in ("component", "from_unit", "to_unit", "length_factor", "source"):
                if key not in conversion:
                    errors.append(f"unit_conversion missing {key}")
            factor = conversion.get("length_factor")
            if not isinstance(factor, (int, float)) or isinstance(factor, bool) or factor <= 0:
                errors.append("unit_conversion.length_factor must be a positive number")

    # connections.
    connections = spec["connections"]
    if not isinstance(connections, list):
        errors.append("connections must be a list")
    else:
        port_index = _port_index(component_specs)
        seen_conn: set[str] = set()
        for i, conn in enumerate(connections):
            errors.extend(_validate_connection(conn, i, port_index, spec, seen_conn))

    # allowed backbone edits must be an explicit list; every BACKBONE_CONTINUATION
    # connection must be covered by it.
    allowed = spec["allowed_backbone_edits"]
    if not isinstance(allowed, list):
        errors.append("allowed_backbone_edits must be a list")
    else:
        for i, conn in enumerate(connections if isinstance(connections, list) else []):
            if isinstance(conn, dict) and conn.get("kind") == "BACKBONE_CONTINUATION":
                cid = conn.get("connection_id")
                if cid not in [e.get("connection_id") for e in allowed if isinstance(e, dict)]:
                    errors.append(
                        f"connections[{i}] ({cid!r}) is a backbone edit but is not covered by "
                        "allowed_backbone_edits (fail-closed)"
                    )

    geometry = spec["geometry"]
    if not isinstance(geometry, dict):
        errors.append("geometry must be an object")
    else:
        if "enabled" not in geometry:
            errors.append("geometry must declare enabled")

    if "notes" in spec and not isinstance(spec["notes"], (str, list)):
        errors.append("notes must be a string or list")
    return errors


def _port_index(component_specs: dict) -> dict:
    index: dict[tuple, dict] = {}
    for role, cs in component_specs.items():
        for port in cs.get("ports", []) or []:
            if isinstance(port, dict) and "port_id" in port:
                index[(role, port["port_id"])] = port
    return index


def _validate_connection(conn: object, i: int, port_index: dict, spec: dict, seen_conn: set) -> list[str]:
    errors: list[str] = []
    where = f"connections[{i}]"
    if not isinstance(conn, dict):
        return [f"{where} must be an object"]
    for key in ("connection_id", "kind", "driver_port", "follower_port", "evidence_status"):
        if key not in conn:
            errors.append(f"{where} missing {key}")
    if errors:
        return errors
    cid = conn["connection_id"]
    if not isinstance(cid, str) or not cid.strip():
        errors.append(f"{where}.connection_id must be a non-empty string")
    elif cid in seen_conn:
        errors.append(f"{where}.connection_id duplicate: {cid!r}")
    else:
        seen_conn.add(cid)
    if conn["kind"] not in CONNECTION_KINDS:
        errors.append(f"{where}.kind must be one of {CONNECTION_KINDS}")
    if conn["evidence_status"] not in EVIDENCE_STATUSES:
        errors.append(f"{where}.evidence_status must be one of {EVIDENCE_STATUSES}")
    if spec["mode"] == "SOURCE_VERIFIED" and conn["evidence_status"] != "SOURCE_CONFIRMED":
        errors.append(
            f"{where}: mode SOURCE_VERIFIED requires evidence_status SOURCE_CONFIRMED"
        )
    for key in ("driver_port", "follower_port"):
        pid = conn.get(key)
        if (key.replace("_port", ""), pid) not in port_index:
            errors.append(f"{where}.{key} {pid!r} does not exist in the component specs")
    if conn["kind"] == "SS_DNA_OVERHANG_HYBRIDIZATION":
        for role_key, role in (("driver_port", "driver"), ("follower_port", "follower")):
            port = port_index.get((role, conn.get(role_key)))
            if isinstance(port, dict) and port.get("interface_type") not in (
                "SS_DNA_OVERHANG_HYBRIDIZATION",
            ):
                errors.append(
                    f"{where}.{role_key}: port interface_type "
                    f"{port.get('interface_type')!r} is incompatible with connection kind "
                    f"{conn['kind']!r}"
                )
    if conn["kind"] == "BACKBONE_CONTINUATION":
        edit = conn.get("backbone_edit")
        if not isinstance(edit, dict):
            errors.append(f"{where}: BACKBONE_CONTINUATION requires backbone_edit")
    return errors


# --------------------------------------------------------------------------
# deterministic receipts
# --------------------------------------------------------------------------

def _receipt(assembly_status: str, geometry_status: str, reason: str | None) -> dict:
    if assembly_status not in ASSEMBLY_STATUSES:
        raise AssemblySpecError(f"unknown assembly status {assembly_status}")
    if geometry_status not in GEOMETRY_STATUSES:
        raise AssemblySpecError(f"unknown geometry status {geometry_status}")
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "assembly_receipt",
        "assembly_status": assembly_status,
        "claim": (
            "STATIC_FILE_OPERATION_ONLY: deterministic file-level construction. Never "
            "ASSEMBLY_VALIDATED; never evidence of hybridization occurring, of motion transfer, "
            "of function, or of wet-lab fabricability."
        ),
        "geometry_status": geometry_status,
        "reason": reason,
        "assembled": None,
    }


def not_reconstructed_receipt(assembly_id: str, components: dict, blocked_inputs: list[str]) -> dict:
    """The honest receipt when published sources do not pin all required inputs."""
    receipt = _receipt(
        "NOT_RECONSTRUCTED",
        "NOT_PERFORMED",
        "required published inputs are missing; no assembly is attempted and no link is invented",
    )
    receipt["assembly_id"] = assembly_id
    receipt["mode"] = "SOURCE_VERIFIED"
    receipt["components"] = components
    receipt["blocked_inputs"] = blocked_inputs
    return receipt


# --------------------------------------------------------------------------
# static assembler
# --------------------------------------------------------------------------

def _load_configuration(path: Path) -> Configuration:
    try:
        return Configuration.parse(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ConfError) as exc:
        raise AssemblySpecError(f"configuration load failed for {path}: {exc}") from exc


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _rotation_matrix(axis: list, angle_deg: float) -> list:
    norm = math.sqrt(sum(x * x for x in axis))
    if norm == 0:
        raise AssemblySpecError("rotation axis must be non-zero")
    x, y, z = (v / norm for v in axis)
    t = math.radians(angle_deg)
    c, s = math.cos(t), math.sin(t)
    return [
        [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
        [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
        [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
    ]


def _fmt(value: float) -> str:
    """Deterministic fixed-point formatting for merged configuration output."""
    text = f"{value:.6f}"
    if text == "-0.000000":
        text = "0.000000"
    return text


def assemble(spec: dict, component_specs: dict[str, dict],
             inputs: dict[str, dict]) -> dict:
    """Deterministic static two-component assembly; returns a fail-closed receipt.

    ``inputs[role] = {"topology_path": ..., "configuration_path": ...}``.
    Nothing is ever written to disk by this function.
    """
    # 1. validate everything structurally first.
    if sorted(component_specs) != sorted(COMPONENT_ROLES):
        return _receipt(
            "BLOCKED_SPEC", "NOT_PERFORMED",
            f"component specs must be keyed exactly by {sorted(COMPONENT_ROLES)}",
        )
    driver_id = component_specs["driver"].get("component_id")
    follower_id = component_specs["follower"].get("component_id")
    if driver_id == follower_id:
        return _receipt(
            "BLOCKED_SPEC", "NOT_PERFORMED",
            f"driver and follower component specs must be distinct identities, both are {driver_id!r}",
        )
    errors: list[str] = []
    for role, cs in component_specs.items():
        errors.extend(validate_component_spec(cs))
    errors.extend(validate_assembly_spec(spec, component_specs))
    if errors:
        receipt = _receipt("BLOCKED_SPEC", "NOT_PERFORMED", "spec validation failed: " + "; ".join(errors))
        receipt["assembly_id"] = spec.get("assembly_id", "UNKNOWN")
        return receipt

    # 2. input requirements. Pass A decides on *structural existence* first: a
    #    component whose pinned topology does not exist in any source makes the
    #    whole assembly NOT_RECONSTRUCTED (decisive, checked for both roles).
    blocked: list[str] = []
    have_structure: dict[str, bool] = {}
    for role in COMPONENT_ROLES:
        cs = component_specs[role]
        top_block = cs["topology"]
        conf_block = cs.get("configuration", {})
        if _status_of_block(top_block) == "UNKNOWN":
            blocked.append(
                f"{role}: pinned topology does not exist in any audited source "
                "(component spec status UNKNOWN)"
            )
            have_structure[role] = False
        else:
            have_structure[role] = True
        if _status_of_block(conf_block) == "UNKNOWN":
            blocked.append(
                f"{role}: component spec has no pinned configuration "
                "(coordinates are required for static assembly)"
            )
    if blocked:
        return not_reconstructed_receipt(spec["assembly_id"], _component_identity(spec, component_specs), blocked)

    # 2b. Pass B: materialized, digest-verified input files for concrete pins.
    for role in COMPONENT_ROLES:
        cs = component_specs[role]
        block = inputs.get(role)
        if not isinstance(block, dict):
            return _fail_missing_input(spec, role, "input file set missing (pins are remote-only and not materialized in this execution)")
        top_block = cs["topology"]
        conf_block = cs.get("configuration", {})
        top_path = Path(block.get("topology_path", ""))
        conf_path = Path(block.get("configuration_path", ""))
        if not top_path.exists() or not conf_path.exists():
            return _fail_missing_input(spec, role, "topology/configuration file missing on disk")
        if hashlib.sha256(top_path.read_bytes()).hexdigest() != top_block["sha256"]:
            return _receipt("BLOCKED_INPUT", "NOT_PERFORMED",
                            f"{role}: topology file digest does not match the pinned sha256 (tampered or wrong input)")
        if hashlib.sha256(conf_path.read_bytes()).hexdigest() != conf_block["sha256"]:
            return _receipt("BLOCKED_INPUT", "NOT_PERFORMED",
                            f"{role}: configuration file digest does not match the pinned sha256 (tampered or wrong input)")
        try:
            top = load_topology_verified(top_path, top_block["sha256"])
            top.check_chain_integrity()
        except Exception as exc:  # IndexMapError/TopologyError
            return _receipt("BLOCKED_INPUT", "NOT_PERFORMED", f"{role}: strict topology parse/chain check failed: {exc}")
        try:
            conf = _load_configuration(conf_path)
        except AssemblySpecError as exc:
            return _receipt("BLOCKED_INPUT", "NOT_PERFORMED", str(exc))
        if top.nucleotides != len(conf.particles):
            return _receipt("BLOCKED_INPUT", "NOT_PERFORMED",
                            f"{role}: topology/configuration particle count mismatch")
        if role == "driver":
            driver_top, driver_conf = top, conf
        else:
            follower_top, follower_conf = top, conf

    # 3. hybridization connections must be backed by reverse-complement evidence
    #    from the component specs' port chemistry (polarity + complementarity)
    #    and every concrete anchor index must be inside its component bounds.
    port_index = _port_index(component_specs)
    conn_results = []
    for conn in spec["connections"]:
        if conn["kind"] != "SS_DNA_OVERHANG_HYBRIDIZATION":
            continue
        dport = port_index[("driver", conn["driver_port"])]
        fport = port_index[("follower", conn["follower_port"])]
        for role, port, limit in (
            ("driver", dport, driver_top.nucleotides),
            ("follower", fport, follower_top.nucleotides),
        ):
            for anchor in port.get("anchors", []):
                value = anchor.get("anchor")
                if isinstance(value, int) and not (0 <= value < limit):
                    return _receipt(
                        "BLOCKED_SPEC", "NOT_PERFORMED",
                        f"connection {conn['connection_id']}: {role} anchor index {value} outside "
                        f"[0, {limit}) (invalid or ambiguous index)",
                    )
        dchem, fchem = dport.get("chemistry", {}), fport.get("chemistry", {})
        dseq, fseq = dchem.get("sequence", "UNKNOWN"), fchem.get("sequence", "UNKNOWN")
        if dseq in ("UNKNOWN", None) or fseq in ("UNKNOWN", None):
            return _receipt(
                "BLOCKED_INFERRED_INTERFACE", "NOT_PERFORMED",
                f"connection {conn['connection_id']}: port sequence UNKNOWN - a connection without "
                "published sequence evidence is never assembled",
            )
        match = max_complementary_match(strip_lna(dseq), strip_lna(fseq))
        if match < MIN_HYBRIDIZATION_MATCH_NT:
            return _receipt(
                "BLOCKED_INFERRED_INTERFACE", "NOT_PERFORMED",
                f"connection {conn['connection_id']}: sequences are not complementary "
                f"(max reverse-complement match {match} nt < {MIN_HYBRIDIZATION_MATCH_NT})",
            )
        conn_results.append({
            "connection_id": conn["connection_id"],
            "kind": conn["kind"],
            "covalent": False,
            "complementarity_match_nt": match,
            "evidence_status": conn["evidence_status"],
            "note": "recorded as a non-covalent hybridization interface; no backbone link created",
        })

    # 4. backbone edits: allow-listed BACKBONE_CONTINUATION connections only.
    edits_applied = []
    if any(c["kind"] == "BACKBONE_CONTINUATION" for c in spec["connections"]):
        return _receipt(
            "BLOCKED_SPEC", "NOT_PERFORMED",
            "BACKBONE_CONTINUATION execution requires the R2 terminal-rewire assembler path; "
            "the v1 two-component hybridization assembler refuses covalent edits",
        )

    # 5. merge topologies: driver rows unchanged, follower rows offset; fresh
    #    contiguous strand ids in file order (driver strands, then follower).
    offset = driver_top.nucleotides
    rows = list(driver_top.rows)
    for (sid, base, n3, n5) in follower_top.rows:
        rows.append((sid + driver_top.strand_count, base,
                     (n3 + offset) if n3 != -1 else -1,
                     (n5 + offset) if n5 != -1 else -1))
    total_n = len(rows)
    total_s = driver_top.strand_count + follower_top.strand_count
    topology_text = f"{total_n} {total_s}\n" + "".join(
        f"{sid} {base} {n3} {n5}\n" for (sid, base, n3, n5) in rows
    )
    try:
        merged_top = Topology.parse(topology_text)
        merged_top.check_chain_integrity()
    except TopologyError as exc:
        return _receipt("BLOCKED_SPEC", "NOT_PERFORMED",
                        f"merged topology failed strict reparse/chain integrity: {exc}")

    # 6. merge configurations with unit conversion + rigid-body transform.
    def particles_text(particles) -> str:
        out = []
        for (pos, o1, o2, v1, v2) in particles:
            nums = [*pos, *o1, *o2, *v1, *v2]
            out.append(" ".join(_fmt(v) for v in nums))
        return "".join(line + "\n" for line in out)

    driver_text = particles_text(driver_conf.particles)
    follower_particles = follower_conf.particles
    conversion = spec.get("unit_conversion")
    if conversion is not None and conversion.get("component") == "follower":
        factor = float(conversion["length_factor"])
        scaled = []
        for (pos, o1, o2, v1, v2) in follower_particles:
            scaled.append((
                [x * factor for x in pos], o1, o2,
                [x * factor for x in v1], [x * factor for x in v2],
            ))
        follower_particles = scaled
    transform = next((tr for tr in spec.get("coordinate_transforms", [])
                      if tr.get("component") == "follower"), None)
    if transform is not None:
        rot = None
        if transform.get("rotation_axis") is not None and transform.get("rotation_angle_deg") is not None:
            rot = _rotation_matrix(transform["rotation_axis"], float(transform["rotation_angle_deg"]))
        trans = [float(x) for x in transform["translation"]]
        transformed = []
        for (pos, o1, o2, v1, v2) in follower_particles:
            def apply(vec):
                if rot is None:
                    return list(vec)
                return [
                    rot[0][0] * vec[0] + rot[0][1] * vec[1] + rot[0][2] * vec[2],
                    rot[1][0] * vec[0] + rot[1][1] * vec[1] + rot[1][2] * vec[2],
                    rot[2][0] * vec[0] + rot[2][1] * vec[1] + rot[2][2] * vec[2],
                ]
            new_pos = apply(pos)
            new_pos = [new_pos[a] + trans[a] for a in range(3)]
            transformed.append((new_pos, apply(o1), apply(o2), apply(v1), apply(v2)))
        follower_particles = transformed
    follower_text = particles_text(follower_particles)

    box = spec.get("assembly_box")
    if box is None:
        box = [max(a, b) for a, b in zip(driver_conf.box, follower_conf.box)]
    header = (
        f"t = {driver_conf.time}\n"
        f"b = {box[0]} {box[1]} {box[2]}\n"
        f"E = 0 0 0\n"
    )
    config_text = header + driver_text + follower_text
    try:
        merged_conf = Configuration.parse(config_text)
    except ConfError as exc:
        return _receipt("BLOCKED_SPEC", "NOT_PERFORMED", f"merged configuration failed strict reparse: {exc}")
    outside = sum(
        1 for (pos, *_rest) in merged_conf.particles
        if not all(0.0 <= pos[a] <= merged_conf.box[a] for a in range(3))
    )
    if outside:
        return _receipt(
            "BLOCKED_GEOMETRY", "GEOMETRIC_CONFLICT",
            f"{outside} merged particle positions fall outside the declared assembly box",
        )

    # 7. coarse geometric checks.
    geometry_status, geometry_facts = _geometry_checks(spec, driver_conf, follower_particles,
                                                       follower_conf, transform, conversion)
    if geometry_status == "GEOMETRIC_CONFLICT":
        receipt = _receipt("BLOCKED_GEOMETRY", geometry_status,
                           geometry_facts.get("violation", "geometric conflict"))
        receipt["assembly_id"] = spec["assembly_id"]
        receipt["mode"] = spec["mode"]
        receipt["design_basis"] = spec["design_basis"]
        receipt["components"] = _component_identity(spec, component_specs)
        receipt["connections"] = conn_results
        receipt["backbone_edits_applied"] = edits_applied
        receipt["geometry"] = geometry_facts
        receipt["inputs"] = {
            role: {
                "topology_sha256": hashlib.sha256(Path(inputs[role]["topology_path"]).read_bytes()).hexdigest(),
                "configuration_sha256": hashlib.sha256(Path(inputs[role]["configuration_path"]).read_bytes()).hexdigest(),
            }
            for role in COMPONENT_ROLES
        }
        return receipt

    # 8. deterministic canonical manifest.
    receipt = _receipt("ASSEMBLED_STATIC_ONLY", geometry_status, None)
    receipt["assembly_id"] = spec["assembly_id"]
    receipt["mode"] = spec["mode"]
    receipt["design_basis"] = spec["design_basis"]
    receipt["components"] = _component_identity(spec, component_specs)
    receipt["connections"] = conn_results
    receipt["backbone_edits_applied"] = edits_applied
    receipt["geometry"] = geometry_facts
    receipt["inputs"] = {
        role: {
            "topology_sha256": hashlib.sha256(Path(inputs[role]["topology_path"]).read_bytes()).hexdigest(),
            "configuration_sha256": hashlib.sha256(Path(inputs[role]["configuration_path"]).read_bytes()).hexdigest(),
        }
        for role in COMPONENT_ROLES
    }
    receipt["assembled"] = {
        "nucleotides": total_n,
        "strands": total_s,
        "index_map_policy": {
            "particle_index_space": "0-based; driver particles keep their local indices; follower "
                                    "particle g = local f + driver nucleotide count",
            "strand_ids": "fresh contiguous 1..S in file order (driver strands, then follower "
                          "strands); collisions are impossible by construction",
            "covalent_links": "created only inside each component by its own n3/n5 rows; hybridization "
                              "connections never create n3/n5 links",
        },
        "topology_text_sha256": _sha256_text(topology_text),
        "configuration_text_sha256": _sha256_text(config_text),
        "assembly_box": [float(b) for b in merged_conf.box],
        "note": "topology_text/configuration_text themselves are returned by assemble_artifacts()",
    }
    return receipt


def assemble_artifacts(spec: dict, component_specs: dict, inputs: dict) -> tuple[str, str, dict]:
    """Return (topology_text, configuration_text, receipt)."""
    # Re-run assemble for validation; then rebuild the texts deterministically.
    receipt = assemble(spec, component_specs, inputs)
    if receipt["assembly_status"] != "ASSEMBLED_STATIC_ONLY":
        return "", "", receipt
    driver_top = load_topology_verified(Path(inputs["driver"]["topology_path"]),
                                        component_specs["driver"]["topology"]["sha256"])
    follower_top = load_topology_verified(Path(inputs["follower"]["topology_path"]),
                                          component_specs["follower"]["topology"]["sha256"])
    offset = driver_top.nucleotides
    rows = list(driver_top.rows)
    for (sid, base, n3, n5) in follower_top.rows:
        rows.append((sid + driver_top.strand_count, base,
                     (n3 + offset) if n3 != -1 else -1,
                     (n5 + offset) if n5 != -1 else -1))
    topology_text = (f"{len(rows)} {driver_top.strand_count + follower_top.strand_count}\n"
                     + "".join(f"{sid} {base} {n3} {n5}\n" for (sid, base, n3, n5) in rows))
    driver_conf = _load_configuration(Path(inputs["driver"]["configuration_path"]))
    follower_conf = _load_configuration(Path(inputs["follower"]["configuration_path"]))
    follower_particles = follower_conf.particles
    conversion = spec.get("unit_conversion")
    if conversion is not None and conversion.get("component") == "follower":
        factor = float(conversion["length_factor"])
        follower_particles = [
            ([x * factor for x in pos], o1, o2, [x * factor for x in v1], [x * factor for x in v2])
            for (pos, o1, o2, v1, v2) in follower_particles
        ]
    transform = next((tr for tr in spec.get("coordinate_transforms", [])
                      if tr.get("component") == "follower"), None)
    if transform is not None:
        rot = None
        if transform.get("rotation_axis") is not None and transform.get("rotation_angle_deg") is not None:
            rot = _rotation_matrix(transform["rotation_axis"], float(transform["rotation_angle_deg"]))
        trans = [float(x) for x in transform["translation"]]
        transformed = []
        for (pos, o1, o2, v1, v2) in follower_particles:
            def apply(vec):
                if rot is None:
                    return list(vec)
                return [
                    rot[0][0] * vec[0] + rot[0][1] * vec[1] + rot[0][2] * vec[2],
                    rot[1][0] * vec[0] + rot[1][1] * vec[1] + rot[1][2] * vec[2],
                    rot[2][0] * vec[0] + rot[2][1] * vec[1] + rot[2][2] * vec[2],
                ]
            new_pos = apply(pos)
            transformed.append(([new_pos[a] + trans[a] for a in range(3)], apply(o1), apply(o2), apply(v1), apply(v2)))
        follower_particles = transformed

    def particles_text(particles) -> str:
        return "".join(
            " ".join(_fmt(v) for v in [*pos, *o1, *o2, *v1, *v2]) + "\n"
            for (pos, o1, o2, v1, v2) in particles
        )

    box = spec.get("assembly_box") or [max(a, b) for a, b in zip(driver_conf.box, follower_conf.box)]
    config_text = (f"t = {driver_conf.time}\nb = {box[0]} {box[1]} {box[2]}\nE = 0 0 0\n"
                   + particles_text(driver_conf.particles) + particles_text(follower_particles))
    if _sha256_text(topology_text) != receipt["assembled"]["topology_text_sha256"]:
        raise AssemblySpecError("internal determinism failure: topology digest mismatch")
    if _sha256_text(config_text) != receipt["assembled"]["configuration_text_sha256"]:
        raise AssemblySpecError("internal determinism failure: configuration digest mismatch")
    return topology_text, config_text, receipt


def _geometry_checks(spec, driver_conf, follower_particles, follower_conf, transform, conversion) -> tuple[str, dict]:
    geometry = spec["geometry"]
    facts: dict = {"enabled": bool(geometry.get("enabled")), "clash_scan": None, "connected_anchor_distances": None}
    if not geometry.get("enabled"):
        facts["note"] = "geometry checks disabled by spec; outcome is NOT_PERFORMED"
        return "NOT_PERFORMED", facts
    box = spec.get("assembly_box") or [max(a, b) for a, b in zip(driver_conf.box, follower_conf.box)]

    fpos = [[float(x) for x in p[0]] for p in follower_particles]
    dpos = [[float(x) for x in p[0]] for p in driver_conf.particles]

    # connected anchor distances (minimum image under the assembly box).
    distances = []
    conn_ports = []
    for conn in spec["connections"]:
        if conn["kind"] == "SS_DNA_OVERHANG_HYBRIDIZATION":
            conn_ports.append((conn["connection_id"], conn["driver_port"], conn["follower_port"]))
    if conn_ports:
        anchor_driver = spec_geometry_anchors(spec_geometry_ports(spec, "driver"))
        anchor_follower = spec_geometry_anchors(spec_geometry_ports(spec, "follower"))
        band = geometry.get("connected_anchor_distance_range")
        for (cid, dpid, fpid) in conn_ports:
            da = anchor_driver.get(dpid)
            fa = anchor_follower.get(fpid)
            if da is None or fa is None:
                facts["note"] = "connected anchor indices not resolvable; anchor distances not evaluated"
                continue
            trans = [float(x) for x in (transform or {}).get("translation", [0, 0, 0])]
            factor = 1.0
            if conversion is not None and conversion.get("component") == "follower":
                factor = float(conversion["length_factor"])
            fp = [fa[a] * factor + trans[a] for a in range(3)]
            delta = [fp[a] - da[a] for a in range(3)]
            for a in range(3):
                delta[a] -= box[a] * round(delta[a] / box[a])
            dist = math.sqrt(sum(x * x for x in delta))
            distances.append({"connection_id": cid, "distance": round(dist, 6)})
            if band and not (float(band[0]) <= dist <= float(band[1])):
                facts["connected_anchor_distances"] = distances
                facts["violation"] = (
                    f"connection {cid}: anchor distance {dist:.3f} outside declared band {band}"
                )
                return "GEOMETRIC_CONFLICT", facts
    if distances:
        facts["connected_anchor_distances"] = distances

    # coarse inter-component clash scan (driver vs follower nucleotides).
    threshold = geometry.get("clash_scan_threshold")
    if threshold is not None:
        clashes = 0
        min_dist = float("inf")
        for dp in dpos:
            for fp in fpos:
                delta = [fp[a] - dp[a] for a in range(3)]
                for a in range(3):
                    delta[a] -= box[a] * round(delta[a] / box[a])
                dist = math.sqrt(sum(x * x for x in delta))
                if dist < min_dist:
                    min_dist = dist
                if dist < float(threshold):
                    clashes += 1
        facts["clash_scan"] = {
            "threshold": float(threshold),
            "overlapping_pairs": clashes,
            "min_inter_component_distance": round(min_dist, 6),
            "method": "centroid nucleotide positions, minimum-image distance; no excluded-volume model",
        }
        if clashes:
            facts["violation"] = f"{clashes} inter-component nucleotide pairs closer than the declared threshold"
            return "GEOMETRIC_CONFLICT", facts
    # Even with zero detected overlaps this coarse scan cannot exclude steric
    # conflicts: honest GEOMETRY_UNVERIFIED, never an unqualified PASS.
    facts["note"] = (
        "coarse scan found no hard conflict, but an excluded-volume/steric impossibility "
        "proof is out of scope for this checker"
    )
    return "GEOMETRY_UNVERIFIED", facts


def spec_geometry_ports(spec, role):
    """Assembly-level port geometry (anchor positions) may be declared per component."""
    comp = next((c for c in spec["components"] if c["role"] == role), {})
    return comp.get("port_geometry", [])


def spec_geometry_anchors(port_geometry):
    return {pg["port_id"]: [float(x) for x in pg["anchor_position"]] for pg in port_geometry if "anchor_position" in pg}


def _fail_missing_input(spec, role: str, reason: str) -> dict:
    receipt = _receipt("BLOCKED_SOURCE", "NOT_PERFORMED", f"{role}: {reason}")
    receipt["assembly_id"] = spec.get("assembly_id", "UNKNOWN")
    receipt["mode"] = spec.get("mode", "UNKNOWN")
    receipt["components"] = spec.get("components", [])
    receipt["blocked_inputs"] = [f"{role}: {reason}"]
    return receipt


def _component_identity(spec, component_specs) -> dict:
    return {
        c["role"]: {
            "component_id": component_specs[c["role"]]["component_id"],
            "version": component_specs[c["role"]]["version"],
            "topology_sha256": c.get("topology_sha256", "UNKNOWN"),
        }
        for c in spec["components"]
    }


def _status_of_block(block: object) -> str:
    if isinstance(block, dict):
        return block.get("status", "UNKNOWN")
    return "UNKNOWN"


def load_assembly_spec(path: Path) -> dict:
    path = Path(path)
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssemblySpecError(f"cannot read assembly spec {path}: {exc}") from exc
    if not isinstance(spec, dict):
        raise AssemblySpecError(f"assembly spec {path} must be a JSON object")
    return spec
