"""Reviewer-repair regression tests for NL5-001-B R1.2."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release import build_library_r12, card_lint, reproduction_rule  # noqa: E402


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestFrozenReproductionRule(unittest.TestCase):
    REF = [65.095434789, 65.708669763, 67.236579608]

    def test_fresh_replica_outside_old_pooled_ci_is_not_automatic_mismatch(self) -> None:
        # 65.50 is outside the old pooled bootstrap CI [65.6749, 66.3183],
        # but independent-replica classification must not use that CI as a prediction band.
        verdict = reproduction_rule.classify(self.REF, [65.50, 65.90, 66.40])
        self.assertEqual(verdict.outcome, "MATCH")

    def test_complete_directional_separation_is_mismatch(self) -> None:
        verdict = reproduction_rule.classify(self.REF, [68.0, 68.2, 68.4])
        self.assertEqual(verdict.outcome, "MISMATCH")

    def test_insufficient_replicas_is_inconclusive(self) -> None:
        verdict = reproduction_rule.classify(self.REF, [65.8, 66.0])
        self.assertEqual(verdict.outcome, "INCONCLUSIVE")

    def test_technical_failure_is_not_scientific_mismatch(self) -> None:
        verdict = reproduction_rule.classify(self.REF, [], technical_ok=False)
        self.assertEqual(verdict.outcome, "INCONCLUSIVE")


class TestEvidenceDerivedPins(unittest.TestCase):
    def test_temp_build_reads_protocol_pins_from_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            build_library_r12.build(pkg)

            evidence_0b = load(ROOT / "docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/component-card-0b.json")
            card_0b = load(pkg / "families/dna_hinge/cards/0b.card.json")
            self.assertEqual(card_0b["protocol_pins"]["steps"], evidence_0b["environment"]["steps_confirmatory"])
            self.assertEqual(card_0b["protocol_pins"]["seeds"], evidence_0b["simulation_confidence"]["seeds"])
            self.assertEqual(card_0b["protocol_pins"]["options"]["print_conf_interval"], evidence_0b["environment"]["print_conf_interval"])
            self.assertEqual(card_0b["protocol_pins"]["options"]["print_energy_every"], evidence_0b["environment"]["print_energy_every"])
            self.assertEqual(card_0b["protocol_pins"]["options"]["salt_concentration"], evidence_0b["environment"]["salt_concentration"])

            for variant in ("11b", "32b", "53b"):
                summary = load(ROOT / f"docs/work/executions/EX-NL3-002-PARAM-{variant.upper()}-R1/evidence/PARAM-{variant.upper()}-summary.json")
                reports = [summary["run_reports"][key] for key in sorted(summary["run_reports"])]
                card = load(pkg / f"families/dna_hinge/cards/{variant}.card.json")
                self.assertEqual(card["protocol_pins"]["seeds"], [row["seed"] for row in reports])
                self.assertEqual(card["protocol_pins"]["steps"], reports[0]["steps_requested"])
                self.assertTrue(all(row["steps_requested"] == card["protocol_pins"]["steps"] for row in reports))

    def test_two_full_temp_builds_are_byte_identical_including_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a"
            b = Path(tmp) / "b"
            build_library_r12.build(a)
            build_library_r12.build(b)
            files_a = {p.relative_to(a).as_posix(): p.read_bytes() for p in a.rglob("*") if p.is_file()}
            files_b = {p.relative_to(b).as_posix(): p.read_bytes() for p in b.rglob("*") if p.is_file()}
            self.assertEqual(files_a, files_b)
            self.assertIn("RELEASE_MANIFEST.json", files_a)
            manifest = json.loads(files_a["RELEASE_MANIFEST.json"])
            self.assertNotIn("generated_at_utc", manifest)


class TestManifestHardening(unittest.TestCase):
    def _base_manifest(self, pkg: Path) -> dict:
        return card_lint.manifest_create(pkg)

    def _write_and_verify(self, pkg: Path, manifest: dict) -> dict:
        (pkg / card_lint.MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return card_lint.manifest_verify(pkg, card_lint.MANIFEST_SCHEMA)

    def test_duplicate_identical_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            build_library_r12.build(pkg)
            m = self._base_manifest(pkg)
            m["files"].append(copy.deepcopy(m["files"][0]))
            report = self._write_and_verify(pkg, m)
            self.assertFalse(report["ok"])
            self.assertTrue(any("duplicate path" in e for e in report["errors"]))

    def test_duplicate_conflicting_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            build_library_r12.build(pkg)
            m = self._base_manifest(pkg)
            dup = copy.deepcopy(m["files"][0])
            dup["sha256"] = "0" * 64
            m["files"].append(dup)
            report = self._write_and_verify(pkg, m)
            self.assertFalse(report["ok"])
            self.assertTrue(any("duplicate path" in e for e in report["errors"]))

    def test_unsafe_paths_rejected(self) -> None:
        bad_paths = ["/absolute", "../escape", "dir\\file"]
        for bad in bad_paths:
            with self.subTest(path=bad), tempfile.TemporaryDirectory() as tmp:
                pkg = Path(tmp) / "pkg"
                build_library_r12.build(pkg)
                m = self._base_manifest(pkg)
                m["files"][0]["path"] = bad
                report = self._write_and_verify(pkg, m)
                self.assertFalse(report["ok"])
                self.assertTrue(any("path" in e for e in report["errors"]))


if __name__ == "__main__":
    unittest.main()
