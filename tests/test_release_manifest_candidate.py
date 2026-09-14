"""Committed release-manifest exactness checks for R1.2 repair.

On mismatch the test prints the exact deterministic manifest computed from the
committed package bytes. The diagnostic is intentional during repair and becomes
an ordinary equality regression once the committed manifest is refreshed.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release import card_lint  # noqa: E402


class TestCommittedReleaseManifest(unittest.TestCase):
    maxDiff = None

    def _assert_manifest(self, pkg: Path, generated_by: str, label: str) -> None:
        actual = json.loads((pkg / card_lint.MANIFEST_NAME).read_text(encoding="utf-8"))
        expected = card_lint.manifest_create(pkg, generated_by=generated_by)
        if actual != expected:
            print(f"EXPECTED_{label}_MANIFEST_BEGIN")
            print(json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True))
            print(f"EXPECTED_{label}_MANIFEST_END")
        self.assertEqual(actual, expected)
        report = card_lint.manifest_verify(pkg, card_lint.MANIFEST_SCHEMA)
        self.assertTrue(report["ok"], report["errors"])

    def test_real_release_manifest_exact(self) -> None:
        self._assert_manifest(
            ROOT / "releases" / "nanolab-components-v0.1",
            "release.build_library_r12 deterministic-r1.2",
            "REAL",
        )

    def test_example_release_manifest_exact(self) -> None:
        self._assert_manifest(
            ROOT / "examples" / "release" / "nanolab-components-v0.1",
            "release.card_lint manifest create deterministic-r1.2",
            "EXAMPLE",
        )


if __name__ == "__main__":
    unittest.main()
