"""Legacy out-of-enum event_type tolerance tests (science integration 2026-09-30).

Acceptance targets (docs/infra/VALIDATION_GATES_R1.md section 2.5):
- the single immutable science event EX-NL5-002-E-R1
  0007-continuation-paired-analysis-and-handoff was published with
  event_type "END_ANALYSIS" (outside the validator enum) and is never edited
  (AGENTS.md: corrections are recorded as new events);
- LEGACY_END_ANALYSIS_EVENTS admits EXACTLY that (execution_id, event_id) pair;
- any other execution, event_id, or a brand-new END_ANALYSIS event FAILS;
- the real science closure directory validates OK (regression pin for
  hosted-ci Check 3 on the integration branch).

Run: python -m unittest discover -s tests -t .
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from harness.work_cli import inspect_execution  # noqa: E402

LEGACY_EXECUTION_ID = "EX-NL5-002-E-R1"
LEGACY_EVENT_ID = "0007-continuation-paired-analysis-and-handoff"
OTHER_EXECUTION_ID = "EX-OTHER-R1"
WORK_ORDER_ID = "WO-NL5-002-E-R1"
FULL_SHA = "0123456789abcdef0123456789abcdef01234567"


def event(event_id: str, event_type: str, *, execution_id: str = LEGACY_EXECUTION_ID, seq: int = 0) -> dict:
    return {
        "schema_version": 1,
        "event_id": event_id,
        "timestamp_utc": "2026-09-27T10:00:{:02d}Z".format(seq % 60),
        "execution_id": execution_id,
        "work_order_id": WORK_ORDER_ID,
        "event_type": event_type,
        "actor_role": "SCIENTIFIC_OPERATOR",
        "subject_sha": FULL_SHA,
        "summary": "test event",
        "blocker": None,
    }


def science_shape() -> list[dict]:
    """Mirror the published science chain: mid-chain END_ANALYSIS legacy event
    followed by a CONTINUATION_CHECKPOINT (no terminal yet)."""
    return [
        event("0001-work-order-started", "WORK_ORDER_STARTED", seq=1),
        event("0002-continuation", "CONTINUATION_CHECKPOINT", seq=2),
        event(LEGACY_EVENT_ID, "END_ANALYSIS", seq=3),
        event("0008-continuation", "CONTINUATION_CHECKPOINT", seq=4),
    ]


def build_execution(events: list[dict], execution_id: str = LEGACY_EXECUTION_ID) -> Path:
    import json
    import tempfile

    root = Path(tempfile.mkdtemp()) / execution_id
    (root / "events").mkdir(parents=True)
    passport = {
        "schema_version": 1,
        "execution_id": execution_id,
        "work_order_id": WORK_ORDER_ID,
        "checkpoint": "NL5",
        "base_sha": FULL_SHA,
        "branch": "work/test-r1",
        "risk_class": "HIGH",
        "claim_class": "C1_COMPUTATIONAL_REPRODUCTION",
        "allowed_paths": [],
        "started_at_utc": "2026-09-27T09:00:00Z",
        "status": "IN_PROGRESS",
    }
    (root / "passport.json").write_text(json.dumps(passport, indent=2) + "\n", encoding="utf-8")
    for item in events:
        target = root / "events" / f"{item['event_id']}.json"
        target.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
    return root


def validate(events: list[dict], execution_id: str = LEGACY_EXECUTION_ID) -> dict:
    return inspect_execution(build_execution(events, execution_id))


class LegacyEndAnalysisToleranceTests(unittest.TestCase):
    def test_exact_legacy_pair_is_accepted(self) -> None:
        result = validate(science_shape())
        self.assertTrue(result["ok"], result["errors"])
        self.assertFalse(result["has_terminal_handoff"])

    def test_legacy_pair_in_other_execution_fails(self) -> None:
        events = [
            event("0001-work-order-started", "WORK_ORDER_STARTED", execution_id=OTHER_EXECUTION_ID, seq=1),
            event(LEGACY_EVENT_ID, "END_ANALYSIS", execution_id=OTHER_EXECUTION_ID, seq=2),
        ]
        result = validate(events, execution_id=OTHER_EXECUTION_ID)
        self.assertFalse(result["ok"])
        self.assertTrue(any("unsupported event_type" in item for item in result["errors"]), result["errors"])

    def test_legacy_type_with_other_event_id_in_same_execution_fails(self) -> None:
        events = science_shape() + [event("0009-new-end-analysis", "END_ANALYSIS", seq=5)]
        result = validate(events)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any("0009-new-end-analysis.json: unsupported event_type" in item for item in result["errors"]),
            result["errors"],
        )

    def test_end_analysis_in_unrelated_new_execution_fails(self) -> None:
        events = [
            event("0001-work-order-started", "WORK_ORDER_STARTED", execution_id=OTHER_EXECUTION_ID, seq=1),
            event("0002-end-analysis", "END_ANALYSIS", execution_id=OTHER_EXECUTION_ID, seq=2),
        ]
        result = validate(events, execution_id=OTHER_EXECUTION_ID)
        self.assertFalse(result["ok"])
        self.assertTrue(any("unsupported event_type" in item for item in result["errors"]), result["errors"])

    def test_real_science_closure_directory_validates_ok(self) -> None:
        subject = REPO_ROOT / "docs" / "work" / "executions" / LEGACY_EXECUTION_ID
        if not subject.is_dir():  # pragma: no cover - repository layout guard
            self.skipTest("science closure directory not present in this checkout")
        result = inspect_execution(subject)
        self.assertTrue(result["ok"], result["errors"])
        self.assertIn("END_ANALYSIS", result["event_types"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
