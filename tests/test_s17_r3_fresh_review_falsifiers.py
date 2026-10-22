"""Independent R3 adversarial falsifiers for exact PR #60 implementation.

Review-only branch created from 2cf8297f10ab5ec98b8c8023ff76b39d92ef398b.
These are intentionally *negative* expectations. A failure means the original
assembler accepts something its fail-closed contract should prohibit (or
miscomputes a geometric check). NEVER MERGE this temporary review branch.

No MD, physical experiments, external network, or scientific computations.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.test_s17_r3_assembly import Fixture
from knowledge_pack import assembly_spec as aps


class TestR3AdversarialFalsifiers(unittest.TestCase):
    """Each expectation is a proposed fail-closed invariant, not a claimed PASS."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.fx = Fixture(Path(self.temp.name))
        self.spec = self.fx.assembly_spec()
        self.parts = {
            "driver": self.fx.component_spec("driver"),
            "follower": self.fx.component_spec("follower"),
        }

    def tearDown(self):
        self.temp.cleanup()

    def assemble(self):
        return aps.assemble(self.spec, self.parts, self.fx.inputs())

    def test_f01_non_capable_unknown_port_must_not_assemble(self):
        """A declared non-connectable port must block even with concrete structures."""
        port = self.parts["driver"]["ports"][0]
        port["anchors"] = [{
            "namespace": "syn_driver",
            "index_space": "0-based particle index",
            "anchor": "UNKNOWN",
            "status": "UNKNOWN",
        }]
        port["orientation"] = {"status": "UNKNOWN"}
        port["connection_capable"] = False
        self.assertEqual([], __import__("knowledge_pack.mechanical_component_spec",
                                         fromlist=["validate_component_spec"])
                         .validate_component_spec(self.parts["driver"]))
        receipt = self.assemble()
        self.assertNotEqual(
            receipt["assembly_status"], "ASSEMBLED_STATIC_ONLY",
            "F01: assembler accepted connection_capable=false and UNKNOWN anchor/orientation",
        )

    def test_f02_source_verified_must_verify_recipe_bytes(self):
        """A forged source recipe pointer must not authorize SOURCE_VERIFIED."""
        self.spec = self.fx.assembly_spec(mode="SOURCE_VERIFIED")
        self.spec["interface_recipe_ref"] = {
            "path": "missing-definitely-not-present-recipe.json",
            "sha256": "a" * 64,
            "status": "SOURCE_CONFIRMED",
        }
        receipt = self.assemble()
        self.assertNotEqual(
            receipt["assembly_status"], "ASSEMBLED_STATIC_ONLY",
            "F02: SOURCE_VERIFIED accepted missing recipe file and unverified claimed digest",
        )

    def test_f03_rotated_anchor_geometry_must_use_rotation(self):
        """A geometrically valid transformed anchor pair must not be rejected."""
        self.spec["connections"] = self.spec["connections"][:1]
        self.spec["coordinate_transforms"] = [{
            "component": "follower",
            "rotation_axis": [0, 0, 1],
            "rotation_angle_deg": 90.0,
            "translation": [20.0, 20.0, 0.0],
        }]
        self.spec["assembly_box"] = [60.0, 60.0, 20.0]
        # Actual transformed follower A = (11.5, 29, 5); driver A = (12,5,5).
        # True minimum-image anchor separation: sqrt(0.5^2 + 24^2) ~24.005.
        # Buggy pre-rotation hint gives (29,28.5,5), separation ~29.005.
        self.spec["geometry"]["connected_anchor_distance_range"] = [23.5, 24.5]
        receipt = self.assemble()
        self.assertEqual(
            "ASSEMBLED_STATIC_ONLY", receipt["assembly_status"],
            f"F03: valid rotated anchor geometry was falsely rejected: {receipt}",
        )

    def test_f04_hybridization_must_bind_exposed_overhang_segment(self):
        """Complementary internal/full ODN sequence cannot mask mismatched overhangs."""
        dchem = self.parts["driver"]["ports"][0]["chemistry"]
        fchem = self.parts["follower"]["ports"][0]["chemistry"]
        dchem["overhang_segment"] = "A" * 20
        fchem["overhang_segment"] = "C" * 20
        dchem["overhang_end"] = "3p"
        fchem["overhang_end"] = "3p"
        # The complete synthetic sequences are complementary, but the declared
        # protruding segments are not. The assembler must reject this mismatch.
        receipt = self.assemble()
        self.assertNotEqual(
            "ASSEMBLED_STATIC_ONLY", receipt["assembly_status"],
            "F04: assembler approved an internal/full-ODN match despite mismatched exposed overhangs",
        )


if __name__ == "__main__":
    unittest.main()
