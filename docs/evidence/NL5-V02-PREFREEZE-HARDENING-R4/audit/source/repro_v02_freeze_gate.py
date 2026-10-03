"""Freeze consistency gate (candidate R3, protocol §12.4) — machine validation.

Protocol N == seed-record cardinalities == budget N == N_min basis.
Any mismatch => FREEZE_GATE_FAIL (mission §11: impossible for a Reviewer or
Verifier to miss — this module is the mechanical check they run).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PRIMARY_N = 64
CONTROL_N = 10
N_MIN_PRIMARY = 51  # >= 80% of 64 (floor)
N_MIN_CONTROL = 8  # >= 80% of 10 (floor)
REPLACEMENT_FRACTION = 0.20
WALL_HOURS_PER_PLATFORM = 560


def derive_budget(primary_variants: int, control_variants: int) -> dict[str, int]:
    primaries = len([v for v in ("0b", "32b")]) if primary_variants is None else primary_variants
    confirmatory = (
        primary_variants * PRIMARY_N * 2 + control_variants * CONTROL_N * 2
    )
    replacements = math_ceil(confirmatory * REPLACEMENT_FRACTION)
    return {
        "confirmatory_runs": confirmatory,
        "replacement_runs": replacements,
        "max_runs": confirmatory + replacements,
        "wall_hours_per_platform": WALL_HOURS_PER_PLATFORM,
    }


def math_ceil(value: float) -> int:
    return int(-(-value // 1))


def parse_protocol_cardinalities(protocol_text: str) -> dict[str, int]:
    match = re.search(
        r"0b = (\d+), 32b = (\d+), 11b = (\d+), 53b = (\d+)", protocol_text
    )
    if not match:
        raise ValueError("protocol cardinality contract line not found")
    keys = ("0b", "32b", "11b", "53b")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def freeze_consistency_gate(
    protocol_text: str,
    seed_record: dict[str, Any],
    primary_variants: int = 2,
    control_variants: int = 2,
) -> dict[str, Any]:
    """Return PASS/FAIL with per-check facts; any mismatch = FREEZE_GATE_FAIL."""
    failures: list[str] = []
    protocol_counts = parse_protocol_cardinalities(protocol_text)
    record_counts = {k: int(v) for k, v in seed_record["variant_counts"].items()}

    budget = derive_budget(primary_variants, control_variants)

    for variant in ("0b", "32b"):
        if protocol_counts.get(variant) != PRIMARY_N:
            failures.append(f"protocol {variant} N != PRIMARY_N ({protocol_counts.get(variant)} != {PRIMARY_N})")
        if record_counts.get(variant) != PRIMARY_N:
            failures.append(f"seed record {variant} N != PRIMARY_N ({record_counts.get(variant)} != {PRIMARY_N})")
    for variant in ("11b", "53b"):
        if protocol_counts.get(variant) != CONTROL_N:
            failures.append(f"protocol {variant} N != CONTROL_N ({protocol_counts.get(variant)} != {CONTROL_N})")
        if record_counts.get(variant) != CONTROL_N:
            failures.append(f"seed record {variant} N != CONTROL_N ({record_counts.get(variant)} != {CONTROL_N})")

    if seed_record.get("primary_replicas") != PRIMARY_N:
        failures.append("seed record primary_replicas field != PRIMARY_N")
    if seed_record.get("control_replicas") != CONTROL_N:
        failures.append("seed record control_replicas field != CONTROL_N")
    if seed_record.get("fresh_seed_total") != 148:  # 64+64+10+10 (grid-selected N=64)
        failures.append("seed record fresh_seed_total != 148")
    if len(seed_record.get("seeds", {}).get("0b", [])) != PRIMARY_N:
        failures.append("seed record 0b stream length != PRIMARY_N")
    if len(seed_record.get("seeds", {}).get("32b", [])) != PRIMARY_N:
        failures.append("seed record 32b stream length != PRIMARY_N")
    if budget["confirmatory_runs"] != 296:
        failures.append("budget confirmatory != 296 for 2 primary + 2 control variants")
    if budget["max_runs"] != 356:
        failures.append("budget max_runs != 356")
    if N_MIN_PRIMARY != int(0.8 * PRIMARY_N):
        failures.append("N_min primary is not the 80% basis of PRIMARY_N")

    return {
        "kind": "r3_freeze_consistency_gate",
        "gate": "PASS" if not failures else "FREEZE_GATE_FAIL",
        "failures": failures,
        "protocol_counts": protocol_counts,
        "record_counts": record_counts,
        "budget": budget,
    }
