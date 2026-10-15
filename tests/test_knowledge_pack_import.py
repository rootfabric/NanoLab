"""Import validation tests (PREP-S17, WO-PREP-S17-R1).

Positive: well-formed synthetic oxDNA pair imports deterministically.
Negative controls: corrupted base, broken neighbour link, truncated
configuration, count mismatch — all fail closed.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from knowledge_pack.import_validation import (  # noqa: E402
    ImportValidationError,
    canonical_structural_digest,
    import_paired,
)
from hinge_family.oxdna_conf import Configuration  # noqa: E402
from hinge_family.oxdna_topology import Topology  # noqa: E402

# Simple two-strand duplex: 5 bases each. Strands are listed 3'->5'; n3/n5
# are 0-based neighbour indices, -1 = none.
TOP_OK = (
    "10 2\n"
    "1 A -1 1\n1 C 0 2\n1 G 1 3\n1 T 2 4\n1 A 3 -1\n"
    "2 T -1 6\n2 A 5 7\n2 T 6 8\n2 C 7 9\n2 G 8 -1\n"
)
CONF_HEADER = "t = 1000\nb = 100 100 100\nE = 0.1 0.2 0.3\n"
CONF_ROW = "1.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0 0.1 0.1 0.1 0.0 0.0 0.0\n"


def _write_pair(top_text: str, conf_text: str) -> tuple:
    tmp = tempfile.mkdtemp(prefix="kp-import-")
    top = Path(tmp) / "s.top"
    conf = Path(tmp) / "s.dat"
    top.write_text(top_text, encoding="utf-8")
    conf.write_text(conf_text, encoding="utf-8")
    return top, conf


class TestPositiveImport(unittest.TestCase):
    def test_wellformed_pair_imports_ok(self) -> None:
        top, conf = _write_pair(TOP_OK, CONF_HEADER + CONF_ROW * 10)
        result = import_paired(top, conf)
        self.assertEqual(result.errors, [])
        self.assertTrue(result.ok)
        self.assertTrue(result.counts_match)
        self.assertTrue(result.deterministic_reimport)
        self.assertEqual(result.nucleotides, 10)
        self.assertEqual(result.strand_count, 2)
        self.assertEqual(result.chain_facts.get("linear_strands"), 2)
        self.assertEqual(
            result.base_composition, {"A": 3, "C": 2, "G": 2, "T": 3}
        )

    def test_structural_digest_is_stable_across_whitespace(self) -> None:
        top_a, conf_a = _write_pair(TOP_OK, CONF_HEADER + CONF_ROW * 10)
        top_b, conf_b = _write_pair(TOP_OK.replace(" ", "  "), CONF_HEADER + CONF_ROW * 10)
        result_a = import_paired(top_a, conf_a)
        result_b = import_paired(top_b, conf_b)
        self.assertEqual(result_a.structural_digest, result_b.structural_digest)

    def test_structural_digest_changes_with_content(self) -> None:
        top_a, conf_a = _write_pair(TOP_OK, CONF_HEADER + CONF_ROW * 10)
        top_b, conf_b = _write_pair(TOP_OK.replace("1 A -1 1", "1 T -1 1", 1), CONF_HEADER + CONF_ROW * 10)
        result_a = import_paired(top_a, conf_a)
        result_b = import_paired(top_b, conf_b)
        self.assertNotEqual(result_a.structural_digest, result_b.structural_digest)


class TestNegativeImports(unittest.TestCase):
    def _assert_not_ok(self, result, fragment: str) -> None:
        self.assertFalse(result.ok)
        self.assertTrue(
            any(fragment in e for e in result.errors),
            f"expected {fragment!r} in {result.errors}",
        )

    def test_invalid_base_letter_fails(self) -> None:
        top, conf = _write_pair(TOP_OK.replace("1 A -1 1", "1 X -1 1", 1), CONF_HEADER + CONF_ROW * 10)
        result = import_paired(top, conf)
        self._assert_not_ok(result, "topology parse error")

    def test_broken_neighbour_link_fails_integrity(self) -> None:
        # 5' neighbour of nucleotide 9 claims 7 instead of 8: asymmetric link.
        broken = TOP_OK.replace("2 G 8 -1", "2 G 7 -1", 1)
        top, conf = _write_pair(broken, CONF_HEADER + CONF_ROW * 10)
        result = import_paired(top, conf)
        self._assert_not_ok(result, "chain integrity error")

    def test_truncated_configuration_fails(self) -> None:
        top, conf = _write_pair(TOP_OK, CONF_HEADER + CONF_ROW * 9)  # 9 rows for 10 nts
        result = import_paired(top, conf)
        self._assert_not_ok(result, "count mismatch")

    def test_count_mismatch_fails(self) -> None:
        # Topology declares 10 but conf has 10 rows of a different length? Use
        # a top with 11 declared rows removed from conf: header mismatch path.
        top, conf = _write_pair("10 2\n" + "\n".join(TOP_OK.strip().splitlines()[1:9]) + "\n", CONF_HEADER + CONF_ROW * 8)
        result = import_paired(top, conf)
        self.assertFalse(result.ok)
        self.assertTrue(result.errors)

    def test_non_utf8_configuration_fails_closed(self) -> None:
        top, conf = _write_pair(TOP_OK, CONF_HEADER + CONF_ROW * 10)
        conf.write_bytes(b"\xff\xfe not utf-8 at all")
        with self.assertRaises(ImportValidationError):
            import_paired(top, conf)

    def test_structural_digest_is_sensitive_to_linkage(self) -> None:
        # Same counts/bases/strand lengths, different n3/n5 linkage.
        rows_a = [(1, "A", -1, 1), (1, "C", 0, -1)]
        rows_b = [(1, "A", -1, -1), (1, "C", -1, -1)]
        conf = Configuration(time="0", box=[1.0, 1.0, 1.0], energy_line="E = 0 0 0", particles=[])
        digest_a, _ = canonical_structural_digest(Topology(2, 1, rows_a), conf)
        digest_b, _ = canonical_structural_digest(Topology(2, 1, rows_b), conf)
        self.assertNotEqual(digest_a, digest_b)


if __name__ == "__main__":
    unittest.main()
