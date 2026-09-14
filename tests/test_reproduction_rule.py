"""Frozen reproduction rule REPRODUCTION_RULE_R1 tests (repair R1, finding F-B3).

Guarantees (docs/evidence/NL5-001-B/REPAIR_MAP_R1.md, R1 required tests):
  * a control campaign that should reproduce is classified REPRODUCTION_MATCH;
  * a campaign statistic OUTSIDE the original pooled bootstrap CI95 is NOT
    automatically a scientific mismatch (the CI95 is not an acceptance band);
  * insufficient valid replicas yield an explicit non-pass (INCONCLUSIVE),
    never an implicit PASS;
  * technical failures stay separated from scientific mismatch;
  * the frozen constants are pinned (no silent re-tuning).
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release import reproduction  # noqa: E402

RELEASE_PKG = ROOT / "releases" / "nanolab-components-v0.1"
CARD_0B = RELEASE_PKG / "families" / "dna_hinge" / "cards" / "0b.card.json"
CARD_11B = RELEASE_PKG / "families" / "dna_hinge" / "cards" / "11b.card.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate(medians: list[float], gates: list[bool] | None = None, card_id: str = "dna_hinge/0b") -> dict:
    return {
        "rule": reproduction.RULE_ID,
        "card": card_id,
        "replicas": [
            {
                "replica_id": f"C-NEW-{index + 1:03d}",
                "median_deg": median,
                "frames_valid": 37,
                "frames_total": 37,
                "gates_passed": True if gates is None else gates[index],
            }
            for index, median in enumerate(medians)
        ],
    }


def reference_band(card: dict) -> tuple[float, float]:
    observable = reproduction._select_observable(card, {})[1]
    values = sorted(reproduction._reference_medians(observable).values())
    return values[0], values[-1]


class TestFrozenConstants(unittest.TestCase):
    def test_rule_identity_is_pinned(self) -> None:
        self.assertEqual(reproduction.RULE_ID, "REPRODUCTION_RULE_R1")
        self.assertEqual(reproduction.MIN_VALID_REPLICAS, 3)
        self.assertEqual(reproduction.MIN_REFERENCE_REPLICAS, 2)

    def test_rule_document_is_present_and_frozen(self) -> None:
        text = (ROOT / "docs" / "research" / "REPRODUCTION_RULE_R1.md").read_text(encoding="utf-8")
        self.assertIn("FROZEN", text)
        self.assertIn(reproduction.RULE_ID, text)
        self.assertIn("INCONCLUSIVE", text)
        self.assertIn("TECHNICAL_FAILURE", text)


class TestVerdictsOnRealCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.card_0b = load(CARD_0B)

    def test_control_campaign_reproduces(self) -> None:
        band_min, band_max = reference_band(self.card_0b)
        middle = (band_min + band_max) / 2
        report = reproduction.evaluate(self.card_0b, candidate([middle - 0.1, middle, middle + 0.1]))
        self.assertEqual(report["verdict"], "REPRODUCTION_MATCH")
        self.assertTrue(report["ok"])

    def test_outside_pooled_ci_is_not_a_mismatch(self) -> None:
        """F-B3 regression: the pooled bootstrap CI95 must not act as the
        acceptance band. A statistic between the CI edge and the band edge is a
        legitimate reproduction of the original between-replica spread."""
        observable = reproduction._select_observable(self.card_0b, {})[1]
        ci_low, ci_high = observable["uncertainty"]
        band_min, band_max = reference_band(self.card_0b)
        # The original card itself provides the counterexample: at least one
        # own replica median lies outside the pooled CI95 by construction.
        self.assertGreater(band_max, ci_high, "0b reference must demonstrate CI != band")
        outside_ci_inside_band = ci_high + (band_max - ci_high) / 2
        report = reproduction.evaluate(
            self.card_0b, candidate([outside_ci_inside_band - 0.05, outside_ci_inside_band, outside_ci_inside_band + 0.05])
        )
        self.assertEqual(report["verdict"], "REPRODUCTION_MATCH")
        self.assertTrue(report["ci95_is_not_acceptance_band"])
        self.assertEqual(report["reference_pooled_ci95"], observable["uncertainty"])

    def test_outside_band_is_mismatch(self) -> None:
        _, band_max = reference_band(self.card_0b)
        high = band_max + 0.5
        report = reproduction.evaluate(self.card_0b, candidate([high - 0.1, high, high + 0.1]))
        self.assertEqual(report["verdict"], "REPRODUCTION_MISMATCH")
        self.assertFalse(report["ok"])

    def test_below_band_is_mismatch(self) -> None:
        band_min, _ = reference_band(self.card_0b)
        low = band_min - 0.5
        report = reproduction.evaluate(self.card_0b, candidate([low - 0.1, low, low + 0.1]))
        self.assertEqual(report["verdict"], "REPRODUCTION_MISMATCH")

    def test_band_boundaries_are_inclusive(self) -> None:
        band_min, band_max = reference_band(self.card_0b)
        report = reproduction.evaluate(self.card_0b, candidate([band_min, (band_min + band_max) / 2, band_max]))
        self.assertEqual(report["verdict"], "REPRODUCTION_MATCH")

    def test_two_valid_replicas_are_inconclusive_not_pass(self) -> None:
        report = reproduction.evaluate(self.card_0b, candidate([66.0, 66.1, 66.2], gates=[True, True, False]))
        self.assertEqual(report["verdict"], "INCONCLUSIVE")
        self.assertFalse(report["ok"])
        self.assertIn("C-NEW-003", report["candidate_statistic"]["excluded"])

    def test_one_valid_replica_is_inconclusive(self) -> None:
        report = reproduction.evaluate(self.card_0b, candidate([66.0, 66.1, 66.2], gates=[True, False, False]))
        self.assertEqual(report["verdict"], "INCONCLUSIVE")

    def test_all_gates_failed_is_technical_failure(self) -> None:
        report = reproduction.evaluate(self.card_0b, candidate([66.0, 66.1, 66.2], gates=[False, False, False]))
        self.assertEqual(report["verdict"], "TECHNICAL_FAILURE")
        self.assertFalse(report["ok"])

    def test_empty_report_is_technical_failure(self) -> None:
        report = reproduction.evaluate(
            self.card_0b, {"rule": reproduction.RULE_ID, "card": "dna_hinge/0b", "replicas": []}
        )
        self.assertEqual(report["verdict"], "TECHNICAL_FAILURE")

    def test_even_replica_count_uses_mean_of_middle_two(self) -> None:
        band_min, band_max = reference_band(self.card_0b)
        beyond = band_max + 0.2
        # median of [beyond, beyond, beyond+0.2, beyond+0.4] = beyond+0.1 > band_max
        report = reproduction.evaluate(self.card_0b, candidate([beyond, beyond, beyond + 0.2, beyond + 0.4]))
        self.assertEqual(report["verdict"], "REPRODUCTION_MISMATCH")
        self.assertAlmostEqual(
            report["candidate_statistic"]["median_of_replica_medians_deg"], beyond + 0.1, places=12
        )

    def test_parametric_card_evaluates_on_common_window_observable(self) -> None:
        card_11b = load(CARD_11B)
        observable_name, observable = reproduction._select_observable(card_11b, {})
        self.assertEqual(observable_name, "hinge_angle_common_window_150k")
        values = sorted(observable["distribution"]["per_replica_median_deg"].values())
        report = reproduction.evaluate(
            card_11b, candidate([values[0], (values[0] + values[-1]) / 2, values[-1]], card_id="dna_hinge/11b")
        )
        self.assertEqual(report["verdict"], "REPRODUCTION_MATCH")


class TestRuleInputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.card_0b = load(CARD_0B)

    def test_wrong_rule_id_rejected(self) -> None:
        with self.assertRaises(reproduction.RuleError):
            reproduction.evaluate(self.card_0b, {"rule": "SOME_OTHER_RULE", "replicas": []})

    def test_card_mismatch_rejected(self) -> None:
        with self.assertRaises(reproduction.RuleError):
            reproduction.evaluate(self.card_0b, candidate([66.0, 66.1, 66.2], card_id="dna_hinge/53b"))

    def test_reference_with_too_few_replicas_is_inconclusive(self) -> None:
        card = json.loads(json.dumps(self.card_0b))
        observable = reproduction._select_observable(card, {})[0]
        medians = card["measured_observables"][observable]["distribution"]["per_replica_median_deg"]
        card["measured_observables"][observable]["distribution"]["per_replica_median_deg"] = {
            key: medians[key] for key in sorted(medians)[:1]
        }
        report = reproduction.evaluate(card, candidate([66.0, 66.1, 66.2]))
        self.assertEqual(report["verdict"], "INCONCLUSIVE")

    def test_not_measured_card_is_a_rule_error(self) -> None:
        card_74b = load(RELEASE_PKG / "families" / "dna_hinge" / "cards" / "74b.card.json")
        with self.assertRaises(reproduction.RuleError):
            reproduction.evaluate(card_74b, candidate([66.0, 66.1, 66.2]))

    def test_cli_exit_codes_follow_harness_style(self) -> None:
        band_min, band_max = reference_band(self.card_0b)
        middle = (band_min + band_max) / 2
        with self.subTest(case="match"):
            self.assertEqual(reproduction.main([str(CARD_0B), self._write(candidate([middle, middle, middle]))]), 0)
        with self.subTest(case="mismatch"):
            high = band_max + 1.0
            self.assertEqual(
                reproduction.main([str(CARD_0B), self._write(candidate([high, high, high]))]), 3
            )
        with self.subTest(case="rule error"):
            self.assertEqual(reproduction.main([str(CARD_0B), self._write({"rule": "NOPE", "replicas": []})]), 2)

    @staticmethod
    def _write(payload: dict) -> str:
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            return handle.name


if __name__ == "__main__":
    unittest.main()
