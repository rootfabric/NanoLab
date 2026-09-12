"""Equivalence tests for the bucketed reference-pairs algorithm (EX-NL3-002-PILOT-R1).

WO-NL3-002-PILOT allows an additive bucketed implementation of the frozen
reference-pairs definition for the 8378-nucleotide 0b subject when the naive
O(N^2) loop is impractical; equivalence with the frozen naive definition is
asserted here on the deterministic synthetic fixtures (fixtures.build),
including periodic (minimum-image) placements that force wrap-around.
"""
import unittest

from e2.fixtures import build
from e2.observables import reference_pairs, reference_pairs_bucketed
from hinge_family.oxdna_conf import Configuration
from hinge_family.oxdna_topology import Topology


def _conf_from_text(text):
    return Configuration.parse(text)


def _topo_from_text(text):
    return Topology.parse(text)


class BucketedReferencePairsEquivalence(unittest.TestCase):
    def _check(self, fixture):
        topology = Topology.parse(fixture["topology_text"])
        for frame_text in fixture["frame_texts"]:
            conf = _conf_from_text(frame_text)
            naive = reference_pairs(conf, topology)
            bucketed = reference_pairs_bucketed(conf, topology)
            self.assertEqual(
                naive, bucketed, "bucketed reference pairs differ from naive definition"
            )

    def test_parallel_fixture(self):
        self._check(build(mode="parallel", arm_len=12, n_frames=2))

    def test_angled_fixture_with_brace(self):
        self._check(build(angle_deg=70.0, mode="angled", arm_len=14, n_frames=1))

    def test_broken_fixture(self):
        self._check(build(mode="parallel", arm_len=10, n_frames=1, broken=True))

    def test_wrapped_positions(self):
        # shift a fixture into the box corner so several minimum-image deltas
        # wrap around the periodic boundary before comparing the algorithms
        fixture = build(mode="angled", angle_deg=40.0, arm_len=16, n_frames=1)
        topology = Topology.parse(fixture["topology_text"])
        conf = Configuration.parse(fixture["frame_texts"][0])
        for i, particle in enumerate(conf.particles):
            pos = particle[0]
            conf.particles[i] = (
                (pos[0] - 60.0, pos[1] - 60.0, pos[2] - 60.0),
                particle[1],
                particle[2],
            )
        naive = reference_pairs(conf, topology)
        bucketed = reference_pairs_bucketed(conf, topology)
        self.assertEqual(naive, bucketed)


if __name__ == "__main__":
    unittest.main()
