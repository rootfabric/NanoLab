from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
STALE = "POST_MVP_EXECUTION_PROGRAM_R1"


class TestReleasePlanningReferences(unittest.TestCase):
    def test_no_stale_post_mvp_execution_program_reference(self) -> None:
        offenders = []
        for base in (ROOT / "docs" / "release", ROOT / "docs" / "work"):
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix not in {".md", ".json"}:
                    continue
                if STALE in path.read_text(encoding="utf-8", errors="replace"):
                    offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [], f"stale planning reference found: {offenders}")


if __name__ == "__main__":
    unittest.main()
