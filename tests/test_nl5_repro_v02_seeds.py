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
            outcome = seeds.generate_variant_seeds(seeds.DEFAULT_ANCHOR, variant, seeds.VARIANT_REPLICAS[variant])
            for seed in outcome["seeds"]:
                self.assertTrue(0 <= seed < 2**31)

    def test_seed_count_contract(self):
        record = seeds.seed_record()
        self.assertEqual(len(record["seeds"]["0b"]), 64)
        self.assertEqual(len(record["seeds"]["32b"]), 64)
        self.assertEqual(len(record["seeds"]["11b"]), 10)
        self.assertEqual(len(record["seeds"]["53b"]), 10)
        total = sum(len(v) for v in record["seeds"].values())
        self.assertEqual(total, 148)
        all_seeds = [s for v in record["seeds"].values() for s in v]
        self.assertEqual(len(set(all_seeds)), 148)
        self.assertEqual(record["fresh_seed_total"], 148)
        self.assertEqual(record["bootstrap_seed_total"], 4)

    def test_bootstrap_isolation(self):
        record = seeds.seed_record()
        fresh = {s for v in record["seeds"].values() for s in v}
        bootstraps = set(record["bootstrap_seeds"].values())
        self.assertEqual(len(bootstraps), 4)
        self.assertEqual(bootstraps & fresh, set())
        self.assertEqual(bootstraps & seeds.HISTORICAL_SEEDS_V1, set())

    def test_tree_collision_continuation_rule(self):
        # Deterministic continuation: a colliding identity is skipped, the next
        # index consumed, the skip recorded (protocol §7, fixed pre-data).
        anchor = "tree-collision-probe"
        first = seeds.derive_seed(anchor, seeds.replica_label("probe", 1))
        second = seeds.derive_seed(anchor, seeds.replica_label("probe", 2))
        outcome = seeds.generate_variant_seeds(
            anchor, "probe", count=1, excluded=frozenset(),
            tree_collision_scan=lambda seed: seed == first,
        )
        self.assertEqual(outcome["seeds"], [second])
        self.assertEqual(outcome["skipped"], [{"index": 1, "seed": first, "reason": "SEED_COLLISION_TREE"}])

    def test_literal_tree_scan_hits_needle(self):
        from nl5.repro_v02_seeds import literal_tree_collision_scan
        root = Path(__file__).resolve().parents[1]
        marker = 20260930  # this literal exists in this test file
        result = literal_tree_collision_scan(root, [marker])
        self.assertEqual(result["collision_count"], 1)
        self.assertTrue(any("test_nl5_repro_v02_seeds.py" in f for f in result["collisions"][str(marker)]))

    def test_deterministic_across_calls(self):
        first = seeds.seed_record()
        second = seeds.seed_record()
        self.assertEqual(first, second)
        self.assertEqual(first["record_sha256"], second["record_sha256"])
        self.assertEqual(first["variant_counts"], {"0b": 64, "32b": 64, "11b": 10, "53b": 10})

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
            self.assertEqual(len(stream), seeds.VARIANT_REPLICAS[variant])
        for variant, seed in record["bootstrap_seeds"].items():
            self.assertNotIn(seed, seeds.HISTORICAL_SEEDS_V1, variant)

    def test_exclusion_list_contains_all_documented_r1_seeds(self):
        documented = {
            -200619630, 319832093, 201004, 202008, 203012,
            204016, 205020, 206024, 902107,
            # B-R1 (EX-NL5-002-B-R1 evidence/frozen_seeds.json)
            510101, 520202, 530303,
            # B-R2 (EX-NL5-002-B-R2 evidence/seeds_frozen.json, per variant)
            410273, 520931, 638257,
            741953, 852607, 963541,
            174329, 285637, 396421,
            507283, 618457, 729613,
            # platform study S001-S010 (PREREGISTRATION_FREEZE_R1)
            1259289227, 1358106528, 1524307444, 601855227, 274288237,
            972234272, 1934775205, 1747973984, 880427736, 744386736,
        }
        self.assertEqual(len(documented), 34)
        self.assertEqual(seeds.HISTORICAL_SEEDS_V1, frozenset(documented))

    def test_generator_refuses_excluded_value(self):
        anchor = "collide-probe"
        # Inject the value the stream will actually produce: the refusal path
        # must trigger whenever any generated seed is excluded.
        first_seed = seeds.derive_seed(anchor, seeds.replica_label("probe", 1))
        with self.assertRaises(seeds.SeedCollisionError):
            seeds.generate_variant_seeds(anchor, "probe", count=1, excluded=frozenset({first_seed}))
        # Without the injected exclusion the same stream is fine.
        clean = seeds.generate_variant_seeds(anchor, "probe", count=1, excluded=frozenset())
        self.assertEqual(clean["seeds"], [first_seed])

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
                "variant_counts": record["variant_counts"],
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
        self.assertIn("N = 64 fresh paired replicas", text)
        self.assertIn("NANOLAB_REPRO_V0_2_DISTRIBUTIONAL", text)
        self.assertIn("candidate revision  = R3", text)
        for seed in sorted(seeds.HISTORICAL_SEEDS_V1):
            self.assertIn(str(seed), text)

    def test_document_pins_paired_bootstrap_and_feasibility_gate(self):
        text = CANDIDATE_DOC.read_text(encoding="utf-8")
        self.assertIn("PAIRED scheme", text)
        self.assertIn("random.Random(bootstrap_seed_v)", text)
        self.assertIn("B = 10 000", text)
        self.assertIn("### 12.3 Mandatory feasibility gate", text)
        self.assertIn("### 12.4 Consistency gate", text)
        self.assertIn("SELECTED_N = 64", text)
        self.assertIn("candidate revision  = R3", text)
        self.assertIn("NOT FROZEN", text)

    def test_document_declares_frozen_vocabulary(self):
        text = CANDIDATE_DOC.read_text(encoding="utf-8")
        for outcome in ("REPRODUCED", "REPRODUCED_WITH_DEVIATION", "INCONCLUSIVE", "FAILED_TECHNICAL", "MISMATCH"):
            self.assertIn(outcome, text)
        self.assertIn("δ = 0.5", text)


