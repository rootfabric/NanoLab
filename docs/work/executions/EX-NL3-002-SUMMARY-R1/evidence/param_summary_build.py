"""EX-NL3-002-SUMMARY-R1: parametric common-window (t <= 150000) summary builder.

No physics runs. Reads ONLY published evidence JSONs from the merged
parametric branches. Recomputes per-replica and pooled angle statistics over
the common comparison window t <= 150000 (E2_PROTO_R1 addendum section 8)
using the frozen section-6 methodology (median/IQR/q5-q95 + bootstrap CI95,
10000 resamples, seed 424242) byte-identical to confirm_analysis.py.

Frame time: every published analysis JSON stores per-frame "time" (oxDNA
steps, print_conf_interval = 4000), so windowing uses the recorded frame
time directly — no index-based reconstruction and no raw trajectory access.

Determinism: pure function of the input JSONs; two runs must produce a
byte-identical parametric-summary.json (verified by the caller).
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.canonical import canonical_json  # noqa: E402

EV = lambda *p: os.path.join(REPO, "docs", "work", "executions", *p)

WINDOW_STEPS = 150000
BOOT_N = 10000
BOOT_SEED = 424242


def quantile_sorted(sorted_vals, q):
    """Linear-interpolation quantile (numpy 'linear' method), deterministic."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def angle_stats(angles):
    if not angles:
        return None
    s = sorted(angles)
    med = quantile_sorted(s, 0.5)
    q1 = quantile_sorted(s, 0.25)
    q3 = quantile_sorted(s, 0.75)
    q05 = quantile_sorted(s, 0.05)
    q95 = quantile_sorted(s, 0.95)
    rng = random.Random(BOOT_SEED)
    n = len(s)
    meds = []
    for _ in range(BOOT_N):
        sample = [s[rng.randrange(n)] for _ in range(n)]
        sample.sort()
        meds.append(quantile_sorted(sample, 0.5))
    meds.sort()
    return {
        "n_frames": n,
        "median_deg": med,
        "iqr_deg": [q1, q3],
        "q05_deg": q05, "q95_deg": q95,
        "mean_deg": sum(s) / n,
        "min_deg": s[0], "max_deg": s[-1],
        "bootstrap": {"resamples": BOOT_N, "seed": BOOT_SEED, "statistic": "median",
                      "ci95": [quantile_sorted(meds, 0.025), quantile_sorted(meds, 0.975)]},
    }


def window_angles(frames, window=WINDOW_STEPS):
    """Valid in-window angles + window bookkeeping from published frame rows."""
    in_win = [f for f in frames if int(f["time"]) <= window]
    valid = [f for f in in_win if f.get("valid") and f.get("angle_deg") is not None]
    return [f["angle_deg"] for f in valid], {
        "frames_total": len(frames),
        "frames_in_window": len(in_win),
        "frames_valid_in_window": len(valid),
        "valid_frame_fraction_in_window": len(valid) / len(in_win) if in_win else None,
        "time_first_steps": int(frames[0]["time"]) if frames else None,
        "time_last_steps": int(frames[-1]["time"]) if frames else None,
        "time_last_in_window_steps": int(in_win[-1]["time"]) if in_win else None,
    }


def load(path):
    with open(path, "r", encoding="utf-8", newline="") as h:
        return json.load(h)


def variant_block(variant, replica_reports, published, steps_mode, extra=None):
    """replica_reports: list of (run_id, seed, frames). published: dict with
    per-replica and pooled published angle stats."""
    per_replica = {}
    pooled = []
    for run_id, seed, frames in replica_reports:
        angles, info = window_angles(frames)
        pooled += angles
        per_replica[run_id] = {
            "seed": seed,
            "window": info,
            "angle_stats_valid_frames_in_window": angle_stats(angles),
        }
    block = {
        "parameter": variant,
        "execution_id": extra["execution_id"],
        "steps_mode": steps_mode,
        "common_window_steps": WINDOW_STEPS,
        "window_method": "per-frame recorded time (oxDNA steps, print_conf_interval=4000) filtered to <= 150000",
        "reslice_note": extra.get("reslice_note"),
        "per_replica_common_window": per_replica,
        "pooled_common_window": {
            "valid_frames_total": len(pooled),
            "angle_stats_valid_frames": angle_stats(pooled),
        },
        "published_as_recorded": published,
    }
    if extra:
        for k, v in extra.items():
            if k not in ("execution_id", "reslice_note"):
                block[k] = v
    return block


