#!/usr/bin/env python3
"""NanoLab component package - frozen convention analyzer (v0.1).

Reference implementation CLI for the published observable convention:
  [0,180] deg, PCA axes, erratum R1 section 2.5; detector v2 mutual-nearest;
  frozen arm manifest; frame-validity gates; window t <= 150000;
  per-replica median over valid in-window frames; campaign statistic =
  median of three replica medians; classification by
  NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE against the card's published envelope.

Subcommands
  frame0    compute the hinge angle of the FIRST configuration of an oxDNA
            configuration file (upstream .conf or a trajectory). Oracle: the
            value MUST equal the card field design.angle_frame0_deg.
  run       analyse one replica directory/trajectory: frame-validity gates,
            angle series in the comparison window, per-replica median and
            descriptive bootstrap (never a tolerance).
  campaign  combine three per-replica medians into the campaign statistic and
            classify the card with the frozen envelope rule.

Stdlib only. Deterministic. License: Apache-2.0.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nlbl_convention.canonical import canonical_json  # noqa: E402
from nlbl_convention.observables import (  # noqa: E402
    bonded_integrity,
    displacement_max,
    hinge_angle,
    iter_frames,
    pairs_fraction_v2,
    reference_pairs_v2,
)
from nlbl_convention.oxdna_topology import Topology  # noqa: E402
from nlbl_convention.reproduction_rule import classify  # noqa: E402

WINDOW_STEPS = 150000
GATE_LBF_MAX = 0.1078
GATE_PF2_MIN = 0.50
GATE_DISP_MAX = 20.0
BOOT_N = 10000
BOOT_SEED = 424242


def parse_energy(text: str) -> dict:
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 8 and parts[0].isdigit():
            rows.append([float(p) for p in parts])
    if not rows:
        return {"rows": 0}
    first, last = rows[0], rows[-1]
    return {
        "rows": len(rows),
        "first_step": first[0],
        "last_step": last[0],
        "potential_energy_first": first[2],
        "potential_energy_last": last[2],
        "drift": (last[2] - first[2]) / abs(first[2]) if first[2] else None,
    }


def quantile_sorted(sorted_vals: list, q: float) -> float:
    pos = (len(sorted_vals) - 1) * q
    lo = int(pos)
    frac = pos - lo
    if lo + 1 < len(sorted_vals):
        return sorted_vals[lo] * (1 - frac) + sorted_vals[lo + 1] * frac
    return sorted_vals[lo]


def angle_stats(angles: list) -> dict:
    if not angles:
        return {"n": 0, "median_deg": None}
    s = sorted(angles)
    med = statistics.median(s)
    rng = random.Random(BOOT_SEED)
    boots = []
    for _ in range(BOOT_N):
        boots.append(statistics.median(rng.choice(s) for _ in range(len(s))))
    boots.sort()
    return {
        "n": len(s),
        "median_deg": med,
        "iqr_deg": [quantile_sorted(s, 0.25), quantile_sorted(s, 0.75)],
        "q05_q95_deg": [quantile_sorted(s, 0.05), quantile_sorted(s, 0.95)],
        "bootstrap": {"resamples": BOOT_N, "seed": BOOT_SEED, "statistic": "median",
                      "ci95_descriptive_only": [boots[int(0.025 * BOOT_N)], boots[int(0.975 * BOOT_N) - 1]]},
    }


def load_arms(manifest_path: str) -> dict:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))["arms"]


def cmd_frame0(args: argparse.Namespace) -> int:
    topology = Topology.from_file(args.topology)
    topology.check_chain_integrity()
    with open(args.conf, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    first = next(iter_frames(text))
    first.check_orientation()
    angle = hinge_angle(first, load_arms(args.manifest))
    ref_pairs = reference_pairs_v2(first, topology)
    out = {
        "kind": "nanolab_convention_frame0_check",
        "conf": args.conf,
        "manifest": args.manifest,
        "angle_deg": angle["angle_deg"],
        "angle_status": angle["status"],
        "reference_pairs_v2_count": len(ref_pairs),
        "oracle": "MUST equal card field design.angle_frame0_deg",
    }
    print(canonical_json(out))
    return 0 if angle["status"] == "OK" else 1


def cmd_run(args: argparse.Namespace) -> int:
    topology = Topology.from_file(args.topology)
    topology.check_chain_integrity()
    with open(args.trajectory, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    with open(args.energy, "r", encoding="utf-8", newline="") as handle:
        energy = parse_energy(handle.read())
    manifest = load_arms(args.manifest)
    frames = list(iter_frames(text))
    ref = frames[0]
    ref.check_orientation()
    ref_pairs = reference_pairs_v2(ref, topology)
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
            "frame": pos, "time": float(conf.time),
            "angle_deg": angle["angle_deg"] if angle["status"] == "OK" else None,
            "angle_status": angle["status"],
            "pairs_fraction_v2": pairs["pairs_fraction"],
            "long_bond_fraction": bonds["long_bond_fraction"],
            "displacement_max": disp["displacement_max"],
            "valid": not reasons,
            "invalid_reasons": reasons,
        })
    in_window = [f for f in frame_rows if f["time"] <= args.window]
    valid_in_window = [f for f in in_window if f["valid"]]
    valid_angles = [f["angle_deg"] for f in valid_in_window if f["angle_deg"] is not None]
    stats = angle_stats(valid_angles)
    engine_exit_code = None
    if args.exit_code_file and Path(args.exit_code_file).is_file():
        text_exit = Path(args.exit_code_file).read_text(encoding="utf-8").strip()
        engine_exit_code = int(text_exit.split(":", 1)[1]) if ":" in text_exit else None
    out = {
        "schema_version": 1,
        "kind": "nanolab_convention_replica_analysis",
        "rule_id": "NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE",
        "run_id": args.run_id,
        "variant": args.variant,
        "seed": args.seed,
        "detector": "v2 mutual-nearest (frozen, packaged convention)",
        "angle_convention": "[0,180] deg, PCA axes, erratum R1 section 2.5",
        "window_steps": args.window,
        "gates": {"long_bond_fraction_max": GATE_LBF_MAX,
                  "pairs_fraction_v2_min": GATE_PF2_MIN,
                  "displacement_max_max": GATE_DISP_MAX},
        "engine_exit_code": engine_exit_code,
        "energy": energy,
        "frames_total": len(frame_rows),
        "frames_in_window": len(in_window),
        "frames_valid_in_window": len(valid_in_window),
        "valid_frame_fraction_in_window": (len(valid_in_window) / len(in_window)) if in_window else None,
        "angle_stats_valid_in_window": stats,
        "replica_median_deg": stats["median_deg"],
        "frames": frame_rows,
    }
    rendered = canonical_json(out)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8", newline="\n")
    print(rendered)
    return 0


def cmd_campaign(args: argparse.Namespace) -> int:
    card = json.loads(Path(args.card).read_text(encoding="utf-8"))
    expected = card["reproduction"]["expected"]
    medians = []
    technical_ok = True
    if args.run_jsons:
        for path in args.run_jsons:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            medians.append(data["replica_median_deg"])
            if data.get("engine_exit_code") is not None and data["engine_exit_code"] != 0:
                technical_ok = False
    else:
        medians = [float(x) for x in args.medians.split(",")]
    if len(medians) != expected.get("required_fresh_replicas", 3):
        print(canonical_json({
            "kind": "nanolab_convention_campaign_classification",
            "rule_id": "NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE",
            "error": f"expected {expected.get('required_fresh_replicas', 3)} replicas, got {len(medians)}",
        }))
        return 2
    verdict = classify(
        expected["reference_replica_medians_deg"],
        medians,
        technical_ok=technical_ok,
        integrity_analysis_complete=True,
    )
    out = {
        "schema_version": 1,
        "kind": "nanolab_convention_campaign_classification",
        "rule_id": "NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE",
        "variant": args.variant,
        "card_reference": expected,
        "fresh_replica_medians_deg": medians,
        "campaign_statistic_deg": statistics.median(medians) if all(
            m is not None for m in medians) else None,
        "classification": verdict.as_dict(),
        "note": "bootstrap CI is descriptive only and never a tolerance",
    }
    print(canonical_json(out))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_f0 = sub.add_parser("frame0", help="oracle check: hinge angle of the first configuration")
    p_f0.add_argument("--conf", required=True)
    p_f0.add_argument("--topology", required=True)
    p_f0.add_argument("--manifest", required=True)
    p_f0.set_defaults(func=cmd_frame0)

    p_run = sub.add_parser("run", help="analyse one replica: gates + angle series + median")
    p_run.add_argument("--trajectory", required=True)
    p_run.add_argument("--energy", required=True)
    p_run.add_argument("--topology", required=True)
    p_run.add_argument("--manifest", required=True)
    p_run.add_argument("--variant", required=True)
    p_run.add_argument("--run-id", default="run")
    p_run.add_argument("--seed", type=int, default=None)
    p_run.add_argument("--window", type=int, default=WINDOW_STEPS)
    p_run.add_argument("--exit-code-file", default=None)
    p_run.add_argument("--report", default=None, help="also write canonical JSON here")
    p_run.set_defaults(func=cmd_run)

    p_cmp = sub.add_parser("campaign", help="classify a card from three replica medians")
    p_cmp.add_argument("--card", required=True)
    p_cmp.add_argument("--variant", required=True)
    group = p_cmp.add_mutually_exclusive_group(required=True)
    group.add_argument("--medians", help="comma-separated three replica medians (deg)")
    group.add_argument("--run-jsons", nargs=3, help="three replica analysis JSON files")
    p_cmp.set_defaults(func=cmd_campaign)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
