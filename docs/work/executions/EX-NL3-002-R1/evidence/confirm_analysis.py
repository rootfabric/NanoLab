"""Confirmatory analysis for EX-NL3-002-R1 (E2_PROTO_R1, frozen).

Per replica: observables v2 (mutual) + integrity v1 + hinge angle with the
FROZEN arm manifest arm-manifest-0b.json; frame validity gates per protocol
section 4; per-replica and pooled angle statistics over VALID frames
(median/IQR/q5/q95 + bootstrap CI, 10000 resamples, seed 424242); energy
drift; valid-frame fraction. All frames reported. scientific_outcome =
MEASURED; no interpretation.
"""
import argparse
import json
import math
import os
import random
import subprocess
import sys

REPO = r"C:\NanoLab\nl3-002-confirm"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(EX, "evidence"))
from e2.canonical import canonical_json  # noqa: E402
from e2.observables import (  # noqa: E402
    bonded_integrity,
    displacement_max,
    hinge_angle,
    iter_frames,
    load_manifest,
    pairs_fraction_v2,
    reference_pairs_v2,
)
from hinge_family.oxdna_topology import Topology  # noqa: E402

WSL_ROOT = "/home/yurig/nl3-002-confirm/runs"
RUNS = [
    {"run_id": "E2-R1-C001", "prefix": "c001", "seed": 201004},
    {"run_id": "E2-R1-C002", "prefix": "c002", "seed": 202008},
    {"run_id": "E2-R1-C003", "prefix": "c003", "seed": 203012},
]
FROZEN_MANIFEST = os.path.join(
    REPO, "docs", "work", "executions", "EX-NL3-002-PROTO-R1", "evidence", "arm-manifest-0b.json")
# E2_PROTO_R1 section 4 gates
GATE_LBF_MAX = 0.1078
GATE_PF2_MIN = 0.50
GATE_DISP_MAX = 20.0
BOOT_N = 10000
BOOT_SEED = 424242


def wsl_read(path, binary=False):
    # copy to Windows temp then read locally (trajectories are ~50 MB)
    tmp = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "nl3-002-confirm-read")
    os.makedirs(tmp, exist_ok=True)
    local = os.path.join(tmp, path.replace("/", "__"))
    src = path.replace("/home/yurig", r"\\wsl.localhost\Ubuntu\home\yurig")
    import shutil
    shutil.copyfile(src, local)
    if binary:
        with open(local, "rb") as h:
            return h.read()
    with open(local, "r", encoding="utf-8", newline="") as h:
        return h.read()


def parse_energy(text):
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            try:
                rows.append([float(x) for x in parts])
            except ValueError:
                continue
    if not rows:
        raise ValueError("energy file has no numeric rows")
    totals = [r[3] for r in rows]
    return {
        "columns": ["time", "potential", "kinetic", "total"],
        "rows_total": len(rows),
        "time_first": rows[0][0], "time_last": rows[-1][0],
        "total_energy_first": totals[0], "total_energy_last": totals[-1],
        "total_energy_min": min(totals), "total_energy_max": max(totals),
        "max_abs_drift_total": max(abs(t - totals[0]) for t in totals),
    }


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
    # bootstrap CI for the median, deterministic
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


