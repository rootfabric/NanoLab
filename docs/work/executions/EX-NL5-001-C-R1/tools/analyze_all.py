#!/usr/bin/env python3
"""EX-NL5-001-C-R1 analysis + classification (frozen protocol).

Per replica: observables v2 (mutual-nearest, frozen) + integrity gates
(E2_PROTO_R1 section 4) + hinge angle with the pre-run frozen arm manifest;
frames resliced to the common comparison window t <= WINDOW_STEPS; per-replica
median over valid in-window frames. Per variant: classification with the
frozen NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE rule using the card's published
reference replica medians/envelope. Bootstrap CI (10000, seed 424242) is
computed descriptively and is never a tolerance.
"""
from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]  # tools -> EX dir -> executions -> work -> docs -> repo root
RUN_ROOT = None  # resolved in main() from argv[1]
sys.path.insert(0, str(REPO / "scripts"))

from e2.canonical import canonical_json  # noqa: E402
from e2.observables import (  # noqa: E402
    bonded_integrity,
    displacement_max,
    hinge_angle,
    iter_frames,
    pairs_fraction_v2,
    reference_pairs_v2,
)
from hinge_family.oxdna_topology import Topology  # noqa: E402
from release.reproduction_rule import classify  # noqa: E402

GATE_LBF_MAX = 0.1078
GATE_PF2_MIN = 0.50
GATE_DISP_MAX = 20.0
WINDOW_STEPS = 150000
BOOT_N = 10000
BOOT_SEED = 424242

VARIANTS = {
    "0b": {"replicas": ["NL5-001-C-0B-S001", "NL5-001-C-0B-S002", "NL5-001-C-0B-S003"],
           "manifest": "docs/work/executions/EX-NL3-002-PROTO-R1/evidence/arm-manifest-0b.json",
           "card": "releases/nanolab-components-v0.1/families/dna_hinge/cards/0b.card.json"},
    "11b": {"replicas": ["NL5-001-C-11B-S001", "NL5-001-C-11B-S002", "NL5-001-C-11B-S003"],
            "manifest": "docs/work/executions/EX-NL3-002-PARAM-11B-R1/evidence/arm-manifest-11b.json",
            "card": "releases/nanolab-components-v0.1/families/dna_hinge/cards/11b.card.json"},
    "32b": {"replicas": ["NL5-001-C-32B-S001", "NL5-001-C-32B-S002", "NL5-001-C-32B-S003"],
            "manifest": "docs/work/executions/EX-NL3-002-PARAM-32B-R1/evidence/arm-manifest-32b.json",
            "card": "releases/nanolab-components-v0.1/families/dna_hinge/cards/32b.card.json"},
    "53b": {"replicas": ["NL5-001-C-53B-S001", "NL5-001-C-53B-S002", "NL5-001-C-53B-S003"],
            "manifest": "docs/work/executions/EX-NL3-002-PARAM-53B-R1/evidence/arm-manifest-53b.json",
            "card": "releases/nanolab-components-v0.1/families/dna_hinge/cards/53b.card.json"},
}


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


def analyse_run(run: dict, manifest: dict, topology_text: str, run_report: dict) -> dict:
    rid, prefix = run["run_id"], run["prefix"]
    run_dir = RUN_ROOT / rid
    topology = Topology.parse(topology_text)
    topology.check_chain_integrity()
    energy = parse_energy((run_dir / f"{prefix}_energy.dat").read_text(encoding="utf-8"))
    frames = list(iter_frames((run_dir / f"{prefix}_traj.dat").read_text(encoding="utf-8")))
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
    in_window = [f for f in frame_rows if f["time"] <= WINDOW_STEPS]
    valid_in_window = [f for f in in_window if f["valid"]]
    valid_angles = [f["angle_deg"] for f in valid_in_window if f["angle_deg"] is not None]
    exit_code = None
    exit_file = run_dir / "exit_code.txt"
    if exit_file.is_file():
        text = exit_file.read_text(encoding="utf-8").strip()
        exit_code = int(text.split(":", 1)[1]) if ":" in text else None
    return {
        "schema_version": 1,
        "kind": "nl5_001_c_replica_analysis",
        "execution_id": "EX-NL5-001-C-R1",
        "run_id": rid, "variant": run["variant"], "seed": run["seed"],
        "detector": "v2 mutual-nearest (frozen, E2_OBSERVABLES_R2 + E2_PROTO_R1 section 2)",
        "angle_convention": "[0,180] deg, PCA axes, erratum R1 section 2.5",
        "window_steps": WINDOW_STEPS,
        "gates": {"long_bond_fraction_max": GATE_LBF_MAX,
                  "pairs_fraction_v2_min": GATE_PF2_MIN,
                  "displacement_max_max": GATE_DISP_MAX},
        "engine_exit_code": exit_code,
        "budget_abort": (run_report or {}).get("budget_abort"),
        "energy": energy,
        "frames_total": len(frame_rows),
        "frames_in_window": len(in_window),
        "frames_valid_in_window": len(valid_in_window),
        "valid_frame_fraction_in_window": (len(valid_in_window) / len(in_window)) if in_window else None,
        "angle_stats_valid_in_window": angle_stats(valid_angles),
        "replica_median_deg": angle_stats(valid_angles)["median_deg"],
        "frames": frame_rows,
    }


