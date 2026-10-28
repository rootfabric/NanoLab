"""C0 planning arithmetic, not host readiness or scientific launch authority."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean


def bytes_to_free(used: int, available: int, target_percent: int = 80) -> int:
    """df uses used/(used+unprivileged available), excluding reserved blocks."""
    if any(type(v) is not int for v in (used, available, target_percent)) or used < 0 or available < 0 or used + available <= 0 or not 0 < target_percent < 100:
        raise ValueError("invalid filesystem byte counts/target")
    return max(0, (100 * used - target_percent * (used + available) + 99) // 100)


def p2_estimate(manifest: dict, slots: int = 2) -> dict:
    if type(slots) is not int or slots < 1:
        raise ValueError("slots must be positive integer")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("missing measured P2 runs")
    groups = {"0b": [], "32b": []}
    ids = set()
    for run in runs:
        if not isinstance(run, dict) or not isinstance(run.get("run_id"), str) or not run["run_id"] or run["run_id"] in ids:
            raise ValueError("missing/duplicate measured run id")
        ids.add(run["run_id"])
        variant = run.get("variant")
        if variant not in groups:
            raise ValueError("unexpected P2 variant")
        seconds = run.get("wall_time_s")
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
            raise ValueError("invalid measured wall_time_s")
        if type(run.get("exit_code")) is not int or run["exit_code"] != 0:
            raise ValueError("technical failures require explicit handling")
        if run.get("steps") != {"0b": 200000, "32b": 150000}[variant]:
            raise ValueError("step count differs from historical reference")
        groups[variant].append(seconds)
    if any(len(v) != 10 for v in groups.values()):
        raise ValueError("historical P2 reference must have 10 runs per primary variant")
    hours = {key: mean(values) / 3600 for key, values in groups.items()}
    job_hours = 64 * sum(hours.values())
    return {"historical_runs": len(runs), "mean_wall_hours": hours, "primary_runs_projected": 128,
            "primary_job_wall_hours": job_hours, "slots": slots,
            "ideal_primary_elapsed_lower_bound_hours": job_hours / slots,
            "frozen_wall_hours_per_platform": 560, "excludes_controls_and_replacements": True,
            "assumptions": "Historical speed unchanged; ideal parallelism; no contention/setup; NOT a new-build benchmark. CPU-hours are not wall-hours.",
            "requires_current_profile_measurement": True, "dispatch_authorized": False}


def service_readiness(system_state: str, critical_units: dict, failed_units: list, classified_unrelated: list) -> dict:
    errors = []
    if system_state not in {"running", "degraded"}:
        errors.append("systemctl is-system-running must report running/degraded, not unit state active")
    if not critical_units:
        errors.append("critical unit inventory is required")
    for unit, status in critical_units.items():
        if status != "active" or unit in failed_units:
            errors.append("critical unit not active: " + unit)
    if system_state == "running" and failed_units:
        errors.append("inconsistent running state and failed-unit list")
    if system_state == "degraded" and not failed_units:
        errors.append("degraded system needs a complete failed-unit inventory")
    for unit in failed_units:
        if unit not in classified_unrelated or unit in critical_units:
            errors.append("unclassified/relevant failed unit: " + unit)
    return {"ok": not errors, "errors": errors, "scientific_dispatch_authorized": False,
            "note": "Unrelated classification needs operator evidence; memory/storage/process-survival gates remain separate."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--p2-manifest", required=True)
    p.add_argument("--slots", type=int, default=2)
    a = p.parse_args()
    try:
        payload = Path(a.p2_manifest).read_bytes()
        result = {"ok": True, "source_sha256": hashlib.sha256(payload).hexdigest(), **p2_estimate(json.loads(payload), a.slots)}
    except (ValueError, OSError, TypeError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
