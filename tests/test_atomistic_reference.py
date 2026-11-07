"""Package tests use the real source records and synthetic corruptions, no ASE."""

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from atomistic.reference import DEFAULT_PACKAGE, ValidationError, main, validate_package


class ReferencePackageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.package = Path(temporary.name) / "cu-r1"
        shutil.copytree(DEFAULT_PACKAGE, self.package)
        self.protocol = self.package / "protocol.json"
        self.sources = self.package / "sources.json"
        self.facts = self.package / "source-artifacts/overton-gaffney-1955-facts.json"

    @staticmethod
    def _write(path, data):
        path.write_text(json.dumps(data), encoding="utf-8")

    @staticmethod
    def _read(path):
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _pin(path):
        raw = path.read_bytes()
        return {"sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}

    def _write_sources(self, sources):
        self._write(self.sources, sources)
        protocol = self._read(self.protocol)
        protocol["source_manifest"].update(self._pin(self.sources))
        self._write(self.protocol, protocol)

    def test_real_package_and_default_cli_are_structural_only(self):
        out = io.StringIO()
        with mock.patch.dict(sys.modules, {"ase": None}), redirect_stdout(out):
            self.assertEqual(main([]), 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["validation"], "PACKAGE_VALID")
        self.assertEqual(report["remote_pins"], "DECLARED_NOT_RECHECKED")
        self.assertEqual(report["scientific_outcome"], "NOT_EVALUATED")
        self.assertIs(report["scientific_runs_allowed"], False)
        self.assertEqual(report["physics_runs"], 0)
        self.assertEqual(report["engineering_band_gpa"], [127.827, 156.233])

    def test_tampered_manifest_and_facts_fail_local_pins(self):
        sources_raw = self.sources.read_bytes()
        self.sources.write_bytes(sources_raw + b"\n")
        with self.assertRaisesRegex(ValidationError, r"sources\.json: SHA-256"):
            validate_package(self.package)
        self.sources.write_bytes(sources_raw)
        self.facts.write_bytes(self.facts.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValidationError, "facts.json: SHA-256"):
            validate_package(self.package)

    def test_rehashed_factual_change_still_fails_crosscheck(self):
        facts = self._read(self.facts)
        facts["observable"]["value"] = 145.50
        self._write(self.facts, facts)
        sources = self._read(self.sources)
        sources["sources"][0]["artifact"].update(self._pin(self.facts))
        self._write_sources(sources)
        with self.assertRaisesRegex(ValidationError, r"source facts\.observable"):
            validate_package(self.package)

    def test_rehashed_wrong_source_units_conditions_rights_and_model_pins(self):
        cases = (
            (("observables", 0, "unit"), "MPa", r"source observable\.unit"),
            (("observables", 0, "temperature_k"), 4.2, r"source observable\.temperature_k"),
            (("observables", 0, "pressure_basis"), "exact_zero_pressure", r"source observable\.pressure_basis"),
            (("observables", 0, "source_uncertainty", "value"), 0.34, r"source uncertainty\.value"),
            (("sources", 0, "rights", "redistribute_full_text"), True, r"source\.rights"),
            (("sources", 0, "full_text_url"), "https://example.org/10.1103/PhysRev.98.969", r"source\.full_text_url"),
            (("model", "theory_doi"), None, r"model\.theory_doi"),
            (("model", "release_metadata_url"), "https://example.org/", r"model\.release_metadata_url"),
            (("model", "artifacts", 1, "sha256"), "invalid", r"ase-emt-module: invalid SHA-256"),
            (("model", "artifacts", 1, "member"), "ase/calculators/eam.py", r"ase-emt-module\.member"),
        )
        original = self.sources.read_text(encoding="utf-8")
        for path, bad, reason in cases:
            with self.subTest(path=path):
                sources = json.loads(original)
                target = sources
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = bad
                self._write_sources(sources)
                with self.assertRaisesRegex(ValidationError, reason):
                    validate_package(self.package)

    def test_rehashed_adiabatic_uncertainty_cannot_be_relabelled(self):
        bad_basis = "0,34 % — 95%-й доверительный интервал K^T при 0 K"
        facts = self._read(self.facts)
        facts["observable"]["source_uncertainty"]["basis"] = bad_basis
        self._write(self.facts, facts)
        sources = self._read(self.sources)
        sources["observables"][0]["source_uncertainty"]["basis"] = bad_basis
        sources["sources"][0]["artifact"].update(self._pin(self.facts))
        self._write_sources(sources)
        with self.assertRaisesRegex(ValidationError, r"source uncertainty\.basis"):
            validate_package(self.package)

    def test_missing_or_tampered_narrative_draft_fails(self):
        method = self.package / "PROTOCOL.md"
        source_notes = self.package / "SOURCES.md"
        notes_raw = source_notes.read_bytes()
        source_notes.write_bytes(notes_raw + b"\n")
        with self.assertRaisesRegex(ValidationError, r"SOURCES\.md: SHA-256"):
            validate_package(self.package)
        source_notes.write_bytes(notes_raw)
        method.unlink()
        with self.assertRaisesRegex(ValidationError, r"PROTOCOL\.md: missing or unsafe file"):
            validate_package(self.package)

    def test_future_budget_cannot_turn_into_authority(self):
        cases = (
            ("status", "FROZEN", r"protocol\.status"),
            ("scientific_runs_allowed", True, r"protocol\.scientific_runs_allowed"),
            ("scientific_runs_allowed", 0, r"protocol\.scientific_runs_allowed"),
            ("physics_runs", False, r"protocol\.physics_runs"),
            ("scientific_outcome", "SUPPORTED", r"protocol\.scientific_outcome"),
            ("launch_authorized", True, "unexpected fields"),
        )
        original = self.protocol.read_text(encoding="utf-8")
        for key, bad, reason in cases:
            with self.subTest(key=key, bad=bad):
                protocol = json.loads(original)
                protocol[key] = bad
                self._write(self.protocol, protocol)
                with self.assertRaisesRegex(ValidationError, reason):
                    validate_package(self.package)

    def test_volume_grid_budget_and_conditions_cannot_be_silently_changed(self):
        cases = (
            ("scenario", "pbc", [True, True, False], r"protocol\.scenario"),
            ("numerics", "finite_difference_volume_fraction_steps", [0.005], "finite_difference_volume_fraction_steps"),
            ("observable", "engineering_tolerance_relative", 0.20, "engineering_tolerance_relative"),
            ("proposed_future_budget", "max_static_evaluations", 40, "proposed_future_budget"),
        )
        original = self.protocol.read_text(encoding="utf-8")
        for section, key, bad, reason in cases:
            with self.subTest(key=key):
                protocol = json.loads(original)
                protocol[section][key] = bad
                self._write(self.protocol, protocol)
                with self.assertRaisesRegex(ValidationError, reason):
                    validate_package(self.package)

    def test_path_escape_and_symlink_rejected(self):
        protocol = self._read(self.protocol)
        protocol["source_manifest"]["local_path"] = "../sources.json"
        self._write(self.protocol, protocol)
        with self.assertRaisesRegex(ValidationError, "local_path"):
            validate_package(self.package)

        shutil.copyfile(DEFAULT_PACKAGE / "protocol.json", self.protocol)
        target = self.package.parent / "facts.json"
        self.facts.rename(target)
        self.facts.symlink_to(target)
        with self.assertRaisesRegex(ValidationError, "missing or unsafe file"):
            validate_package(self.package)

    def test_duplicate_or_nonfinite_json_fails_cli(self):
        for raw, reason in (('{"scientific_runs_allowed":true,"scientific_runs_allowed":false}', "duplicate JSON key"),
                            ('{"value":NaN}', "non-finite JSON constant")):
            with self.subTest(raw=raw):
                self.protocol.write_text(raw, encoding="utf-8")
                err, out = io.StringIO(), io.StringIO()
                with redirect_stderr(err), redirect_stdout(out):
                    self.assertEqual(main(["--package", str(self.package)]), 1)
                self.assertIn(reason, err.getvalue())
                self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
