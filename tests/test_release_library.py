"""Release library v0.1 tests (WO-NL5-001-B-R1; extended by repair R1).

Guarantees: the committed package is exactly what the deterministic builder
produces from published evidence (byte-for-byte, manifest included), every card
number matches its evidence source, protocol pins are DERIVED from the frozen
run-config evidence (no hand-transcribed scientific values), the manifest is
deterministic frozen release metadata, the frozen reproduction rule ships with
the package, and the 74b honest gap is preserved (never encoded as PASS or as
a fabricated value).
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


def read_oxdna_input(path: Path) -> dict:
    """Independent re-parse of a frozen run-config input file (test-side)."""
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.split("#", 1)[0].strip()
        if text and "=" in text:
            key, _, value = text.partition("=")
            values[key.strip()] = value.strip()
    return values


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


class TestEvidenceDerivedPins(unittest.TestCase):
    """Repair R1 (F-B1): protocol/scientific pins must be derived from the
    frozen run-config evidence, not hand-transcribed. These tests re-read the
    evidence files independently and compare them to the generated cards."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.param = load(ROOT / "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json")
        cls.confirm = load(ROOT / "docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json")
        cls.pins = load(ROOT / "scripts/hinge_family/source_pins.json")

    @staticmethod
    def _inputs(paths: list[Path]) -> list[dict]:
        return [read_oxdna_input(path) for path in paths]

    def test_0b_protocol_pins_derived_from_run_inputs(self) -> None:
        inputs = self._inputs(
            [ROOT / f"docs/work/executions/EX-NL3-002-R1/evidence/c00{i}_input.in" for i in (1, 2, 3)]
        )
        pins = card("0b")["protocol_pins"]
        self.assertEqual(pins["steps"], int(inputs[0]["steps"]))
        self.assertEqual(pins["seeds"], sorted(int(values["seed"]) for values in inputs))
        self.assertEqual(pins["seeds"], sorted(run["seed"] for run in self.confirm["runs"].values()))
        self.assertEqual(pins["temperature"], f"{int(inputs[0]['T'].rstrip('K'))} K")
        self.assertEqual(pins["options"]["salt_concentration"], float(inputs[0]["salt_concentration"]))
        self.assertEqual(pins["options"]["print_conf_interval"], int(inputs[0]["print_conf_interval"]))
        self.assertEqual(pins["options"]["print_energy_every"], int(inputs[0]["print_energy_every"]))
        evidence_environment = load(
            ROOT / "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/component-card-0b.json"
        )["environment"]
        self.assertEqual(pins["platform"], evidence_environment["platform"])
        self.assertEqual(pins["model"], evidence_environment["model"])

    def test_parametric_protocol_pins_derived_from_run_inputs(self) -> None:
        for variant in ("11b", "32b", "53b"):
            with self.subTest(variant=variant):
                inputs = self._inputs(
                    [
                        ROOT / f"docs/work/executions/EX-NL3-002-PARAM-{variant.upper()}-R1/evidence/s00{i}_input.in"
                        for i in (1, 2, 3)
                    ]
                )
                pins = card(variant)["protocol_pins"]
                reps = self.param["variants"][variant]["per_replica_common_window"]
                self.assertEqual(pins["seeds"], sorted(int(values["seed"]) for values in inputs))
                self.assertEqual(pins["seeds"], sorted(reps[key]["seed"] for key in sorted(reps)))
                self.assertEqual(pins["temperature"], f"{int(inputs[0]['T'].rstrip('K'))} K")
                self.assertEqual(pins["options"]["salt_concentration"], float(inputs[0]["salt_concentration"]))
                self.assertEqual(pins["options"]["print_conf_interval"], int(inputs[0]["print_conf_interval"]))
                self.assertEqual(pins["options"]["print_energy_every"], int(inputs[0]["print_energy_every"]))

    def test_window_steps_derived_from_summary(self) -> None:
        window_steps = int(self.param["window"]["common_window_steps"])
        self.assertEqual(window_steps, 150000)
        for variant in ("0b", "11b", "32b", "53b"):
            with self.subTest(variant=variant):
                pooled = card(variant)["measured_observables"]["hinge_angle_common_window_150k"]
                source_window = self.param["variants"][variant]["pooled_common_window"]["angle_stats_valid_frames"]
                self.assertEqual(pooled["estimate"], source_window["median_deg"])
                self.assertEqual(pooled["n"], source_window["n_frames"])
                self.assertIn(f"{window_steps // 1000}k", pooled["convention"])
        # steps pin: the common window for variants fully inside it; None with
        # an evidence-derived note otherwise (11b ran past the window).
        for variant in ("11b", "32b", "53b"):
            reps = self.param["variants"][variant]["per_replica_common_window"]
            fully_inside = all(
                reps[key]["window"]["frames_in_window"] == reps[key]["window"]["frames_total"]
                for key in reps
            )
            pins = card(variant)["protocol_pins"]
            if fully_inside:
                self.assertEqual(pins["steps"], window_steps)
            else:
                self.assertIsNone(pins["steps"])
                self.assertIn("окно", pins["notes"])

    def test_bootstrap_text_derived_from_evidence(self) -> None:
        for variant, observable in (
            ("0b", "hinge_angle_confirmatory_200k"),
            ("11b", "hinge_angle_common_window_150k"),
        ):
            with self.subTest(variant=variant):
                bootstrap = card(variant)["measured_observables"][observable]["distribution"]["bootstrap"]
                steps_text = " ".join(card(variant)["reproduction"]["steps"])
                self.assertIn(str(bootstrap["resamples"]), steps_text)
                self.assertIn(f"seed {bootstrap['seed']}", steps_text)

    def test_rights_pins_derived_from_source_pins(self) -> None:
        upstream = self.pins["source"]
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                self.assertEqual(card(variant)["rights"]["pinned_commit"], upstream["commit"])
                self.assertEqual(card(variant)["rights"]["upstream_repo"], upstream["repository"])
        rights = load(RELEASE_PKG / "RIGHTS.json")
        for item in rights["items"]:
            if item["rights_mode"] == "REFERENCE_ONLY":
                self.assertEqual(item["pinned_commit"], upstream["commit"])

    def test_cards_reference_frozen_rule_not_ci_band(self) -> None:
        for variant in ("0b", "11b", "32b", "53b"):
            with self.subTest(variant=variant):
                reproduction_section = card(variant)["reproduction"]
                self.assertIn("REPRODUCTION_RULE_R1", reproduction_section["tolerance_policy"])
                self.assertIn("не полоса допуска", reproduction_section["tolerance_policy"])
                self.assertNotIn("в пределах bootstrap CI95", reproduction_section["tolerance_policy"])
                self.assertTrue(any("REPRODUCTION_RULE_R1" in step for step in reproduction_section["steps"]))
        not_measured = card("74b")["reproduction"]
        self.assertNotIn("REPRODUCTION_RULE_R1", not_measured["tolerance_policy"])

    def test_manifest_is_deterministic_release_metadata(self) -> None:
        manifest = load(RELEASE_PKG / "RELEASE_MANIFEST.json")
        self.assertEqual(manifest["generated_at_utc"], build_library.RELEASE_GENERATED_AT_UTC)
        self.assertEqual(manifest["subject"], build_library.RELEASE_SUBJECT)
        self.assertEqual(manifest["generated_by"], f"release.build_library {build_library.VERSION}")
        self.assertNotIn(card_lint.MANIFEST_NAME, [entry["path"] for entry in manifest["files"]])

    def test_builder_cross_checks_fail_closed(self) -> None:
        good = read_oxdna_input(ROOT / "docs/work/executions/EX-NL3-002-R1/evidence/c001_input.in")
        del good["seed"]
        with self.assertRaises(build_library.BuildError):
            build_library._protocol_from_inputs("0b", build_library.CONFIRM_RUN_INPUTS, [1, 2, 3])
        with self.assertRaises(build_library.BuildError):
            build_library._shared_config_gate(
                {"files": {"MD_Hinges/pro_CPU.in": {"sha256": "0" * 64}}},
                "11b",
                {"files": {"MD_Hinges/pro_CPU.in": {"sha256": "1" * 64}}},
            )
        # the happy path must hold for the published evidence
        confirm = load(ROOT / "docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json")
        seeds = [confirm["runs"][run_id]["seed"] for run_id in sorted(confirm["runs"])]
        protocol = build_library._protocol_from_inputs(
            "0b",
            build_library.CONFIRM_RUN_INPUTS,
            seeds,
            shared={
                "salt_concentration": float(good["salt_concentration"]),
                "temperature": f"{int(good['T'].rstrip('K'))} K",
            },
        )
        self.assertEqual(protocol["seeds"], sorted(seeds))


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
