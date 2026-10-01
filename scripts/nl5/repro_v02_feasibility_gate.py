"""Mandatory pre-dispatch feasibility gate for NANOLAB_REPRO_V0_2 (protocol §12).

Implements the pinned §12 procedure on committed R1 platform-study paired data:
- per-seed medians per primary variant from paired_platform_sensitivity.json;
- s = pooled within-platform SD(n-1); s_eff = max(s, 0.01);
- expected CI90 half-width of median(d) at n=40 via the pinned paired
  percentile bootstrap (B=10_000, RNG python random.Random(bootstrap_seed_v),
  quantile 'linear'), subsampling n=40 pairs from the committed n=10;
- ratio = half-width / (delta * s_eff); gate PASS iff ratio <= 1.0.

Two estimates are produced (review R-2): the R2-pinned subsample estimate
(decision input) and an advisory sqrt(n) extrapolation from the full n=10
bootstrap (granularity diagnostics). The DECISION follows the pinned subsample
ratio per protocol R2; both numbers are published so the owner sees the
uncertainty before HG-B. No tuning: delta and the rule are read from the
protocol constants below.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

DELTA = 0.5
S_FLOOR = 0.01
B = 10_000
GATE_N = 40
CONF = 0.90


def pooled_sd(xs: list[float], ys: list[float]) -> float:
    n1, n2 = len(xs), len(ys)
    if n1 < 2 or n2 < 2:
        raise ValueError("need >= 2 samples per platform")
    m1 = sum(xs) / n1
    m2 = sum(ys) / n2
    v1 = sum((x - m1) ** 2 for x in xs) / (n1 - 1)
    v2 = sum((y - m2) ** 2 for y in ys) / (n2 - 1)
    return math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))


def quantile_linear(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("empty sample")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = q * (len(sorted_values) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return sorted_values[int(position)]
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (position - low)


def paired_bootstrap_half_width(
    diffs: list[float],
    bootstrap_seed: int,
    subsample_n: int,
    blocks: int = B,
) -> float:
    """CI90 half-width of median(d) under the pinned paired bootstrap.

    ``subsample_n`` is the simulated cell size: each block draws that many
    values WITH replacement from the committed support (draws may exceed the
    source size — that is the point of extrapolating to n=40 from n=10).
    """
    rng = random.Random(bootstrap_seed)
    n = len(diffs)
    half = (1.0 - CONF) / 2.0
    medians: list[float] = []
    for _ in range(blocks):
        sample = (diffs[rng.randrange(n)] for _ in range(subsample_n))
        medians.append(quantile_linear(sorted(sample), 0.5))
    medians.sort()
    low = quantile_linear(medians, half)
    high = quantile_linear(medians, 1.0 - half)
    return (high - low) / 2.0


def load_paired_medians(path: Path) -> dict[str, dict[str, list[float]]]:
    """Extract per-seed medians per variant per platform from committed JSON.

    Observed committed shape (paired_platform_sensitivity.json):
    {"variants": {"0b": {"per_seed": [{"p1_median_deg":..., "p2_median_deg":...,
    "seed":...}, ...], ...}, "32b": {...}}}
    """
    document = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, dict[str, list[float]]] = {}
    variants = document.get("variants", {}) if isinstance(document, dict) else {}
    for variant, payload in variants.items():
        per_seed = payload.get("per_seed", []) if isinstance(payload, dict) else []
        medians_a: list[float] = []
        medians_b: list[float] = []
        for record in sorted(per_seed, key=lambda item: item.get("seed", 0)):
            medians_a.append(float(record["p1_median_deg"]))
            medians_b.append(float(record["p2_median_deg"]))
        result[variant] = {"P1": medians_a, "P2": medians_b}
    return result


def evaluate_variant(
    medians_a: list[float],
    medians_b: list[float],
    bootstrap_seed: int,
) -> dict[str, Any]:
    if len(medians_a) != len(medians_b):
        raise ValueError("paired design requires equal platform sample sizes")
    diffs = [b - a for a, b in zip(medians_a, medians_b)]
    s = pooled_sd(medians_a, medians_b)
    s_eff = max(s, S_FLOOR)
    margin = DELTA * s_eff
    half_subsample = paired_bootstrap_half_width(diffs, bootstrap_seed, GATE_N)
    half_full10 = paired_bootstrap_half_width(diffs, bootstrap_seed, len(diffs), blocks=2000)
    half_sqrt_extrapolated = half_full10 * math.sqrt(len(diffs) / GATE_N)
    return {
        "n_source_pairs": len(diffs),
        "s": s,
        "s_eff": s_eff,
        "margin": margin,
        "half_width_n40_subsample": half_subsample,
        "ratio_subsample": half_subsample / margin,
        "half_width_n10_full": half_full10,
        "half_width_n40_sqrt_extrapolated": half_sqrt_extrapolated,
        "ratio_sqrt_extrapolated": half_sqrt_extrapolated / margin,
        "gate_pass": half_subsample / margin <= 1.0,
    }


def evaluate(
    paired_json: Path,
    bootstrap_seeds: dict[str, int],
    variants: list[str] | None = None,
) -> dict[str, Any]:
    data = load_paired_medians(paired_json)
    platforms = sorted(next(iter(data.values())).keys())
    if len(platforms) != 2:
        raise ValueError(f"expected exactly 2 platforms, found {platforms}")
    variants = variants or sorted(data.keys())
    results = {
        variant: evaluate_variant(
            data[variant][platforms[0]],
            data[variant][platforms[1]],
            bootstrap_seeds[variant],
        )
        for variant in variants
    }
    return {
        "kind": "r2_feasibility_gate_evidence",
        "protocol": "NANOLAB_REPRO_V0_2_DISTRIBUTIONAL candidate R2 §12",
        "delta": DELTA,
        "s_floor": S_FLOOR,
        "bootstrap": {"scheme": "paired-subsample", "B": B, "n": GATE_N, "quantile": "linear"},
        "source": str(paired_json),
        "source_sha256": hashlib.sha256(paired_json.read_bytes()).hexdigest(),
        "platforms": platforms,
        "variants": results,
        "gate_pass_all": all(item["gate_pass"] for item in results.values()),
    }


# --- Candidate R3: declared N-grid search (protocol §12, fixed pre-data) ----
N_GRID = (40, 48, 64, 80, 96, 128)
HEADROOM_RATIO = 0.80  # design margin: ratio_decision <= 0.80 required (not 1.0)


def run_n_grid(
    paired_json: Path,
    bootstrap_seeds: dict[str, int],
    variants: list[str],
    n_grid: tuple[int, ...] = N_GRID,
    headroom: float = HEADROOM_RATIO,
    blocks: int = 2000,
) -> dict[str, Any]:
    """Mechanically evaluate every declared N; select minimal passing N.

    Selection rule (fixed in candidate R3 BEFORE this function was ever run):
    the minimal grid N for which BOTH primary variants have ratio_decision
    (pinned paired bootstrap half-width / (delta * s_eff)) <= headroom (0.80).
    Full grid output is preserved — inconvenient rows are never discarded.
    """
    data = load_paired_medians(paired_json)
    platforms = sorted(next(iter(data.values())).keys())
    grid_rows: list[dict[str, Any]] = []
    for n in n_grid:
        row: dict[str, Any] = {"n": n, "variants": {}}
        passing = True
        for variant in variants:
            medians_a = data[variant][platforms[0]]
            medians_b = data[variant][platforms[1]]
            diffs = [b - a for a, b in zip(medians_a, medians_b)]
            s = pooled_sd(medians_a, medians_b)
            s_eff = max(s, S_FLOOR)
            margin = DELTA * s_eff
            half = paired_bootstrap_half_width(
                diffs, bootstrap_seeds[variant], n, blocks=blocks
            )
            ratio = half / margin
            row["variants"][variant] = {
                "half_width": half,
                "margin": margin,
                "ratio_decision": ratio,
                "passes_headroom": ratio <= headroom,
            }
            passing = passing and ratio <= headroom
        row["passes_headroom_all_variants"] = passing
        grid_rows.append(row)
    selected = next((row["n"] for row in grid_rows if row["passes_headroom_all_variants"]), None)
    return {
        "kind": "r3_feasibility_n_grid",
        "n_grid": list(n_grid),
        "headroom_ratio": headroom,
        "selection_rule": "minimal grid N with ratio_decision <= 0.80 for BOTH primaries",
        "source": str(paired_json),
        "source_sha256": hashlib.sha256(paired_json.read_bytes()).hexdigest(),
        "grid": grid_rows,
        "selected_n": selected,
        "design_infeasible_at_grid": selected is None,
    }
