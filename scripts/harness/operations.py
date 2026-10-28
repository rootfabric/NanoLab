"""Read-only operational queue. Recommendations are never launch/merge authority."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

STATES = {"PLANNED", "READY", "IN_PROGRESS", "WAITING_HUMAN", "BLOCKED_HOST",
          "BLOCKED_SOURCE", "BLOCKED_DEPENDENCY", "WAITING_REVIEW", "DONE", "DEFERRED"}
BLOCKED = {"WAITING_HUMAN", "BLOCKED_HOST", "BLOCKED_SOURCE", "BLOCKED_DEPENDENCY", "DEFERRED"}
ROLES = {"HUMAN", "IMPLEMENTER", "REVIEWER", "VERIFIER", "DIRECTOR", "OPERATOR"}
FIELDS = {"schema_version", "id", "title", "track", "status", "actor", "priority",
          "depends_on", "blockers", "resume_condition", "next_action", "evidence_refs",
          "updated_at_utc", "claim_class", "scientific_runs_allowed"}


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load_tasks(root: Path, plan: dict, state: dict) -> dict:
    """Validate all cards together; an invalid card blocks recommendations."""
    directory = plan.get("operational_task_directory")
    if directory is None:
        return {"ok": True, "errors": [], "tasks": []}  # legacy control snapshots
    if directory != "project/operations":
        return {"ok": False, "errors": ["unsupported operational_task_directory"], "tasks": []}
    folder = root / directory
    if folder.is_symlink() or (root / "project").is_symlink() or not folder.is_dir():
        return {"ok": False, "errors": ["missing or unsafe operations directory"], "tasks": []}
    errors, cards = [], []
    paths = sorted(folder.glob("*.json"))
    if not paths:
        errors.append("operations registry is empty")
    for path in paths:
        try:
            if path.is_symlink() or not path.is_file():
                raise ValueError("unsafe task file")
            card = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
            if not isinstance(card, dict) or set(card) != FIELDS:
                raise ValueError("task fields differ from operational-task v1")
            if not isinstance(card["id"], str) or not re.fullmatch(r"[A-Z][A-Z0-9-]+", card["id"]) or path.stem != card["id"]:
                raise ValueError("task id must match filename")
            if type(card["schema_version"]) is not int or card["schema_version"] != 1:
                raise ValueError("invalid task schema version")
            if card["status"] not in STATES or card["actor"] not in ROLES:
                raise ValueError("unknown task status/actor")
            if card["claim_class"] != "C0_SOFTWARE_ONLY" or card["scientific_runs_allowed"] is not False:
                raise ValueError("operational cards cannot authorize science")
            if type(card["priority"]) is not int or card["priority"] < 0:
                raise ValueError("priority must be a nonnegative integer")
            for key in ("title", "track", "next_action", "updated_at_utc"):
                if not isinstance(card[key], str) or not card[key].strip():
                    raise ValueError("empty/non-string " + key)
            for key in ("depends_on", "blockers", "evidence_refs"):
                if not isinstance(card[key], list) or any(not isinstance(v, str) or not v.strip() for v in card[key]):
                    raise ValueError("invalid list " + key)
                if len(card[key]) != len(set(card[key])):
                    raise ValueError("duplicates in " + key)
            if not isinstance(card["resume_condition"], str):
                raise ValueError("resume_condition must be text")
            if card["status"] in BLOCKED and not card["resume_condition"].strip():
                raise ValueError("blocked/deferred task requires resume condition")
            if card["status"] in {"READY", "IN_PROGRESS", "DONE"} and card["blockers"]:
                raise ValueError("ready/active/done task has blockers")
            if card["status"] == "WAITING_HUMAN" and card["actor"] != "HUMAN":
                raise ValueError("WAITING_HUMAN must route to HUMAN")
            from datetime import datetime
            stamp = datetime.fromisoformat(card["updated_at_utc"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("updated_at_utc requires timezone")
            cards.append(card)
        except (ValueError, TypeError, OSError) as exc:
            errors.append(f"{path.name}: {exc}")
    by_id = {c["id"]: c for c in cards}
    canonical = state.get("task_status", {})
    if set(by_id) & set(canonical):
        errors.append("operational task shadows canonical scientific task")
    done = {k for k, v in canonical.items() if v == "ACCEPTED"} | {c["id"] for c in cards if c["status"] == "DONE"}
    visiting, visited = set(), set()
    def visit(key):
        if key in visiting:
            errors.append("operational dependency cycle: " + key)
            return
        if key in visited:
            return
        visiting.add(key)
        for dep in by_id[key]["depends_on"]:
            if dep not in by_id and dep not in canonical:
                errors.append(key + ": unknown dependency " + dep)
            elif dep in by_id:
                visit(dep)
        visiting.remove(key)
        visited.add(key)
    for key in by_id:
        visit(key)
    for card in cards:
        missing = [d for d in card["depends_on"] if d not in done]
        if missing and card["status"] in {"READY", "IN_PROGRESS", "DONE"}:
            errors.append(card["id"] + ": unsatisfied dependencies " + ", ".join(missing))
    return {"ok": not errors, "errors": errors, "tasks": sorted(cards, key=lambda c: (c["priority"], c["id"]))}


def route(state: dict, plan: dict, tasks: list[dict]) -> dict:
    task = next((t for t in plan.get("tasks", []) if t["id"] == state.get("next_work_order")), None)
    status = state.get("task_status", {}).get(state.get("next_work_order"), "UNKNOWN")
    missing = [] if task is None else [d for d in task.get("depends_on", []) if state.get("task_status", {}).get(d) != "ACCEPTED"]
    dispatchable = task is not None and not missing and status in {"READY", "DISPATCHED", "IN_PROGRESS"}
    actor = "HUMAN" if status == "WAITING_HUMAN" else ("IMPLEMENTER" if dispatchable else "DIRECTOR")
    action = task.get("title") if dispatchable else "Resolve canonical gate; do not dispatch the scientific task."
    ready = [c for c in tasks if c["status"] == "READY"]
    return {"canonical_task_status": status, "work_order": task, "dispatchable": dispatchable,
            "next_actor": actor, "next_action": action, "unmet_dependencies": missing,
            "human_decision_required": status == "WAITING_HUMAN" or any(c["status"] == "WAITING_HUMAN" for c in tasks),
            "parallel_ready_work": ready, "operational_tasks": tasks,
            "recommended_operational_task": ready[0] if ready else None,
            "execution_authorized": False, "merge_authorized": False, "mission_complete": False}


def render_markdown(tasks: list[dict]) -> str:
    def text(value):
        return str(value).replace("|", r"\|").replace("\n", " ")
    rows = ["# Текущая операционная очередь NanoLab", "", "Предложения для C0-работы; не разрешение на научный запуск или merge.", "",
            "| Задача | Статус | Исполнитель | Следующее действие / условие возврата |", "|---|---|---|---|"]
    for c in tasks:
        rows.append("| " + " | ".join(map(text, [c["id"], c["status"], c["actor"], c["next_action"] + (" / " + c["resume_condition"] if c["resume_condition"] else "")])) + " |")
    return "\n".join(rows) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        plan = json.loads((root / "project/plan.json").read_text())
        state = json.loads((root / "project/state.json").read_text())
        result = load_tasks(root, plan, state)
    except (ValueError, OSError) as exc:
        result = {"ok": False, "errors": [str(exc)], "tasks": []}
    print(render_markdown(result["tasks"]) if args.format == "markdown" and result["ok"] else json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
