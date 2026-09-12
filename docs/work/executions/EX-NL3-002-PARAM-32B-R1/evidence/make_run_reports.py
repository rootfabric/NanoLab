"""Collect run reports for EX-NL3-002-PARAM-32B-R1 from the per-run marker files.

The robust launcher (setsid/nohup, docs the 11b wrapper-timeout incident lesson)
wrote start_epoch.txt / exit_code.txt / end_epoch.txt inside each run dir, so
walls and exit codes are read from the filesystem without any reconstruction.
Cross-check: energy rows (1501 expected = 150000/100 + 1), traj frames
(38 expected = 150000/4000 + 1), log time_passed.
"""
import json
import os
import subprocess
import sys

REPO = r"C:\NanoLab\nl3-002-param-32b"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-PARAM-32B-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.canonical import canonical_json  # noqa: E402

WSL_ROOT = "/home/yurig/nl3-002-param-32b/runs"
RUNS = [
    {"run_id": "PARAM-32B-S001", "prefix": "s001", "seed": 201004},
    {"run_id": "PARAM-32B-S002", "prefix": "s002", "seed": 202008},
    {"run_id": "PARAM-32B-S003", "prefix": "s003", "seed": 203012},
]
ENGINE = "/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA"
BUDGET_S = 3.5 * 3600
STEPS = 150000


def wsl(cmd):
    return subprocess.run(["wsl", "-e", "bash", "-c", cmd],
                          capture_output=True, text=True, timeout=300)


def main() -> int:
    report = {"schema_version": 1, "kind": "e2_param_run_reports",
              "execution_id": "EX-NL3-002-PARAM-32B-R1", "variant": "32b",
              "steps": STEPS,
              "engine": ENGINE,
              "engine_source_commit": "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591",
              "parallel": True, "budget_s_per_replica": BUDGET_S,
              "launch_method": "setsid+nohup detached bash per replica; exit codes and epochs written to files in run dirs (no wrapper dependency)",
              "runs": {}}
    for run in RUNS:
        rid, p = run["run_id"], run["prefix"]
        d = f"{WSL_ROOT}/{rid}"
        out = wsl(
            f"cat '{d}/start_epoch.txt' 2>/dev/null; cat '{d}/exit_code.txt' 2>/dev/null; "
            f"cat '{d}/end_epoch.txt' 2>/dev/null; wc -l < '{d}/{p}_energy.dat'; "
            f"grep -c '^t =' '{d}/{p}_traj.dat'; "
            f"grep -o 'time_passed: [0-9.]*' '{d}/{p}_log.dat' | tail -1")
        lines = [l.strip() for l in out.stdout.splitlines() if l.strip()]
        start_epoch = int(lines[0])
        exit_code = None
        end_epoch = None
        rest = lines[1:]
        if rest and rest[0].startswith("EXIT:"):
            exit_code = int(rest[0].split(":", 1)[1])
            rest = rest[1:]
        if rest and rest[0].isdigit():
            end_epoch = int(rest[0])
            rest = rest[1:]
        energy_rows = int(rest[0])
        traj_frames = int(rest[1]) if len(rest) > 1 else None
        time_passed = [l for l in rest if l.startswith("time_passed")]
        wall_fs = (end_epoch - start_epoch) if end_epoch is not None else None
        report["runs"][rid] = {
            "prefix": p, "seed": run["seed"], "wsl_dir": d,
            "exit_code": exit_code,
            "start_epoch": start_epoch, "end_epoch": end_epoch,
            "wall_time_s": wall_fs,
            "budget_ok": (wall_fs is not None and wall_fs <= BUDGET_S),
            "interrupted_budget": False,
            "energy_rows": energy_rows, "energy_rows_expected_full_run": STEPS // 100 + 1,
            "traj_frames_written": traj_frames, "traj_frames_expected_full_run": STEPS // 4000 + 1,
            "log_time_passed_s_crosscheck": float(time_passed[-1].split(":")[1]) if time_passed else None,
            "per_step_s": round(wall_fs / STEPS, 6) if wall_fs else None,
            "steps_requested": STEPS,
        }
        print(rid, json.dumps(report["runs"][rid]))
    path = os.path.join(EX, "evidence", "run-reports.json")
    with open(path, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(report) + "\n")
    print("written", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