def main() -> int:
    global RUN_ROOT
    RUN_ROOT = Path(sys.argv[1]).resolve()
    run_reports = json.loads((RUN_ROOT / "run-reports.json").read_text(encoding="utf-8")) \
        if (RUN_ROOT / "run-reports.json").is_file() else {}
    out_dir = REPO / "docs/work/executions/EX-NL5-001-C-R1/evidence"
    out_dir.mkdir(parents=True, exist_ok=True)
    campaign = {"kind": "nl5_001_c_campaign_classification", "execution_id": "EX-NL5-001-C-R1",
                "rule_id": "NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE", "window_steps": WINDOW_STEPS,
                "variants": {}}
    for variant, spec in VARIANTS.items():
        manifest = json.loads((REPO / spec["manifest"]).read_text(encoding="utf-8"))["arms"]
        card = json.loads((REPO / spec["card"]).read_text(encoding="utf-8"))
        expected = card["reproduction"]["expected"]
        card_top_text = None
        replica_medians = []
        per_replica = {}
        for rid in spec["replicas"]:
            run = {"run_id": rid, "variant": variant, "prefix": rid.split("-")[-1].lower(),
                   "seed": json.loads((RUN_ROOT / rid / "input-build.json").read_text(encoding="utf-8"))["seed"]}
            topology_text = (RUN_ROOT / rid / f"{variant}.top").read_text(encoding="utf-8")
            report = analyse_run(run, manifest, topology_text, run_reports.get(rid))
            (out_dir / f"{rid}-analysis.json").write_text(canonical_json(report) + "\n", encoding="utf-8")
            per_replica[rid] = {k: report[k] for k in (
                "seed", "engine_exit_code", "budget_abort", "frames_total", "frames_in_window",
                "frames_valid_in_window", "replica_median_deg")}
            replica_medians.append(report["replica_median_deg"])
        technical_ok = all(
            per_replica[rid]["engine_exit_code"] == 0 and not per_replica[rid]["budget_abort"]
            for rid in spec["replicas"])
        integrity_ok = all(per_replica[rid]["frames_valid_in_window"] is not None for rid in spec["replicas"])
        verdict = classify(
            expected["reference_replica_medians_deg"],
            replica_medians,
            technical_ok=technical_ok,
            integrity_analysis_complete=integrity_ok,
        )
        record = {
            "variant": variant,
            "card_reference": expected,
            "replicas": per_replica,
            "fresh_replica_medians_deg": replica_medians,
            "campaign_statistic_deg": statistics.median(replica_medians) if all(
                m is not None for m in replica_medians) else None,
            "classification": verdict.as_dict(),
        }
        (out_dir / f"classification-{variant}.json").write_text(canonical_json(record) + "\n", encoding="utf-8")
        campaign["variants"][variant] = {
            "outcome": verdict.outcome,
            "campaign_statistic_deg": record["campaign_statistic_deg"],
            "reference_envelope_deg": expected["reference_replica_envelope_deg"],
            "fresh_replica_medians_deg": replica_medians,
        }
        print(f"{variant}: {verdict.outcome} campaign={record['campaign_statistic_deg']} "
              f"envelope={expected['reference_replica_envelope_deg']} replicas={replica_medians}")
    (out_dir / "campaign-summary.json").write_text(canonical_json(campaign) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
