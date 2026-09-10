"""Pinned-source registry loader for the NanoLab hinge family (NL3-001).

Fail-closed: any structural deviation of the registry is an error, never a
warning. The registry records digests of the Shi-Castro-Arya source surfaces
(gauravarya77/DNA-hinge-simulations) in REFERENCE_ONLY mode; source bytes are
never stored in NanoLab.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

BLOB_PROVENANCE = {"NL0_001_PREREGISTERED", "R1_TREE_LISTING"}
SHA256_PROVENANCE = {"NL0_001_PREREGISTERED", "R1_TREE_LISTING", "R1_CONTENT_VERIFIED", "NOT_VERIFIED"}

REQUIRED_SOURCE_KEYS = ("repository", "commit", "tree", "rights", "mode", "obtain_procedure")
REQUIRED_FILE_KEYS = ("size_bytes", "blob_sha1", "sha256", "blob_sha1_provenance", "sha256_provenance")
REQUIRED_VARIANT_KEYS = ("role", "topology", "configuration", "design", "spring_layers_reported_bases", "spring_layers_source")


class PinsError(Exception):
    """Raised when the pinned-source registry deviates from its contract."""


def git_blob_sha1(data: bytes) -> str:
    """Git object SHA-1 of a blob with the given content."""
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_pins(path: Path) -> dict:
    """Load and contract-check the pins registry. Raises PinsError on any deviation."""
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise PinsError(f"pins registry unreadable or not JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PinsError("pins registry must be a JSON object")

    for key in ("schema_version", "registry_id", "source", "files", "variants"):
        if key not in data:
            raise PinsError(f"pins registry missing {key}")
    if data["schema_version"] != 1:
        raise PinsError("unsupported pins schema_version")

    source = data["source"]
    if not isinstance(source, dict):
        raise PinsError("pins source must be an object")
    for key in REQUIRED_SOURCE_KEYS:
        if key not in source or not isinstance(source[key], str) or not source[key]:
            raise PinsError(f"pins source missing {key}")
    if not SHA1_RE.match(source["commit"]) or not SHA1_RE.match(source["tree"]):
        raise PinsError("pins source commit/tree must be 40-hex SHA-1")
    if source["rights"] != "UNKNOWN" or source["mode"] != "REFERENCE_ONLY":
        raise PinsError("pins source must record rights UNKNOWN and mode REFERENCE_ONLY")

    files = data["files"]
    if not isinstance(files, dict) or not files:
        raise PinsError("pins files must be a non-empty object")
    for path_str, entry in sorted(files.items()):
        if not isinstance(entry, dict):
            raise PinsError(f"pins file {path_str} must be an object")
        for key in REQUIRED_FILE_KEYS:
            if key not in entry:
                raise PinsError(f"pins file {path_str} missing {key}")
        if not isinstance(entry["size_bytes"], int) or entry["size_bytes"] <= 0:
            raise PinsError(f"pins file {path_str} size_bytes must be a positive integer")
        if not SHA1_RE.match(str(entry["blob_sha1"])):
            raise PinsError(f"pins file {path_str} blob_sha1 must be 40-hex SHA-1")
        if entry["blob_sha1_provenance"] not in BLOB_PROVENANCE:
            raise PinsError(f"pins file {path_str} has unknown blob_sha1_provenance")
        sha256 = entry["sha256"]
        if sha256 is not None:
            if not isinstance(sha256, str) or not SHA256_RE.match(sha256):
                raise PinsError(f"pins file {path_str} sha256 must be null or 64-hex")
            if entry["sha256_provenance"] not in SHA256_PROVENANCE - {"NOT_VERIFIED"}:
                raise PinsError(f"pins file {path_str} sha256 present but provenance not a verification class")
        elif entry["sha256_provenance"] != "NOT_VERIFIED":
            raise PinsError(f"pins file {path_str} sha256 null but provenance not NOT_VERIFIED")

    variants = data["variants"]
    if not isinstance(variants, dict) or not variants:
        raise PinsError("pins variants must be a non-empty object")
    for name, entry in sorted(variants.items()):
        if not isinstance(entry, dict):
            raise PinsError(f"pins variant {name} must be an object")
        for key in REQUIRED_VARIANT_KEYS:
            if key not in entry:
                raise PinsError(f"pins variant {name} missing {key}")
        layers = entry["spring_layers_reported_bases"]
        if not isinstance(layers, list) or len(layers) != 2 or not all(isinstance(x, int) for x in layers):
            raise PinsError(f"pins variant {name} spring_layers_reported_bases must be two integers")
        for key in ("topology", "configuration", "design"):
            target = entry[key]
            if target not in files:
                raise PinsError(f"pins variant {name} references unregistered file {target}")
    return data


def variant_surface(pins: dict, variant: str) -> dict:
    """Return the validation surface (file paths) for one variant."""
    if variant not in pins["variants"]:
        raise PinsError(f"variant {variant} not registered")
    return pins["variants"][variant]


def verify_source_file(path: Path, entry: dict) -> dict:
    """Digest-verify one downloaded source file against its pin entry.

    All recorded digests (size, sha256 when present, git blob SHA-1) must match;
    any mismatch is a failure of the result, never a warning.
    """
    result = {"size_ok": False, "sha256_ok": None, "blob_sha1_ok": False, "observed": {}}
    try:
        data = path.read_bytes()
    except OSError as exc:
        result["read_error"] = str(exc)
        return result
    result["observed"]["size_bytes"] = len(data)
    result["size_ok"] = len(data) == entry["size_bytes"]
    result["observed"]["blob_sha1"] = git_blob_sha1(data)
    result["blob_sha1_ok"] = result["observed"]["blob_sha1"] == entry["blob_sha1"]
    if entry["sha256"] is not None:
        result["observed"]["sha256"] = sha256_hex(data)
        result["sha256_ok"] = result["observed"]["sha256"] == entry["sha256"]
    return result
