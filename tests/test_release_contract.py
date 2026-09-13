"""Release contract tests (WO-NL5-001-A-R1).

Covers: example package passes the linter; schema-level rejections;
semantic rules S1-S4; family invariants I1/I2; manifest create/verify
round-trip and tamper detection; fail-closed schema executor;
stdlib-only guard (hosted CI has no third-party packages).
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

from release import card_lint, mini_schema  # noqa: E402

EXAMPLE_PKG = ROOT / "examples" / "release" / "nanolab-components-v0.1"
CARD_0B = EXAMPLE_PKG / "families" / "dna_hinge" / "cards" / "0b.card.json"
CARD_74B = EXAMPLE_PKG / "families" / "dna_hinge" / "cards" / "74b.card.json"


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
            manifest = card_lint.manifest_create(pkg)
            self.assertNotIn(card_lint.MANIFEST_NAME, [entry["path"] for entry in manifest["files"]])
            (pkg / card_lint.MANIFEST_NAME).write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            report = card_lint.manifest_verify(pkg, card_lint.MANIFEST_SCHEMA)
            self.assertTrue(report["ok"], report["errors"])


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
