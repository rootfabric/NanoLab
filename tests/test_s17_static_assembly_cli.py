"""End-to-end tests for the deterministic offline assembly CLI.

WO-S17-STATIC-ASSEMBLY-HARDENING-R1 (issue #66). The CLI
(``knowledge_pack.assembly_cli``) is exercised as a real subprocess; the
repair-review minors (driver-side transforms, SOURCE_VERIFIED recipe
strictness) are additionally pinned at the library level.

Claim discipline under test: statuses only ``ASSEMBLED_STATIC_ONLY`` /
``NOT_RECONSTRUCTED`` / ``BLOCKED_*``; geometry ``GEOMETRY_UNVERIFIED``;
never ``ASSEMBLY_VALIDATED`` / ``MODEL_REPRODUCED``; no ``.top``/``.dat`` is
ever written on a failure path; artifact bytes are timestamp-free and
byte-deterministic across runs.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from knowledge_pack import assembly_spec as aps
from tests.test_s17_r3_assembly import DRIVER_N, Fixture, SEQ_A, SEQ_C

EXAMPLE_DIR = REPO_ROOT / "docs" / "examples" / "s17_static_assembly_example"
CLI_MODULE = ["-m", "knowledge_pack.assembly_cli"]
FORBIDDEN = ("ASSEMBLY_VALIDATED", "MODEL_REPRODUCED")

# SOURCE_VERIFIED recipe fixture: odn names join the Fixture's port chemistry.
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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def run_cli(*argv: str, cwd: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SCRIPTS) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, *CLI_MODULE, *argv],
        cwd=str(cwd), env=env, capture_output=True, text=True, timeout=120,
    )


def write_json(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


class CliWorkspace:
    """A temp dir holding one Fixture exported as CLI input JSON files."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        (self.dir / "inputs").mkdir(parents=True)
        self.fx = Fixture(self.dir / "inputs")
        self.driver_spec = write_json(self.dir / "driver.json", self.fx.component_spec("driver"))
        self.follower_spec = write_json(self.dir / "follower.json", self.fx.component_spec("follower"))
        self.assembly_spec = write_json(self.dir / "assembly.json", self.fx.assembly_spec())

    def cleanup(self) -> None:
        self._tmp.cleanup()

    def assemble(self, outdir: str = "out/run", **overrides) -> subprocess.CompletedProcess:
        argv = [
            "assemble",
            "--driver-spec", str(self.driver_spec),
            "--follower-spec", str(self.follower_spec),
            "--assembly-spec", str(self.assembly_spec),
            "--input-root", str(self.dir / "inputs"),
            "--outdir", outdir,
        ]
        return run_cli(*argv, cwd=self.dir)

    def artifact_paths(self, outdir: str = "out/run") -> list:
        base = self.dir / outdir
        return sorted(base.glob("*")) if base.is_dir() else []


