from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

TERMINAL = {"RUN_COMPLETED", "RUN_FAILED_TECHNICAL", "RUN_ABORTED", "RUN_BLOCKED_ENVIRONMENT"}
ALLOWED_EVENTS = {"RUN_STARTED", "INPUTS_FROZEN", "PREPARATION_COMPLETED", "RUN_CHECKPOINT", *TERMINAL, "ANALYSIS_STARTED", "ANALYSIS_COMPLETED", "PROTOCOL_SUPERSEDED", "ANALYSIS_SUPERSEDED", "REVIEW_COMPLETED"}
ALLOWED_ROLES = {"IMPLEMENTER", "SCIENTIFIC_OPERATOR", "REVIEWER", "VERIFIER", "DIRECTOR"}
SCIENTIFIC_OUTCOMES = {"SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE", "NOT_EVALUATED", "INVALIDATED"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
# NL2-003 repair R1 (REVIEWER F-1): the explicit midnight placeholder stamp is
# rejected for experiment events too — same rule, same regex as work_cli
# (docs/research/PROVENANCE_RECOVERY_R1.md §6). The "constant copy across >= 3
# events" rule is deliberately NOT carried over here: fast runs legitimately
# stamp terminal+analysis within the same second (E0-R4 precedent).
MIDNIGHT_PLACEHOLDER = re.compile(r"^\d{4}-\d{2}-\d{2}T00:00:00(\.0+)?(?:Z|z|\+00:00)$")


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_run(run_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = run_dir / "manifest.json"
    events_dir = run_dir / "events"
    artifacts_path = run_dir / "artifacts.manifest.json"

    if not manifest_path.is_file():
        return {"ok": False, "errors": ["missing manifest.json"], "warnings": []}

    manifest = load(manifest_path)
    required = ["schema_version", "experiment_id", "campaign_id", "run_id", "work_order_id", "protocol_revision", "subject_sha", "claim_ceiling", "model", "inputs", "observables", "resource_budget", "stop_conditions", "status"]
    for key in required:
        if key not in manifest:
            errors.append(f"manifest missing {key}")
    if not SHA40.fullmatch(str(manifest.get("subject_sha", ""))):
        errors.append("manifest subject_sha must be 40 lowercase hex characters")

    event_files = sorted(events_dir.glob("*.json")) if events_dir.is_dir() else []
    if not event_files:
        errors.append("no experiment events")

    events: list[dict[str, Any]] = []
    ids: list[str] = []
    required_event = ["event_id", "event_type", "experiment_id", "campaign_id", "run_id", "actor_role", "subject_sha", "summary"]
    for path in event_files:
        event = load(path)
        events.append(event)
        ids.append(str(event.get("event_id", "")))
        for key in required_event:
            if key not in event:
                errors.append(f"{path.name}: missing {key}")
        if path.stem != event.get("event_id"):
            errors.append(f"{path.name}: filename must equal event_id + .json")
        if event.get("experiment_id") != manifest.get("experiment_id"):
            errors.append(f"{path.name}: experiment_id differs from manifest")
        if event.get("campaign_id") != manifest.get("campaign_id"):
            errors.append(f"{path.name}: campaign_id differs from manifest")
        if event.get("run_id") != manifest.get("run_id"):
            errors.append(f"{path.name}: run_id differs from manifest")
        if event.get("event_type") not in ALLOWED_EVENTS:
            errors.append(f"{path.name}: unsupported event_type")
        if event.get("actor_role") not in ALLOWED_ROLES:
            errors.append(f"{path.name}: unsupported actor_role")
        if not SHA40.fullmatch(str(event.get("subject_sha", ""))):
            errors.append(f"{path.name}: invalid subject_sha")
        elif event.get("subject_sha") != manifest.get("subject_sha"):
            warnings.append(f"{path.name}: subject_sha differs; requires explicit superseding revision")
        # NL2-003 repair R1 (REVIEWER F-1): midnight placeholder stamps are the
        # explicit fabrication marker class (O2/F3); the git chronology
        # cross-check used by review relies on machine stamps.
        stamp_value = event.get("timestamp_utc")
        if isinstance(stamp_value, str) and MIDNIGHT_PLACEHOLDER.match(stamp_value.strip()):
            errors.append(f"{path.name}: timestamp_utc {stamp_value!r} is a midnight placeholder; record the actual machine time")
        if event.get("event_type") == "ANALYSIS_COMPLETED" and event.get("scientific_outcome") not in SCIENTIFIC_OUTCOMES:
            errors.append(f"{path.name}: ANALYSIS_COMPLETED requires scientific_outcome")
        # S003 hardening (NL2-003; gap preserved in NL2-001 evidence): SUPPORTED is
        # a scientific conclusion and must not ride on surfaces that do not carry
        # scientific verification. A technical terminal event never carries it;
        # ANALYSIS_COMPLETED carries it only with a verification surface (non-empty
        # artifact_refs resolving to existing analysis artifacts). Fail-closed.
        if event.get("scientific_outcome") == "SUPPORTED":
            event_type = str(event.get("event_type"))
            if event_type == "ANALYSIS_COMPLETED":
                refs = event.get("artifact_refs")
                refs = refs if isinstance(refs, list) else []
                resolvable = any(
                    isinstance(ref, str) and ref and ((run_dir / ref).is_file() or (events_dir / ref).is_file())
                    for ref in refs
                )
                if not refs or not resolvable:
                    errors.append(f"{path.name}: S003: scientific_outcome=SUPPORTED requires a verification surface (non-empty artifact_refs pointing to existing analysis artifacts)")
            else:
                errors.append(f"{path.name}: S003: scientific_outcome=SUPPORTED is a scientific conclusion and must not be carried by a {event_type} event; publish it on ANALYSIS_COMPLETED with analysis evidence (technical/scientific separation)")

    if ids != sorted(ids):
        errors.append("events are not lexically ordered by event_id")
    if len(ids) != len(set(ids)):
        errors.append("duplicate event_id")

    event_types = [event.get("event_type") for event in events]
    if event_types and event_types[0] != "RUN_STARTED":
        errors.append("RUN_STARTED must be the first event")
    if event_types.count("RUN_STARTED") != 1:
        errors.append("exactly one RUN_STARTED event is required")
    terminal_positions = [idx for idx, item in enumerate(event_types) if item in TERMINAL]
    if len(terminal_positions) > 1:
        errors.append("more than one terminal execution event")
    analysis_positions = [idx for idx, item in enumerate(event_types) if item == "ANALYSIS_COMPLETED"]
    review_positions = [idx for idx, item in enumerate(event_types) if item == "REVIEW_COMPLETED"]
    if terminal_positions and analysis_positions and terminal_positions[0] > analysis_positions[0]:
        errors.append("ANALYSIS_COMPLETED cannot precede terminal execution")
    if analysis_positions and review_positions and analysis_positions[-1] > review_positions[0]:
        errors.append("REVIEW_COMPLETED cannot precede final ANALYSIS_COMPLETED")

    if artifacts_path.is_file():
        artifacts = load(artifacts_path)
        for index, item in enumerate(artifacts.get("artifacts", [])):
            prefix = f"artifact[{index}]"
            for key in ["sha256", "size_bytes", "producer_run_id", "subject_sha", "storage_location"]:
                if key not in item:
                    errors.append(f"{prefix}: missing {key}")
            if not SHA256.fullmatch(str(item.get("sha256", ""))):
                errors.append(f"{prefix}: invalid sha256")
            if not isinstance(item.get("size_bytes"), int) or item.get("size_bytes", -1) < 0:
                errors.append(f"{prefix}: invalid size_bytes")
            if item.get("producer_run_id") != manifest.get("run_id"):
                errors.append(f"{prefix}: producer_run_id differs from manifest")
            if item.get("subject_sha") != manifest.get("subject_sha"):
                errors.append(f"{prefix}: subject_sha differs from manifest")
            if not item.get("storage_location"):
                errors.append(f"{prefix}: storage_location required")
            # O1 hardening (NL2-003; 55 stale storage_location entries preserved in
            # the superseded E0-R2 attempt): for the established in-Git convention
            # ("experiments/evidence/...") the storage path must carry the
            # manifest's campaign_id and run_id as path segments. External storage
            # schemes (non "experiments/" locations) stay beyond this structural
            # rule; they keep the non-empty requirement only.
            location = str(item.get("storage_location", ""))
            if location.startswith("experiments/"):
                segments = location.split("/")
                if str(manifest.get("campaign_id")) not in segments:
                    errors.append(f"{prefix}: storage_location must contain the manifest campaign_id as a path segment (stale storage_location, O1)")
                if str(manifest.get("run_id")) not in segments:
                    errors.append(f"{prefix}: storage_location must contain the run_id as a path segment (stale storage_location, O1)")
    elif terminal_positions:
        errors.append("terminal run requires artifacts.manifest.json")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "manifest_sha256": digest_file(manifest_path),
        "run_id": manifest.get("run_id"),
        "status": manifest.get("status"),
        "events": [{"id": event.get("event_id"), "type": event.get("event_type")} for event in events],
        "has_terminal_execution": bool(terminal_positions),
        "has_analysis": bool(analysis_positions),
        "has_review": bool(review_positions),
    }


# ---------------------------------------------------------------------------
# digest-vs-blob verification (NL2-003; F1-class gap: validators never compared
# artifact manifest digests with the actual published bytes)
# ---------------------------------------------------------------------------


def git_blob_at(repo_root: Path, rev: str, rel_posix: str) -> bytes:
    """Return blob bytes at rev, bypassing the working copy (autocrlf lesson:
    NL2-001/NL2-002 verifiers read blobs via git cat-file, never CRLF working
    files, to avoid false mismatches)."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "cat-file", "blob", f"{rev}:{rel_posix}"],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git cat-file failed for {rev}:{rel_posix}: {result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout


def git_repo_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git rev-parse --show-toplevel failed for {start}: {result.stderr.strip()}")
    return Path(result.stdout.strip())


def find_artifact_manifest_dirs(root: Path) -> list[Path]:
    """A single run dir (contains artifacts.manifest.json) or a parent whose
    subtree is scanned for run dirs."""
    if (root / "artifacts.manifest.json").is_file():
        return [root]
    return sorted({path.parent for path in root.rglob("artifacts.manifest.json")})


def verify_digests(target: Path, rev: str = "HEAD") -> dict[str, Any]:
    """Compare every artifacts.manifest.json entry (sha256/size_bytes) with the
    actual git blob bytes at rev. CI-checkable: exit 0 only with 0 mismatches."""
    errors: list[str] = []
    mismatches: list[dict[str, Any]] = []
    entries_checked = 0
    manifest_dirs = find_artifact_manifest_dirs(target)
    if not manifest_dirs:
        return {
            "ok": False,
            "rev": rev,
            "runs_checked": 0,
            "entries_checked": 0,
            "mismatches": [],
            "errors": [f"no artifacts.manifest.json found under {target}"],
        }
    try:
        repo_root = git_repo_root(target)
    except RuntimeError as exc:
        return {"ok": False, "rev": rev, "runs_checked": 0, "entries_checked": 0, "mismatches": [], "errors": [str(exc)]}

    for run_dir in manifest_dirs:
        manifest_path = run_dir / "artifacts.manifest.json"
        try:
            manifest = load(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{manifest_path}: unreadable artifacts manifest: {exc}")
            continue
        for index, item in enumerate(manifest.get("artifacts", [])):
            prefix = f"{manifest_path}: artifact[{index}]"
            if not isinstance(item, dict):
                # legacy OBJECT-form manifests keep failing closed (N007 class),
                # but as a graceful error so bulk scans can report every surface
                errors.append(f"{prefix}: artifact entry must be an object (array contract)")
                continue
            name = item.get("name")
            try:
                rel = (run_dir / "artifacts" / str(name)).resolve().relative_to(repo_root).as_posix()
            except ValueError:
                errors.append(f"{prefix}: run directory is outside the git repository {repo_root}")
                continue
            try:
                blob = git_blob_at(repo_root, rev, rel)
            except RuntimeError as exc:
                errors.append(f"{prefix}: {exc}")
                continue
            entries_checked += 1
            actual_sha = hashlib.sha256(blob).hexdigest()
            actual_size = len(blob)
            expected_sha = str(item.get("sha256", ""))
            try:
                expected_size = int(item.get("size_bytes", -1))
            except (TypeError, ValueError):
                expected_size = -1
            if actual_sha != expected_sha or actual_size != expected_size:
                mismatches.append({
                    "manifest": str(manifest_path),
                    "name": name,
                    "expected_sha256": expected_sha,
                    "actual_sha256": actual_sha,
                    "expected_size_bytes": expected_size,
                    "actual_size_bytes": actual_size,
                })
    return {
        "ok": not errors and not mismatches,
        "rev": rev,
        "runs_checked": len(manifest_dirs),
        "entries_checked": entries_checked,
        "mismatches": mismatches,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["validate", "status", "close", "verify-digests"])
    parser.add_argument("run_dir")
    parser.add_argument("--rev", default="HEAD", help="git rev for verify-digests (default HEAD)")
    args = parser.parse_args()
    if args.mode == "verify-digests":
        result = verify_digests(Path(args.run_dir).resolve(), rev=args.rev)
        print(json.dumps({"schema": "nanolab.control_experiment_output.v1", "command": "VERIFY_DIGESTS", **result}, ensure_ascii=False, indent=2))
        return 0 if result["ok"] else 3
    result = inspect_run(Path(args.run_dir).resolve())
    if args.mode == "close" and result["ok"]:
        missing: list[str] = []
        if not result["has_terminal_execution"]:
            missing.append("terminal execution event")
        if not result["has_analysis"]:
            missing.append("ANALYSIS_COMPLETED")
        if not result["has_review"]:
            missing.append("REVIEW_COMPLETED")
        if missing:
            result["ok"] = False
            result["errors"].append("close blocked: missing " + ", ".join(missing))
    print(json.dumps({"schema": "nanolab.control_experiment_output.v1", "command": args.mode.upper(), **result}, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
