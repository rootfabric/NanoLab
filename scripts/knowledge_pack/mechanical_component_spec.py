"""MechanicalComponentSpec v1 — executable contract for a mechanical DNA part.

WO-PREP-S17-R3 stage B. First executable implementation of the future-contract
requirements in ``docs/DATA_CONTRACTS.md`` (MechanicalComponentSpec v1 row) and
``docs/control/LITERATURE_TO_MECHANISM_ROUTE_R1.md``.

Design rules (fail-closed, mirroring the KnowledgePack v1 contract in
``knowledge_pack.contract`` — no second provenance registry is introduced):

* A spec references the existing KnowledgePack via ``knowledge_pack_ref``
  (pack id + path + SHA-256 of the exact pack file). It never re-states
  provenance that the pack already owns.
* Every uncertain value is either the literal string ``UNKNOWN`` or carries an
  explicit ``status`` field. A missing check is never encoded as PASS.
* ``claim_level`` must stay inside the v1 ceiling (``CLAIM_LEVELS_V1``);
  scientific-result levels (``FORBIDDEN_CLAIM_LEVELS``) are rejected.
* ``ports[]`` carries molecular anchors, orientation, interface type and
  chemistry semantics. **A port is never ``connection_capable`` merely because
  a well-formed numeric index exists**: capability requires (a) a non-UNKNOWN
  interface type, (b) every anchor ``SOURCE_CONFIRMED``, and (c) orientation
  ``SOURCE_CONFIRMED``.
* Interface types separate backbone topology edits from hybridization: DNA
  hybridization is a non-covalent record and never creates a phosphodiester
  bond. ``BACKBONE_CONTINUATION`` is the only covalent kind and is only ever
  executed by the assembly stage when explicitly declared there.

Claim ceiling: validation proves *contract structure and claim discipline*
only. A valid spec is not a simulation, not a physics claim, and never
``ASSEMBLY_VALIDATED`` / ``MODEL_REPRODUCED``.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from knowledge_pack.contract import CLAIM_LEVELS_V1, FORBIDDEN_CLAIM_LEVELS

SCHEMA_VERSION = 1
SPEC_KIND = "mechanical_component_spec"
SPEC_VERSION = "v1"

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# Explicit status vocabulary, aligned with knowledge_pack.s17_index_map.
CLAIM_STATUSES = ("SOURCE_CONFIRMED", "INFERRED_CANDIDATE", "UNVERIFIED", "UNKNOWN")

# Interface / connection chemistry vocabulary. Semantics:
#   SS_DNA_OVERHANG_HYBRIDIZATION — non-covalent Watson-Crick pairing between
#       protruding ssDNA segments; the assembler records it, never creates
#       backbone links from it.
#   BACKBONE_CONTINUATION — covalent phosphodiester continuation (n3/n5 rewire);
#       executed only when explicitly declared in an AssemblySpec.
#   BASE_STACKING / MECHANICAL_INTERLOCK — recognized vocabulary values that
#       assembler v1 refuses to execute (explicit UNSUPPORTED_INTERFACE).
#   UNKNOWN — honest unknown; never connection-capable.
INTERFACE_TYPES = (
    "SS_DNA_OVERHANG_HYBRIDIZATION",
    "BACKBONE_CONTINUATION",
    "BASE_STACKING",
    "MECHANICAL_INTERLOCK",
    "UNKNOWN",
)
COVALENT_INTERFACE_TYPES = ("BACKBONE_CONTINUATION",)
ASSEMBLER_SUPPORTED_INTERFACE_TYPES = ("SS_DNA_OVERHANG_HYBRIDIZATION",)

PORT_ROLES = ("driver", "follower", "neutral")
DOF_KINDS = ("TRANSLATIONAL", "ROTATIONAL", "COMPLIANT", "RIGID_BODY", "UNKNOWN")

TOP_LEVEL_KEYS = (
    "schema_version",
    "kind",
    "spec_version",
    "component_id",
    "version",
    "source_id",
    "title",
    "knowledge_pack_ref",
    "source_pin",
    "claim_level",
    "topology",
    "configuration",
    "molecular_namespaces",
    "local_frame",
    "ports",
    "mechanical_dofs",
    "model_and_units",
    "observables",
    "actuation",
    "unverified_fields",
    "known_limitations",
    "provenance",
)

REQUIRED_TOP_LEVEL = (
    "schema_version",
    "kind",
    "spec_version",
    "component_id",
    "version",
    "source_id",
    "knowledge_pack_ref",
    "source_pin",
    "claim_level",
    "topology",
    "molecular_namespaces",
    "local_frame",
    "ports",
    "mechanical_dofs",
    "model_and_units",
    "unverified_fields",
    "known_limitations",
)


class ComponentSpecError(Exception):
    """Raised on fail-closed component-spec violations."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.match(value))


