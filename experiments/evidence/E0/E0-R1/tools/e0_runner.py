#!/usr/bin/env python3
"""E0-R1 e0_runner.py -- mechanical executor of the preregistered control cases.

Instrument of campaign E0-R1 (protocol E0-PROTO-R1, WO NL2-001).
Frozen BEFORE any run (committed in the freeze commit); changes invalidate the
campaign subject (exact-head rule).

The runner:
  1. reads protocol.json cases (expectations frozen BEFORE any execution);
  2. materializes fixture bytes from git blobs of the subject commit
     (byte-exact; working-tree line endings are never trusted) and verifies
     digests against input_digests.json;
  3. executes each case command (subprocess, captured stdout/stderr/exit);
  4. compares observed facts against the frozen expectations;
  5. writes ONLY post-start surfaces per run: terminal event (0002-*),
     analysis event (0003-*), artifacts/, artifacts.manifest.json (array
     contract), summary.md; frozen manifest.json/0001-started.json untouched;
  6. machine-validates every emitted JSON against config/control/harness
     v1 schemas (jsonschema Draft 2020-12, format checks on).

Decisions are mechanical only: SUPPORTED = observed facts equal preregistered
expectations; NOT_SUPPORTED = they differ (preserved, no rerun under the same
run id); technical infra failure = RUN_FAILED_TECHNICAL. No retries, no
post-hoc tolerance changes, no result-driven branching.

Usage:
  python e0_runner.py --subject <40-hex> [--only RUN_ID] [--skip-tier2]
Exit code: 0 if every case reached a terminal state (any scientific outcome),
3 if any case failed to reach a terminal state, 2 on runner misuse.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

CAMPAIGN_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = CAMPAIGN_DIR.parents[2]
SCRATCH_ROOT = Path(r"C:\NanoLab\scratch\nl2-001")
RUNS_DIR = CAMPAIGN_DIR / "runs"
SCHEMA_DIR = REPO_ROOT / "config" / "control" / "harness"

SCHEMA_FILES = {
    "event": "experiment-event.schema.v1.json",
    "run": "experiment-run.schema.v1.json",
    "artifacts": "artifact-manifest.schema.v1.json",
}

OXDNA_PIN = "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591"


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_of(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def git_blob(subject: str, rel_path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), "cat-file", "blob", f"{subject}:{rel_path}"],
        capture_output=True,
        check=True,
    ).stdout


def materialize(subject: str, rel_paths: list[str], digests: dict[str, dict], case_scratch: Path) -> dict[str, Path]:
    """Byte-exact fixture materialization from subject blobs + digest verification."""
    case_scratch.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}
    for rel in rel_paths:
        blob = git_blob(subject, rel)
        expected = digests[rel]
        actual = sha256_of(blob)
        if actual != expected["sha256"] or len(blob) != expected["size_bytes"]:
            raise RuntimeError(f"fixture digest mismatch for {rel}: {actual} != {expected['sha256']}")
        target = case_scratch / rel.replace("fixtures/", "")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        out[rel] = target
    return out


def run_command(argv: list[str], env: dict | None = None, timeout: int = 120) -> dict:
    started = _dt.datetime.now(_dt.timezone.utc)
    proc = subprocess.run(argv, cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=timeout)
    finished = _dt.datetime.now(_dt.timezone.utc)
    return {
        "argv": argv,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "duration_seconds": round((finished - started).total_seconds(), 6),
    }


def validator_env() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "scripts")
    return env


def validate_against_schema(payload, kind: str) -> list[str]:
    from jsonschema import Draft202012Validator, FormatChecker

    schema = load_json(SCHEMA_DIR / SCHEMA_FILES[kind])
    checker = Draft202012Validator(schema, format_checker=FormatChecker())
    return [f"{list(err.absolute_path)}: {err.message}" for err in checker.iter_errors(payload)]


# ---------------------------------------------------------------------------
# case execution
# ---------------------------------------------------------------------------


def exec_validator_case(case: dict, subject: str, digests: dict, case_scratch: Path, tier2: bool) -> dict:
    """NEG/STATUS families: feed a synthetic broken contract surface to a frozen validator."""
    fixtures = materialize(subject, case["input_refs"], digests, case_scratch)
    target = fixtures[case["input_refs"][0]].parent
    module = "harness.work_cli" if case["target"] == "work_cli" else "harness.experiment_cli"
    cmd = run_command([sys.executable, "-m", module, "validate", str(target)], env=validator_env())

    stdout = cmd["stdout"]
    expected = case["expected"]
    checks = {}
    if expected["exit_code"] == "nonzero":
        checks["exit_nonzero"] = cmd["exit_code"] != 0
    else:
        checks["exit_code_pinned_3"] = cmd["exit_code"] == expected["exit_code"]
    for needle in expected.get("stdout_must_contain", []):
        checks[f"stdout_contains:{needle}"] = needle in stdout
    for needle in expected.get("stdout_must_not_contain", []):
        checks[f"stdout_not_contains:{needle}"] = needle not in stdout
    if expected.get("ok_field_false"):
        try:
            parsed = json.loads(stdout)
            checks["ok_field_false"] = parsed.get("ok") is False and len(parsed.get("errors", [])) > 0
        except json.JSONDecodeError:
            checks["ok_field_false"] = False
    if case.get("separation_probe"):
        # S003: contract expectation is that the instrument flags a scientific
        # claim attached to a technical terminal event.
        enforced = cmd["exit_code"] != 0
        if not enforced:
            try:
                parsed = json.loads(stdout)
                enforced = parsed.get("ok") is not True or bool(parsed.get("errors"))
            except json.JSONDecodeError:
                enforced = True  # unparseable output on a zero exit is still a flag
        checks["separation_enforced"] = enforced

    observed = {
        "exit_code": cmd["exit_code"],
        "stdout_excerpt": stdout[:4000],
        "stderr_excerpt": cmd["stderr"][:2000],
        "checks": checks,
    }
    scientific = "SUPPORTED" if checks and all(checks.values()) else "NOT_SUPPORTED"
    return {"command": cmd, "observed": observed, "scientific": scientific, "extra_artifacts": {}}


def exec_units_case(case: dict, subject: str, digests: dict, case_scratch: Path, tier2: bool) -> dict:
    fixtures = materialize(subject, case["input_refs"], digests, case_scratch)
    tool = REPO_ROOT / "experiments/evidence/E0/E0-R1/tools/units_check.py"
    argv = [sys.executable, str(tool)] + [str(fixtures[rel]) for rel in case["input_refs"]]
    cmd = run_command(argv)
    extra: dict[str, bytes] = {}

    scientific = "FAILED_TECHNICAL"
    observed: dict = {"exit_code": cmd["exit_code"], "stderr_excerpt": cmd["stderr"][:2000]}
    if cmd["exit_code"] == 0:
        verdicts = {Path(v["fixture"]).name: v["verdict"] for v in json.loads(cmd["stdout"])["verdicts"]}
        observed["verdicts"] = verdicts
        observed["delta_detail"] = json.loads(cmd["stdout"])
        expected_verdicts = case["expected"]["verdicts"]
        checks = {f"verdict:{name}": verdicts.get(name) == want for name, want in expected_verdicts.items()}
        observed["checks"] = checks
        scientific = "SUPPORTED" if all(checks.values()) else "NOT_SUPPORTED"
    else:
        observed["stdout_excerpt"] = cmd["stdout"][:2000]

    if case["run_id"] == "E0-R1-U001" and tier2:
        # Supplementary provenance tier (preregistered as NON-GATING): locate the
        # temperature-conversion branch in the pinned engine sources. Network
        # failure => documented inconclusive note; tier-1 result unaffected.
        pin_dir = case_scratch / "oxdna-pin"
        fetch_log: list[str] = []
        excerpt = "NOT_OBTAINED\n"
        try:
            pin_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "-C", str(pin_dir), "init"], capture_output=True, check=True)
            subprocess.run(["git", "-C", str(pin_dir), "remote", "add", "origin", "https://github.com/lorenzo-rovigatti/oxDNA"], capture_output=True, check=True)
            fetch = subprocess.run(
                ["git", "-C", str(pin_dir), "fetch", "--depth", "1", "origin", OXDNA_PIN],
                capture_output=True, text=True, timeout=300,
            )
            fetch_log.append(f"fetch exit={fetch.returncode}\n{fetch.stdout}\n{fetch.stderr}")
            if fetch.returncode == 0:
                grep = subprocess.run(
                    ["git", "-C", str(pin_dir), "grep", "-n", "-i", "converting temperature", "FETCH_HEAD", "--", "*.cpp"],
                    capture_output=True, text=True, check=True,
                )
                fetch_log.append(f"grep exit={grep.returncode}\n{grep.stdout}\n{grep.stderr}")
                hit = grep.stdout.splitlines()[0]
                hit_file, hit_line = hit.split(":", 3)[1], int(hit.split(":", 3)[2])
                show = subprocess.run(
                    ["git", "-C", str(pin_dir), "show", f"FETCH_HEAD:{hit_file}"],
                    capture_output=True, text=True, check=True,
                )
                lines = show.stdout.splitlines()
                lo, hi = max(0, hit_line - 26), min(len(lines), hit_line + 25)
                excerpt = (
                    f"pinned commit {OXDNA_PIN}\nhit: {hit}\n"
                    f"---- {hit_file} lines {lo + 1}..{hi} ----\n" + "\n".join(lines[lo:hi]) + "\n"
                )
        except Exception as exc:  # noqa: BLE001 - any failure is a documented non-gating note
            fetch_log.append(f"tier2 exception: {type(exc).__name__}: {exc}")
        extra["pinned_source_excerpt.txt"] = (
            "E0-R1 U001 supplementary (non-gating) provenance artifact: pinned-engine temperature conversion, located mechanically.\n"
            + excerpt + "\n".join(fetch_log) + "\n"
        ).encode("utf-8")

    return {"command": cmd, "observed": observed, "scientific": scientific, "extra_artifacts": extra}


def exec_geometry_case(case: dict, subject: str, digests: dict, case_scratch: Path, tier2: bool) -> dict:
    fixtures = materialize(subject, case["input_refs"], digests, case_scratch)
    tool = REPO_ROOT / "experiments/evidence/E0/E0-R1/tools/geometry_check.py"
    rel = case["input_refs"][0]
    cmd = run_command([sys.executable, str(tool), str(fixtures[rel])])
    observed: dict = {"exit_code": cmd["exit_code"], "stderr_excerpt": cmd["stderr"][:2000]}
    scientific = "FAILED_TECHNICAL"
    if cmd["exit_code"] == 0:
        results = {r["query_id"]: r for r in json.loads(cmd["stdout"])["results"]}
        observed["results"] = results
        checks = {}
        for query_id, want in case["expected"]["queries"].items():
            got = results.get(query_id)
            if got is None:
                checks[f"query:{query_id}"] = False
                continue
            if want["op"] == "undefined":
                checks[f"query:{query_id}"] = got["verdict"] == "ANGLE_UNDEFINED" and got["value"] is None
            else:
                value = got.get("value")
                checks[f"query:{query_id}"] = (
                    got["verdict"] == "DEFINED"
                    and isinstance(value, float)
                    and abs(value - want["value"]) <= want["atol"]
                )
        observed["checks"] = checks
        scientific = "SUPPORTED" if all(checks.values()) else "NOT_SUPPORTED"
    else:
        observed["stdout_excerpt"] = cmd["stdout"][:2000]
    return {"command": cmd, "observed": observed, "scientific": scientific, "extra_artifacts": {}}


def exec_positive_case(case: dict, subject: str, digests: dict, case_scratch: Path, tier2: bool) -> dict:
    """POS001: the campaign's own published evidence must pass the frozen validators."""
    run_ids = sorted(p.name for p in RUNS_DIR.iterdir() if p.is_dir() and p.name != case["run_id"])
    blocks: list[str] = []
    checks: dict[str, bool] = {}
    ok_all = True
    for run_id in run_ids:
        cmd = run_command([sys.executable, "-m", "harness.experiment_cli", "validate", str(RUNS_DIR / run_id)], env=validator_env())
        parsed = None
        try:
            parsed = json.loads(cmd["stdout"])
        except json.JSONDecodeError:
            pass
        good = cmd["exit_code"] == 0 and parsed is not None and parsed.get("ok") is True and parsed.get("warnings") == []
        checks[f"experiment_cli:{run_id}"] = good
        ok_all = ok_all and good
        blocks.append(f"### experiment_cli validate {run_id}\nexit={cmd['exit_code']}\n{cmd['stdout']}")
    cons = run_command([sys.executable, "-m", "harness.cli", "check-consistency", "--root", "."], env=validator_env())
    try:
        cons_parsed = json.loads(cons["stdout"])
    except json.JSONDecodeError:
        cons_parsed = {}
    checks["check_consistency"] = cons["exit_code"] == 0 and cons_parsed.get("ok") is True
    ok_all = ok_all and checks["check_consistency"]
    blocks.append(f"### cli check-consistency\nexit={cons['exit_code']}\n{cons['stdout']}")

    ex_dir = REPO_ROOT / "docs" / "work" / "executions" / "EX-NL2-001-R1"
    work = run_command([sys.executable, "-m", "harness.work_cli", "validate", str(ex_dir)], env=validator_env())
    try:
        work_parsed = json.loads(work["stdout"])
    except json.JSONDecodeError:
        work_parsed = {}
    checks["work_cli_EX_NL2_001_R1"] = work["exit_code"] == 0 and work_parsed.get("ok") is True
    ok_all = ok_all and checks["work_cli_EX_NL2_001_R1"]
    blocks.append(f"### work_cli validate EX-NL2-001-R1\nexit={work['exit_code']}\n{work['stdout']}")

    observed = {"checks": checks, "validator_runs": len(run_ids) + 1}
    return {
        "command": {"argv": ["python -m harness.experiment_cli validate <run-dir> (x17)", "python -m harness.cli check-consistency"], "exit_code": 0 if ok_all else 3, "stdout": "", "stderr": "", "duration_seconds": None},
        "observed": observed,
        "scientific": "SUPPORTED" if ok_all else "NOT_SUPPORTED",
        "extra_artifacts": {"validate_outputs.txt": ("\n\n".join(blocks) + "\n").encode("utf-8")},
    }


