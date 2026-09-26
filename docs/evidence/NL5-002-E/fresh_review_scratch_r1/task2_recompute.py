#!/usr/bin/env python3
"""FRESH REVIEWER Task 2: independent recompute of all 20 P2 replica analyses.

Runs the PACKAGED analyzer (nanolab-components 0.1.1 convention/analyze_hinge.py,
unmodified) with my own driver, then diffs my recomputed replica_median_deg and
all scalar fields against the committed P2 analysis JSONs.
"""
import json
import os
import subprocess
import sys
import time

PKG = "/home/rdpuser/nl5-002-e-p2/workspace/package"
ANALYZER = os.path.join(PKG, "convention", "analyze_hinge.py")
MANIFEST = {v: os.path.join(PKG, "convention", f"arm-manifest-{v}.json") for v in ("0b", "32b")}
RAW = "/home/rdpuser/nl5-002-e-p2/workspace/runs"
OUT = "/tmp/reviewer_p2/reports_p2"
COMMITTED = ("/home/rdpuser/NanoLab/nl5-002-e-p2-exec"
             "/docs/work/executions/EX-NL5-002-E-R1/evidence/p2/analysis")
WINDOW = {"0b": 200000, "32b": 150000}
SIDS = [f"S{i:03d}" for i in range(1, 11)]
os.makedirs(OUT, exist_ok=True)

results = {}
t0 = time.time()
for var in ("0b", "32b"):
    for sid in SIDS:
        rid = f"PLATSENS-P2-{var.upper()}-{sid}"
        run = os.path.join(RAW, rid)
        rep = os.path.join(OUT, f"{rid}.json")
        cmd = [
            sys.executable, ANALYZER, "run",
            "--trajectory", os.path.join(run, "traj.dat"),
            "--energy", os.path.join(run, "energy.dat"),
            "--topology", os.path.join(run, f"{var}.top"),
            "--manifest", MANIFEST[var],
            "--variant", var,
            "--run-id", rid,
            "--window", str(WINDOW[var]),
            "--exit-code-file", os.path.join(run, "exit_code.txt"),
            "--report", rep,
        ]
        t = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        dt = time.time() - t
        status = "OK" if p.returncode == 0 else f"RC={p.returncode}"
        print(f"{rid}: analyzer {status} in {dt:.1f}s", flush=True)
        if p.returncode != 0:
            print("STDERR:", p.stderr[-2000:], flush=True)
            results[rid] = {"analyzer_rc": p.returncode}
            continue
        mine = json.load(open(rep))
        committed = json.load(open(os.path.join(COMMITTED, f"{rid}_analysis.json")))
        diff = []
        for k in sorted(set(mine) | set(committed)):
            if k == "frames":
                continue  # compared below, expensive scalar-by-scalar
            mv, cv = mine.get(k), committed.get(k)
            if mv != cv:
                diff.append((k, mv, cv))
        # frame-by-frame exact comparison
        mf, cf = mine.get("frames", []), committed.get("frames", [])
        if len(mf) != len(cf):
            diff.append(("frames.length", len(mf), len(cf)))
        else:
            for i, (a, b) in enumerate(zip(mf, cf)):
                if a != b:
                    diff.append((f"frames[{i}]", a, b))
                    break
        results[rid] = {
            "analyzer_rc": 0,
            "replica_median_deg_mine": mine.get("replica_median_deg"),
            "replica_median_deg_committed": committed.get("replica_median_deg"),
            "exact_equal": not diff,
            "diffs": diff,
        }
        print(f"    median mine={mine.get('replica_median_deg')} "
              f"committed={committed.get('replica_median_deg')} "
              f"exact={'YES' if not diff else 'NO ' + str(diff[:3])}", flush=True)

print(f"\nTotal wall: {time.time()-t0:.1f}s")
json.dump(results, open("/tmp/reviewer_p2/task2_recompute_summary.json", "w"), indent=1)
n_ok = sum(1 for r in results.values() if r.get("exact_equal"))
print(f"EXACT MATCH (all fields incl. frame-by-frame): {n_ok}/20")
