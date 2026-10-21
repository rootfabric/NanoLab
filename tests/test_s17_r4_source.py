"""Offline validator for EX-PREP-S17-R4-SOURCE-R1 JSON deliverables.

No network access: validates structure and cross-references of
docs/research/S17_R4_PORT_CANDIDATES.json and
docs/research/S17_R4_FOLLOWER_PROVENANCE.json plus the gap-closure report.
"""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PORT_CANDIDATES = REPO_ROOT / "docs/research/S17_R4_PORT_CANDIDATES.json"
FOLLOWER_PROVENANCE = REPO_ROOT / "docs/research/S17_R4_FOLLOWER_PROVENANCE.json"
GAP_CLOSURE = REPO_ROOT / "docs/research/S17_R4_SOURCE_GAP_CLOSURE.md"

ALLOWED_HOP_STATUSES = {"SOURCE_CONFIRMED", "INFERRED_CANDIDATE", "UNKNOWN"}
ALLOWED_ENDS = {"top", "bottom"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_PAIRS = 10


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


class TestPortCandidates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_json(PORT_CANDIDATES)

    def test_valid_json_object(self):
        self.assertIsInstance(self.data, dict)
        self.assertEqual(self.data.get("schema_version"), 1)
        self.assertEqual(self.data.get("kind"), "s17_r4_port_candidates")

    def test_claim_ceiling_present(self):
        self.assertIn("claim_ceiling", self.data)
        self.assertIn("PINNED_IMPORT_VERIFIED", self.data["claim_ceiling"])

    def test_exactly_ten_pairs(self):
        pairs = self.data["pairs"]
        self.assertEqual(len(pairs), EXPECTED_PAIRS)
        self.assertEqual([p["pair_id"] for p in pairs], list(range(1, EXPECTED_PAIRS + 1)))

    def test_pair_fields_and_segments_reverse_complement(self):
        comp = {"A": "T", "T": "A", "G": "C", "C": "G"}
        for pair in self.data["pairs"]:
            for key in ("driver_odn", "follower_odn", "driver_segment", "follower_segment", "sequence_hop"):
                self.assertIn(key, pair, f"pair {pair.get('pair_id')} missing {key}")
            drv, fol = pair["driver_segment"], pair["follower_segment"]
            self.assertTrue(SHA256_RE.match is not None and re.fullmatch(r"[ACGT]{20}", drv), drv)
            self.assertTrue(re.fullmatch(r"[ACGT]{20}", fol), fol)
            rc = "".join(comp[base] for base in reversed(fol))
            self.assertEqual(drv, rc, f"pair {pair['pair_id']} segments are not reverse complements")
            self.assertEqual(pair["sequence_hop"]["status"], "SOURCE_CONFIRMED")
            self.assertIsInstance(pair["lna"], bool)

    def test_hop_statuses_within_vocabulary(self):
        for pair in self.data["pairs"]:
            for side in ("driver_hop", "follower_hop"):
                hop = pair[side]
                self.assertIn(hop["sequence_status"], ALLOWED_HOP_STATUSES)
                self.assertEqual(hop["sequence_status"], "SOURCE_CONFIRMED")
                self.assertIn(hop["index_anchor"]["status"], ALLOWED_HOP_STATUSES)
                assignment = hop["helix_arm_assignment"]
                self.assertEqual(assignment["status"], "INFERRED_CANDIDATE")
                self.assertIn(assignment["end"], ALLOWED_ENDS)
                self.assertTrue(assignment.get("note"))

    def test_index_anchors_are_unknown_without_author_design(self):
        # No author design files were recovered (G1 BLOCKED_SOURCE): every
        # nucleotide-index anchor must remain UNKNOWN, never guessed.
        for pair in self.data["pairs"]:
            for side in ("driver_hop", "follower_hop"):
                self.assertEqual(pair[side]["index_anchor"]["status"], "UNKNOWN")
                self.assertIn("reason", pair[side]["index_anchor"])

    def test_source_pins_are_64hex(self):
        pins = self.data["source_pins"]
        for pin_id in ("dataset_s1", "suppl_figure_s5", "si_engine_caDNAno_map", "nNE_top_pin"):
            self.assertIn(pin_id, pins)
            self.assertTrue(SHA256_RE.fullmatch(pins[pin_id]["sha256"]), pin_id)
        self.assertEqual(
            pins["dataset_s1"]["sha256"],
            "dc3cc6c53a9a116630db25a423c8439910d9e2d0ba159ef32424b546bcf3036c",
        )
        self.assertEqual(
            pins["suppl_figure_s5"]["sha256"],
            "66074e7d0c07139ecfb2d65f0526e3386fb91853d2218badbc27cd32f1a42c66",
        )

    def test_hypothesis_map_is_explicitly_marked(self):
        hyp = self.data["candidate_following_interface_map"]
        self.assertEqual(hyp["kind"], "HYPOTHESIS")
        self.assertIn("CANDIDATE_DESIGN", hyp["marked"])
        self.assertIn("HYPOTHESIS", hyp["marked"])


class TestFollowerProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_json(FOLLOWER_PROVENANCE)

    def test_valid_json_object(self):
        self.assertIsInstance(self.data, dict)
        self.assertEqual(self.data.get("schema_version"), 1)
        self.assertEqual(self.data.get("kind"), "s17_r4_follower_provenance")

    def test_g1_blocked_source_verdict(self):
        self.assertEqual(self.data["verdict"]["g1_status"], "BLOCKED_SOURCE")
        self.assertEqual(
            self.data["verdict"]["follower_topology_config_design_files"], "BLOCKED_SOURCE"
        )

    def test_blocked_source_receipt_structure(self):
        receipt = self.data["blocked_source_receipt"]
        self.assertEqual(receipt["kind"], "BLOCKED_SOURCE")
        self.assertEqual(receipt["gap"], "G1")
        self.assertTrue(receipt["searched_surfaces"])
        for surface in receipt["searched_surfaces"]:
            for key in ("surface", "queries", "found_absent"):
                self.assertIn(key, surface)
        self.assertTrue(receipt["resume_conditions"])

    def test_provenance_records_have_digests_or_explicit_null(self):
        records = self.data["provenance_records"]
        self.assertTrue(records)
        for record in records:
            for key in ("id", "role", "retrieved_at_utc", "license", "content_summary"):
                self.assertIn(key, record, f"{record.get('id')} missing {key}")
            self.assertTrue(
                "url" in record or "urls" in record, f"{record.get('id')} missing url(s)"
            )
            sha = record.get("sha256")
            if sha is not None:
                self.assertTrue(SHA256_RE.fullmatch(sha), f"{record['id']} sha256 not 64-hex: {sha}")
        ids = [r["id"] for r in records]
        self.assertEqual(len(ids), len(set(ids)), "duplicate provenance record ids")

    def test_dataset_s1_pin_recorded(self):
        pins = {
            r["sha256"]: r for r in self.data["provenance_records"] if r.get("sha256")
        }
        self.assertIn("dc3cc6c53a9a116630db25a423c8439910d9e2d0ba159ef32424b546bcf3036c", pins)

    def test_network_budget_within_limit(self):
        budget = self.data["network_budget"]
        self.assertEqual(budget["scientific_runs"], 0)
        self.assertEqual(budget["outbound_messages_to_authors"], 0)
        self.assertLessEqual(budget["used_mib_unique_downloads"], budget["budget_mib"])

    def test_test_vehicle_is_labeled_not_follower(self):
        vehicle = self.data["workflow_test_vehicle_alternative"]
        self.assertEqual(vehicle["kind"], "NOT_THE_S17_FOLLOWER")
        self.assertIn("256", vehicle["available_files"][0])


class TestGapClosureDoc(unittest.TestCase):
    def test_document_exists_and_covers_gaps(self):
        self.assertTrue(GAP_CLOSURE.is_file())
        text = GAP_CLOSURE.read_text(encoding="utf-8")
        for token in ("G1", "G2", "G3", "G4", "G6", "BLOCKED_SOURCE", "INFERRED_CANDIDATE"):
            self.assertIn(token, text)
        # author questions must be present and explicitly marked as drafted/not sent
        self.assertIn("НЕ ОТПРАВЛЕН", text)
        self.assertGreaterEqual(text.count("\n"), 40)

    def test_documents_are_cross_consistent(self):
        port = load_json(PORT_CANDIDATES)
        prov = load_json(FOLLOWER_PROVENANCE)
        # the pinned Dataset S1 digest must agree across both deliverables
        self.assertEqual(
            port["source_pins"]["dataset_s1"]["sha256"],
            "dc3cc6c53a9a116630db25a423c8439910d9e2d0ba159ef32424b546bcf3036c",
        )
        prov_by_id = {r["id"]: r for r in prov["provenance_records"]}
        self.assertEqual(
            prov_by_id["dataset_s1_docx"]["sha256"],
            port["source_pins"]["dataset_s1"]["sha256"],
        )
        # every negative-evidence digest must be a 64-hex digest of a real record
        for digest in prov["blocked_source_receipt"]["negative_evidence_digests"]:
            self.assertTrue(SHA256_RE.fullmatch(digest), digest)
            self.assertIn(digest, {r.get("sha256") for r in prov["provenance_records"]})
        # SI figure digest cited by the port map must be a provenance record pin
        record_shas = {r.get("sha256") for r in prov["provenance_records"]}
        self.assertIn(port["source_pins"]["suppl_figure_s5"]["sha256"], record_shas)


class TestRepoStateInvariants(unittest.TestCase):
    def test_forbidden_state_files_not_modified_by_this_wo(self):
        # This test asserts the files exist (read-only sanity); the actual
        # not-modified guarantee is enforced by review/diff against base main.
        for rel in ("project/state.json", "project/plan.json"):
            self.assertTrue((REPO_ROOT / rel).is_file())

    def test_deliverable_files_exist_on_disk(self):
        self.assertTrue(PORT_CANDIDATES.is_file())
        self.assertTrue(FOLLOWER_PROVENANCE.is_file())
        # digest sanity: computed digests must parse as hex (self-check of tooling)
        self.assertTrue(SHA256_RE.fullmatch(sha256_of_file(PORT_CANDIDATES)))


if __name__ == "__main__":
    unittest.main()
