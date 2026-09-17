#!/usr/bin/env python3
"""Run the 12 EX-NL5-001-C-R1 replicas in parallel local processes.

Per-replica budget: wall > BUDGET_S -> SIGTERM kill, recorded as
FAILED_TECHNICAL (budget abort, E2_PROTO section 5 pattern). Exit codes and
wall times are recorded per run; the supervisor returns 0 only when all 12
processes completed without budget abort and with engine exit 0.
"""
from __future__ import annotations

import json
import signal
import subprocess
import sys
import time
from pathlib import Path

ENGINE = "/home/rdpuser/nl5-001-c-env/oxdna-src/build/bin/oxDNA"
RUN_ROOT = Path(sys.argv[1]).resolve()
BUDGET_S = 20 * 3600  # WO-NL5-001-C-R1 frozen per-replica hard kill

RUNS = []
for variant, seeds in (("0b", [170085, 157480, 561483]), ("11b", [373439, 592596, 456410]),
                       ("32b", [399746, 801667, 659403]), ("53b", [511532, 979551, 175554])):
    for i in range(1, 4):
        RUNS.append(f"NL5-001-C-{variant.upper()}-S{i:03d}")


def main() -> int:
    procs = {}
    started = {}
    for rid in RUNS:
        run_dir = RUN_ROOT / rid
        if not (run_dir / "input.in").is_file():
            print(f"FAIL {rid}: input.in missing", file=sys.stderr)
            return 3
        cmd = (f"cd '{run_dir}' && '{ENGINE}' input.in > engine_stdout.txt 2> engine_stderr.txt; "
               f"echo EXIT:$? > exit_code.txt")
        procs[rid] = subprocess.Popen(["bash", "-c", cmd], start_new_session=True)
        started[rid] = time.perf_counter()
        print(f"started {rid} pid={procs[rid].pid}", flush=True)
    pending = set(RUNS)
    reports = {}
    while pending:
        time.sleep(30)
        for rid in list(pending):
            code = procs[rid].poll()
            wall = time.perf_counter() - started[rid]
            if code is not None:
                reports[rid] = {"exit_code": code, "wall_s": round(wall, 1), "budget_abort": False}
                print(f"finished {rid} exit={code} wall_s={wall:.0f}", flush=True)
                pending.discard(rid)
            elif wall > BUDGET_S:
                try:
                    os_kill_tree(procs[rid])
                finally:
                    reports[rid] = {"exit_code": None, "wall_s": round(wall, 1), "budget_abort": True}
                print(f"BUDGET ABORT {rid} wall_s={wall:.0f}", flush=True)
                pending.discard(rid)
        (RUN_ROOT / "run-reports-live.json").write_text(
            json.dumps(reports, indent=2) + "\n", encoding="utf-8")
    ok = all(r["exit_code"] == 0 and not r["budget_abort"] for r in reports.values())
    (RUN_ROOT / "run-reports.json").write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
    print("all done; engine_ok =", ok)
    return 0 if ok else 3


def os_kill_tree(proc: subprocess.Popen) -> None:
    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=30)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
