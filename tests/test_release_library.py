"""Release library tests after NL5-001-B Repair R1.

No scientific control numbers are duplicated here: expected machine fields are
read from published evidence/config and compared to a fresh R1.2 build.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release import build_library_r12, card_lint, reproduction_rule  # noqa: E402

VARIANTS = ["0b", "11b", "32b", "53b", "74b"]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class BuiltPackageCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pkg = Path(cls.tmp.name) / "pkg"
        build_library_r12.build(cls.pkg)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def card(self, variant: str) -> dict:
        return load(self.pkg / "families" / "dna_hinge" / "cards" / f"{variant}.card.json")


class TestBuilderDeterminism(BuiltPackageCase):
    def test_two_independent_full_builds_byte_identical_including_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            other = Path(tmp) / "pkg"
            build_library_r12.build(other)
            a = {p.relative_to(self.pkg).as_posix(): p.read_bytes() for p in self.pkg.rglob("*") if p.is_file()}
            b = {p.relative_to(other).as_posix(): p.read_bytes() for p in other.rglob("*") if p.is_file()}
            self.assertEqual(a, b)
            self.assertIn("RELEASE_MANIFEST.json", a)


class TestPackageIntegrity(BuiltPackageCase):
    def test_package_lints_clean(self) -> None:
        report = card_lint.run_package(self.pkg)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["cards"], [f"families/dna_hinge/cards/{v}.card.json" for v in VARIANTS])

    def test_manifest_is_deterministic_and_verifies(self) -> None:
        manifest = load(self.pkg / "RELEASE_MANIFEST.json")
        self.assertNotIn("generated_at_utc", manifest)
        report = card_lint.manifest_verify(self.pkg, card_lint.MANIFEST_SCHEMA)
        self.assertTrue(report["ok"], report["errors"])

    def test_variant_statuses(self) -> None:
        report = card_lint.run_package(self.pkg)
        for variant in ("0b", "11b", "32b", "53b"):
            self.assertEqual(report["variant_status"][variant], "MEASURED")
        self.assertEqual(report["variant_status"]["74b"], "NOT_MEASURED")


class TestEvidenceDerivedNumbers(BuiltPackageCase):
    def test_observables_match_published_evidence(self) -> None:
        param = load(ROOT / "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json")
        confirm = load(ROOT / "docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json")

        obs0 = self.card("0b")["measured_observables"]["hinge_angle_confirmatory_200k"]
        self.assertEqual(obs0["estimate"], confirm["pooled_angle_stats_valid_frames"]["median_deg"])
        self.assertEqual(obs0["n"], confirm["pooled_angle_stats_valid_frames"]["n_frames"])
        self.assertEqual(obs0["uncertainty"], confirm["pooled_angle_stats_valid_frames"]["bootstrap"]["ci95"])

        for variant in ("11b", "32b", "53b"):
            source = param["variants"][variant]["pooled_common_window"]["angle_stats_valid_frames"]
            obs = self.card(variant)["measured_observables"]["hinge_angle_common_window_150k"]
            self.assertEqual(obs["estimate"], source["median_deg"])
            self.assertEqual(obs["n"], source["n_frames"])
            self.assertEqual(obs["uncertainty"], source["bootstrap"]["ci95"])

    def test_protocol_pins_match_evidence(self) -> None:
        evidence0 = load(ROOT / "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/component-card-0b.json")
        card0 = self.card("0b")
        self.assertEqual(card0["protocol_pins"]["steps"], evidence0["environment"]["steps_confirmatory"])
        self.assertEqual(card0["protocol_pins"]["seeds"], evidence0["simulation_confidence"]["seeds"])
        self.assertEqual(card0["protocol_pins"]["options"]["print_conf_interval"], evidence0["environment"]["print_conf_interval"])
        self.assertEqual(card0["protocol_pins"]["options"]["print_energy_every"], evidence0["environment"]["print_energy_every"])
        self.assertEqual(card0["protocol_pins"]["options"]["salt_concentration"], evidence0["environment"]["salt_concentration"])

        for variant in ("11b", "32b", "53b"):
            summary = load(ROOT / f"docs/work/executions/EX-NL3-002-PARAM-{variant.upper()}-R1/evidence/PARAM-{variant.upper()}-summary.json")
            reports = [summary["run_reports"][key] for key in sorted(summary["run_reports"])]
            card = self.card(variant)
            self.assertEqual(card["protocol_pins"]["seeds"], [row["seed"] for row in reports])
            self.assertEqual(card["protocol_pins"]["steps"], reports[0]["steps_requested"])

    def test_reproduction_rule_payload_comes_from_replica_medians(self) -> None:
        for variant in ("0b", "11b", "32b", "53b"):
            card = self.card(variant)
            expected = card["reproduction"]["expected"]
            self.assertEqual(expected["rule_id"], reproduction_rule.RULE_ID)
            self.assertEqual(expected["bootstrap_ci_role"], "DESCRIPTIVE_ONLY_NOT_A_REPRODUCTION_TOLERANCE")
            self.assertEqual(expected["required_fresh_replicas"], 3)
            self.assertIn("replica median", card["reproduction"]["tolerance_policy"])


class TestDigestHonesty(BuiltPackageCase):
    def test_registry_blob_and_size_match_source_pins(self) -> None:
        pins = load(ROOT / "scripts/hinge_family/source_pins.json")
        for variant in VARIANTS:
            gates = self.card(variant)["source_provenance"]["digest_gates"]
            for rel in (f"MD_Hinges/{variant}.conf", f"MD_Hinges/{variant}.top"):
                self.assertEqual(gates[rel]["blob_sha1"], pins["files"][rel]["blob_sha1"])
                self.assertEqual(gates[rel]["size_bytes"], pins["files"][rel]["size_bytes"])
                self.assertEqual("sha256" in gates[rel], "sha256_status" in gates[rel])

    def test_74b_honest_gap(self) -> None:
        card = self.card("74b")
        self.assertEqual(card["measurement_status"], "NOT_MEASURED")
        self.assertEqual(card["measured_observables"], {})
        self.assertEqual(card["reproduction"]["expected"], {})
        self.assertFalse(card["known_gaps"][0]["blocking_release"])
        self.assertIn("NOT_RUN", card["scientific_outcome"])


if __name__ == "__main__":
    unittest.main()