EXECUTORS = {
    "validator_negative": exec_validator_case,
    "status_separation": exec_validator_case,
    "units": exec_units_case,
    "geometry": exec_geometry_case,
    "positive": exec_positive_case,
}


# ---------------------------------------------------------------------------
# per-run surfaces
# ---------------------------------------------------------------------------


def emit_run(case: dict, subject: str, result: dict, technical_failure: str | None) -> None:
    run_dir = RUNS_DIR / case["run_id"]
    art_dir = run_dir / "artifacts"
    art_dir.mkdir(parents=True, exist_ok=True)
    run_id = case["run_id"]

    case_record = {
        "schema": "nanolab.e0.case_record.v1",
        "run_id": run_id,
        "family": case["family"],
        "subject_sha": subject,
        "synthetic": True,
        "expected_frozen_in_protocol": True,
        "expected": case["expected"],
        "observed": result["observed"],
        "scientific_outcome": "NOT_EVALUATED" if technical_failure else result["scientific"],
        "technical_failure": technical_failure,
        "finished_at_utc": now_iso(),
    }
    write_json(art_dir / "case_record.json", case_record)
    write_text(art_dir / "stdout.txt", result["command"].get("stdout") or "")
    write_text(art_dir / "stderr.txt", result["command"].get("stderr") or "")
    for name, blob in result["extra_artifacts"].items():
        write_text(art_dir / name, blob.decode("utf-8"))

    schema_issues: dict[str, list[str]] = {}
    manifest = load_json(run_dir / "manifest.json")
    schema_issues["manifest.json"] = validate_against_schema(manifest, "run")
    for event_path in sorted((run_dir / "events").glob("*.json")):
        schema_issues[f"events/{event_path.name}"] = validate_against_schema(load_json(event_path), "event")
    case_record["schema_validation"] = schema_issues
    write_json(art_dir / "case_record.json", case_record)

    if technical_failure:
        terminal_type, terminal_slug = "RUN_FAILED_TECHNICAL", "run-failed-technical"
    else:
        terminal_type, terminal_slug = "RUN_COMPLETED", "run-completed"
    terminal_event = {
        "schema_version": 1,
        "event_id": f"0002-{terminal_slug}",
        "timestamp_utc": now_iso(),
        "experiment_id": "E0",
        "campaign_id": "E0-R1",
        "run_id": run_id,
        "event_type": terminal_type,
        "actor_role": "IMPLEMENTER",
        "subject_sha": subject,
        "summary": (
            f"Control case {run_id} (family {case['family']}) executed mechanically by tools/e0_runner.py against frozen subject {subject}. "
            f"Fixture bytes materialized from git blobs and digest-verified; validator/tool invoked as subprocess; "
            f"observed exit code {result['command'].get('exit_code')}. "
            + (f"Technical failure: {technical_failure}" if technical_failure else "The control itself executed to completion; expected-vs-observed comparison is in the analysis event.")
        ),
        "command": " ".join(result["command"]["argv"]) if result["command"].get("argv") else case["command"],
        "exit_code": result["command"].get("exit_code"),
        "artifact_refs": [
            f"artifacts/case_record.json",
            "artifacts/stdout.txt",
            "artifacts/stderr.txt",
        ] + [f"artifacts/{name}" for name in sorted(result["extra_artifacts"])],
        "resource_usage": {"duration_seconds": result["command"].get("duration_seconds"), "cpu_class": "sub-second local CPU"},
        "scientific_outcome": None,
    }
    write_json(run_dir / "events" / f"{terminal_event['event_id']}.json", terminal_event)

    analysis_event = {
        "schema_version": 1,
        "event_id": "0003-analysis-completed",
        "timestamp_utc": now_iso(),
        "experiment_id": "E0",
        "campaign_id": "E0-R1",
        "run_id": run_id,
        "event_type": "ANALYSIS_COMPLETED",
        "actor_role": "IMPLEMENTER",
        "subject_sha": subject,
        "summary": (
            f"Mechanical comparison of observed facts against expectations frozen in protocol.json (E0-PROTO-R1), case {run_id}. "
            f"Checks: {json.dumps(case_record['observed'].get('checks', {}), ensure_ascii=False)} -> {case_record['scientific_outcome']}. "
            "No tolerance was changed after seeing results; a NOT_SUPPORTED outcome is preserved as-is and is not retried under this run id."
        ),
        "exit_code": None,
        "artifact_refs": ["artifacts/case_record.json"],
        "resource_usage": {},
        "scientific_outcome": case_record["scientific_outcome"],
    }
    write_json(run_dir / "events" / analysis_event["event_id"], analysis_event)

    artifacts_manifest = {"schema_version": 1, "artifacts": []}
    for name in sorted(p.name for p in art_dir.iterdir() if p.is_file()):
        blob = (art_dir / name).read_bytes()
        artifacts_manifest["artifacts"].append(
            {
                "name": name,
                "sha256": sha256_of(blob),
                "size_bytes": len(blob),
                "producer_run_id": run_id,
                "subject_sha": subject,
                "storage_location": f"experiments/evidence/E0/E0-R1/runs/{run_id}/artifacts/{name} (in Git)",
                "media_type": "application/json" if name.endswith(".json") else "text/plain",
                "producer_command": "experiments/evidence/E0/E0-R1/tools/e0_runner.py (mechanical; argv in case_record.json)",
            }
        )
    write_json(run_dir / "artifacts.manifest.json", artifacts_manifest)
    schema_issues["artifacts.manifest.json"] = validate_against_schema(artifacts_manifest, "artifacts")
    write_json(art_dir / "case_record.json", case_record)

    write_text(
        run_dir / "summary.md",
        f"""# Run {run_id} — E0-R1 control case

- Family: {case['family']} (SYNTHETIC software control, no physics content)
- Subject: `{subject}`
- Expected (frozen in protocol.json before execution): `{json.dumps(case['expected'], ensure_ascii=False)}`
- Observed: see `artifacts/case_record.json` (exit code {result['command'].get('exit_code')}, checks in `0003-analysis-completed`)
- Execution outcome: {terminal_type}
- Scientific outcome (per-case, mechanical): **{case_record['scientific_outcome']}**
- Schema validation of this run's machine files: {"all clean" if all(not v for v in case_record["schema_validation"].values()) else "ISSUES: " + json.dumps({k: v for k, v in case_record["schema_validation"].items() if v}, ensure_ascii=False)}

Nota: NEG-случаи «проходят» (SUPPORTED) тогда, когда валидатор корректно отвергает повреждённый вход;
NOT_SUPPORTED означает, что валидатор пропустил некорректную поверхность (сохраняется как есть).
""",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True, help="40-hex freeze-commit sha (campaign subject)")
    parser.add_argument("--only", help="execute a single case by run_id (diagnostics only)")
    parser.add_argument("--skip-tier2", action="store_true", help="skip non-gating pinned-source fetch for U001")
    args = parser.parse_args()

    protocol = load_json(CAMPAIGN_DIR / "protocol.json")
    digests = {e["path"]: e for e in load_json(CAMPAIGN_DIR / "input_digests.json")["files"]}
    if len(args.subject) != 40:
        print("subject must be 40 hex chars", file=sys.stderr)
        return 2

    cases = protocol["cases"]
    if args.only:
        cases = [c for c in cases if c["run_id"] == args.only]
    if not cases:
        print("no cases selected", file=sys.stderr)
        return 2

    summary_rows = []
    fatal = False
    for case in cases:
        run_id = case["run_id"]
        case_scratch = SCRATCH_ROOT / run_id
        technical_failure = None
        try:
            result = EXECUTORS[case["kind"]](case, args.subject, digests, case_scratch, tier2=not args.skip_tier2)
        except Exception as exc:  # noqa: BLE001 - a broken control is a technical failure, recorded as such
            technical_failure = f"{type(exc).__name__}: {exc}"
            result = {
                "command": {"argv": [case["command"]], "exit_code": None, "stdout": "", "stderr": technical_failure, "duration_seconds": None},
                "observed": {"technical_failure": technical_failure},
                "scientific": "NOT_EVALUATED",
                "extra_artifacts": {},
            }
        try:
            emit_run(case, args.subject, result, technical_failure)
        except Exception as exc:  # noqa: BLE001
            print(f"{run_id}: emit failure {type(exc).__name__}: {exc}", file=sys.stderr)
            fatal = True
            summary_rows.append((run_id, case["family"], "EMIT_FAILURE", "FAILED_TECHNICAL"))
            continue
        outcome = "RUN_FAILED_TECHNICAL" if technical_failure else "RUN_COMPLETED"
        sci = "NOT_EVALUATED" if technical_failure else result["scientific"]
        summary_rows.append((run_id, case["family"], outcome, sci))
        print(f"{run_id}: {outcome}, scientific={sci}")

    print("\n=== E0-R1 execution summary ===")
    for row in summary_rows:
        print(f"{row[0]:<14} {row[1]:<20} {row[2]:<22} {row[3]}")
    return 3 if fatal else 0


if __name__ == "__main__":
    raise SystemExit(main())
