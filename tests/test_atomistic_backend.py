"""Deterministic stdlib negative tests. These do not execute a calculator."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from atomistic.api import (CLAIM, RunError, ValidationError, digest, read_config,
                           run, validate_config, verify_run, write_json)

ROOT = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "examples/atomistic/cu-demo.json").read_text())
        self.budget_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.budget_dir.cleanup)
        self.budget_patch = mock.patch("atomistic.budget.mission_directory", return_value=Path(self.budget_dir.name))
        self.budget_patch.start()
        self.addCleanup(self.budget_patch.stop)

    def test_valid_config_copy(self):
        canonical = validate_config(self.config)
        self.assertEqual(canonical, self.config)
        self.assertIsNot(canonical, self.config)

    def test_bad_parameters(self):
        cases = [
            ("material", "Al"), ("model", "shell:rm"), ("schema_version", 1),
            ("structure.size", [16, 16, 16]), ("structure.size", [2, 2]),
            ("structure.size", [2, 2, True]), ("structure.size", [1, 1, 1e300]),
            ("structure.kind", "custom"), ("structure.lattice_constant_angstrom", float("nan")),
            ("structure.lattice_constant_angstrom", 0.361),
            ("relaxation.max_steps", 501), ("relaxation.fmax_ev_per_angstrom", 0),
            ("md.steps", 2001), ("md.steps", 2.0), ("md.steps", 10**1000),
            ("md.timestep_fs", float("inf")), ("md.temperature_k", -1),
            ("md.friction_per_fs", "0.01"), ("md.seed", -1), ("md.sample_interval", 0),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=str(value)[:100]):
                config = copy.deepcopy(self.config)
                parts = key.split(".")
                target = config
                for part in parts[:-1]:
                    target = target[part]
                target[parts[-1]] = value
                with self.assertRaises(ValidationError):
                    validate_config(config)

    def test_unknown_keys_units_and_frame_cap(self):
        self.config["structure"]["lattice_constant_nm"] = 0.361
        with self.assertRaises(ValidationError):
            validate_config(self.config)
        del self.config["structure"]["lattice_constant_nm"]
        self.config["md"].update(steps=2000, sample_interval=1)
        with self.assertRaises(ValidationError):
            validate_config(self.config)

    def test_duplicate_input_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text('{"material":"Cu","material":"Al"}')
            with self.assertRaises(ValidationError):
                read_config(path)

    def test_bad_ids_and_duplicate_directory_no_worker(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch("atomistic.api.subprocess.Popen") as popen:
            for name in ["../bad", "/tmp/bad", "bad name", "", ".", "a" * 65]:
                with self.assertRaises(ValidationError):
                    run(self.config, tmp, name)
            (Path(tmp) / "used").mkdir()
            with self.assertRaises(ValidationError):
                run(self.config, tmp, "used")
            popen.assert_not_called()

    def test_unsafe_root_and_timeout(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch("atomistic.api.subprocess.Popen") as popen:
            (Path(tmp) / "alias").symlink_to(tmp, target_is_directory=True)
            for root in [Path(tmp) / "alias", Path(tmp) / "sub" / ".."]:
                with self.assertRaises(ValidationError):
                    run(self.config, root, "test")
            for timeout in [0, 121, True]:
                with self.assertRaises(ValidationError):
                    run(self.config, tmp, "test", timeout_seconds=timeout)
            popen.assert_not_called()

    def test_worker_launch_failure_retained(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch("atomistic.api.subprocess.Popen", side_effect=OSError("test failure")):
            with self.assertRaises(RunError):
                run(self.config, tmp, "launch-failure")
            path = Path(tmp) / "launch-failure"
            manifest = verify_run(path)
            self.assertEqual(manifest["status"], "FAILED")
            self.assertEqual(manifest["scientific_outcome"], "NOT_EVALUATED")
            self.assertTrue((path / "protocol.json").is_file())

    def test_cancellation_terminates_child_without_simulation(self):
        cancelled = threading.Event()
        cancelled.set()
        child = mock.Mock()
        child.poll.return_value = None
        child.wait.return_value = -15
        with tempfile.TemporaryDirectory() as tmp, mock.patch("atomistic.api._subject", return_value={}), mock.patch("atomistic.api.subprocess.Popen", return_value=child) as popen:
            with self.assertRaisesRegex(RunError, "CANCELLED"):
                run(self.config, tmp, "cancelled", cancel_event=cancelled)
            child.terminate.assert_called_once()
            args, kwargs = popen.call_args
            self.assertNotIn("shell", kwargs)
            self.assertEqual(kwargs["env"]["OPENBLAS_NUM_THREADS"], "1")
            self.assertEqual(verify_run(Path(tmp) / "cancelled")["failure_class"], "CANCELLED")

    def test_verify_detects_tampering_and_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "evidence.txt").write_text("original")
            manifest = {"schema_version": "atomistic-manifest-v1", "claim_ceiling": CLAIM, "status": "FAILED", "files": {"evidence.txt": digest(path / "evidence.txt")}}
            write_json(path / "manifest.json", manifest)
            verify_run(path)
            (path / "evidence.txt").write_text("tampered")
            with self.assertRaises(RunError):
                verify_run(path)
            manifest["files"] = {"../evidence.txt": {"sha256": "none", "size_bytes": 1}}
            write_json(path / "manifest.json", manifest)
            with self.assertRaises(RunError):
                verify_run(path)

    def test_missing_success_artifacts_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp) / "manifest.json", {"schema_version": "atomistic-manifest-v1", "claim_ceiling": CLAIM, "status": "COMPLETED", "files": {}})
            with self.assertRaises(RunError):
                verify_run(tmp)

    def test_mission_ledger_restart_count_and_serial_guard(self):
        from atomistic import budget
        first = budget.reserve("/tmp/first", 120, 256 * 1024**2)
        with self.assertRaisesRegex(RuntimeError, "active reservation"):
            budget.reserve("/tmp/second", 120, 256 * 1024**2)
        budget.finish(first, "FAILED", 0.5, 100)
        for index in range(7):
            reservation = budget.reserve(f"/tmp/other-output-{index}", 120, 256 * 1024**2)
            budget.finish(reservation, "COMPLETED", 0.5, 100)
        with self.assertRaisesRegex(RuntimeError, "count exhausted"):
            budget.reserve("/tmp/new-root", 120, 256 * 1024**2)
        ledger = json.loads(next(Path(self.budget_dir.name).glob("*.json")).read_text())
        self.assertEqual(len(ledger["runs"]), 8)
        self.assertEqual(sum(row["charged_seconds"] for row in ledger["runs"]), 4)


@unittest.skipUnless(__import__("os").environ.get("NANOLAB_REAL_ATOMISTIC_TEST") == "1", "real MD requires explicit pilot budget; use dedicated integration command")
class RealIntegrationTest(unittest.TestCase):
    def test_real_engine(self):
        # Explicit opt-in only; ordinary unittest discovery remains stdlib-only.
        from atomistic.integration import check_real_run
        import os
        check_real_run(os.environ.get("NANOLAB_ATOMISTIC_OUTPUT_ROOT"), os.environ.get("NANOLAB_ATOMISTIC_RUN_ID", "integration-cu-001"))


if __name__ == "__main__":
    unittest.main()
