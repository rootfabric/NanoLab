"""Tests for the E2-PROTO-R1 preparation tooling (WO-NL3-002-PROTO).

Covers the v2 base-pair detector (docs/research/E2_OBSERVABLES_R2.md) and
the first-principles arm-manifest derivation (scripts/e2/arm_manifest.py)
on synthetic fixtures with analytically known geometry. Network access is
never needed: the author frame-0 validations live in the execution evidence
(EX-NL3-002-PROTO-R1), not in unittest.
"""
from __future__ import annotations

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from e2.arm_manifest import ArmManifestError, derive_manifest
from e2.canonical import canonical_json
from e2.fixtures import build_pairable
from e2.observables import (
    PAIR_A1_DOT_MAX_V2,
    PAIR_D_MAX_V2,
    PAIR_D_MAX,
    analyse_v2,
    hinge_angle,
    pairs_fraction_v2,
    reference_pairs,
    reference_pairs_v2,
)
from hinge_family.oxdna_conf import ConfError, Configuration
from hinge_family.oxdna_topology import Topology


def load(fx):
    topology = Topology.parse(fx["topology_text"])
    frames = [Configuration.parse(t) for t in fx["frame_texts"]]
    return topology, frames


class V2DetectorTests(unittest.TestCase):
    def test_parallel_pairable_exact_count_and_v1_equivalence(self):
        fx = build_pairable(mode="parallel")
        topology, frames = load(fx)
        pairs_v2 = reference_pairs_v2(frames[0], topology)
        pairs_v1 = reference_pairs(frames[0], topology)
        self.assertEqual(len(pairs_v2), 12)
        self.assertEqual(len(pairs_v1), 12)
        self.assertEqual(
            sorted((p["i"], p["j"]) for p in pairs_v2),
            sorted((p["i"], p["j"]) for p in pairs_v1),
        )
        # every detected pair is in the v2 window with antiparallel a1 axes
        conf = frames[0]
        for pair in pairs_v2:
            self.assertGreater(pair["d_ref"], 0.05)
            self.assertLessEqual(pair["d_ref"], PAIR_D_MAX_V2)
            ai = conf.particles[pair["i"]][1]
            aj = conf.particles[pair["j"]][1]
            dot = sum(ai[k] * aj[k] for k in range(3))
            self.assertLessEqual(dot, PAIR_A1_DOT_MAX_V2)

    def test_determinism_two_runs(self):
        fx = build_pairable(mode="angled", angle_deg=60.0)
        topology, frames = load(fx)
        first = reference_pairs_v2(frames[0], topology)
        second = reference_pairs_v2(frames[0], topology)
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertGreaterEqual(len(first), 3)

    def test_pairs_fraction_v2_intact_and_broken(self):
        fx = build_pairable(mode="parallel", n_frames=1, broken=True)
        topology, frames = load(fx)
        ref_pairs = reference_pairs_v2(frames[0], topology)
        intact = pairs_fraction_v2(frames[0], ref_pairs)
        self.assertEqual(intact["pairs_fraction"], 1.0)
        broken = pairs_fraction_v2(frames[1], ref_pairs)
        self.assertLess(broken["pairs_fraction"], 1.0)

    def test_analyse_v2_report_shape_and_angle(self):
        fx = build_pairable(mode="parallel", n_frames=2)
        topology, frames = load(fx)
        report = analyse_v2(topology, frames, fx["manifest"])
        self.assertEqual(report["schema_version"], 2)
        self.assertIn("v2", report["reference_pairs_detector"])
        self.assertEqual(report["reference_pairs_count"], 12)
        self.assertAlmostEqual(
            report["frames"][0]["hinge_angle"]["angle_deg"], 0.0, places=5
        )
        self.assertEqual(report["frames"][0]["pairs_v2"]["pairs_fraction"], 1.0)
        # canonical byte-determinism
        self.assertEqual(canonical_json(report), canonical_json(analyse_v2(topology, frames, fx["manifest"])))

    def test_greedy_variant_superset_of_mutual(self):
        fx = build_pairable(mode="angled", angle_deg=60.0)
        topology, frames = load(fx)
        mutual = reference_pairs_v2(frames[0], topology, mutual_nearest=True)
        greedy = reference_pairs_v2(frames[0], topology, mutual_nearest=False)
        self.assertGreaterEqual(len(greedy), len(mutual))
        self.assertTrue(
            set((p["i"], p["j"]) for p in mutual)
            <= set((p["i"], p["j"]) for p in greedy)
        )

    def test_v1_functions_untouched_reference_values(self):
        # regression guard: v1 window constants unchanged (frozen R1)
        fx = build_pairable(mode="parallel")
        topology, frames = load(fx)
        pairs = reference_pairs(frames[0], topology)
        for pair in pairs:
            self.assertLessEqual(pair["d_ref"], PAIR_D_MAX)


class ArmManifestTests(unittest.TestCase):
    def test_twoarm_fixture_recovers_known_groups(self):
        fx = build_pairable(mode="twoarm", angle_deg=60.0)
        topology, frames = load(fx)
        report = derive_manifest(frames[0], topology)
        self.assertEqual(
            report["arms"]["arm_a"]["nucleotides"],
            sorted(fx["manifest"]["arm_a"]["nucleotides"]),
        )
        self.assertEqual(
            report["arms"]["arm_b"]["nucleotides"],
            sorted(fx["manifest"]["arm_b"]["nucleotides"]),
        )
        self.assertEqual(report["coverage"]["manifest_fraction_of_paired"], 1.0)
        self.assertTrue(report["validation"]["groups_disjoint"])
        # unsigned axis convention: the 60 deg construction reads as its
        # supplement 120 deg under the R1 sign convention (theta and
        # 180 - theta are indistinguishable pairs)
        angle = report["validation"]["hinge_angle_frame0"]["angle_deg"]
        self.assertTrue(
            math.isclose(angle, 120.0, abs_tol=1e-6)
            or math.isclose(angle, 60.0, abs_tol=1e-6)
        )

    def test_derivation_byte_deterministic(self):
        fx = build_pairable(mode="twoarm", angle_deg=45.0)
        topology, frames = load(fx)
        first = derive_manifest(frames[0], topology)
        second = derive_manifest(frames[0], topology)
        self.assertEqual(canonical_json(first), canonical_json(second))

    def test_single_blob_fixture_fails_closed(self):
        # one duplex only: no second rigid block exists -> fail-closed error
        fx = build_pairable(mode="parallel")
        topology, frames = load(fx)
        with self.assertRaises(ArmManifestError):
            derive_manifest(frames[0], topology)

    def test_truncated_configuration_is_an_error(self):
        fx = build_pairable(mode="twoarm", angle_deg=60.0)
        truncated = fx["frame_texts"][0][: len(fx["frame_texts"][0]) // 2]
        with self.assertRaises(ConfError):
            Configuration.parse(truncated)

    def test_topology_conf_count_mismatch_is_an_error(self):
        fx = build_pairable(mode="twoarm", angle_deg=60.0)
        topology, frames = load(fx)
        other = build_pairable(mode="twoarm", angle_deg=90.0, arm_len=8)
        smaller_top = Topology.parse(other["topology_text"])
        from e2.observables import ObservableError

        with self.assertRaises(ObservableError):
            reference_pairs_v2(frames[0], smaller_top)


if __name__ == "__main__":
    unittest.main()
