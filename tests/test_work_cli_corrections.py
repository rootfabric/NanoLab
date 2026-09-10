"""Corrections-aware work-event validator tests (INFRA1-002, incl. repair R1).

Acceptance targets:
- legacy case EX-NL1-002-R1: 5 residual errors must become OK;
- negative: a post-terminal event without the corrections marker must FAIL;
- terminal-last stays enforced for the normal (non-corrections) flow;
- repair R1 (MINOR-2): abbreviated subject_sha only for whitelisted legacy events;
- repair R1 (MINOR-3): corrections timestamp >= terminal timestamp;
  REVIEW_CORRECTIONS must not be authored by IMPLEMENTER.

Run: python -m unittest discover -s tests -t .
"""
from __future__ import annotations

import json
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
LEGACY_SHA = "9cc83e8"
EXECUTION_ID = "EX-TEST-R1"
WORK_ORDER_ID = "INFRA1-002"


def event(event_id: str, event_type: str, *, subject_sha: str = FULL_SHA, timestamp: str | None = None, actor_role: str = "IMPLEMENTER", execution_id: str = EXECUTION_ID, work_order_id: str = WORK_ORDER_ID, **extra: Any) -> dict[str, Any]:
    if timestamp is None:
        # NL2-003 hardening: a constant copy timestamp across 3+ events is now a
        # validator error, so the fixture generator derives a distinct per-event
        # machine stamp from the event-id sequence number by default.
        seq = "".join(ch for ch in event_id.split("-")[0] if ch.isdigit()) or "0"
        timestamp = "2026-09-09T13:00:{:02d}Z".format(int(seq) % 60)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "event_id": event_id,
        "timestamp_utc": timestamp,
        "execution_id": execution_id,
        "work_order_id": work_order_id,
        "event_type": event_type,
        "actor_role": actor_role,
        "subject_sha": subject_sha,
        "summary": "test event",
        "blocker": None,
    }
    payload.update(extra)
    return payload


def build_execution(events: list[dict[str, Any]], with_summary: bool = True, execution_id: str = EXECUTION_ID, work_order_id: str = WORK_ORDER_ID) -> Path:
    root = Path(tempfile.mkdtemp()) / execution_id
    (root / "events").mkdir(parents=True)
    passport = {
        "schema_version": 1,
        "execution_id": execution_id,
        "work_order_id": work_order_id,
        "checkpoint": "INFRA1",
        "base_sha": FULL_SHA,
        "branch": "infra/test-r1",
        "risk_class": "MEDIUM",
        "claim_class": "C0_SOFTWARE_ONLY",
        "allowed_paths": [],
        "started_at_utc": "2026-09-09T12:00:00Z",
        "status": "IN_PROGRESS",
    }
    (root / "passport.json").write_text(json.dumps(passport, indent=2) + "\n", encoding="utf-8")
    for item in events:
        target = root / "events" / f"{item['event_id']}.json"
        target.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
    if with_summary:
        (root / "summary.md").write_text("test summary\n", encoding="utf-8")
    return root


