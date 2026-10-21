"""Offline tests for NanoLab's first published two-part DNA source-readiness gate.

The original 2024 and 2025 paper references have NO observed data-file bytes
in this Work Order. Synthetic fixtures test code mechanics only; they do not
certify either publication, molecular contact, or physical function.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from knowledge_pack import alt_pair_source_gate as gate

PACK_FILE = ROOT / "docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json"


def as_input(path: Path, root: Path) -> dict:
    data = path.read_bytes()
    return {
        "status": "CONTENT_VERIFIED",
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "rights": "ALLOWED",
        "source_url": "https://example.org/fixture/" + path.name,
    }


def topology() -> str:
    return "4 1\n1 A -1 1\n1 C 0 2\n1 G 1 3\n1 T 2 -1\n"


def config() -> str:
    lines = ["t = 0", "b = 30 30 30", "E = 0 0 0"]
    for i in range(4):
        vals = [float(i + 1), 5.0, 5.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        lines.append(" ".join(str(x) for x in vals))
    return "\n".join(lines) + "\n"


def anchor_map() -> dict:
    return {
        "kind": "two_part_dna_interface_map",
        "pairs": [{
            "part_a": "NARCISSUS",
            "part_b": "ECHO",
            "a_index": 1, "b_index": 1,
            "a_end": "3p", "b_end": "3p",
            "segment_a": "ACGTAC", "segment_b": "GTACGT",
            "kind": "NONCOVALENT_DNA_HYBRIDIZATION",
            "status": "SOURCE_CONFIRMED",
        }],
    }


class PublishedAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = gate.parse_json_no_duplicate_keys(PACK_FILE.read_text(encoding="utf-8"))

    def test_contract_identity_and_zero_science(self):
        self.assertEqual(self.pack["kind"], gate.KIND)
        self.assertEqual(self.pack["claim_ceiling"], "BIBLIOGRAPHIC")
        self.assertEqual(self.pack["scientific_runs"], 0)
        self.assertEqual(gate.validate_manifest(self.pack), [])

    def test_both_original_papers_are_distinct(self):
        self.assertEqual(
            {c["doi"] for c in self.pack["candidates"]},
            {"10.1038/s41565-024-01738-7", "10.1038/s41467-025-56846-2"},
        )
        self.assertEqual(self.pack["selected_candidate_id"], "S23_NARCISSUS_ECHO")

    def test_reported_files_are_not_fabricated_digest_pins(self):
        for candidate in self.pack["candidates"]:
            for source in candidate["reported_design_files"]:
                self.assertEqual(source["sha256"], "UNKNOWN")
                self.assertEqual(source["redistribution"], "UNKNOWN")
                self.assertIn(source["status"], gate.VALID_REPORTED)

    def test_no_fake_topology_or_follower_ready_claim(self):
        for candidate in self.pack["candidates"]:
            for part in candidate["parts"]:
                for role in ("topology", "configuration"):
                    self.assertEqual(part[role]["status"], "UNKNOWN")
                    self.assertEqual(part[role]["sha256"], "UNKNOWN")
            self.assertEqual(candidate["interface"]["anchor_map"]["status"], "UNKNOWN")
            result = gate.evaluate(self.pack, candidate["candidate_id"], ROOT)
            self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
            self.assertTrue(any("SOURCE_BYTES_NOT_OBSERVED" in x for x in result["reasons"]))

    def test_does_not_conflate_nemesis_with_s17_ne(self):
        s23 = self.pack["candidates"][0]
        self.assertIn("not the unrelated S17", s23["structure_description"])
        self.assertEqual([x["part_id"] for x in s23["parts"]], ["NARCISSUS", "ECHO"])

    def test_file_roles_are_reports_not_oxdna_inputs(self):
        reported = self.pack["candidates"][0]["reported_design_files"]
        self.assertTrue(any(x["format"] == "OXVIEW_JSON" for x in reported))
        self.assertFalse(any(x["name"].endswith(".top") for x in reported))
        self.assertFalse(any(x["name"].endswith(".dat") for x in reported))

    def test_claim_inflation_rejected(self):
        copy_pack = copy.deepcopy(self.pack)
        copy_pack["claim_ceiling"] = "ASSEMBLY_VALIDATED"
        self.assertTrue(any("BIBLIOGRAPHIC" in e for e in gate.validate_manifest(copy_pack)))

    def test_unobserved_files_cannot_gain_concrete_sha(self):
        copy_pack = copy.deepcopy(self.pack)
        copy_pack["candidates"][0]["reported_design_files"][0]["sha256"] = "a" * 64
        self.assertTrue(gate.validate_manifest(copy_pack))

    def test_duplicate_json_keys_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            gate.parse_json_no_duplicate_keys('{"kind":"A","kind":"B"}')

    def test_duplicate_parts_rejected(self):
        x = copy.deepcopy(self.pack)
        x["candidates"][0]["parts"][1]["part_id"] = "NARCISSUS"
        self.assertTrue(any("distinct" in m for m in gate.validate_manifest(x)))

    def test_missing_candidate_fail_closed(self):
        x = gate.evaluate(self.pack, "DOES_NOT_EXIST", ROOT)
        self.assertEqual(x["outcome"], "BLOCKED_SOURCE")
        self.assertIn("candidate not found", x["reasons"])


class SyntheticGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pack = gate.parse_json_no_duplicate_keys(PACK_FILE.read_text(encoding="utf-8"))
        candidate = self.pack["candidates"][0]
        candidate["candidate_id"] = "SYNTHETIC_TWO_PART"
        candidate["design_basis"] = "SYNTHETIC_FIXTURE"
        self.pack["selected_candidate_id"] = candidate["candidate_id"]
        self.pack["candidates"] = [candidate]
        for part in candidate["parts"]:
            pid = part["part_id"].lower()
            top = self.root / f"{pid}.top"
            conf = self.root / f"{pid}.dat"
            top.write_text(topology(), encoding="utf-8")
            conf.write_text(config(), encoding="utf-8")
            part["topology"] = as_input(top, self.root)
            part["configuration"] = as_input(conf, self.root)
        amap = self.root / "ports.json"
        amap.write_text(json.dumps(anchor_map(), sort_keys=True), encoding="utf-8")
        candidate["interface"]["anchor_map"] = as_input(amap, self.root)

    @property
    def candidate(self):
        return self.pack["candidates"][0]

    def _evaluate(self):
        return gate.evaluate(self.pack, self.candidate["candidate_id"], self.root)

    def test_positive_fixture_only_never_science_pass(self):
        self.assertEqual(gate.validate_manifest(self.pack), [])
        outcome = self._evaluate()
        self.assertEqual(outcome["outcome"], "TEST_FIXTURE_STATIC_INPUTS_OK", outcome)
        self.assertEqual(outcome["scientific_runs"], 0)
        self.assertEqual(outcome["part_structure_sizes"]["NARCISSUS"]["nucleotides"], 4)
        self.assertEqual(outcome["part_structure_sizes"]["ECHO"]["strands"], 1)

    def test_tampered_topology_digest_rejected(self):
        (self.root / "echo.top").write_text(topology() + " ", encoding="utf-8")
        result = self._evaluate()
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("SHA-256 mismatch" in x for x in result["reasons"]))

    def test_tampered_configuration_digest_rejected(self):
        (self.root / "echo.dat").write_text(config().replace("E = 0", "E = 1"), encoding="utf-8")
        result = self._evaluate()
        self.assertTrue(any("SHA-256 mismatch" in x for x in result["reasons"]))

    def test_source_undefined_rights_rejected(self):
        self.candidate["parts"][0]["topology"]["rights"] = "UNKNOWN"
        self.assertTrue(any("RIGHTS_NOT_CLEARED" in x for x in self._evaluate()["reasons"]))

    def test_source_restricted_rights_rejected(self):
        self.candidate["interface"]["anchor_map"]["rights"] = "RESTRICTED"
        self.assertTrue(any("RIGHTS_NOT_CLEARED" in x for x in self._evaluate()["reasons"]))

    def test_relative_parent_escape_rejected(self):
        self.candidate["parts"][0]["topology"]["path"] = "../bad.top"
        self.assertTrue(any("path traversal" in x for x in self._evaluate()["reasons"]))

    def test_absolute_path_rejected(self):
        self.candidate["parts"][0]["topology"]["path"] = str(self.root / "narcissus.top")
        self.assertTrue(any("path traversal" in x for x in self._evaluate()["reasons"]))

    def test_symlink_rejected(self):
        p = self.root / "alias.top"
        try:
            p.symlink_to(self.root / "narcissus.top")
        except (OSError, NotImplementedError):
            self.skipTest("symlink unsupported")
        self.candidate["parts"][0]["topology"]["path"] = "alias.top"
        self.assertTrue(any("symlink" in x for x in self._evaluate()["reasons"]))

    def test_missing_file_rejected(self):
        (self.root / "narcissus.top").unlink()
        self.assertTrue(any("missing" in x for x in self._evaluate()["reasons"]))

    def test_bad_declared_size_rejected(self):
        self.candidate["parts"][0]["topology"]["size_bytes"] += 1
        self.assertTrue(any("file size mismatch" in x for x in self._evaluate()["reasons"]))

    def test_size_cap_validation(self):
        self.candidate["parts"][0]["topology"]["size_bytes"] = gate.MAX_SOURCE_BYTES + 1
        self.assertTrue(any("resource cap" in x for x in gate.validate_manifest(self.pack)))

    def test_missing_anchor_map_rejected(self):
        self.candidate["interface"]["anchor_map"]["status"] = "UNKNOWN"
        self.candidate["interface"]["anchor_map"].update({
            "path": "UNKNOWN", "sha256": "UNKNOWN",
            "size_bytes": "UNKNOWN", "rights": "UNKNOWN", "source_url": "UNKNOWN"})
        self.assertTrue(any("SOURCE_BYTES_NOT_OBSERVED" in x for x in self._evaluate()["reasons"]))

    def test_bad_anchor_map_pair_fails(self):
        p = self.root / "ports.json"
        j = anchor_map()
        j["pairs"][0]["segment_b"] = "AAAAAA"
        p.write_text(json.dumps(j), encoding="utf-8")
        self.candidate["interface"]["anchor_map"] = as_input(p, self.root)
        self.assertTrue(any("not reverse complements" in x for x in self._evaluate()["reasons"]))

    def test_bad_anchor_index_fails(self):
        p = self.root / "ports.json"
        j = anchor_map()
        j["pairs"][0]["b_index"] = 4
        p.write_text(json.dumps(j), encoding="utf-8")
        self.candidate["interface"]["anchor_map"] = as_input(p, self.root)
        self.assertTrue(any("out-of-bounds" in x for x in self._evaluate()["reasons"]))

    def test_ambiguous_unknown_port_fails(self):
        p = self.root / "ports.json"
        j = anchor_map()
        j["pairs"][0]["status"] = "INFERRED_CANDIDATE"
        p.write_text(json.dumps(j), encoding="utf-8")
        self.candidate["interface"]["anchor_map"] = as_input(p, self.root)
        self.assertTrue(any("UNKNOWN or inferred" in x for x in self._evaluate()["reasons"]))

    def test_duplicate_pair_fails(self):
        p = self.root / "ports.json"
        j = anchor_map()
        j["pairs"].append(copy.deepcopy(j["pairs"][0]))
        p.write_text(json.dumps(j), encoding="utf-8")
        self.candidate["interface"]["anchor_map"] = as_input(p, self.root)
        self.assertTrue(any("duplicate anchor pair" in x for x in self._evaluate()["reasons"]))

    def test_modified_backbone_fails_strict_preflight(self):
        p = self.root / "narcissus.top"
        p.write_text(topology().replace("1 A -1 1", "1 A 3 1"), encoding="utf-8")
        self.candidate["parts"][0]["topology"] = as_input(p, self.root)
        result = self._evaluate()
        self.assertTrue(any("strict oxDNA structural preflight failed" in x for x in result["reasons"]))

    def test_particle_count_mismatch_fails(self):
        p = self.root / "echo.dat"
        lines = config().splitlines()
        p.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        self.candidate["parts"][1]["configuration"] = as_input(p, self.root)
        self.assertTrue(any("particle-count mismatch" in x for x in self._evaluate()["reasons"]))

    def test_non_sha256_digest_rejected(self):
        self.candidate["parts"][0]["topology"]["sha256"] = "1" * 32
        self.assertTrue(gate.validate_manifest(self.pack))

    def test_invalid_license_enum_rejected(self):
        self.candidate["parts"][0]["topology"]["rights"] = "CC_BY_INFERRED_FROM_PAPER"
        self.assertTrue(any("unknown rights" in x for x in gate.validate_manifest(self.pack)))

    def test_cli_produces_fail_closed_json_and_exit_code(self):
        fp = self.root / "pack.json"
        published = gate.parse_json_no_duplicate_keys(PACK_FILE.read_text(encoding="utf-8"))
        fp.write_text(json.dumps(published), encoding="utf-8")
        output = StringIO()
        with redirect_stdout(output):
            code = gate.main([str(fp), "--candidate", "S23_NARCISSUS_ECHO", "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["outcome"], "BLOCKED_SOURCE")

    def test_cli_bad_manifest_double_key_fails(self):
        fp = self.root / "bad.json"
        fp.write_text('{"kind":"A", "kind":"B"}', encoding="utf-8")
        output = StringIO()
        with redirect_stdout(output):
            code = gate.main([str(fp), "--candidate", "x"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["outcome"], "BLOCKED_INVALID_MANIFEST")


if __name__ == "__main__":
    unittest.main()
