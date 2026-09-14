"""NanoLab release contract linter (stdlib-only).

Executes the normative release schemas (via release.mini_schema) plus the
semantic cross-field rules of docs/release/RELEASE_CONTRACT_V0_1.md that
the mini executor subset cannot express. Fail-closed: unknown schema
keywords are errors, manifest digests are recomputed, path rules are
enforced.

Usage (from repo root):
    PYTHONPATH=scripts python3 -m release.card_lint card FILE [FILE...]
    PYTHONPATH=scripts python3 -m release.card_lint rights RIGHTS_JSON
    PYTHONPATH=scripts python3 -m release.card_lint manifest create PKG_ROOT
    PYTHONPATH=scripts python3 -m release.card_lint manifest verify PKG_ROOT
    PYTHONPATH=scripts python3 -m release.card_lint package PKG_ROOT

Exit codes: 0 = ok, 3 = validation failure (harness style), 2 = usage error.
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
# Repair R1 (finding F-B2): a manifest timestamp is frozen release metadata,
# never wall-clock. The caller must pass an explicit ISO-8601 UTC stamp.
UTC_STAMP_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
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
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise LintFailure(f"{path}: cannot load JSON ({exc})") from exc


def _load_schema(path: Path, label: str) -> dict[str, Any]:
    schema = _load_json(path)
    scan_errors = mini_schema.lint_schema(schema, path=str(path))
    if scan_errors:
        raise LintFailure(f"{label} schema at {path} uses unsupported constructs: {scan_errors}")
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
# cards


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
            errors.append(
                f"{origin}: rights_mode={rights['rights_mode']} requires durable_cache=FORBIDDEN (S3, G1 decision)"
            )

    if card["claim_ceiling"] == "C1_COMPUTATIONAL_REPRODUCTION" and measurement not in (
        "MEASURED",
        "MEASURED_STATISTICALLY_VALIDATED",
    ):
        errors.append(
            f"{origin}: claim_ceiling=C1_COMPUTATIONAL_REPRODUCTION requires measured data, got measurement_status={measurement} (S4)"
        )

    for gap in card["known_gaps"]:
        _check_rel_path(str(gap.get("gap_id", "")), f"{origin}: known_gap {gap.get('gap_id')!r}", errors)

    # S5 (amendment R1.1): a sha256 claim without its verification level (or the
    # reverse) is a half-claim; the registry pin remains blob_sha1.
    for gate_path, digest in card.get("source_provenance", {}).get("digest_gates", {}).items():
        has_sha256 = "sha256" in digest
        has_status = "sha256_status" in digest
        if has_sha256 != has_status:
            errors.append(
                f"{origin}: digest {gate_path!r}: sha256 and sha256_status must be provided together (S5)"
            )

    return errors


def run_card(paths: list[Path], schema_path: Path) -> dict[str, Any]:
    schema = _load_schema(schema_path, "component card")
    errors: list[str] = []
    checked: list[str] = []
    for path in paths:
        card = _load_json(path)
        errors.extend(validate_card(card, schema, origin=str(path)))
        checked.append(str(path))
    return {"command": "CARD", "checked": checked, "ok": not errors, "errors": errors}


# ---------------------------------------------------------------------------
# rights


def validate_rights(rights: Any, schema: dict[str, Any], origin: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). UNDECIDED own licenses are a legal draft state
    (program D2) — publication-blocking process rule, not a file-level error."""
    errors = mini_schema.validate(rights, schema, path=origin)
    warnings: list[str] = []
    if errors:
        return errors, warnings
    for index, item in enumerate(rights["items"]):
        where = f"{origin}.items[{index}]"
        _check_rel_path(item["path"], where, errors)
        if item["rights_mode"] == "REFERENCE_ONLY":
            if not item.get("upstream_repo") or not item.get("pinned_commit"):
                errors.append(
                    f"{where}: REFERENCE_ONLY item requires upstream_repo and pinned_commit (40-hex)"
                )
    if (
        rights["own_code_license"] == "UNDECIDED_PENDING_OWNER_DECISION"
        or rights["own_docs_data_license"] == "UNDECIDED_PENDING_OWNER_DECISION"
    ):
        warnings.append(
            f"{origin}: own license UNDECIDED_PENDING_OWNER_DECISION (program D2) — the package is "
            "draft-only and MUST NOT be published until the owner decision is recorded"
        )
    return errors, warnings


