"""Aggregating analysis for EX-NL4-002-E3-MECH-R1 (WO-NL4-002, mechanical arms).

Reads the per-run analysis records and the two arm execution payloads
(random / grid) produced by ``e3_mech_runner.py`` and writes:

- ``evidence/E3-MECH-analysis.json``: per-run ledger (candidates, exit codes,
  wall times, gate aggregates, valid-frame counts, median angle over valid
  frames, score = |median - 90|) and per-arm summaries with honest
  invalid/failed counters;
- ``evidence/E3-MECH-summary.json``: canonical two-arm summary,
  scientific_outcome = MEASURED, explicitly WITHOUT any LLM-arm comparison
  (that arm runs in a separate execution).

stdlib-only; deterministic; canonical JSON output.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from e2.canonical import canonical_json  # noqa: E402
from nl4.scoring import score_run  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EX_DIR = os.path.join(REPO, "docs", "work", "executions", "EX-NL4-002-E3-MECH-R1")
EVIDENCE = os.path.join(EX_DIR, "evidence")
TARGET = 90.0
ARMS = ("random", "grid")


def load(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return json.load(handle)


def run_row(analysis: dict) -> dict:
    stats = analysis.get("angle_stats_valid_frames") or {}
    summary = analysis.get("summary_valid_frames") or {}
    gate_summary = {
        "long_bond_fraction": summary.get("long_bond_fraction"),
        "pairs_fraction_v2": summary.get("pairs_fraction_v2"),
        "displacement_max": summary.get("displacement_max"),
    }
    scored = score_run(
        {
            "median_angle_deg": stats.get("median_deg"),
            **gate_summary,
        },
        TARGET,
    )
    return {
        "run_id": analysis["run_id"],
        "candidate": analysis["candidate"],
        "status": analysis.get("status", "ANALYSED"),
        "exit_code": analysis.get("exit_code"),
        "interrupted_budget": analysis.get("interrupted_budget"),
        "wall_seconds": analysis.get("wall_seconds"),
        "frames_total": analysis.get("frames_total"),
        "frames_valid": analysis.get("frames_valid"),
        "valid_frame_fraction": analysis.get("valid_frame_fraction"),
        "reference_pairs_v2_count": analysis.get("reference_pairs_v2_count"),
        "gate_summary_valid_frames": gate_summary,
        "median_angle_deg_valid_frames": stats.get("median_deg"),
        "integrity_status": scored["status"],
        "score": scored["score"],
    }


def arm_summary(arm: str, rows: list) -> dict:
    scored = [(r["score"], r["run_id"], r["candidate"]) for r in rows if r["score"] is not None]
    scored.sort(key=lambda item: (item[0], item[1]))
    return {
        "arm": arm,
        "runs_executed": len(rows),
        "runs_failed": sum(1 for r in rows if r["status"] == "FAILED"),
        "runs_structurally_invalid": sum(
            1 for r in rows if r["status"] != "FAILED" and r["integrity_status"] == "STRUCTURALLY_INVALID"
        ),
        "runs_scored": len(scored),
        "candidates": [r["candidate"] for r in rows],
        "scores": [
            {"run_id": r["run_id"], "candidate": r["candidate"], "score": r["score"],
             "median_angle_deg": r["median_angle_deg_valid_frames"]}
            for r in rows
        ],
        "best": (
            {"run_id": scored[0][1], "candidate": scored[0][2], "score": scored[0][0]}
            if scored
            else None
        ),
    }


def main() -> int:
    per_arm = {}
    all_rows = []
    for arm in ARMS:
        payload = load(os.path.join(EVIDENCE, f"E3-{arm.upper()}-arm.json"))
        rows = []
        for result in payload["session_report"]["runs"]:
            analysis = load(os.path.join(EX_DIR, result["analysis_evidence_path"]))
            rows.append(run_row(analysis))
        per_arm[arm] = arm_summary(arm, rows)
        all_rows.extend(rows)
    analysis_doc = {
        "schema_version": 1,
        "kind": "nl4_e3_mech_analysis",
        "execution_id": "EX-NL4-002-E3-MECH-R1",
        "work_order_id": "NL4-002",
        "protocol": "docs/work/WO-NL4-002.md + docs/research/E2_PROTO_R1.md (frozen §4 gates, v2 mutual detector)",
        "scoring": "score = |median_angle(valid frames) - 90|, angle convention [0,180] deg",
        "target_angle_deg": TARGET,
        "runs": all_rows,
        "per_arm": per_arm,
        "scientific_outcome": "MEASURED (mechanical arms only; no LLM-arm comparison in this execution)",
    }
    with open(os.path.join(EVIDENCE, "E3-MECH-analysis.json"), "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(analysis_doc) + "\n")

    total_wall = sum(r["wall_seconds"] or 0.0 for r in all_rows)
    summary_doc = {
        "schema_version": 1,
        "kind": "nl4_e3_mech_summary",
        "execution_id": "EX-NL4-002-E3-MECH-R1",
        "scientific_outcome": "MEASURED (E3 mechanical arms; LLM arm NOT run here — separate execution EX-NL4-002-E3-LLM-R1)",
        "claim_class": "C0_SOFTWARE_ONLY / E3 comparison measured, no physics-interpretation",
        "arms": {
            arm: {
                "agent": per_arm[arm]["runs_executed"] and None,
                "runs_executed": per_arm[arm]["runs_executed"],
                "runs_failed": per_arm[arm]["runs_failed"],
                "runs_structurally_invalid": per_arm[arm]["runs_structurally_invalid"],
                "best": per_arm[arm]["best"],
                "scores": per_arm[arm]["scores"],
            }
            for arm in ARMS
        },
        "runs_total": len(all_rows),
        "cumulative_executor_wall_seconds": round(total_wall, 2),
        "deviations": [
            {
                "key": "candidate_space_narrowing",
                "detail": "E3 space = {0b,11b,32b,53b} x {50000} x {201004,202008,203012}; "
                          "74b excluded by BLOCKED status (EX-NL3-002-PARAM-74B-R1); "
                          "steps pinned to 50000 by the WO-NL4-002 budget; "
                          "filtering at runner level only, scripts/nl4/allowlist.json NOT modified",
            },
            {
                "key": "arm_manifests_11b_32b_53b",
                "detail": "verified present at base SHA 592c4a1 (merged from the parametric "
                          "batch branches via main); no copying was required",
            },
            {
                "key": "parallel_runs",
                "detail": "non-adaptive mechanical arms executed their 5 runs concurrently; "
                          "canonical budget accounting via Controller replay with identical "
                          "action order (ReplayExecutor)",
            },
        ],
    }
    with open(os.path.join(EVIDENCE, "E3-MECH-summary.json"), "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(summary_doc) + "\n")
    print(canonical_json(summary_doc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
