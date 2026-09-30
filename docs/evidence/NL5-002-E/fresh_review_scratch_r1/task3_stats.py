#!/usr/bin/env python3
"""FRESH REVIEWER Task 3: independent frozen-plan paired statistics.

Uses committed P1 medians + committed P2 medians (P2 medians independently
verified against raw replay in Task 2). No operator code is imported or run.

Frozen plan (verbatim from passport/WO/task):
  d_i = median(P2, seed_i) - median(P1, seed_i)
  shift_v = median_i(d_i)
  MAD = raw MAD (no 1.4826), over the 10 per-seed medians per platform/variant
  within_v = median(MAD_P1, MAD_P2)
  ratio_v: within>0 -> |shift|/within; within==0,shift==0 -> 0; within==0,shift>0 -> +INF
  bootstrap: random.Random(902107), B=10000, per resample draw N=10 indices WITH
    replacement from 0..9, statistic = median of selected d_i
  percentile CI95: h=(B-1)*p; lo=floor(h); hi=ceil(h); q = a[lo] + (h-lo)*(a[hi]-a[lo])
  verdict: SENSITIVE = CI excludes 0 AND ratio>=1; INSENSITIVE = CI contains 0 OR ratio<0.5
           else INCONCLUSIVE; WO: both S -> PLATFORM_SENSITIVE, both I -> PLATFORM_INSENSITIVE
"""
import json
import math
import os
import random
import re
import statistics
import sys

REPO = "/home/rdpuser/NanoLab/nl5-002-e-p2-exec"
EX = os.path.join(REPO, "docs/work/executions/EX-NL5-002-E-R1")
P1_AN = os.path.join(EX, "evidence/p1/analysis")
P2_AN = os.path.join(EX, "evidence/p2/analysis")
PAIRED = os.path.join(EX, "evidence/paired/paired_platform_sensitivity.json")

SEEDS = {
    "S001": 1259289227, "S002": 1358106528, "S003": 1524307444, "S004": 601855227,
    "S005": 274288237, "S006": 972234272, "S007": 1934775205, "S008": 1747973984,
    "S009": 880427736, "S010": 744386736,
}
SIDS = sorted(SEEDS)
VARIANTS = ("0b", "32b")
B = 10000
BOOT_SEED = 902107
N = 10

problems = []


