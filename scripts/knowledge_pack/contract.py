"""KnowledgePack v1 — scoped prototype contract for audited literature sources.

PREP-S17 (WO-PREP-S17-R1). A KnowledgePack records the auditable identity of a
published source (paper + data + code repositories), its rights posture, the
exact pinned input files with digests, and the scientific model / observables
context needed before any import. It certifies AUDIT and PINNED IMPORT levels
only; it can never certify reproduction or mechanism function (fail-closed
claim ceiling, see CLAIM_LEVELS_V1).

This module is deliberately independent of the NL5 frozen tooling and of
scripts/hinge_family/pins.py (that registry pins the S16 hinge source for E2).
It reuses the project's provenance vocabulary style but does not import or
modify existing provenance/manifest/harness machinery.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PACK_SCHEMA_VERSION = 1
PACK_KIND = "knowledge_pack"

# Fail-closed claim ceiling: v1 packs support AUDIT/PIN levels only.
CLAIM_LEVELS_V1 = {
    "BIBLIOGRAPHIC",
    "RIGHTS_AND_INPUTS_AUDITED",
    "PINNED_IMPORT_VERIFIED",
}
# These levels describe scientific results and must never appear in a v1 pack.
FORBIDDEN_CLAIM_LEVELS = {
    "MODEL_REPRODUCED",
    "COMPONENT_CHARACTERIZED",
    "ASSEMBLY_VALIDATED",
}

REQUIRED_TOP_LEVEL = (
    "schema_version",
    "kind",
    "pack_id",
    "source_id",
    "source_version",
    "doi",
    "license",
    "rights",
    "input_file_manifest",
    "scientific_model",
    "simulation_engine",
    "topology_format",
    "configuration_format",
    "observables",
    "protocol_references",
    "missing_inputs",
    "known_limitations",
    "claim_level",
    "provenance",
)

MANIFEST_ROLES = {
    "DESIGN_TOPOLOGY",
    "STARTING_CONFIGURATION",
    "SIMULATION_INPUT",
    "ANALYSIS_CODE",
    "DOCUMENTATION",
    "DATA_PRODUCT",
}
AVAILABILITY = {"ON_DISK_VERIFIED", "REMOTE_ONLY", "MISSING"}
SHA256_PROVENANCE = {"CONTENT_VERIFIED", "UPSTREAM_METADATA", "NOT_VERIFIED"}
REDISTRIBUTION = {"ALLOWED", "RESTRICTED", "FORBIDDEN", "UNKNOWN"}
ACCESS_MODES = {"REFERENCE_ONLY", "DOWNLOAD_ON_SETUP", "VENDORED"}
OBSERVABLE_STATUS = {"DEFINED_IN_SOURCE", "PROPOSED", "UNVERIFIED"}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DOI_RE = re.compile(r"^10\.[0-9]{4,9}/\S+$")

REQUIRED_RIGHTS_KEYS = ("license", "redistribution", "access_mode", "notes")
REQUIRED_PROVENANCE_KEYS = (
    "audit_work_order",
    "audit_execution_id",
    "audit_date_utc",
    "audit_method",
    "base_repo_sha",
)


class KnowledgePackError(Exception):
    """Raised when a pack violates the KnowledgePack v1 contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_explicitly_unknown(value: object) -> bool:
    return isinstance(value, str) and value == "UNKNOWN"


def _require_non_empty_or_unknown(errors: list[str], where: str, value: object) -> None:
    if value is None:
        errors.append(f"{where}: null is forbidden; use explicit UNKNOWN")
    elif isinstance(value, str):
        if not value.strip():
            errors.append(f"{where}: empty string is forbidden; use explicit UNKNOWN")
    elif isinstance(value, (list, dict)):
        errors.append(f"{where}: expected scalar string")


