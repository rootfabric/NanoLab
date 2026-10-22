"""[REVIEWER-76] Independent ad-hoc falsification probes for PR #76 @ HEAD 2e199d6.

Read-only against the repo: all fixtures live in a TemporaryDirectory.
Probes:
  P1  chain-direction semantics re-derivation (n3/n5, 3p/5p, 5'->3' order)
  P2  wrong-polarity declared segment (raw file order, not 5'->3') must be blocked
  P3  valid unwrapped PBC coordinates + rotated orthonormal orientation must NOT block
  P4  covalent / same-part / float-index / duplicate-key anchor maps must block
  P5  inf box must block
  P6  rights=ALLOWED required (RESTRICTED blocked) at anchor-map level
  P7  nested path traversal + symlinked parent dir must block
"""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path("/home/rdpuser/NanoLab/review-pr76-r1")
sys.path.insert(0, str(REPO / "scripts"))
from knowledge_pack import alt_pair_source_gate as gate  # noqa: E402

PUBLISHED = json.loads((REPO / "docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json").read_text())


def topology_rows(seq_5p_to_3p: str, strand_id: int = 1) -> str:
    """Legacy .top: rows traverse 3p->5p, row = 'sid base n3 n5'."""
    rows_3p_to_5p = seq_5p_to_3p[::-1]
    body = "".join(
        f"{strand_id} {base} {i-1 if i else -1} {i+1 if i + 1 < len(rows_3p_to_5p) else -1}\n"
        for i, base in enumerate(rows_3p_to_5p)
    )
    return f"{len(rows_3p_to_5p)} 1\n" + body


def dat_lines(positions, o1=(1.0, 0.0, 0.0), o2=(0.0, 0.0, 1.0)):
    lines = ["t = 0", "b = 30 30 30", "E = 0 0 0"]
    for p in positions:
        vals = list(p) + list(o1) + list(o2) + [0.0] * 6
        lines.append(" ".join(repr(float(v)) for v in vals))
    return "\n".join(lines) + "\n"


class ProbeBase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pack = json.loads(json.dumps(PUBLISHED))
        cand = self.pack["candidates"][0]
        cand["candidate_id"] = "PROBE_TWO_PART"
        cand["design_basis"] = "SYNTHETIC_FIXTURE"
        self.pack["selected_candidate_id"] = cand["candidate_id"]
        self.pack["candidates"] = [cand]
        # part A sequence 5'->3': AAGGTTACGTAC ; part B is its reverse complement
        for part, seq in zip(cand["parts"], ("AAGGTTACGTAC", "GTACGTAACCTT")):
            pid = part["part_id"].lower()
            top = self.root / f"{pid}.top"
            top.write_text(topology_rows(seq), encoding="utf-8")
            conf = self.root / f"{pid}.dat"
            positions = [(1.0 + i, 5.0, 5.0) for i in range(12)]
            conf.write_text(dat_lines(positions), encoding="utf-8")
            for role, f in (("topology", top), ("configuration", conf)):
                data = f.read_bytes()
                part[role] = {
                    "status": "CONTENT_VERIFIED",
                    "path": f.name,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "size_bytes": len(data),
                    "rights": "ALLOWED",
                    "source_url": "https://example.org/probe/" + f.name,
                }
        self.cand = cand

    def write_anchor_map(self, amap):
        p = self.root / "ports.json"
        p.write_text(json.dumps(amap, sort_keys=True), encoding="utf-8")
        data = p.read_bytes()
        self.cand["interface"]["anchor_map"] = {
            "status": "CONTENT_VERIFIED",
            "path": "ports.json",
            "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data),
            "rights": "ALLOWED",
            "source_url": "https://example.org/probe/ports.json",
        }

    def base_pair(self):
        # A suffix "ACGTAC" at its 3p terminus; B prefix "GTACGT" at its 5p terminus;
        # revcomp(ACGTAC) == GTACGT.
        return {
            "part_a": "NARCISSUS", "part_b": "ECHO",
            "a_index": 0, "b_index": 11,
            "a_end": "3p", "b_end": "5p",
            "segment_a": "ACGTAC", "segment_b": "GTACGT",
            "kind": "NONCOVALENT_DNA_HYBRIDIZATION",
            "status": "SOURCE_CONFIRMED",
        }


