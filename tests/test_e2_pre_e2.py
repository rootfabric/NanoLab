"""NL3-002A pre-E2 toolkit tests (synthetic fixtures only, no source data)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from e2 import compat_audit, digests, fixtures, observables, restraints_inventory, topology_mapping  # noqa: E402
from e2.extract_engine_options import build_registry, extract  # noqa: E402
from hinge_family.cadnano_design import Design  # noqa: E402
from hinge_family.oxdna_conf import ConfError, Configuration  # noqa: E402
from hinge_family.oxdna_topology import Topology  # noqa: E402

TOL = 1e-6


def _angle_of(fixture) -> float:
    topology = Topology.parse(fixture["topology_text"])
    topology.check_chain_integrity()
    frames = list(observables.iter_frames("".join(fixture["frame_texts"])))
    report = observables.analyse(topology, frames, fixture["manifest"])
    return report


class ObservableAngleTests(unittest.TestCase):
    def test_parallel_angle_zero(self):
        fixture = fixtures.build(mode="parallel", arm_len=12, n_frames=1)
        report = _angle_of(fixture)
        self.assertEqual(report["frames_total"], 1)
        frame = report["frames"][0]
        self.assertEqual(frame["hinge_angle"]["status"], "OK")
        self.assertAlmostEqual(frame["hinge_angle"]["angle_deg"], 0.0, delta=TOL)
        self.assertEqual(frame["pairs"]["pairs_fraction"], 1.0)
        self.assertEqual(frame["bonded"]["long_bond_fraction"], 0.0)
        self.assertEqual(report["reference_pairs_count"], 12)

    def test_angled_45_and_90(self):
        for angle in (45.0, 90.0):
            fixture = fixtures.build(mode="angled", angle_deg=angle, arm_len=12, n_frames=1)
            report = _angle_of(fixture)
            frame = report["frames"][0]
            self.assertEqual(frame["hinge_angle"]["status"], "OK")
            self.assertAlmostEqual(frame["hinge_angle"]["angle_deg"], angle, delta=TOL)
            self.assertEqual(frame["pairs"]["pairs_fraction"], 1.0)
            self.assertEqual(report["reference_pairs_count"], 4)  # 2 brace + 2 near-hinge arm/arm

    def test_broken_frame_angle_kept_integrity_failed(self):
        fixture = fixtures.build(mode="angled", angle_deg=45.0, arm_len=12, n_frames=1, broken=True)
        report = _angle_of(fixture)
        self.assertEqual(report["frames_total"], 2)
        intact, broken = report["frames"]
        self.assertAlmostEqual(intact["hinge_angle"]["angle_deg"], 45.0, delta=TOL)
        # "beautiful angle of a fallen-apart construction": angle survives, integrity does not
        self.assertAlmostEqual(broken["hinge_angle"]["angle_deg"], 45.0, delta=TOL)
        self.assertEqual(broken["pairs"]["pairs_fraction"], 0.0)
        self.assertAlmostEqual(broken["displacement"]["displacement_max"], fixture["expected"]["jump"], delta=TOL)
        self.assertEqual(intact["pairs"]["pairs_fraction"], 1.0)
        self.assertAlmostEqual(intact["displacement"]["displacement_max"], 0.0, delta=TOL)

    def test_angle_determinism_byte_identical(self):
        fixture = fixtures.build(mode="angled", angle_deg=45.0, arm_len=10, n_frames=2)
        topology = Topology.parse(fixture["topology_text"])
        frames = list(observables.iter_frames("".join(fixture["frame_texts"])))
        first = observables.canonical_json(observables.analyse(topology, frames, fixture["manifest"]))
        second = observables.canonical_json(observables.analyse(topology, frames, fixture["manifest"]))
        self.assertEqual(first, second)

    def test_fixture_bytes_deterministic(self):
        first = fixtures.build(mode="angled", angle_deg=45.0, arm_len=12, n_frames=1)
        second = fixtures.build(mode="angled", angle_deg=45.0, arm_len=12, n_frames=1)
        self.assertEqual(first["topology_text"], second["topology_text"])
        self.assertEqual(first["frame_texts"], second["frame_texts"])

    def test_nan_configuration_rejected(self):
        fixture = fixtures.build(mode="parallel", arm_len=6, n_frames=1)
        lines = fixture["frame_texts"][0].splitlines()
        parts = lines[3].split()
        parts[0] = "nan"
        lines[3] = " ".join(parts)
        with self.assertRaises(ConfError):
            Configuration.parse("\n".join(lines))

    def test_truncated_trajectory_rejected(self):
        fixture = fixtures.build(mode="parallel", arm_len=6, n_frames=2)
        text = "".join(fixture["frame_texts"])
        truncated = text[: int(len(text) * 0.75)]
        with self.assertRaises((ConfError, observables.ObservableError)):
            list(observables.iter_frames(truncated))

    def test_overlapping_arms_rejected(self):
        fixture = fixtures.build(mode="parallel", arm_len=6, n_frames=1)
        manifest = {
            "arm_a": {"nucleotides": [0, 1, 2]},
            "arm_b": {"nucleotides": [2, 3, 4]},
        }
        topology = Topology.parse(fixture["topology_text"])
        frames = list(observables.iter_frames(fixture["frame_texts"][0]))
        with self.assertRaises(observables.ObservableError):
            observables.analyse(topology, frames, manifest)


class DigestTests(unittest.TestCase):
    def test_verify_and_tamper(self):
        fixture = fixtures.build(mode="parallel", arm_len=6, n_frames=1)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "t.top")
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(fixture["topology_text"])
            expected = digests.sha256_file(path)
            self.assertTrue(digests.verify_file_sha256(path, expected)["match"])
            with open(path, "rb") as handle:
                data = bytearray(handle.read())
            data[0] = data[0] ^ 0x20
            with open(path, "wb") as handle:
                handle.write(bytes(data))
            self.assertFalse(digests.verify_file_sha256(path, expected)["match"])

    def test_git_blob_sha1_known_vector(self):
        # git hash-object of b"hello\n" is a well-known stable vector
        self.assertEqual(
            digests.git_blob_sha1(b"hello\n"),
            "ce013625030ba8dba906f756967f9e9ca394464a",
        )


class TopologyMappingTests(unittest.TestCase):
    def _report(self, design_text, topology_text):
        design = Design.parse(design_text)
        topology = Topology.parse(topology_text)
        return topology_mapping.map_design_to_topology(design, topology)

    def test_synthetic_mapping_one_to_one(self):
        fix = fixtures.design_pair_fixture()
        report = self._report(fix["design_text"], fix["topology_text"])
        self.assertEqual(report["association"]["status"], fix["expected"]["association_status"])
        self.assertEqual(report["association"]["exact"], fix["expected"]["exact_entries"])
        self.assertEqual(report["base_conservation"]["status"], "CONSERVED")
        self.assertEqual(report["base_conservation"]["total"], 32)
        self.assertEqual(report["design"]["paths_total"], 4)
        self.assertEqual(report["topology"]["strands"], 4)

    def test_mapping_determinism(self):
        fix = fixtures.design_pair_fixture()
        first = observables.canonical_json(self._report(fix["design_text"], fix["topology_text"]))
        second = observables.canonical_json(self._report(fix["design_text"], fix["topology_text"]))
        self.assertEqual(first, second)

    def test_mapping_conservation_violation_detected(self):
        fix = fixtures.design_pair_fixture()
        # rebuild the topology with strand 3 shortened by 2 nucleotides:
        # chains stay internally consistent, totals no longer match the design
        blocks = [(16, "A", 1), (4, "T", 2), (6, "T", 3)]
        lines = [f"{sum(b[0] for b in blocks)} {len(blocks)}"]
        index = 0
        for length, base, sid in blocks:
            for k in range(length):
                n3 = index + k + 1 if k < length - 1 else -1
                n5 = index + k - 1 if k > 0 else -1
                lines.append(f"{sid} {base} {n3} {n5}")
            index += length
        report = self._report(fix["design_text"], "\n".join(lines) + "\n")
        self.assertEqual(report["base_conservation"]["status"], "CONSERVATION_VIOLATION")


class CompatAuditTests(unittest.TestCase):
    CLEAN_INPUT = (
        "interaction_type = DNA2\n"
        "salt_concentration = 0.5\n"
        "T = 300K\n"
        "steps = 2e7\n"
        "backend = CPU\n"
        "backend_precision = double\n"
        "topology = 0b.top\n"
        "conf_file = 0b.conf\n"
        "trajectory_file = traj.dat\n"
        "energy_file = energy.dat\n"
        "seed = 7777\n"
    )

    def test_clean_input_known_and_confirmed(self):
        registry = compat_audit.load_registry()
        report = compat_audit.audit(self.CLEAN_INPUT, registry)
        self.assertEqual(report["unknown_keys"], [])
        self.assertEqual(report["undocumented_keys"], ["energy_file", "topology"])
        self.assertEqual(report["preregistered_values"]["status"], "CONFIRMED")
        self.assertEqual(report["conclusion"], "NO_EXTERNAL_FORCES_DECLARED")
        self.assertIn("seed", report["keys"])

    def test_unknown_key_is_gap(self):
        registry = compat_audit.load_registry()
        report = compat_audit.audit(self.CLEAN_INPUT + "not_a_real_option = 3\n", registry)
        self.assertEqual(report["unknown_keys"], ["not_a_real_option"])

    def test_preregistered_mismatch_detected(self):
        registry = compat_audit.load_registry()
        report = compat_audit.audit(self.CLEAN_INPUT.replace("300K", "298K"), registry)
        self.assertEqual(report["preregistered_values"]["status"], "MISMATCH")

    def test_external_forces_flagged(self):
        registry = compat_audit.load_registry()
        report = compat_audit.audit(
            self.CLEAN_INPUT + "external_forces = 1\nexternal_forces_file = traps.txt\n", registry
        )
        self.assertEqual(report["conclusion"].startswith("EXTERNAL_FORCES_ACTIVE"), True)
        self.assertIn("external_forces", report["force_related_keys"])

    def test_external_forces_zero_explicitly_disabled(self):
        registry = compat_audit.load_registry()
        report = compat_audit.audit(self.CLEAN_INPUT + "external_forces = 0\n", registry)
        self.assertEqual(
            report["conclusion"].startswith("EXTERNAL_FORCES_EXPLICITLY_DISABLED"), True
        )

    def test_source_confirmed_undocumented_keys(self):
        registry = compat_audit.load_registry()
        report = compat_audit.audit(
            self.CLEAN_INPUT + "dt = 0.002\nrefresh_vel = 0\ndebug = 0\nlog_file = log.txt\n", registry
        )
        self.assertEqual(report["unknown_keys"], [])
        for key in ("dt", "refresh_vel", "debug", "log_file"):
            self.assertIn(key, report["undocumented_keys"])
            self.assertIn("pinned engine source", report["keys"][key]["note"])

    def test_not_parsed_legacy_key_reported_separately(self):
        registry = compat_audit.load_registry()
        report = compat_audit.audit(self.CLEAN_INPUT + "rcut = 2.5\n", registry)
        self.assertEqual(report["unknown_keys"], [])
        self.assertEqual(report["not_parsed_keys"], ["rcut"])
        self.assertIn("no getInput* call", report["keys"]["rcut"]["note"])


class EngineRegistryTests(unittest.TestCase):
    SAMPLE = (
        "# Input file options\n\nCore options:\n\n    T = <float>\n"
        "        temperature.\n    [fix_diffusion = <bool>]\n        diffusion.\n"
    )

    def test_extraction_deterministic(self):
        self.assertEqual(extract(self.SAMPLE), extract(self.SAMPLE))

    def test_extraction_keys_and_sections(self):
        options = extract(self.SAMPLE)
        self.assertIn("T", options)
        self.assertIn("fix_diffusion", options)
        self.assertFalse(options["T"]["optional"])
        self.assertTrue(options["fix_diffusion"]["optional"])
        self.assertEqual(options["T"]["section"], "Core options")

    def test_frozen_registry_is_loaded(self):
        registry = compat_audit.load_registry()
        self.assertGreater(registry["option_count"], 150)
        for key in ("interaction_type", "steps", "backend", "T", "external_forces"):
            self.assertIn(key, registry["options"])
        self.assertEqual(registry["engine_commit"], "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591")


class RestraintsInventoryTests(unittest.TestCase):
    CLEAN_INPUT = "interaction_type = DNA2\nsteps = 2e7\n"

    def test_clean_input_no_restraints(self):
        report = restraints_inventory.combined(self.CLEAN_INPUT, {})
        self.assertEqual(report["production_input"]["status"], "NO_EXTERNAL_FORCES_DECLARED")
        self.assertEqual(report["verdict"].startswith("NO_RESTRAINTS_OBSERVED"), True)

    def test_active_external_forces_open_question(self):
        report = restraints_inventory.combined(
            self.CLEAN_INPUT + "external_forces = 1\nexternal_forces_file = traps.txt\n", {}
        )
        self.assertEqual(report["production_input"]["status"], "EXTERNAL_FORCES_DECLARED_ACTIVE")
        self.assertTrue(any("U-rest-1" in q for q in report["production_input"]["open_questions"]))
        self.assertEqual(report["verdict"].startswith("RESTRAINTS_PRESENT"), True)

    def test_init_script_keyword_scan(self):
        script = "print('hello')\n# uses mutual_trap during relax\nx = 1\n"
        report = restraints_inventory.combined(self.CLEAN_INPUT, {"init.py": script})
        hits = [h for h in report["scanned_scripts"] if h["source_name"] == "init.py"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["keyword_observations"][0]["line"], 2)

    def test_explicitly_disabled_external_forces_is_clean(self):
        report = restraints_inventory.combined(self.CLEAN_INPUT + "external_forces = 0\n", {})
        self.assertEqual(
            report["production_input"]["status"], "EXTERNAL_FORCES_EXPLICITLY_DISABLED"
        )
        self.assertEqual(report["verdict"].startswith("NO_RESTRAINTS_OBSERVED"), True)


if __name__ == "__main__":
    unittest.main()