def run_rights(path: Path, schema_path: Path) -> dict[str, Any]:
    schema = _load_schema(schema_path, "rights")
    rights = _load_json(path)
    errors, warnings = validate_rights(rights, schema, origin=str(path))
    return {"command": "RIGHTS", "checked": [str(path)], "ok": not errors, "errors": errors, "warnings": warnings}


# ---------------------------------------------------------------------------
# manifest


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
    version_path = pkg_root / VERSION_NAME
    try:
        return version_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise LintFailure(f"{version_path}: cannot read VERSION ({exc})") from exc


def manifest_create(
    pkg_root: Path,
    generated_at_utc: str,
    generated_by: str = "release.card_lint manifest create",
    subject: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic manifest: a pure function of (payload files, version,
    frozen stamp, subject). There is intentionally NO default timestamp: a
    wall-clock ``now()`` would make regeneration non-reproducible (F-B2)."""
    if not isinstance(generated_at_utc, str) or not UTC_STAMP_PATTERN.match(generated_at_utc):
        raise LintFailure(f"generated_at_utc {generated_at_utc!r} must be an ISO-8601 UTC stamp (YYYY-MM-DDTHH:MM:SSZ)")
    version = _read_version(pkg_root)
    files = []
    for path in _package_files(pkg_root):
        rel = path.relative_to(pkg_root).as_posix()
        files.append(
            {
                "path": rel,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
                "role": _role_for(rel, path.name),
            }
        )
    manifest = {
        "schema_version": 1,
        "kind": "nanolab_release_manifest",
        "package": "nanolab-components",
        "package_version": version,
        "generated_at_utc": generated_at_utc,
        "generated_by": generated_by,
        "files": files,
    }
    if subject is not None:
        manifest["subject"] = {str(key): str(value) for key, value in subject.items()}
    return manifest


def manifest_verify(pkg_root: Path, schema_path: Path) -> dict[str, Any]:
    schema = _load_schema(schema_path, "release manifest")
    manifest_path = pkg_root / MANIFEST_NAME
    manifest = _load_json(manifest_path)
    errors = mini_schema.validate(manifest, schema, path=str(manifest_path))
    if errors:
        return {"command": "MANIFEST_VERIFY", "ok": False, "errors": errors}

    # Repair R1 (finding F-B6), fail-closed BEFORE any dict conversion: path
    # semantics and duplicate rejection on the raw entry list. A dict keyed by
    # path would silently collapse duplicate entries, letting a conflicting
    # duplicate hide behind the last record.
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for index, entry in enumerate(manifest["files"]):
        where = f"{manifest_path}.files[{index}]"
        path_text = entry.get("path") if isinstance(entry, dict) else None
        if not isinstance(path_text, str):
            errors.append(f"{where}: path must be a string")
            continue
        _check_rel_path(path_text, where, errors)
        if path_text in seen:
            duplicates.append(path_text)
            errors.append(
                f"{where}: duplicate manifest path {path_text!r} (first seen at files[{seen[path_text]}])"
            )
        else:
            seen[path_text] = index
    if duplicates:
        # Never evaluate a manifest whose file list is not bijective with the
        # package: fail closed without partial verification results.
        return {"command": "MANIFEST_VERIFY", "ok": False, "errors": errors, "files": len(manifest["files"])}

    listed = seen
    actual = {p.relative_to(pkg_root).as_posix(): p for p in _package_files(pkg_root)}

    version = _read_version(pkg_root)
    if manifest["package_version"] != version:
        errors.append(f"{manifest_path}: package_version {manifest['package_version']!r} != {VERSION_NAME} content {version!r}")

    for rel in sorted(set(listed) - set(actual)):
        errors.append(f"{manifest_path}: manifest lists missing file {rel!r}")
    for rel in sorted(set(actual) - set(listed)):
        errors.append(f"{manifest_path}: file not in manifest: {rel!r}")
    for rel in sorted(set(listed) & set(actual)):
        entry = manifest["files"][listed[rel]]
        path = actual[rel]
        digest = _sha256(path)
        if digest != entry["sha256"]:
            errors.append(f"{manifest_path}: sha256 mismatch for {rel!r}")
        if path.stat().st_size != entry["size_bytes"]:
            errors.append(f"{manifest_path}: size_bytes mismatch for {rel!r}")

    return {"command": "MANIFEST_VERIFY", "ok": not errors, "errors": errors, "files": len(listed)}


# ---------------------------------------------------------------------------
# package


def _check_family_file(path: Path, variants_seen: dict[str, str]) -> list[str]:
    family = _load_json(path)
    errors: list[str] = []
    if not isinstance(family, dict):
        return [f"{path}: family.json must be a JSON object"]
    family_id = family.get("family_id")
    if not isinstance(family_id, str) or not family_id:
        errors.append(f"{path}: missing family_id")
    variants = family.get("variants")
    if not isinstance(variants, list) or not variants:
        errors.append(f"{path}: variants must be a non-empty array")
    status = family.get("variant_status")
    if not isinstance(status, dict):
        errors.append(f"{path}: variant_status must be an object")
    else:
        if variants and sorted(status) != sorted(map(str, variants)):
            errors.append(f"{path}: variant_status keys {sorted(status)} != variants {sorted(variants)}")
        for variant, value in status.items():
            variants_seen[variant] = str(value)
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
    if card_schema_path.is_file() and card_schema_path.read_bytes() == CARD_SCHEMA.read_bytes():
        pass
    elif card_schema_path.is_file():
        warnings.append(
            f"{card_schema_path}: packaged schema snapshot differs from repo schema {CARD_SCHEMA}; "
            "allowed for pinned releases, record the reason in the package changelog"
        )

    card_results: list[str] = []
    variants_seen: dict[str, str] = {}
    card_paths = sorted((pkg_root / "families").rglob("*.card.json")) if (pkg_root / "families").is_dir() else []
    if not card_paths:
        errors.append(f"{pkg_root}: no component cards found under families/")
    schema = _load_schema(schema_source, "component card")
    for path in card_paths:
        card_errors = validate_card(_load_json(path), schema, origin=path.relative_to(pkg_root).as_posix())
        errors.extend(card_errors)
        card_results.append(path.relative_to(pkg_root).as_posix())
        if not card_errors:
            card = _load_json(path)
            variants_seen.setdefault(str(card.get("variant")), str(card.get("measurement_status")))

    for family_path in sorted((pkg_root / "families").rglob("family.json")) if (pkg_root / "families").is_dir() else []:
        errors.extend(_check_family_file(family_path, variants_seen))

    # Invariants I1/I2 (contract §7): a declared variant must have a card file,
    # and a card's variant must be declared by its family — a family is one
    # family with variants, never a bag of unrelated cards.
    for family_path in sorted((pkg_root / "families").rglob("family.json")) if (pkg_root / "families").is_dir() else []:
        family = _load_json(family_path)
        family_id = str(family.get("family_id", ""))
        cards_dir = family_path.parent / "cards"
        for variant in map(str, family.get("variants", [])):
            card_path = cards_dir / f"{variant}.card.json"
            if not card_path.is_file():
                errors.append(f"{family_path}: variant {variant!r} declared but {card_path.relative_to(pkg_root).as_posix()} is missing (I1)")
        declared_by_family = set(map(str, family.get("variants", [])))
        for path in card_paths:
            relative = path.relative_to(pkg_root).as_posix()
            card = _load_json(path)
            if str(card.get("family")) == family_id and str(card.get("variant")) not in declared_by_family:
                errors.append(
                    f"{relative}: variant {card.get('variant')!r} has a card but is not declared in family.json (I2)"
                )

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
        "variant_status": variants_seen,
        "warnings": warnings,
        "ok": not errors,
        "errors": errors,
    }


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="release.card_lint", description="NanoLab release contract linter")
    sub = parser.add_subparsers(dest="command", required=True)
    p_card = sub.add_parser("card", help="validate component card JSON file(s)")
    p_card.add_argument("files", nargs="+")
    p_card.add_argument("--schema", default=str(CARD_SCHEMA))
    p_rights = sub.add_parser("rights", help="validate RIGHTS.json")
    p_rights.add_argument("file")
    p_rights.add_argument("--schema", default=str(RIGHTS_SCHEMA))
    p_manifest = sub.add_parser("manifest", help="create or verify RELEASE_MANIFEST.json")
    p_manifest.add_argument("mode", choices=["create", "verify"])
    p_manifest.add_argument("pkg_root")
    p_manifest.add_argument("--schema", default=str(MANIFEST_SCHEMA))
    p_manifest.add_argument("--stdout", action="store_true", help="manifest create: print manifest instead of writing")
    p_manifest.add_argument(
        "--generated-at-utc",
        dest="generated_at_utc",
        default=None,
        help="manifest create: frozen ISO-8601 UTC stamp (required; never wall-clock)",
    )
    p_package = sub.add_parser("package", help="full package check")
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
                if not args.generated_at_utc:
                    parser.error("manifest create requires --generated-at-utc (frozen stamp, never wall-clock)")
                manifest = manifest_create(pkg_root, generated_at_utc=args.generated_at_utc)
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