class P1_ChainSemantics(ProbeBase):
    """Re-derive n3/n5 semantics straight from Topology, independent of the gate."""

    def test_parser_semantics(self):
        top = gate.Topology.parse(topology_rows("AAGGTTACGTAC"))
        rows = top.rows
        # rows traverse 3p->5p: first row is the 3' terminus (n3 == -1),
        # last row is the 5' terminus (n5 == -1)
        self.assertEqual(rows[0][2], -1, "3p terminus must have n3 == -1")
        self.assertEqual(rows[-1][3], -1, "5p terminus must have n5 == -1")
        self.assertEqual([r[2] for r in rows[1:]], list(range(0, 11)), "n3 points back toward 3p side")
        self.assertEqual([r[3] for r in rows[:-1]], list(range(1, 12)), "n5 points forward toward 5p side")
        self.assertEqual(top.check_chain_integrity()["linear_strands"], 1)
        # gate segment reader returns the conventional 5'->3' representation
        got_3p, err = gate._verified_terminal_segment(top, 0, "3p", 6)
        self.assertIsNone(err)
        self.assertEqual(got_3p, "ACGTAC", "3p-end 6-mer in 5'->3' order of AAGGTTACGTAC is the suffix")
        got_5p, err = gate._verified_terminal_segment(top, 11, "5p", 6)
        self.assertIsNone(err)
        self.assertEqual(got_5p, "AAGGTT", "5p-end 6-mer is the prefix")
        # internal index is refused as a terminal
        _, err = gate._verified_terminal_segment(top, 5, "3p", 6)
        self.assertIn("internal anchor", err)
        _, err = gate._verified_terminal_segment(top, 5, "5p", 6)
        self.assertIn("internal anchor", err)
        # segment longer than the strand is refused (bounds check fires first)
        _, err = gate._verified_terminal_segment(top, 0, "3p", 13)
        self.assertIn("invalid segment length", err)
        # circular strand has no terminus
        circ = "12 1\n" + "".join(
            f"1 {'ACGT' [i % 4]} {(i-1) % 12} {(i+1) % 12}\n" for i in range(12)
        )
        ctop = gate.Topology.parse(circ)
        ctop.check_chain_integrity()
        _, err = gate._verified_terminal_segment(ctop, 0, "3p", 6)
        self.assertIn("terminus", err)