def _is_unknown(value: object) -> bool:
    return value == "UNKNOWN"


def _status_of(obj: object, key: str = "status") -> object:
    """Explicit-status read: a *missing* status field yields None (an error)."""
    if isinstance(obj, dict):
        return obj.get(key)
    return None


def validate_component_spec(spec: object) -> list[str]:
    """Strict structural + discipline validation. Returns a list of errors."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return ["spec must be a JSON object"]
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
    for key in ("component_id", "version", "source_id"):
        value = spec[key]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} must be a non-empty string")
    claim = spec["claim_level"]
    if claim in FORBIDDEN_CLAIM_LEVELS:
        errors.append(
            f"claim_level {claim!r} exceeds the v1 ceiling; a component spec never certifies "
            "scientific results"
        )
    elif claim not in CLAIM_LEVELS_V1:
        errors.append(f"claim_level must be one of {sorted(CLAIM_LEVELS_V1)}")

    # knowledge_pack_ref: reference into the existing source registry.
    kpr = spec["knowledge_pack_ref"]
    if not isinstance(kpr, dict):
        errors.append("knowledge_pack_ref must be an object")
    else:
        for key in ("pack_id", "pack_path", "pack_sha256"):
            if key not in kpr:
                errors.append(f"knowledge_pack_ref missing {key}")
        if "pack_sha256" in kpr and not _is_sha256(kpr.get("pack_sha256")):
            errors.append("knowledge_pack_ref.pack_sha256 must be a 64-hex sha256")

    # source_pin: what exact external source surface this component derives from.
    pin = spec["source_pin"]
    if not isinstance(pin, dict):
        errors.append("source_pin must be an object")
    else:
        for key in ("role", "url", "sha256", "status", "license"):
            if key not in pin:
                errors.append(f"source_pin missing {key}")
        if "sha256" in pin and not _is_sha256(pin.get("sha256")):
            errors.append("source_pin.sha256 must be a 64-hex sha256 (UNKNOWN is not allowed for a pin)")
        if _status_of(pin) not in CLAIM_STATUSES:
            errors.append(f"source_pin.status must be one of {CLAIM_STATUSES}")

    # topology: fully pinned or honestly UNKNOWN.
    errors.extend(_validate_structure_block(spec["topology"], "topology", required=True))

    # configuration: optional but must be pinned-or-UNKNOWN when present.
    if "configuration" in spec:
        errors.extend(_validate_structure_block(spec["configuration"], "configuration"))

    # molecular_namespaces: at least one, each with a pinned digest or UNKNOWN.
    ns = spec["molecular_namespaces"]
    if not isinstance(ns, dict) or not ns:
        errors.append("molecular_namespaces must be a non-empty object")
    else:
        for name, block in ns.items():
            if not isinstance(block, dict):
                errors.append(f"namespace {name!r} must be an object")
                continue
            for key in ("index_space", "particle_count"):
                if key not in block:
                    errors.append(f"namespace {name!r} missing {key}")
            digest = block.get("topology_sha256")
            if digest is not None and not _is_sha256(digest):
                errors.append(f"namespace {name!r} topology_sha256 must be 64-hex sha256")

    # local_frame: explicit object with a status; UNKNOWN allowed.
    frame = spec["local_frame"]
    if not isinstance(frame, dict):
        errors.append("local_frame must be an object")
    else:
        if _status_of(frame) not in CLAIM_STATUSES:
            errors.append(f"local_frame.status must be one of {CLAIM_STATUSES}")
        if _status_of(frame) != "UNKNOWN":
            for key in ("origin", "axes", "units"):
                if key not in frame:
                    errors.append(f"local_frame missing {key} (required unless status is UNKNOWN)")

    # ports.
    ports = spec["ports"]
    if not isinstance(ports, list):
        errors.append("ports must be a list")
    else:
        seen_ids: set[str] = set()
        for i, port in enumerate(ports):
            errors.extend(_validate_port(port, i, seen_ids))

    # mechanical_dofs.
    dofs = spec["mechanical_dofs"]
    if not isinstance(dofs, list) or not dofs:
        errors.append("mechanical_dofs must be a non-empty list")
    else:
        for i, dof in enumerate(dofs):
            if not isinstance(dof, dict):
                errors.append(f"mechanical_dofs[{i}] must be an object")
                continue
            for key in ("dof_id", "kind", "status"):
                if key not in dof:
                    errors.append(f"mechanical_dofs[{i}] missing {key}")
            if dof.get("kind") not in DOF_KINDS:
                errors.append(f"mechanical_dofs[{i}].kind must be one of {DOF_KINDS}")
            if _status_of(dof) not in CLAIM_STATUSES:
                errors.append(f"mechanical_dofs[{i}].status must be one of {CLAIM_STATUSES}")

    # model_and_units.
    mu = spec["model_and_units"]
    if not isinstance(mu, dict):
        errors.append("model_and_units must be an object")
    else:
        for key in ("model", "length_unit", "compatible_conditions"):
            if key not in mu:
                errors.append(f"model_and_units missing {key}")
        if not isinstance(mu.get("compatible_conditions", []), list):
            errors.append("model_and_units.compatible_conditions must be a list")

    # honesty blocks.
    for key in ("unverified_fields", "known_limitations"):
        value = spec[key]
        if not isinstance(value, list) or not value:
            errors.append(f"{key} must be a non-empty list")

    if "observables" in spec and not isinstance(spec["observables"], list):
        errors.append("observables must be a list")

    # actuation (optional): documented drive inputs; never executed by v1 tools.
    if "actuation" in spec:
        actuation = spec["actuation"]
        if not isinstance(actuation, dict):
            errors.append("actuation must be an object")
        else:
            if "mechanism" not in actuation:
                errors.append("actuation missing mechanism")
            pair = actuation.get("force_pair")
            if pair is not None:
                if not isinstance(pair, dict):
                    errors.append("actuation.force_pair must be an object")
                else:
                    for key in ("particle", "ref_particle", "status"):
                        if key not in pair:
                            errors.append(f"actuation.force_pair missing {key}")
                    for key in ("particle", "ref_particle"):
                        value = pair.get(key)
                        if key in pair and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
                            errors.append(f"actuation.force_pair.{key} must be a non-negative integer")
                    if _status_of(pair) not in CLAIM_STATUSES:
                        errors.append(f"actuation.force_pair.status must be one of {CLAIM_STATUSES}")

    return errors


def _validate_structure_block(block: object, label: str, required: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(block, dict):
        if required:
            errors.append(f"{label} must be an object")
        return errors
    status = _status_of(block)
    if status not in CLAIM_STATUSES:
        errors.append(f"{label}.status must be one of {CLAIM_STATUSES}")
    if status == "UNKNOWN":
        if block.get("sha256") not in (None, "UNKNOWN"):
            errors.append(f"{label} with status UNKNOWN must not carry a concrete sha256")
        if block.get("uri") not in (None, "UNKNOWN"):
            errors.append(f"{label} with status UNKNOWN must not carry a concrete uri")
        return errors
    for key in ("uri", "sha256", "nucleotides", "strand_count"):
        if key not in block:
            errors.append(f"{label} missing {key} (required unless status is UNKNOWN)")
    if "sha256" in block and not _is_sha256(block.get("sha256")):
        errors.append(f"{label}.sha256 must be a 64-hex sha256")
    for key in ("nucleotides", "strand_count"):
        value = block.get(key)
        if key in block and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
            errors.append(f"{label}.{key} must be a positive integer")
    return errors


def _validate_port(port: object, i: int, seen_ids: set) -> list[str]:
    errors: list[str] = []
    where = f"ports[{i}]"
    if not isinstance(port, dict):
        return [f"{where} must be an object"]
    for key in ("port_id", "role", "interface_type", "anchors", "orientation", "connection_capable", "status"):
        if key not in port:
            errors.append(f"{where} missing {key}")
    if errors:
        return errors
    pid = port["port_id"]
    if not isinstance(pid, str) or not pid.strip():
        errors.append(f"{where}.port_id must be a non-empty string")
    elif pid in seen_ids:
        errors.append(f"{where}.port_id duplicate: {pid!r}")
    else:
        seen_ids.add(pid)
    if port["role"] not in PORT_ROLES:
        errors.append(f"{where}.role must be one of {PORT_ROLES}")
    itype = port["interface_type"]
    if itype not in INTERFACE_TYPES:
        errors.append(f"{where}.interface_type must be one of {INTERFACE_TYPES}")
    status = _status_of(port)
    if status not in CLAIM_STATUSES:
        errors.append(f"{where}.status must be one of {CLAIM_STATUSES}")

    anchors = port["anchors"]
    if not isinstance(anchors, list) or not anchors:
        errors.append(f"{where}.anchors must be a non-empty list")
    else:
        for j, anchor in enumerate(anchors):
            awhere = f"{where}.anchors[{j}]"
            if not isinstance(anchor, dict):
                errors.append(f"{awhere} must be an object")
                continue
            for key in ("namespace", "index_space", "anchor", "status"):
                if key not in anchor:
                    errors.append(f"{awhere} missing {key}")
            if _status_of(anchor) not in CLAIM_STATUSES:
                errors.append(f"{awhere}.status must be one of {CLAIM_STATUSES}")
            anchor_value = anchor.get("anchor")
            if anchor_value != "UNKNOWN" and not isinstance(anchor_value, int):
                errors.append(f"{awhere}.anchor must be an integer index or the literal UNKNOWN")
            if anchor_value == "UNKNOWN" and _status_of(anchor) == "SOURCE_CONFIRMED":
                errors.append(f"{awhere}: a SOURCE_CONFIRMED anchor can never be the literal UNKNOWN")

    orientation = port["orientation"]
    if not isinstance(orientation, dict):
        errors.append(f"{where}.orientation must be an object")
    elif _status_of(orientation) not in CLAIM_STATUSES:
        errors.append(f"{where}.orientation.status must be one of {CLAIM_STATUSES}")

    # connection-capability gate: a well-formed numeric index alone never
    # makes a port physically connectable.
    capable = port["connection_capable"]
    if not isinstance(capable, bool):
        errors.append(f"{where}.connection_capable must be a boolean")
        return errors
    anchors_confirmed = bool(anchors) and all(
        isinstance(a, dict) and _status_of(a) == "SOURCE_CONFIRMED" and a.get("anchor") != "UNKNOWN"
        for a in anchors
    )
    orientation_confirmed = isinstance(orientation, dict) and _status_of(orientation) == "SOURCE_CONFIRMED"
    itype_known = itype in ASSEMBLER_SUPPORTED_INTERFACE_TYPES + COVALENT_INTERFACE_TYPES
    if capable:
        if not itype_known:
            errors.append(
                f"{where}: connection_capable=true requires a concrete interface type, got {itype!r}"
            )
        if not anchors_confirmed:
            errors.append(
                f"{where}: connection_capable=true requires all anchors SOURCE_CONFIRMED with "
                "concrete indices"
            )
        if not orientation_confirmed:
            errors.append(
                f"{where}: connection_capable=true requires orientation.status SOURCE_CONFIRMED"
            )
        if status not in ("SOURCE_CONFIRMED",):
            errors.append(f"{where}: connection_capable=true requires port status SOURCE_CONFIRMED")
    else:
        if itype_known and anchors_confirmed and orientation_confirmed and status == "SOURCE_CONFIRMED":
            errors.append(
                f"{where}: fully confirmed port must not be marked connection_capable=false "
                "(fail-closed in the other direction)"
            )
    chemistry = port.get("chemistry")
    if chemistry is not None:
        if not isinstance(chemistry, dict):
            errors.append(f"{where}.chemistry must be an object when present")
        else:
            if itype == "SS_DNA_OVERHANG_HYBRIDIZATION":
                for key in ("kind", "sequence"):
                    if key not in chemistry:
                        errors.append(f"{where}.chemistry missing {key}")
                seq = chemistry.get("sequence")
                if seq is not None and seq != "UNKNOWN" and not isinstance(seq, str):
                    errors.append(f"{where}.chemistry.sequence must be a string or UNKNOWN")
            elif itype != "UNKNOWN" and chemistry.get("kind") not in (None, "UNKNOWN"):
                errors.append(
                    f"{where}.chemistry is only meaningful for SS_DNA_OVERHANG_HYBRIDIZATION or UNKNOWN ports"
                )
    return errors


def verify_component_spec_against_repo(spec: object, repo_root: Path) -> list[str]:
    """Deterministic cross-checks against pinned surfaces.

    * The referenced KnowledgePack file must exist and match its digest.
    * Local (repo-relative) pinned topology/configuration files must exist and
      match their digests.
    * Remote-only pins (http/https URIs — raw source files are never vendored)
      are checked for digest format/provenance only; their bytes were verified
      at import time and recorded with ``sha256_provenance``.
    """
    errors: list[str] = []
    root = Path(repo_root)
    kpr = spec.get("knowledge_pack_ref", {})
    pack_path = root / kpr.get("pack_path", "")
    if not pack_path.exists():
        errors.append(f"knowledge pack file not found: {kpr.get('pack_path')!r}")
    elif sha256_file(pack_path) != kpr.get("pack_sha256"):
        errors.append("knowledge_pack_ref.pack_sha256 does not match the pack file bytes")
    for label in ("topology", "configuration"):
        block = spec.get(label)
        if not isinstance(block, dict) or _status_of(block) == "UNKNOWN":
            continue
        uri = str(block.get("uri", ""))
        if uri.startswith("http://") or uri.startswith("https://"):
            if block.get("sha256_provenance") not in ("CONTENT_VERIFIED", "REMOTE_UNVERIFIED"):
                errors.append(
                    f"{label} remote pin {uri!r} must declare sha256_provenance "
                    "CONTENT_VERIFIED or REMOTE_UNVERIFIED"
                )
            continue
        path = root / uri
        if not path.exists():
            errors.append(f"{label} pinned file not found: {uri!r}")
            continue
        actual = sha256_file(path)
        if actual != block.get("sha256"):
            errors.append(f"{label} digest mismatch: file {uri!r} has {actual}")
    return errors


def load_component_spec(path: Path) -> dict:
    """Load and strictly validate a spec file. Raises ComponentSpecError."""
    path = Path(path)
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComponentSpecError(f"cannot read component spec {path}: {exc}") from exc
    errors = validate_component_spec(spec)
    if errors:
        raise ComponentSpecError(f"invalid component spec {path}: " + "; ".join(errors))
    return spec
