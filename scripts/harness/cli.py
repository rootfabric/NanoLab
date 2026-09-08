from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contracts import check_consistency, load_json

SCHEMA = "nanolab.control_development_output.v1"


def output(payload: dict, code: int = 0) -> int:
    print(json.dumps({"schema": SCHEMA, **payload}, ensure_ascii=False, indent=2))
    return code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["overview", "check-consistency", "status", "plan", "drive", "close-role", "close-mission"])
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    result = check_consistency(root)

    if args.mode == "check-consistency":
        return output({"command": "CHECK_CONSISTENCY", **result}, 0 if result["ok"] else 3)
    if not result["ok"]:
        return output({"command": args.mode.upper().replace("-", "_"), "ok": False, "error": "CONTRACT_OR_DEPENDENCY_INVALID", "details": result}, 3)

    state = load_json(root / "project/state.json")
    plan = load_json(root / "project/plan.json")
    base = {
        "ok": True,
        "frontier": state["frontier"],
        "next_work_order": state["next_work_order"],
        "experiment_status": state.get("experiment_status", {}),
        "head": result.get("head"),
        "tree": result.get("tree"),
        "branch": result.get("branch"),
    }

    if args.mode in {"overview", "status"}:
        return output({"command": args.mode.upper(), **base})

    task = next((item for item in plan.get("tasks", []) if item["id"] == state["next_work_order"]), None)
    if args.mode in {"plan", "drive"}:
        return output({
            "command": args.mode.upper(),
            **base,
            "next_actor": "DIRECTOR" if task is None else "IMPLEMENTER_OR_DIRECTOR",
            "next_action": None if task is None else task.get("title"),
            "work_order": task,
            "mission_complete": False,
            "human_decision_required": False,
        })

    if args.mode == "close-role":
        return output({
            "command": "CLOSE_ROLE",
            **base,
            "role_exit_allowed": True,
            "note": "Role may end only after durable Git handoff; this command cannot prove that handoff by itself.",
        })

    return output({
        "command": "CLOSE_MISSION",
        **base,
        "mission_exit_allowed": False,
        "mission_complete": False,
        "reason": "Current frontier is not canonically complete; continue or record a real human/blocker gate.",
    }, 8)


if __name__ == "__main__":
    raise SystemExit(main())
