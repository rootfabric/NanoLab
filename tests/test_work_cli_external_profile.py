"""External execution profile tests (repair/nl5-002-ci-external-vocab-r1).

The NL5-002 external reproduction campaign (EX-NL5-002-B-R1/B-R2) reports with a
dedicated vocabulary: ORCHESTRATOR actor, EXTERNAL_EXECUTOR_DISPATCHED opener,
CONTINUATION progress/errata records, EXTERNAL_RUN_COMPLETED terminal. CI Check 3
validates every docs/work/executions/EX-* directory with harness.work_cli, so the
validator recognises this as a distinct profile while keeping standard work-order
directories unchanged and fail-closed.

Acceptance targets:
- a well-formed external execution directory validates OK (profile external_execution);
- CONTINUATION is allowed after the external terminal (append-only errata pattern);
- unknown event types / standard-only roles / missing or duplicated opener/terminal FAIL;
- standard vocabulary in an external directory and external vocabulary in a standard
  directory both FAIL (profile boundary preserved, fail-closed both ways).

Run: python -m unittest discover -s tests -t .
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from harness.work_cli import inspect_execution  # noqa: E402

FULL_SHA = "0123456789abcdef0123456789abcdef01234567"
EXECUTION_ID = "EX-NL5-002-B-TEST"
WORK_ORDER_ID = "NL5-002-B"


def event(event_id: str, event_type: str, *, actor_role: str = "ORCHESTRATOR", timestamp: str | None = None, **extra: Any) -> dict[str, Any]:
    if timestamp is None:
        seq = "".join(ch for ch in event_id.split("-")[0] if ch.isdigit()) or "0"
        timestamp = "2026-09-19T01:00:{:02d}Z".format(int(seq) % 60)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "event_id": event_id,
        "timestamp_utc": timestamp,
        "execution_id": EXECUTION_ID,
        "work_order_id": WORK_ORDER_ID,
        "event_type": event_type,
        "actor_role": actor_role,
        "subject_sha": FULL_SHA,
        "summary": "test event",
        "blocker": None,
    }
    payload.update(extra)
    return payload


def build_execution(events: list[dict[str, Any]]) -> Path:
    root = Path(__import__("tempfile").mkdtemp()) / EXECUTION_ID
    (root / "events").mkdir(parents=True)
    passport = {
        "schema_version": 1,
        "execution_id": EXECUTION_ID,
        "work_order_id": WORK_ORDER_ID,
        "checkpoint": "NL5",
        "base_sha": FULL_SHA,
        "branch": "work/test-external-r1",
        "risk_class": "MEDIUM",
        "claim_class": "C1_COMPUTATIONAL_REPRODUCTION",
        "allowed_paths": ["docs/work/executions/EX-NL5-002-B-TEST/**"],
        "started_at_utc": "2026-09-19T00:30:00Z",
        "status": "DISPATCHED",
    }
    (root / "passport.json").write_text(__import__("json").dumps(passport), encoding="utf-8")
    for item in events:
        (root / "events" / f"{item['event_id']}.json").write_text(__import__("json").dumps(item), encoding="utf-8")
    return root


def result(events: list[dict[str, Any]]) -> dict[str, Any]:
    return inspect_execution(build_execution(events))


class ExternalExecutionProfile(unittest.TestCase):
    def test_valid_external_directory_is_ok(self):
        res = result([
            event("0001-external-executor-dispatched", "EXTERNAL_EXECUTOR_DISPATCHED"),
            event("0002-continuation", "CONTINUATION"),
            event("0003-external-run-completed", "EXTERNAL_RUN_COMPLETED"),
        ])
        self.assertTrue(res["ok"], res["errors"])
        self.assertEqual(res["profile"], "external_execution")
        self.assertTrue(res["has_terminal_handoff"])

    def test_continuation_after_terminal_is_allowed_as_errata(self):
        res = result([
            event("0001-external-executor-dispatched", "EXTERNAL_EXECUTOR_DISPATCHED"),
            event("0002-external-run-completed", "EXTERNAL_RUN_COMPLETED", timestamp="2026-09-19T02:00:00Z"),
            event("0003-timestamp-errata", "CONTINUATION", timestamp="2026-09-19T01:30:00Z"),
        ])
        self.assertTrue(res["ok"], res["errors"])
        self.assertTrue(res["has_post_terminal_corrections"])

    def test_unknown_event_type_fails(self):
        res = result([
            event("0001-external-executor-dispatched", "EXTERNAL_EXECUTOR_DISPATCHED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
        ])
        self.assertFalse(res["ok"])
        self.assertTrue(any("0002-handoff-completed.json: unsupported event_type" in e for e in res["errors"]))

    def test_standard_only_actor_role_fails(self):
        res = result([
            event("0001-external-executor-dispatched", "EXTERNAL_EXECUTOR_DISPATCHED", actor_role="DIRECTOR"),
        ])
        self.assertFalse(res["ok"])
        self.assertTrue(any("unsupported actor_role" in e for e in res["errors"]))

    def test_missing_terminal_fails(self):
        res = result([
            event("0001-external-executor-dispatched", "EXTERNAL_EXECUTOR_DISPATCHED"),
            event("0002-continuation", "CONTINUATION"),
        ])
        self.assertFalse(res["ok"])
        self.assertTrue(any("exactly one EXTERNAL_RUN_COMPLETED" in e for e in res["errors"]))

    def test_duplicate_opener_fails(self):
        res = result([
            event("0001-external-executor-dispatched", "EXTERNAL_EXECUTOR_DISPATCHED"),
            event("0002-external-executor-dispatched", "EXTERNAL_EXECUTOR_DISPATCHED"),
            event("0003-external-run-completed", "EXTERNAL_RUN_COMPLETED"),
        ])
        self.assertFalse(res["ok"])
        self.assertTrue(any("exactly one EXTERNAL_EXECUTOR_DISPATCHED" in e for e in res["errors"]))

    def test_external_vocabulary_in_standard_directory_fails(self):
        res = result([
            event("0001-work-order-started", "WORK_ORDER_STARTED", actor_role="IMPLEMENTER"),
            event("0002-external-run-completed", "EXTERNAL_RUN_COMPLETED"),
        ])
        self.assertFalse(res["ok"])
        self.assertEqual(res["profile"], "standard_work_order")
        self.assertTrue(any("unsupported event_type" in e for e in res["errors"]))

    def test_orchestrator_in_standard_directory_fails(self):
        res = result([
            event("0001-work-order-started", "WORK_ORDER_STARTED", actor_role="ORCHESTRATOR"),
        ])
        self.assertFalse(res["ok"])
        self.assertTrue(any("unsupported actor_role" in e for e in res["errors"]))


if __name__ == "__main__":
    unittest.main()
