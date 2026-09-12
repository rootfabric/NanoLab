"""Non-confirmatory pilot analysis for EX-NL3-002-PILOT-R1 (sampling, NOT science).

Per replica: (a) energy trace summary from the oxDNA energy file (header line
per sample: time then energy columns; here: time, U, K, total); (b) integrity
v1 on a subsample of <= 15 trajectory frames: bonded long-bond fraction,
displacement_max vs frame 0, pairs_fraction via the equivalence-tested
bucketed reference-pairs algorithm (frozen definition, docs/research/
E2_OBSERVABLES_R1.md); (c) DRAFT-proxy PCA angle between scaffold halves
arm_a = [0, 2132], arm_b = [2133, 4265] — DRAFT proxy, non-confirmatory,
NOT the E2-PROTO manifest.

All outputs are canonical JSON (e2.canonical_json). scientific_outcome is
NOT_EVALUATED: no scientific claims are published from this pilot.
"""
import argparse
import json
import os
import subprocess
import sys

REPO = r"C:\NanoLab\nl3-002-pilot"
sys.path.insert(0, os.path.join(REPO, "scripts"))

from e2.canonical import canonical_json
from e2.observables import (
    bonded_integrity,
    displacement_max,
    hinge_angle,
    iter_frames,
    pairs_fraction,
    reference_pairs_bucketed,
)
from hinge_family.oxdna_topology import Topology

DRAFT_MANIFEST = {
    "arm_a": {"nucleotides": list(range(0, 2133))},
    "arm_b": {"nucleotides": list(range(2133, 4266))},
}
MAX_FRAMES = 15
ENERGY_SAMPLES = 15


def wsl_read(path):
    out = subprocess.run(["wsl", "-e", "bash", "-c", f"cat '{path}'"],
                         capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        raise RuntimeError(f"cannot read {path}: {out.stderr}")
    return out.stdout


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
    times = [r[0] for r in rows]
    totals = [r[3] for r in rows]
    step = max(1, len(rows) // ENERGY_SAMPLES)
    sample_rows = rows[::step]
    if sample_rows[-1] != rows[-1]:
        sample_rows.append(rows[-1])
    return {
        "columns": ["time", "potential", "kinetic", "total"],
        "rows_total": len(rows),
        "time_first": times[0],
        "time_last": times[-1],
        "total_energy_first": totals[0],
        "total_energy_last": totals[-1],
        "total_energy_min": min(totals),
        "total_energy_max": max(totals),
        "max_abs_drift_total": max(abs(t - totals[0]) for t in totals),
        "samples": [[r[0], r[1], r[2], r[3]] for r in sample_rows],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="run id, e.g. E2-PILOT-S001")
    parser.add_argument("--prefix", required=True, help="output file prefix, e.g. s001")
    parser.add_argument("--wsl-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--steps", type=int, required=True)
    parser.add_argument("--wall-s", type=float, required=True)
    parser.add_argument("--exit-code", type=int, required=True)
    args = parser.parse_args()

    # read topology via WSL cat to avoid UNC issues
    topology = Topology.parse(wsl_read(f"{args.wsl_dir}/0b.top"))
    topology.check_chain_integrity()

    energy = parse_energy(wsl_read(f"{args.wsl_dir}/{args.prefix}_energy.dat"))
    traj_text = wsl_read(f"{args.wsl_dir}/{args.prefix}_traj.dat")

    frames = list(iter_frames(traj_text))
    total = len(frames)
    if total > MAX_FRAMES:
        positions = [round(i * (total - 1) / (MAX_FRAMES - 1)) for i in range(MAX_FRAMES)]
    else:
        positions = list(range(total))
    chosen = [frames[p] for p in positions]

    ref = chosen[0]
    ref_pairs = reference_pairs_bucketed(ref, topology)
    frame_rows = []
    for pos, conf in zip(positions, chosen):
        angle = hinge_angle(conf, DRAFT_MANIFEST)
        bonds = bonded_integrity(conf, topology)
        disp = displacement_max(ref, conf)
        pairs = pairs_fraction(conf, ref_pairs)
        frame_rows.append({
            "frame_index": pos,
            "time": conf.time,
            "long_bond_fraction": bonds["long_bond_fraction"],
            "displacement_max": disp["displacement_max"],
            "pairs_fraction": pairs["pairs_fraction"],
            "draft_angle_deg": angle["angle_deg"] if angle["status"] == "OK" else None,
            "draft_angle_status": angle["status"],
        })

    report = {
        "schema_version": 1,
        "kind": "e2_pilot_replica_analysis",
        "run_id": args.run,
        "class": "non-confirmatory pilot calibration; scientific_outcome = NOT_EVALUATED",
        "draft_angle_note": "DRAFT proxy, non-confirmatory, not the E2-PROTO manifest",
        "steps": args.steps,
        "exit_code": args.exit_code,
        "wall_time_s": args.wall_s,
        "per_step_cost_s": args.wall_s / args.steps,
        "energy": energy,
        "reference_pairs_count": len(ref_pairs),
        "frames_total": total,
        "frames_analysed": len(frame_rows),
        "max_long_bond_fraction": max(f["long_bond_fraction"] for f in frame_rows),
        "max_displacement": max(f["displacement_max"] for f in frame_rows),
        "min_pairs_fraction": min((f["pairs_fraction"] for f in frame_rows if f["pairs_fraction"] is not None), default=None),
        "draft_angle_first_deg": frame_rows[0]["draft_angle_deg"],
        "draft_angle_last_deg": frame_rows[-1]["draft_angle_deg"],
        "frames": frame_rows,
    }
    out = os.path.join(args.out_dir, f"{args.prefix}-analysis.json")
    with open(out, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(report))
    print(json.dumps({"run": args.run, "out": out,
                      "drift": report["energy"]["max_abs_drift_total"],
                      "max_lbf": report["max_long_bond_fraction"],
                      "min_pf": report["min_pairs_fraction"],
                      "angle_first": report["draft_angle_first_deg"],
                      "angle_last": report["draft_angle_last_deg"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
