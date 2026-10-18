"""Tests for the AssemblySpec v1 contract and the static two-component assembler.

WO-PREP-S17-R3 stage D. Positive cases prove deterministic static assembly of
two synthetic DNA parts (topology/config merge, strand renumbering, transforms,
unit conversion, hybridization records). The negative-control matrix proves a
deterministic refusal for every invalid case class: tampered pins, incompatible
ports, bad indices, ID reuse, backbone corruption, polarity/orientation errors,
unknown sequences, incompatible complementarity, unit mismatches, missing
coordinates, geometric conflicts, a missing follower, an unproven recipe,
incompatible versions, rights violations and tampered inputs.

Static assembly is ``ASSEMBLED_STATIC_ONLY`` and never ``ASSEMBLY_VALIDATED``;
the coarse geometry scan reports ``GEOMETRY_UNVERIFIED`` even when it finds no
conflict.
"""
from __future__ import annotations

import copy
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

from hinge_family.oxdna_conf import Configuration
from hinge_family.oxdna_topology import Topology
from knowledge_pack import assembly_spec as aps
from knowledge_pack import mechanical_component_spec as mcs

SEQ_A = "ACGTGACTGGAGTTCATCGA"
SEQ_C = "TTGACCTAGGACGATCAGGT"


def lin_topology_text(strands: list[tuple[int, str]]) -> str:
    """oxDNA .top text: strands listed 3'->5', contiguous 1-based strand ids.

    n3/n5 are *global* 0-based neighbour indices (-1 = none); a linear strand's
    first row has n3=-1 and its last row has n5=-1.
    """
    rows: list[tuple[int, str, int, int]] = []
    offset = 0
    for sid, seq in strands:
        n = len(seq)
        for pos, base in enumerate(seq):
            n3 = offset + pos - 1 if pos > 0 else -1
            n5 = offset + pos + 1 if pos < n - 1 else -1
            rows.append((sid, base, n3, n5))
        offset += n
    header = f"{len(rows)} {len(strands)}\n"
    return header + "".join(f"{sid} {b} {n3} {n5}\n" for (sid, b, n3, n5) in rows)