class P2_Polarity(ProbeBase):
    def test_raw_file_order_segment_must_block(self):
        """Declared segment equal to the raw 3p->5p file-order slice (wrong polarity) is refused."""
        amap = {"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]}
        amap["pairs"][0]["segment_a"] = "CATGCA"  # file rows 0..5 = reverse of ACGTAC
        amap["pairs"][0]["segment_b"] = "TGCATG"  # reverse complement of CATGCA
        self.write_anchor_map(amap)
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE", result)
        self.assertTrue(any("topology sequence mismatch" in r for r in result["reasons"]), result)


class P3_NoFalsePositives(ProbeBase):
    def test_unwrapped_pbc_and_rotated_orientation_pass(self):
        """Valid oxDNA PBC unwrapped coords + rotated orthonormal frame must NOT block."""
        s2 = 0.6, 0.0, 0.8
        o2r = (-0.8, 0.0, 0.6)
        for part in self.cand["parts"]:
            conf = self.root / (part["part_id"].lower() + ".dat")
            positions = [(40.0 + i * 1.5, -12.5 + i, 61.0) for i in range(12)]  # outside box 30
            conf.write_text(dat_lines(positions, o1=s2, o2=o2r), encoding="utf-8")
            data = conf.read_bytes()
            part["configuration"] = {
                "status": "CONTENT_VERIFIED",
                "path": conf.name,
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
                "rights": "ALLOWED",
                "source_url": "https://example.org/probe/" + conf.name,
            }
        self.write_anchor_map({"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]})
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        self.assertEqual(result["outcome"], "TEST_FIXTURE_STATIC_INPUTS_OK", result)


class P4_AnchorMapNegatives(ProbeBase):
    def _run(self, amap):
        self.write_anchor_map(amap)
        return gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)

    def test_covalent_kind_blocked(self):
        amap = {"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]}
        amap["pairs"][0]["kind"] = "COVALENT_LIGATION"
        result = self._run(amap)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("unsupported connection chemistry" in r for r in result["reasons"]))

    def test_same_part_pair_blocked(self):
        amap = {"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]}
        amap["pairs"][0]["part_b"] = "NARCISSUS"
        result = self._run(amap)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("wrong parts" in r for r in result["reasons"]))

    def test_float_index_blocked(self):
        amap = {"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]}
        amap["pairs"][0]["a_index"] = 0.0
        result = self._run(amap)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("out-of-bounds anchor" in r for r in result["reasons"]))

    def test_bool_index_blocked(self):
        amap = {"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]}
        amap["pairs"][0]["b_index"] = True
        result = self._run(amap)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")

    def test_duplicate_json_key_in_anchor_map_blocked(self):
        p = self.root / "ports.json"
        p.write_text('{"kind":"two_part_dna_interface_map","pairs":[],"pairs":[{"x":1}]}', encoding="utf-8")
        data = p.read_bytes()
        self.cand["interface"]["anchor_map"] = {
            "status": "CONTENT_VERIFIED",
            "path": "ports.json",
            "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data),
            "rights": "ALLOWED",
            "source_url": "https://example.org/probe/ports.json",
        }
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("anchor map JSON invalid" in r for r in result["reasons"]))

    def test_inferred_status_blocked(self):
        amap = {"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]}
        amap["pairs"][0]["status"] = "SOURCE_CONFIRMED_BY_REVIEWER"
        result = self._run(amap)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("UNKNOWN or inferred" in r for r in result["reasons"]))


class P5_NonfiniteBox(ProbeBase):
    def test_inf_box_blocked(self):
        for part in self.cand["parts"]:
            conf = self.root / (part["part_id"].lower() + ".dat")
            conf.write_text(dat_lines([(1.0 + i, 5.0, 5.0) for i in range(12)]).replace(
                "b = 30 30 30", "b = 30 inf 30"), encoding="utf-8")
            data = conf.read_bytes()
            part["configuration"] = {
                "status": "CONTENT_VERIFIED", "path": conf.name,
                "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data),
                "rights": "ALLOWED", "source_url": "https://example.org/probe/x",
            }
        self.write_anchor_map({"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]})
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("nonfinite or invalid configuration box" in r for r in result["reasons"]))


class P6_Rights(ProbeBase):
    def test_restricted_anchor_map_blocked(self):
        self.write_anchor_map({"kind": "two_part_dna_interface_map", "pairs": [self.base_pair()]})
        self.cand["interface"]["anchor_map"]["rights"] = "RESTRICTED"
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("RIGHTS_NOT_CLEARED" in r for r in result["reasons"]))

    def test_forbidden_rights_blocked(self):
        self.cand["parts"][0]["configuration"]["rights"] = "FORBIDDEN"
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("RIGHTS_NOT_CLEARED (FORBIDDEN)" in r for r in result["reasons"]))


class P7_Paths(ProbeBase):
    def test_nested_traversal_blocked(self):
        self.cand["parts"][0]["topology"]["path"] = "sub/../../escape.top"
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("path traversal" in r for r in result["reasons"]))

    def test_symlinked_parent_dir_blocked(self):
        link_dir = self.root / "linkdir"
        try:
            link_dir.symlink_to(self.root)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unsupported")
        self.cand["parts"][0]["topology"]["path"] = "linkdir/narcissus.top"
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        self.assertEqual(result["outcome"], "BLOCKED_SOURCE")
        self.assertTrue(any("symlink" in r for r in result["reasons"]))

    def test_dot_segment_is_normalized_not_an_escape(self):
        """'./x' is normalized by pathlib; it must stay inside root (no escape either way)."""
        self.cand["parts"][0]["topology"]["path"] = "./narcissus.top"
        result = gate.evaluate(self.pack, "PROBE_TWO_PART", self.root)
        # Either accepted (same file, digest matches) or fail-closed; in both cases
        # the resolved file must remain inside root. Documented reviewer observation.
        self.assertIn(result["outcome"], ("TEST_FIXTURE_STATIC_INPUTS_OK", "BLOCKED_SOURCE"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
