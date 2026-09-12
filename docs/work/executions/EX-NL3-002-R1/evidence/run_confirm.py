"""Run the 3 confirmatory replicas in parallel WSL processes (E2_PROTO_R1 §3, §5).

No timeout kill: the only interruption condition is wall > BUDGET_S per replica
(<= 3.5 h), which is then recorded as a measured calibration fact. Waits for
ALL replicas, measures per-run wall time, writes a canonical run report.
"""
import os
import subprocess
import sys
import time

REPO = r"C:\NanoLab\nl3-002-confirm"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(EX, "evidence"))
from e2.canonical import canonical_json  # noqa: E402
from rec_util import write_text  # noqa: E402

ENGINE = "/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA"
WSL_ROOT = "/home/yurig/nl3-002-confirm/runs"
RUNS = [
    {"run_id": "E2-R1-C001", "prefix": "c001", "seed": 201004},
    {"run_id": "E2-R1-C002", "prefix": "c002", "seed": 202008},
    {"run_id": "E2-R1-C003", "prefix": "c003", "seed": 203012},
]
BUDGET_S = 3.5 * 3600  # E2_PROTO_R1 section 5


def main() -> int:
    procs = {}
    started = {}
    for run in RUNS:
        wsl_dir = f"{WSL_ROOT}/{run['run_id']}"
        cmd = (f"cd '{wsl_dir}' && '{ENGINE}' input.in > engine_stdout.txt 2> engine_stderr.txt; "
               f"echo EXIT:$? > exit_code.txt")
        procs[run["run_id"]] = subprocess.Popen(["wsl", "-e", "bash", "-c", cmd])
        started[run["run_id"]] = time.perf_counter()
        print(f"started {run['run_id']} pid={procs[run['run_id']].pid}", flush=True)
    interrupted = {}
    pending = {r["run_id"] for r in RUNS}
    while pending:
        for rid in list(pending):
            rc = procs[rid].poll()
            if rc is not None:
                print(f"finished {rid} rc={rc} wall={time.perf_counter() - started[rid]:.1f}s", flush=True)
                interrupted[rid] = False
                del pending[rid]
            elif time.perf_counter() - started[rid] > BUDGET_S:
                # budget exceeded: interrupt this run and record it (measured fact)
                subprocess.run(["wsl", "-e", "bash", "-c", f"pkill -f 'runs/{rid}' || true"], timeout=60)
                procs[rid].wait()
                print(f"BUDGET-INTERRUPTED {rid} wall={time.perf_counter() - started[rid]:.1f}s", flush=True)
                interrupted[rid] = True
                del pending[rid]
        if pending:
            time.sleep(30)
    walls = {rid: time.perf_counter() - started[rid] for rid in interrupted}
    report = {"schema_version": 1, "kind": "e2_confirm_run_reports",
              "execution_id": "EX-NL3-002-R1", "engine": ENGINE,
              "engine_source_commit": "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591",
              "parallel": True, "budget_s_per_replica": BUDGET_S, "runs": {}}
    for run in RUNS:
        rid = run["run_id"]
        wsl_dir = f"{WSL_ROOT}/{rid}"
        out = subprocess.run(["wsl", "-e", "bash", "-c", f"cat '{wsl_dir}/exit_code.txt' 2>/dev/null"],
                             capture_output=True, text=True, timeout=60)
        exit_code = None
        for line in out.stdout.splitlines():
            if line.startswith("EXIT:"):
                exit_code = int(line.split(":", 1)[1])
        report["runs"][rid] = {
            "prefix": run["prefix"], "seed": run["seed"], "wsl_dir": wsl_dir,
            "exit_code": exit_code, "interrupted_budget": interrupted[rid],
            "wall_time_s": round(walls[rid], 2),
            "per_step_s": round(walls[rid] / 200000.0, 6), "steps_requested": 200000,
        }
    write_text(os.path.join("evidence", "run-reports.json"), canonical_json(report) + "\n")
    print(canonical_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
