#!/usr/bin/env python3
"""EX-NL5-002-E-R1 frozen paired platform-sensitivity analysis.

Runs ONLY after P1 evidence is committed and mechanically matched with the
published P2 evidence. Implements the frozen statistics plan verbatim:
  d_i = P2 replica_median_deg - P1 replica_median_deg (per seed)
  shift_v = median(d_i)
  MAD(x) = median(|x_i - median(x)|)
  within_v = median(MAD(P1 cell), MAD(P2 cell))
  ratio_v = |shift_v| / within_v   (frozen within=0 rule below)
  bootstrap: Python random.Random(902107), 10000 resamples, paired index
  sampling, percentile CI95 with linear interpolation
  PLATFORM_SENSITIVE iff CI excludes 0 AND ratio >= 1
  PLATFORM_INSENSITIVE iff CI contains 0 OR ratio < 0.5
  otherwise INCONCLUSIVE
WO-level: both sensitive -> PLATFORM_SENSITIVE; both insensitive ->
PLATFORM_INSENSITIVE; otherwise INCONCLUSIVE.

Frozen within=0 rule: if within_v == 0 then ratio_v = inf when shift_v != 0
(perfectly identical cells cannot be shifted), and 0 when shift_v == 0.
"""
import json
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.dirname(HERE)  # .../EX-NL5-002-E-R1/evidence
P2_AN = os.path.join(EV, "p2", "analysis")
P1_AN = os.path.join(EV, "p1", "analysis")

SEEDS = {
    "S001": 1259289227, "S002": 1358106528, "S003": 1524307444, "S004": 601855227,
    "S005": 274288237, "S006": 972234272, "S007": 1934775205, "S008": 1747973984,
    "S009": 880427736, "S010": 744386736,
}
VARIANTS = ("0b", "32b")
BOOT_N = 10000
BOOT_SEED = 902107


def mad(xs):
    m = statistics.median(xs)
    return statistics.median([abs(x - m) for x in xs])


def percentile_linear(sorted_xs, q):
    """Percentile q in [0,100] with linear interpolation (frozen implementation)."""
    if len(sorted_xs) == 1:
        return sorted_xs[0]
    pos = (len(sorted_xs) - 1) * (q / 100.0)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_xs) - 1)
    frac = pos - lo
    return sorted_xs[lo] * (1.0 - frac) + sorted_xs[hi] * frac


RUNMAPS = {
    "P1": os.path.join(EV, "seeds_runmap_p1.json"),
    "P2": os.path.join(EV, "p2", "seeds_runmap_p2.json"),
}


def canonical_seed(platform, run_id, variant):
    """Frozen seed for a slot from the committed runmap (base ID, no -R suffix).

    P1 runmap: run_map -> {variant: {base_run_id: seed}}.
    P2 runmap: seeds -> {Sxxx: seed} (identical frozen list by design).
    """
    m = json.load(open(RUNMAPS[platform]))
    base = run_id.split("-R")[0]
    sid = base.split("-")[-1]
    if "run_map" in m:
        return m["run_map"][variant][base]
    return m["seeds"][sid]


def load_variant(an_dir, platform, variant):
    import glob as _glob
    out = {}
    for sid in SEEDS:
        # final attempt = highest -R<N> analysis present, else base attempt
        base = "PLATSENS-%s-%s-%s_analysis.json" % (platform, variant.upper(), sid)
        patt = "PLATSENS-%s-%s-%s-R*_analysis.json" % (platform, variant.upper(), sid)
        retries = _glob.glob(os.path.join(an_dir, patt))
        found = None
        if retries:
            def rnum(p):
                n = os.path.basename(p).replace("_analysis.json", "").split("-R")[-1]
                return int(n)
            found = max(retries, key=rnum)
        else:
            p = os.path.join(an_dir, base)
            if os.path.isfile(p):
                found = p
        if found is None:
            raise SystemExit("MISSING analysis: %s %s %s" % (platform, variant, sid))
        with open(found) as f:
            data = json.load(f)
        rid = data.get("run_id")
        med = data.get("replica_median_deg")
        if med is None:
            raise SystemExit("no replica_median_deg in %s" % found)
        if data.get("engine_exit_code") != 0:
            raise SystemExit("engine_exit_code != 0 in %s" % found)
        # packaged analyzer may record seed as null (accepted precedent);
        # the frozen seed for pairing comes from the committed runmap
        seed_frozen = canonical_seed(platform, rid, variant)
        out[sid] = {"file": os.path.basename(found), "run_id": rid,
                    "seed": data.get("seed"),
                    "seed_frozen_runmap": seed_frozen,
                    "steps": data.get("window_steps") or data.get("window"),
                    "replica_median_deg": med,
                    "frames_valid": data.get("frames_valid_in_window"),
                    "frames_total": data.get("frames_in_window")}
    return out


