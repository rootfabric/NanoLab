from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

REQUIRED_FILES = [
    "PROJECT_CONTROL.md",
    "HARNESS_CONTROL.md",
    "project/plan.json",
    "project/state.json",
    "config/control/harness/project-goals.v1.json",
    "config/control/harness/checkpoint-catalog.v1.json",
    "config/control/harness/harness-policy.v1.json",
    "config/control/harness/scheduler-policy.v1.json",
    "config/control/harness/risk-policy.v1.json",
    "config/control/harness/review-policy.v1.json",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return value


def git_value(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def _unique(items: list[str], label: str, errors: list[str]) -> None:
    if len(items) != len(set(items)):
        errors.append(f"duplicate {label} ids")


def _check_dag(nodes: list[str], deps: dict[str, list[str]], label: str, errors: list[str]) -> None:
    known = set(nodes)
    for node, parents in deps.items():
        for parent in parents:
            if parent not in known:
                errors.append(f"{label} {node} depends on unknown {parent}")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            errors.append(f"cycle in {label} graph at {node}")
            return
        visiting.add(node)
        for parent in deps.get(node, []):
            if parent in known:
                visit(parent)
        visiting.remove(node)
        visited.add(node)

    for node in nodes:
        visit(node)


def check_consistency(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    plan = load_json(root / "project/plan.json")
    state = load_json(root / "project/state.json")
    goals = load_json(root / "config/control/harness/project-goals.v1.json")
    catalog = load_json(root / "config/control/harness/checkpoint-catalog.v1.json")
    scheduler = load_json(root / "config/control/harness/scheduler-policy.v1.json")

    stages = [item["id"] for item in plan.get("stages", [])]
    tasks = [item["id"] for item in plan.get("tasks", [])]
    experiments = [item["id"] for item in plan.get("experiments", [])]
    _unique(stages, "stage", errors)
    _unique(tasks, "task", errors)
    _unique(experiments, "experiment", errors)

    stage_deps = {item["id"]: list(item.get("depends_on", [])) for item in plan.get("stages", [])}
    task_deps = {item["id"]: list(item.get("depends_on", [])) for item in plan.get("tasks", [])}
    _check_dag(stages, stage_deps, "stage", errors)
    _check_dag(tasks, task_deps, "task", errors)

    if set(state.get("task_status", {})) != set(tasks):
        errors.append("project/state.json task_status ids differ from project/plan.json")
    if set(state.get("stage_status", {})) != set(stages):
        errors.append("project/state.json stage_status ids differ from project/plan.json")
    if set(state.get("experiment_status", {})) != set(experiments):
        errors.append("project/state.json experiment_status ids differ from project/plan.json")

    frontier = state.get("frontier")
    next_work = state.get("next_work_order")
    if frontier not in set(stages):
        errors.append(f"unknown frontier: {frontier}")
    if next_work not in set(tasks):
        errors.append(f"unknown next_work_order: {next_work}")

    if {item["id"] for item in goals.get("goals", [])} != set(stages):
        errors.append("project-goals ids differ from plan stages")
    if {item["id"] for item in catalog.get("checkpoints", [])} != set(stages):
        errors.append("checkpoint-catalog ids differ from plan stages")
    if scheduler.get("current_checkpoint") != frontier:
        errors.append("scheduler current_checkpoint differs from project state frontier")
    if scheduler.get("next_work_order") != next_work:
        errors.append("scheduler next_work_order differs from project state")

    branch = git_value(root, "branch", "--show-current")
    head = git_value(root, "rev-parse", "HEAD")
    tree = git_value(root, "rev-parse", "HEAD^{tree}")
    if branch is None:
        warnings.append("git metadata unavailable")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "frontier": frontier,
        "next_work_order": next_work,
        "branch": branch,
        "head": head,
        "tree": tree,
        "counts": {"stages": len(stages), "tasks": len(tasks), "experiments": len(experiments)},
    }