class TestCliExampleDeterminism(unittest.TestCase):
    """The committed CANDIDATE_DESIGN example, run end-to-end via the CLI."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.work = Path(cls._tmp.name)
        for run in ("run1", "run2"):
            result = run_cli(
                "assemble",
                "--driver-spec", str(EXAMPLE_DIR / "driver_component_spec.json"),
                "--follower-spec", str(EXAMPLE_DIR / "follower_component_spec.json"),
                "--assembly-spec", str(EXAMPLE_DIR / "assembly_spec.json"),
                "--input-root", str(REPO_ROOT),
                "--outdir", run,
                cwd=cls.work,
            )
            if result.returncode != 0:
                raise AssertionError(f"example assemble failed: {result.stderr}")
        cls.run1 = cls.work / "run1"
        cls.run2 = cls.work / "run2"

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_two_runs_produce_identical_sha256_digests(self):
        for name in ("SYN-EX-DF-1.top", "SYN-EX-DF-1.dat", "receipt.json"):
            first = sha256_bytes((self.run1 / name).read_bytes())
            second = sha256_bytes((self.run2 / name).read_bytes())
            self.assertEqual(first, second, f"{name} is not byte-deterministic")

    def test_example_receipt_matches_expected_bytes(self):
        expected = (EXAMPLE_DIR / "expected_receipt.json").read_bytes()
        self.assertEqual((self.run1 / "receipt.json").read_bytes(), expected)

    def test_receipt_fields_and_claim_ceiling(self):
        receipt = json.loads((self.run1 / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["kind"], "assembly_receipt")
        self.assertEqual(receipt["assembly_status"], "ASSEMBLED_STATIC_ONLY")
        self.assertEqual(receipt["geometry_status"], "GEOMETRY_UNVERIFIED")
        self.assertEqual(receipt["mode"], "CANDIDATE_DESIGN")
        self.assertEqual(receipt["design_basis"], "HYPOTHESIS")
        self.assertEqual(receipt["assembled"]["nucleotides"], 24)
        self.assertEqual(receipt["assembled"]["strands"], 2)
        for key in ("assembly_status", "geometry_status"):
            self.assertNotIn(receipt[key], FORBIDDEN)
        self.assertIn("Never ASSEMBLY_VALIDATED", receipt["claim"])

    def test_artifacts_reparse_as_strict_oxdna(self):
        from hinge_family.oxdna_conf import Configuration
        from hinge_family.oxdna_topology import Topology
        top = Topology.parse((self.run1 / "SYN-EX-DF-1.top").read_text(encoding="utf-8"))
        top.check_chain_integrity()
        conf = Configuration.parse((self.run1 / "SYN-EX-DF-1.dat").read_text(encoding="utf-8"))
        self.assertEqual((top.nucleotides, top.strand_count), (24, 2))
        self.assertEqual(len(conf.particles), 24)

    def test_verify_roundtrip_ok(self):
        result = run_cli("verify", "--artifact-dir", "run1", cwd=self.work)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verify ok", result.stdout)


class TestCliVerifyNegative(unittest.TestCase):
    """verify must detect tampered artifacts and tampered/foreign receipts."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.work = Path(self._tmp.name)
        result = run_cli(
            "assemble",
            "--driver-spec", str(EXAMPLE_DIR / "driver_component_spec.json"),
            "--follower-spec", str(EXAMPLE_DIR / "follower_component_spec.json"),
            "--assembly-spec", str(EXAMPLE_DIR / "assembly_spec.json"),
            "--input-root", str(REPO_ROOT),
            "--outdir", "artifacts",
            cwd=self.work,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self):
        self._tmp.cleanup()

    def _verify(self) -> subprocess.CompletedProcess:
        return run_cli("verify", "--artifact-dir", "artifacts", cwd=self.work)

    def test_tampered_artifact_detected(self):
        dat = self.work / "artifacts" / "SYN-EX-DF-1.dat"
        text = dat.read_text(encoding="utf-8")
        dat.write_text(text.replace("2.000000", "2.000001", 1), encoding="utf-8")
        result = self._verify()
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not match the receipt digest", result.stderr)

    def test_tampered_receipt_detected(self):
        path = self.work / "artifacts" / "receipt.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["assembled"]["nucleotides"] = 25
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
        result = self._verify()
        self.assertEqual(result.returncode, 1)

    def test_unparseable_receipt_detected(self):
        path = self.work / "artifacts" / "receipt.json"
        path.write_text("not json at all {", encoding="utf-8")
        result = self._verify()
        self.assertEqual(result.returncode, 1)

    def test_missing_receipt_detected(self):
        for name in ("receipt.json",):
            (self.work / "artifacts" / name).unlink()
        result = self._verify()
        self.assertEqual(result.returncode, 1)
        self.assertIn("receipt.json not found", result.stderr)

    def test_missing_artifact_dir_detected(self):
        result = run_cli("verify", "--artifact-dir", "does-not-exist", cwd=self.work)
        self.assertEqual(result.returncode, 1)