def validate(events: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    return inspect_execution(build_execution(events, **kwargs))


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
            event("0003-review-corrections", "REVIEW_CORRECTIONS", subject_sha=FULL_SHA_B, actor_role="REVIEWER"),
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
            event("0002-review-corrections", "REVIEW_CORRECTIONS", actor_role="REVIEWER"),
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
            event("0004-review-corrections-2", "REVIEW_CORRECTIONS", timestamp="2026-09-09T13:30:00Z", actor_role="REVIEWER"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("non-decreasing" in item for item in result["errors"]), result["errors"])


class SubjectShaLegacyScopeTests(unittest.TestCase):
    """MINOR-2 repair: abbreviated SHAs are reserved for whitelisted legacy events."""

    def test_new_event_with_arbitrary_abbreviated_sha_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", subject_sha="abc1234"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("invalid subject_sha" in item for item in result["errors"]), result["errors"])

    def test_new_event_with_8_to_39_hex_sha_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", subject_sha="abc1234a"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("invalid subject_sha" in item for item in result["errors"]), result["errors"])

    def test_legacy_whitelisted_event_still_accepts_abbreviated_sha(self) -> None:
        result = validate(
            [
                event("0001-work-order-started", "WORK_ORDER_STARTED", execution_id="EX-NL1-002-R1", work_order_id="NL1-002"),
                event("0002-handoff-completed", "HANDOFF_COMPLETED", execution_id="EX-NL1-002-R1", work_order_id="NL1-002"),
                event("0005-resource-evidence-committed", "CONTINUATION_CHECKPOINT", subject_sha=LEGACY_SHA, execution_id="EX-NL1-002-R1", work_order_id="NL1-002"),
            ],
            execution_id="EX-NL1-002-R1",
            work_order_id="NL1-002",
        )
        self.assertTrue(result["ok"], result["errors"])

    def test_legacy_value_reused_by_other_execution_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", subject_sha=LEGACY_SHA),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("invalid subject_sha" in item for item in result["errors"]), result["errors"])

    def test_legacy_event_id_in_other_execution_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0005-resource-evidence-committed", "CONTINUATION_CHECKPOINT", subject_sha=LEGACY_SHA, timestamp="2026-09-09T13:30:00Z"),
            event("0006-handoff-completed", "HANDOFF_COMPLETED", timestamp="2026-09-09T14:00:00Z"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("invalid subject_sha" in item for item in result["errors"]), result["errors"])


class CorrectionsTimestampVsTerminalTests(unittest.TestCase):
    """MINOR-3 repair: corrections timestamps must not precede the terminal event."""

    def test_corrections_before_terminal_timestamp_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED", timestamp="2026-09-09T14:00:00Z"),
            event("0003-review-corrections", "CONTINUATION_CHECKPOINT", subject_sha=FULL_SHA_B, timestamp="2026-09-09T13:00:00Z"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any(">= terminal event timestamp" in item for item in result["errors"]), result["errors"])

    def test_corrections_at_or_after_terminal_timestamp_passes(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED", timestamp="2026-09-09T12:00:00Z"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED", timestamp="2026-09-09T14:00:00Z"),
            event("0003-review-corrections", "CONTINUATION_CHECKPOINT", subject_sha=FULL_SHA_B, timestamp="2026-09-09T14:00:00Z"),
        ])
        self.assertTrue(result["ok"], result["errors"])

    def test_legacy_exempt_event_may_precede_terminal_timestamp(self) -> None:
        result = validate(
            [
                event("0001-work-order-started", "WORK_ORDER_STARTED", execution_id="EX-NL1-002-R1", work_order_id="NL1-002", timestamp="2026-09-09T10:00:00Z"),
                event("0004-handoff-completed", "HANDOFF_COMPLETED", execution_id="EX-NL1-002-R1", work_order_id="NL1-002", timestamp="2026-09-09T11:30:00Z"),
                event("0005-resource-evidence-committed", "CONTINUATION_CHECKPOINT", subject_sha=LEGACY_SHA, execution_id="EX-NL1-002-R1", work_order_id="NL1-002", timestamp="2026-09-09T11:16:30Z"),
            ],
            execution_id="EX-NL1-002-R1",
            work_order_id="NL1-002",
        )
        self.assertTrue(result["ok"], result["errors"])

    def test_non_exempt_new_event_in_legacy_execution_still_fails(self) -> None:
        result = validate(
            [
                event("0001-work-order-started", "WORK_ORDER_STARTED", execution_id="EX-NL1-002-R1", work_order_id="NL1-002", timestamp="2026-09-09T10:00:00Z"),
                event("0004-handoff-completed", "HANDOFF_COMPLETED", execution_id="EX-NL1-002-R1", work_order_id="NL1-002", timestamp="2026-09-09T11:30:00Z"),
                event("0005-some-new-correction", "CONTINUATION_CHECKPOINT", subject_sha=FULL_SHA_B, execution_id="EX-NL1-002-R1", work_order_id="NL1-002", timestamp="2026-09-09T11:16:30Z"),
            ],
            execution_id="EX-NL1-002-R1",
            work_order_id="NL1-002",
        )
        self.assertFalse(result["ok"])
        self.assertTrue(any(">= terminal event timestamp" in item for item in result["errors"]), result["errors"])


class ReviewCorrectionsRoleTests(unittest.TestCase):
    """MINOR-3 repair: REVIEW_CORRECTIONS is reserved for review authority."""

    def test_review_corrections_from_implementer_fails(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "REVIEW_CORRECTIONS", subject_sha=FULL_SHA_B, actor_role="IMPLEMENTER"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("REVIEWER, VERIFIER or DIRECTOR" in item for item in result["errors"]), result["errors"])

    def test_review_corrections_from_verifier_passes(self) -> None:
        result = validate([
            event("0001-work-order-started", "WORK_ORDER_STARTED"),
            event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            event("0003-review-corrections", "REVIEW_CORRECTIONS", subject_sha=FULL_SHA_B, actor_role="VERIFIER"),
        ])
        self.assertTrue(result["ok"], result["errors"])


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
