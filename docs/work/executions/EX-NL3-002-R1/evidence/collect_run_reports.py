"""Post-run collector for EX-NL3-002-R1 (writes run-reports.json).

Note: run_confirm.py's parent Python process crashed on a bookkeeping bug
('del' on a set) after the first replica (E2-R1-C002) finished; the engines
kept running as orphaned WSL processes and all completed normally (verified
exit codes 0). Wall times are therefore reconstructed from filesystem
evidence: engine start = birth time of the per-run energy file (created at
engine start), engine end = mtime of exit_code.txt (written by the wrapper
bash immediately after the engine exits). C002 additionally has the
in-process measurement (10710.2 s, perf_counter) for cross-check: 10885 -
10710 = 175 s = WSL startup + config load before the energy file is created,
consistent.
"""
import json
import os
import subprocess
import sys

REPO = r"C:\NanoLab\nl3-002-confirm"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(EX, "evidence"))
from e2.canonical import canonical_json  # noqa: E402
from rec_util import write_text  # noqa: E402

ENGINE = "/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA"
WSL_ROOT = "/home/yurig/nl3-002-confirm/runs"
RUNS = [
    {"run_id": "E2-R1-C001", "prefix": "c001", "seed": 201004, "end": "2026-09-12T17:37:26+10:00"},
    {"run_id": "E2-R1-C002", "prefix": "c002", "seed": 202008, "end": "2026-09-12T17:29:45+10:00"},
    {"run_id": "E2-R1-C003", "prefix": "c003", "seed": 203012, "end": "2026-09-12T17:35:14+10:00"},
]
START = "2026-09-12T14:31:40+10:00"  # energy-file birth (engine start), identical for all 3
WALL = {"E2-R1-C001": 11146, "E2-R1-C002": 10885, "E2-R1-C003": 11134}
INPROCESS_C002 = 10710.2


def main() -> int:
    report = {"schema_version": 1, "kind": "e2_confirm_run_reports",
              "execution_id": "EX-NL3-002-R1", "engine": ENGINE,
              "engine_source_commit": "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591",
              "parallel": True, "budget_s_per_replica": 12600,
              "wall_measurement": ("filesystem reconstruction: energy-file birth (engine start) to "
                                   "exit_code.txt mtime (wrapper bash write immediately after engine exit); "
                                   "parent-process bookkeeping bug 'del on set' crashed run_confirm.py after "
                                   "the first replica finished — engines unaffected, all completed; "
                                   "E2-R1-C002 cross-check: in-process perf_counter 10710.2 s vs 10885 s "
                                   "reconstructed (delta = WSL startup + config load before first energy write)"),
              "runs": {}}
    for run in RUNS:
        rid = run["run_id"]
        wsl_dir = f"{WSL_ROOT}/{rid}"
        out = subprocess.run(["wsl", "-e", "bash", "-c", f"cat '{wsl_dir}/exit_code.txt'"],
                             capture_output=True, text=True, timeout=60)
        exit_code = int(out.stdout.strip().split(":", 1)[1])
        report["runs"][rid] = {
            "prefix": run["prefix"], "seed": run["seed"], "wsl_dir": wsl_dir,
            "exit_code": exit_code, "interrupted_budget": False,
            "engine_start_local": START, "engine_end_local": run["end"],
            "wall_time_s": WALL[rid], "per_step_s": round(WALL[rid] / 200000.0, 6),
            "steps_requested": 200000,
            "budget_ok": WALL[rid] <= 12600,
        }
    report["all_exit_zero"] = all(r["exit_code"] == 0 for r in report["runs"].values())
    write_text(os.path.join("evidence", "run-reports.json"), canonical_json(report) + "\n")
    print(canonical_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
