"""Tests for S17 R2 static assembly preflight and fail-closed recipe enforcement.

WO-PREP-S17-R2 stage C. The core discipline under test: a recipe that is not
SOURCE_CONFIRMED never assembles anything; SOURCE_CONFIRMED recipes must cite
sources for every link; links may only join file-strand terminals; assembled
topologies must reparse strictly and digest deterministically.
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from knowledge_pack import s17_assembly as asm
from hinge_family.oxdna_topology import Topology


def lin_rows(strands: dict[int, str]) -> list:
    """Build rows with *global* neighbour indices (strands are contiguous)."""
    rows = []
    offset = 0
    for sid, seq in strands.items():
        n = len(seq)
        for i, base in enumerate(seq):
            rows.append((sid, base,
                         offset + i - 1 if i > 0 else -1,
                         offset + i + 1 if i < n - 1 else -1))
        offset += n
    return rows


def write_pair(td: Path, name: str, strands: dict[int, str]) -> tuple[Path, Path, str]:
    rows = lin_rows(strands)
    text = f"{len(rows)} {len(strands)}\n" + "".join(f"{s} {b} {n3} {n5}\n" for s, b, n3, n5 in rows)
    top = td / f"{name}.top"
    top.write_text(text)
    conf = td / f"{name}.dat"
    conf.write_text(dat_text(len(rows)))
    return top, conf, hashlib.sha256(text.encode()).hexdigest()


def dat_text(n: int) -> str:
    """Minimal strict-parseable oxDNA configuration with n particles."""
    head = "t = 0\nb = 10 10 10\nE = 0.0 0.0 0.0\n"
    row = "{:.3f} 0 0  1 0 0  0 0 1  0 0 0  0 0 0\n"
    return head + "".join(row.format(0.1 * i) for i in range(n))


def make_top(strands: dict[int, str]) -> Topology:
    rows = lin_rows(strands)
    return Topology(len(rows), len(strands), rows)


class StaticPreflightTests(unittest.TestCase):
    def test_preflight_ok_on_consistent_pair(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            top, conf, sha = write_pair(td, "compA", {1: "ACG", 2: "TTAGCC"})
            r = asm.static_preflight(top, conf, topology_sha256=sha)
            self.assertTrue(r.ok, r.errors)
            self.assertEqual(r.nucleotides, 9)
            self.assertEqual(r.strand_count, 2)
            self.assertTrue(r.counts_match)
            self.assertTrue(r.valency_ok)
            self.assertTrue(r.deterministic_reimport)
            self.assertEqual(r.circular_strands, 0)
            self.assertTrue(r.index_map_digest)

    def test_preflight_fails_on_wrong_pin(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            top, conf, _ = write_pair(td, "compA", {1: "ACG"})
            r = asm.static_preflight(top, conf, topology_sha256="f" * 64)
            self.assertFalse(r.ok)
            self.assertTrue(any("pin mismatch" in e for e in r.errors))

    def test_preflight_fails_on_count_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            top, conf, _ = write_pair(td, "compA", {1: "ACG"})
            conf.write_text(dat_text(1))  # 1 particle vs 3
            r = asm.static_preflight(top, conf)
            self.assertFalse(r.ok)
            self.assertTrue(any("count" in e.lower() for e in r.errors))

    def test_preflight_detects_circular_strand(self):
        n = 4
        rows = [(1, "ACGT"[i], (i - 1) % n, (i + 1) % n) for i in range(n)]
        text = f"{n} 1\n" + "".join(f"{s} {b} {n3} {n5}\n" for s, b, n3, n5 in rows)
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            top = td / "c.top"
            top.write_text(text)
            conf = td / "c.dat"
            conf.write_text(dat_text(n))
            r = asm.static_preflight(top, conf)
            self.assertTrue(r.ok, r.errors)
            self.assertEqual(r.circular_strands, 1)
            self.assertEqual(r.linear_strands, 0)

    def test_preflight_fails_on_broken_valency(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            top = td / "v.top"
            top.write_text("2 1\n0 A -1 1\n1 C 0 99\n")  # n5 out of bounds
            conf = td / "v.dat"
            conf.write_text(dat_text(2))
            r = asm.static_preflight(top, conf)
            self.assertFalse(r.ok)
            self.assertTrue(any("valency" in e for e in r.errors))


class RecipeDisciplineTests(unittest.TestCase):
    COMPONENTS = {"driver": {"nucleotides": 6, "strands": 2},
                  "follower": {"nucleotides": 4, "strands": 1}}
    ORDER = ([{"component": "driver", "strand_id": 1},
              {"component": "driver", "strand_id": 2},
              {"component": "follower", "strand_id": 1}])

    def test_no_recipe_is_not_reconstructed(self):
        r = asm.evaluate_recipe(None, self.COMPONENTS)
        self.assertEqual(r["assembly_status"], "NOT_RECONSTRUCTED")
        self.assertIsNone(r["assembled"])
        self.assertTrue(r["blocked_inputs"])

    def test_inferred_recipe_never_assembles(self):
        recipe = {"status": "INFERRED_CANDIDATE", "source_refs": ["x"], "strand_order": [], "links": []}
        r = asm.evaluate_recipe(recipe, self.COMPONENTS)
        self.assertEqual(r["assembly_status"], "BLOCKED_INFERRED_RECIPE")
        self.assertIn("may never pass a production preflight", r["reason"])

    def test_unknown_status_fails_closed(self):
        r = asm.evaluate_recipe({"status": "SOMEHOW_FINE"}, self.COMPONENTS)
        self.assertEqual(r["assembly_status"], "NOT_RECONSTRUCTED")

    def test_source_confirmed_requires_full_strand_coverage(self):
        recipe = {"status": "SOURCE_CONFIRMED", "source_refs": ["s1"],
                  "strand_order": [{"component": "driver", "strand_id": 1}],
                  "links": []}
        r = asm.evaluate_recipe(recipe, self.COMPONENTS)
        self.assertEqual(r["assembly_status"], "BLOCKED_INFERRED_RECIPE")
        self.assertIn("exactly 1", r["reason"])

    def test_link_without_source_ref_rejected(self):
        order = list(self.ORDER)
        recipe = {"status": "SOURCE_CONFIRMED", "source_refs": ["s1"], "strand_order": order,
                  "links": [{"from_particle": {"component": "driver", "particle": 1},
                             "to_particle": {"component": "follower", "particle": 0},
                             "kind": "n3_n5"}]}
        r = asm.evaluate_recipe(recipe, self.COMPONENTS)
        self.assertEqual(r["assembly_status"], "BLOCKED_INFERRED_RECIPE")
        self.assertIn("source_ref", r["reason"])

    def test_link_out_of_bounds_rejected(self):
        order = list(self.ORDER)
        recipe = {"status": "SOURCE_CONFIRMED", "source_refs": ["s1"], "strand_order": order,
                  "links": [{"from_particle": {"component": "driver", "particle": 999},
                             "to_particle": {"component": "follower", "particle": 0},
                             "kind": "n3_n5", "source_ref": "pinned-source"}]}
        r = asm.evaluate_recipe(recipe, self.COMPONENTS)
        self.assertEqual(r["assembly_status"], "BLOCKED_INFERRED_RECIPE")
        self.assertIn("out of bounds", r["reason"])

    def test_well_formed_recipe_is_pending(self):
        order = list(self.ORDER)
        recipe = {"status": "SOURCE_CONFIRMED", "source_refs": ["pinned:source"], "strand_order": order,
                  "links": [{"from_particle": {"component": "driver", "particle": 2},
                             "to_particle": {"component": "follower", "particle": 0},
                             "kind": "n3_n5", "source_ref": "pinned:source"}]}
        r = asm.evaluate_recipe(recipe, self.COMPONENTS)
        self.assertEqual(r["assembly_status"], "PENDING_ASSEMBLY", r["reason"])


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        # driver: strand 1 "ACG", strand 2 "TTA" (particle 5 is its 5'-terminal);
        # follower: strand 1 "GGC" (particle 6 is its 3'-terminal).
        self.driver = make_top({1: "ACG", 2: "TTA"})
        self.follower = make_top({1: "GGC"})
        self.order = ([{"component": "driver", "strand_id": 1},
                       {"component": "driver", "strand_id": 2},
                       {"component": "follower", "strand_id": 1}])

    def linked_recipe(self):
        return {"status": "SOURCE_CONFIRMED", "source_refs": ["pinned:source"],
                "strand_order": self.order,
                "links": [{"from_particle": {"component": "driver", "particle": 5},
                           "to_particle": {"component": "follower", "particle": 0},
                           "kind": "n3_n5", "source_ref": "pinned:source"}]}

    def test_assembly_is_deterministic(self):
        r1 = asm.assemble_from_recipe(self.linked_recipe(),
                                      {"driver": self.driver, "follower": self.follower})
        r2 = asm.assemble_from_recipe(self.linked_recipe(),
                                      {"driver": self.driver, "follower": self.follower})
        self.assertEqual(r1["assembly_status"], "ASSEMBLED_STATIC_ONLY", r1["reason"])
        self.assertEqual(r1["assembled"], r2["assembled"])
        self.assertEqual(r1["assembled"]["nucleotides"], 9)
        self.assertEqual(r1["assembled"]["strands"], 2)

    def test_assembled_topology_reparses_and_carries_rewire(self):
        tops = {"driver": self.driver, "follower": self.follower}
        r = asm.assemble_from_recipe(self.linked_recipe(), tops)
        text, _ = asm.assemble_topology_text(self.linked_recipe(), tops)
        t = Topology.parse(text)
        self.assertEqual(t.nucleotides, 9)
        # driver particle 5 (5'-terminal of its file strand) is now bonded to
        # follower particle 6 (its 3'-terminal); both pieces share strand id 1.
        self.assertEqual(t.rows[5][3], 6)
        self.assertEqual(t.rows[6][2], 5)
        self.assertEqual(t.rows[5][0], t.rows[6][0])
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),
                         r["assembled"]["topology_text_sha256"])

    def test_non_terminal_link_rejected(self):
        recipe = self.linked_recipe()
        recipe["links"] = [{"from_particle": {"component": "driver", "particle": 3},
                            "to_particle": {"component": "follower", "particle": 0},
                            "kind": "n3_n5", "source_ref": "pinned:source"}]
        r = asm.assemble_from_recipe(recipe, {"driver": self.driver, "follower": self.follower})
        self.assertEqual(r["assembly_status"], "BLOCKED_INFERRED_RECIPE")
        self.assertIn("terminals", r["reason"])

    def test_invented_link_vocabulary_is_ignored_at_assembly(self):
        # A recipe whose links lack source_ref can never reach the assembly code.
        recipe = self.linked_recipe()
        for lnk in recipe["links"]:
            lnk.pop("source_ref")
        r = asm.assemble_from_recipe(recipe, {"driver": self.driver, "follower": self.follower})
        self.assertEqual(r["assembly_status"], "BLOCKED_INFERRED_RECIPE")


class NotReconstructedTests(unittest.TestCase):
    def test_df_receipt_lists_blocked_inputs_and_never_assembles(self):
        r = asm.not_reconstructed_receipt(
            "driver_follower_md_linked_assembly",
            {"driver": {"nucleotides": 14343, "strands": 163}},
            ["driver/follower MD run directories are absent from all four Zenodo archives",
             "D-F inter-molecular linkage list is not published in any audited surface"])
        self.assertEqual(r["assembly_status"], "NOT_RECONSTRUCTED")
        self.assertIsNone(r["assembled"])
        self.assertEqual(len(r["blocked_inputs"]), 2)
        self.assertIn("never ASSEMBLY_VALIDATED", r["claim"])

    def test_unknown_status_string_is_rejected(self):
        with self.assertRaises(asm.AssemblyError):
            asm._receipt("MAGIC_STATUS", None, {}, [], None)


if __name__ == "__main__":
    unittest.main()
