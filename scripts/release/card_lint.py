"""NanoLab release contract linter (stdlib-only).

R1.2 hardening:
- fail-closed schema execution;
- S1..S5 component semantics;
- deterministic manifest creation (no wall-clock field by default);
- duplicate and unsafe manifest paths rejected before mapping;
- manifest digests/sizes recomputed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from release import mini_schema

REPO_ROOT = Path(__file__).resolve().parents[2]
CARD_SCHEMA = REPO_ROOT / "schemas" / "components" / "component-card.v1.json"
RIGHTS_SCHEMA = REPO_ROOT / "schemas" / "release" / "rights.v1.json"
MANIFEST_SCHEMA = REPO_ROOT / "schemas" / "release" / "release-manifest.v1.json"
MANIFEST_NAME = "RELEASE_MANIFEST.json"
RIGHTS_NAME = "RIGHTS.json"
VERSION_NAME = "VERSION"
CITATION_NAME = "CITATION.cff"
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
ROLE_PREFIXES = (
    ("schema/", "schema"),
    ("protocols/", "protocol"),
    ("reports/", "report"),
    ("provenance/", "provenance"),
    ("reproduction/", "reproduction"),
)


class LintFailure(Exception):
    pass


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LintFailure(f"{path}: cannot load JSON ({exc})") from exc


def _load_schema(path: Path, label: str) -> dict[str, Any]:
    schema = _load_json(path)
    errors = mini_schema.lint_schema(schema, path=str(path))
    if errors:
        raise LintFailure(f"{label} schema at {path} uses unsupported constructs: {errors}")
    return schema


def _check_rel_path(path_text: str, where: str, errors: list[str]) -> None:
    if not path_text:
        errors.append(f"{where}: empty path")
        return
    if path_text.startswith(("/", "\\")) or (len(path_text) > 1 and path_text[1] == ":"):
        errors.append(f"{where}: path must be relative: {path_text!r}")
    if "\\" in path_text:
        errors.append(f"{where}: path must use POSIX separators: {path_text!r}")
    if ".." in Path(path_text).parts:
        errors.append(f"{where}: path must not contain '..': {path_text!r}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Cards


def validate_card(card: Any, schema: dict[str, Any], origin: str) -> list[str]:
    errors = mini_schema.validate(card, schema, path=origin)
    if errors:
        return errors

    measurement = card["measurement_status"]
    observables = card["measured_observables"]
    if measurement in ("MEASURED", "MEASURED_STATISTICALLY_VALIDATED"):
        if not observables:
            errors.append(f"{origin}: measurement_status={measurement} but measured_observables is empty (S1)")
        for name, observable in observables.items():
            if not observable.get("source"):
                errors.append(f"{origin}: observable {name!r} has no source path (S1)")
        if not card["reproduction"]["expected"]:
            errors.append(f"{origin}: measurement_status={measurement} but reproduction.expected is empty (S1)")

    if measurement == "NOT_MEASURED" and not card["known_gaps"]:
        errors.append(f"{origin}: NOT_MEASURED card must declare known_gaps (S2)")

    rights = card["rights"]
    if rights["rights_mode"] in ("REFERENCE_ONLY", "DOWNLOAD_ON_RUN", "MIXED"):
        if not rights.get("upstream_repo"):
            errors.append(f"{origin}: rights_mode={rights['rights_mode']} requires upstream_repo (S3)")
        if not rights.get("pinned_commit"):
            errors.append(f"{origin}: rights_mode={rights['rights_mode']} requires pinned_commit (S3)")
        if rights["durable_cache"] != "FORBIDDEN":
            errors.append(f"{origin}: rights_mode={rights['rights_mode']} requires durable_cache=FORBIDDEN (S3)")

    if card["claim_ceiling"] == "C1_COMPUTATIONAL_REPRODUCTION" and measurement not in (
        "MEASURED",
        "MEASURED_STATISTICALLY_VALIDATED",
    ):
        errors.append(f"{origin}: C1_COMPUTATIONAL_REPRODUCTION requires measured data (S4)")

    for gate_path, digest in card.get("source_provenance", {}).get("digest_gates", {}).items():
        has_sha = "sha256" in digest
        has_status = "sha256_status" in digest
        if has_sha != has_status:
            errors.append(f"{origin}: digest {gate_path!r}: sha256 and sha256_status must be provided together (S5)")

    return errors


def run_card(paths: list[Path], schema_path: Path) -> dict[str, Any]:
    schema = _load_schema(schema_path, "component card")
    errors: list[str] = []
    checked: list[str] = []
    for path in paths:
        errors.extend(validate_card(_load_json(path), schema, origin=str(path)))
        checked.append(str(path))
    return {"command": "CARD", "checked": checked, "ok": not errors, "errors": errors}


# ---------------------------------------------------------------------------
# Rights


def validate_rights(rights: Any, schema: dict[str, Any], origin: str) -> tuple[list[str], list[str]]:
    errors = mini_schema.validate(rights, schema, path=origin)
    warnings: list[str] = []
    if errors:
        return errors, warnings
    for index, item in enumerate(rights["items"]):
        where = f"{origin}.items[{index}]"
        _check_rel_path(item["path"], where, errors)
        if item["rights_mode"] == "REFERENCE_ONLY":
            if not item.get("upstream_repo") or not item.get("pinned_commit"):
                errors.append(f"{where}: REFERENCE_ONLY item requires upstream_repo and pinned_commit")
    if (
        rights["own_code_license"] == "UNDECIDED_PENDING_OWNER_DECISION"
        or rights["own_docs_data_license"] == "UNDECIDED_PENDING_OWNER_DECISION"
    ):
        warnings.append(
            f"{origin}: own license UNDECIDED_PENDING_OWNER_DECISION (owner license decision D2)"
            " — package is draft-only; public release blocked until D2"
        )
    return errors, warnings


def run_rights(path: Path, schema_path: Path) -> dict[str, Any]:
    schema = _load_schema(schema_path, "rights")
    errors, warnings = validate_rights(_load_json(path), schema, origin=str(path))
    return {"command": "RIGHTS", "checked": [str(path)], "ok": not errors, "errors": errors, "warnings": warnings}


# ---------------------------------------------------------------------------
# Manifest


def _package_files(pkg_root: Path) -> list[Path]:
    return sorted(p for p in pkg_root.rglob("*") if p.is_file() and p.name != MANIFEST_NAME)


def _role_for(rel_path: str, file_name: str) -> str:
    if rel_path == RIGHTS_NAME:
        return "rights"
    if rel_path == CITATION_NAME:
        return "citation"
    if rel_path == VERSION_NAME:
        return "metadata"
    for prefix, role in ROLE_PREFIXES:
        if rel_path.startswith(prefix):
            return role
    if rel_path.startswith("families/"):
        return "card" if file_name.endswith(".card.json") else "family"
    return "other"


def _read_version(pkg_root: Path) -> str:
    try:
        return (pkg_root / VERSION_NAME).read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise LintFailure(f"cannot read VERSION: {exc}") from exc


def manifest_create(
    pkg_root: Path,
    generated_by: str = "release.card_lint manifest create deterministic-r1.2",
    *,
    subject: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    """Create deterministic manifest bytes from package bytes and frozen metadata.

    No wall-clock value is emitted. Optional subject must itself be frozen input.
    """
    files = []
    for path in _package_files(pkg_root):
        rel = path.relative_to(pkg_root).as_posix()
        files.append({"path": rel, "sha256": _sha256(path), "size_bytes": path.stat().st_size, "role": _role_for(rel, path.name)})
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "kind": "nanolab_release_manifest",
        "package": "nanolab-components",
        "package_version": _read_version(pkg_root),
        "generated_by": generated_by,
        "files": files,
    }
    if subject:
        manifest["subject"] = subject
    return manifest


def manifest_verify(pkg_root: Path, schema_path: Path) -> dict[str, Any]:
    schema = _load_schema(schema_path, "release manifest")
    manifest_path = pkg_root / MANIFEST_NAME
    manifest = _load_json(manifest_path)
    errors = mini_schema.validate(manifest, schema, path=str(manifest_path))
    if errors:
        return {"command": "MANIFEST_VERIFY", "ok": False, "errors": errors}

    entries = manifest["files"]
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        rel = entry["path"]
        _check_rel_path(rel, f"{manifest_path}.files[{index}].path", errors)
        if rel in seen:
            errors.append(f"{manifest_path}: duplicate path entry {rel!r}")
        seen.add(rel)

    if errors:
        return {"command": "MANIFEST_VERIFY", "ok": False, "errors": errors}

    listed = {entry["path"]: entry for entry in entries}
    actual = {p.relative_to(pkg_root).as_posix(): p for p in _package_files(pkg_root)}
    version = _read_version(pkg_root)
    if manifest["package_version"] != version:
        errors.append(f"{manifest_path}: package_version {manifest['package_version']!r} != VERSION {version!r}")
    for rel in sorted(set(listed) - set(actual)):
        errors.append(f"{manifest_path}: manifest lists missing file {rel!r}")
    for rel in sorted(set(actual) - set(listed)):
        errors.append(f"{manifest_path}: file not in manifest: {rel!r}")
    for rel in sorted(set(listed) & set(actual)):
        entry = listed[rel]
        path = actual[rel]
        if _sha256(path) != entry["sha256"]:
            errors.append(f"{manifest_path}: sha256 mismatch for {rel!r}")
        if path.stat().st_size != entry["size_bytes"]:
            errors.append(f"{manifest_path}: size_bytes mismatch for {rel!r}")
    return {"command": "MANIFEST_VERIFY", "ok": not errors, "errors": errors, "files": len(entries)}


# ---------------------------------------------------------------------------
# Package


def _check_family_file(path: Path) -> list[str]:
    family = _load_json(path)
    errors: list[str] = []
    if not isinstance(family, dict):
        return [f"{path}: family.json must be a JSON object"]
    variants = family.get("variants")
    status = family.get("variant_status")
    if not isinstance(family.get("family_id"), str) or not family.get("family_id"):
        errors.append(f"{path}: missing family_id")
    if not isinstance(variants, list) or not variants:
        errors.append(f"{path}: variants must be a non-empty array")
    if not isinstance(status, dict):
        errors.append(f"{path}: variant_status must be an object")
    elif isinstance(variants, list) and sorted(status) != sorted(map(str, variants)):
        errors.append(f"{path}: variant_status keys {sorted(status)} != variants {sorted(variants)}")
    return errors


def run_package(pkg_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    pkg_root = pkg_root.resolve()
    version = _read_version(pkg_root)
    if not SEMVER_PATTERN.match(version):
        errors.append(f"{pkg_root / VERSION_NAME}: content {version!r} is not semver")

    for required in (CITATION_NAME, RIGHTS_NAME, "schema/components/component-card.v1.json", MANIFEST_NAME):
        if not (pkg_root / required).is_file():
            errors.append(f"{pkg_root}: missing required package file {required!r}")

    card_schema_path = pkg_root / "schema" / "components" / "component-card.v1.json"
    schema_source = card_schema_path if card_schema_path.is_file() else CARD_SCHEMA
    if card_schema_path.is_file() and card_schema_path.read_bytes() != CARD_SCHEMA.read_bytes():
        warnings.append(f"{card_schema_path}: packaged schema snapshot differs from repo schema")

    schema = _load_schema(schema_source, "component card")
    card_paths = sorted((pkg_root / "families").rglob("*.card.json")) if (pkg_root / "families").is_dir() else []
    card_results: list[str] = []
    cards_by_family: dict[str, set[str]] = {}
    variant_status: dict[str, str] = {}
    if not card_paths:
        errors.append(f"{pkg_root}: no component cards found")
    for path in card_paths:
        rel = path.relative_to(pkg_root).as_posix()
        card = _load_json(path)
        card_errors = validate_card(card, schema, origin=rel)
        errors.extend(card_errors)
        card_results.append(rel)
        if not card_errors:
            cards_by_family.setdefault(str(card.get("family")), set()).add(str(card.get("variant")))
            variant_status[str(card.get("variant"))] = str(card.get("measurement_status"))

    family_paths = sorted((pkg_root / "families").rglob("family.json")) if (pkg_root / "families").is_dir() else []
    for family_path in family_paths:
        errors.extend(_check_family_file(family_path))
        family = _load_json(family_path)
        family_id = str(family.get("family_id", ""))
        declared = set(map(str, family.get("variants", [])))
        present = cards_by_family.get(family_id, set())
        for variant in sorted(declared - present):
            errors.append(f"{family_path}: declared variant {variant!r} has no card (I1)")
        for variant in sorted(present - declared):
            errors.append(f"{family_path}: card variant {variant!r} is not declared (I2)")

    rights_result = run_rights(pkg_root / RIGHTS_NAME, RIGHTS_SCHEMA)
    errors.extend(rights_result["errors"])
    warnings.extend(rights_result.get("warnings", []))
    manifest_result = manifest_verify(pkg_root, MANIFEST_SCHEMA)
    errors.extend(manifest_result["errors"])
    return {
        "command": "PACKAGE",
        "package_root": str(pkg_root),
        "version": version,
        "cards": card_results,
        "variant_status": variant_status,
        "warnings": warnings,
        "ok": not errors,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="release.card_lint")
    sub = parser.add_subparsers(dest="command", required=True)
    p_card = sub.add_parser("card")
    p_card.add_argument("files", nargs="+")
    p_card.add_argument("--schema", default=str(CARD_SCHEMA))
    p_rights = sub.add_parser("rights")
    p_rights.add_argument("file")
    p_rights.add_argument("--schema", default=str(RIGHTS_SCHEMA))
    p_manifest = sub.add_parser("manifest")
    p_manifest.add_argument("mode", choices=["create", "verify"])
    p_manifest.add_argument("pkg_root")
    p_manifest.add_argument("--schema", default=str(MANIFEST_SCHEMA))
    p_manifest.add_argument("--stdout", action="store_true")
    p_package = sub.add_parser("package")
    p_package.add_argument("pkg_root")
    args = parser.parse_args(argv)

    try:
        if args.command == "card":
            report = run_card([Path(p) for p in args.files], Path(args.schema))
        elif args.command == "rights":
            report = run_rights(Path(args.file), Path(args.schema))
        elif args.command == "manifest":
            pkg_root = Path(args.pkg_root)
            if args.mode == "create":
                manifest = manifest_create(pkg_root)
                if args.stdout:
                    report = {"command": "MANIFEST_CREATE", "ok": True, "manifest": manifest}
                else:
                    out = pkg_root / MANIFEST_NAME
                    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                    report = {"command": "MANIFEST_CREATE", "ok": True, "written": str(out), "files": len(manifest["files"])}
            else:
                report = manifest_verify(pkg_root, Path(args.schema))
        else:
            report = run_package(Path(args.pkg_root))
    except LintFailure as exc:
        report = {"ok": False, "errors": [str(exc)]}
        print(json.dumps({"schema": "nanolab.release_lint_output.v1", **report}, ensure_ascii=False, indent=2))
        return 3

    print(json.dumps({"schema": "nanolab.release_lint_output.v1", **report}, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 3


if __name__ == "__main__":
    sys.exit(main())
