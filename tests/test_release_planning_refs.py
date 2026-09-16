"""No stale planning-document references outside immutable historical events.

The nonexistent execution-program planning document was superseded by the
durable POST_MVP_DEVELOPMENT_ROUTE_R1 (Phase B, A..D decomposition). Mutable
records (work orders, passports, release docs) must not carry the stale
filename literal anymore.

Immutable historical events are the documented exception (AGENTS.md: old
experiment events are never edited; corrections are appended as new events).
Following the hosted-ci Check 1 precedent for durable evidence bytes, every
such exception is pinned by exact path AND sha256: any content drift fails
and requires a reviewed erratum instead of a silent rewrite of history.
"""

from pathlib import Path
import hashlib
import unittest

ROOT = Path(__file__).resolve().parents[1]
STALE = "POST_MVP_EXECUTION_PROGRAM_R1"

# Immutable historical events that factually cite the superseded planning
# document at start time. Key: exact repo-relative path; value: sha256 of the
# pinned historical bytes. A digest mismatch is reported as an offender.
IMMUTABLE_EVENT_EXCEPTIONS = {
    "docs/work/executions/EX-NL5-001-A-R1/events/0001-work-order-started.json": (
        "26f939d551576b0fdea93784eaf5977a8f0af057a7835a3a3c713abf9ea41fa2"
    ),
}


class TestReleasePlanningReferences(unittest.TestCase):
    def test_no_stale_post_mvp_execution_program_reference(self) -> None:
        offenders = []
        for base in (ROOT / "docs" / "release", ROOT / "docs" / "work"):
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix not in {".md", ".json"}:
                    continue
                rel = path.relative_to(ROOT).as_posix()
                if STALE not in path.read_text(encoding="utf-8", errors="replace"):
                    continue
                expected = IMMUTABLE_EVENT_EXCEPTIONS.get(rel)
                if expected is not None:
                    actual = hashlib.sha256(path.read_bytes()).hexdigest()
                    if actual == expected:
                        continue
                    offenders.append(f"{rel} (pinned immutable event drifted from reviewed sha256; erratum required)")
                    continue
                offenders.append(rel)
        self.assertEqual(offenders, [], f"stale planning reference found: {offenders}")


if __name__ == "__main__":
    unittest.main()