def analyse_run(run, manifest, topology_text):
    rid, prefix = run["run_id"], run["prefix"]
    wsl_dir = f"{WSL_ROOT}/{rid}"
    topology = Topology.parse(topology_text)
    topology.check_chain_integrity()
    energy = parse_energy(wsl_read(f"{wsl_dir}/{prefix}_energy.dat"))
    traj_text = wsl_read(f"{wsl_dir}/{prefix}_traj.dat")
    frames = list(iter_frames(traj_text))
    ref = frames[0]
    ref.check_orientation()
    ref_pairs = reference_pairs_v2(ref, topology)  # mutual-nearest default (frozen)
    frame_rows = []
    for pos, conf in enumerate(frames):
        conf.check_orientation()
        angle = hinge_angle(conf, manifest)
        pairs = pairs_fraction_v2(conf, ref_pairs)
        bonds = bonded_integrity(conf, topology)
        disp = displacement_max(ref, conf)
        reasons = []
        if bonds["long_bond_fraction"] > GATE_LBF_MAX:
            reasons.append("long_bond_fraction")
        if pairs["pairs_fraction"] is None or pairs["pairs_fraction"] < GATE_PF2_MIN:
            reasons.append("pairs_fraction_v2")
        if disp["displacement_max"] > GATE_DISP_MAX:
            reasons.append("displacement_max")
        frame_rows.append({
            "frame": pos, "time": conf.time,
            "angle_deg": angle["angle_deg"] if angle["status"] == "OK" else None,
            "angle_status": angle["status"],
            "pairs_fraction_v2": pairs["pairs_fraction"],
            "long_bond_fraction": bonds["long_bond_fraction"],
            "displacement_max": disp["displacement_max"],
            "valid": not reasons,
            "invalid_reasons": reasons,
        })
    valid = [f for f in frame_rows if f["valid"]]
    valid_angles = [f["angle_deg"] for f in valid if f["angle_deg"] is not None]
    report = {
        "schema_version": 1,
        "kind": "e2_confirm_replica_analysis",
        "execution_id": "EX-NL3-002-R1",
        "protocol": "docs/research/E2_PROTO_R1.md (frozen)",
        "run_id": rid, "seed": run["seed"], "steps_requested": 200000,
        "detector": "v2 mutual-nearest (frozen, E2_OBSERVABLES_R2 + E2_PROTO_R1 §2)",
        "arm_manifest": "docs/work/executions/EX-NL3-002-PROTO-R1/evidence/arm-manifest-0b.json (frozen, arm-manifest-v1)",
        "angle_convention": "[0,180] deg, PCA axes, erratum R1 §2.5",
        "gates": {"long_bond_fraction_max": GATE_LBF_MAX,
                  "pairs_fraction_v2_min": GATE_PF2_MIN,
                  "displacement_max_max": GATE_DISP_MAX},
        "reference_pairs_v2_count": len(ref_pairs),
        "frames_total": len(frame_rows),
        "frames_valid": len(valid),
        "valid_frame_fraction": len(valid) / len(frame_rows) if frame_rows else None,
        "energy": energy,
        "pairs_fraction_v2_first": frame_rows[0]["pairs_fraction_v2"] if frame_rows else None,
        "pairs_fraction_v2_last": frame_rows[-1]["pairs_fraction_v2"] if frame_rows else None,
        "pairs_fraction_v2_min": min((f["pairs_fraction_v2"] for f in frame_rows
                                      if f["pairs_fraction_v2"] is not None), default=None),
        "long_bond_fraction_max": max((f["long_bond_fraction"] for f in frame_rows), default=None),
        "displacement_max_max": max((f["displacement_max"] for f in frame_rows), default=None),
        "angle_stats_valid_frames": angle_stats(valid_angles),
        "scientific_outcome": "MEASURED (distributions; no interpretation; acceptance — Director after review)",
        "frames": frame_rows,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="comma-separated prefixes, e.g. c001")
    args = parser.parse_args()
    manifest = load_manifest(FROZEN_MANIFEST)
    topology_text = wsl_read(f"{WSL_ROOT}/E2-R1-C001/0b.top")
    selected = RUNS if not args.only else [r for r in RUNS if r["prefix"] in args.only.split(",")]
    reports = []
    for run in selected:
        print("analysing", run["run_id"], flush=True)
        rep = analyse_run(run, manifest, topology_text)
        with open(os.path.join(EX, "evidence", f"{run['prefix']}-analysis.json"), "w",
                  encoding="utf-8", newline="\n") as h:
            h.write(canonical_json(rep) + "\n")
        reports.append(rep)
        st = rep["angle_stats_valid_frames"]
        print(f"{run['run_id']}: frames {rep['frames_total']} valid {rep['frames_valid']} "
              f"angle_median {st['median_deg'] if st else None}", flush=True)
    if len(reports) == len(RUNS):
        pool_angles = []
        for rep in reports:
            pool_angles += [f["angle_deg"] for f in rep["frames"]
                            if f["valid"] and f["angle_deg"] is not None]
        summary = {
            "schema_version": 1,
            "kind": "e2_confirm_summary",
            "execution_id": "EX-NL3-002-R1",
            "protocol": "docs/research/E2_PROTO_R1.md (frozen)",
            "scientific_outcome": "MEASURED (measured distributions; no scientific conclusions; acceptance — Director after review)",
            "runs": {r["run_id"]: {
                "seed": r["seed"], "frames_total": r["frames_total"],
                "frames_valid": r["frames_valid"],
                "valid_frame_fraction": r["valid_frame_fraction"],
                "reference_pairs_v2_count": r["reference_pairs_v2_count"],
                "pairs_fraction_v2_first": r["pairs_fraction_v2_first"],
                "pairs_fraction_v2_last": r["pairs_fraction_v2_last"],
                "pairs_fraction_v2_min": r["pairs_fraction_v2_min"],
                "long_bond_fraction_max": r["long_bond_fraction_max"],
                "displacement_max_max": r["displacement_max_max"],
                "energy_max_abs_drift_total": r["energy"]["max_abs_drift_total"],
                "angle_stats_valid_frames": r["angle_stats_valid_frames"],
            } for r in reports},
            "pooled_angle_stats_valid_frames": angle_stats(pool_angles),
            "pooled_valid_frames_total": len(pool_angles),
        }
        with open(os.path.join(EX, "evidence", "confirmatory-summary.json"), "w",
                  encoding="utf-8", newline="\n") as h:
            h.write(canonical_json(summary) + "\n")
        print("pooled angle stats written", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
