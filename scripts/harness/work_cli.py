from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

TERMINAL = {"HANDOFF_COMPLETED", "WORK_ORDER_BLOCKED", "WORK_ORDER_CANCELLED"}


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

    event_files = sorted(events_dir.glob("*.json")) if events_dir.is_dir() else []
    if not event_files:
        errors.append("no work events")

    ids: list[str] = []
    event_types: list[str] = []
    for path in event_files:
        event = load(path)
        ids.append(str(event.get("event_id", "")))
        event_types.append(str(event.get("event_type", "")))
        if path.stem != event.get("event_id"):
            errors.append(f"{path.name}: filename must equal event_id + .json")
        if event.get("execution_id") != passport.get("execution_id"):
            errors.append(f"{path.name}: execution_id differs from passport")
        if event.get("work_order_id") != passport.get("work_order_id"):
            errors.append(f"{path.name}: work_order_id differs from passport")

    if ids != sorted(ids):
        errors.append("events are not lexically ordered")
    if len(ids) != len(set(ids)):
        errors.append("duplicate event_id")
    if "WORK_ORDER_STARTED" not in event_types:
        errors.append("WORK_ORDER_STARTED event missing")
    if sum(1 for item in event_types if item in TERMINAL) > 1:
        errors.append("more than one terminal/handoff event")

    return {
        "ok": not errors,
        "errors": errors,
        "execution_id": passport.get("execution_id"),
        "work_order_id": passport.get("work_order_id"),
        "status": passport.get("status"),
        "passport_sha256": sha256(passport_path),
        "event_types": event_types,
        "has_terminal_handoff": any(item in TERMINAL for item in event_types),
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