def config_text(positions: list[tuple[float, float, float]], box=(45.0, 12.0, 12.0), time="0") -> str:
    lines = [f"t = {time}", f"b = {box[0]} {box[1]} {box[2]}", "E = 0 0 0"]
    for (x, y, z) in positions:
        cols = [x, y, z, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        lines.append(" ".join(f"{v}" for v in cols))
    return "\n".join(lines) + "\n"


DRIVER_STRANDS = [
    (1, "ACGTACGTACGT"),  # 12 nt
    (2, "GGCCAA TT".replace(" ", "")),  # 8 nt
    (3, "TTAACC"),  # 6 nt
]
FOLLOWER_STRANDS = [
    (1, "AAAACCCCGG"),  # 10 nt
    (2, "TTGGCCAA"),  # 8 nt
]
DRIVER_N = sum(len(s[1]) for s in DRIVER_STRANDS)
FOLLOWER_N = sum(len(s[1]) for s in FOLLOWER_STRANDS)


class Fixture:
    """Writes synthetic component files + specs into a temp dir."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.driver_top = tmp / "driver.top"
        self.driver_conf = tmp / "driver.dat"
        self.follower_top = tmp / "follower.top"
        self.follower_conf = tmp / "follower.dat"
        self.driver_top.write_text(lin_topology_text(DRIVER_STRANDS), encoding="utf-8")
        self.follower_top.write_text(lin_topology_text(FOLLOWER_STRANDS), encoding="utf-8")
        self.driver_conf.write_text(
            config_text([(i + 1.0, 5.0, 5.0) for i in range(DRIVER_N)]), encoding="utf-8"
        )
        self.follower_conf.write_text(
            config_text([(i + 1.0, 8.5, 5.0) for i in range(FOLLOWER_N)]), encoding="utf-8"
        )

    @staticmethod
    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def component_spec(self, role: str) -> dict:
        top_path = self.driver_top if role == "driver" else self.follower_top
        conf_path = self.driver_conf if role == "driver" else self.follower_conf
        n = DRIVER_N if role == "driver" else FOLLOWER_N
        strands = DRIVER_STRANDS if role == "driver" else FOLLOWER_STRANDS
        seq = "seq-driver" if role == "driver" else "seq-follower"
        spec = {
            "schema_version": 1,
            "kind": "mechanical_component_spec",
            "spec_version": "v1",
            "component_id": f"SYN-{role.upper()}",
            "version": "1.0.0",
            "source_id": "SYNTHETIC",
            "knowledge_pack_ref": {
                "pack_id": "SYN",
                "pack_path": "nowhere.json",
                "pack_sha256": "0" * 64,
            },
            "source_pin": {
                "role": "SYNTHETIC",
                "url": f"https://example.org/{role}.top",
                "sha256": "a" * 64,
                "status": "SOURCE_CONFIRMED",
                "license": "synthetic test fixture (no external source)",
            },
            "claim_level": "PINNED_IMPORT_VERIFIED",
            "topology": {
                "uri": str(top_path),
                "sha256": self.sha(top_path),
                "nucleotides": n,
                "strand_count": len(strands),
                "status": "SOURCE_CONFIRMED",
            },
            "configuration": {
                "uri": str(conf_path),
                "sha256": self.sha(conf_path),
                "nucleotides": n,
                "strand_count": len(strands),
                "status": "SOURCE_CONFIRMED",
            },
            "molecular_namespaces": {
                f"syn_{role}": {
                    "index_space": "0-based particle index",
                    "particle_count": n,
                    "topology_sha256": self.sha(top_path),
                },
            },
            "local_frame": {"status": "INFERRED_CANDIDATE", "origin": "particle 0", "axes": "config axes", "units": "oxDNA"},
            "ports": [],
            "mechanical_dofs": [
                {"dof_id": "rigid", "kind": "RIGID_BODY", "status": "INFERRED_CANDIDATE"}
            ],
            "model_and_units": {
                "model": "oxDNA2 (synthetic)",
                "length_unit": "oxDNA_length_unit",
                "compatible_conditions": ["test"],
            },
            "unverified_fields": ["local_frame"],
            "known_limitations": ["synthetic fixture - not a published structure"],
        }
        anchor = 11 if role == "driver" else 8
        spec["ports"] = [
            {
                "port_id": f"p-{role}-A",
                "role": role,
                "interface_type": "SS_DNA_OVERHANG_HYBRIDIZATION",
                "anchors": [{"namespace": f"syn_{role}", "index_space": "0-based", "anchor": anchor, "status": "SOURCE_CONFIRMED"}],
                "orientation": {"status": "SOURCE_CONFIRMED", "note": "fixture"},
                "chemistry": {
                    "kind": "DNA_HYBRIDIZATION",
                    "sequence": SEQ_A if role == "driver" else aps.reverse_complement(SEQ_A),
                    "lna": False,
                },
                "connection_capable": True,
                "status": "SOURCE_CONFIRMED",
            },
            {
                "port_id": f"p-{role}-C",
                "role": role,
                "interface_type": "SS_DNA_OVERHANG_HYBRIDIZATION",
                "anchors": [{"namespace": f"syn_{role}", "index_space": "0-based", "anchor": anchor + 1, "status": "SOURCE_CONFIRMED"}],
                "orientation": {"status": "SOURCE_CONFIRMED", "note": "fixture"},
                "chemistry": {
                    "kind": "DNA_HYBRIDIZATION",
                    "sequence": SEQ_C if role == "driver" else aps.reverse_complement(SEQ_C),
                    "lna": False,
                },
                "connection_capable": True,
                "status": "SOURCE_CONFIRMED",
            },
        ]
        return spec

    def assembly_spec(self, mode: str = "CANDIDATE_DESIGN") -> dict:
        driver = self.component_spec("driver")
        follower = self.component_spec("follower")
        return {
            "schema_version": 1,
            "kind": "assembly_spec",
            "spec_version": "v1",
            "assembly_id": "SYN-DF-1",
            "mode": mode,
            "design_basis": "PUBLISHED_SOURCE" if mode == "SOURCE_VERIFIED" else "HYPOTHESIS",
            "claim_level": "PINNED_IMPORT_VERIFIED",
            "knowledge_pack_ref": {
                "pack_id": "SYN",
                "pack_path": "nowhere.json",
                "pack_sha256": "0" * 64,
            },
            "components": [
                {
                    "role": "driver",
                    "component_id": driver["component_id"],
                    "version": driver["version"],
                    "topology_sha256": driver["topology"]["sha256"],
                    "port_geometry": [
                        {"port_id": "p-driver-A", "anchor_position": [12.0, 5.0, 5.0]},
                        {"port_id": "p-driver-C", "anchor_position": [13.0, 5.0, 5.0]},
                    ],
                },
                {
                    "role": "follower",
                    "component_id": follower["component_id"],
                    "version": follower["version"],
                    "topology_sha256": follower["topology"]["sha256"],
                    "port_geometry": [
                        {"port_id": "p-follower-A", "anchor_position": [9.0, 8.5, 5.0]},
                        {"port_id": "p-follower-C", "anchor_position": [10.0, 8.5, 5.0]},
                    ],
                },
            ],
            "coordinate_transforms": [
                {"component": "follower", "translation": [20.0, 0.0, 0.0]}
            ],
            "unit_conversion": None,
            "connections": [
                {
                    "connection_id": "c1",
                    "kind": "SS_DNA_OVERHANG_HYBRIDIZATION",
                    "driver_port": "p-driver-A",
                    "follower_port": "p-follower-A",
                    "evidence_status": "SOURCE_CONFIRMED" if mode == "SOURCE_VERIFIED" else "INFERRED_CANDIDATE",
                },
                {
                    "connection_id": "c2",
                    "kind": "SS_DNA_OVERHANG_HYBRIDIZATION",
                    "driver_port": "p-driver-C",
                    "follower_port": "p-follower-C",
                    "evidence_status": "SOURCE_CONFIRMED" if mode == "SOURCE_VERIFIED" else "INFERRED_CANDIDATE",
                },
            ],
            "allowed_backbone_edits": [],
            "geometry": {
                "enabled": True,
                "connected_anchor_distance_range": [10.0, 30.0],
                "clash_scan_threshold": 0.5,
            },
            "expected_units": {"length_unit": "oxDNA_length_unit"},
            "notes": "synthetic two-part assembly test",
        }

    def inputs(self) -> dict:
        return {
            "driver": {"topology_path": self.driver_top, "configuration_path": self.driver_conf},
            "follower": {"topology_path": self.follower_top, "configuration_path": self.follower_conf},
        }


class TestPositiveAssembly(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(Path(self._tmp.name))
        self.spec = self.fx.assembly_spec()
        self.components = {
            "driver": self.fx.component_spec("driver"),
            "follower": self.fx.component_spec("follower"),
        }

    def tearDown(self):
        self._tmp.cleanup()

    def test_candidate_design_assembles_deterministically(self):
        receipt = aps.assemble(self.spec, self.components, self.fx.inputs())
        self.assertEqual(receipt["assembly_status"], "ASSEMBLED_STATIC_ONLY", receipt["reason"])
        self.assertEqual(receipt["geometry_status"], "GEOMETRY_UNVERIFIED")
        self.assertEqual(receipt["mode"], "CANDIDATE_DESIGN")
        self.assertEqual(receipt["assembled"]["nucleotides"], DRIVER_N + FOLLOWER_N)
        self.assertEqual(receipt["assembled"]["strands"], 5)
        receipt2 = aps.assemble(self.spec, self.components, self.fx.inputs())
        self.assertEqual(receipt, receipt2)

    def test_artifacts_are_valid_oxdna_and_deterministic(self):
        top_text, conf_text, receipt = aps.assemble_artifacts(
            self.spec, self.components, self.fx.inputs()
        )
        self.assertEqual(receipt["assembly_status"], "ASSEMBLED_STATIC_ONLY")
        top = Topology.parse(top_text)
        top.check_chain_integrity()
        conf = Configuration.parse(conf_text)
        self.assertEqual(top.nucleotides, DRIVER_N + FOLLOWER_N)
        self.assertEqual(len(conf.particles), DRIVER_N + FOLLOWER_N)
        # follower strand ids are renumbered after the driver's strands
        ids = [row[0] for row in top.rows]
        runs = []
        for sid in ids:
            if not runs or runs[-1] != sid:
                runs.append(sid)
        self.assertEqual(runs, [1, 2, 3, 4, 5])
        # follower particle indices are offset by the driver size: the first
        # follower nucleotide's n5 neighbour is the next follower nucleotide
        self.assertEqual(top.rows[DRIVER_N][3], DRIVER_N + 1)
        top2, conf2, _ = aps.assemble_artifacts(self.spec, self.components, self.fx.inputs())
        self.assertEqual(top_text, top2)
        self.assertEqual(conf_text, conf2)
        self.assertEqual(
            hashlib.sha256(top_text.encode()).hexdigest(),
            receipt["assembled"]["topology_text_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(conf_text.encode()).hexdigest(),
            receipt["assembled"]["configuration_text_sha256"],
        )

    def test_hybridization_records_are_non_covalent(self):
        _top, _conf, receipt = aps.assemble_artifacts(self.spec, self.components, self.fx.inputs())
        self.assertEqual(len(receipt["connections"]), 2)
        for conn in receipt["connections"]:
            self.assertFalse(conn["covalent"])
            self.assertEqual(conn["complementarity_match_nt"], 20)
        self.assertEqual(receipt["backbone_edits_applied"], [])

    def test_unit_conversion_applies_deterministically(self):
        spec = self.spec
        self.components["follower"]["model_and_units"]["length_unit"] = "nm"
        spec["unit_conversion"] = {
            "component": "follower",
            "from_unit": "nm",
            "to_unit": "oxDNA_length_unit",
            "length_factor": 1 / 0.8518,
            "source": "0.8518 nm per oxDNA length unit (EX-PREP-S17-R2, r0 = 8.8 units = 7.496 nm)",
        }
        # widen the anchor band: the follower coordinates shrink by ~0.85x
        spec["components"][1]["port_geometry"] = [
            {"port_id": "p-follower-A", "anchor_position": [7.7, 7.3, 4.3]},
            {"port_id": "p-follower-C", "anchor_position": [8.5, 7.3, 4.3]},
        ]
        receipt = aps.assemble(spec, self.components, self.fx.inputs())
        self.assertEqual(receipt["assembly_status"], "ASSEMBLED_STATIC_ONLY", receipt["reason"])
        _top, conf_text, _ = aps.assemble_artifacts(spec, self.components, self.fx.inputs())
        conf = Configuration.parse(conf_text)
        follower_x = [p[0][0] for p in conf.particles[DRIVER_N:]]
        self.assertAlmostEqual(follower_x[0], (1.0 / 0.8518) + 20.0, places=5)

    def test_no_transform_translation_only_identity(self):
        spec = self.spec
        spec["coordinate_transforms"] = [{"component": "follower", "translation": [0.0, 0.0, 0.0]}]
        spec["geometry"] = {"enabled": True}
        receipt = aps.assemble(spec, self.components, self.fx.inputs())
        self.assertEqual(receipt["assembly_status"], "ASSEMBLED_STATIC_ONLY", receipt["reason"])


class TestNegativeControls(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(Path(self._tmp.name))
        self.spec = self.fx.assembly_spec()
        self.components = {
            "driver": self.fx.component_spec("driver"),
            "follower": self.fx.component_spec("follower"),
        }

    def tearDown(self):
        self._tmp.cleanup()

    def _assemble(self):
        return aps.assemble(self.spec, self.components, self.fx.inputs())

    def test_missing_follower_spec(self):
        receipt = aps.assemble(self.spec, {"driver": self.components["driver"]}, self.fx.inputs())
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")
        self.assertEqual(receipt["geometry_status"], "NOT_PERFORMED")

    def test_duplicate_component_identity(self):
        self.components["follower"]["component_id"] = self.components["driver"]["component_id"]
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")
        self.assertIn("distinct identities", receipt["reason"])

    def test_incompatible_versions(self):
        self.spec["components"][1]["version"] = "2.0.0"
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")
        self.assertTrue(any("version" in e for e in receipt["reason"].split(";")))

    def test_tampered_topology_input(self):
        inputs = self.fx.inputs()
        path = Path(inputs["follower"]["topology_path"])
        path.write_text(path.read_text().replace("A", "T"), encoding="utf-8")
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_INPUT")
        self.assertIn("pinned sha256", receipt["reason"])

    def test_tampered_configuration_input(self):
        inputs = self.fx.inputs()
        path = Path(inputs["driver"]["configuration_path"])
        path.write_text(path.read_text().replace("5.0", "5.5"), encoding="utf-8")
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_INPUT")

    def test_broken_backbone_connectivity(self):
        inputs = self.fx.inputs()
        path = Path(inputs["follower"]["topology_path"])
        broken = lin_topology_text(FOLLOWER_STRANDS).splitlines()
        # break the n5 link of the first follower nucleotide to its successor
        parts = broken[2].split()
        parts[3] = "-1"
        broken[2] = " ".join(parts)
        path.write_text("\n".join(broken) + "\n", encoding="utf-8")
        self.components["follower"]["topology"]["sha256"] = self.fx.sha(path)
        self.spec["components"][1]["topology_sha256"] = self.fx.sha(path)
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_INPUT")
        self.assertIn("chain", receipt["reason"])

    def test_incompatible_molecular_ports_interface_type(self):
        self.components["follower"]["ports"][0]["interface_type"] = "BASE_STACKING"
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")
        self.assertIn("incompatible", receipt["reason"])

    def test_incompatible_complementarity(self):
        self.components["follower"]["ports"][0]["chemistry"]["sequence"] = SEQ_C  # not rc(SEQ_A)
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_INFERRED_INTERFACE")
        self.assertIn("not complementary", receipt["reason"])

    def test_wrong_polarity_same_direction_sequence(self):
        self.components["follower"]["ports"][0]["chemistry"]["sequence"] = SEQ_A  # ==, not rc
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_INFERRED_INTERFACE")

    def test_unknown_sequence(self):
        self.components["follower"]["ports"][0]["chemistry"]["sequence"] = "UNKNOWN"
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_INFERRED_INTERFACE")
        self.assertIn("UNKNOWN", receipt["reason"])

    def test_invalid_anchor_index_out_of_bounds(self):
        self.components["driver"]["ports"][0]["anchors"][0]["anchor"] = DRIVER_N  # == count
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")
        self.assertIn("outside", receipt["reason"])

    def test_negative_anchor_index(self):
        self.components["driver"]["ports"][0]["anchors"][0]["anchor"] = -3
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")
        self.assertIn("outside", receipt["reason"])

    def test_inconsistent_units_without_conversion(self):
        self.components["follower"]["model_and_units"]["length_unit"] = "nm"
        errors = aps.validate_assembly_spec(self.spec, self.components)
        self.assertTrue(any("unit" in e for e in errors))
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")

    def test_unknown_units_with_concrete_topology(self):
        self.components["follower"]["model_and_units"]["length_unit"] = "UNKNOWN"
        errors = aps.validate_assembly_spec(self.spec, self.components)
        self.assertTrue(any("UNKNOWN" in e and "units" in e for e in errors))

    def test_wrong_conversion_semantics(self):
        self.components["follower"]["model_and_units"]["length_unit"] = "nm"
        self.spec["unit_conversion"] = {
            "component": "follower",
            "from_unit": "oxDNA_length_unit",
            "to_unit": "oxDNA_length_unit",
            "length_factor": 1.0,
            "source": "bogus",
        }
        errors = aps.validate_assembly_spec(self.spec, self.components)
        self.assertTrue(any("from_unit" in e for e in errors))

    def test_missing_coordinates(self):
        self.components["follower"]["configuration"] = {
            "uri": "UNKNOWN", "sha256": "UNKNOWN", "nucleotides": "UNKNOWN",
            "strand_count": "UNKNOWN", "status": "UNKNOWN",
        }
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "NOT_RECONSTRUCTED")
        self.assertTrue(any("configuration" in b for b in receipt["blocked_inputs"]))

    def test_missing_follower_structure(self):
        self.components["follower"]["topology"] = {
            "uri": "UNKNOWN", "sha256": "UNKNOWN", "nucleotides": "UNKNOWN",
            "strand_count": "UNKNOWN", "status": "UNKNOWN",
        }
        self.spec["components"][1]["topology_sha256"] = "UNKNOWN"
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "NOT_RECONSTRUCTED")
        self.assertTrue(any("topology" in b and "follower" in b for b in receipt["blocked_inputs"]))

    def test_geometry_conflict_anchor_distance(self):
        self.spec["geometry"]["connected_anchor_distance_range"] = [100.0, 200.0]
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_GEOMETRY")
        self.assertEqual(receipt["geometry_status"], "GEOMETRIC_CONFLICT")
        self.assertIn("outside declared band", receipt["geometry"]["violation"])

    def test_geometry_conflict_clash(self):
        self.spec["geometry"]["clash_scan_threshold"] = 50.0  # everything clashes
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_GEOMETRY")
        self.assertEqual(receipt["geometry_status"], "GEOMETRIC_CONFLICT")
        self.assertGreater(
            receipt["geometry"]["clash_scan"]["overlapping_pairs"], 0
        )

    def test_merged_positions_outside_box(self):
        self.spec["assembly_box"] = [10.0, 10.0, 10.0]
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_GEOMETRY")
        self.assertIn("outside the declared assembly box", receipt["reason"])

    def test_source_verified_requires_recipe(self):
        spec = self.fx.assembly_spec(mode="SOURCE_VERIFIED")
        errors = aps.validate_assembly_spec(spec, self.components)
        self.assertTrue(any("interface_recipe_ref" in e for e in errors))
        receipt = aps.assemble(spec, self.components, self.fx.inputs())
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")

    def test_source_verified_rejects_inferred_recipe_status(self):
        spec = self.fx.assembly_spec(mode="SOURCE_VERIFIED")
        spec["interface_recipe_ref"] = {
            "path": "recipe.json",
            "sha256": "a" * 64,
            "status": "INFERRED_CANDIDATE",
        }
        errors = aps.validate_assembly_spec(spec, self.components)
        self.assertTrue(any("SOURCE_CONFIRMED" in e for e in errors))
        receipt = aps.assemble(spec, self.components, self.fx.inputs())
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")

    def test_source_verified_rejects_non_confirmed_connection_evidence(self):
        spec = self.fx.assembly_spec(mode="SOURCE_VERIFIED")
        spec["interface_recipe_ref"] = {
            "path": "recipe.json",
            "sha256": "a" * 64,
            "status": "SOURCE_CONFIRMED",
        }
        spec["connections"][0]["evidence_status"] = "INFERRED_CANDIDATE"
        errors = aps.validate_assembly_spec(spec, self.components)
        self.assertTrue(any("SOURCE_CONFIRMED" in e for e in errors))

    def test_backbone_edit_requires_allow_list(self):
        self.spec["connections"] = [
            {
                "connection_id": "ce",
                "kind": "BACKBONE_CONTINUATION",
                "driver_port": "p-driver-A",
                "follower_port": "p-follower-A",
                "evidence_status": "INFERRED_CANDIDATE",
                "backbone_edit": {"component": "follower", "particle": 0, "terminal": "3p"},
            }
        ]
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")

    def test_backbone_edit_refused_even_when_allow_listed(self):
        self.spec["connections"] = [
            {
                "connection_id": "ce",
                "kind": "BACKBONE_CONTINUATION",
                "driver_port": "p-driver-A",
                "follower_port": "p-follower-A",
                "evidence_status": "INFERRED_CANDIDATE",
                "backbone_edit": {"component": "follower", "particle": 0, "terminal": "3p"},
            }
        ]
        self.spec["allowed_backbone_edits"] = [
            {"connection_id": "ce", "max_edits": 1}
        ]
        receipt = self._assemble()
        self.assertEqual(receipt["assembly_status"], "BLOCKED_SPEC")
        self.assertIn("refuses covalent edits", receipt["reason"])

    def test_duplicate_connection_ids(self):
        self.spec["connections"][1]["connection_id"] = self.spec["connections"][0]["connection_id"]
        errors = aps.validate_assembly_spec(self.spec, self.components)
        self.assertTrue(any("duplicate" in e for e in errors))

    def test_unknown_port_reference(self):
        self.spec["connections"][0]["follower_port"] = "does-not-exist"
        errors = aps.validate_assembly_spec(self.spec, self.components)
        self.assertTrue(any("does not exist" in e for e in errors))

    def test_spec_corruption_rejected_deterministically(self):
        spec = copy.deepcopy(self.spec)
        spec["kind"] = "other"
        errors = aps.validate_assembly_spec(spec, self.components)
        self.assertTrue(any("kind" in e for e in errors))
        with self.assertRaises(mcs.ComponentSpecError):
            mcs.load_component_spec(self.fx.tmp / "missing.json")


if __name__ == "__main__":
    unittest.main()
