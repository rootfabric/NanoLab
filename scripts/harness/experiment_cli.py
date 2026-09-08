from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

TERMINAL = {"RUN_COMPLETED", "RUN_FAILED_TECHNICAL", "RUN_ABORTED", "RUN_BLOCKED_ENVIRONMENT"}
ALLOWED_EVENTS = {"RUN_STARTED", "INPUTS_FROZEN", "PREPARATION_COMPLETED", "RUN_CHECKPOINT", *TERMINAL, "ANALYSIS_STARTED", "ANALYSIS_COMPLETED", "PROTOCOL_SUPERSEDED", "ANALYSIS_SUPERSEDED", "REVIEW_COMPLETED"}
ALLOWED_ROLES = {"IMPLEMENTER", "SCIENTIFIC_OPERATOR", "REVIEWER", "VERIFIER", "DIRECTOR"}
SCIENTIFIC_OUTCOMES = {"SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE", "NOT_EVALUATED", "INVALIDATED"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


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
        if event.get("event_type") == "ANALYSIS_COMPLETED" and event.get("scientific_outcome") not in SCIENTIFIC_OUTCOMES:
            errors.append(f"{path.name}: ANALYSIS_COMPLETED requires scientific_outcome")

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
