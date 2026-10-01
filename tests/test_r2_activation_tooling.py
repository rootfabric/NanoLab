"""Unit tests for the R2 activation tooling (WO-INFRA3-R2-ACTIVATION-R1).

Science-free: tests exercise run-contract logic, fingerprint parsing/eligibility,
executor evidence lifecycle, supervisor scenario evaluators, gate state machine
and the activation decision machine using temp dirs and fake runners. No systemd,
no network, no oxDNA build, no scientific runs.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from r2 import engine_build
from r2.contract import (
    AttemptLedger,
    AttemptRecord,
    AttemptReuseError,
    attempt_id,
    build_artifact_manifest,
    manifest_digest,
    next_attempt_id,
    sha256_file,
)
from r2.executor import DirectLauncher, RunExecutor, RunSpec
from r2.fingerprint import (
    collect_fingerprint,
    fingerprint_markdown,
    parse_os_release,
    parse_root_filesystem,
    parse_virtualization,
    validate_native_u1,
)
from r2.gates import GateError, GateReport, activation_decision
from r2.supervisor import (
    ci_actions_policy_violation,
    nc_u1_evaluate,
    nc_u2_evaluate,
    nc_u3_evaluate,
    nc_u4_evaluate,
    nc_u5_evaluate,
    parse_is_active,
    scope_argv,
    transient_service_argv,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def ok_fingerprint(hostname: str = "u1-lab") -> dict:
    return {
        "parsed": {
            "hostname": hostname,
            "uname": "Linux u1-lab 6.8.0-40-generic #40-Ubuntu SMP x86_64 GNU/Linux",
            "os_pretty_name": "Ubuntu 24.04.1 LTS",
            "os_id": "ubuntu",
            "os_version_id": "24.04",
            "virtualization": "none",
            "wsl_marker": False,
            "root_filesystem": "ext4",
            "systemd_available": True,
            "tools": {"gcc": "gcc 13.2.0", "cmake": "cmake 3.28.3"},
        }
    }


def fake_runner(responses: dict | None = None):
    table = responses or {}

    def runner(argv):
        key = " ".join(argv)
        if key in table:
            return table[key]
        return {"returncode": 0, "stdout": "stub", "stderr": ""}

    return runner


class AttemptIdTest(unittest.TestCase):
    def test_first_attempt_has_no_suffix(self):
        self.assertEqual(attempt_id("S001", 0), "S001")

    def test_retries_get_r_suffixes(self):
        self.assertEqual(attempt_id("S001", 1), "S001-R1")
        self.assertEqual(attempt_id("S001", 2), "S001-R2")

    def test_negative_attempt_rejected(self):
        with self.assertRaises(ValueError):
            attempt_id("S001", -1)

    def test_unsafe_run_base_rejected(self):
        for bad in ("", "a/b", ".."):
            with self.assertRaises(ValueError):
                attempt_id(bad, 0)


class LedgerTest(unittest.TestCase):
    def _record(self, attempt_id_value: str) -> AttemptRecord:
        return AttemptRecord(
            execution_id="EX-TEST",
            attempt_id=attempt_id_value,
            run_base="S001",
            attempt=0,
            command=["true"],
            technical_outcome="COMPLETED",
        )

    def test_append_and_read_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = AttemptLedger(Path(tmp) / "ledger" / "attempts.jsonl")
            ledger.append(self._record("S001"))
            ledger.append(self._record("S001-R1"))
            ids = [entry["attempt_id"] for entry in ledger.entries()]
            self.assertEqual(ids, ["S001", "S001-R1"])

    def test_reuse_rejected_even_after_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = AttemptLedger(Path(tmp) / "l.jsonl")
            failed = self._record("S001")
            failed.technical_outcome = "FAILED_TECHNICAL"
            ledger.append(failed)
            with self.assertRaises(AttemptReuseError):
                ledger.append(self._record("S001"))
            self.assertEqual(ledger.known_attempt_ids(), {"S001"})

    def test_next_attempt_id_skips_known(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = AttemptLedger(Path(tmp) / "l.jsonl")
            ledger.append(self._record("S001"))
            ledger.append(self._record("S001-R1"))
            self.assertEqual(next_attempt_id("S001", ledger), "S001-R2")
            self.assertEqual(next_attempt_id("S002", ledger), "S002")


class ManifestTest(unittest.TestCase):
    def test_manifest_fields_and_determinism(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "out.txt").write_text("hello", encoding="utf-8")
            first = build_artifact_manifest(root, producer="EX-TEST/S001")
            second = build_artifact_manifest(root, producer="EX-TEST/S001")
            self.assertEqual(first, second)
            entry = first[0]
            self.assertEqual(entry["path"], "out.txt")
            self.assertEqual(entry["size"], 5)
            self.assertEqual(entry["sha256"], sha256_file(root / "out.txt"))
            self.assertEqual(entry["producer"], "EX-TEST/S001")
            self.assertEqual(entry["retention"], "raw-local-persistent")
            self.assertEqual(len(entry["sha256"]), 64)
            self.assertEqual(manifest_digest(first), manifest_digest(second))


class FingerprintTest(unittest.TestCase):
    def test_parse_os_release(self):
        values = parse_os_release('PRETTY_NAME="Ubuntu 22.04.5 LTS"\nID=ubuntu\nVERSION_ID="22.04"\n')
        self.assertEqual(values["PRETTY_NAME"], "Ubuntu 22.04.5 LTS")
        self.assertEqual(values["VERSION_ID"], "22.04")

    def test_systemd_detect_virt_rc1_means_none(self):
        self.assertEqual(parse_virtualization({"returncode": 1, "stdout": "", "stderr": ""}), "none")
        self.assertEqual(parse_virtualization({"returncode": 0, "stdout": "kvm\n"}), "kvm")
        self.assertEqual(parse_virtualization({"returncode": 0, "stdout": "none\n"}), "none")

    def test_df_t_parse(self):
        df_output = "Filesystem Type 1024-blocks Used Available Capacity Mounted on\n/dev/sda1 ext4 100 40 60 40% /\n"
        self.assertEqual(parse_root_filesystem({"stdout": df_output, "returncode": 0}), "ext4")

    def test_wsl_marker_detection(self):
        runner = fake_runner({
            "cat /proc/version": {"returncode": 0, "stdout": "Linux version 5.15.153.1-microsoft-standard-WSL2", "stderr": ""},
        })
        fingerprint = collect_fingerprint(runner)
        self.assertTrue(fingerprint["parsed"]["wsl_marker"])

    def test_native_eligibility_ok(self):
        ok, reasons = validate_native_u1(ok_fingerprint())
        self.assertTrue(ok, reasons)
        self.assertEqual(reasons, [])

    def test_outenemy_never_eligible(self):
        ok, reasons = validate_native_u1(ok_fingerprint(hostname="outenemy"))
        self.assertFalse(ok)
        self.assertTrue(any("outenemy" in reason for reason in reasons))

    def test_outenemy_fqdn_form_also_rejected(self):
        # Repair R1 (review NOTE-3): deny-list must survive suffix forms.
        ok, reasons = validate_native_u1(ok_fingerprint(hostname="outenemy.lab.local"))
        self.assertFalse(ok)
        self.assertTrue(any("forbidden as author host" in reason for reason in reasons))

    def test_wsl_host_rejected(self):
        fp = ok_fingerprint()
        fp["parsed"]["wsl_marker"] = True
        ok, reasons = validate_native_u1(fp)
        self.assertFalse(ok)
        self.assertTrue(any("Microsoft" in reason for reason in reasons))

    def test_vm_rejected(self):
        fp = ok_fingerprint()
        fp["parsed"]["virtualization"] = "kvm"
        self.assertFalse(validate_native_u1(fp)[0])

    def test_non_native_fs_rejected(self):
        fp = ok_fingerprint()
        fp["parsed"]["root_filesystem"] = "overlay"
        self.assertFalse(validate_native_u1(fp)[0])

    def test_missing_systemd_rejected(self):
        fp = ok_fingerprint()
        fp["parsed"]["systemd_available"] = False
        self.assertFalse(validate_native_u1(fp)[0])

    def test_markdown_block_deterministic(self):
        first = fingerprint_markdown(ok_fingerprint())
        second = fingerprint_markdown(ok_fingerprint())
        self.assertEqual(first, second)
        self.assertIn("hostname: `u1-lab`", first)


def fake_run_result(returncode: int) -> dict:
    return {"returncode": returncode, "killed": False, "note": ""}


class ExecutorTest(unittest.TestCase):
    class StaticLauncher:
        def __init__(self, returncode: int, killed: bool = False):
            self.returncode = returncode
            self.killed = killed

        def run(self, argv, stdout_path, stderr_path, timeout_seconds, working_directory):
            stdout_path.write_bytes(b"out\n")
            stderr_path.write_bytes(b"err\n")
            return {"returncode": self.returncode, "killed": self.killed, "note": "static"}

    def _spec(self, raw_root: Path, attempt: int = 0) -> RunSpec:
        return RunSpec(
            execution_id="EX-TEST",
            run_base="S001",
            attempt=attempt,
            command=["true"],
            seed=42,
            subject_pins={"engine_commit": engine_build.ENGINE_PINNED_COMMIT},
            raw_root=raw_root,
        )

    def test_completed_attempt_produces_raw_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = AttemptLedger(tmp_path / "attempts.jsonl")
            executor = RunExecutor(ledger, launcher=self.StaticLauncher(0))
            record = executor.execute(self._spec(tmp_path / "raw"))
            self.assertEqual(record.technical_outcome, "COMPLETED")
            self.assertEqual(record.scientific_outcome, "NOT_EVALUATED")
            raw_dir = tmp_path / "raw" / "EX-TEST" / "S001"
            for name in ("stdout.txt", "stderr.txt", "exit.json", "artifact-manifest.json"):
                self.assertTrue((raw_dir / name).is_file(), name)
            exit_meta = json.loads((raw_dir / "exit.json").read_text(encoding="utf-8"))
            self.assertEqual(exit_meta["exit_code"], 0)
            self.assertEqual(exit_meta["seed"], 42)
            manifest_doc = json.loads((raw_dir / "artifact-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest_doc["digest"], record.manifest_digest)
            # stdout/stderr/exit.json are manifest-ed; the manifest file itself
            # cannot contain its own digest and is written last (by design).
            self.assertEqual(len(manifest_doc["manifest"]), 3)
            self.assertEqual(len(ledger.entries()), 1)

    def test_nonzero_exit_is_failed_technical(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = AttemptLedger(tmp_path / "l.jsonl")
            executor = RunExecutor(ledger, launcher=self.StaticLauncher(3))
            record = executor.execute(self._spec(tmp_path / "raw"))
            self.assertEqual(record.technical_outcome, "FAILED_TECHNICAL")
            self.assertEqual(record.exit_code, 3)

    def test_deliberate_kill_is_failed_technical_and_retry_gets_new_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = AttemptLedger(tmp_path / "l.jsonl")
            executor = RunExecutor(ledger, launcher=self.StaticLauncher(None, killed=True))
            killed = executor.execute(self._spec(tmp_path / "raw"))
            self.assertEqual(killed.technical_outcome, "FAILED_TECHNICAL")
            self.assertIsNone(killed.exit_code)
            retry = executor.execute(self._spec(tmp_path / "raw", attempt=1))
            self.assertEqual(retry.attempt_id, "S001-R1")
            self.assertEqual([e["attempt_id"] for e in ledger.entries()], ["S001", "S001-R1"])

    def test_attempt_id_reuse_rejected_before_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = AttemptLedger(tmp_path / "l.jsonl")
            executor = RunExecutor(ledger, launcher=self.StaticLauncher(0))
            executor.execute(self._spec(tmp_path / "raw"))
            with self.assertRaises(AttemptReuseError):
                executor.execute(self._spec(tmp_path / "raw"))

    def test_real_direct_launcher_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = AttemptLedger(tmp_path / "l.jsonl")
            executor = RunExecutor(ledger, launcher=DirectLauncher())
            spec = self._spec(tmp_path / "raw")
            spec.command = [sys.executable, "-c", "print('ok')"]
            record = executor.execute(spec)
            self.assertEqual(record.technical_outcome, "COMPLETED")
            self.assertEqual(record.exit_code, 0)

    def test_timeout_is_killed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = AttemptLedger(tmp_path / "l.jsonl")
            executor = RunExecutor(ledger, launcher=DirectLauncher())
            spec = self._spec(tmp_path / "raw")
            spec.command = [sys.executable, "-c", "import time; time.sleep(30)"]
            spec.timeout_seconds = 1
            record = executor.execute(spec)
            self.assertEqual(record.technical_outcome, "FAILED_TECHNICAL")
            self.assertIsNone(record.exit_code)
            self.assertIn("timeout", record.note)


class SupervisorTest(unittest.TestCase):
    def test_transient_service_argv_is_detached_unit(self):
        argv = transient_service_argv("nanolab-run-1", ["./engine"], working_directory="/tmp/w")
        self.assertEqual(argv[0], "systemd-run")
        self.assertIn("--unit=nanolab-run-1", argv)
        self.assertIn("--working-directory=/tmp/w", argv)
        self.assertEqual(argv[-1], "./engine")

    def test_scope_argv(self):
        argv = scope_argv("nanolab-scope-1", ["./engine"])
        self.assertIn("--scope", argv)
        self.assertEqual(argv[-1], "./engine")

    def test_parse_is_active(self):
        self.assertTrue(parse_is_active({"returncode": 0, "stdout": "active\n"}))
        self.assertFalse(parse_is_active({"returncode": 3, "stdout": "inactive\n"}))
        self.assertFalse(parse_is_active(None))

    def test_ci_lifecycle_violations_detected(self):
        violations = ci_actions_policy_violation([
            "systemctl reboot -i",
            "systemctl shutdown now",
            "kill executor cgroup",
            "rm -rf build",
        ])
        self.assertEqual(len(violations), 3)
        self.assertTrue(all("CI must not own" in item for item in violations))

    def test_nc_evaluators(self):
        self.assertTrue(nc_u1_evaluate(True, True)["pass"])
        self.assertFalse(nc_u1_evaluate(False, True)["pass"])
        self.assertTrue(nc_u2_evaluate(True, True)["pass"])
        self.assertFalse(nc_u2_evaluate(True, False)["pass"])
        self.assertTrue(nc_u3_evaluate(True, True)["pass"])
        self.assertFalse(nc_u3_evaluate(False, True)["pass"])
        self.assertTrue(nc_u4_evaluate(True, True, True)["pass"])
        self.assertFalse(nc_u4_evaluate(True, False, True)["pass"])
        self.assertFalse(nc_u4_evaluate(True, True, False)["pass"])
        ok = nc_u5_evaluate(True, True, True, True)
        self.assertTrue(ok["pass"])
        self.assertFalse(nc_u5_evaluate(True, True, True, False)["pass"])


class GateReportTest(unittest.TestCase):
    def test_initial_status_is_waiting_host(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = GateReport(Path(tmp) / "gates.json")
            self.assertEqual(report.unmet(), ["U1=WAITING_HOST", "U2=WAITING_HOST", "U3=WAITING_HOST", "U4=WAITING_HOST", "U5=WAITING_HOST", "NC-U1=WAITING_HOST", "NC-U2=WAITING_HOST", "NC-U3=WAITING_HOST", "NC-U4=WAITING_HOST", "NC-U5=WAITING_HOST"])
            self.assertFalse(report.all_gates_pass())

    def test_pass_requires_existing_nonempty_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            report = GateReport(tmp_path / "gates.json")
            with self.assertRaises(GateError):
                report.set_status("U1", "PASS", "")
            with self.assertRaises(GateError):
                report.set_status("U1", "PASS", str(tmp_path / "missing.txt"))
            empty = tmp_path / "empty.txt"
            empty.write_text("", encoding="utf-8")
            with self.assertRaises(GateError):
                report.set_status("U1", "PASS", str(empty))
            evidence = tmp_path / "evidence.txt"
            evidence.write_text("build log", encoding="utf-8")
            entry = report.set_status("U1", "PASS", str(evidence))
            self.assertEqual(entry["status"], "PASS")
            # Repair R1 (review MINOR-2): PASS pins the evidence content.
            self.assertEqual(entry["evidence_sha256"], sha256_file(evidence))
            self.assertEqual(entry["evidence_size"], evidence.stat().st_size)
            with self.assertRaises(GateError):
                report.set_status("U9", "PASS", str(evidence))
            with self.assertRaises(GateError):
                report.set_status("U1", "MAGIC", "")

    def test_state_survives_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            evidence = tmp_path / "e.txt"
            evidence.write_text("x", encoding="utf-8")
            GateReport(tmp_path / "gates.json").set_status("NC-U5", "PASS", str(evidence))
            reloaded = GateReport(tmp_path / "gates.json")
            self.assertEqual(reloaded.entry("NC-U5")["status"], "PASS")
            self.assertEqual(reloaded.entry("U1")["status"], "WAITING_HOST")


class ActivationDecisionTest(unittest.TestCase):
    def _all_pass_report(self, tmp: Path) -> GateReport:
        report = GateReport(Path(tmp) / "gates.json")
        for gate_id, _ in report.state["entries"].items():
            evidence = Path(tmp) / f"{gate_id}-evidence.txt"
            evidence.write_text("measured fact", encoding="utf-8")
            report.set_status(gate_id, "PASS", str(evidence))
        return report

    def test_refuses_when_gates_waiting(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = GateReport(Path(tmp) / "gates.json")
            decision = activation_decision(report, ok_fingerprint(), "PASS", "VERIFIED", True)
            self.assertFalse(decision["r2_activated"])
            self.assertEqual(decision["r2_status"], "WAITING_HOST / NOT_ACTIVE")
            self.assertTrue(any("U1=WAITING_HOST" in item for item in decision["unmet"]))

    def test_refuses_without_review_verify_or_human_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self._all_pass_report(tmp)
            for review, verify, gate in ((None, "VERIFIED", True), ("PASS", None, True), ("PASS", "VERIFIED", False)):
                decision = activation_decision(report, ok_fingerprint(), review, verify, gate)
                self.assertFalse(decision["r2_activated"])

    def test_refuses_outenemy_fingerprint_even_when_everything_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self._all_pass_report(tmp)
            decision = activation_decision(report, ok_fingerprint(hostname="outenemy"), "PASS", "VERIFIED", True)
            self.assertFalse(decision["r2_activated"])
            self.assertTrue(any("forbidden as author host" in item for item in decision["unmet"]))

    def test_activated_only_with_every_precondition(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self._all_pass_report(tmp)
            decision = activation_decision(report, ok_fingerprint(hostname="u1-lab"), "PASS", "VERIFIED", True)
            self.assertTrue(decision["r2_activated"], decision["unmet"])
            self.assertEqual(decision["r2_status"], "ACTIVE")
            self.assertEqual(decision["author_u1"], "u1-lab")


class EngineBuildTest(unittest.TestCase):
    def test_pinned_source_check(self):
        runner = fake_runner({
            "git -C /src rev-parse HEAD": {"returncode": 0, "stdout": engine_build.ENGINE_PINNED_COMMIT + "\n", "stderr": ""},
        })
        ok, actual = engine_build.verify_pinned_source(runner, Path("/src"))
        self.assertTrue(ok)
        self.assertEqual(actual, engine_build.ENGINE_PINNED_COMMIT)

    def test_wrong_commit_detected(self):
        runner = fake_runner({
            "git -C /src rev-parse HEAD": {"returncode": 0, "stdout": "deadbeef" * 5, "stderr": ""},
        })
        ok, actual = engine_build.verify_pinned_source(runner, Path("/src"))
        self.assertFalse(ok)
        self.assertEqual(actual, "deadbeef" * 5)

    def test_configure_argv_carries_intended_flags(self):
        argv = engine_build.configure_argv(Path("/src"), Path("/build"))
        self.assertEqual(argv[0], "cmake")
        self.assertEqual(argv[1], "-S")
        for flag in ("-DCMAKE_BUILD_TYPE=Release", "-DDOUBLE=ON", "-DCUDA=OFF", "-DMPI=OFF"):
            self.assertIn(flag, argv)

    def test_cache_pin_verification(self):
        cache = "\n".join(f"{key}:={value}" for key, value in (
            ("CMAKE_BUILD_TYPE", "Release"), ("DOUBLE", "ON"), ("CUDA", "OFF"), ("MPI", "OFF"),
            ("NATIVE_COMPILATION", "ON"), ("JSON_ENABLED", "ON"),
        ))
        values = engine_build.parse_cmake_cache(cache)
        ok, deviations = engine_build.verify_cache_pins(values)
        self.assertTrue(ok, deviations)
        values["CUDA"] = "ON"
        ok, deviations = engine_build.verify_cache_pins(values)
        self.assertFalse(ok)
        self.assertTrue(any("CUDA" in item for item in deviations))

    def test_cache_missing_pin_detected(self):
        ok, deviations = engine_build.verify_cache_pins({"CMAKE_BUILD_TYPE": "Release"})
        self.assertFalse(ok)
        self.assertEqual(len(deviations), 3)

    def test_tree_digest_deterministic_and_content_sensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("one", encoding="utf-8")
            first = engine_build.tree_digest(root)
            self.assertEqual(first, engine_build.tree_digest(root))
            (root / "a.txt").write_text("two", encoding="utf-8")
            self.assertNotEqual(first, engine_build.tree_digest(root))

    def test_provenance_record_rejects_binary_sha_equality_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "oxdna-src"
            (src / ".git").mkdir(parents=True)
            (src / ".git" / "HEAD").write_text("ref: refs/heads/pinned\n", encoding="utf-8")
            (src / "src").mkdir()
            (src / "src" / "main.cpp").write_text("int main() { return 0; }", encoding="utf-8")
            build_dir = tmp_path / "build"
            build_dir.mkdir()
            (build_dir / "oxdna").write_bytes(b"\x7fELF-fake-binary")
            (build_dir / "CMakeCache.txt").write_text(
                "CMAKE_BUILD_TYPE:=Release\nDOUBLE:=ON\nCUDA:=OFF\nMPI:=OFF\n",
                encoding="utf-8",
            )
            record = engine_build.provenance_record(
                src,
                build_dir,
                engine_build.parse_cmake_cache((build_dir / "CMakeCache.txt").read_text(encoding="utf-8")),
                {"gcc": "gcc 13.2.0"},
                build_dir / "build-r2.log",
            )
            self.assertFalse(record["binary_sha_equality_with_r1_required"])
            self.assertEqual(record["source_commit"], "resolved-at-execution")
            self.assertFalse(record["source_commit_verified"])
            self.assertEqual(record["binary"]["size"], len(b"\x7fELF-fake-binary"))
            self.assertEqual(record["cmake_cache_pins"]["DOUBLE"], "ON")
            # Repair R1 (review NOTE-4): a verified commit is embedded as fact.
            verified = engine_build.provenance_record(
                src,
                build_dir,
                engine_build.parse_cmake_cache((build_dir / "CMakeCache.txt").read_text(encoding="utf-8")),
                {"gcc": "gcc 13.2.0"},
                build_dir / "build-r2.log",
                source_commit=engine_build.ENGINE_PINNED_COMMIT,
            )
            self.assertEqual(verified["source_commit"], engine_build.ENGINE_PINNED_COMMIT)
            self.assertTrue(verified["source_commit_verified"])


class CliNegativeControlTest(unittest.TestCase):
    """Dev-host negative controls: the CLI must refuse non-eligible hosts."""

    def _run_cli(self, *argv: str) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT / "scripts")
        return subprocess.run(
            [sys.executable, "-m", "r2.cli", *argv],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
            cwd=str(REPO_ROOT),
        )

    def test_check_host_reports_verdict_and_exit_code(self):
        completed = self._run_cli("check-host")
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], ("ELIGIBLE_U1", "NOT_ELIGIBLE"))
        if payload["hostname"] == "outenemy":
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(payload["status"], "NOT_ELIGIBLE")
            self.assertTrue(any("forbidden as author host" in reason for reason in payload["reasons"]))

    def test_build_engine_blocked_on_ineligible_host(self):
        completed = self._run_cli("check-host")
        payload = json.loads(completed.stdout)
        if payload["eligible"]:
            self.skipTest("host is eligible; BLOCKED_HOST path not exercisable here")
        blocked = self._run_cli("build-engine", "--src", "/tmp", "--build-dir", "/tmp/r2-build-probe")
        self.assertEqual(blocked.returncode, 2)
        self.assertEqual(json.loads(blocked.stdout)["status"], "BLOCKED_HOST")

    def test_run_blocked_on_ineligible_host(self):
        completed = self._run_cli("check-host")
        payload = json.loads(completed.stdout)
        if payload["eligible"]:
            self.skipTest("host is eligible; BLOCKED_HOST path not exercisable here")
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "spec.json"
            spec_path.write_text(json.dumps({
                "execution_id": "EX-PROBE",
                "run_base": "P001",
                "attempt": 0,
                "command": ["true"],
            }), encoding="utf-8")
            blocked = self._run_cli("run", "--spec", str(spec_path), "--ledger", str(Path(tmp) / "l.jsonl"))
            self.assertEqual(blocked.returncode, 2)
            self.assertEqual(json.loads(blocked.stdout)["status"], "BLOCKED_HOST")
            self.assertFalse((Path(tmp) / "l.jsonl").exists())

    def test_activation_check_refuses_fresh_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "gates.json"
            GateReport(report_path)  # creates WAITING_HOST state on save-less load
            report = GateReport(report_path)
            report.save()
            completed = self._run_cli(
                "activation-check", "--report", str(report_path),
                "--fingerprint", "",
                "--review-verdict", "PASS",
                "--verify-verdict", "VERIFIED",
                "--human-gate-approved",
            )
            self.assertEqual(completed.returncode, 2)
            decision = json.loads(completed.stdout)
            self.assertFalse(decision["r2_activated"])
            self.assertIn("fingerprint frozen (no fingerprint provided)", decision["unmet"])

    def test_nc_plan_safe_anywhere(self):
        completed = self._run_cli("nc-plan", "--nc", "NC-U5")
        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["control"], "NC-U5")
        self.assertIn("FAILED_TECHNICAL", payload["procedure"])

    def test_gate_pass_blocked_or_rejected(self):
        # Repair R1 (review MINOR-1): on a non-eligible host the gate command
        # is host-guarded (BLOCKED_HOST); on an eligible host a PASS without
        # evidence is still REJECTED.
        host = json.loads(self._run_cli("check-host").stdout)
        completed = self._run_cli("gate", "--report", "/tmp/r2-repair-probe-gates.json", "--gate", "U1", "--status", "PASS", "--evidence", "")
        payload = json.loads(completed.stdout)
        if host["eligible"]:
            self.assertEqual(completed.returncode, 3)
            self.assertEqual(payload["status"], "REJECTED")
        else:
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(payload["status"], "BLOCKED_HOST")

    def test_nc_verify_blocked_on_ineligible_host(self):
        host = json.loads(self._run_cli("check-host").stdout)
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "ncu1.json"
            evidence.write_text(json.dumps({"owner_session_gone": True, "job_still_running": False}), encoding="utf-8")
            completed = self._run_cli("nc-verify", "--nc", "NC-U1", "--evidence", str(evidence))
            payload = json.loads(completed.stdout)
            if host["eligible"]:
                self.assertEqual(completed.returncode, 2)
                self.assertFalse(payload["pass"])
                evidence.write_text(json.dumps({"owner_session_gone": True, "job_still_running": True}), encoding="utf-8")
                passed = self._run_cli("nc-verify", "--nc", "NC-U1", "--evidence", str(evidence))
                self.assertEqual(passed.returncode, 0)
                self.assertTrue(json.loads(passed.stdout)["pass"])
            else:
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(payload["status"], "BLOCKED_HOST")


class ConfigContractTest(unittest.TestCase):
    """The pin file must match the code-level contract (no drift)."""

    def test_config_matches_code(self):
        config = json.loads((REPO_ROOT / "config" / "infra" / "r2-activation.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(config["engine"]["pinned_commit"], engine_build.ENGINE_PINNED_COMMIT)
        for key, value in engine_build.EXPECTED_CACHE_PINS.items():
            self.assertEqual(config["engine"]["intended_flags"][key], value)
        self.assertFalse(config["engine"]["binary_sha_equality_with_r1_required"])
        self.assertEqual(config["policy"]["author_u1"], "NOT_ASSIGNED")
        self.assertEqual(config["policy"]["r2_status"], "WAITING_HOST / NOT_ACTIVE")
        self.assertFalse(config["policy"]["r2_activated"])
        self.assertEqual(config["host_eligibility"]["forbidden_hostnames"], ["outenemy"])
        self.assertEqual(config["policy"]["new_science_without_r2"], "HARD_BLOCKED")


if __name__ == "__main__":
    unittest.main()
