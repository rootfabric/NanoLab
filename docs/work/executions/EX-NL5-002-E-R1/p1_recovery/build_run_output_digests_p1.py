#!/usr/bin/env python3
"""Build the P1 run-output digest manifest (EX-NL5-002-E-R1 leg P1).

Run ON THE P1 MACHINE (DESKTOP-QNAGSTI WSL, user yurig) after all 20 primary
runs finished. Robust to the P1 launcher's file-naming variants.

Output: <P1 workspace>/run_output_digests_p1.json
Exit 1 if any of the 20 final runs is missing (completeness gate).
"""
import hashlib, json, os, sys, datetime, glob

WS = os.path.expanduser("~/nanolab-platform-sensitivity-r1/P1")
RUN_IDS = [f"PLATSENS-P1-{v}-S{s:03d}" for v in ("0B", "32B") for s in range(1, 11)]

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def artifact(rel, producer):
    p = os.path.join(WS, rel)
    if not os.path.isfile(p):
        return None
    return {"path": rel, "sha256": sha256_of(p), "size": os.path.getsize(p), "producer": producer}

def read_exit(run_dir):
    # P1 launcher variant: bare-integer exit code file (exit_code.txt) or exit_code_raw.txt
    for name in ("exit_code_raw.txt", "exit_code.txt"):
        p = os.path.join(run_dir, name)
        if os.path.isfile(p):
            digits = open(p).read().strip()
            try:
                return int(digits), name
            except ValueError:
                pass
    return None, None

def read_time(run_dir, names):
    for n in names:
        p = os.path.join(run_dir, n)
        if os.path.isfile(p):
            t = open(p).read().strip()
            if t:
                return t
    return None

def wall_seconds(a, b):
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        d = datetime.datetime.strptime(b, fmt) - datetime.datetime.strptime(a, fmt)
        return int(d.total_seconds())
    except Exception:
        return None

def main():
    runs, missing, superseded = [], [], []
    for rid in RUN_IDS:
        rd = os.path.join(WS, "runs", rid)
        if not os.path.isdir(rd):
            missing.append(rid)
            continue
        meta = {}
        mp = os.path.join(rd, "run_meta.json")
        if os.path.isfile(mp):
            meta = json.load(open(mp))
        exit_code, exit_file = read_exit(rd)
        start = read_time(rd, ("start_time.txt",))
        end = read_time(rd, ("end_time.txt",))
        if not start:
            start = meta.get("launched_at_utc", "").replace("+00:00", "Z") or None
        variant = meta.get("variant") or ("0b" if "-0B-" in rid else "32b")
        arts = {
            "traj_dat": artifact(f"runs/{rid}/traj.dat", "oxDNA (pinned 00dc7fb9, P1 build) replica trajectory"),
            "energy": artifact(f"runs/{rid}/energy.dat", "oxDNA (pinned 00dc7fb9, P1 build) replica energy file"),
            "last_conf": artifact(f"runs/{rid}/last_conf.dat", "oxDNA (pinned 00dc7fb9, P1 build) replica final configuration"),
            "stdout": artifact(f"runs/{rid}/stdout.log", "oxDNA replica run stdout"),
            "stderr": artifact(f"runs/{rid}/stderr.log", "oxDNA replica run stderr"),
            "input": artifact(f"runs/{rid}/input", "executor (overlay input; upstream pro_CPU.in verbatim + pinned overlay fields)"),
            "conf": artifact(f"runs/{rid}/{variant}.conf", "upstream verbatim copy (digest-gated)"),
            "top": artifact(f"runs/{rid}/{variant}.top", "upstream verbatim copy (digest-gated)"),
            "run_meta": artifact(f"runs/{rid}/run_meta.json", "executor (run infrastructure)"),
        }
        runs.append({
            "run_id": rid, "variant": variant, "seed": meta.get("seed"), "steps": meta.get("steps"),
            "attempt": 1,
            "exit_code": exit_code, "exit_code_file": exit_file,
            "wrapper_pid": (open(os.path.join(rd, "wrapper.pid")).read().strip()
                            if os.path.isfile(os.path.join(rd, "wrapper.pid")) else None),
            "start_utc": start, "end_utc": end,
            "wall_time_s": wall_seconds(start, end) if start and end else None,
            "engine_binary": meta.get("engine_binary"),
            "input_sha256": meta.get("input_sha256"),
            "conf_sha256": meta.get("conf_sha256"),
            "top_sha256": meta.get("top_sha256"),
            "artifacts": arts,
        })
    runs_dir = os.path.join(WS, "runs")
    if os.path.isdir(runs_dir):
        for d in sorted(os.listdir(runs_dir)):
            if d.startswith("PLATSENS-P1-") and d not in RUN_IDS:
                superseded.append(d)
    out = {
        "kind": "platform_sensitivity_run_output_digests_v1",
        "execution_id": "EX-NL5-002-E-R1", "leg": "P1",
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "expected_final_runs": 20,
        "final_runs_recorded": len(runs),
        "missing_runs": missing,
        "duplicate_check": len({r['run_id'] for r in runs}) == len(runs),
        "runs": runs,
        "superseded_attempts": superseded,
        "raw_trajectories_note": "raw trajectories remain in WSL Linux FS outside Git",
    }
    json.dump(out, open(os.path.join(WS, "run_output_digests_p1.json"), "w"), indent=2)
    print(f"final_runs_recorded={len(runs)} missing={len(missing)} superseded={len(superseded)}")
    if missing:
        print("MISSING:", ", ".join(missing)); sys.exit(1)

if __name__ == "__main__":
    main()
