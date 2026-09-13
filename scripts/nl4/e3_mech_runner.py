"""Runner for the mechanical E3 arms of EX-NL4-002-E3-MECH-R1 (WO-NL4-002).

Determines the candidate sequence of a non-adaptive baseline agent (random
or grid) against the E3-narrowed candidate space, executes all runs in
parallel through ``RealExecutorAdapter`` (smoke: one sequential run), then
replays the identical action stream through the frozen ``Controller`` for
canonical budget accounting and writes the session report + scoring to the
execution evidence dir.

E3 space narrowing (runner-level only; allowlist.json untouched):
variants {0b, 11b, 32b, 53b} x steps {50000} x seeds {201004, 202008, 203012}.
74b is excluded by its BLOCKED status in EX-NL3-002-PARAM-74B-R1.

Usage (from the repo root, with proxy env set for downloads):
  python scripts/nl4/e3_mech_runner.py --arm smoke|random|grid
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from nl4.real_executor import E3_VARIANTS, STEPS_FIXED, RealExecutorAdapter, ReplayExecutor  # noqa: E402
from nl4.controller import Controller, load_allowlist  # noqa: E402
from nl4.scoring import score_session  # noqa: E402
from nl4.agents.baseline_grid import GridBaseline  # noqa: E402
from nl4.agents.baseline_random import RandomBaseline  # noqa: E402
from e2.canonical import canonical_json  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EX_DIR = os.path.join(REPO, "docs", "work", "executions", "EX-NL4-002-E3-MECH-R1")
EVIDENCE = os.path.join(EX_DIR, "evidence")

# Frozen E3 goal (WO-NL4-002 owner decisions; target 90 deg, 5 runs x 50000
# steps). max_wall_minutes is the cumulative executor wall budget for the
# arm's 5 runs (runs execute in parallel; per-run hard cap 1.2 h).
GOAL = {
    "target_angle_deg": 90.0,
    "max_simulations": 5,
    "max_wall_minutes": 400.0,
    "integrity_gate": "E2_PROTO_R1_S4_FROZEN",
}

SMOKE_CANDIDATE = {"variant": "0b", "steps": STEPS_FIXED, "seed": 201004}


def narrowed_allowlist() -> dict:
    """Frozen allowlist copy narrowed to the E3 space (documented deviation)."""
    allowlist = copy.deepcopy(load_allowlist(Path(os.path.join(REPO, "scripts", "nl4", "allowlist.json"))))
    spec = allowlist["candidate_params"]
    spec["variant"]["values"] = [v for v in E3_VARIANTS]
    spec["steps"]["values"] = [STEPS_FIXED]
    spec["steps"]["default"] = STEPS_FIXED
    allowlist["_e3_narrowing"] = {
        "note": "runner-level narrowing for EX-NL4-002-E3-MECH-R1; frozen file scripts/nl4/allowlist.json is NOT modified",
        "variants": list(E3_VARIANTS),
        "steps": [STEPS_FIXED],
        "reason": "74b excluded by BLOCKED status (EX-NL3-002-PARAM-74B-R1); steps fixed to 50000 by WO-NL4-002 budget",
    }
    return allowlist


def collect_candidates(agent, limit: int) -> list:
    """Step a non-adaptive agent and collect its request_run candidates."""
    out = []
    observations = []
    while len(out) < limit:
        action = agent.next_action(observations)
        if action is None or action.get("action") == "stop":
            break
        if action.get("action") == "request_run":
            out.append(dict(action["candidate"]))
    return out[:limit]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("smoke", "random", "grid"), required=True)
    args = parser.parse_args()
    allowlist = narrowed_allowlist()

    if args.arm == "smoke":
        executor = RealExecutorAdapter(REPO, EVIDENCE, run_prefix="E3-SMOKE")
        result = executor.run(SMOKE_CANDIDATE, 1)
        print(canonical_json(result))
        with open(os.path.join(EVIDENCE, "smoke-result.json"), "w", encoding="utf-8", newline="\n") as h:
            h.write(canonical_json(result) + "\n")
        return 0 if result["status"] == "ANALYSED" else 1

    agent_cls = RandomBaseline if args.arm == "random" else GridBaseline
    agent_name = agent_cls.name
    candidates = collect_candidates(agent_cls(GOAL, allowlist), GOAL["max_simulations"])
    print(f"[runner] {agent_name} candidates:", canonical_json(candidates), flush=True)
    executor = RealExecutorAdapter(REPO, EVIDENCE, run_prefix=f"E3-{args.arm.upper()}")
    results = executor.run_parallel(candidates)

    # canonical replay through the frozen Controller (identical action order)
    replay = ReplayExecutor(results)
    controller = Controller(GOAL, replay, allowlist=allowlist)
    report = controller.run(agent_cls(GOAL, allowlist))
    scoring = score_session(report)
    payload = {
        "schema_version": 1,
        "kind": "nl4_e3_arm_execution",
        "execution_id": "EX-NL4-002-E3-MECH-R1",
        "arm": args.arm,
        "agent": agent_name,
        "goal": GOAL,
        "parallel_runs": True,
        "allowlist_narrowing": allowlist["_e3_narrowing"],
        "candidates": candidates,
        "scoring": scoring,
        "session_report": report,
    }
    out_path = os.path.join(EVIDENCE, f"E3-{args.arm.upper()}-arm.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(payload) + "\n")
    print(f"[runner] wrote {out_path}")
    print(canonical_json(scoring))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
