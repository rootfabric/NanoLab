from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TERMINAL = {"HANDOFF_COMPLETED", "WORK_ORDER_BLOCKED", "WORK_ORDER_CANCELLED"}
# Explicit post-terminal corrections class (docs/infra/VALIDATION_GATES_R1.md):
# REVIEW_CORRECTIONS is the dedicated marker event type; CONTINUATION_CHECKPOINT
# doubles as the legacy spelling used by already-published canonical executions.
CORRECTIONS_EVENTS = {"CONTINUATION_CHECKPOINT", "REVIEW_CORRECTIONS"}
ALLOWED_EVENTS = {"WORK_ORDER_STARTED", "CONTINUATION_CHECKPOINT", "IMPLEMENTATION_COMMITTED", "VALIDATION_RECORDED", "BLOCKER_RECORDED", "REPAIR_STARTED", "REPAIR_COMPLETED", "REVIEW_RECORDED", "REVIEW_CORRECTIONS", *TERMINAL}
ALLOWED_ROLES = {"IMPLEMENTER", "SCIENTIFIC_OPERATOR", "REVIEWER", "VERIFIER", "DIRECTOR"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SUBJECT_SHA_ABBREV = re.compile(r"^[0-9a-f]{7,39}$")
# MINOR-2 repair (INFRA1-002 review R1): an abbreviated subject_sha is accepted
# ONLY for the exact immutable events already published on canonical main
# (harvested from docs/work/executions/EX-* at a4533ab, 2026-09-09; every value
# equals "9cc83e8"). Every new event must use the full 40-hex form required by
# work-event.schema.v1.json.
LEGACY_ABBREVIATED_SHA_EVENTS = frozenset({
    ("EX-NL1-002-R1", "0002-campaign-runs-completed"),
    ("EX-NL1-002-R1", "0003-validation-recorded"),
    ("EX-NL1-002-R1", "0004-handoff-completed"),
    ("EX-NL1-002-R1", "0005-resource-evidence-committed"),
})
# MINOR-3 repair: post-terminal corrections events that pre-date this rule on
# canonical main, grandfathered from the new "corrections timestamp must not
# precede the terminal event timestamp" requirement (EX-NL1-002-R1 0005 was
# recorded 11:16:30Z, before its 11:30:00Z handoff record; the other three
# already comply and are listed for completeness). All NEW corrections events
# must satisfy the requirement.
LEGACY_TIMESTAMP_EXEMPT_CORRECTIONS = frozenset({
    ("EX-INFRA0-001-R1", "0005-review-corrections"),
    ("EX-NL1-001-R1", "0005-review-corrections"),
    ("EX-NL1-002-R1", "0005-resource-evidence-committed"),
    ("EX-NL1-002-R1", "0006-repair-completed"),
})
# MINOR-3 repair: REVIEW_CORRECTIONS is a review-authority marker; the
# implementer of an execution cannot self-issue it.
REVIEW_CORRECTIONS_ALLOWED_ROLES = {"REVIEWER", "VERIFIER", "DIRECTOR"}


def parse_utc_timestamp(value: Any) -> datetime | None:
    """Parse an ISO-8601 UTC timestamp; return None when absent or malformed."""
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


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
    events: list[dict[str, Any]] = []
    required_event = ["event_id", "event_type", "execution_id", "work_order_id", "actor_role", "subject_sha", "summary"]
    for path in event_files:
        event = load(path)
        events.append(event)
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
        sha_value = str(event.get("subject_sha", ""))
        legacy_key = (str(event.get("execution_id")), str(event.get("event_id")))
        if not SHA40.fullmatch(sha_value) and not (SUBJECT_SHA_ABBREV.fullmatch(sha_value) and legacy_key in LEGACY_ABBREVIATED_SHA_EVENTS):
            errors.append(f"{path.name}: invalid subject_sha (full 40-hex required; abbreviated values are reserved for pre-existing legacy events)")

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

    # Terminal-last stays the rule for the normal flow; an explicit corrections
    # class may follow the terminal/handoff event (AGENTS.md: corrections are
    # recorded as new events, old events are never edited). Any post-terminal
    # event outside the class is a hard error, so the marker cannot be skipped.
    corrections_tail: list[int] = []
    terminal_timestamp: datetime | None = None
    if terminal_positions:
        terminal_idx = terminal_positions[0]
        terminal_timestamp = parse_utc_timestamp(events[terminal_idx].get("timestamp_utc"))
        unmarked: list[str] = []
        for idx in range(terminal_idx + 1, len(event_types)):
            if event_types[idx] in CORRECTIONS_EVENTS:
                corrections_tail.append(idx)
            else:
                unmarked.append(event_files[idx].name)
        if unmarked:
            errors.append("events after terminal/handoff must be review-corrections events (CONTINUATION_CHECKPOINT or REVIEW_CORRECTIONS): " + ", ".join(unmarked))
    for idx, event_type in enumerate(event_types):
        if event_type == "REVIEW_CORRECTIONS" and (not terminal_positions or idx < terminal_positions[0]):
            errors.append(f"{event_files[idx].name}: REVIEW_CORRECTIONS is allowed only after the terminal/handoff event")
        if event_type == "REVIEW_CORRECTIONS" and str(events[idx].get("actor_role")) not in REVIEW_CORRECTIONS_ALLOWED_ROLES:
            errors.append(f"{event_files[idx].name}: REVIEW_CORRECTIONS must be authored by REVIEWER, VERIFIER or DIRECTOR, not by {events[idx].get('actor_role')}")
    tail_times: list[tuple[str, datetime | None]] = [(event_files[idx].name, parse_utc_timestamp(events[idx].get("timestamp_utc"))) for idx in corrections_tail]
    for name, moment in tail_times:
        if moment is None:
            errors.append(f"{name}: corrections event requires a parseable ISO-8601 timestamp_utc")
    for (_, previous), (name, moment) in zip(tail_times, tail_times[1:]):
        if previous is not None and moment is not None and moment < previous:
            errors.append(f"{name}: corrections events timestamps must be non-decreasing")
    # MINOR-3 repair: a corrections event must not precede the terminal/handoff
    # event it corrects; pre-existing canonical events are grandfathered.
    if terminal_timestamp is not None:
        for idx in corrections_tail:
            moment = parse_utc_timestamp(events[idx].get("timestamp_utc"))
            legacy_key = (str(events[idx].get("execution_id")), str(events[idx].get("event_id")))
            if moment is not None and moment < terminal_timestamp and legacy_key not in LEGACY_TIMESTAMP_EXEMPT_CORRECTIONS:
                errors.append(f"{event_files[idx].name}: corrections event timestamp must be >= terminal event timestamp")

    return {
        "ok": not errors,
        "errors": errors,
        "execution_id": passport.get("execution_id"),
        "work_order_id": passport.get("work_order_id"),
        "status": passport.get("status"),
        "passport_sha256": digest_file(passport_path),
        "event_types": event_types,
        "has_terminal_handoff": bool(terminal_positions),
        "has_post_terminal_corrections": bool(corrections_tail),
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
