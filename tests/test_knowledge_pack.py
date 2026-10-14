"""KnowledgePack v1 contract tests (PREP-S17, WO-PREP-S17-R1).

Positive: the committed S17 pack instance validates and its pinned inputs
re-verify byte-for-byte. Negative controls: corruption of every critical
surface (digests, sizes, claim ceiling, rights gating, manifest structure)
must fail closed.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from knowledge_pack.contract import (  # noqa: E402
    FORBIDDEN_CLAIM_LEVELS,
    KnowledgePackError,
    load_pack,
    sha256_file,
    validate_pack,
    verify_manifest,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
S17_PACK_PATH = REPO_ROOT / "docs" / "research" / "S17_KNOWLEDGEPACK.json"


def _minimal_pack() -> dict:
    return {
        "schema_version": 1,
        "kind": "knowledge_pack",
        "pack_id": "S17-TEST",
        "source_id": "S17",
        "source_version": "r1-test",
        "doi": "10.5281/zenodo.8248808",
        "license": "UNKNOWN",
        "rights": {
            "license": "UNKNOWN",
            "redistribution": "UNKNOWN",
            "access_mode": "REFERENCE_ONLY",
            "notes": "test fixture",
        },
        "input_file_manifest": [
            {
                "path": "inputs/example.top",
                "size_bytes": 11,
                "sha256": "0" * 64,
                "role": "DESIGN_TOPOLOGY",
                "availability": "REMOTE_ONLY",
                "sha256_provenance": "UPSTREAM_METADATA",
                "source_url": "https://example.org/example.top",
            }
        ],
        "scientific_model": "DNA_COARSE_GRAINED",
        "simulation_engine": "oxDNA",
        "topology_format": "UNKNOWN",
        "configuration_format": "UNKNOWN",
        "observables": [
            {
                "name": "test_observable",
                "definition": "fixture",
                "status": "UNVERIFIED",
            }
        ],
        "protocol_references": ["test-proto-r1"],
        "missing_inputs": [],
        "known_limitations": ["fixture only"],
        "claim_level": "BIBLIOGRAPHIC",
        "provenance": {
            "audit_work_order": "WO-PREP-S17-R1",
            "audit_execution_id": "EX-PREP-S17-R1",
            "audit_date_utc": "2026-10-14T00:00:00.000Z",
            "audit_method": "test fixture",
            "base_repo_sha": "0" * 40,
        },
    }


class TestCommittedPack(unittest.TestCase):
    """The committed S17 KnowledgePack instance must conform and re-verify."""

    def setUp(self) -> None:
        if not S17_PACK_PATH.is_file():
            self.skipTest("S17_KNOWLEDGEPACK.json not present on this branch")
        self.pack = json.loads(S17_PACK_PATH.read_text(encoding="utf-8"))

    def test_committed_s17_pack_validates(self) -> None:
        self.assertEqual(validate_pack(self.pack), [])

    def test_load_pack_accepts_committed_pack(self) -> None:
        pack = load_pack(S17_PACK_PATH)
        self.assertEqual(pack["source_id"], "S17")

    def test_pinned_inputs_reverify_on_disk(self) -> None:
        errors = verify_manifest(REPO_ROOT, self.pack)
        self.assertEqual(errors, [])

    def test_validation_is_deterministic(self) -> None:
        self.assertEqual(validate_pack(self.pack), validate_pack(copy.deepcopy(self.pack)))

    def test_no_inflated_claim_level(self) -> None:
        self.assertNotIn(self.pack["claim_level"], FORBIDDEN_CLAIM_LEVELS)


class TestPositiveSynthetic(unittest.TestCase):
    def test_minimal_pack_validates(self) -> None:
        self.assertEqual(validate_pack(_minimal_pack()), [])

    def test_verify_manifest_accepts_matching_file(self) -> None:
        pack = _minimal_pack()
        pack["input_file_manifest"][0].update(
            availability="ON_DISK_VERIFIED", sha256_provenance="CONTENT_VERIFIED"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inputs" / "example.top"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"hello_world")  # 11 bytes
            pack["input_file_manifest"][0]["sha256"] = sha256_file(path)
            self.assertEqual(verify_manifest(Path(tmp), pack), [])

    def test_unknown_is_valid_scalar(self) -> None:
        pack = _minimal_pack()
        pack["license"] = "UNKNOWN"
        self.assertEqual(validate_pack(pack), [])


class TestNegativeControls(unittest.TestCase):
    """Every corruption below must produce at least one specific error."""

    def _assert_error_contains(self, pack: dict, fragment: str) -> None:
        errors = validate_pack(pack)
        self.assertTrue(
            any(fragment in e for e in errors),
            f"expected error containing {fragment!r}, got {errors}",
        )

    def test_corrupted_sha256_rejected(self) -> None:
        pack = _minimal_pack()
        pack["input_file_manifest"][0]["sha256"] = "f" * 63
        self._assert_error_contains(pack, "sha256 must be 64 lowercase hex")

    def test_manifest_digest_mismatch_rejected_by_verify(self) -> None:
        pack = _minimal_pack()
        pack["input_file_manifest"][0].update(
            availability="ON_DISK_VERIFIED", sha256_provenance="CONTENT_VERIFIED"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inputs" / "example.top"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"hello_world")
            pack["input_file_manifest"][0]["sha256"] = sha256_file(path)
            self.assertEqual(verify_manifest(Path(tmp), pack), [])
            path.write_bytes(b"hello_wor1d")  # corrupt one byte
            errors = verify_manifest(Path(tmp), pack)
            self.assertTrue(any("sha256 mismatch" in e for e in errors))

    def test_size_mismatch_rejected_by_verify(self) -> None:
        pack = _minimal_pack()
        pack["input_file_manifest"][0].update(
            availability="ON_DISK_VERIFIED",
            sha256_provenance="CONTENT_VERIFIED",
            size_bytes=999,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inputs" / "example.top"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"hello_world")
            pack["input_file_manifest"][0]["sha256"] = sha256_file(path)
            errors = verify_manifest(Path(tmp), pack)
            self.assertTrue(any("size mismatch" in e for e in errors))

    def test_claim_inflation_rejected(self) -> None:
        for level in sorted(FORBIDDEN_CLAIM_LEVELS):
            pack = _minimal_pack()
            pack["claim_level"] = level
            self._assert_error_contains(pack, "exceeds the v1 ceiling")

    def test_unknown_claim_level_rejected(self) -> None:
        pack = _minimal_pack()
        pack["claim_level"] = "NOT_A_LEVEL"
        self._assert_error_contains(pack, "claim_level must be one of")

    def test_missing_required_field_rejected(self) -> None:
        for key in (
            "source_id", "source_version", "doi", "rights", "input_file_manifest",
            "scientific_model", "simulation_engine", "topology_format",
            "configuration_format", "observables", "protocol_references",
            "missing_inputs", "known_limitations", "claim_level", "provenance",
        ):
            pack = _minimal_pack()
            del pack[key]
            self._assert_error_contains(pack, f"missing required field {key}")

    def test_unknown_top_level_field_rejected(self) -> None:
        pack = _minimal_pack()
        pack["extra_field"] = "nope"
        self._assert_error_contains(pack, "unknown top-level fields")

    def test_null_and_empty_forbidden_in_favor_of_unknown(self) -> None:
        pack = _minimal_pack()
        pack["license"] = None
        self._assert_error_contains(pack, "null is forbidden")
        pack["license"] = ""
        self._assert_error_contains(pack, "empty string is forbidden")

    def test_vendoring_blocked_without_allowed_redistribution(self) -> None:
        pack = _minimal_pack()
        pack["input_file_manifest"][0]["vendored"] = True
        self._assert_error_contains(pack, "vendoring requires rights.redistribution ALLOWED")

    def test_vendoring_allowed_only_with_permission(self) -> None:
        pack = _minimal_pack()
        pack["rights"]["redistribution"] = "ALLOWED"
        entry = pack["input_file_manifest"][0]
        entry["vendored"] = True
        entry["source_url"] = "https://example.org/example.top"
        self.assertEqual(validate_pack(pack), [])

    def test_forbidden_redistribution_blocks_vendored_mode(self) -> None:
        pack = _minimal_pack()
        pack["rights"]["redistribution"] = "FORBIDDEN"
        pack["rights"]["access_mode"] = "VENDORED"
        self._assert_error_contains(pack, "incompatible with redistribution FORBIDDEN")

    def test_on_disk_requires_content_verified_provenance(self) -> None:
        pack = _minimal_pack()
        pack["input_file_manifest"][0].update(
            availability="ON_DISK_VERIFIED", sha256_provenance="NOT_VERIFIED"
        )
        self._assert_error_contains(pack, "CONTENT_VERIFIED")

    def test_remote_entry_requires_source_url(self) -> None:
        pack = _minimal_pack()
        del pack["input_file_manifest"][0]["source_url"]
        self._assert_error_contains(pack, "must record source_url")

    def test_declared_format_without_manifest_entry_rejected(self) -> None:
        pack = _minimal_pack()
        pack["topology_format"] = "oxDNA_top"
        pack["input_file_manifest"][0]["role"] = "ANALYSIS_CODE"
        self._assert_error_contains(pack, "no DESIGN_TOPOLOGY manifest entry")

    def test_empty_observables_require_explanation(self) -> None:
        pack = _minimal_pack()
        pack["observables"] = []
        self._assert_error_contains(pack, "requires an explicit missing_inputs entry")
        pack["missing_inputs"] = ["observables not yet audited"]
        self.assertEqual(validate_pack(pack), [])

    def test_duplicate_manifest_path_rejected(self) -> None:
        pack = _minimal_pack()
        first = pack["input_file_manifest"][0]
        second = copy.deepcopy(first)
        second["path"] = first["path"]
        pack["input_file_manifest"].append(second)
        self._assert_error_contains(pack, "duplicated")

    def test_bad_provenance_sha_rejected(self) -> None:
        pack = _minimal_pack()
        pack["provenance"]["base_repo_sha"] = "abc"
        self._assert_error_contains(pack, "40-hex commit SHA or UNKNOWN")

    def test_non_json_load_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json")
            with self.assertRaises(KnowledgePackError):
                load_pack(bad)

    def test_invalid_pack_load_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({"schema_version": 2}))
            with self.assertRaises(KnowledgePackError):
                load_pack(bad)


if __name__ == "__main__":
    unittest.main()
