#!/usr/bin/env python3
"""FRESH REVIEWER Task 1: completeness + pins check for EX-NL5-002-E-R1.

Own implementation; trusts nothing operator-written except the committed
JSON artifacts themselves (which are the evidence under review).
"""
import hashlib
import json
import os
import re
import sys

REPO = "/home/rdpuser/NanoLab/nl5-002-e-p2-exec"
EX = os.path.join(REPO, "docs/work/executions/EX-NL5-002-E-R1")
P1_AN = os.path.join(EX, "evidence/p1/analysis")
P2_AN = os.path.join(EX, "evidence/p2/analysis")
P2_RAW = "/home/rdpuser/nl5-002-e-p2/workspace/runs"

SEEDS = {
    "S001": 1259289227, "S002": 1358106528, "S003": 1524307444, "S004": 601855227,
    "S005": 274288237, "S006": 972234272, "S007": 1934775205, "S008": 1747973984,
    "S009": 880427736, "S010": 744386736,
}
VARIANTS = ("0b", "32b")
STEPS_PIN = {"0b": 200000, "32b": 150000}
FRAMES_PIN = {"0b": 50, "32b": 37}
SIDS = sorted(SEEDS)

problems = []
notes = []


def check(cond, msg):
    if cond:
        print(f"  OK   {msg}")
    else:
        problems.append(msg)
        print(f"  FAIL {msg}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_all(an_dir, platform):
    out = {}
    files = sorted(f for f in os.listdir(an_dir) if f.endswith("_analysis.json"))
    for fn in files:
        with open(os.path.join(an_dir, fn)) as f:
            d = json.load(f)
        rid = d.get("run_id")
        out[rid] = d
        out[rid]["_file"] = fn
    return out, files


print("=" * 72)
print("TASK 1a: committed analysis JSON inventory")
p1, p1_files = load_all(P1_AN, "P1")
p2, p2_files = load_all(P2_AN, "P2")
check(len(p1_files) == 20, f"P1 analysis JSON count == 20 (got {len(p1_files)})")
check(len(p2_files) == 20, f"P2 analysis JSON count == 20 (got {len(p2_files)})")

print("=" * 72)
print("TASK 1b: per-file pin checks (run_id/variant/window/steps/exit/frames)")
expected_final = {
    ("0b", s): f"PLATSENS-P1-0B-{s}" + ("-R21" if s in ("S009",) else "-R14" if s in ("S010",) else "")
    for s in SIDS
}
expected_final.update({
    ("32b", s): f"PLATSENS-P1-32B-{s}" + ("-R14" if s == "S001" else "-R13" if s in ("S002", "S003", "S004", "S005", "S006") else "")
    for s in SIDS
})
for var in VARIANTS:
    for sid in SIDS:
        base = f"PLATSENS-P1-{var.upper()}-{sid}"
        # exactly one final P1 analysis for this (variant, seed)
        cands = [r for r in p1 if re.fullmatch(rf"PLATSENS-P1-{var.upper()}-{sid}(-R\d+)?", r)]
        if len(cands) != 1:
            check(False, f"P1 {var} {sid}: exactly one final analysis (got {sorted(cands)})")
            continue
        rid = cands[0]
        d = p1[rid]
        tag = f"P1 {rid}"
        check(d["_file"] == rid + "_analysis.json", f"{tag}: filename matches run_id")
        check(d.get("variant") == var, f"{tag}: variant == {var}")
        check(d.get("window_steps") == STEPS_PIN[var], f"{tag}: window_steps == {STEPS_PIN[var]}")
        check(d.get("engine_exit_code") == 0, f"{tag}: engine_exit_code == 0")
        fiw = d.get("frames_in_window")
        fvw = d.get("frames_valid_in_window")
        check(fvw == fiw == FRAMES_PIN[var],
              f"{tag}: frames valid {fvw} == total {fiw} == {FRAMES_PIN[var]}")
        check(isinstance(d.get("replica_median_deg"), (int, float)), f"{tag}: replica_median_deg present = {d.get('replica_median_deg')}")
        check(rid == expected_final[(var, sid)], f"{tag}: matches event-0006 final-attempt map")
        check(d.get("rule_id") == "NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE", f"{tag}: rule_id pin")
        check(len(d.get("frames", [])) == FRAMES_PIN[var], f"{tag}: frames[] length == {FRAMES_PIN[var]}")

for var in VARIANTS:
    for sid in SIDS:
        rid = f"PLATSENS-P2-{var.upper()}-{sid}"
        d = p2.get(rid)
        if d is None:
            check(False, f"P2 {rid}: analysis present")
            continue
        tag = f"P2 {rid}"
        check(d["_file"] == rid + "_analysis.json", f"{tag}: filename matches run_id")
        check(d.get("variant") == var, f"{tag}: variant == {var}")
        check(d.get("window_steps") == STEPS_PIN[var], f"{tag}: window_steps == {STEPS_PIN[var]}")
        check(d.get("engine_exit_code") == 0, f"{tag}: engine_exit_code == 0")
        fiw = d.get("frames_in_window")
        fvw = d.get("frames_valid_in_window")
        check(fvw == fiw == FRAMES_PIN[var],
              f"{tag}: frames valid {fvw} == total {fiw} == {FRAMES_PIN[var]}")
        check(isinstance(d.get("replica_median_deg"), (int, float)), f"{tag}: replica_median_deg present = {d.get('replica_median_deg')}")
        check(d.get("rule_id") == "NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE", f"{tag}: rule_id pin")
        check(len(d.get("frames", [])) == FRAMES_PIN[var], f"{tag}: frames[] length == {FRAMES_PIN[var]}")

print("=" * 72)
print("TASK 1c: pairing gate (exactly one P1 and one P2 median per variant x seed)")
for var in VARIANTS:
    for sid in SIDS:
        seed = SEEDS[sid]
        p1_c = [r for r in p1 if re.fullmatch(rf"PLATSENS-P1-{var.upper()}-{sid}(-R\d+)?", r)]
        p2_r = f"PLATSENS-P2-{var.upper()}-{sid}"
        ok = len(p1_c) == 1 and p2_r in p2
        check(ok, f"pair {var}/{sid}: exactly 1 P1 ({p1_c}) + 1 P2 ({p2_r in p2})")
        if ok:
            # seeds via committed runmaps
            p1_med = p1[p1_c[0]]["replica_median_deg"]
            p2_med = p2[p2_r]["replica_median_deg"]
            check(isinstance(p1_med, float) and isinstance(p2_med, float),
                  f"pair {var}/{sid}: both medians numeric")

print("=" * 72)
print("TASK 1d: seed/steps cross-check vs runmaps and frozen WO list")
rm1 = json.load(open(os.path.join(EX, "evidence/seeds_runmap_p1.json")))
rm2 = json.load(open(os.path.join(EX, "evidence/p2/seeds_runmap_p2.json")))
check(rm2["seeds"] == SEEDS, "P2 runmap seeds == frozen WO seed list")
for var in VARIANTS:
    check(rm1["steps"][var] == rm2["steps"][var] == STEPS_PIN[var],
          f"runmap steps pin {var} == {STEPS_PIN[var]}")
    for sid in SIDS:
        base = f"PLATSENS-P1-{var.upper()}-{sid}"
        check(rm1["run_map"][var][base] == SEEDS[sid], f"P1 runmap {base} seed == frozen")

print("=" * 72)
print("TASK 1e: P1 digest manifest internal consistency")
dm1 = json.load(open(os.path.join(EX, "evidence/p1/run_output_digests_p1.json")))
check(dm1["expected_final_runs"] == 20 and dm1["final_runs_recorded"] == 20,
      "P1 digest manifest: expected==recorded==20")
check(dm1["missing_runs"] == [] and dm1["duplicate_check"] is True,
      "P1 digest manifest: missing_runs empty, duplicate_check true")
sup = dm1["interrupted_or_failed_attempts_kept"]
n_sup = sum(len(s["superseded_attempts_history"]) for s in sup)
check(n_sup == 114, f"P1 digest manifest: 114 superseded attempts enumerated (got {n_sup})")
check(len(sup) == 8, f"P1 digest manifest: 8 slots with retry chains (got {len(sup)})")
# per final run: seed, steps, exit
for r in dm1["runs"]:
    rid = r["run_id"]
    var = r["variant"]
    sid = "S" + rid.split("-S")[-1].split("-")[0]
    ok = (r["seed"] == SEEDS[sid] and r["steps"] == STEPS_PIN[var]
          and r["engine_exit_code"] == 0 and r["status"] == "COMPLETE_EXIT_0"
          and len(r["artifacts"]) == 10)
    if not ok:
        check(False, f"P1 digest run {rid}: seed/steps/exit/status/10-artifacts")
check(all(r["seed"] == SEEDS["S" + r["run_id"].split("-S")[-1].split("-")[0]]
          and r["steps"] == STEPS_PIN[r["variant"]]
          and r["engine_exit_code"] == 0 and r["status"] == "COMPLETE_EXIT_0"
          and len(r["artifacts"]) == 10 for r in dm1["runs"]),
      "P1 digest manifest: all 20 finals seed/steps/exit/status/10-artifacts consistent")
# retry chains: final attempt id = max of chain
for s in sup:
    chain = s["superseded_attempts_history"]  # base + -R1..-Rk (k = len-1)
    final = chain[-1] + "-" + f"R{len(chain):02d}" if False else None
    base = s["slot"]
    k = len(chain)  # attempts 0..k-1 superseded; final = -R{k}
    fin_id = f"{base}-R{k}"
    dm_ids = {r["run_id"] for r in dm1["runs"]}
    real_final = [r["final_attempt_id"] for r in dm1["runs"] if r["run_id"] == base][0]
    check(real_final == fin_id, f"retry chain {base}: final attempt {real_final} == -R{k} (append-only, no gaps)")
# chain continuity: IDs are base, base-R1..base-R(k-1)
for s in sup:
    base = s["slot"]
    chain = s["superseded_attempts_history"]
    expect = [base] + [f"{base}-R{i}" for i in range(1, len(chain))]
    check(chain == expect, f"chain {base}: append-only contiguous IDs")

print("=" * 72)
print("TASK 1f: P2 digest manifest vs raw runs on this host")
dm2 = json.load(open(os.path.join(EX, "evidence/p2/run_output_digests_p2.json")))
check(dm2["expected_final_runs"] == 20 and dm2["final_runs_recorded"] == 20,
      "P2 digest manifest: expected==recorded==20")
check(dm2["missing_runs"] == [] and dm2["superseded_attempts"] == [] and dm2["duplicate_check"] is True,
      "P2 digest manifest: no missing/superseded, duplicate_check true")
for r in dm2["runs"]:
    rid = r["run_id"]
    var = r["variant"]
    sid = "S" + rid.split("-S")[-1]
    rd = os.path.join(P2_RAW, rid)
    ok = os.path.isdir(rd)
    check(ok, f"P2 raw dir exists: {rid}")
    if not ok:
        continue
    meta = json.load(open(os.path.join(rd, "run_meta.json")))
    ec = open(os.path.join(rd, "exit_code.txt")).read().strip()
    ec_raw = open(os.path.join(rd, "exit_code_raw.txt")).read().strip()
    conf_sha = sha256(os.path.join(rd, f"{var}.conf"))
    top_sha = sha256(os.path.join(rd, f"{var}.top"))
    inp_sha = sha256(os.path.join(rd, "input"))
    inp_txt = open(os.path.join(rd, "input")).read()
    seed_inp = int(re.search(r"^seed\s*=\s*(\d+)", inp_txt, re.M).group(1))
    steps_inp = int(re.search(r"^steps\s*=\s*(\d+)", inp_txt, re.M).group(1))
    row_ok = (r["seed"] == meta["seed"] == seed_inp == SEEDS[sid]
              and r["steps"] == meta["steps"] == steps_inp == STEPS_PIN[var]
              and r["exit_code"] == 0 and ec == "EXIT_CODE: 0" and ec_raw == "0"
              and r["conf_sha256"] == conf_sha == meta["conf_sha256"]
              and r["top_sha256"] == top_sha == meta["top_sha256"]
              and r["input_sha256"] == inp_sha == meta["input_sha256"]
              and meta["run_id"] == rid and meta["variant"] == var)
    check(row_ok, f"P2 raw {rid}: seed={seed_inp} steps={steps_inp} exit=0 sha(conf/top/input) all match manifest+meta")

# cross-platform input identity: P2 conf/top digests vs P1-recorded digests
p1_by_var = {}
for r in dm1["runs"]:
    v = r["variant"]
    if v not in p1_by_var:
        a = r["artifacts"]
        p1_by_var[v] = (a[f"{v}.conf"]["sha256"], a[f"{v}.top"]["sha256"])
for var in VARIANTS:
    p2_confs = {r["conf_sha256"] for r in dm2["runs"] if r["variant"] == var}
    p2_tops = {r["top_sha256"] for r in dm2["runs"] if r["variant"] == var}
    check(p2_confs == {p1_by_var[var][0]} and p2_tops == {p1_by_var[var][1]},
          f"cross-platform input identity {var}: P2 sha256(conf/top) identical across all 10 runs and == P1-recorded digests")

print("=" * 72)
print()
if problems:
    print(f"RESULT: {len(problems)} PROBLEM(S):")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("RESULT: ALL TASK-1 CHECKS PASS")
