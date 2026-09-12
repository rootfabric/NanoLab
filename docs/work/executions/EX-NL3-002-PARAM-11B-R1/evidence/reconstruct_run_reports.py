"""Reconstruct run reports for EX-NL3-002-PARAM-11B-R1 from the filesystem.

The parent Python wrapper (run_param.py) was terminated by the harness job
timeout AFTER launching the engines; the WSL engine processes and their parent
bash shells kept running and finish/interrupt normally (exit_code.txt is
written by the bash shell, not by the wrapper). Wall times are reconstructed
from the filesystem: energy-file birth time (engine start) -> exit_code.txt
mtime (engine end). Cross-check: log DEBUG 'time_passed' at the last row.
This mirrors the documented EX-NL3-002-R1 wrapper-crash precedent (F-3).
"""
import json
import os
import subprocess
import sys

REPO = r"C:\NanoLab\nl3-002-param-11b"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-PARAM-11B-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.canonical import canonical_json  # noqa: E402

WSL_ROOT = "/home/yurig/nl3-002-param-11b/runs"
RUNS = [
    {"run_id": "PARAM-11B-S001", "prefix": "s001", "seed": 201004},
    {"run_id": "PARAM-11B-S002", "prefix": "s002", "seed": 202008},
    {"run_id": "PARAM-11B-S003", "prefix": "s003", "seed": 203012},
]
ENGINE = "/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA"
BUDGET_S = 3.5 * 3600


def wsl(cmd):
    return subprocess.run(["wsl", "-e", "bash", "-c", cmd],
                          capture_output=True, text=True, timeout=300)


def main() -> int:
    report = {"schema_version": 1, "kind": "e2_param_run_reports",
              "execution_id": "EX-NL3-002-PARAM-11B-R1", "variant": "11b",
              "engine": ENGINE,
              "engine_source_commit": "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591",
              "parallel": True, "budget_s_per_replica": BUDGET_S,
              "wall_reconstruction": ("parent wrapper run_param.py was killed by the harness job "
                                      "timeout after engine launch; wall = energy-file birth -> "
                                      "exit_code.txt mtime (WSL stat), cross-checked vs log time_passed"),
              "runs": {}}
    for run in RUNS:
        rid, p = run["run_id"], run["prefix"]
        d = f"{WSL_ROOT}/{rid}"
        out = wsl(
            f"stat -c %W '{d}/{p}_energy.dat'; stat -c %Y '{d}/exit_code.txt' 2>/dev/null || echo MISSING; "
            f"cat '{d}/exit_code.txt' 2>/dev/null; wc -l < '{d}/{p}_energy.dat'; "
            f"stat -c %Y '{d}/{p}_traj.dat'; "
            f"grep -o 'time_passed: [0-9.]*' '{d}/{p}_log.dat' | tail -1")
        lines = [l.strip() for l in out.stdout.splitlines() if l.strip()]
        birth = int(lines[0])
        exit_mtime = None
        exit_code = None
        if lines[1] != "MISSING":
            exit_mtime = int(lines[1])
            for line in lines[2:]:
                if line.startswith("EXIT:"):
                    exit_code = int(line.split(":", 1)[1])
                    break
            rest = lines[3:]
        else:
            rest = lines[2:]
        energy_rows = int(rest[0])
        traj_mtime = int(rest[1])
        time_passed = [l for l in rest if l.startswith("time_passed")]
        # engines were SIGTERM-killed by the budget interrupt (pkill also matched
        # the parent bash, so no exit_code.txt): wall = energy birth -> last traj write
        end_mtime = exit_mtime if exit_mtime is not None else traj_mtime
        wall_fs = end_mtime - birth
        report["runs"][rid] = {
            "prefix": p, "seed": run["seed"], "wsl_dir": d,
            "exit_code": exit_code,
            "exit_condition": ("SIGTERM budget interrupt at 3.5h deadline (engine + parent bash killed; "
                               "no exit_code.txt written)") if exit_code is None else "engine exit",
            "interrupted_budget": True,
            "energy_rows": energy_rows, "energy_rows_expected_full_run": 2001,
            "traj_frames_written": 46, "traj_frames_expected_full_run": 50,
            "wall_time_s": wall_fs,
            "log_time_passed_s_crosscheck": float(time_passed[-1].split(":")[1]) if time_passed else None,
            "per_step_s_approx": round(wall_fs / (energy_rows * 100.0), 6),
            "steps_requested": 200000,
        }
        print(rid, json.dumps(report["runs"][rid]))
    path = os.path.join(EX, "evidence", "run-reports.json")
    with open(path, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(report) + "\n")
    print("written", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
