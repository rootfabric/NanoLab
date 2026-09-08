from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

TERMINAL = {"HANDOFF_COMPLETED", "WORK_ORDER_BLOCKED", "WORK_ORDER_CANCELLED"}
ALLOWED_EVENTS = {"WORK_ORDER_STARTED", "CONTINUATION_CHECKPOINT", "IMPLEMENTATION_COMMITTED", "VALIDATION_RECORDED", "BLOCKER_RECORDED", "REPAIR_STARTED", "REPAIR_COMPLETED", "REVIEW_RECORDED", *TERMINAL}
ALLOWED_ROLES = {"IMPLEMENTER", "SCIENTIFIC_OPERATOR", "REVIEWER", "VERIFIER", "DIRECTOR"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


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


def inspect_execution(execution_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    passport_path = execution_dir / "passport.json"
    summary_path = execution_dir / "summary.md"
    events_dir = execution_dir / "events"
    if not passport_path.is_file():
        return {"ok": False, "errors": ["missing passport.json"]}

    passport = load(passport_path)
    required = ["schema_version", "execution_id", "work_order_id", "checkpoint", "base_sha", "branch", "risk_class", "claim_class", "allowed_paths", "started_at_utc", "status"]
    for key in required:
        if key not in passport:
            errors.append(f"passport missing {key}")
    if not SHA40.fullmatch(str(passport.get("base_sha", ""))):
        errors.append("passport base_sha must be 40 lowercase hex characters")

    event_files = sorted(events_dir.glob("*.json")) if events_dir.is_dir() else []
    if not event_files:
        errors.append("no work events")

    ids: list[str] = []
    event_types: list[str] = []
    required_event = ["event_id", "event_type", "execution_id", "work_order_id", "actor_role", "subject_sha", "summary"]
    for path in event_files:
        event = load(path)
        ids.append(str(event.get("event_id", "")))
        event_types.append(str(event.get("event_type", "")))
        for key in required_event:
            if key not in event:
                errors.append(f"{path.name}: missing {key}")
        if path.stem != event.get("event_id"):
            errors.append(f"{path.name}: filename must equal event_id + .json")
        if event.get("execution_id") != passport.get("execution_id"):
            errors.append(f"{path.name}: execution_id differs from passport")
        if event.get("work_order_id") != passport.get("work_order_id"):
            errors.append(f"{path.name}: work_order_id differs from passport")
        if event.get("event_type") not in ALLOWED_EVENTS:
            errors.append(f"{path.name}: unsupported event_type")
        if event.get("actor_role") not in ALLOWED_ROLES:
            errors.append(f"{path.name}: unsupported actor_role")
        if not SHA40.fullmatch(str(event.get("subject_sha", ""))):
            errors.append(f"{path.name}: invalid subject_sha")

    if ids != sorted(ids):
        errors.append("events are not lexically ordered")
    if len(ids) != len(set(ids)):
        errors.append("duplicate event_id")
    if event_types and event_types[0] != "WORK_ORDER_STARTED":
        errors.append("WORK_ORDER_STARTED must be the first event")
    if event_types.count("WORK_ORDER_STARTED") != 1:
        errors.append("exactly one WORK_ORDER_STARTED event is required")
    terminal_positions = [idx for idx, item in enumerate(event_types) if item in TERMINAL]
    if len(terminal_positions) > 1:
        errors.append("more than one terminal/handoff event")
    if terminal_positions and terminal_positions[0] != len(event_types) - 1:
        errors.append("terminal/handoff event must be last")

    return {
        "ok": not errors,
        "errors": errors,
        "execution_id": passport.get("execution_id"),
        "work_order_id": passport.get("work_order_id"),
        "status": passport.get("status"),
        "passport_sha256": digest_file(passport_path),
        "event_types": event_types,
        "has_terminal_handoff": bool(terminal_positions),
        "has_summary": summary_path.is_file(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["validate", "status", "close"])
    parser.add_argument("execution_dir")
    args = parser.parse_args()
    result = inspect_execution(Path(args.execution_dir).resolve())
    if args.mode == "close" and result["ok"]:
        missing: list[str] = []
        if not result["has_terminal_handoff"]:
            missing.append("HANDOFF_COMPLETED/BLOCKED/CANCELLED event")
        if not result["has_summary"]:
            missing.append("summary.md")
        if missing:
            result["ok"] = False
            result["errors"].append("close blocked: missing " + ", ".join(missing))
    print(json.dumps({"schema": "nanolab.control_work_output.v1", "command": args.mode.upper(), **result}, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
