"""Corrections-aware work-event validator tests (INFRA1-002).

Acceptance targets:
- legacy case EX-NL1-002-R1: 5 residual errors must become OK;
- negative: a post-terminal event without the corrections marker must FAIL;
- terminal-last stays enforced for the normal (non-corrections) flow.

Run: python -m unittest discover -s tests -t .
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from harness.work_cli import inspect_execution  # noqa: E402

FULL_SHA = "0123456789abcdef0123456789abcdef01234567"
FULL_SHA_B = "fedcba9876543210fedcba9876543210fedcba98"
ABBR_SHA = "9cc83e8"
EXECUTION_ID = "EX-TEST-R1"
WORK_ORDER_ID = "INFRA1-002"


def event(event_id: str, event_type: str, *, subject_sha: str = FULL_SHA, timestamp: str = "2026-09-09T13:00:00Z", actor_role: str = "IMPLEMENTER", **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "event_id": event_id,
        "timestamp_utc": timestamp,
        "execution_id": EXECUTION_ID,
        "work_order_id": WORK_ORDER_ID,
        "event_type": event_type,
        "actor_role": actor_role,
        "subject_sha": subject_sha,
        "summary": "test event",
        "blocker": None,
    }
    payload.update(extra)
    return payload


def build_execution(events: list[dict[str, Any]], with_summary: bool = True) -> Path:
    root = Path(tempfile.mkdtemp()) / "EX-TEST-R1"
    (root / "events").mkdir(parents=True)
    passport = {
        "schema_version": 1,
        "execution_id": EXECUTION_ID,
        "work_order_id": WORK_ORDER_ID,
        "checkpoint": "INFRA1",
        "base_sha": FULL_SHA,
        "branch": "infra/test-r1",
        "risk_class": "MEDIUM",
        "claim_class": "C0_SOFTWARE_ONLY",
        "allowed_paths": [],
        "started_at_utc": "2026-09-09T12:00:00Z",
        "status": "IN_PROGRESS",
    }
    (root / "passport.json").write_text(__import__("json").dumps(passport, indent=2) + "\n", encoding="utf-8")
    for item in events:
        target = root / "events" / f"{item['event_id']}.json"
        target.write_text(__import__("json").dumps(item, indent=2) + "\n", encoding="utf-8")
    if with_summary:
        (root / "summary.md").write_text("test summary\n", encoding="utf-8")
    return root


def validate(events: list[dict[str, Any]]) -> dict[str, Any]:
    return inspect_execution(build_execution(events))


class TerminalLastNormalFlowTests(unittest.TestCase):
    def test_terminal_last_flow_is_ok(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED"),
            event("0003-handoff-completed", "HANDOFF_COMPLETED"),
        ])
        self.assertTrue(result["ok"], result["errors"])
        self.assertTrue(result["has_terminal_handoff"])
        self.assertFalse(result["has_post_terminal_corrections"])

    def test_event_after_terminal_in_normal_flow_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-validation-recorded", "VALIDATION_RECORDED"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("review-corrections" in item for item in result["errors"]), result["errors"])


class PostTerminalCorrectionsTests(unittest.TestCase):
    def test_continuation_checkpoint_after_handoff_is_accepted(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "CONTINUATION_CHECKPOINT", subject_sha=FULL_SHA_B),
        ])
        self.assertTrue(result["ok"], result["errors"])
        self.assertTrue(result["has_post_terminal_corrections"])

    def test_review_corrections_marker_after_handoff_is_accepted(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "REVIEW_CORRECTIONS", subject_sha=FULL_SHA_B),
        ])
        self.assertTrue(result["ok"], result["errors"])

    def test_unmarked_event_after_corrections_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "CONTINUATION_CHECKPOINT", subject_sha=FULL_SHA_B),
            event("0004-implementation-committed", "IMPLEMENTATION_COMMITTED"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("review-corrections" in item for item in result["errors"]), result["errors"])

    def test_review_corrections_before_terminal_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-review-corrections", "REVIEW_CORRECTIONS"),
            event("0003-handoff-completed", "HANDOFF_COMPLETED"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("only after the terminal" in item for item in result["errors"]), result["errors"])

    def test_second_terminal_after_corrections_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "CONTINUATION_CHECKPOINT", subject_sha=FULL_SHA_B),
            event("0004-work-order-blocked", "WORK_ORDER_BLOCKED"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("more than one terminal" in item for item in result["errors"]), result["errors"])


class CorrectionsSemanticValidityTests(unittest.TestCase):
    def test_corrections_with_invalid_subject_sha_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "REVIEW_CORRECTIONS", subject_sha="abc"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("invalid subject_sha" in item for item in result["errors"]), result["errors"])

    def test_corrections_require_parseable_timestamp(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "CONTINUATION_CHECKPOINT", subject_sha=FULL_SHA_B, timestamp="not-a-time"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("parseable ISO-8601" in item for item in result["errors"]), result["errors"])

    def test_corrections_tail_timestamps_must_be_non_decreasing(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "CONTINUATION_CHECKPOINT", subject_sha=FULL_SHA_B, timestamp="2026-09-09T14:00:00Z"),
            event("0004-review-corrections-2", "REVIEW_CORRECTIONS", timestamp="2026-09-09T13:30:00Z"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("non-decreasing" in item for item in result["errors"]), result["errors"])

    def test_subject_sha_format_bounds(self) -> None:
        self.assertTrue(validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", subject_sha=ABBR_SHA),
        ])["ok"])
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", subject_sha="9cc83"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("invalid subject_sha" in item for item in result["errors"]), result["errors"])


class LegacyCanonicalCasesTests(unittest.TestCase):
    @unittest.skipUnless((REPO_ROOT / "docs/work/executions/EX-NL1-002-R1").is_dir(), "canonical checkout required")
    def test_ex_nl1_002_r1_residual_errors_now_ok(self) -> None:
        result = inspect_execution(REPO_ROOT / "docs/work/executions/EX-NL1-002-R1")
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["has_post_terminal_corrections"])

    @unittest.skipUnless((REPO_ROOT / "docs/work/executions/EX-INFRA0-001-R1").is_dir(), "canonical checkout required")
    def test_ex_infra0_001_r1_now_ok(self) -> None:
        result = inspect_execution(REPO_ROOT / "docs/work/executions/EX-INFRA0-001-R1")
        self.assertTrue(result["ok"], result["errors"])

    @unittest.skipUnless((REPO_ROOT / "docs/work/executions/EX-NL1-001-R1").is_dir(), "canonical checkout required")
    def test_ex_nl1_001_r1_now_ok(self) -> None:
        result = inspect_execution(REPO_ROOT / "docs/work/executions/EX-NL1-001-R1")
        self.assertTrue(result["ok"], result["errors"])


if __name__ == "__main__":
    unittest.main()
