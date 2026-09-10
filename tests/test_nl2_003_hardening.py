"""NL2-003 validator hardening tests (provenance & recovery WO).

Closes the accumulated hardening candidates, each with positive/negative
mechanical controls:
- S003: scientific_outcome=SUPPORTED must not ride on non-analysis surfaces;
  ANALYSIS_COMPLETED carries it only with a verification surface;
- O1: in-Git storage_location must carry the manifest campaign_id/run_id
  segments (55 stale entries preserved in superseded E0-R2);
- digest-vs-blob: experiment_cli verify_digests compares manifest sha256/size
  with actual bytes via git blobs (git access is monkeypatched here; the
  canonical smoke test runs against the real repo when the blobs exist);
- emit_run ordering (REPAIR_MAP_F1_R1 §5.1): the artifacts manifest is written
  AFTER the final case_record, so every manifest digest describes the published
  bytes;
- work_cli placeholder timestamps (O2/F3 class): midnight placeholders,
  unparseable stamps, and constant copy timestamps across 3+ events fail;
  published immutable events are grandfathered by exact (execution_id,
  event_id);
- evidence-map.schema.v1.json follows the de-facto campaign convention; the
  required-key core of every published campaign map is checked (stdlib-only).

Run: python -m unittest discover -s tests -t .
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from harness import experiment_cli  # noqa: E402
from harness import work_cli  # noqa: E402
from harness.work_cli import inspect_execution  # noqa: E402

FULL_SHA = "0123456789abcdef0123456789abcdef01234567"


# ---------------------------------------------------------------------------
# fixtures: experiment run dirs
# ---------------------------------------------------------------------------


def experiment_manifest(run_id: str, campaign_id: str = "E0-RX") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "experiment_id": "E0",
        "campaign_id": campaign_id,
        "run_id": run_id,
        "work_order_id": "NL2-003",
        "protocol_revision": "E0-PROTO-RX",
        "subject_sha": FULL_SHA,
        "claim_ceiling": "C0_SOFTWARE_ONLY",
        "model": {"kind": "SYNTHETIC test object"},
        "inputs": [{"name": "synthetic"}],
        "observables": [{"name": "synthetic"}],
        "resource_budget": {"cap_cpu_seconds": 1},
        "stop_conditions": ["synthetic stop"],
        "status": "STARTED",
    }


def experiment_event(event_id: str, event_type: str, run_id: str, campaign_id: str = "E0-RX", timestamp: str = "2026-09-10T12:00:00Z", **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "event_id": event_id,
        "timestamp_utc": timestamp,
        "experiment_id": "E0",
        "campaign_id": campaign_id,
        "run_id": run_id,
        "event_type": event_type,
        "actor_role": "IMPLEMENTER",
        "subject_sha": FULL_SHA,
        "summary": "synthetic test event",
        "scientific_outcome": None,
    }
    payload.update(extra)
    return payload


def build_run_dir(events: list[dict[str, Any]], manifest: dict[str, Any] | None = None, artifacts_manifest: list[dict[str, Any]] | None = None, analysis_artifact: bytes | None = None) -> Path:
    manifest = manifest or experiment_manifest(events[0]["run_id"])
    root = Path(tempfile.mkdtemp()) / manifest["run_id"]
    (root / "events").mkdir(parents=True)
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for item in events:
        target = root / "events" / f"{item['event_id']}.json"
        target.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
    if artifacts_manifest is not None:
        (root / "artifacts.manifest.json").write_text(json.dumps({"schema_version": 1, "artifacts": artifacts_manifest}, indent=2) + "\n", encoding="utf-8")
    if analysis_artifact is not None:
        (root / "artifacts").mkdir(exist_ok=True)
        (root / "artifacts" / "analysis.json").write_bytes(analysis_artifact)
    return root


def validate_run(events: list, **kwargs: Any) -> dict[str, Any]:
    return experiment_cli.inspect_run(build_run_dir(events, **kwargs))


class S003TechnicalScientificSeparationTests(unittest.TestCase):
    def test_supported_on_terminal_event_fails(self) -> None:
        """The preserved S003 gap shape: RUN_COMPLETED carrying SUPPORTED."""
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-S003"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-S003", scientific_outcome="SUPPORTED"),
        ], artifacts_manifest=[])
        self.assertFalse(result["ok"])
        self.assertTrue(any("S003" in item and "RUN_COMPLETED" in item for item in result["errors"]), result["errors"])

    def test_published_gap_fixture_fails(self) -> None:
        """The real published fixture (NL2-001 evidence) must now FAIL closed."""
        fixture = REPO_ROOT / "experiments/evidence/E0/E0-R1/fixtures/status/s003_tech_with_sci_claim/run"
        if not fixture.is_dir():
            self.skipTest("canonical checkout required")
        result = experiment_cli.inspect_run(fixture)
        self.assertFalse(result["ok"])
        self.assertTrue(any("S003" in item for item in result["errors"]), result["errors"])

    def test_supported_on_analysis_with_surface_passes(self) -> None:
        """Legitimate verify-chain: technical terminal (null) -> analysis SUPPORTED with evidence."""
        analysis = json.dumps({"observed": 1, "expected": 1}).encode("utf-8")
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-POS1"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-POS1"),
            experiment_event("0003-analysis-completed", "ANALYSIS_COMPLETED", "E0-RX-POS1", scientific_outcome="SUPPORTED", artifact_refs=["artifacts/analysis.json"]),
        ], artifacts_manifest=[], analysis_artifact=analysis)
        self.assertTrue(result["ok"], result["errors"])

    def test_supported_on_analysis_without_refs_fails(self) -> None:
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-NEG1"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-NEG1"),
            experiment_event("0003-analysis-completed", "ANALYSIS_COMPLETED", "E0-RX-NEG1", scientific_outcome="SUPPORTED"),
        ], artifacts_manifest=[])
        self.assertFalse(result["ok"])
        self.assertTrue(any("S003" in item and "verification surface" in item for item in result["errors"]), result["errors"])

    def test_supported_on_analysis_with_missing_artifact_fails(self) -> None:
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-NEG2"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-NEG2"),
            experiment_event("0003-analysis-completed", "ANALYSIS_COMPLETED", "E0-RX-NEG2", scientific_outcome="SUPPORTED", artifact_refs=["artifacts/absent.json"]),
        ], artifacts_manifest=[])
        self.assertFalse(result["ok"])
        self.assertTrue(any("S003" in item and "verification surface" in item for item in result["errors"]), result["errors"])

    def test_supported_on_checkpoint_event_fails(self) -> None:
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-NEG3"),
            experiment_event("0002-checkpoint", "RUN_CHECKPOINT", "E0-RX-NEG3", scientific_outcome="SUPPORTED"),
        ], artifacts_manifest=[])
        self.assertFalse(result["ok"])
        self.assertTrue(any("S003" in item for item in result["errors"]), result["errors"])

    def test_published_e0_r4_supported_analyses_still_pass(self) -> None:
        """No regression: all published E0-R4 run dirs must stay valid."""
        runs = REPO_ROOT / "experiments/evidence/E0/E0-R4/runs"
        if not runs.is_dir():
            self.skipTest("canonical checkout required")
        for run_dir in sorted(runs.iterdir()):
            with self.subTest(run_dir=run_dir.name):
                result = experiment_cli.inspect_run(run_dir)
                self.assertTrue(result["ok"], result["errors"])


class ExperimentCliMidnightPlaceholderTests(unittest.TestCase):
    """Repair R1 (REVIEWER F-1, path a): the midnight placeholder rule is now
    enforced for experiment events too — same regex as work_cli; the >=3-copy
    rule is deliberately NOT carried over (fast runs stamp terminal+analysis
    within the same second)."""

    def test_valid_run_with_three_midnight_events_fails(self) -> None:
        """A structurally valid run whose three events all carry T00:00:00Z."""
        stamp = "2026-09-09T00:00:00Z"
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-MID", timestamp=stamp),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-MID", timestamp=stamp),
            experiment_event("0003-analysis-completed", "ANALYSIS_COMPLETED", "E0-RX-MID", timestamp=stamp, scientific_outcome="NOT_EVALUATED"),
        ], artifacts_manifest=[])
        self.assertFalse(result["ok"])
        midnight_errors = [item for item in result["errors"] if "midnight placeholder" in item]
        self.assertEqual(len(midnight_errors), 3, result["errors"])

    def test_machine_stamped_run_passes(self) -> None:
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-MIDOK", timestamp="2026-09-09T13:59:55Z"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-MIDOK", timestamp="2026-09-09T13:59:56Z"),
            experiment_event("0003-analysis-completed", "ANALYSIS_COMPLETED", "E0-RX-MIDOK", timestamp="2026-09-09T13:59:56Z", scientific_outcome="NOT_EVALUATED"),
        ], artifacts_manifest=[])
        self.assertTrue(result["ok"], result["errors"])

    def test_midnight_offset_form_is_rejected_too(self) -> None:
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-MIDOFF", timestamp="2026-09-09T00:00:00+00:00"),
        ], artifacts_manifest=[])
        self.assertFalse(result["ok"])
        self.assertTrue(any("midnight placeholder" in item for item in result["errors"]), result["errors"])

    def test_published_s003_fixture_also_flags_midnight(self) -> None:
        fixture = REPO_ROOT / "experiments/evidence/E0/E0-R1/fixtures/status/s003_tech_with_sci_claim/run"
        if not fixture.is_dir():
            self.skipTest("canonical checkout required")
        result = experiment_cli.inspect_run(fixture)
        self.assertFalse(result["ok"])
        self.assertTrue(any("midnight placeholder" in item for item in result["errors"]), result["errors"])

    def test_published_e1_e0_r4_events_are_machine_stamped(self) -> None:
        """No regression: real campaign events carry real machine stamps."""
        targets = [
            REPO_ROOT / "experiments/evidence/E1/E1-R2/runs",
            REPO_ROOT / "experiments/evidence/E0/E0-R4/runs",
        ]
        if not targets[0].is_dir():
            self.skipTest("canonical checkout required")
        for runs in targets:
            for run_dir in sorted(runs.iterdir()):
                with self.subTest(run_dir=run_dir.name):
                    result = experiment_cli.inspect_run(run_dir)
                    self.assertFalse(any("midnight placeholder" in item for item in result["errors"]), result["errors"])


class O1StorageLocationTests(unittest.TestCase):
    def artifact(self, location: str) -> dict[str, Any]:
        return {
            "name": "x.txt",
            "sha256": "a" * 64,
            "size_bytes": 1,
            "producer_run_id": "E0-RX-O1",
            "subject_sha": FULL_SHA,
            "storage_location": location,
        }

    def test_stale_campaign_segment_fails(self) -> None:
        """The historical E0-R2 defect shape: campaign segment names another campaign."""
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-O1", campaign_id="E0-R2"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-O1", campaign_id="E0-R2"),
        ], manifest=experiment_manifest("E0-RX-O1", campaign_id="E0-R2"), artifacts_manifest=[
            self.artifact("experiments/evidence/E0/E0-R1/runs/E0-RX-O1/artifacts/x.txt (in Git)"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("campaign_id as a path segment" in item for item in result["errors"]), result["errors"])

    def test_missing_run_id_segment_fails(self) -> None:
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-O1"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-O1"),
        ], artifacts_manifest=[
            self.artifact("experiments/evidence/E0/E0-RX/runs/other-run/artifacts/x.txt (in Git)"),
        ])
        self.assertFalse(result["ok"])
        self.assertTrue(any("run_id as a path segment" in item for item in result["errors"]), result["errors"])

    def test_correct_location_passes(self) -> None:
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-O1"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-O1"),
        ], artifacts_manifest=[
            self.artifact("experiments/evidence/E0/E0-RX/runs/E0-RX-O1/artifacts/x.txt (in Git)"),
        ])
        self.assertTrue(result["ok"], result["errors"])

    def test_external_storage_scheme_out_of_scope(self) -> None:
        result = validate_run([
            experiment_event("0001-started", "RUN_STARTED", "E0-RX-O1"),
            experiment_event("0002-run-completed", "RUN_COMPLETED", "E0-RX-O1"),
        ], artifacts_manifest=[self.artifact("s3://bucket/E0-RX/E0-RX-O1/x.txt")])
        self.assertTrue(result["ok"], result["errors"])

    def test_published_e0_r4_and_e1_locations_are_not_stale(self) -> None:
        for campaign in ["E0/E0-R4", "E1/E1-R1", "E1/E1-R2"]:
            runs = REPO_ROOT / "experiments/evidence" / campaign / "runs"
            if not runs.is_dir():
                self.skipTest("canonical checkout required")
            for run_dir in sorted(runs.iterdir()):
                with self.subTest(run_dir=run_dir.name):
                    result = experiment_cli.inspect_run(run_dir)
                    self.assertFalse(any("O1" in item for item in result["errors"]), result["errors"])


class VerifyDigestsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._originals = (experiment_cli.git_blob_at, experiment_cli.git_repo_root)

    def tearDown(self) -> None:
        experiment_cli.git_blob_at, experiment_cli.git_repo_root = self._originals

    def _fake_git(self, repo_root: Path) -> None:
        experiment_cli.git_repo_root = lambda start: repo_root

        def blob_at(_root: Path, _rev: str, rel_posix: str) -> bytes:
            path = repo_root / rel_posix
            if not path.is_file():
                raise RuntimeError(f"blob not found: {rel_posix}")
            return path.read_bytes()

        experiment_cli.git_blob_at = blob_at

    def _materialize(self, run_dir: Path, tamper: bool = False) -> None:
        art = run_dir / "artifacts"
        art.mkdir(parents=True, exist_ok=True)
        entries = []
        for name, blob in [("a.txt", b"alpha"), ("b.txt", b"beta")]:
            if tamper and name == "b.txt":
                blob = b"beta-tampered"
            (art / name).write_bytes(blob)
            entries.append({
                "name": name,
                "sha256": hashlib.sha256(b"alpha" if name == "a.txt" else b"beta").hexdigest(),
                "size_bytes": len(b"alpha" if name == "a.txt" else b"beta"),
                "producer_run_id": "E0-RX-DIG",
                "subject_sha": FULL_SHA,
                "storage_location": f"experiments/evidence/E0/E0-RX/runs/E0-RX-DIG/artifacts/{name} (in Git)",
            })
        (run_dir / "artifacts.manifest.json").write_text(json.dumps({"schema_version": 1, "artifacts": entries}, indent=2) + "\n", encoding="utf-8")

    def test_zero_mismatch_on_published_bytes(self) -> None:
        base = Path(tempfile.mkdtemp())
        run_dir = base / "experiments/evidence/E0/E0-RX/runs/E0-RX-DIG"
        (run_dir / "events").mkdir(parents=True)
        self._materialize(run_dir)
        self._fake_git(base)
        result = experiment_cli.verify_digests(base)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["entries_checked"], 2)
        self.assertEqual(result["mismatches"], [])

    def test_tampered_byte_is_reported(self) -> None:
        base = Path(tempfile.mkdtemp())
        run_dir = base / "experiments/evidence/E0/E0-RX/runs/E0-RX-DIG"
        (run_dir / "events").mkdir(parents=True)
        self._materialize(run_dir, tamper=True)
        self._fake_git(base)
        result = experiment_cli.verify_digests(base)
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["mismatches"]), 1)
        self.assertEqual(result["mismatches"][0]["name"], "b.txt")

    def test_missing_blob_fails_closed(self) -> None:
        base = Path(tempfile.mkdtemp())
        run_dir = base / "experiments/evidence/E0/E0-RX/runs/E0-RX-DIG"
        (run_dir / "events").mkdir(parents=True)
        self._materialize(run_dir)
        (run_dir / "artifacts" / "b.txt").unlink()
        self._fake_git(base)
        result = experiment_cli.verify_digests(base)
        self.assertFalse(result["ok"])
        self.assertTrue(any("blob not found" in item for item in result["errors"]), result["errors"])

    def test_no_manifests_found_fails_closed(self) -> None:
        base = Path(tempfile.mkdtemp())
        self._fake_git(base)
        result = experiment_cli.verify_digests(base)
        self.assertFalse(result["ok"])

    def test_canonical_e1_e0_surfaces_zero_mismatch(self) -> None:
        """Mandated run: E1-R1/E1-R2/E0-R4 against real git blobs of HEAD."""
        import subprocess

        def blob_exists(rel: str) -> bool:
            probe = subprocess.run(["git", "-C", str(REPO_ROOT), "cat-file", "-e", f"HEAD:{rel}"])
            return probe.returncode == 0

        targets = [
            REPO_ROOT / "experiments/evidence/E1/E1-R1",
            REPO_ROOT / "experiments/evidence/E1/E1-R2",
            REPO_ROOT / "experiments/evidence/E0/E0-R4",
        ]
        tracked = [str(t.relative_to(REPO_ROOT)).replace("\\", "/") for t in targets]
        if not all(blob_exists(tracked[i] + "/campaign.md") for i in range(3) if (targets[i] / "campaign.md").is_file()):
            self.skipTest("blobs not committed at HEAD yet")
        for target in targets:
            with self.subTest(target=target.name):
                result = experiment_cli.verify_digests(target, rev="HEAD")
                self.assertTrue(result["ok"], json.dumps(result, indent=2)[:2000])


EMIT_RUN_PATH = REPO_ROOT / "experiments/evidence/E0/E0-R1/tools/e0_runner.py"


def load_e0_runner():
    spec = importlib.util.spec_from_file_location("e0_runner_under_test", EMIT_RUN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EmitRunOrderingTests(unittest.TestCase):
    """REPAIR_MAP_F1_R1 §5.1: the manifest must describe the published bytes."""

    def setUp(self) -> None:
        if not EMIT_RUN_PATH.is_file():
            self.skipTest("canonical checkout required")
        self.mod = load_e0_runner()
        self.tmp = Path(tempfile.mkdtemp())
        self.runs_dir = self.tmp / "runs"
        self.runs_dir.mkdir()
        self._originals = (self.mod.RUNS_DIR, dict(self.mod._CTX), self.mod.validate_against_schema)
        self.mod.RUNS_DIR = self.runs_dir
        self.mod._CTX.update({
            "campaign_id": "E0-RX",
            "experiment_id": "E0",
            "fixture_base": "experiments/evidence/E0/E0-R1/fixtures",
            "tools_dir": "experiments/evidence/E0/E0-R1/tools",
            "runs_rel": "experiments/evidence/E0/E0-RX/runs",
        })
        # stdlib-only: schema validation is not under test here, the write ORDER
        # and digest consistency are.
        self.mod.validate_against_schema = lambda payload, kind: []
        # scaffold: frozen manifest.json + 0001-started.json (pre-exist the run)
        run_dir = self.runs_dir / "E0-RX-EMIT"
        (run_dir / "events").mkdir(parents=True)
        (run_dir / "manifest.json").write_text(json.dumps(experiment_manifest("E0-RX-EMIT"), indent=2) + "\n", encoding="utf-8")
        (run_dir / "events" / "0001-started.json").write_text(json.dumps(experiment_event("0001-started", "RUN_STARTED", "E0-RX-EMIT"), indent=2) + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.mod.RUNS_DIR, self.mod._CTX, self.mod.validate_against_schema = self._originals

    def test_manifest_describes_published_bytes(self) -> None:
        case = {"run_id": "E0-RX-EMIT", "family": "UNIT", "expected": {"verdict": "ACCEPTED"}, "command": "synthetic"}
        result = {
            "command": {"argv": ["synthetic-tool"], "exit_code": 0, "stdout": "out", "stderr": "", "duration_seconds": 0.01},
            "observed": {"checks": {"verdict": True}},
            "scientific": "SUPPORTED",
            "extra_artifacts": {},
        }
        self.mod.emit_run(case, FULL_SHA, result, None)
        run_dir = self.runs_dir / "E0-RX-EMIT"
        manifest = json.loads((run_dir / "artifacts.manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["artifacts"], "manifest must not be empty")
        for entry in manifest["artifacts"]:
            blob = (run_dir / "artifacts" / entry["name"]).read_bytes()
            self.assertEqual(entry["sha256"], hashlib.sha256(blob).hexdigest(), f"stale digest for {entry['name']} (F1 class)")
            self.assertEqual(entry["size_bytes"], len(blob), f"stale size for {entry['name']} (F1 class)")
        case_record = json.loads((run_dir / "artifacts" / "case_record.json").read_text(encoding="utf-8"))
        self.assertIn("artifacts.manifest.json", case_record["schema_validation"])
        self.assertTrue((run_dir / "summary.md").is_file())

    def test_entry_counts_match_artifacts(self) -> None:
        case = {"run_id": "E0-RX-EMIT", "family": "NEG", "expected": {"exit_code": "nonzero"}, "command": "synthetic"}
        result = {
            "command": {"argv": ["synthetic-tool"], "exit_code": 3, "stdout": "", "stderr": "err", "duration_seconds": 0.01},
            "observed": {"checks": {}},
            "scientific": "NOT_SUPPORTED",
            "extra_artifacts": {"validate_outputs.txt": b"extra\n"},
        }
        self.mod.emit_run(case, FULL_SHA, result, None)
        run_dir = self.runs_dir / "E0-RX-EMIT"
        manifest = json.loads((run_dir / "artifacts.manifest.json").read_text(encoding="utf-8"))
        on_disk = sorted(p.name for p in (run_dir / "artifacts").iterdir())
        self.assertEqual(sorted(e["name"] for e in manifest["artifacts"]), on_disk)


# ---------------------------------------------------------------------------
# fixtures: work executions
# ---------------------------------------------------------------------------


def work_event(event_id: str, event_type: str, timestamp: str = "2026-09-10T12:00:00Z", execution_id: str = "EX-TEST-R1", **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "event_id": event_id,
        "timestamp_utc": timestamp,
        "execution_id": execution_id,
        "work_order_id": "NL2-003",
        "event_type": event_type,
        "actor_role": "IMPLEMENTER",
        "subject_sha": FULL_SHA,
        "summary": "test event",
        "blocker": None,
    }
    payload.update(extra)
    return payload


def build_execution(events: list[dict[str, Any]], started_at: str = "2026-09-10T11:00:00Z", execution_id: str = "EX-TEST-R1") -> Path:
    root = Path(tempfile.mkdtemp()) / execution_id
    (root / "events").mkdir(parents=True)
    passport = {
        "schema_version": 1,
        "execution_id": execution_id,
        "work_order_id": "NL2-003",
        "checkpoint": "NL2",
        "base_sha": FULL_SHA,
        "branch": "work/test-r1",
        "risk_class": "MEDIUM",
        "claim_class": "C0_SOFTWARE_ONLY",
        "allowed_paths": [],
        "started_at_utc": started_at,
        "status": "IN_PROGRESS",
    }
    (root / "passport.json").write_text(json.dumps(passport, indent=2) + "\n", encoding="utf-8")
    for item in events:
        target = root / "events" / f"{item['event_id']}.json"
        target.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
    return root


class PlaceholderTimestampTests(unittest.TestCase):
    def test_midnight_placeholder_event_fails(self) -> None:
        result = inspect_execution(build_execution([
            work_event("0001-work-order-started", "WORK_ORDER_STARTED", timestamp="2026-09-09T00:00:00Z"),
            work_event("0002-handoff-completed", "HANDOFF_COMPLETED", timestamp="2026-09-09T10:00:00Z"),
        ]))
        self.assertFalse(result["ok"])
        self.assertTrue(any("midnight placeholder" in item for item in result["errors"]), result["errors"])

    def test_midnight_placeholder_passport_fails(self) -> None:
        result = inspect_execution(build_execution([
            work_event("0001-work-order-started", "WORK_ORDER_STARTED"),
        ], started_at="2026-09-09T00:00:00Z"))
        self.assertFalse(result["ok"])
        self.assertTrue(any("started_at_utc is a midnight placeholder" in item for item in result["errors"]), result["errors"])

    def test_unparseable_timestamp_fails(self) -> None:
        result = inspect_execution(build_execution([
            work_event("0001-work-order-started", "WORK_ORDER_STARTED"),
            work_event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", timestamp="14:25:00"),
        ]))
        self.assertFalse(result["ok"])
        self.assertTrue(any("not a parseable ISO-8601" in item for item in result["errors"]), result["errors"])

    def test_missing_timestamp_fails(self) -> None:
        result = inspect_execution(build_execution([
            work_event("0001-work-order-started", "WORK_ORDER_STARTED"),
            work_event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", timestamp=None),
        ]))
        self.assertFalse(result["ok"])
        self.assertTrue(any("timestamp_utc is required" in item for item in result["errors"]), result["errors"])

    def test_constant_copy_across_three_events_fails(self) -> None:
        stamp = "2026-09-10T15:00:00Z"
        result = inspect_execution(build_execution([
            work_event("0001-work-order-started", "WORK_ORDER_STARTED"),
            work_event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", timestamp=stamp),
            work_event("0003-validation-recorded", "VALIDATION_RECORDED", timestamp=stamp),
            work_event("0004-handoff-completed", "HANDOFF_COMPLETED", timestamp=stamp),
        ]))
        self.assertFalse(result["ok"])
        self.assertTrue(any("constant copy timestamp across 3 events" in item for item in result["errors"]), result["errors"])

    def test_two_identical_stamps_stay_allowed(self) -> None:
        stamp = "2026-09-10T15:00:00Z"
        result = inspect_execution(build_execution([
            work_event("0001-work-order-started", "WORK_ORDER_STARTED", timestamp=stamp),
            work_event("0002-implementation-committed", "IMPLEMENTATION_COMMITTED", timestamp=stamp),
            work_event("0003-handoff-completed", "HANDOFF_COMPLETED", timestamp="2026-09-10T16:00:00Z"),
        ]))
        self.assertTrue(result["ok"], result["errors"])

    def test_legacy_whitelisted_batch_execution_passes(self) -> None:
        """EX-NL2-002-R1 published batch events (0002-0004, one stamp) stay valid."""
        stamp = "2026-09-10T11:37:54Z"
        result = inspect_execution(build_execution([
            work_event("0001-work-order-started", "WORK_ORDER_STARTED", timestamp="2026-09-10T11:17:00Z", execution_id="EX-NL2-002-R1"),
            work_event("0002-continuation-checkpoint", "CONTINUATION_CHECKPOINT", timestamp=stamp, execution_id="EX-NL2-002-R1"),
            work_event("0003-validation-recorded", "VALIDATION_RECORDED", timestamp=stamp, execution_id="EX-NL2-002-R1"),
            work_event("0004-handoff-completed", "HANDOFF_COMPLETED", timestamp=stamp, execution_id="EX-NL2-002-R1"),
        ], execution_id="EX-NL2-002-R1"))
        self.assertTrue(result["ok"], result["errors"])

    def test_same_event_ids_in_other_execution_get_no_exemption(self) -> None:
        stamp = "2026-09-10T11:37:54Z"
        result = inspect_execution(build_execution([
            work_event("0001-work-order-started", "WORK_ORDER_STARTED"),
            work_event("0002-continuation-checkpoint", "CONTINUATION_CHECKPOINT", timestamp=stamp),
            work_event("0003-validation-recorded", "VALIDATION_RECORDED", timestamp=stamp),
            work_event("0004-handoff-completed", "HANDOFF_COMPLETED", timestamp=stamp),
        ]))
        self.assertFalse(result["ok"])
        self.assertTrue(any("constant copy timestamp" in item for item in result["errors"]), result["errors"])

    def test_published_ex_nl2_002_r1_still_valid(self) -> None:
        canonical = REPO_ROOT / "docs/work/executions/EX-NL2-002-R1"
        if not canonical.is_dir():
            self.skipTest("canonical checkout required")
        result = inspect_execution(canonical)
        self.assertTrue(result["ok"], result["errors"])


class EvidenceMapSchemaSyncTests(unittest.TestCase):
    """stdlib-only structural check: schema core ↔ published campaign maps."""

    def test_schema_is_campaign_convention(self) -> None:
        schema = json.loads((REPO_ROOT / "config/control/harness/evidence-map.schema.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["kind"]["const"], "evidence_map")
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        self.assertEqual(schema["properties"]["base_sha"]["pattern"], "^[0-9a-f]{40}$")
        for key in ["kind", "campaign_id", "execution_id", "claim", "runs", "failed_or_excluded_runs", "next_action"]:
            self.assertIn(key, schema["required"])
        self.assertNotIn("checkpoint", schema["required"])
        self.assertNotIn("review_verdict", schema["required"])

    def test_published_campaign_maps_carry_schema_core(self) -> None:
        schema = json.loads((REPO_ROOT / "config/control/harness/evidence-map.schema.v1.json").read_text(encoding="utf-8"))
        maps = [
            REPO_ROOT / "experiments/evidence/E1/E1-R1/evidence-map.json",
            REPO_ROOT / "experiments/evidence/E0/E0-R4/evidence-map.json",
            REPO_ROOT / "experiments/evidence/E1/E1-R2/evidence-map.json",
        ]
        if not maps[0].is_file():
            self.skipTest("canonical checkout required")
        for path in maps:
            with self.subTest(map=path.name):
                doc = json.loads(path.read_text(encoding="utf-8"))
                missing = [key for key in schema["required"] if key not in doc]
                self.assertEqual(missing, [])
                self.assertEqual(doc["kind"], "evidence_map")
                self.assertEqual(doc["schema_version"], 1)
                for run in doc["runs"]:
                    self.assertIn("run_id", run)
                    self.assertIn("execution_outcome", run)
                self.assertIn(doc["claim"]["campaign_scientific_outcome"], ["SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE", "NOT_EVALUATED", "INVALIDATED"])

    def test_broken_map_core_is_detected(self) -> None:
        schema = json.loads((REPO_ROOT / "config/control/harness/evidence-map.schema.v1.json").read_text(encoding="utf-8"))
        doc = {"schema_version": 1, "kind": "evidence_map", "campaign_id": "X-R1"}
        missing = [key for key in schema["required"] if key not in doc]
        self.assertTrue(missing)


if __name__ == "__main__":
    unittest.main()