def validate_pack(pack: object) -> list[str]:
    """Validate a KnowledgePack instance. Returns a list of contract violations.

    Empty list means the pack conforms. Fail-closed: any structural deviation,
    missing field, ambiguous value, or claim inflation is an error, never a
    warning.
    """
    errors: list[str] = []
    if not isinstance(pack, dict):
        return ["pack must be a JSON object"]

    if pack.get("schema_version") != PACK_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PACK_SCHEMA_VERSION}")
    if pack.get("kind") != PACK_KIND:
        errors.append(f'kind must be "{PACK_KIND}"')

    unknown_keys = set(pack) - set(REQUIRED_TOP_LEVEL)
    if unknown_keys:
        errors.append(f"unknown top-level fields require a contract revision: {sorted(unknown_keys)}")

    for key in REQUIRED_TOP_LEVEL:
        if key not in pack:
            errors.append(f"missing required field {key}")
    if errors:
        return errors

    for key in ("pack_id", "source_id", "source_version"):
        _require_non_empty_or_unknown(errors, key, pack[key])
        if pack[key] == "UNKNOWN":
            errors.append(f"{key} must be pinned, not UNKNOWN")

    doi = pack["doi"]
    _require_non_empty_or_unknown(errors, "doi", doi)
    if doi != "UNKNOWN" and not (isinstance(doi, str) and DOI_RE.match(doi)):
        errors.append("doi must be a valid DOI (10.xxxx/...) or the explicit string UNKNOWN")

    claim = pack["claim_level"]
    if claim in FORBIDDEN_CLAIM_LEVELS:
        errors.append(
            f"claim_level {claim} exceeds the v1 ceiling; a KnowledgePack never certifies "
            "reproduction/characterization/assembly — record it in a scientific WO instead"
        )
    elif claim not in CLAIM_LEVELS_V1:
        errors.append(f"claim_level must be one of {sorted(CLAIM_LEVELS_V1)}")

    # --- rights block -----------------------------------------------------
    rights = pack["rights"]
    if not isinstance(rights, dict):
        errors.append("rights must be an object")
        rights = {}
    for key in REQUIRED_RIGHTS_KEYS:
        if key not in rights:
            errors.append(f"rights missing {key}")
        elif key != "notes":
            _require_non_empty_or_unknown(errors, f"rights.{key}", rights[key])
    unknown_rights = set(rights) - set(REQUIRED_RIGHTS_KEYS)
    if unknown_rights:
        errors.append(f"rights has unknown fields: {sorted(unknown_rights)}")
    redistribution = rights.get("redistribution")
    if redistribution not in REDISTRIBUTION:
        errors.append(f"rights.redistribution must be one of {sorted(REDISTRIBUTION)}")
    mode = rights.get("access_mode")
    if mode not in ACCESS_MODES:
        errors.append(f"rights.access_mode must be one of {sorted(ACCESS_MODES)}")
    if redistribution == "FORBIDDEN" and mode == "VENDORED":
        errors.append("VENDORED access_mode is incompatible with redistribution FORBIDDEN")

    # --- input manifest ---------------------------------------------------
    manifest = pack["input_file_manifest"]
    if not isinstance(manifest, list) or not manifest:
        errors.append("input_file_manifest must be a non-empty list")
        manifest = []
    seen_paths: set[str] = set()
    on_disk_paths = 0
    for i, entry in enumerate(manifest):
        where = f"input_file_manifest[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be an object")
            continue
        unknown_entry = set(entry) - {
            "path", "size_bytes", "sha256", "role", "availability",
            "sha256_provenance", "source_url", "vendored", "upstream_checksum",
        }
        if unknown_entry:
            errors.append(f"{where}: unknown fields {sorted(unknown_entry)}")
        for key in ("path", "sha256", "role", "availability", "sha256_provenance"):
            if key not in entry:
                errors.append(f"{where}: missing {key}")
        path_value = entry.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            errors.append(f"{where}.path must be a non-empty string")
        elif path_value in seen_paths:
            errors.append(f"{where}.path duplicated: {path_value}")
        else:
            seen_paths.add(path_value)
        sha = entry.get("sha256")
        sha_unknown = sha == "UNKNOWN"
        if not isinstance(sha, str) or (not sha_unknown and not SHA256_RE.match(sha)):
            errors.append(f"{where}.sha256 must be 64 lowercase hex characters or the explicit string UNKNOWN")
        if sha_unknown and entry.get("sha256_provenance") != "NOT_VERIFIED":
            errors.append(f"{where}: sha256 UNKNOWN is only valid with sha256_provenance NOT_VERIFIED")
        upstream = entry.get("upstream_checksum")
        if upstream is not None:
            if (
                not isinstance(upstream, dict)
                or set(upstream) != {"algorithm", "value"}
                or upstream.get("algorithm") not in ("md5", "sha1", "sha256", "git_blob_sha1")
                or not isinstance(upstream.get("value"), str)
                or not upstream.get("value")
            ):
                errors.append(f"{where}.upstream_checksum must be {{algorithm, value}} with a known algorithm")
        if sha_unknown and upstream is None:
            errors.append(f"{where}: sha256 UNKNOWN requires an upstream_checksum record")
        size = entry.get("size_bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            errors.append(f"{where}.size_bytes must be a non-negative integer")
        if entry.get("role") not in MANIFEST_ROLES:
            errors.append(f"{where}.role must be one of {sorted(MANIFEST_ROLES)}")
        if entry.get("availability") not in AVAILABILITY:
            errors.append(f"{where}.availability must be one of {sorted(AVAILABILITY)}")
        if entry.get("sha256_provenance") not in SHA256_PROVENANCE:
            errors.append(f"{where}.sha256_provenance must be one of {sorted(SHA256_PROVENANCE)}")
        vendored = entry.get("vendored", False)
        if not isinstance(vendored, bool):
            errors.append(f"{where}.vendored must be a boolean")
        if vendored:
            if redistribution not in ("ALLOWED",):
                errors.append(
                    f"{where}: vendoring requires rights.redistribution ALLOWED "
                    f"(current: {redistribution})"
                )
            if entry.get("source_url") is None:
                errors.append(f"{where}: vendored entries must record source_url")
        if entry.get("availability") == "ON_DISK_VERIFIED":
            on_disk_paths += 1
            if entry.get("sha256_provenance") != "CONTENT_VERIFIED":
                errors.append(
                    f"{where}: ON_DISK_VERIFIED entries must have sha256_provenance CONTENT_VERIFIED"
                )
        if entry.get("availability") in ("REMOTE_ONLY", "MISSING") and entry.get("source_url") is None:
            errors.append(f"{where}: remote/missing entries must record source_url")

    # --- consistency between declared formats and the manifest ------------
    for fmt_key, role in (("topology_format", "DESIGN_TOPOLOGY"), ("configuration_format", "STARTING_CONFIGURATION")):
        fmt = pack.get(fmt_key)
        _require_non_empty_or_unknown(errors, fmt_key, fmt)
        if isinstance(fmt, str) and fmt != "UNKNOWN":
            if not any(
                e.get("role") == role and e.get("availability") in ("ON_DISK_VERIFIED", "REMOTE_ONLY")
                for e in manifest if isinstance(e, dict)
            ):
                errors.append(
                    f"{fmt_key} is declared ('{fmt}') but no {role} manifest entry is "
                    "ON_DISK_VERIFIED or REMOTE_ONLY"
                )

    # --- observables / protocol / gaps ------------------------------------
    observables = pack["observables"]
    if not isinstance(observables, list):
        errors.append("observables must be a list")
        observables = []
    for i, obs in enumerate(observables):
        where = f"observables[{i}]"
        if not isinstance(obs, dict):
            errors.append(f"{where}: must be an object")
            continue
        if set(obs) - {"name", "definition", "status", "definition_source"}:
            errors.append(f"{where}: unknown fields")
        for key in ("name", "status"):
            if key not in obs:
                errors.append(f"{where}: missing {key}")
        if obs.get("status") not in OBSERVABLE_STATUS:
            errors.append(f"{where}.status must be one of {sorted(OBSERVABLE_STATUS)}")
        if obs.get("status") == "DEFINED_IN_SOURCE" and not obs.get("definition_source"):
            errors.append(f"{where}: DEFINED_IN_SOURCE requires definition_source")

    missing_inputs = pack["missing_inputs"]
    if not isinstance(missing_inputs, list) or not all(isinstance(x, str) and x.strip() for x in missing_inputs):
        errors.append("missing_inputs must be a list of non-empty strings")
    if not observables and not missing_inputs:
        errors.append(
            "no observables recorded and no missing_inputs explanation: an empty "
            "observables list requires an explicit missing_inputs entry"
        )

    limitations = pack["known_limitations"]
    if not isinstance(limitations, list) or not all(isinstance(x, str) and x.strip() for x in limitations):
        errors.append("known_limitations must be a list of non-empty strings")

    for scalar_key in ("scientific_model", "simulation_engine", "license"):
        _require_non_empty_or_unknown(errors, scalar_key, pack[scalar_key])

    for list_key in ("protocol_references",):
        value = pack[list_key]
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
            errors.append(f"{list_key} must be a list of non-empty strings")

    provenance = pack["provenance"]
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
        provenance = {}
    for key in REQUIRED_PROVENANCE_KEYS:
        if key not in provenance:
            errors.append(f"provenance missing {key}")
        else:
            _require_non_empty_or_unknown(errors, f"provenance.{key}", provenance[key])
    if provenance.get("base_repo_sha") != "UNKNOWN" and not re.match(r"^[0-9a-f]{40}$", str(provenance.get("base_repo_sha", ""))):
        errors.append("provenance.base_repo_sha must be a 40-hex commit SHA or UNKNOWN")

    return errors


def verify_manifest(root: Path, pack: object) -> list[str]:
    """Re-verify digests of every ON_DISK_VERIFIED manifest entry under root.

    Deterministic: recomputes SHA-256 from bytes. Any digest/size deviation is
    an error (fail-closed).
    """
    errors: list[str] = []
    if not isinstance(pack, dict):
        return ["pack must be a JSON object"]
    manifest = pack.get("input_file_manifest")
    if not isinstance(manifest, list):
        return ["input_file_manifest must be a list"]
    for entry in manifest:
        if not isinstance(entry, dict) or entry.get("availability") != "ON_DISK_VERIFIED":
            continue
        rel = entry.get("path")
        path = root / str(rel)
        where = f"manifest[{rel}]"
        if not path.is_file():
            errors.append(f"{where}: pinned file missing on disk")
            continue
        actual = sha256_file(path)
        if actual != entry.get("sha256"):
            errors.append(f"{where}: sha256 mismatch (expected {entry.get('sha256')}, got {actual})")
        expected_size = entry.get("size_bytes")
        actual_size = path.stat().st_size
        if expected_size != actual_size:
            errors.append(f"{where}: size mismatch (expected {expected_size}, got {actual_size})")
    return errors


def load_pack(path: Path) -> dict:
    """Load a pack JSON file and contract-check it. Raises KnowledgePackError."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
        pack = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise KnowledgePackError(f"pack unreadable or not JSON: {exc}") from exc
    errors = validate_pack(pack)
    if errors:
        raise KnowledgePackError("pack violates KnowledgePack v1 contract: " + "; ".join(errors))
    return pack