if __name__ == "__main__":
    unittest.main()


class FeasibilityGateTest(unittest.TestCase):
    """Pinned §12 gate mechanics (review refresh R-1/R-2)."""

    def test_quantile_linear(self):
        from nl5.repro_v02_feasibility_gate import quantile_linear
        self.assertEqual(quantile_linear([1.0], 0.05), 1.0)
        self.assertEqual(quantile_linear([0.0, 10.0], 0.5), 5.0)
        self.assertAlmostEqual(quantile_linear(sorted([1.0, 2.0, 3.0, 4.0]), 0.25), 1.75)

    def test_pooled_sd_known_values(self):
        from nl5.repro_v02_feasibility_gate import pooled_sd
        # v1 = 1.0, v2 = 4.0 -> pooled = sqrt((2*1 + 2*4) / 4) = sqrt(2.5)
        self.assertAlmostEqual(pooled_sd([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]), 2.5 ** 0.5)

    def test_half_width_shrinks_with_n(self):
        from nl5.repro_v02_feasibility_gate import paired_bootstrap_half_width
        diffs = [0.5, -0.3, 1.2, 0.0, -0.8, 0.4, 2.1, -1.0, 0.7, 0.2]
        w10 = paired_bootstrap_half_width(diffs, 42, 10, blocks=2000)
        w40 = paired_bootstrap_half_width(diffs, 42, 40, blocks=2000)
        self.assertLess(w40, w10)

    def test_evaluate_variant_gate_fields(self):
        from nl5.repro_v02_feasibility_gate import evaluate_variant
        res = evaluate_variant([1.0, 2.0, 3.0, 4.0] * 2 + [1.5, 2.5, 3.5, 4.5] + [2.0, 1.0],
                               [1.2, 2.2, 3.2, 4.2] * 2 + [1.7, 2.7, 3.7, 4.7] + [2.2, 1.2],
                               bootstrap_seed=7)
        for key in ("s", "s_eff", "margin", "ratio_subsample", "ratio_sqrt_extrapolated", "gate_pass"):
            self.assertIn(key, res)
        self.assertEqual(res["gate_pass"], res["ratio_subsample"] <= 1.0)