def analyze_variant(variant, p1, p2, rng_tables):
    ds = {sid: p2[sid]["replica_median_deg"] - p1[sid]["replica_median_deg"]
          for sid in SEEDS}
    d_list = [ds[s] for s in sorted(SEEDS)]
    shift_v = statistics.median(d_list)
    mad_p1 = mad([p1[s]["replica_median_deg"] for s in sorted(SEEDS)])
    mad_p2 = mad([p2[s]["replica_median_deg"] for s in sorted(SEEDS)])
    within_v = statistics.median([mad_p1, mad_p2])
    if within_v == 0:
        ratio_v = float("inf") if shift_v != 0 else 0.0
    else:
        ratio_v = abs(shift_v) / within_v
    # frozen bootstrap: paired index sampling, one shared frozen RNG per plan
    rng = random.Random(BOOT_SEED)
    n = len(d_list)
    meds = []
    for _ in range(BOOT_N):
        sample = [d_list[rng.randrange(n)] for _ in range(n)]
        meds.append(statistics.median(sample))
    meds.sort()
    ci95 = [percentile_linear(meds, 2.5), percentile_linear(meds, 97.5)]
    ci_contains_zero = ci95[0] <= 0 <= ci95[1]
    if (not ci_contains_zero) and ratio_v >= 1:
        verdict = "PLATFORM_SENSITIVE"
    elif ci_contains_zero or ratio_v < 0.5:
        verdict = "PLATFORM_INSENSITIVE"
    else:
        verdict = "INCONCLUSIVE"
    rng_tables[variant] = meds
    return {
        "variant": variant,
        "per_seed": [{"seed_id": sid, "seed": SEEDS[sid],
                      "p1_run": p1[sid]["run_id"], "p2_run": p2[sid]["run_id"],
                      "p1_median_deg": p1[sid]["replica_median_deg"],
                      "p2_median_deg": p2[sid]["replica_median_deg"],
                      "d_deg": ds[sid]} for sid in sorted(SEEDS)],
        "shift_v_deg": shift_v,
        "mad_p1_deg": mad_p1, "mad_p2_deg": mad_p2,
        "within_v_deg": within_v,
        "ratio_v": ratio_v,
        "within_zero_rule": "applied (within_v=0 -> ratio=inf if shift!=0 else 0)",
        "bootstrap": {"rng": "Python random.Random(%d)" % BOOT_SEED,
                      "resamples": BOOT_N,
                      "sampling": "paired index sampling over d_i",
                      "statistic": "median",
                      "ci95_deg": ci95,
                      "ci_interpolation": "linear",
                      "ci_contains_zero": ci_contains_zero},
        "verdict": verdict,
    }


def main():
    # mechanical pairing gate
    pairing = {}
    for variant in VARIANTS:
        p1 = load_variant(P1_AN, "P1", variant)
        p2 = load_variant(P2_AN, "P2", variant)
        for sid in sorted(SEEDS):
            assert p1[sid]["seed_frozen_runmap"] == p2[sid]["seed_frozen_runmap"] == SEEDS[sid], (variant, sid)
            assert p1[sid]["steps"] == p2[sid]["steps"], (variant, sid)
            assert ("-%s-" % variant.upper()) in p1[sid]["run_id"] and ("-%s-" % variant.upper()) in p2[sid]["run_id"], (variant, sid)
        pairing[variant] = {"p1": p1, "p2": p2}
    rng_tables = {}
    results = [analyze_variant(v, pairing[v]["p1"], pairing[v]["p2"], rng_tables)
               for v in VARIANTS]
    verdicts = {r["variant"]: r["verdict"] for r in results}
    if all(v == "PLATFORM_SENSITIVE" for v in verdicts.values()):
        wo = "PLATFORM_SENSITIVE"
    elif all(v == "PLATFORM_INSENSITIVE" for v in verdicts.values()):
        wo = "PLATFORM_INSENSITIVE"
    else:
        wo = "INCONCLUSIVE"
    out = {
        "kind": "platform_sensitivity_paired_analysis_v1",
        "execution_id": "EX-NL5-002-E-R1",
        "statistics_plan": "frozen in WO-NL5-002-E-R1 (shift_v median of paired d_i; within_v=median(MAD_P1,MAD_P2); ratio_v=|shift|/within with frozen within=0 rule; bootstrap random.Random(902107), 10000 paired-index resamples, percentile CI95 linear interpolation)",
        "pairing_gate": {"seeds_identical": True, "steps_identical": True,
                         "pairs_0b": 10, "pairs_32b": 10},
        "execution_deviation_disclosure": {
            "EXECUTION_ORCHESTRATION_DEVIATION": "YES",
            "SCIENTIFIC_PROTOCOL_MUTATION": "NO",
            "cause": "P2 dispatched before durable P1-complete evidence (Director override); scientific pins (seeds, steps, variants, engine, package, analyzer) unchanged"},
        "variants": {r["variant"]: r for r in results},
        "wo_level_verdict": wo,
        "nl5_nl6_status": {"NL5": "IN_PROGRESS", "external_reproductions": 0,
                           "NL6-001": "LOCKED",
                           "note": "unchanged pending NL5-ACCEPTANCE-POLICY"},
        "boundary": "computed by SCIENTIFIC_OPERATOR per frozen plan; NOT Director acceptance; fresh Reviewer + fresh Verifier + Director gate apply",
    }
    out_path = os.path.join(HERE, "paired_platform_sensitivity.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    for r in results:
        print("%s: shift=%.6f ci95=[%.6f, %.6f] within=%.6f ratio=%s -> %s" % (
            r["variant"], r["shift_v_deg"], r["bootstrap"]["ci95_deg"][0],
            r["bootstrap"]["ci95_deg"][1], r["within_v_deg"],
            r["ratio_v"], r["verdict"]))
    print("WO_VERDICT:", wo)
    print("written:", out_path)


if __name__ == "__main__":
    main()