def pub_stats(st):
    if st is None:
        return None
    return {
        "n_frames": st["n_frames"],
        "median_deg": st["median_deg"],
        "iqr_deg": st["iqr_deg"],
        "q05_deg": st["q05_deg"], "q95_deg": st["q95_deg"],
        "bootstrap_ci95": st["bootstrap"]["ci95"],
    }


def main() -> int:
    # ---- 0b confirmatory (EX-NL3-002-R1) --------------------------------
    conf = load(EV("EX-NL3-002-R1", "evidence", "confirmatory-summary.json"))
    reps0 = []
    for pref, rid in (("c001", "E2-R1-C001"), ("c002", "E2-R1-C002"), ("c003", "E2-R1-C003")):
        rep = load(EV("EX-NL3-002-R1", "evidence", f"{pref}-analysis.json"))
        assert rep["run_id"] == rid
        reps0.append((rid, conf["runs"][rid]["seed"], rep["frames"]))
    pub0 = {
        "steps_requested": 200000,
        "pooled": pub_stats(conf["pooled_angle_stats_valid_frames"]),
        "per_replica": {rid: pub_stats(conf["runs"][rid]["angle_stats_valid_frames"])
                        for rid in (r[0] for r in reps0)},
    }
    block0 = variant_block(
        "0b", reps0, pub0,
        "200000 confirmatory (frozen primary; NOT resliced for the primary result)",
        {
            "execution_id": "EX-NL3-002-R1",
            "reslice_note": "addendum s.8 item 3: secondary cross-variant table reslices 0b to t <= 150000; primary confirmatory result (200000 steps) is NOT revised",
            "published_source": "docs/work/executions/EX-NL3-002-R1/evidence/confirmatory-summary.json (+c001-003-analysis.json frame rows)",
        })

    # ---- 11b (truncated at ~184000 by budget interrupt) ------------------
    a11 = load(EV("EX-NL3-002-PARAM-11B-R1", "evidence", "PARAM-11B-analysis.json"))
    reps11 = []
    for s in ("s001", "s002", "s003"):
        rep = a11["runs"][s]
        reps11.append((rep["run_id"], rep["seed"], rep["frames"]))
    p11pub = {rid: st["angle_stats_valid_frames"] for rid, st in
              ((a11["runs"][s]["run_id"], a11["runs"][s]) for s in ("s001", "s002", "s003"))}
    pooled11pub = load(EV("EX-NL3-002-PARAM-11B-R1", "evidence", "PARAM-11B-summary.json"))
    pub11 = {
        "steps_requested": 200000,
        "truncation": "SIGTERM budget interrupt at 3.5h (E2_PROTO_R1 s.5); 46/50 frames written, last t = 184000",
        "pooled": pub_stats(pooled11pub["pooled_angle_stats_valid_frames"]),
        "per_replica": {rid: pub_stats(st) for rid, st in p11pub.items()},
    }
    block11 = variant_block(
        "11b", reps11, pub11,
        "200000 requested, truncated at ~184000 steps (ABORTED_BUDGET_INTERRUPT; window covered)",
        {
            "execution_id": "EX-NL3-002-PARAM-11B-R1",
            "reslice_note": "addendum s.8 item 1: 11b covers the window and is resliced to t <= 150000 without a rerun",
            "published_source": "docs/work/executions/EX-NL3-002-PARAM-11B-R1/evidence/PARAM-11B-summary.json (+PARAM-11B-analysis.json frame rows)",
        })

    # ---- 32b (150000 steps, already fully inside the window) -------------
    a32 = load(EV("EX-NL3-002-PARAM-32B-R1", "evidence", "PARAM-32B-analysis.json"))
    reps32 = []
    for s in ("s001", "s002", "s003"):
        rep = a32["runs"][s]
        reps32.append((rep["run_id"], rep["seed"], rep["frames"]))
    p32pub = {a32["runs"][s]["run_id"]: a32["runs"][s]["angle_stats_valid_frames"]
              for s in ("s001", "s002", "s003")}
    pooled32pub = load(EV("EX-NL3-002-PARAM-32B-R1", "evidence", "PARAM-32B-summary.json"))
    pub32 = {
        "steps_requested": 150000,
        "pooled": pub_stats(pooled32pub["pooled_angle_stats_valid_frames"]),
        "per_replica": {rid: pub_stats(st) for rid, st in p32pub.items()},
    }
    block32 = variant_block(
        "32b", reps32, pub32,
        "150000 (addendum s.8 item 1)",
        {
            "execution_id": "EX-NL3-002-PARAM-32B-R1",
            "reslice_note": "full data already within t <= 150000 (37 frames, last t = 148000); common-window stats recomputed here must equal published stats",
            "published_source": "docs/work/executions/EX-NL3-002-PARAM-32B-R1/evidence/PARAM-32B-summary.json (+PARAM-32B-analysis.json frame rows)",
        })

    # ---- 53b (150000 steps, already fully inside the window) -------------
    a53 = load(EV("EX-NL3-002-PARAM-53B-R1", "evidence", "PARAM-53B-analysis.json"))
    reps53 = []
    for s in ("s001", "s002", "s003"):
        rep = load(EV("EX-NL3-002-PARAM-53B-R1", "evidence", f"{s}-analysis.json"))
        reps53.append((rep["run_id"], rep["seed"], rep["frames"]))
    pooled53pub = a53["pooled_angle_stats_valid_frames"]
    pub53 = {
        "steps_requested": 150000,
        "pooled": pub_stats(pooled53pub),
        "per_replica": {rid: pub_stats(st["angle_stats_valid_frames"])
                        for rid, st in a53["per_replica"].items()},
    }
    block53 = variant_block(
        "53b", reps53, pub53,
        "150000 (addendum s.8 item 1)",
        {
            "execution_id": "EX-NL3-002-PARAM-53B-R1",
            "reslice_note": "full data already within t <= 150000 (37 frames, last t = 148000); common-window stats recomputed here must equal published stats",
            "published_source": "docs/work/executions/EX-NL3-002-PARAM-53B-R1/evidence/PARAM-53B-analysis.json (+s001-003-analysis.json frame rows)",
        })

    # ---- 74b (BLOCKED before runs: manifest derivation failure) ----------
    f74 = load(EV("EX-NL3-002-PARAM-74B-R1", "evidence", "arm-manifest-74b-failure.json"))
    block74 = {
        "parameter": "74b",
        "execution_id": "EX-NL3-002-PARAM-74B-R1",
        "steps_mode": "not run (blocked before runs)",
        "common_window_steps": WINDOW_STEPS,
        "measurement_status": "NOT_MEASURED",
        "reason": "arm-manifest-v1 derivation FAILED_TWO_DOMINANT_BLOCKS (deterministic, byte-identical over 2 attempts); per-variant stop rule -> BLOCKED, honest gap",
        "failure_report": "docs/work/executions/EX-NL3-002-PARAM-74B-R1/evidence/arm-manifest-74b-failure.json",
        "runs": "NOT_RUN (0 physics runs for 74b)",
        "angle_stats": None,
    }

    # ---- arm-manifest cross-variant summary ------------------------------
    m0 = load(EV("EX-NL3-002-PROTO-R1", "evidence", "arm-manifest-0b.json"))
    m0a = m0["arms"]["arm_a"]["nucleotides"]
    m0b = m0["arms"]["arm_b"]["nucleotides"]
    m11 = load(EV("EX-NL3-002-PARAM-11B-R1", "evidence", "arm-manifest-11b-report.json"))
    m32 = load(EV("EX-NL3-002-PARAM-32B-R1", "evidence", "arm-manifest-32b-report.json"))
    m53 = load(EV("EX-NL3-002-PARAM-53B-R1", "evidence", "arm-manifest-53b-report.json"))
    ang0 = m0["validation"]["hinge_angle_frame0"]["angle_deg"]

    def cov(man, *ks):
        c = man.get("coverage", {}) if man else {}
        return {k: c.get(k) for k in ks}

    manifest_summary = {
        "0b": {
            "source": "docs/work/executions/EX-NL3-002-PROTO-R1/evidence/arm-manifest-0b.json (frozen, arm-manifest-v1)",
            "arm_a": len(m0a), "arm_b": len(m0b),
            "angle_frame0_deg": ang0,
            "coverage": m0["coverage"],
        },
        "11b": {
            "source": "docs/work/executions/EX-NL3-002-PARAM-11B-R1/evidence/arm-manifest-11b-report.json",
            "arm_a": m11["arms"]["arm_a_size"], "arm_b": m11["arms"]["arm_b_size"],
            "angle_frame0_deg": m11["angle_frame0_deg"],
            "coverage": cov(m11, "manifest_fraction_of_paired", "manifest_fraction_of_topology", "topology_nucleotides"),
            "determinism": m11["determinism"],
        },
        "32b": {
            "source": "docs/work/executions/EX-NL3-002-PARAM-32B-R1/evidence/arm-manifest-32b-report.json",
            "arm_a": m32["arms"]["arm_a"], "arm_b": m32["arms"]["arm_b"],
            "angle_frame0_deg": m32["validation"]["hinge_angle_frame0"]["angle_deg"],
            "coverage": cov(m32, "manifest_fraction_of_paired", "manifest_fraction_of_topology", "topology_nucleotides"),
            "determinism": m32["determinism"],
        },
        "53b": {
            "source": "docs/work/executions/EX-NL3-002-PARAM-53B-R1/evidence/arm-manifest-53b-report.json",
            "arm_a": m53["arms"]["arm_a"], "arm_b": m53["arms"]["arm_b"],
            "angle_frame0_deg": m53["validation"]["hinge_angle_frame0"]["angle_deg"],
            "coverage": cov(m53, "manifest_fraction_of_paired", "manifest_fraction_of_topology", "topology_nucleotides"),
            "determinism": m53["determinism"],
        },
        "74b": {
            "status": "MANIFEST_DERIVATION_FAILED (FAILED_TWO_DOMINANT_BLOCKS)",
            "source": "docs/work/executions/EX-NL3-002-PARAM-74B-R1/evidence/arm-manifest-74b-failure.json",
            "determinism": {"attempts": 2, "deterministic_identical_error": f74["deterministic_identical_error"]},
        },
    }

    # ---- cross-checks: 32b/53b recomputed window == published ------------
    checks = []
    for name, blk in (("32b", block32), ("53b", block53)):
        rec = blk["pooled_common_window"]["angle_stats_valid_frames"]
        pub = blk["published_as_recorded"]["pooled"]
        checks.append({
            "check": f"{name}: common-window pooled == published (data fully inside window)",
            "ok": rec["median_deg"] == pub["median_deg"]
                  and rec["bootstrap"]["ci95"] == pub["bootstrap_ci95"]
                  and rec["n_frames"] == pub["n_frames"],
        })
    for name, blk, src in (("0b", block0, "confirmatory-summary.json"),
                           ("11b", block11, "PARAM-11B-summary.json")):
        n_pub = blk["published_as_recorded"]["pooled"]["n_frames"]
        n_win = blk["pooled_common_window"]["valid_frames_total"]
        checks.append({
            "check": f"{name}: window valid frames ({n_win}) <= published valid frames ({n_pub})",
            "ok": n_win <= n_pub,
        })

    summary = {
        "schema_version": 1,
        "kind": "e2_parametric_series_common_window_summary",
        "execution_id": "EX-NL3-002-SUMMARY-R1",
        "protocol": "docs/research/E2_PROTO_R1.md (FROZEN, incl. addendum s.8: common comparison window t <= 150000) + docs/research/E2_OBSERVABLES_R2.md",
        "physics_runs_in_this_execution": 0,
        "window": {
            "common_window_steps": WINDOW_STEPS,
            "frame_time_source": "per-frame recorded 'time' field (oxDNA steps) in published analysis JSONs; print_conf_interval = 4000 for all variants",
            "time_reconstruction_assumption": None,
        },
        "statistics_method": "E2_PROTO_R1 s.6 as frozen: median/IQR/q5-q95 over valid in-window frames, pooled across replicas; bootstrap CI95 for the median, 10000 resamples, seed 424242 (same deterministic implementation as EX-NL3-002-R1 evidence/confirm_analysis.py)",
        "variants": {"0b": block0, "11b": block11, "32b": block32, "53b": block53, "74b": block74},
        "arm_manifest_summary": manifest_summary,
        "cross_checks": checks,
        "determinism": "pure function of published evidence JSONs; builder rerun must be byte-identical",
        "scientific_outcome": "MEASURED (aggregated measured distributions; no cross-variant trend interpretation in this execution; comparisons/interpretation reserved for Director-level review)",
        "no_interpretation_note": "acceptance NL3-002 requires the parameter->angle table and the 0b component card; trend statements are explicitly out of scope here",
    }
    out = os.path.join(HERE, "parametric-summary.json")
    with open(out, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(summary))
    ok = all(c["ok"] for c in checks)
    print("cross_checks:", json.dumps(checks))
    print("written", out, "ok=", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
