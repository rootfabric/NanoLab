"""Tests for the S17 R2 deterministic nucleotide index-space map.

WO-PREP-S17-R2 stage B. Synthetic mini-topologies only (offline); the real
14343-nt pins are exercised by the evidence layer, not by unit tests.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from knowledge_pack import s17_index_map as im
from hinge_family.oxdna_topology import Topology


def lin_top(strands: dict[int, str]) -> Topology:
    """Build a linear-strand topology; rows listed 3'->5' per strand."""
    rows = []
    for sid, seq in strands.items():
        n = len(seq)
        for i, base in enumerate(seq):
            rows.append((sid, base, i - 1 if i > 0 else -1, i + 1 if i < n - 1 else -1))
    return Topology(len(rows), len(strands), rows)


def circ_top(sid: int, seq: str) -> Topology:
    n = len(seq)
    rows = [(sid, seq[i], (i - 1) % n, (i + 1) % n) for i in range(n)]
    return Topology(n, 1, rows)


class ConventionTests(unittest.TestCase):
    def test_zero_based_indexing_and_terminals(self):
        t = lin_top({0: "ACGT"})
        rec = im.resolve_indices(t, [0, 3], "0" * 64)
        first, last = rec["resolved"]
        self.assertEqual(first["position_in_strand"], 0)
        self.assertTrue(first["is_3prime_terminal_of_file_strand"])
        self.assertFalse(first["is_5prime_terminal_of_file_strand"])
        self.assertEqual(last["position_in_strand"], 3)
        self.assertTrue(last["is_5prime_terminal_of_file_strand"])

    def test_negative_index_rejected(self):
        t = lin_top({0: "AC"})
        with self.assertRaises(im.IndexMapError):
            im.resolve_indices(t, [-1], "0" * 64)

    def test_index_equal_to_count_is_out_of_bounds(self):
        t = lin_top({0: "AC"})
        with self.assertRaises(im.IndexMapError):
            im.resolve_indices(t, [2], "0" * 64)

    def test_non_integer_and_bool_indices_rejected(self):
        t = lin_top({0: "AC"})
        for bad in ("1", 1.0, True, None):
            with self.assertRaises(im.IndexMapError):
                im.resolve_indices(t, [bad], "0" * 64)

    def test_circular_strand_detected_and_last_index_resolves(self):
        t = circ_top(7, "ACGT")
        spans = im.strand_spans(t)
        self.assertTrue(spans[0].circular)
        rec = im.resolve_indices(t, [3], "0" * 64)["resolved"][0]
        self.assertEqual(rec["strand_id"], 7)
        self.assertEqual(rec["position_in_strand"], 3)
        self.assertTrue(rec["strand_circular"])

    def test_linear_strand_not_marked_circular(self):
        t = lin_top({0: "ACGT"})
        self.assertFalse(im.strand_spans(t)[0].circular)


class PinDisciplineTests(unittest.TestCase):
    def test_load_topology_verified_rejects_wrong_pin(self):
        data = b"3 1\n0 A -1 1\n1 C 0 2\n2 G 1 -1\n"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "t.top"
            p.write_bytes(data)
            wrong = "b" * 64
            with self.assertRaises(im.IndexMapError):
                im.load_topology_verified(p, wrong)
            good = hashlib.sha256(data).hexdigest()
            t = im.load_topology_verified(p, good)
            self.assertEqual(t.nucleotides, 3)

    def test_load_topology_rejects_non_utf8(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "t.top"
            p.write_bytes(b"\xff\xfe\x00garbage")
            with self.assertRaises(im.IndexMapError):
                im.load_topology_verified(p, "0" * 64)

    def test_load_topology_rejects_structurally_broken_file(self):
        data = b"5 1\n0 A -1 1\n"  # header declares 5 rows, only 1 present
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "t.top"
            p.write_bytes(data)
            with self.assertRaises(im.IndexMapError):
                im.load_topology_verified(p, hashlib.sha256(data).hexdigest())


class DeterminismTests(unittest.TestCase):
    def test_index_map_digest_is_stable_across_reparse(self):
        t1 = lin_top({0: "ACGTACGT", 1: "TTTTGGGG"})
        t2 = lin_top({0: "ACGTACGT", 1: "TTTTGGGG"})
        self.assertEqual(im.index_map_digest(t1), im.index_map_digest(t2))

    def test_index_map_digest_changes_with_content(self):
        t1 = lin_top({0: "ACGTACGT"})
        t2 = lin_top({0: "ACGTACGA"})
        self.assertNotEqual(im.index_map_digest(t1), im.index_map_digest(t2))

    def test_map_is_fully_serializable(self):
        t = circ_top(1, "ACGT" * 5)
        blob = json.dumps(im.build_index_map(t))
        self.assertIn('"convention"', blob)
        self.assertEqual(len(json.loads(blob)["records"]), 20)

    def test_duplicate_non_contiguous_strand_rejected(self):
        rows = [(0, "A", -1, 1), (0, "C", 0, -1), (1, "G", -1, -1), (0, "T", -1, -1)]
        t = Topology(4, 3, rows)
        with self.assertRaises(im.IndexMapError):
            im.build_index_map(t)


class PairingClaimDiscipline(unittest.TestCase):
    def test_base_pairing_from_bare_top_is_refused(self):
        t = lin_top({0: "AC", 1: "GT"})
        with self.assertRaises(NotImplementedError):
            im.base_pair_pairs(t)


if __name__ == "__main__":
    unittest.main()
