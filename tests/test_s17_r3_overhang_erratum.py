"""S17-R3 ERRATUM-1: pinned 20nt follower overhang source contract (offline).

Original state has seven 21nt declarations; their extra leading nucleotide is
outside each published matched 20nt window. This is a RED->GREEN falsifier: do
not weaken the assertions or re-pin any original source file.
"""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from knowledge_pack.assembly_spec import reverse_complement, strip_lna

FOLLOWER = ROOT / "docs/research/S17_R3_COMPONENT_FOLLOWER.json"
DRIVER = ROOT / "docs/research/S17_R3_COMPONENT_DRIVER.json"
RECIPE = ROOT / "docs/work/executions/EX-PREP-S17-R3/evidence/s17-r3-df-interface-recipe.json"
EXPECTED_RECIPE_SHA256 = "5f485b0ac8d1e822a424a73f065ede7df36245ee4cd8a8e27cbe93681f1b61b6"

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

class S17Follower20ntErratum(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.follow = read_json(FOLLOWER)
        cls.driver = read_json(DRIVER)
        cls.recipe = read_json(RECIPE)
        cls.ports_f = {x["chemistry"]["odn_name"]: x for x in cls.follow["ports"]}
        cls.ports_d = {x["chemistry"]["odn_name"]: x for x in cls.driver["ports"]}
        cls.pairs = cls.recipe["pairs"]

    def test_original_pinned_recipe_bytes_unchanged(self):
        self.assertEqual(hashlib.sha256(RECIPE.read_bytes()).hexdigest(), EXPECTED_RECIPE_SHA256)
        self.assertEqual(self.recipe["source_pins"]["dataset_s1"]["sha256"],
                         "dc3cc6c53a9a116630db25a423c8439910d9e2d0ba159ef32424b546bcf3036c")

    def test_all_ten_follower_windows_match_exact_20nt_pinned_segments(self):
        self.assertEqual(len(self.pairs), 10)
        self.assertEqual(len(self.ports_f), 10)
        self.assertEqual({x["follower_odn"] for x in self.pairs}, set(self.ports_f))
        for pair in self.pairs:
            with self.subTest(pair_id=pair["pair_id"], follower_odn=pair["follower_odn"]):
                actual = self.ports_f[pair["follower_odn"]]["chemistry"]["overhang_segment"]
                self.assertEqual(len(actual), 20, "R3-REPAIR-ERRATUM-1: not an exact 20nt segment")
                self.assertEqual(actual, pair["follower_segment"],
                                 "source component segment must equal pinned recipe byte-for-byte")
                seq = strip_lna(self.ports_f[pair["follower_odn"]]["chemistry"]["sequence"])
                lo, hi = pair["follower_segment_offsets"]
                self.assertEqual(seq[lo:hi], pair["follower_segment"])
                self.assertEqual(hi-lo, 20)

    def test_all_ten_driver_windows_are_still_exactly_pinned(self):
        self.assertEqual(len(self.ports_d), 10)
        for pair in self.pairs:
            with self.subTest(pair=pair["pair_id"]):
                p = self.ports_d[pair["driver_odn"]]
                self.assertEqual(p["chemistry"]["overhang_segment"], pair["driver_segment"])
                self.assertEqual(reverse_complement(pair["driver_segment"]), pair["follower_segment"])
                self.assertEqual(pair["match_length_nt"], 20)

    def test_no_spurious_physical_port_or_science_claim(self):
        self.assertEqual(self.follow["topology"]["status"], "UNKNOWN")
        self.assertEqual(self.follow["configuration"]["status"], "UNKNOWN")
        for p in self.follow["ports"]:
            self.assertFalse(p["connection_capable"])
            self.assertEqual(p["anchors"][0]["anchor"], "UNKNOWN")
        receipt = read_json(ROOT / "docs/research/S17_R3_ASSEMBLY_RECEIPT.json")
        self.assertEqual(receipt["assembly_status"], "NOT_RECONSTRUCTED")

if __name__ == "__main__":
    unittest.main()
