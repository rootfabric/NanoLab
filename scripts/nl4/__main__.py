"""CLI for the NL4 toolkit (WO-NL4-001): demo runs and validation probes.

Examples:
    python -m nl4 demo --agent random --target 45 --max-simulations 5
    python -m nl4 demo --agent grid --target 45 --max-simulations 5
    python -m nl4 demo --agent scripted --target 45 --max-simulations 5 \
        --proposals proposals.json

Output is canonical JSON (byte-deterministic for the same inputs).
"""
from __future__ import annotations

import argparse
import json
import sys

try:
    from e2.canonical import canonical_json
except ImportError:  # pragma: no cover
    from ..e2.canonical import canonical_json

from .agents.baseline_grid import GridBaseline
from .agents.baseline_random import RandomBaseline
from .agents.bounded_agent import BoundedAgent, ScriptedBrain
from .controller import Controller, load_allowlist
from .mock_executor import MockExecutor
from .scoring import score_session


def _goal(args) -> dict:
    return {
        "target_angle_deg": args.target,
        "max_simulations": args.max_simulations,
        "max_wall_minutes": args.max_wall_minutes,
    }


def _agent(name: str, goal: dict, allowlist: dict, proposals):
    if name == "random":
        return RandomBaseline(goal, allowlist)
    if name == "grid":
        return GridBaseline(goal, allowlist)
    if name == "scripted":
        return BoundedAgent(ScriptedBrain(proposals), goal, allowlist)
    raise SystemExit("unknown agent: " + name)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="nl4", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run one bounded-agent session on the mock executor")
    demo.add_argument("--agent", choices=("random", "grid", "scripted"), required=True)
    demo.add_argument("--target", type=float, required=True)
    demo.add_argument("--max-simulations", type=int, required=True)
    demo.add_argument("--max-wall-minutes", type=float, default=30.0)
    demo.add_argument("--proposals", help="JSON file with raw proposals (scripted agent)")

    check = sub.add_parser("validate-candidate", help="validate one candidate JSON against the allowlist")
    check.add_argument("candidate_json")

    args = parser.parse_args(argv)
    allowlist = load_allowlist()

    if args.command == "validate-candidate":
        candidate = json.loads(args.candidate_json)
        from .controller import normalize_candidate

        normalized, reason = normalize_candidate(candidate, allowlist)
        print(canonical_json({"valid": normalized is not None, "reason": reason, "candidate": normalized}))
        return 0 if normalized is not None else 3

    proposals = None
    if args.proposals:
        with open(args.proposals, "r", encoding="utf-8") as handle:
            proposals = json.load(handle)
    elif args.agent == "scripted":
        proposals = json.loads(sys.stdin.read())
    goal = _goal(args)
    agent = _agent(args.agent, goal, allowlist, proposals)
    controller = Controller(goal, MockExecutor(), allowlist)
    report = controller.run(agent)
    report["scoring"] = score_session(report)
    print(canonical_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
