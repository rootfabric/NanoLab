"""Determinism, uniqueness and exclusion tests for NANOLAB_REPRO_V0_2 seeds.

Pre-data tooling tests (WO-NL5-ACCEPTANCE-POLICY-R2). No simulations.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from nl5 import repro_v02_seeds as seeds

CANDIDATE_DOC = Path(__file__).resolve().parents[1] / "docs" / "research" / "NANOLAB_REPRO_V0_2_CANDIDATE_R1.md"


class DerivationTest(unittest.TestCase):
    def test_derivation_matches_documented_algorithm(self):
        expected = (
            int.from_bytes(hashlib.sha256(b"NANOLAB-REPRO-V0.2-R1|0b|replica-0001").digest()[:4], "big")
            & 0x7FFFFFFF
        )
        self.assertEqual(seeds.derive_seed(seeds.DEFAULT_ANCHOR, "0b|replica-0001"), expected)

    def test_positive_int32(self):
        for variant in seeds.DEFAULT_VARIANTS:
            for seed in seeds.generate_variant_seeds(seeds.DEFAULT_ANCHOR, variant):
                self.assertTrue(0 <= seed < 2**31)

    def test_deterministic_across_calls(self):
        first = seeds.seed_record()
        second = seeds.seed_record()
        self.assertEqual(first, second)
        self.assertEqual(first["record_sha256"], second["record_sha256"])

    def test_anchor_changes_stream(self):
        record_default = seeds.seed_record()
        record_alt = seeds.seed_record(anchor="NANOLAB-REPRO-V0.2-R1-ALT")
        self.assertNotEqual(record_default["record_sha256"], record_alt["record_sha256"])
        self.assertNotEqual(record_default["seeds"]["0b"], record_alt["seeds"]["0b"])

    def test_replica_index_is_one_based(self):
        with self.assertRaises(ValueError):
            seeds.replica_label("0b", 0)


class ExclusionTest(unittest.TestCase):
    def test_no_historical_seed_in_any_stream(self):
        record = seeds.seed_record()
        emitted = set(record["exclusions_applied"])
        self.assertEqual(emitted, set(seeds.HISTORICAL_SEEDS_V1))
        for variant, stream in record["seeds"].items():
            self.assertEqual(set(stream) & seeds.HISTORICAL_SEEDS_V1, set(), variant)
            self.assertEqual(len(stream), seeds.REPLICAS_PER_CELL)
        for variant, seed in record["bootstrap_seeds"].items():
            self.assertNotIn(seed, seeds.HISTORICAL_SEEDS_V1, variant)

    def test_exclusion_list_contains_all_documented_r1_seeds(self):
        documented = {
            -200619630, 319832093, 201004, 202008, 203012,
            204016, 205020, 206024, 902107,
            1259289227, 1358106528, 1524307444, 601855227, 274288237,
            972234272, 1934775205, 1747973984, 880427736, 744386736,
        }
        self.assertEqual(seeds.HISTORICAL_SEEDS_V1, frozenset(documented))

    def test_generator_refuses_excluded_value(self):
        anchor = "collide-probe"
        # Inject the value the stream will actually produce: the refusal path
        # must trigger whenever any generated seed is excluded.
        first_seed = seeds.derive_seed(anchor, seeds.replica_label("probe", 1))
        with self.assertRaises(ValueError):
            seeds.generate_variant_seeds(anchor, "probe", count=1, excluded=frozenset({first_seed}))
        # Without the injected exclusion the same stream is fine.
        self.assertEqual(seeds.generate_variant_seeds(anchor, "probe", count=1, excluded=frozenset()), [first_seed])

    def test_cross_variant_uniqueness_enforced(self):
        # 10 replicas x 4 variants from one anchor must be globally unique.
        record = seeds.seed_record()
        all_seeds = [seed for stream in record["seeds"].values() for seed in stream]
        self.assertEqual(len(set(all_seeds)), len(all_seeds))


class RecordTest(unittest.TestCase):
    def test_record_structure_and_digest_stability(self):
        record = seeds.seed_record()
        self.assertEqual(record["rule_id"], "NANOLAB_REPRO_V0_2_DISTRIBUTIONAL")
        self.assertEqual(set(record["seeds"]), {"0b", "11b", "32b", "53b"})
        canonical = json.dumps(
            {
                "seeds": record["seeds"],
                "bootstrap_seeds": record["bootstrap_seeds"],
                "anchor": record["anchor"],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        self.assertEqual(record["record_sha256"], hashlib.sha256(canonical.encode("utf-8")).hexdigest())

    def test_write_seed_record_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "seeds" / "record.json"
            written = seeds.write_seed_record(path)
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(written, loaded)
            self.assertIn("record_sha256", loaded)


class CandidateDocConsistencyTest(unittest.TestCase):
    """The tool must agree with the candidate protocol text (no drift)."""

    def test_document_declares_same_anchor_and_n(self):
        text = CANDIDATE_DOC.read_text(encoding="utf-8")
        self.assertIn('anchor   = "NANOLAB-REPRO-V0.2-R1"', text)
        self.assertIn("N = 10 fresh replicas", text)
        self.assertIn("NANOLAB_REPRO_V0_2_DISTRIBUTIONAL", text)
        for seed in sorted(seeds.HISTORICAL_SEEDS_V1):
            if seed < 0:
                self.assertIn(str(seed), text)
            else:
                self.assertIn(str(seed), text)

    def test_document_declares_frozen_vocabulary(self):
        text = CANDIDATE_DOC.read_text(encoding="utf-8")
        for outcome in ("REPRODUCED", "REPRODUCED_WITH_DEVIATION", "INCONCLUSIVE", "FAILED_TECHNICAL", "MISMATCH"):
            self.assertIn(outcome, text)
        self.assertIn("δ = 0.5", text)


if __name__ == "__main__":
    unittest.main()
