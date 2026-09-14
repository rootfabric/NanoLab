"""Release contract tests (WO-NL5-001-A-R1; extended by NL5-001-B repair R1).

Covers: example package passes the linter; schema-level rejections;
semantic rules S1-S5; family invariants I1/I2; manifest create/verify
round-trip, tamper detection, deterministic creation, duplicate-path and
path-semantics hardening; frozen reproduction rule conformance between the
normative executor and the package-shipped helper; fail-closed schema
executor; stdlib-only guard (hosted CI has no third-party packages).
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release import card_lint, mini_schema, reproduction  # noqa: E402

EXAMPLE_PKG = ROOT / "examples" / "release" / "nanolab-components-v0.1"
RELEASE_PKG = ROOT / "releases" / "nanolab-components-v0.1"
RELEASE_PKG_MANIFEST = RELEASE_PKG / "RELEASE_MANIFEST.json"
RELEASE_PKG_MANIFEST_EXAMPLE = EXAMPLE_PKG / "RELEASE_MANIFEST.json"
CARD_0B = EXAMPLE_PKG / "families" / "dna_hinge" / "cards" / "0b.card.json"
CARD_74B = EXAMPLE_PKG / "families" / "dna_hinge" / "cards" / "74b.card.json"
FROZEN_STAMP = "2026-09-13T15:27:54Z"  # example-package release metadata stamp


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ReleaseContractTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = card_lint._load_schema(card_lint.CARD_SCHEMA, "component card")


class TestExamplePackage(ReleaseContractTestBase):
    def test_example_package_passes(self) -> None:
        report = card_lint.run_package(EXAMPLE_PKG)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(
            report["variant_status"].get("0b"), "MEASURED", "0b must be measured in the example"
        )
        self.assertIn("NOT_MEASURED", report["variant_status"].get("74b", ""))

    def test_example_manifest_self_consistent(self) -> None:
        report = card_lint.manifest_verify(EXAMPLE_PKG, card_lint.MANIFEST_SCHEMA)
        self.assertTrue(report["ok"], report["errors"])

    def test_reproduce_self_test(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(EXAMPLE_PKG / "reproduction" / "reproduce.py"), "self-test"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        report = json.loads(proc.stdout)
        self.assertTrue(report["ok"], report)

    def test_cli_card_exit_zero(self) -> None:
        env = dict(os.environ, PYTHONPATH=str(ROOT / "scripts"))
        proc = subprocess.run(
            [sys.executable, "-m", "release.card_lint", "card", str(CARD_0B)],
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class TestCardSchema(ReleaseContractTestBase):
    def test_valid_examples_pass(self) -> None:
        for path in (CARD_0B, CARD_74B):
            errors = card_lint.validate_card(load(path), self.schema, origin=path.name)
            self.assertEqual(errors, [])

    def test_missing_required_rejected(self) -> None:
        card = load(CARD_0B)
        del card["rights"]
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("missing required property 'rights'" in e for e in errors), errors)

    def test_additional_property_rejected(self) -> None:
        card = load(CARD_0B)
        card["claim_ceiling_tbd"] = True
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("additional property" in e for e in errors), errors)

    def test_bad_digest_rejected(self) -> None:
        card = load(CARD_0B)
        card["source_provenance"]["digest_gates"]["MD_Hinges/0b.conf"]["sha256"] = "not-a-digest"
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("sha256" in e and "pattern" in e for e in errors), errors)

    def test_bad_engine_commit_rejected(self) -> None:
        card = load(CARD_0B)
        card["protocol_pins"]["engine_commit"] = "00dc7fb9"
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("engine_commit" in e for e in errors), errors)

    def test_unknown_claim_ceiling_rejected(self) -> None:
        card = load(CARD_0B)
        card["claim_ceiling"] = "C9_LOOKS_GREAT"
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("claim_ceiling" in e and "enum" in e for e in errors), errors)


class TestCardSemantics(ReleaseContractTestBase):
    def test_s1_measured_requires_observables_and_expected(self) -> None:
        card = load(CARD_0B)
        card["measured_observables"] = {}
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("(S1)" in e for e in errors), errors)

        card = load(CARD_0B)
        card["reproduction"]["expected"] = {}
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("(S1)" in e for e in errors), errors)

    def test_s1_measured_observable_requires_source(self) -> None:
        card = load(CARD_0B)
        card["measured_observables"]["hinge_angle_confirmatory_200k"]["source"] = ""
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        # The empty source is already a schema-level pattern violation; either
        # way a card without a source path must not pass.
        self.assertTrue(any("source" in e for e in errors), errors)

    def test_s2_not_measured_requires_known_gaps(self) -> None:
        card = load(CARD_74B)
        card["known_gaps"] = []
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("(S2)" in e for e in errors), errors)

    def test_s3_reference_only_requires_pins_and_no_cache(self) -> None:
        card = load(CARD_0B)
        del card["rights"]["pinned_commit"]
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("(S3)" in e and "pinned_commit" in e for e in errors), errors)

        card = load(CARD_0B)
        card["rights"]["durable_cache"] = "ALLOWED"
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("S3" in e and "FORBIDDEN" in e for e in errors), errors)

    def test_s4_c1_ceiling_requires_measurement(self) -> None:
        card = load(CARD_74B)
        card["claim_ceiling"] = "C1_COMPUTATIONAL_REPRODUCTION"
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("(S4)" in e for e in errors), errors)

    def test_s5_sha256_requires_status_together(self) -> None:
        card = load(CARD_0B)
        del card["source_provenance"]["digest_gates"]["MD_Hinges/0b.conf"]["sha256_status"]
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("(S5)" in e for e in errors), errors)

        card = load(CARD_74B)
        card["source_provenance"]["digest_gates"]["MD_Hinges/74b.conf"] = {
            "size_bytes": 2403188,
            "blob_sha1": "70ea81cd22f382162d69468895f87dac6675dd02",
            "sha256_status": "COMPUTED_NOT_VERIFIED",
        }
        errors = card_lint.validate_card(card, self.schema, origin="mutated")
        self.assertTrue(any("(S5)" in e for e in errors), errors)


class TestRightsAndPackage(ReleaseContractTestBase):
    def test_rights_example_passes_with_draft_warning(self) -> None:
        report = card_lint.run_rights(EXAMPLE_PKG / "RIGHTS.json", card_lint.RIGHTS_SCHEMA)
        self.assertTrue(report["ok"], report["errors"])
        self.assertTrue(any("D2" in w for w in report["warnings"]), report["warnings"])

    def test_rights_reference_only_item_requires_pins(self) -> None:
        schema = card_lint._load_schema(card_lint.RIGHTS_SCHEMA, "rights")
        rights = load(EXAMPLE_PKG / "RIGHTS.json")
        for item in rights["items"]:
            if item["rights_mode"] == "REFERENCE_ONLY":
                del item["pinned_commit"]
        errors, _ = card_lint.validate_rights(rights, schema, origin="mutated")
        self.assertTrue(any("REFERENCE_ONLY item requires" in e for e in errors), errors)

    def test_rights_bad_path_rejected(self) -> None:
        schema = card_lint._load_schema(card_lint.RIGHTS_SCHEMA, "rights")
        rights = load(EXAMPLE_PKG / "RIGHTS.json")
        rights["items"][0]["path"] = "../escape/**"
        errors, _ = card_lint.validate_rights(rights, schema, origin="mutated")
        self.assertTrue(any("'..'" in e for e in errors), errors)

    def test_family_invariant_i1_missing_variant_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            shutil.copytree(EXAMPLE_PKG, pkg)
            (pkg / "families" / "dna_hinge" / "family.json").write_text(
                json.dumps(
                    {**load(pkg / "families" / "dna_hinge" / "family.json"), "variants": ["0b", "74b", "99b"]},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            report = card_lint.run_package(pkg)
            self.assertFalse(report["ok"])
            self.assertTrue(any("(I1)" in e for e in report["errors"]), report["errors"])

    def test_family_invariant_i2_undeclared_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            shutil.copytree(EXAMPLE_PKG, pkg)
            undeclared = load(CARD_0B)
            undeclared["variant"] = "11b"
            undeclared["component_id"] = "dna_hinge/11b"
            (pkg / "families" / "dna_hinge" / "cards" / "11b.card.json").write_text(
                json.dumps(undeclared, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            report = card_lint.run_package(pkg)
            self.assertFalse(report["ok"])
            self.assertTrue(any("(I2)" in e for e in report["errors"]), report["errors"])

    def test_manifest_tamper_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            shutil.copytree(EXAMPLE_PKG, pkg)
            target = pkg / "VERSION"
            target.write_text(target.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            report = card_lint.manifest_verify(pkg, card_lint.MANIFEST_SCHEMA)
            self.assertFalse(report["ok"])
            self.assertTrue(any("mismatch" in e for e in report["errors"]), report["errors"])

    def test_manifest_create_roundtrip_excludes_itself(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            shutil.copytree(EXAMPLE_PKG, pkg)
            (pkg / card_lint.MANIFEST_NAME).unlink()
            manifest = card_lint.manifest_create(pkg, generated_at_utc=FROZEN_STAMP)
            self.assertNotIn(card_lint.MANIFEST_NAME, [entry["path"] for entry in manifest["files"]])
            (pkg / card_lint.MANIFEST_NAME).write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            report = card_lint.manifest_verify(pkg, card_lint.MANIFEST_SCHEMA)
            self.assertTrue(report["ok"], report["errors"])


class TestManifestDeterminism(unittest.TestCase):
    """Repair R1 (F-B2): the manifest is a deterministic pure function of the
    payload plus explicitly passed frozen release metadata — never wall-clock."""

    def test_create_requires_explicit_frozen_stamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "pkg"
            shutil.copytree(EXAMPLE_PKG, pkg)
            with self.assertRaises(card_lint.LintFailure):
                card_lint.manifest_create(pkg, generated_at_utc=None)  # type: ignore[arg-type]
            with self.assertRaises(card_lint.LintFailure):
                card_lint.manifest_create(pkg, generated_at_utc="2026-09-13 15:27:54")

    def test_same_inputs_produce_identical_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg_a = Path(tmp) / "a"
            pkg_b = Path(tmp) / "b"
            shutil.copytree(EXAMPLE_PKG, pkg_a)
            shutil.copytree(EXAMPLE_PKG, pkg_b)
            manifest_a = card_lint.manifest_create(pkg_a, generated_at_utc=FROZEN_STAMP, subject={"repository": "r", "commit": "c"})
            manifest_b = card_lint.manifest_create(pkg_b, generated_at_utc=FROZEN_STAMP, subject={"repository": "r", "commit": "c"})
            self.assertEqual(
                json.dumps(manifest_a, sort_keys=True),
                json.dumps(manifest_b, sort_keys=True),
                "manifest regeneration must be byte-identical",
            )

    def test_release_manifest_is_frozen_release_metadata(self) -> None:
        manifest = load(RELEASE_PKG_MANIFEST)
        self.assertEqual(
            manifest["generated_at_utc"],
            "2026-09-13T15:32:04Z",
            "release manifest stamp must stay the frozen assembly stamp",
        )


class TestManifestHardening(unittest.TestCase):
    """Repair R1 (F-B6): duplicate paths and bad path semantics must be
    rejected fail-closed, before any dictionary conversion hides them."""

    @staticmethod
    def _pkg_with_manifest(manifest: dict) -> Path:
        pkg = Path(tempfile.mkdtemp()) / "pkg"
        shutil.copytree(EXAMPLE_PKG, pkg)
        (pkg / card_lint.MANIFEST_NAME).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return pkg

    def test_duplicate_path_identical_metadata_rejected(self) -> None:
        manifest = load(RELEASE_PKG_MANIFEST_EXAMPLE)
        entries = manifest["files"]
        manifest["files"] = entries + [copy.deepcopy(entries[0])]
        report = card_lint.manifest_verify(self._pkg_with_manifest(manifest), card_lint.MANIFEST_SCHEMA)
        self.assertFalse(report["ok"])
        self.assertTrue(any("duplicate manifest path" in e for e in report["errors"]), report["errors"])

    def test_duplicate_path_conflicting_metadata_rejected(self) -> None:
        manifest = load(RELEASE_PKG_MANIFEST_EXAMPLE)
        conflicting = copy.deepcopy(manifest["files"][0])
        conflicting["sha256"] = "0" * 64
        conflicting["size_bytes"] = conflicting["size_bytes"] + 1
        manifest["files"] = manifest["files"] + [conflicting]
        report = card_lint.manifest_verify(self._pkg_with_manifest(manifest), card_lint.MANIFEST_SCHEMA)
        self.assertFalse(report["ok"])
        self.assertTrue(any("duplicate manifest path" in e for e in report["errors"]), report["errors"])

    def test_manifest_entry_bad_paths_rejected(self) -> None:
        for bad in ("/etc/passwd", "families\\74b.card.json", "../escape.json"):
            with self.subTest(path=bad):
                manifest = load(RELEASE_PKG_MANIFEST_EXAMPLE)
                manifest["files"][0]["path"] = bad
                report = card_lint.manifest_verify(self._pkg_with_manifest(manifest), card_lint.MANIFEST_SCHEMA)
                self.assertFalse(report["ok"])
                self.assertTrue(
                    any(("relative" in e) or ("POSIX" in e) or ("'..'" in e) for e in report["errors"]),
                    report["errors"],
                )


class TestReproductionRuleConformance(unittest.TestCase):
    """Repair R1 (F-B3): the package-shipped evaluate() must agree with the
    normative release.reproduction executor on identical inputs."""

    @staticmethod
    def _write(tmp: str, name: str, payload: dict) -> str:
        path = Path(tmp) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    @staticmethod
    def _candidate(medians: list, gates: list | None = None) -> dict:
        return {
            "rule": reproduction.RULE_ID,
            "card": "dna_hinge/0b",
            "replicas": [
                {
                    "replica_id": f"c{index}",
                    "median_deg": median,
                    "frames_valid": 37,
                    "frames_total": 37,
                    "gates_passed": True if gates is None else gates[index],
                }
                for index, median in enumerate(medians)
            ],
        }

    def test_shipped_helper_matches_normative_executor(self) -> None:
        card_payload = load(CARD_0B)
        cases = [
            (self._candidate([66.5, 66.9, 66.7]), "REPRODUCTION_MATCH"),
            (self._candidate([67.5, 67.6, 67.7]), "REPRODUCTION_MISMATCH"),
            (self._candidate([66.0, 66.1, 66.2], [True, True, False]), "INCONCLUSIVE"),
            (self._candidate([66.0, 66.1, 66.2], [False, False, False]), "TECHNICAL_FAILURE"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            card_path = self._write(tmp, "card.json", card_payload)
            for candidate_payload, expected in cases:
                with self.subTest(verdict=expected):
                    candidate_path = self._write(tmp, "candidate.json", candidate_payload)
                    proc = subprocess.run(
                        [
                            sys.executable,
                            str(EXAMPLE_PKG / "reproduction" / "reproduce.py"),
                            "evaluate",
                            card_path,
                            candidate_path,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    shipped = json.loads(proc.stdout)
                    normative = reproduction.evaluate(card_payload, candidate_payload)
                    self.assertEqual(shipped["verdict"], expected, proc.stdout)
                    self.assertEqual(shipped["verdict"], normative["verdict"])
                    self.assertEqual(
                        shipped["candidate_statistic"].get("median_of_replica_medians_deg"),
                        normative["candidate_statistic"].get("median_of_replica_medians_deg"),
                    )
                    self.assertTrue(shipped["ci95_is_not_acceptance_band"])

    def test_package_ships_frozen_rule_copy(self) -> None:
        rule_doc = ROOT / "docs" / "research" / "REPRODUCTION_RULE_R1.md"
        shipped = EXAMPLE_PKG / "reproduction" / "REPRODUCTION_RULE_R1.md"
        self.assertTrue(shipped.is_file(), "example package must ship the frozen rule")
        self.assertEqual(shipped.read_bytes(), rule_doc.read_bytes())
        released = ROOT / "releases" / "nanolab-components-v0.1" / "reproduction" / "REPRODUCTION_RULE_R1.md"
        self.assertEqual(released.read_bytes(), rule_doc.read_bytes())


class TestSchemaExecutorFailClosed(unittest.TestCase):
    def test_unsupported_keyword_rejected(self) -> None:
        errors = mini_schema.lint_schema({"type": "object", "xor": {"a": 1}})
        self.assertTrue(any("unsupported schema keyword" in e and "'xor'" in e for e in errors), errors)

    def test_one_of_rejected(self) -> None:
        errors = mini_schema.lint_schema({"oneOf": [{"type": "string"}]})
        self.assertTrue(errors, "oneOf must be rejected by the fail-closed executor")

    def test_validate_raises_schema_error(self) -> None:
        with self.assertRaises(mini_schema.SchemaError):
            mini_schema.validate({"a": 1}, {"contains": {"const": 1}})

    def test_repo_schemas_are_executable(self) -> None:
        for schema_path in (card_lint.CARD_SCHEMA, card_lint.RIGHTS_SCHEMA, card_lint.MANIFEST_SCHEMA):
            self.assertEqual(mini_schema.lint_schema(load(schema_path)), [], str(schema_path))

    def test_bool_int_confusion_guarded(self) -> None:
        errors = mini_schema.validate(True, {"const": 1})
        self.assertTrue(errors, "True must not equal integer 1")
        errors = mini_schema.validate(1, {"type": "boolean"})
        self.assertTrue(errors, "1 must not be a boolean")


class TestStdlibOnly(unittest.TestCase):
    def test_release_tooling_has_no_third_party_imports(self) -> None:
        forbidden = ("jsonschema", "yaml", "pydantic")
        for source in (ROOT / "scripts" / "release").glob("*.py"):
            text = source.read_text(encoding="utf-8")
            for module in forbidden:
                self.assertNotIn(f"import {module}", text, f"{source.name} must stay stdlib-only")
                self.assertNotIn(f"from {module}", text, f"{source.name} must stay stdlib-only")


if __name__ == "__main__":
    unittest.main()
