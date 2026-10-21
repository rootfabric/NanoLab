"""Tests for the MechanicalComponentSpec v1 contract (S17 R3 stage B).

WO-PREP-S17-R3. Fail-closed discipline under test:

* strict schema: unknown fields, wrong kinds, bad digests are errors;
* claim ceiling: scientific-result claim levels are rejected;
* UNKNOWN honesty: an UNKNOWN structure must never carry concrete pins, and a
  fully confirmed port must never be marked non-connectable;
* the connection-capability gate: a well-formed numeric index alone never
  makes a port physically connectable;
* the published S17 driver/follower specs and the interface recipe are valid
  and mutually consistent (digests re-verified offline).
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from knowledge_pack import assembly_spec as aps
from knowledge_pack import mechanical_component_spec as mcs

DRIVER_SPEC = REPO_ROOT / "docs/research/S17_R3_COMPONENT_DRIVER.json"
FOLLOWER_SPEC = REPO_ROOT / "docs/research/S17_R3_COMPONENT_FOLLOWER.json"
RECIPE = REPO_ROOT / "docs/work/executions/EX-PREP-S17-R3/evidence/s17-r3-df-interface-recipe.json"
PACK = REPO_ROOT / "docs/research/S17_KNOWLEDGEPACK_R2.json"


def base_spec() -> dict:
    return {
        "schema_version": 1,
        "kind": "mechanical_component_spec",
        "spec_version": "v1",
        "component_id": "TEST-COMPONENT",
        "version": "1.0.0",
        "source_id": "S17",
        "knowledge_pack_ref": {
            "pack_id": "P",
            "pack_path": "docs/research/S17_KNOWLEDGEPACK_R2.json",
            "pack_sha256": "0" * 64,
        },
        "source_pin": {
            "role": "DESIGN_TOPOLOGY",
            "url": "https://example.org/x.top",
            "sha256": "a" * 64,
            "status": "SOURCE_CONFIRMED",
            "license": "CC BY 4.0",
        },
        "claim_level": "PINNED_IMPORT_VERIFIED",
        "topology": {
            "uri": "https://example.org/x.top",
            "sha256": "b" * 64,
            "nucleotides": 10,
            "strand_count": 2,
            "status": "SOURCE_CONFIRMED",
        },
        "molecular_namespaces": {
            "ns": {"index_space": "0-based", "particle_count": 10, "topology_sha256": "b" * 64},
        },
        "local_frame": {"status": "UNKNOWN"},
        "ports": [],
        "mechanical_dofs": [
            {"dof_id": "angle", "kind": "ROTATIONAL", "status": "SOURCE_CONFIRMED"}
        ],
        "model_and_units": {
            "model": "oxDNA2",
            "length_unit": "oxDNA_length_unit",
            "compatible_conditions": ["23C"],
        },
        "unverified_fields": ["local_frame"],
        "known_limitations": ["synthetic test component"],
    }


class TestStructuralValidation(unittest.TestCase):
    def test_base_spec_is_valid(self):
        self.assertEqual(mcs.validate_component_spec(base_spec()), [])

    def test_missing_required_field(self):
        spec = base_spec()
        del spec["claim_level"]
        errors = mcs.validate_component_spec(spec)
        self.assertTrue(any("claim_level" in e for e in errors))

    def test_unknown_top_level_field_rejected(self):
        spec = base_spec()
        spec["magic_field"] = True
        errors = mcs.validate_component_spec(spec)
        self.assertTrue(any("magic_field" in e for e in errors))

    def test_wrong_kind_and_version(self):
        spec = base_spec()
        spec["kind"] = "component_card"
        spec["spec_version"] = "v2"
        errors = mcs.validate_component_spec(spec)
        self.assertEqual(len(errors), 2)

    def test_bad_sha256_format(self):
        spec = base_spec()
        spec["source_pin"]["sha256"] = "XYZ"
        errors = mcs.validate_component_spec(spec)
        self.assertTrue(any("source_pin.sha256" in e for e in errors))

    def test_claim_inflation_rejected(self):
        for claim in ("MODEL_REPRODUCED", "ASSEMBLY_VALIDATED", "COMPONENT_CHARACTERIZED"):
            spec = base_spec()
            spec["claim_level"] = claim
            errors = mcs.validate_component_spec(spec)
            self.assertTrue(any("exceeds the v1 ceiling" in e for e in errors), claim)

    def test_unknown_topology_must_not_carry_concrete_pins(self):
        spec = base_spec()
        spec["topology"] = {"status": "UNKNOWN", "uri": "real.top", "sha256": "b" * 64}
        errors = mcs.validate_component_spec(spec)
        self.assertTrue(any("UNKNOWN" in e and "uri" in e for e in errors))
        self.assertTrue(any("UNKNOWN" in e and "sha256" in e for e in errors))

    def test_unknown_structure_requires_explicit_status(self):
        spec = base_spec()
        spec["topology"] = {"uri": "x", "sha256": "b" * 64, "nucleotides": 5, "strand_count": 1}
        errors = mcs.validate_component_spec(spec)
        self.assertTrue(any("topology.status" in e for e in errors))


class TestPortCapabilityGate(unittest.TestCase):
    def _spec_with_port(self, port: dict) -> dict:
        spec = base_spec()
        spec["ports"] = [port]
        return spec

    def test_numeric_index_alone_never_enables_connection(self):
        port = {
            "port_id": "p1",
            "role": "driver",
            "interface_type": "SS_DNA_OVERHANG_HYBRIDIZATION",
            "anchors": [{"namespace": "ns", "index_space": "i", "anchor": 5, "status": "UNVERIFIED"}],
            "orientation": {"status": "UNKNOWN"},
            "connection_capable": True,
            "status": "SOURCE_CONFIRMED",
        }
        errors = mcs.validate_component_spec(self._spec_with_port(port))
        self.assertTrue(any("requires all anchors SOURCE_CONFIRMED" in e for e in errors))
        self.assertTrue(any("orientation.status SOURCE_CONFIRMED" in e for e in errors))

    def test_unknown_interface_type_never_enables_connection(self):
        port = {
            "port_id": "p1",
            "role": "driver",
            "interface_type": "UNKNOWN",
            "anchors": [{"namespace": "ns", "index_space": "i", "anchor": 5, "status": "SOURCE_CONFIRMED"}],
            "orientation": {"status": "SOURCE_CONFIRMED"},
            "connection_capable": True,
            "status": "SOURCE_CONFIRMED",
        }
        errors = mcs.validate_component_spec(self._spec_with_port(port))
        self.assertTrue(any("requires a concrete interface type" in e for e in errors))

    def test_fully_confirmed_port_must_be_capable(self):
        port = {
            "port_id": "p1",
            "role": "driver",
            "interface_type": "SS_DNA_OVERHANG_HYBRIDIZATION",
            "anchors": [{"namespace": "ns", "index_space": "i", "anchor": 5, "status": "SOURCE_CONFIRMED"}],
            "orientation": {"status": "SOURCE_CONFIRMED"},
            "connection_capable": False,
            "status": "SOURCE_CONFIRMED",
        }
        errors = mcs.validate_component_spec(self._spec_with_port(port))
        self.assertTrue(any("must not be marked connection_capable=false" in e for e in errors))

    def test_source_confirmed_anchor_cannot_be_literal_unknown(self):
        port = {
            "port_id": "p1",
            "role": "driver",
            "interface_type": "SS_DNA_OVERHANG_HYBRIDIZATION",
            "anchors": [{"namespace": "ns", "index_space": "i", "anchor": "UNKNOWN", "status": "SOURCE_CONFIRMED"}],
            "orientation": {"status": "UNKNOWN"},
            "connection_capable": False,
            "status": "SOURCE_CONFIRMED",
        }
        errors = mcs.validate_component_spec(self._spec_with_port(port))
        self.assertTrue(any("never be the literal UNKNOWN" in e for e in errors))

    def test_duplicate_port_ids_rejected(self):
        spec = base_spec()
        port = {
            "port_id": "p1",
            "role": "driver",
            "interface_type": "UNKNOWN",
            "anchors": [{"namespace": "ns", "index_space": "i", "anchor": 1, "status": "UNVERIFIED"}],
            "orientation": {"status": "UNKNOWN"},
            "connection_capable": False,
            "status": "UNKNOWN",
        }
        spec["ports"] = [dict(port), dict(port)]
        errors = mcs.validate_component_spec(spec)
        self.assertTrue(any("duplicate" in e for e in errors))


class TestRepoVerification(unittest.TestCase):
    def test_real_specs_are_valid_and_repo_consistent(self):
        for path in (DRIVER_SPEC, FOLLOWER_SPEC):
            spec = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(mcs.validate_component_spec(spec), [], str(path))
            self.assertEqual(
                mcs.verify_component_spec_against_repo(spec, REPO_ROOT), [], str(path)
            )

    def test_pack_digest_tamper_detected(self):
        spec = json.loads(DRIVER_SPEC.read_text(encoding="utf-8"))
        spec["knowledge_pack_ref"]["pack_sha256"] = "e" * 64
        errors = mcs.verify_component_spec_against_repo(spec, REPO_ROOT)
        self.assertTrue(any("pack_sha256" in e for e in errors))

    def test_local_pin_tamper_detected(self):
        spec = json.loads(DRIVER_SPEC.read_text(encoding="utf-8"))
        spec["topology"] = {
            "uri": "project/state.json",
            "sha256": "b" * 64,
            "nucleotides": 1,
            "strand_count": 1,
            "status": "SOURCE_CONFIRMED",
        }
        errors = mcs.verify_component_spec_against_repo(spec, REPO_ROOT)
        self.assertTrue(any("digest mismatch" in e for e in errors))

    def test_remote_pin_requires_provenance(self):
        spec = json.loads(DRIVER_SPEC.read_text(encoding="utf-8"))
        del spec["topology"]["sha256_provenance"]
        errors = mcs.verify_component_spec_against_repo(spec, REPO_ROOT)
        self.assertTrue(any("sha256_provenance" in e for e in errors))

    def test_load_rejects_invalid_spec_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({"schema_version": 2}), encoding="utf-8")
            with self.assertRaises(mcs.ComponentSpecError):
                mcs.load_component_spec(bad)


class TestInterfaceRecipe(unittest.TestCase):
    """The published D-F recipe must survive independent offline re-verification."""

    @classmethod
    def setUpClass(cls):
        cls.recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
        cls.driver_spec = json.loads(DRIVER_SPEC.read_text(encoding="utf-8"))
        cls.follower_spec = json.loads(FOLLOWER_SPEC.read_text(encoding="utf-8"))

    def test_recipe_digest_is_pinned_by_both_component_specs(self):
        digest = aps.hashlib.sha256(RECIPE.read_bytes()).hexdigest()
        for spec in (self.driver_spec, self.follower_spec):
            self.assertEqual(spec["knowledge_pack_ref"]["interface_recipe"]["sha256"], digest)

    def test_source_pins_match_r1r2_knowledgepack(self):
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        pins = {entry["path"]: entry["sha256"] for entry in pack["input_file_manifest"]}
        nne_top = self.driver_spec["topology"]["sha256"]
        nne_conf = self.driver_spec["configuration"]["sha256"]
        self.assertEqual(pins.get("s17/nanobase/structure/nNE.top"), nne_top)
        self.assertEqual(pins.get("s17/nanobase/structure/nNE.dat"), nne_conf)

    def test_all_ten_pairs_are_exact_20nt_reverse_complements(self):
        pairs = self.recipe["pairs"]
        self.assertEqual(len(pairs), 10)
        driver_odns = {
            p["chemistry"]["odn_name"]: p["chemistry"]["sequence"]
            for p in self.driver_spec["ports"]
        }
        follower_odns = {
            p["chemistry"]["odn_name"]: p["chemistry"]["sequence"]
            for p in self.follower_spec["ports"]
        }
        for pair in pairs:
            dseq = aps.strip_lna(driver_odns[pair["driver_odn"]])
            fseq = aps.strip_lna(follower_odns[pair["follower_odn"]])
            d0, d1 = pair["driver_segment_offsets"]
            f0, f1 = pair["follower_segment_offsets"]
            self.assertEqual(dseq[d0:d1], pair["driver_segment"], pair["pair_id"])
            self.assertEqual(fseq[f0:f1], pair["follower_segment"], pair["pair_id"])
            self.assertEqual(
                pair["driver_segment"],
                aps.reverse_complement(pair["follower_segment"]),
                pair["pair_id"],
            )
            self.assertEqual(pair["match_length_nt"], 20, pair["pair_id"])

    def test_pairing_is_strictly_unique(self):
        for pair in self.recipe["pairs"]:
            self.assertTrue(pair["unique_best"], pair["pair_id"])
            self.assertLessEqual(pair["second_best_match_nt"], 8, pair["pair_id"])

    def test_component_ports_cover_exactly_the_recipe_pairs(self):
        driver_ports = {p["port_id"] for p in self.driver_spec["ports"]}
        follower_ports = {p["port_id"] for p in self.follower_spec["ports"]}
        self.assertEqual(len(driver_ports), 10)
        self.assertEqual(len(follower_ports), 10)
        recipe_pairs = {(p["driver_odn"], p["follower_odn"]) for p in self.recipe["pairs"]}

        def odn_of(port_id: str) -> str:
            for spec in (self.driver_spec, self.follower_spec):
                for p in spec["ports"]:
                    if p["port_id"] == port_id:
                        return p["chemistry"]["odn_name"]
            raise AssertionError(port_id)

        spec_pairs = set()
        assembly_spec = json.loads(
            (REPO_ROOT / "docs/research/S17_R3_ASSEMBLY_SPEC.json").read_text(encoding="utf-8")
        )
        for conn in assembly_spec["connections"]:
            spec_pairs.add((odn_of(conn["driver_port"]), odn_of(conn["follower_port"])))
        self.assertEqual(spec_pairs, recipe_pairs)

    def test_no_same_number_complementarity(self):
        for pair in self.recipe["pairs"]:
            dnum = pair["driver_odn"].split("-con")[0].upper().replace("HI-", "HI-")
            fnum = pair["follower_odn"].split("-con")[0].upper().replace("HI-", "HI-")
            self.assertNotEqual(dnum, fnum, pair["pair_id"])

    def test_real_pair_assembly_is_deterministic_not_reconstructed(self):
        spec = json.loads(
            (REPO_ROOT / "docs/research/S17_R3_ASSEMBLY_SPEC.json").read_text(encoding="utf-8")
        )
        receipt1 = aps.assemble(spec, {"driver": self.driver_spec, "follower": self.follower_spec}, {})
        receipt2 = aps.assemble(spec, {"driver": self.driver_spec, "follower": self.follower_spec}, {})
        self.assertEqual(receipt1, receipt2)
        self.assertEqual(receipt1["assembly_status"], "NOT_RECONSTRUCTED")
        self.assertEqual(receipt1["geometry_status"], "NOT_PERFORMED")
        self.assertTrue(any("follower" in b and "topology" in b for b in receipt1["blocked_inputs"]))
        published = json.loads(
            (REPO_ROOT / "docs/research/S17_R3_ASSEMBLY_RECEIPT.json").read_text(encoding="utf-8")
        )
        self.assertEqual(receipt1, published)


if __name__ == "__main__":
    unittest.main()
