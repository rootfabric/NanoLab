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
        # R3-F04 (repair): ports declare their exposed overhang interface
        # explicitly. Driver A exposes SEQ_A at its 3' end; follower A exposes
        # the exact reverse complement at its 5' end (same-end pairs are also
        # legal - the pinned real S17 recipe is 3p/3p - but an *undeclared*
        # end never assembles). Port C repeats the pattern with SEQ_C.
        seq = {"driver": SEQ_A, "follower": aps.reverse_complement(SEQ_A)}
        seq_c = {"driver": SEQ_C, "follower": aps.reverse_complement(SEQ_C)}
        spec["ports"] = [
            {
                "port_id": f"p-{role}-A",
                "role": role,
                "interface_type": "SS_DNA_OVERHANG_HYBRIDIZATION",
                "anchors": [{"namespace": f"syn_{role}", "index_space": "0-based", "anchor": anchor, "status": "SOURCE_CONFIRMED"}],
                "orientation": {"status": "SOURCE_CONFIRMED", "note": "fixture"},
                "chemistry": {
                    "kind": "DNA_HYBRIDIZATION",
                    "odn_name": f"odn-{role}-A",
                    "sequence": seq[role],
                    "overhang_segment": seq[role],
                    "overhang_end": "3p" if role == "driver" else "5p",
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
                    "odn_name": f"odn-{role}-C",
                    "sequence": seq_c[role],
                    "overhang_segment": seq_c[role],
                    "overhang_end": "3p" if role == "driver" else "5p",
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


class TestRepairR1FalsifierMatrix(unittest.TestCase):
    """WO-PREP-S17-R3-REPAIR-R1 extended negative controls (issue #62).

    Every test pins one refusal class introduced or hardened by the repair:
    F01 usable-port gate, F02 interface-recipe verification, F03 rotation-aware
    geometry, F04 exposed-overhang interface binding, plus finite-number and
    input-integrity hardening. The real pinned S17 artifacts keep their honest
    NOT_RECONSTRUCTED verdict (never flipped into a spec error).
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.fx = Fixture(self.tmp)
        self.spec = self.fx.assembly_spec()
        self.parts = {
            "driver": self.fx.component_spec("driver"),
            "follower": self.fx.component_spec("follower"),
        }

    def tearDown(self):
        self._tmp.cleanup()

    def assemble(self):
        return aps.assemble(self.spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)

    # ---------------- R3-F01: usable-port gate ----------------

    def test_f01_capable_false_with_concrete_anchors_blocks(self):
        port = self.parts["driver"]["ports"][0]
        port["connection_capable"] = False
        receipt = self.assemble()
        self.assertEqual("BLOCKED_SPEC", receipt["assembly_status"])
        self.assertIn("connection_capable", receipt["reason"])

    def test_f01_incapable_port_blocks_before_anchor_audit(self):
        """UNKNOWN-status anchors + capable=false: refused on capability first.

        The component validator already forbids capable=true with UNKNOWN
        anchors, so this combination reaches the assembly gate with
        connection_capable=false and is refused on that guarantee.
        """
        port = self.parts["follower"]["ports"][0]
        port["anchors"][0]["status"] = "UNKNOWN"
        port["connection_capable"] = False  # consistent: an UNKNOWN anchor is not usable
        receipt = self.assemble()
        self.assertEqual("BLOCKED_SPEC", receipt["assembly_status"])
        self.assertIn("connection_capable", receipt["reason"])

    def test_f01_unknown_orientation_blocks(self):
        port = self.parts["driver"]["ports"][1]
        port["orientation"] = {"status": "UNKNOWN"}
        port["connection_capable"] = False  # consistent with the unknown orientation
        receipt = self.assemble()
        self.assertEqual("BLOCKED_SPEC", receipt["assembly_status"])
        self.assertIn("connection_capable", receipt["reason"])

    def test_f01_boolean_anchor_index_blocks(self):
        port = self.parts["driver"]["ports"][0]
        port["anchors"][0]["anchor"] = True
        receipt = self.assemble()
        self.assertEqual("BLOCKED_SPEC", receipt["assembly_status"])
        self.assertIn("concrete integer", receipt["reason"])

    def test_f01_string_anchor_index_blocks_in_validation(self):
        self.parts["driver"]["ports"][0]["anchors"][0]["anchor"] = "12"
        errors = mcs.validate_component_spec(self.parts["driver"])
        self.assertTrue(any("anchor" in e for e in errors))
        receipt = self.assemble()
        self.assertEqual("BLOCKED_SPEC", receipt["assembly_status"])
        self.assertIn("anchor", receipt["reason"])

    def test_f01_structureless_pair_keeps_not_reconstructed_over_port_gate(self):
        """A structure-less follower is NOT_RECONSTRUCTED even with incapable ports."""
        self.parts["follower"]["topology"] = {
            "uri": "UNKNOWN", "sha256": "UNKNOWN", "nucleotides": "UNKNOWN",
            "strand_count": "UNKNOWN", "status": "UNKNOWN",
        }
        self.spec["components"][1]["topology_sha256"] = "UNKNOWN"
        dport = self.parts["driver"]["ports"][0]
        dport["connection_capable"] = False
        dport["anchors"] = [{"namespace": "nNE", "index_space": "0-based", "anchor": "UNKNOWN", "status": "UNKNOWN"}]
        dport["orientation"] = {"status": "UNKNOWN"}
        receipt = self.assemble()
        self.assertEqual("NOT_RECONSTRUCTED", receipt["assembly_status"])

    # ---------------- R3-F02: interface-recipe verification ----------------

    RECIPE = {
        "schema_version": 1,
        "kind": "interface_recipe",
        "pairs": [
            {"pair_id": 1, "driver_odn": "odn-driver-A", "follower_odn": "odn-follower-A",
             "driver_segment": SEQ_A, "follower_segment": aps.reverse_complement(SEQ_A)},
            {"pair_id": 2, "driver_odn": "odn-driver-C", "follower_odn": "odn-follower-C",
             "driver_segment": SEQ_C, "follower_segment": aps.reverse_complement(SEQ_C)},
        ],
    }

    def _source_verified_spec(self):
        spec = self.fx.assembly_spec(mode="SOURCE_VERIFIED")
        return spec

    def _write_recipe(self, recipe, name="recipe.json"):
        path = self.tmp / name
        path.write_text(json.dumps(recipe), encoding="utf-8")
        return name, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_f02_missing_recipe_file_blocks_source(self):
        spec = self._source_verified_spec()
        spec["interface_recipe_ref"] = {
            "path": "missing-definitely-not-present-recipe.json",
            "sha256": "a" * 64, "status": "SOURCE_CONFIRMED",
        }
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_SOURCE", receipt["assembly_status"])
        self.assertIn("not found on disk", receipt["reason"])

    def test_f02_forged_digest_blocks_input(self):
        spec = self._source_verified_spec()
        name, real_sha = self._write_recipe(self.RECIPE)
        spec["interface_recipe_ref"] = {"path": name, "sha256": "b" * 64, "status": "SOURCE_CONFIRMED"}
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_INPUT", receipt["assembly_status"])
        self.assertIn("digest mismatch", receipt["reason"])

    def test_f02_non_json_recipe_blocks_input(self):
        path = self.tmp / "recipe.txt"
        path.write_text("this is not json {", encoding="utf-8")
        spec = self._source_verified_spec()
        spec["interface_recipe_ref"] = {
            "path": "recipe.txt",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "status": "SOURCE_CONFIRMED",
        }
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_INPUT", receipt["assembly_status"])

    def test_f02_wrong_recipe_kind_blocks_source(self):
        recipe = dict(self.RECIPE, kind="shopping_list")
        name, sha = self._write_recipe(recipe)
        spec = self._source_verified_spec()
        spec["interface_recipe_ref"] = {"path": name, "sha256": sha, "status": "SOURCE_CONFIRMED"}
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_SOURCE", receipt["assembly_status"])
        self.assertIn("kind", receipt["reason"])

    def test_f02_recipe_not_covering_connections_blocks_source(self):
        recipe = json.loads(json.dumps(self.RECIPE))
        recipe["pairs"][1]["follower_odn"] = "some-other-odn"
        name, sha = self._write_recipe(recipe)
        spec = self._source_verified_spec()
        spec["interface_recipe_ref"] = {"path": name, "sha256": sha, "status": "SOURCE_CONFIRMED"}
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_SOURCE", receipt["assembly_status"])
        self.assertIn("not bound", receipt["reason"])

    def test_f02_recipe_segment_contradicting_port_blocks_source(self):
        recipe = json.loads(json.dumps(self.RECIPE))
        recipe["pairs"][0]["driver_segment"] = "A" * 20
        name, sha = self._write_recipe(recipe)
        spec = self._source_verified_spec()
        spec["interface_recipe_ref"] = {"path": name, "sha256": sha, "status": "SOURCE_CONFIRMED"}
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_SOURCE", receipt["assembly_status"])
        self.assertIn("contradicts", receipt["reason"])

    def test_f02_unsafe_paths_rejected_in_validation(self):
        for bad in ("/etc/passwd", "../../etc/passwd", "a\\b.json", ""):
            spec = self._source_verified_spec()
            spec["interface_recipe_ref"] = {"path": bad, "sha256": "a" * 64, "status": "SOURCE_CONFIRMED"}
            errors = aps.validate_assembly_spec(spec, self.parts)
            self.assertTrue(any("safe relative path" in e for e in errors), bad)

    def test_f02_recipe_path_pointing_to_directory_blocks_source(self):
        spec = self._source_verified_spec()
        spec["interface_recipe_ref"] = {"path": ".", "sha256": "a" * 64, "status": "SOURCE_CONFIRMED"}
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_SOURCE", receipt["assembly_status"])

    def test_f02_verified_recipe_assembles_source_verified(self):
        name, sha = self._write_recipe(self.RECIPE)
        spec = self._source_verified_spec()
        spec["interface_recipe_ref"] = {"path": name, "sha256": sha, "status": "SOURCE_CONFIRMED"}
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])
        self.assertEqual("SOURCE_VERIFIED", receipt["mode"])

    def test_f02_binding_via_explicit_recipe_pair_ref(self):
        recipe = json.loads(json.dumps(self.RECIPE))
        # scramble the odn names: only the explicit ref can bind now
        recipe["pairs"][0]["driver_odn"] = "renamed"
        recipe["pairs"][0]["follower_odn"] = "renamed-too"
        name, sha = self._write_recipe(recipe)
        spec = self._source_verified_spec()
        spec["connections"][0]["recipe_pair_ref"] = 1
        spec["interface_recipe_ref"] = {"path": name, "sha256": sha, "status": "SOURCE_CONFIRMED"}
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])

    # ---------------- R3-F03: rotation-aware geometry ----------------

    def test_f03_90degree_rotation_distance_uses_transform(self):
        spec = self.spec
        spec["connections"] = spec["connections"][:1]
        spec["coordinate_transforms"] = [{
            "component": "follower",
            "rotation_axis": [0, 0, 1],
            "rotation_angle_deg": 90.0,
            "translation": [20.0, 20.0, 0.0],
        }]
        spec["assembly_box"] = [60.0, 60.0, 20.0]
        spec["geometry"]["connected_anchor_distance_range"] = [23.5, 24.5]
        receipt = self.assemble()
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])
        distance = receipt["geometry"]["connected_anchor_distances"][0]["distance"]
        # sqrt(0.5^2 + 24^2) ~ 24.005: the pre-rotation hint gave ~29.005.
        self.assertLess(abs(distance - 24.005), 0.01)

    def test_f03_180degree_rotation_band_only_satisfied_by_rotation(self):
        spec = self.spec
        spec["connections"] = spec["connections"][:1]
        # follower A anchor (9, 8.5, 5) rotated 180 deg about z + translation
        # (30, 30, 0) lands at (21, 21.5, 5): distance to driver A (12, 5, 5)
        # is ~18.79. Without rotation the anchor would be (39, 38.5, 5) with
        # distance ~43.1, far outside the band.
        spec["coordinate_transforms"] = [{
            "component": "follower",
            "rotation_axis": [0, 0, 1],
            "rotation_angle_deg": 180.0,
            "translation": [30.0, 30.0, 0.0],
        }]
        spec["assembly_box"] = [60.0, 60.0, 20.0]
        spec["geometry"]["connected_anchor_distance_range"] = [18.0, 19.5]
        receipt = self.assemble()
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])

    def test_f03_rotated_out_of_band_conflicts(self):
        spec = self.spec
        spec["connections"] = spec["connections"][:1]
        spec["coordinate_transforms"] = [{
            "component": "follower",
            "rotation_axis": [0, 0, 1],
            "rotation_angle_deg": 180.0,
            "translation": [30.0, 30.0, 0.0],
        }]
        spec["assembly_box"] = [60.0, 60.0, 20.0]
        spec["geometry"]["connected_anchor_distance_range"] = [40.0, 50.0]
        receipt = self.assemble()
        self.assertEqual("BLOCKED_GEOMETRY", receipt["assembly_status"])
        self.assertEqual("GEOMETRIC_CONFLICT", receipt["geometry_status"])

    def test_f03_unit_conversion_plus_rotation_compose(self):
        spec = self.spec
        spec["connections"] = spec["connections"][:1]
        self.parts["follower"]["model_and_units"]["length_unit"] = "nm"
        spec["unit_conversion"] = {
            "component": "follower", "from_unit": "nm", "to_unit": "oxDNA_length_unit",
            "length_factor": 2.0, "source": "test fixture factor",
        }
        spec["coordinate_transforms"] = [{
            "component": "follower",
            "rotation_axis": [0, 0, 1],
            "rotation_angle_deg": 180.0,
            "translation": [40.0, 30.0, 0.0],
        }]
        spec["assembly_box"] = [60.0, 60.0, 20.0]
        # follower anchor (9, 8.5, 5): x2 -> (18, 17, 10); rotate 180 about z ->
        # (-18, -17, 10); translate -> (22, 13, 10). Distance to driver A
        # (12, 5, 5) is sqrt(100 + 64 + 25) ~ 13.75. The band below is satisfied
        # ONLY by this exact scale->rotate->translate composition.
        spec["geometry"]["connected_anchor_distance_range"] = [13.0, 14.5]
        receipt = self.assemble()
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])
        top_text, conf_text, _ = aps.assemble_artifacts(
            spec, self.parts, self.fx.inputs(), recipe_base=self.tmp
        )
        conf = Configuration.parse(conf_text)
        # follower particle 0: (1, 8.5, 5) -> x2 -> (2, 17, 10) -> rot180 ->
        # (-2, -17, 10) -> +(40, 30, 0) = (38, 13, 10)
        self.assertAlmostEqual(conf.particles[DRIVER_N][0][0], 38.0, places=4)
        self.assertAlmostEqual(conf.particles[DRIVER_N][0][1], 13.0, places=4)
        self.assertAlmostEqual(conf.particles[DRIVER_N][0][2], 10.0, places=4)

    def test_f03_artifacts_match_receipt_digests_under_rotation(self):
        spec = self.spec
        spec["coordinate_transforms"] = [{
            "component": "follower",
            "rotation_axis": [0, 1, 0],
            "rotation_angle_deg": 90.0,
            "translation": [5.0, 0.0, 25.0],
        }]
        spec["assembly_box"] = [50.0, 30.0, 40.0]
        top_text, conf_text, receipt = aps.assemble_artifacts(
            spec, self.parts, self.fx.inputs(), recipe_base=self.tmp
        )
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])
        self.assertEqual(
            hashlib.sha256(top_text.encode()).hexdigest(),
            receipt["assembled"]["topology_text_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(conf_text.encode()).hexdigest(),
            receipt["assembled"]["configuration_text_sha256"],
        )

    # ---------------- R3-F04: exposed-overhang interface ----------------

    def test_f04_missing_overhang_segment_blocks(self):
        del self.parts["follower"]["ports"][0]["chemistry"]["overhang_segment"]
        receipt = self.assemble()
        self.assertEqual("BLOCKED_INFERRED_INTERFACE", receipt["assembly_status"])
        self.assertIn("overhang_segment", receipt["reason"])

    def test_f04_unknown_overhang_end_blocks(self):
        self.parts["driver"]["ports"][0]["chemistry"]["overhang_end"] = "UNKNOWN"
        receipt = self.assemble()
        self.assertEqual("BLOCKED_INFERRED_INTERFACE", receipt["assembly_status"])
        self.assertIn("overhang_end", receipt["reason"])

    def test_f04_segment_not_part_of_sequence_blocks(self):
        rc_seg = aps.reverse_complement(SEQ_A)
        mutated = rc_seg[:-1] + ("A" if rc_seg[-1] != "A" else "C")
        self.parts["follower"]["ports"][0]["chemistry"]["sequence"] = mutated
        receipt = self.assemble()
        self.assertEqual("BLOCKED_INFERRED_INTERFACE", receipt["assembly_status"])
        self.assertIn("not part of", receipt["reason"])

    def test_f04_short_segment_blocks(self):
        chem = self.parts["driver"]["ports"][0]["chemistry"]
        chem["overhang_segment"] = "ACGTACGT"
        receipt = self.assemble()
        self.assertEqual("BLOCKED_INFERRED_INTERFACE", receipt["assembly_status"])
        self.assertIn("too short", receipt["reason"])

    def test_f04_lna_notation_is_stripped_consistently(self):
        # The driver exposes its 20nt segment with LNA-locked bases written in
        # (LX) notation; the follower exposes the plain reverse complement.
        chem = self.parts["driver"]["ports"][0]["chemistry"]
        plain = chem["overhang_segment"]
        chem["overhang_segment"] = "(LA)(LC)(LG)" + plain[3:]  # locked A, C, G prefix
        chem["sequence"] = chem["overhang_segment"]
        chem["lna"] = True
        receipt = self.assemble()
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])
        record = receipt["connections"][0]["overhang_interface"]
        self.assertTrue(record["exact_reverse_complement"])
        self.assertTrue(record["lna"])

    def test_f04_same_end_pair_is_allowed(self):
        # The pinned real S17 recipe pairs 3p/3p (and 5p/5p); same ends assemble.
        self.parts["follower"]["ports"][0]["chemistry"]["overhang_end"] = "3p"
        receipt = self.assemble()
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])
        record = receipt["connections"][0]["overhang_interface"]
        self.assertEqual(record["driver_overhang_end"], "3p")
        self.assertEqual(record["follower_overhang_end"], "3p")

    def test_f04_receipt_records_interface_record(self):
        receipt = self.assemble()
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"])
        for conn in receipt["connections"]:
            self.assertEqual(20, conn["complementarity_match_nt"])
            self.assertIn("overhang_interface", conn)
            self.assertTrue(conn["overhang_interface"]["exact_reverse_complement"])

    # ---------------- hardening: finite numbers, boxes, files ----------------

    def test_nan_translation_rejected(self):
        self.spec["coordinate_transforms"] = [
            {"component": "follower", "translation": [float("nan"), 0.0, 0.0]}
        ]
        errors = aps.validate_assembly_spec(self.spec, self.parts)
        self.assertTrue(any("finite" in e for e in errors))
        receipt = self.assemble()
        self.assertEqual("BLOCKED_SPEC", receipt["assembly_status"])

    def test_infinite_anchor_position_rejected(self):
        self.spec["components"][1]["port_geometry"][0]["anchor_position"] = [
            float("inf"), 8.5, 5.0
        ]
        errors = aps.validate_assembly_spec(self.spec, self.parts)
        self.assertTrue(any("finite" in e for e in errors))
        receipt = self.assemble()
        self.assertEqual("BLOCKED_SPEC", receipt["assembly_status"])

    def test_nan_length_factor_rejected(self):
        self.parts["follower"]["model_and_units"]["length_unit"] = "nm"
        self.spec["unit_conversion"] = {
            "component": "follower", "from_unit": "nm", "to_unit": "oxDNA_length_unit",
            "length_factor": float("nan"), "source": "broken",
        }
        errors = aps.validate_assembly_spec(self.spec, self.parts)
        self.assertTrue(any("length_factor" in e for e in errors))
        receipt = self.assemble()
        self.assertEqual("BLOCKED_SPEC", receipt["assembly_status"])

    def test_nan_assembly_box_rejected(self):
        self.spec["assembly_box"] = [float("nan"), 12.0, 12.0]
        errors = aps.validate_assembly_spec(self.spec, self.parts)
        self.assertTrue(any("assembly_box" in e for e in errors))

    def test_nonpositive_assembly_box_rejected(self):
        self.spec["assembly_box"] = [0.0, 12.0, 12.0]
        errors = aps.validate_assembly_spec(self.spec, self.parts)
        self.assertTrue(any("positive" in e for e in errors))

    def test_decreasing_anchor_band_rejected(self):
        self.spec["geometry"]["connected_anchor_distance_range"] = [30.0, 10.0]
        errors = aps.validate_assembly_spec(self.spec, self.parts)
        self.assertTrue(any("non-decreasing" in e for e in errors))

    def test_unparseable_configuration_with_matching_digest_blocks(self):
        inputs = self.fx.inputs()
        path = Path(inputs["follower"]["configuration_path"])
        path.write_text("not a configuration at all\n", encoding="utf-8")
        self.parts["follower"]["configuration"]["sha256"] = self.fx.sha(path)
        receipt = self.assemble()
        self.assertEqual("BLOCKED_INPUT", receipt["assembly_status"])
        self.assertIn("configuration load failed", receipt["reason"])

    # ---------------- real pinned S17 artifacts (honest verdicts) ----------------

    def _load_real(self):
        research = REPO_ROOT / "docs" / "research"
        spec = json.loads((research / "S17_R3_ASSEMBLY_SPEC.json").read_text(encoding="utf-8"))
        driver = json.loads((research / "S17_R3_COMPONENT_DRIVER.json").read_text(encoding="utf-8"))
        follower = json.loads((research / "S17_R3_COMPONENT_FOLLOWER.json").read_text(encoding="utf-8"))
        return spec, {"driver": driver, "follower": follower}

    def test_real_s17_pair_remains_not_reconstructed(self):
        """The F01/F02 gates must not flip the honest structureless verdict."""
        spec, parts = self._load_real()
        receipt = aps.assemble(spec, parts, {}, recipe_base=REPO_ROOT)
        self.assertEqual("NOT_RECONSTRUCTED", receipt["assembly_status"])
        self.assertTrue(any("follower" in b for b in receipt["blocked_inputs"]))
        self.assertEqual(receipt["geometry_status"], "NOT_PERFORMED")

    def test_real_recipe_bytes_match_pinned_digest(self):
        spec, _parts = self._load_real()
        recipe_path = REPO_ROOT / spec["interface_recipe_ref"]["path"]
        self.assertTrue(recipe_path.is_file())
        self.assertEqual(
            hashlib.sha256(recipe_path.read_bytes()).hexdigest(),
            spec["interface_recipe_ref"]["sha256"],
        )

    def test_real_recipe_after_20nt_erratum_is_valid_and_tampering_still_refused(self):
        """ERRATUM-1: source-pinned 20nt follower segments now match the recipe.

        Preserve the original RED evidence in CI 39523456603. A deliberately
        reintroduced 21nt error must still be rejected as BLOCKED_SOURCE.
        """
        spec, parts = self._load_real()
        self.assertIsNone(aps._verify_interface_recipe(spec, parts, REPO_ROOT))
        tampered = copy.deepcopy(parts)
        follower_port = next(p for p in tampered["follower"]["ports"]
                             if p["port_id"] == "DF-OVH-F174")
        follower_port["chemistry"]["overhang_segment"] = (
            "T" + follower_port["chemistry"]["overhang_segment"]
        )
        failure = aps._verify_interface_recipe(spec, tampered, REPO_ROOT)
        self.assertIsNotNone(failure)
        self.assertEqual("BLOCKED_SOURCE", failure["assembly_status"])
        self.assertIn("contradicts", failure["reason"])


if __name__ == "__main__":
    unittest.main()