class TestCliFailClosedBoundaries(unittest.TestCase):
    """Every CLI boundary refusal: clean exit code + stderr, no artifacts."""

    def setUp(self):
        self.ws = CliWorkspace()

    def tearDown(self):
        self.ws.cleanup()

    def _assert_refused_without_artifacts(self, result, outdir="out/run"):
        self.assertEqual(result.returncode, 2, f"stdout={result.stdout} stderr={result.stderr}")
        self.assertTrue(result.stderr.strip(), "refusal must carry a stderr message")
        self.assertFalse((self.ws.dir / outdir).exists(), "no artifact dir may be created")

    def test_unknown_argument_rejected(self):
        result = self.ws.assemble("--totally-bogus")
        self.assertEqual(result.returncode, 2)

    def test_missing_input_file_rejected(self):
        (self.ws.dir / "driver.json").unlink()
        result = self.ws.assemble()
        self._assert_refused_without_artifacts(result)
        self.assertIn("not found", result.stderr)

    def test_oversized_input_rejected(self):
        big = self.ws.dir / "driver.json"
        big.write_text(json.dumps({"padding": "x" * (4 * 1024 * 1024 + 1)}), encoding="utf-8")
        result = self.ws.assemble()
        self._assert_refused_without_artifacts(result)
        self.assertIn("input cap", result.stderr)

    def test_absolute_outdir_rejected(self):
        result = run_cli(
            "assemble",
            "--driver-spec", str(self.ws.driver_spec),
            "--follower-spec", str(self.ws.follower_spec),
            "--assembly-spec", str(self.ws.assembly_spec),
            "--outdir", str(self.ws.dir / "abs" / "out"),
            cwd=self.ws.dir,
        )
        self._assert_refused_without_artifacts(result, outdir="abs/out")
        self.assertIn("relative path", result.stderr)

    def test_traversal_outdir_rejected(self):
        result = self.ws.assemble(outdir="../escaped")
        self._assert_refused_without_artifacts(result, outdir="../escaped")
        self.assertIn("'..'", result.stderr)
        self.assertFalse((self.ws.dir.parent / "escaped").exists())

    def test_duplicate_particle_ids_rejected(self):
        spec = json.loads(self.ws.assembly_spec.read_text(encoding="utf-8"))
        duplicate = copy.deepcopy(spec["connections"][0])
        duplicate["connection_id"] = "c2-duplicate"
        spec["connections"] = [spec["connections"][0], duplicate]
        write_json(self.ws.assembly_spec, spec)
        result = self.ws.assemble()
        self._assert_refused_without_artifacts(result)
        self.assertIn("duplicate particle id", result.stderr)

    def test_recipe_with_wrong_bytes_rejected_blocked_input(self):
        spec = json.loads(self.ws.assembly_spec.read_text(encoding="utf-8"))
        spec["mode"] = "SOURCE_VERIFIED"
        spec["design_basis"] = "PUBLISHED_SOURCE"
        for conn in spec["connections"]:
            conn["evidence_status"] = "SOURCE_CONFIRMED"
        declared_sha = sha256_bytes(json.dumps(RECIPE).encode("utf-8"))
        spec["interface_recipe_ref"] = {
            "path": "recipe.json",
            "sha256": declared_sha,
            "status": "SOURCE_CONFIRMED",
        }
        write_json(self.ws.assembly_spec, spec)
        # the file on disk carries different bytes than the declared digest
        (self.ws.dir / "recipe.json").write_text(
            json.dumps({"kind": "interface_recipe", "pairs": []}), encoding="utf-8"
        )
        result = run_cli(
            "assemble",
            "--driver-spec", str(self.ws.driver_spec),
            "--follower-spec", str(self.ws.follower_spec),
            "--assembly-spec", str(self.ws.assembly_spec),
            "--recipe", "recipe.json",
            "--outdir", "out/run",
            cwd=self.ws.dir,
        )
        self.assertEqual(result.returncode, 2)
        outdir = self.ws.dir / "out" / "run"
        self.assertTrue((outdir / "receipt.json").is_file(), "the refusal receipt is evidence")
        receipt = json.loads((outdir / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["assembly_status"], "BLOCKED_INPUT")
        self.assertIn("digest mismatch", receipt["reason"])
        self.assertEqual(sorted(p.name for p in outdir.iterdir()), ["receipt.json"],
                         "no .top/.dat may exist on a failure path")

    def test_recipe_substitution_rejected(self):
        spec = json.loads(self.ws.assembly_spec.read_text(encoding="utf-8"))
        spec["mode"] = "SOURCE_VERIFIED"
        spec["design_basis"] = "PUBLISHED_SOURCE"
        spec["interface_recipe_ref"] = {
            "path": "elsewhere/recipe.json",
            "sha256": "a" * 64,
            "status": "SOURCE_CONFIRMED",
        }
        write_json(self.ws.assembly_spec, spec)
        (self.ws.dir / "recipe.json").write_text(json.dumps(RECIPE), encoding="utf-8")
        result = run_cli(
            "assemble",
            "--driver-spec", str(self.ws.driver_spec),
            "--follower-spec", str(self.ws.follower_spec),
            "--assembly-spec", str(self.ws.assembly_spec),
            "--recipe", "recipe.json",
            "--outdir", "out/run",
            cwd=self.ws.dir,
        )
        self._assert_refused_without_artifacts(result)
        self.assertIn("is not the spec-declared recipe file", result.stderr)

    def test_recipe_with_candidate_design_rejected(self):
        (self.ws.dir / "recipe.json").write_text(json.dumps(RECIPE), encoding="utf-8")
        result = run_cli(
            "assemble",
            "--driver-spec", str(self.ws.driver_spec),
            "--follower-spec", str(self.ws.follower_spec),
            "--assembly-spec", str(self.ws.assembly_spec),
            "--recipe", "recipe.json",
            "--outdir", "out/run",
            cwd=self.ws.dir,
        )
        self._assert_refused_without_artifacts(result)
        self.assertIn("only consulted for SOURCE_VERIFIED", result.stderr)

    def test_not_reconstructed_exits_cleanly_with_receipt_only(self):
        follower = json.loads(self.ws.follower_spec.read_text(encoding="utf-8"))
        follower["topology"] = {
            "uri": "UNKNOWN", "sha256": "UNKNOWN", "nucleotides": "UNKNOWN",
            "strand_count": "UNKNOWN", "status": "UNKNOWN",
        }
        follower["configuration"] = {
            "uri": "UNKNOWN", "sha256": "UNKNOWN", "nucleotides": "UNKNOWN",
            "strand_count": "UNKNOWN", "status": "UNKNOWN",
        }
        port = follower["ports"][0]
        port["connection_capable"] = False
        port["anchors"] = [{"namespace": "example", "index_space": "0-based",
                            "anchor": "UNKNOWN", "status": "UNKNOWN"}]
        port["orientation"] = {"status": "UNKNOWN"}
        write_json(self.ws.follower_spec, follower)
        spec = json.loads(self.ws.assembly_spec.read_text(encoding="utf-8"))
        spec["components"][1]["topology_sha256"] = "UNKNOWN"
        write_json(self.ws.assembly_spec, spec)
        result = self.ws.assemble()
        self.assertEqual(result.returncode, 0, result.stderr)
        outdir = self.ws.dir / "out" / "run"
        receipt = json.loads((outdir / "receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["assembly_status"], "NOT_RECONSTRUCTED")
        self.assertEqual(receipt["geometry_status"], "NOT_PERFORMED")
        self.assertEqual(
            sorted(p.name for p in outdir.iterdir()), ["receipt.json"],
            "an honest NOT_RECONSTRUCTED writes only the receipt, never .top/.dat",
        )

    def test_unsafe_assembly_id_rejected(self):
        spec = json.loads(self.ws.assembly_spec.read_text(encoding="utf-8"))
        spec["assembly_id"] = "bad id with spaces"
        write_json(self.ws.assembly_spec, spec)
        result = self.ws.assemble()
        self._assert_refused_without_artifacts(result)
        self.assertIn("artifact file stem", result.stderr)

    def test_remote_only_pin_rejected_offline(self):
        driver = json.loads(self.ws.driver_spec.read_text(encoding="utf-8"))
        driver["topology"]["uri"] = "https://example.org/remote/driver.top"
        write_json(self.ws.driver_spec, driver)
        result = self.ws.assemble()
        self._assert_refused_without_artifacts(result)
        self.assertIn("never fetches", result.stderr)


class TestRepairReviewMinorADriverTransforms(unittest.TestCase):
    """Minor (a): driver-side transforms are APPLIED, not silently ignored."""

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

    def _artifacts(self):
        return aps.assemble_artifacts(
            self.spec, self.parts, self.fx.inputs(), recipe_base=self.tmp
        )

    def test_driver_translation_moves_driver_particles_and_geometry(self):
        self.spec["coordinate_transforms"] = [
            {"component": "driver", "translation": [5.0, 0.0, 0.0]},
            {"component": "follower", "translation": [20.0, 0.0, 0.0]},
        ]
        _top, conf_text, receipt = self._artifacts()
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])
        from hinge_family.oxdna_conf import Configuration
        conf = Configuration.parse(conf_text)
        # driver particle 0: (1, 5, 5) + (5, 0, 0) = (6, 5, 5) - APPLIED
        self.assertAlmostEqual(conf.particles[0][0][0], 6.0, places=5)
        self.assertAlmostEqual(conf.particles[0][0][1], 5.0, places=5)
        # follower particle 0 unchanged at (21, 8.5, 5)
        self.assertAlmostEqual(conf.particles[DRIVER_N][0][0], 21.0, places=5)
        # geometry: driver anchor (12,5,5)+5 = (17,5,5); follower (9,8.5,5)+20
        distance = receipt["geometry"]["connected_anchor_distances"][0]["distance"]
        self.assertLess(abs(distance - 12.5), 1e-3,
                        "anchor distance must use the transformed driver anchor")

    def test_driver_unit_conversion_scales_driver_anchor_geometry(self):
        self.parts["driver"]["model_and_units"]["length_unit"] = "nm"
        self.spec["unit_conversion"] = {
            "component": "driver", "from_unit": "nm", "to_unit": "oxDNA_length_unit",
            "length_factor": 2.0, "source": "test fixture factor",
        }
        self.spec["coordinate_transforms"] = []
        # scaled driver x reaches 26*2 = 52 > the 45-unit fixture box: declare
        # an assembly box that contains the scaled driver (the box check runs
        # on real merged positions).
        self.spec["assembly_box"] = [60.0, 12.0, 12.0]
        # Only the APPLIED driver transform (driver anchor x2) puts both anchor
        # distances (c1 ~15.88, c2 ~16.83) inside this band; the untransformed
        # driver anchors give ~4.61/~3.64 and would be refused.
        self.spec["geometry"]["connected_anchor_distance_range"] = [15.0, 17.5]
        _top, conf_text, receipt = self._artifacts()
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])
        from hinge_family.oxdna_conf import Configuration
        conf = Configuration.parse(conf_text)
        # driver particle 0: (1, 5, 5) x 2 = (2, 10, 10) - APPLIED
        self.assertAlmostEqual(conf.particles[0][0][0], 2.0, places=5)
        self.assertAlmostEqual(conf.particles[0][0][1], 10.0, places=5)
        self.assertAlmostEqual(conf.particles[0][0][2], 10.0, places=5)
        distance = receipt["geometry"]["connected_anchor_distances"][0]["distance"]
        self.assertLess(abs(distance - 15.883), 0.01)

    def test_driverless_transforms_keep_identity(self):
        _top, conf_text, _receipt = self._artifacts()
        from hinge_family.oxdna_conf import Configuration
        conf = Configuration.parse(conf_text)
        self.assertAlmostEqual(conf.particles[0][0][0], 1.0, places=6)

    def test_cli_applies_driver_translation_end_to_end(self):
        ws = CliWorkspace()
        try:
            spec = json.loads(ws.assembly_spec.read_text(encoding="utf-8"))
            spec["coordinate_transforms"] = [
                {"component": "driver", "translation": [5.0, 0.0, 0.0]},
                {"component": "follower", "translation": [20.0, 0.0, 0.0]},
            ]
            write_json(ws.assembly_spec, spec)
            result = ws.assemble()
            self.assertEqual(result.returncode, 0, result.stderr)
            from hinge_family.oxdna_conf import Configuration
            conf = Configuration.parse((ws.dir / "out" / "run" / "SYN-DF-1.dat").read_text(encoding="utf-8"))
            self.assertAlmostEqual(conf.particles[0][0][0], 6.0, places=5)
        finally:
            ws.cleanup()


