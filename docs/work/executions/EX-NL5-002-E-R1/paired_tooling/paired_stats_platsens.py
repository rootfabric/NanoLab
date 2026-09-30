#!/usr/bin/env python3
"""Frozen paired platform-sensitivity statistics (EX-NL5-002-E-R1), per
passport.statistics_frozen_pre_data - implemented VERBATIM:

  d_i      = median(P2, seed_i) - median(P1, seed_i)
  shift_v  = median_i(d_i)
  MAD      = RAW MAD, NO 1.4826:  median(|x_i - median(x)|)
  within_v = median( MAD(P1 variant v), MAD(P2 variant v) )
  ratio    = |shift|/within  (degenerate: within==0 & shift==0 -> 0;
                               within==0 & |shift|>0 -> +INF)
  bootstrap: Python random.Random(902107), 10000 resamples, paired indices
             with replacement, statistic = median(resampled d_i),
             percentile CI95 with linear interpolation:
             h=(B-1)*p; lo=floor(h); hi=ceil(h); q = a[lo] + (h-lo)*(a[hi]-a[lo])
  verdict (variant): SENSITIVE  = CI excludes 0 AND ratio >= 1
                      INSENSITIVE= CI contains 0 OR ratio < 0.5
                      otherwise INCONCLUSIVE
  WO verdict: both SENSITIVE -> PLATFORM_SENSITIVE;
              both INSENSITIVE -> PLATFORM_INSENSITIVE; else INCONCLUSIVE

MUST NOT be run on campaign data until P1 evidence exists (paired completeness
gate: 10 complete pairs per variant). --self-test validates the implementation
on synthetic data only.
"""
import json, random, sys, os

B = 10000
RNG_SEED = 902107
SEEDS = [f"S{i:03d}" for i in range(1, 11)]
VARIANTS = ("0b", "32b")

def median(xs):
    s = sorted(xs); n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0

def mad_raw(xs):
    m = median(xs)
    return median([abs(x - m) for x in xs])

def bootstrap_ci(diffs):
    rng = random.Random(RNG_SEED)
    stats = []
    n = len(diffs)
    for _ in range(B):
        idx = [rng.randrange(n) for _ in range(n)]
        stats.append(median([diffs[i] for i in idx]))
    stats.sort()
    def q(p):
        h = (B - 1) * p
        lo, hi = int(h // 1), min(int(h // 1) + 1, B - 1)
        import math
        lo, hi = math.floor(h), math.ceil(h)
        if lo == hi:
            return stats[lo]
        return stats[lo] + (h - lo) * (stats[hi] - stats[lo])
    return q(0.025), q(0.975)

def variant_stats(m1, m2):
    d = [m2[s] - m1[s] for s in SEEDS]
    shift = median(d)
    lo, hi = bootstrap_ci(d)
    mad1 = mad_raw([m1[s] for s in SEEDS])
    mad2 = mad_raw([m2[s] for s in SEEDS])
    within = median([mad1, mad2])
    if within > 0:
        ratio = abs(shift) / within
    elif abs(shift) == 0:
        ratio = 0.0
    else:
        ratio = float("inf")
    contains0 = (lo <= 0.0 <= hi)
    if (not contains0) and ratio >= 1:
        verdict = "SENSITIVE"
    elif contains0 or ratio < 0.5:
        verdict = "INSENSITIVE"
    else:
        verdict = "INCONCLUSIVE"
    return {"d_i": {s: m2[s] - m1[s] for s in SEEDS}, "shift": shift,
            "ci95": [lo, hi], "ci_contains_zero": contains0,
            "mad_p1": mad1, "mad_p2": mad2, "within": within, "ratio": ratio,
            "verdict": verdict}

def load_medians(path_glob):
    import glob as g
    out = {}
    for f in sorted(g.glob(path_glob)):
        d = json.load(open(f))
        rid = d["run_id"]; s = rid.split("-")[-1]
        out[s] = float(d["replica_median_deg"])
    return out

def main():
    if "--self-test" in sys.argv:
        return self_test()
    p1_dir = sys.argv[1]; p2_dir = sys.argv[2]
    result = {"kind": "platform_sensitivity_paired_stats_v1",
              "execution_id": "EX-NL5-002-E-R1", "bootstrap_rng": RNG_SEED,
              "bootstrap_resamples": B, "variants": {}}
    verdicts = {}
    for v in VARIANTS:
        m1 = load_medians(os.path.join(p1_dir, f"PLATSENS-P1-{v.upper()}-S*_analysis.json"))
        m2 = load_medians(os.path.join(p2_dir, f"PLATSENS-P2-{v.upper()}-S*_analysis.json"))
        missing = [s for s in SEEDS if s not in m1 or s not in m2]
        if missing:
            print(f"PAIRED_COMPLETENESS_GATE_FAIL variant={v} missing={missing}")
            sys.exit(1)
        result["variants"][v] = variant_stats(m1, m2)
        verdicts[v] = result["variants"][v]["verdict"]
    if verdicts["0b"] == "SENSITIVE" and verdicts["32b"] == "SENSITIVE":
        wo = "PLATFORM_SENSITIVE"
    elif verdicts["0b"] == "INSENSITIVE" and verdicts["32b"] == "INSENSITIVE":
        wo = "PLATFORM_INSENSITIVE"
    else:
        wo = "INCONCLUSIVE"
    result["wo_verdict"] = wo
    print(json.dumps(result, indent=2))

def self_test():
    ok = True
    # case 1: identical platforms -> shift 0, CI [0,0], INSENSITIVE
    m1 = {s: float(50 + i) for i, s in enumerate(SEEDS)}
    r = variant_stats(m1, dict(m1))
    ok &= (r["shift"] == 0 and r["ci95"] == [0.0, 0.0] and r["verdict"] == "INSENSITIVE")
    # case 2: constant +100 shift on spread platforms -> SENSITIVE
    m2 = {s: m1[s] + 100.0 for s in SEEDS}
    r2 = variant_stats(m1, m2)
    ok &= (r2["shift"] == 100.0 and r2["ci95"] == [100.0, 100.0]
           and r2["within"] > 0 and r2["verdict"] == "SENSITIVE")
    # case 3: degenerate within==0, shift>0 -> ratio INF, CI excludes 0 -> SENSITIVE
    m3 = {s: 10.0 for s in SEEDS}; m4 = {s: 12.0 for s in SEEDS}
    r3 = variant_stats(m3, m4)
    ok &= (r3["ratio"] == float("inf") and r3["verdict"] == "SENSITIVE")
    # case 4: determinism - same input twice gives byte-identical CI
    ma = {s: 1.0 + ((i * 37) % 11) for i, s in enumerate(SEEDS)}
    mb = {s: 1.0 + ((i * 53) % 13) + 2 for i, s in enumerate(SEEDS)}
    ra, rb = variant_stats(ma, mb), variant_stats(ma, mb)
    ok &= (ra["ci95"] == rb["ci95"] and ra["shift"] == rb["shift"])
    # case 5: swap symmetry sign check (NC2 property): shift(P2,P1) = -shift(P1,P2)
    ok &= (variant_stats(mb, ma)["shift"] == -ra["shift"])
    print("SELF_TEST:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
