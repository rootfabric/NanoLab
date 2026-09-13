"""LLM arm driver for EX-NL4-002-E3-LLM-R1 (WO-NL4-002).

Sequential adaptive loop, one candidate per invocation:

  python .../tools/llm_arm_driver.py run    --run-seq N --variant V --seed S
  python .../tools/llm_arm_driver.py replay

`run` validates the raw proposal through the frozen BoundedAgent +
narrowed allowlist (out-of-allowlist / duplicate candidate => rejection
recorded, budget NOT spent), then executes exactly one run through the
REAL executor adapter (WSL oxDNA, digest-gated inputs) and appends the
controller result to the run ledger.

`replay` replays the whole ledger through the frozen Controller with
BoundedAgent + ReplayExecutor for the canonical session report and
scoring (budget max_simulations=5 enforced there).

Lives inside the execution dir: scripts/** is import-only for this arm
(WO boundary; code unchanged). stdlib + frozen nl4/e2 toolchain.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "scripts"))

from nl4.real_executor import E3_VARIANTS, STEPS_FIXED, RealExecutorAdapter, ReplayExecutor  # noqa: E402
from nl4.controller import Controller, load_allowlist  # noqa: E402
from nl4.scoring import score_session  # noqa: E402
from nl4.agents.bounded_agent import BoundedAgent, ScriptedBrain  # noqa: E402
from e2.canonical import canonical_json  # noqa: E402

EX_DIR = HERE.parents[1]
EVIDENCE = EX_DIR / "evidence"
LEDGER = EVIDENCE / "llm-runs-ledger.json"
DECISIONS = EVIDENCE / "llm-decisions.json"

GOAL = {
    "target_angle_deg": 90.0,
    "max_simulations": 5,
    "max_wall_minutes": 540.0,
    "integrity_gate": "E2_PROTO_R1_S4_FROZEN",
}

RUN_PREFIX = "E3-LLM"


def narrowed_allowlist() -> dict:
    allowlist = copy.deepcopy(load_allowlist(REPO / "scripts" / "nl4" / "allowlist.json"))
    spec = allowlist["candidate_params"]
    spec["variant"]["values"] = list(E3_VARIANTS)
    spec["steps"]["values"] = [STEPS_FIXED]
    spec["steps"]["default"] = STEPS_FIXED
    allowlist["_e3_narrowing"] = {
        "note": "EX-NL4-002-E3-LLM-R1 runner-level narrowing (same as mech arm); allowlist.json NOT modified",
        "variants": list(E3_VARIANTS),
        "steps": [STEPS_FIXED],
        "reason": "74b excluded by BLOCKED status (EX-NL3-002-PARAM-74B-R1); steps fixed to 50000 by WO-NL4-002 budget",
    }
    return allowlist


def read_ledger() -> list:
    if LEDGER.exists():
        with LEDGER.open("r", encoding="utf-8") as h:
            return json.load(h)
    return []


def write_ledger(runs: list) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(runs) + "\n")


def cmd_run(args) -> int:
    allowlist = narrowed_allowlist()
    runs = read_ledger()
    raw_proposal = {
        "action": "propose_candidate",
        "candidate": {"variant": args.variant, "steps": STEPS_FIXED, "seed": args.seed},
    }
    brain = ScriptedBrain([raw_proposal, {"action": "request_run"}])
    agent = BoundedAgent(brain, GOAL, allowlist)
    proposal = agent.next_action([])
    request = agent.next_action([])
    if request is None or request.get("action") != "request_run":
        rejection = {
            "schema_version": 1,
            "kind": "nl4_e3_llm_rejection",
            "run_seq": args.run_seq,
            "raw_proposal": raw_proposal,
            "bounded_agent_rejected": agent.rejected_actions,
            "budget_spent": False,
        }
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        path = EVIDENCE / f"llm-rejection-{args.run_seq:02d}.json"
        with path.open("w", encoding="utf-8", newline="\n") as h:
            h.write(canonical_json(rejection) + "\n")
        print(f"[driver] REJECTED (no budget spent): {canonical_json(rejection)}")
        return 2
    candidate = request["candidate"]
    if len(runs) >= GOAL["max_simulations"]:
        print("[driver] REJECTED: budget exhausted (5/5 executed)")
        return 3
    if any(r["candidate"] == candidate for r in runs):
        print(f"[driver] REJECTED: CANDIDATE_ALREADY_RUN {candidate}")
        return 4
    if args.run_seq != len(runs) + 1:
        print(f"[driver] run-seq must be {len(runs) + 1}")
        return 5
    executor = RealExecutorAdapter(str(REPO), str(EVIDENCE), run_prefix=RUN_PREFIX)
    result = executor.run(candidate, args.run_seq)
    runs.append(result)
    write_ledger(runs)
    print(canonical_json(result))
    return 0 if result.get("status") == "ANALYSED" else 1


def cmd_replay(args) -> int:
    allowlist = narrowed_allowlist()
    runs = read_ledger()
    if not runs:
        print("[driver] empty ledger")
        return 1
    proposals = []
    for r in runs:
        proposals.append({"action": "propose_candidate", "candidate": r["candidate"]})
        proposals.append({"action": "request_run", "candidate": r["candidate"]})
    replay = ReplayExecutor(list(runs))
    controller = Controller(GOAL, replay, allowlist=allowlist)
    agent = BoundedAgent(ScriptedBrain(proposals), GOAL, allowlist)
    report = controller.run(agent)
    scoring = score_session(report)
    payload = {
        "schema_version": 1,
        "kind": "nl4_e3_llm_arm_execution",
        "execution_id": "EX-NL4-002-E3-LLM-R1",
        "arm": "llm",
        "agent": "llm-brain-r1 (DSH fresh session) via bounded-agent-r1",
        "goal": GOAL,
        "sequential_adaptive": True,
        "allowlist_narrowing": allowlist["_e3_narrowing"],
        "scoring": scoring,
        "session_report": report,
    }
    out = EVIDENCE / "llm-arm-session.json"
    with out.open("w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(payload) + "\n")
    print(canonical_json(scoring))
    print(f"[driver] wrote {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--run-seq", type=int, required=True)
    p_run.add_argument("--variant", required=True)
    p_run.add_argument("--seed", type=int, required=True)
    sub.add_parser("replay")
    args = parser.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    return cmd_replay(args)


if __name__ == "__main__":
    raise SystemExit(main())
