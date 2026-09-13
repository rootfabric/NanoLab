"""Release library v0.1 tests (WO-NL5-001-B-R1).

Guarantees: the committed package is exactly what the deterministic builder
produces from published evidence (byte-for-byte), every card number matches
its evidence source, digest entries match source_pins, and the 74b honest
gap is preserved (never encoded as PASS or as a fabricated value).
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release import build_library, card_lint  # noqa: E402

RELEASE_PKG = ROOT / "releases" / "nanolab-components-v0.1"
VARIANTS = ["0b", "11b", "32b", "53b", "74b"]

# Control numbers from published evidence (parametric-summary.json / confirmatory-summary.json).
EXPECTED_MEDIANS = {
    "0b": ("hinge_angle_confirmatory_200k", 65.976921401, 150),
    "11b": ("hinge_angle_common_window_150k", 73.928725839, 111),
    "32b": ("hinge_angle_common_window_150k", 78.091845516, 111),
    "53b": ("hinge_angle_common_window_150k", 132.357787730, 111),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def card(variant: str) -> dict:
    return load(RELEASE_PKG / "families" / "dna_hinge" / "cards" / f"{variant}.card.json")


class TestBuilderDeterminism(unittest.TestCase):
    def test_builder_check_byte_identical(self) -> None:
        self.assertEqual(build_library.check(), [])


class TestPackageIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = card_lint.run_package(RELEASE_PKG)

    def test_package_lints_clean(self) -> None:
        self.assertTrue(self.report["ok"], self.report["errors"])
        self.assertEqual(
            self.report["cards"],
            [f"families/dna_hinge/cards/{v}.card.json" for v in VARIANTS],
        )

    def test_manifest_verifies(self) -> None:
        report = card_lint.manifest_verify(RELEASE_PKG, card_lint.MANIFEST_SCHEMA)
        self.assertTrue(report["ok"], report["errors"])

    def test_variant_statuses(self) -> None:
        status = self.report["variant_status"]
        for variant in ("0b", "11b", "32b", "53b"):
            self.assertEqual(status[variant], "MEASURED")
        self.assertIn("NOT_MEASURED", status["74b"])


class TestVerbatimNumbers(unittest.TestCase):
    def test_control_medians_exact(self) -> None:
        for variant, (observable, median, n) in EXPECTED_MEDIANS.items():
            with self.subTest(variant=variant):
                observable_data = card(variant)["measured_observables"][observable]
                self.assertEqual(observable_data["estimate"], median)
                self.assertEqual(observable_data["n"], n)

    def test_ci95_matches_evidence(self) -> None:
        param = load(ROOT / "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json")
        confirm = load(ROOT / "docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json")
        self.assertEqual(
            card("0b")["measured_observables"]["hinge_angle_confirmatory_200k"]["uncertainty"],
            confirm["pooled_angle_stats_valid_frames"]["bootstrap"]["ci95"],
        )
        for variant in ("11b", "32b", "53b"):
            pooled = param["variants"][variant]["pooled_common_window"]["angle_stats_valid_frames"]
            self.assertEqual(
                card(variant)["measured_observables"]["hinge_angle_common_window_150k"]["uncertainty"],
                pooled["bootstrap"]["ci95"],
            )

    def test_report_table_matches_cards(self) -> None:
        report_text = (RELEASE_PKG / "reports" / "family-report.md").read_text(encoding="utf-8")
        for variant, (_, median, _) in EXPECTED_MEDIANS.items():
            self.assertIn(f"{median:.9f}", report_text, f"{variant} median missing from report")


class TestDigestHonesty(unittest.TestCase):
    def test_digest_gates_match_source_pins(self) -> None:
        pins = load(ROOT / "scripts/hinge_family/source_pins.json")
        for variant in VARIANTS:
            gates = card(variant)["source_provenance"]["digest_gates"]
            for rel in (f"MD_Hinges/{variant}.conf", f"MD_Hinges/{variant}.top"):
                with self.subTest(variant=variant, rel=rel):
                    self.assertEqual(gates[rel]["blob_sha1"], pins["files"][rel]["blob_sha1"])
                    self.assertEqual(gates[rel]["size_bytes"], pins["files"][rel]["size_bytes"])

    def test_sha256_status_invariant(self) -> None:
        for variant in VARIANTS:
            for rel, digest in card(variant)["source_provenance"]["digest_gates"].items():
                with self.subTest(variant=variant, rel=rel):
                    self.assertEqual("sha256" in digest, "sha256_status" in digest, rel)

    def test_0b_content_verified_others_computed(self) -> None:
        conf_0b = card("0b")["source_provenance"]["digest_gates"]["MD_Hinges/0b.conf"]
        self.assertEqual(conf_0b["sha256_status"], "CONTENT_VERIFIED")
        conf_11b = card("11b")["source_provenance"]["digest_gates"]["MD_Hinges/11b.conf"]
        self.assertEqual(conf_11b["sha256_status"], "COMPUTED_NOT_VERIFIED")


class TestHonestGap74b(unittest.TestCase):
    def test_not_measured_with_known_gap(self) -> None:
        card_74b = card("74b")
        self.assertEqual(card_74b["measurement_status"], "NOT_MEASURED")
        self.assertEqual(card_74b["measured_observables"], {})
        self.assertEqual(card_74b["reproduction"]["expected"], {})
        gaps = card_74b["known_gaps"]
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["status"], "KNOWN_GAP")
        self.assertFalse(gaps[0]["blocking_release"])
        self.assertIn("NOT_RUN", card_74b["scientific_outcome"])

    def test_failure_facts_recorded(self) -> None:
        design = card("74b")["design"]
        self.assertEqual(design["error_class"], "FAILED_TWO_DOMINANT_BLOCKS")
        self.assertTrue(design["deterministic_identical_error"])
        self.assertEqual(design["derivation_attempts"], 2)


if __name__ == "__main__":
    unittest.main()
