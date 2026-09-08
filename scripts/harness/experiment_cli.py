from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

TERMINAL = {"RUN_COMPLETED", "RUN_FAILED_TECHNICAL", "RUN_ABORTED", "RUN_BLOCKED_ENVIRONMENT"}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256(path: Path) -> str:
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

    event_files = sorted(events_dir.glob("*.json")) if events_dir.is_dir() else []
    if not event_files:
        errors.append("no experiment events")

    events: list[dict[str, Any]] = []
    ids: list[str] = []
    for path in event_files:
        event = load(path)
        events.append(event)
        ids.append(str(event.get("event_id", "")))
        if path.stem != event.get("event_id"):
            errors.append(f"{path.name}: filename must equal event_id + .json")
        if event.get("run_id") != manifest.get("run_id"):
            errors.append(f"{path.name}: run_id differs from manifest")
        if event.get("subject_sha") != manifest.get("subject_sha"):
            warnings.append(f"{path.name}: subject_sha differs; requires explicit superseding revision")

    if ids != sorted(ids):
        errors.append("events are not lexically ordered by event_id")
    if len(ids) != len(set(ids)):
        errors.append("duplicate event_id")

    event_types = [event.get("event_type") for event in events]
    if "RUN_STARTED" not in event_types:
        errors.append("RUN_STARTED event missing")
    if sum(1 for item in event_types if item in TERMINAL) > 1:
        errors.append("more than one terminal execution event")

    if artifacts_path.is_file():
        artifacts = load(artifacts_path)
        for item in artifacts.get("artifacts", []):
            if not item.get("sha256") or not item.get("storage_location"):
                errors.append("artifact entry requires sha256 and storage_location")
    elif any(item in TERMINAL for item in event_types):
        errors.append("terminal run requires artifacts.manifest.json")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "manifest_sha256": sha256(manifest_path),
        "run_id": manifest.get("run_id"),
        "status": manifest.get("status"),
        "events": [{"id": event.get("event_id"), "type": event.get("event_type")} for event in events],
        "has_terminal_execution": any(item in TERMINAL for item in event_types),
        "has_analysis": "ANALYSIS_COMPLETED" in event_types,
        "has_review": "REVIEW_COMPLETED" in event_types,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["validate", "status", "close"])
    parser.add_argument("run_dir")
    args = parser.parse_args()
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