def check(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        problems.append(msg)


def mad(xs):
    m = statistics.median(xs)
    return statistics.median([abs(x - m) for x in xs])


def percentile_frozen(a_sorted, p):
    """Frozen: h=(B-1)*p; lo=floor(h); hi=ceil(h); q=a[lo]+(h-lo)*(a[hi]-a[lo])."""
    h = (len(a_sorted) - 1) * p
    lo = math.floor(h)
    hi = math.ceil(h)
    return a_sorted[lo] + (h - lo) * (a_sorted[hi] - a_sorted[lo])


def bootstrap_ci(d_list, draw):
    rng = random.Random(BOOT_SEED)
    stats = []
    for _ in range(B):
        idx = draw(rng, N)
        stats.append(statistics.median([d_list[i] for i in idx]))
    stats.sort()
    return [percentile_frozen(stats, 0.025), percentile_frozen(stats, 0.975)], stats


DRAWS = {
    "randrange": lambda rng, n: [rng.randrange(n) for _ in range(n)],
    "randint": lambda rng, n: [rng.randint(0, n - 1) for _ in range(n)],
    "choice": lambda rng, n: [rng.choice(range(n)) for _ in range(n)],
    "choices": lambda rng, n: rng.choices(range(n), k=n),
}


def load_meds(an_dir, var):
    meds = {}
    for sid in SIDS:
        pat = re.compile(rf"^PLATSENS-P1-{var.upper()}-{sid}(-R\d+)?_analysis\.json$")
        if os.path.basename(os.path.dirname(an_dir)) == "p2":
            pat = re.compile(rf"^PLATSENS-P2-{var.upper()}-{sid}_analysis\.json$")
        files = [f for f in os.listdir(an_dir) if pat.match(f)]
        assert len(files) == 1, (an_dir, var, sid, files)
        d = json.load(open(os.path.join(an_dir, files[0])))
        assert d["engine_exit_code"] == 0
        meds[sid] = d["replica_median_deg"]
    return meds


op = json.load(open(PAIRED))

print("=" * 100)
print("TASK 3a: per-seed d_i (my recomputation vs operator per_seed table)")
my = {}
for var in VARIANTS:
    p1m = load_meds(P1_AN, var)
    p2m = load_meds(P2_AN, var)
    d = {sid: p2m[sid] - p1m[sid] for sid in SIDS}
    my[var] = {"p1": p1m, "p2": p2m, "d": d}
    for sid in SIDS:
        op_row = next(r for r in op["variants"][var]["per_seed"] if r["seed_id"] == sid)
        check(p1m[sid] == op_row["p1_median_deg"],
              f"{var}/{sid}: P1 median exact match {p1m[sid]!r}")
        check(p2m[sid] == op_row["p2_median_deg"],
              f"{var}/{sid}: P2 median exact match {p2m[sid]!r}")
        check(d[sid] == op_row["d_deg"],
              f"{var}/{sid}: d_i exact match {d[sid]!r}")
    # pairing identity
    check(op["pairing_gate"]["pairs_0b"] == 10 and op["pairing_gate"]["pairs_32b"] == 10,
          "operator pairing_gate: 10 pairs per variant")

print("=" * 100)
print("TASK 3b: shift / MAD / within / ratio (exact float comparison)")
for var in VARIANTS:
    d_list = [my[var]["d"][s] for s in SIDS]
    shift = statistics.median(d_list)
    m1 = mad([my[var]["p1"][s] for s in SIDS])
    m2 = mad([my[var]["p2"][s] for s in SIDS])
    within = statistics.median([m1, m2])
    if within > 0:
        ratio = abs(shift) / within
    elif shift == 0:
        ratio = 0.0
    else:
        ratio = float("inf")
    o = op["variants"][var]
    check(shift == o["shift_v_deg"], f"{var}: shift_v exact match: mine={shift!r} op={o['shift_v_deg']!r}")
    check(m1 == o["mad_p1_deg"], f"{var}: MAD_P1 exact match: mine={m1!r} op={o['mad_p1_deg']!r}")
    check(m2 == o["mad_p2_deg"], f"{var}: MAD_P2 exact match: mine={m2!r} op={o['mad_p2_deg']!r}")
    check(within == o["within_v_deg"], f"{var}: within_v exact match: mine={within!r} op={o['within_v_deg']!r}")
    check(ratio == o["ratio_v"], f"{var}: ratio_v exact match: mine={ratio!r} op={o['ratio_v']!r}")
    my[var].update(shift=shift, m1=m1, m2=m2, within=within, ratio=ratio)

print("=" * 100)
print("TASK 3c: bootstrap CI under frozen RNG/percentile (4 stdlib index-draw idioms; "
      "plan does not pin the call)")
ci_result = {}
for var in VARIANTS:
    d_list = [my[var]["d"][s] for s in SIDS]
    o = op["variants"][var]
    op_ci = o["bootstrap"]["ci95_deg"]
    print(f"  -- variant {var}: operator CI95 = [{op_ci[0]!r}, {op_ci[1]!r}]")
    ci_result[var] = {}
    for name, draw in DRAWS.items():
        (lo, hi), stats = bootstrap_ci(d_list, draw)
        contains0 = lo <= 0.0 <= hi
        exact = (lo == op_ci[0] and hi == op_ci[1])
        near = abs(lo - op_ci[0]) < 1e-9 and abs(hi - op_ci[1]) < 1e-9
        ci_result[var][name] = (lo, hi, contains0, exact)
        print(f"     {name:9s}: mine=[{lo!r}, {hi!r}] contains0={contains0} "
              f"exact_match_to_operator={exact} (|diff|<{1e-9}: {near})")

print("=" * 100)
print("TASK 3d: verdicts per frozen decision rule (my primary implementation = randrange)")
verdicts = {}
for var in VARIANTS:
    lo, hi, contains0, _ = ci_result[var]["randrange"]
    ratio = my[var]["ratio"]
    if (not contains0) and ratio >= 1:
        v = "PLATFORM_SENSITIVE"
    elif contains0 or ratio < 0.5:
        v = "PLATFORM_INSENSITIVE"
    else:
        v = "INCONCLUSIVE"
    verdicts[var] = v
    o = op["variants"][var]
    check(v == o["verdict"], f"{var}: verdict mine={v} operator={o['verdict']}")
    check(o["bootstrap"]["ci_contains_zero"] == contains0,
          f"{var}: ci_contains_zero mine={contains0} operator={o['bootstrap']['ci_contains_zero']}")

if all(verdicts[v] == "PLATFORM_SENSITIVE" for v in VARIANTS):
    wo = "PLATFORM_SENSITIVE"
elif all(verdicts[v] == "PLATFORM_INSENSITIVE" for v in VARIANTS):
    wo = "PLATFORM_INSENSITIVE"
else:
    wo = "INCONCLUSIVE"
check(wo == op["wo_level_verdict"], f"WO-level verdict mine={wo} operator={op['wo_level_verdict']}")

print("=" * 100)
print("TASK 3e: verdict robustness across bootstrap index-draw idioms")
for var in VARIANTS:
    ratio = my[var]["ratio"]
    vs = set()
    for name in DRAWS:
        lo, hi, contains0, _ = ci_result[var][name]
        if (not contains0) and ratio >= 1:
            vs.add("PLATFORM_SENSITIVE")
        elif contains0 or ratio < 0.5:
            vs.add("PLATFORM_INSENSITIVE")
        else:
            vs.add("INCONCLUSIVE")
    check(len(vs) == 1, f"{var}: verdict identical across all 4 idioms -> {vs}")

print("=" * 100)
print()
if problems:
    print(f"RESULT: {len(problems)} PROBLEM(S)")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("RESULT: ALL TASK-3 CHECKS PASS")

# machine-readable summary for the report
summary = {
    "variants": {
        var: {
            "shift_v_deg": my[var]["shift"],
            "mad_p1_deg": my[var]["m1"],
            "mad_p2_deg": my[var]["m2"],
            "within_v_deg": my[var]["within"],
            "ratio_v": my[var]["ratio"],
            "ci95_randrange": ci_result[var]["randrange"][:2],
            "ci95_all_idioms": {k: ci_result[var][k][:2] for k in DRAWS},
            "ci_contains_zero": ci_result[var]["randrange"][2],
            "verdict": verdicts[var],
        } for var in VARIANTS
    },
    "wo_level_verdict": wo,
    "d_table": {var: {sid: my[var]["d"][sid] for sid in SIDS} for var in VARIANTS},
    "p1_medians": {var: my[var]["p1"] for var in VARIANTS},
    "p2_medians": {var: my[var]["p2"] for var in VARIANTS},
}
json.dump(summary, open("/tmp/reviewer_p2/task3_stats_summary.json", "w"), indent=1)
print("summary written to /tmp/reviewer_p2/task3_stats_summary.json")