class FreezeConsistencyGateTest(unittest.TestCase):
    """Protocol N == record N == budget N == N_min (mission §11)."""

    def test_pass_on_consistent_package(self):
        from nl5.repro_v02_freeze_gate import freeze_consistency_gate
        record = seeds.seed_record()
        text = CANDIDATE_DOC.read_text(encoding="utf-8")
        result = freeze_consistency_gate(text, record)
        self.assertEqual(result["gate"], "PASS", result["failures"])
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["budget"]["confirmatory_runs"], 296)
        self.assertEqual(result["budget"]["max_runs"], 356)

    def test_fail_on_record_mismatch(self):
        from nl5.repro_v02_freeze_gate import freeze_consistency_gate
        record = seeds.seed_record()
        record["variant_counts"]["0b"] = 10  # the R1/R2-era defect class
        record["seeds"]["0b"] = record["seeds"]["0b"][:10]
        text = CANDIDATE_DOC.read_text(encoding="utf-8")
        result = freeze_consistency_gate(text, record)
        self.assertEqual(result["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("0b" in item for item in result["failures"]))

    def test_fail_on_protocol_mismatch(self):
        from nl5.repro_v02_freeze_gate import freeze_consistency_gate
        record = seeds.seed_record()
        result = freeze_consistency_gate("0b = 40, 32b = 40, 11b = 10, 53b = 10", record)
        # protocol literal 40 (grid minimum) vs contract 64 -> FAIL
        self.assertEqual(result["gate"], "FREEZE_GATE_FAIL")


class NGridDeterminismTest(unittest.TestCase):
    """Mission §21: N-grid deterministic, selected-N deterministic, headroom 0.80."""

    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from nl5.repro_v02_feasibility_gate import run_n_grid
        from nl5.repro_v02_seeds import seed_record
        cls.run_n_grid = staticmethod(run_n_grid)
        rec = seed_record()
        cls.bootstrap_seeds = {v: rec["bootstrap_seeds"][v] for v in ("0b", "32b")}
        cls.src = (Path(__file__).resolve().parents[1] / "docs" / "work" /
                   "executions" / "EX-NL5-002-E-R1" / "evidence" / "paired" /
                   "paired_platform_sensitivity.json").resolve()

    def test_n_grid_constant_matches_protocol(self):
        from nl5.repro_v02_feasibility_gate import N_GRID, HEADROOM_RATIO
        self.assertEqual(N_GRID, (40, 48, 64, 80, 96, 128))
        self.assertEqual(HEADROOM_RATIO, 0.80)

    def test_n_grid_deterministic(self):
        first = self.run_n_grid(self.src, self.bootstrap_seeds, ["0b", "32b"])
        second = self.run_n_grid(self.src, self.bootstrap_seeds, ["0b", "32b"])
        self.assertEqual(first["grid"], second["grid"])
        self.assertEqual(first["selected_n"], second["selected_n"])

    def test_selected_n_deterministic_and_documented(self):
        result = self.run_n_grid(self.src, self.bootstrap_seeds, ["0b", "32b"])
        self.assertEqual(result["selected_n"], 64)
        self.assertIn("SELECTED_N = 64", CANDIDATE_DOC.read_text(encoding="utf-8"))
        ratios = result["grid"][2]["variants"]  # N=64 row
        for item in ratios.values():
            self.assertLessEqual(item["ratio_decision"], 0.80)

    def test_gate_boundary_080_inclusive(self):
        from nl5.repro_v02_feasibility_gate import HEADROOM_RATIO
        self.assertTrue(0.80 <= HEADROOM_RATIO)  # boundary semantics: <= passes
        self.assertFalse(0.800001 <= HEADROOM_RATIO)
        grid = self.run_n_grid(self.src, self.bootstrap_seeds, ["0b", "32b"])["grid"]
        for row in grid:
            expected = all(v["ratio_decision"] <= 0.80 for v in row["variants"].values())
            self.assertEqual(row["passes_headroom_all_variants"], expected)
