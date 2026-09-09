#!/usr/bin/env python3
"""E0-R1 e0_freeze.py -- deterministic fixtures, digests and run scaffolds.

Instrument of campaign E0-R1 (protocol E0-PROTO-R1, WO NL2-001).
Frozen BEFORE any run; changes invalidate the campaign subject (exact-head rule).

Modes (each deterministic, no network):
  fixtures   write every NEG/STATUS/UNIT/GEO fixture file from embedded
             byte-exact definitions below
  digests    compute sha256/size of instrument files + fixtures and write
             input_digests.json (referenced by protocol.json)
  scaffolds  read protocol.json and emit runs/<run_id>/manifest.json plus
             events/0001-started.json for every case (campaign START commit
             content); subject_sha is taken from --subject argument

Nothing in this tool encodes any RESULT; expectations live only in
protocol.json (frozen in the freeze commit, before scaffolds exist).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

CAMPAIGN_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = CAMPAIGN_DIR.parents[3]

SYNTHETIC_STAMP = {
    "kind": "SYNTHETIC_TEST_GEOMETRY",
    "synthetic": True,
    "note": "Synthetic test fixture with analytically known values. NOT a physical trajectory; must never be published as physics data.",
}

VALID_WORK_PASSPORT = {
    "schema_version": 1,
    "execution_id": "EX-FIXTURE-000",
    "work_order_id": "WO-FIXTURE-000",
    "checkpoint": "NL2",
    "base_sha": "e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0",
    "branch": "work/fixture-synthetic-r0",
    "risk_class": "LOW",
    "claim_class": "C0_SOFTWARE_ONLY",
    "allowed_paths": ["docs/work/executions/EX-FIXTURE-000/**"],
    "started_at_utc": "2026-09-09T00:00:00Z",
    "status": "STARTED",
}

VALID_RUN_MANIFEST = {
    "schema_version": 1,
    "experiment_id": "E0",
    "campaign_id": "E0-FIXTURE",
    "run_id": "E0-R1-FIXTURE-000",
    "work_order_id": "NL2-001",
    "protocol_revision": "E0-PROTO-R1",
    "subject_sha": "e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0",
    "claim_ceiling": "C0_SOFTWARE_ONLY",
    "model": {"kind": "SYNTHETIC fixture object; no physics model"},
    "inputs": [{"name": "synthetic", "note": "fixture input"}],
    "observables": [{"name": "synthetic", "note": "fixture observable"}],
    "resource_budget": {"cap_cpu_seconds": 1},
    "stop_conditions": ["synthetic fixture stop condition"],
    "status": "STARTED",
}


def valid_run_event(event_id: str, event_type: str, run_id: str, campaign_id: str, extra: dict | None = None, drop: list[str] | None = None) -> dict:
    event = {
        "schema_version": 1,
        "event_id": event_id,
        "timestamp_utc": "2026-09-09T00:00:00Z",
        "experiment_id": "E0",
        "campaign_id": campaign_id,
        "run_id": run_id,
        "event_type": event_type,
        "actor_role": "IMPLEMENTER",
        "subject_sha": "e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0",
        "summary": "SYNTHETIC fixture event for E0-R1 negative control; not a real execution record.",
        "scientific_outcome": None,
    }
    if extra:
        event.update(extra)
    for key in drop or []:
        event.pop(key, None)
    return event


def valid_work_event(event_id: str, event_type: str, extra: dict | None = None) -> dict:
    event = {
        "schema_version": 1,
        "event_id": event_id,
        "timestamp_utc": "2026-09-09T00:00:00Z",
        "execution_id": "EX-FIXTURE-000",
        "work_order_id": "WO-FIXTURE-000",
        "event_type": event_type,
        "actor_role": "IMPLEMENTER",
        "subject_sha": "e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0",
        "summary": "SYNTHETIC fixture event for E0-R1 negative control; not a real execution record.",
    }
    if extra:
        event.update(extra)
    return event


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# fixture definitions (deterministic bytes)
# ---------------------------------------------------------------------------

def fixture_specs() -> dict[str, dict[str, bytes]]:
    specs: dict[str, dict[str, bytes]] = {}

    def add(path: str, payload) -> None:
        specs[path] = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    # --- UNIT fixtures: pure inputs; expected verdicts live in protocol.json ---
    add("fixtures/units/u001_accepted.json", {"input_T": "20C", "claimed_T_oxDNA": 0.097717})
    add("fixtures/units/u002_wrong_20.json", {"input_T": "20C", "claimed_T_oxDNA": 20})
    add("fixtures/units/u002_wrong_293_15.json", {"input_T": "20C", "claimed_T_oxDNA": 293.15})
    add("fixtures/units/u002_wrong_0_29315.json", {"input_T": "20C", "claimed_T_oxDNA": 0.29315})
    add("fixtures/units/u002_wrong_0_0978.json", {"input_T": "20C", "claimed_T_oxDNA": 0.0978})

    # --- GEO fixtures: SYNTHETIC, analytically known ---
    add("fixtures/geometry/g001_right_angle.json", {
        **SYNTHETIC_STAMP,
        "case": "g001_right_angle",
        "vertices": {"A": [0.0, 0.0, 0.0], "B": [1.0, 0.0, 0.0], "C": [1.0, 1.0, 0.0]},
        "queries": [
            {"id": "q1_distance_AC", "type": "distance", "points": ["A", "C"]},
            {"id": "q2_angle_at_B", "type": "angle_deg", "vertex": "B", "arms": ["A", "C"]},
        ],
    })
    add("fixtures/geometry/g002_zero_axis.json", {
        **SYNTHETIC_STAMP,
        "case": "g002_zero_axis",
        "vertices": {"A": [0.0, 0.0, 0.0], "B": [0.0, 0.0, 0.0], "C": [1.0, 0.0, 0.0]},
        "queries": [
            {"id": "q1_distance_AB", "type": "distance", "points": ["A", "B"]},
            {"id": "q2_angle_at_B", "type": "angle_deg", "vertex": "B", "arms": ["A", "C"]},
        ],
    })
    add("fixtures/geometry/g003_orientation_flip.json", {
        **SYNTHETIC_STAMP,
        "case": "g003_orientation_flip",
        "vertices": {"O": [0.0, 0.0, 0.0], "P": [1.0, 0.0, 0.0], "Q": [0.5, 0.8660254037844386, 0.0], "R": [2.0, 0.0, 0.0]},
        "queries": [
            {"id": "q1_angle_P_O_Q", "type": "angle_deg", "vertex": "P", "arms": ["O", "Q"]},
            {"id": "q2_angle_P_R_Q", "type": "angle_deg", "vertex": "P", "arms": ["R", "Q"]},
        ],
    })

    # --- NEG fixtures ---
    def neg_exec(case_dir: str, passport, events: list[dict] | None) -> None:
        base = f"fixtures/negative/{case_dir}/execution"
        if passport is None:
            specs[f"{base}/passport.json"] = b""
        else:
            add(f"{base}/passport.json", passport)
        for event in events or []:
            add(f"{base}/events/{event['event_id']}.json", event)

    def neg_run(case_dir: str, manifest, events: list[dict], artifacts_manifest=None) -> None:
        base = f"fixtures/{case_dir}/run"
        add(f"{base}/manifest.json", manifest)
        for event in events:
            add(f"{base}/events/{event['event_id']}.json", event)
        if artifacts_manifest is not None:
            add(f"{base}/artifacts.manifest.json", artifacts_manifest)

    # N001: empty passport file (0 bytes)
    neg_exec("n001_empty_passport", None, None)
    # N002: truncated JSON (valid prefix, cut mid-token)
    specs["fixtures/negative/n002_truncated_json/execution/passport.json"] = (
        b'{"schema_version": 1, "execution_id": "EX-FIXTURE-000", "work_order_id": "WO-FIX'
    )
    # N003: valid JSON object, all required fields missing
    neg_exec("n003_missing_fields", {}, None)
    # N004: experiment event filename != event_id (experiment_cli).
    # The event payload carries event_id 0002-started but is stored as
    # events/0001-started.json - the identity mismatch is the only violation.
    neg_run(
        "negative/n004_event_filename_mismatch",
        VALID_RUN_MANIFEST,
        [],
    )
    add(
        "fixtures/negative/n004_event_filename_mismatch/run/events/0001-started.json",
        valid_run_event("0002-started", "RUN_STARTED", "E0-R1-FIXTURE-000", "E0-FIXTURE"),
    )
    # N005: first event is not WORK_ORDER_STARTED (work_cli)
    neg_exec(
        "n005_started_not_first",
        VALID_WORK_PASSPORT,
        [valid_work_event("0001-continuation-checkpoint", "CONTINUATION_CHECKPOINT")],
    )
    # N006: corrupt artifact digests (experiment_cli)
    neg_run(
        "negative/n006_bad_artifact_digest",
        VALID_RUN_MANIFEST,
        [valid_run_event("0001-started", "RUN_STARTED", "E0-R1-FIXTURE-000", "E0-FIXTURE")],
        {
            "schema_version": 1,
            "artifacts": [
                {
                    "name": "corrupted.txt",
                    "sha256": "deadbeef",
                    "size_bytes": -1,
                    "producer_run_id": "E0-R1-OTHER-RUN",
                    "subject_sha": "abc123",
                    "storage_location": "fixtures/synthetic",
                }
            ],
        },
    )
    # N007: legacy OBJECT-form artifacts manifest (pre-NL1-002-repair shape, cf.
    # experiments/evidence/E1/E1-R1/runs/*/\*.artifacts.manifest.v1-superseded.json)
    neg_run(
        "negative/n007_legacy_map_manifest",
        VALID_RUN_MANIFEST,
        [valid_run_event("0001-started", "RUN_STARTED", "E0-R1-FIXTURE-000", "E0-FIXTURE")],
        {
            "schema_version": 1,
            "artifacts": {
                "log.txt": {
                    "sha256": "b" * 64,
                    "size_bytes": 4,
                    "producer_run": "E0-R1-FIXTURE-000",
                    "producer_tool": "synthetic",
                    "storage": "fixtures/synthetic",
                }
            },
        },
    )
    # N008: terminal/handoff event not last (work_cli)
    neg_exec(
        "n008_terminal_not_last",
        VALID_WORK_PASSPORT,
        [
            valid_work_event("0001-work-order-started", "WORK_ORDER_STARTED"),
            valid_work_event("0002-handoff-completed", "HANDOFF_COMPLETED"),
            valid_work_event("0003-continuation-checkpoint", "CONTINUATION_CHECKPOINT"),
        ],
    )
    # N009: exit-code contract on graceful rejection path (work_cli)
    broken_passport = dict(VALID_WORK_PASSPORT)
    broken_passport["base_sha"] = "not-a-sha"
    neg_exec("n009_exit_code_contract", broken_passport, None)

    # --- STATUS fixtures (experiment_cli) ---
    # Valid array-form artifacts manifest so that the ONLY violation under test
    # is the status-separation one (no artifacts noise in the verdict).
    status_valid_artifacts = {
        "schema_version": 1,
        "artifacts": [
            {
                "name": "synthetic.txt",
                "sha256": "b" * 64,
                "size_bytes": 4,
                "producer_run_id": "E0-R1-FIXTURE-000",
                "subject_sha": "e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0",
                "storage_location": "fixtures/synthetic",
            }
        ],
    }
    base_events = [
        valid_run_event("0001-started", "RUN_STARTED", "E0-R1-FIXTURE-000", "E0-FIXTURE"),
        valid_run_event("0002-run-completed", "RUN_COMPLETED", "E0-R1-FIXTURE-000", "E0-FIXTURE"),
    ]
    # S001: ANALYSIS_COMPLETED without scientific_outcome
    s001_events = base_events + [
        valid_run_event(
            "0003-analysis-completed", "ANALYSIS_COMPLETED", "E0-R1-FIXTURE-000", "E0-FIXTURE", drop=["scientific_outcome"]
        )
    ]
    neg_run("status/s001_analysis_without_outcome", VALID_RUN_MANIFEST, s001_events, status_valid_artifacts)
    # S002: ANALYSIS_COMPLETED with reviewer-style verdict instead of scientific outcome
    s002_events = base_events + [
        valid_run_event(
            "0003-analysis-completed", "ANALYSIS_COMPLETED", "E0-R1-FIXTURE-000", "E0-FIXTURE", extra={"scientific_outcome": "PASS"}
        )
    ]
    neg_run("status/s002_invalid_outcome_vocab", VALID_RUN_MANIFEST, s002_events, status_valid_artifacts)
    # S003: technical terminal event carrying a scientific claim (gap probe)
    s003_events = [
        valid_run_event("0001-started", "RUN_STARTED", "E0-R1-FIXTURE-000", "E0-FIXTURE"),
        valid_run_event(
            "0002-run-completed", "RUN_COMPLETED", "E0-R1-FIXTURE-000", "E0-FIXTURE", extra={"scientific_outcome": "SUPPORTED"}
        ),
    ]
    neg_run("status/s003_tech_with_sci_claim", VALID_RUN_MANIFEST, s003_events, status_valid_artifacts)

    return specs


INSTRUMENT_FILES = [
    "config/control/harness/artifact-manifest.schema.v1.json",
    "config/control/harness/experiment-event.schema.v1.json",
    "config/control/harness/experiment-run.schema.v1.json",
    "config/control/harness/work-event.schema.v1.json",
    "config/control/harness/work-order.schema.v1.json",
    "config/control/harness/execution-passport.schema.v1.json",
    "scripts/harness/cli.py",
    "scripts/harness/contracts.py",
    "scripts/harness/experiment_cli.py",
    "scripts/harness/work_cli.py",
    "experiments/evidence/E0/E0-R1/tools/e0_freeze.py",
    "experiments/evidence/E0/E0-R1/tools/e0_runner.py",
    "experiments/evidence/E0/E0-R1/tools/geometry_check.py",
    "experiments/evidence/E0/E0-R1/tools/units_check.py",
]


def sha256_of(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def git_blob_digest(repo_root: Path, rev: str, rel_path: str) -> dict:
    import subprocess

    out = subprocess.run(
        ["git", "-C", str(repo_root), "cat-file", "blob", f"{rev}:{rel_path}"],
        capture_output=True,
        check=True,
    ).stdout
    return {"path": rel_path, "sha256": sha256_of(out), "size_bytes": len(out)}


def mode_fixtures() -> None:
    for rel, blob in sorted(fixture_specs().items()):
        path = CAMPAIGN_DIR / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
        print(f"wrote {rel} ({len(blob)} B)")


def mode_digests(rev: str, out_path: Path, extra_files: list[str]) -> None:
    entries = []
    for rel in INSTRUMENT_FILES:
        entries.append(git_blob_digest(REPO_ROOT, rev, rel))
    for rel in extra_files:
        entries.append(git_blob_digest(REPO_ROOT, rev, rel))
    for rel in sorted(fixture_specs()):
        blob = (CAMPAIGN_DIR / rel).read_bytes()
        entries.append({"path": rel, "sha256": sha256_of(blob), "size_bytes": len(blob)})
    payload = {
        "schema_version": 1,
        "kind": "e0_r1_input_digests",
        "digest_base_note": "instrument files are raw git blobs at the given rev; fixture files are campaign-dir bytes as committed in the freeze commit",
        "digest_rev": rev,
        "files": entries,
    }
    write_json(out_path, payload)
    print(f"wrote {out_path} ({len(entries)} entries, rev {rev})")


def mode_scaffolds(subject: str, runs_dir: Path) -> None:
    protocol = json.loads((CAMPAIGN_DIR / "protocol.json").read_text(encoding="utf-8"))
    campaign_id = protocol["campaign_id"]
    protocol_revision = protocol["protocol_revision"]
    work_order_id = protocol["work_order_id"]
    for case in protocol["cases"]:
        run_id = case["run_id"]
        digests_path = runs_dir.parent / "input_digests.json"
        manifest = {
            "schema_version": 1,
            "experiment_id": "E0",
            "campaign_id": campaign_id,
            "run_id": run_id,
            "work_order_id": work_order_id,
            "protocol_revision": protocol_revision,
            "subject_sha": subject,
            "claim_ceiling": "C0_SOFTWARE_ONLY",
            "model": {
                "kind": "none - software contract validation of the frozen control harness (no physics model)",
                "instrument": "scripts/harness validators + config/control/harness v1 schemas at subject_sha (digests: input_digests.json)",
            },
            "inputs": [
                {
                    "name": "instrument_bundle",
                    "ref": str(runs_dir.parent.relative_to(REPO_ROOT) / "input_digests.json").replace("\\", "/"),
                    "note": "sha256/size_bytes of every instrument file (schemas, validators, tools) as raw git blobs at subject_sha",
                }
            ]
            + [
                {"name": entry["path"], "role": "fixture input", "sha256": entry["sha256"], "size_bytes": entry["size_bytes"]}
                for entry in json.loads(digests_path.read_text(encoding="utf-8"))["files"]
                if entry["path"] in set(case.get("input_refs", []))
            ],
            "observables": [
                {
                    "name": case["observable"],
                    "expected": case["expected"],
                    "criterion": case["criterion"],
                }
            ],
            "environment": {
                "family": case["family"],
                "description": case["description"],
                "host": "local Windows workstation (DSH harness session), no paid compute",
                "synthetic": True,
            },
            "seed_policy": {"policy": "NOT_APPLICABLE - fully deterministic software control, no RNG"},
            "resource_budget": {"cap_cpu_seconds": case.get("cap_cpu_seconds", 5), "local_only": True},
            "stop_conditions": [
                "runner or validator technical crash on an intact environment -> RUN_FAILED_TECHNICAL, new run id required for any retry",
                "instrument file drift (sha256 differs from input_digests.json) -> campaign BLOCKED",
                "cpu budget exceeded -> stop",
            ],
            "status": "STARTED",
        }
        write_json(runs_dir / run_id / "manifest.json", manifest)
        started_event = {
            "schema_version": 1,
            "event_id": "0001-started",
            "timestamp_utc": case["frozen_at_utc"],
            "experiment_id": "E0",
            "campaign_id": campaign_id,
            "run_id": run_id,
            "event_type": "RUN_STARTED",
            "actor_role": "IMPLEMENTER",
            "subject_sha": subject,
            "summary": (
                f"Frozen before execution: manifest.json + protocol.json + fixtures + tools committed at subject {subject}; "
                f"case {run_id} (family {case['family']}): {case['description']} Expected outcome is preregistered in protocol.json "
                "and was not changed after seeing any result. Synthetic software control; no physics content."
            ),
            "command": case["command"],
            "exit_code": None,
            "artifact_refs": list(case.get("input_refs", [])),
            "resource_usage": {},
            "scientific_outcome": None,
        }
        write_json(runs_dir / run_id / "events" / "0001-started.json", started_event)
        print(f"scaffolded {run_id}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["fixtures", "digests", "scaffolds"])
    parser.add_argument("--rev", default="HEAD", help="git rev for instrument blob digests (mode=digests)")
    parser.add_argument("--out", help="output path for input_digests.json (mode=digests)")
    parser.add_argument("--extra", nargs="*", default=[], help="extra repo-relative files to digest (mode=digests)")
    parser.add_argument("--subject", help="40-hex campaign subject sha (mode=scaffolds)")
    parser.add_argument("--runs-dir", help="runs output directory (mode=scaffolds)")
    args = parser.parse_args()
    if args.mode == "fixtures":
        mode_fixtures()
    elif args.mode == "digests":
        mode_digests(args.rev, Path(args.out), list(args.extra))
    else:
        if not args.subject or not args.runs_dir:
            print("--subject and --runs-dir are required for scaffolds", file=sys.stderr)
            return 2
        mode_scaffolds(args.subject, Path(args.runs_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