class TestRepairReviewMinorBRecipeStrictness(unittest.TestCase):
    """Minor (b): SOURCE_VERIFIED never silently skips the segment cross-check."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.fx = Fixture(self.tmp)
        self.parts = {
            "driver": self.fx.component_spec("driver"),
            "follower": self.fx.component_spec("follower"),
        }

    def tearDown(self):
        self._tmp.cleanup()

    def _source_verified(self, recipe: dict) -> dict:
        path = self.tmp / "recipe.json"
        path.write_text(json.dumps(recipe), encoding="utf-8")
        spec = self.fx.assembly_spec(mode="SOURCE_VERIFIED")
        spec["interface_recipe_ref"] = {
            "path": "recipe.json",
            "sha256": sha256_bytes(path.read_bytes()),
            "status": "SOURCE_CONFIRMED",
        }
        return spec

    def test_recipe_entry_without_driver_segment_blocks_source(self):
        recipe = copy.deepcopy(RECIPE)
        del recipe["pairs"][0]["driver_segment"]
        spec = self._source_verified(recipe)
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_SOURCE", receipt["assembly_status"])
        self.assertIn("driver_segment", receipt["reason"])
        self.assertIn("never silently skipped", receipt["reason"])

    def test_recipe_entry_without_follower_segment_blocks_source(self):
        recipe = copy.deepcopy(RECIPE)
        del recipe["pairs"][1]["follower_segment"]
        spec = self._source_verified(recipe)
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_SOURCE", receipt["assembly_status"])
        self.assertIn("follower_segment", receipt["reason"])

    def test_port_without_declared_overhang_segment_blocks_source(self):
        del self.parts["driver"]["ports"][0]["chemistry"]["overhang_segment"]
        spec = self._source_verified(RECIPE)
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("BLOCKED_SOURCE", receipt["assembly_status"])
        self.assertIn("overhang_segment", receipt["reason"])

    def test_candidate_design_stays_permissive_without_recipe(self):
        for part in self.parts.values():
            for port in part["ports"]:
                port["chemistry"].pop("recipe_pair_ref", None)
        spec = self.fx.assembly_spec(mode="CANDIDATE_DESIGN")
        self.assertIsNone(spec.get("interface_recipe_ref"))
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])

    def test_complete_recipe_still_assembles_source_verified(self):
        spec = self._source_verified(copy.deepcopy(RECIPE))
        receipt = aps.assemble(spec, self.parts, self.fx.inputs(), recipe_base=self.tmp)
        self.assertEqual("ASSEMBLED_STATIC_ONLY", receipt["assembly_status"], receipt["reason"])


if __name__ == "__main__":
    unittest.main()
