"""Freeze consistency gate (candidate R4, protocol §12.4) — machine validation.

Pre-freeze hardening R4 (WO-NL5-V02-PREFREEZE-HARDENING-R4): the R3 gate
returned PASS for corrupted control arrays, duplicate/historical seeds,
stale digests, missing bootstrap seeds and contradicting protocol fields
(audit finding F1). The R4 gate is fail-closed and delegates every integer
quantity (N_min, per-cell replacement quotas, run caps, wall cap) to the
single machine contract policy in ``repro_v02_freeze_contract`` (F4).

Protocol N == seed-record cardinalities == budget N == N_min basis == the
authoritative machine block in the candidate document. Any mismatch =>
FREEZE_GATE_FAIL. The dispatch entrypoint (``build_execution_plan`` in
``repro_v02_freeze_contract``) always runs this gate; bypassing it is
impossible by construction.
"""

from __future__ import annotations

from typing import Any

from nl5.repro_v02_freeze_contract import (
    INTEGER_ROUNDING_POLICY,
    ContractError,
    CONTROL_N,
    PRIMARY_N,
    derive_budget,
    logical_record_digest,
    n_min_cell,
    parse_protocol_cardinalities,
    parse_protocol_machine_block,
    replacement_quota_pairs,
)
from nl5.repro_v02_seeds import (
    BOOTSTRAP_RESAMPLES,
    DEFAULT_VARIANTS,
    HISTORICAL_SEEDS_V1,
)

__all__ = [
    "PRIMARY_N",
    "CONTROL_N",
    "N_MIN_PRIMARY",
    "N_MIN_CONTROL",
    "WALL_HOURS_PER_PLATFORM",
    "INTEGER_ROUNDING_POLICY",
    "derive_budget",
    "parse_protocol_cardinalities",
    "freeze_consistency_gate",
]

# N_min values follow the single F4 integer policy (ceil(0.80*N), literal
# ">= 80%"): 51/64 = 79.6875% does NOT satisfy it, so N_min = 52 / 8.
N_MIN_PRIMARY = n_min_cell(PRIMARY_N)
N_MIN_CONTROL = n_min_cell(CONTROL_N)
WALL_HOURS_PER_PLATFORM = derive_budget()["wall_hours_per_platform"]


def budget_for_variant_counts(variant_counts: dict[str, int] | None = None) -> dict[str, int]:
    """Budget from the single integer policy (F4 single source)."""
    return derive_budget(variant_counts)


def _deep_record_checks(record: dict[str, Any], failures: list[str]) -> None:
    """F1 classes the R3 gate missed (fail-closed, preserved as regressions)."""
    seeds = record.get("seeds")
    if not isinstance(seeds, dict):
        failures.append("seed record: seeds object missing")
        seeds = {}
    variant_counts = record.get("variant_counts")
    if not isinstance(variant_counts, dict):
        failures.append("seed record: variant_counts missing")
        variant_counts = {}
    expected_counts = {"0b": PRIMARY_N, "32b": PRIMARY_N, "11b": CONTROL_N, "53b": CONTROL_N}
    for variant, expected in expected_counts.items():
        stream = seeds.get(variant)
        if not isinstance(stream, list):
            failures.append(f"seed record {variant}: seeds array missing (not a list)")
            continue
        if len(stream) != expected or variant_counts.get(variant) != expected:
            failures.append(
                f"seed record {variant}: {len(stream)} identities / count "
                f"{variant_counts.get(variant)} != expected {expected}"
            )
        if not stream:
            failures.append(f"seed record {variant}: seeds array is empty")
        for position, seed in enumerate(stream):
            if not isinstance(seed, int) or isinstance(seed, bool):
                failures.append(f"seed record {variant}[{position}]: non-integer seed")
            elif not 0 <= seed < 2**31:
                failures.append(f"seed record {variant}[{position}]: seed outside int32-positive range")
        if len(set(stream)) != len(stream):
            failures.append(f"seed record {variant}: duplicate seed inside stream")
    all_seeds = [s for stream in seeds.values() if isinstance(stream, list) for s in stream]
    if len(set(all_seeds)) != len(all_seeds):
        failures.append("seed record: duplicate seeds across variants")
    historical = set(record.get("exclusions_applied") or HISTORICAL_SEEDS_V1)
    hits = sorted({s for s in all_seeds if s in historical})
    if hits:
        failures.append(f"seed record: historical R1 seeds inside fresh streams: {hits}")
    bootstrap = record.get("bootstrap_seeds")
    if not isinstance(bootstrap, dict) or not set(DEFAULT_VARIANTS) <= set(bootstrap):
        failures.append("seed record: bootstrap_seeds missing or incomplete (fail-closed)")
        bootstrap = {}
    for variant in DEFAULT_VARIANTS:
        seed = bootstrap.get(variant)
        if not isinstance(seed, int) or isinstance(seed, bool):
            failures.append(f"seed record bootstrap {variant}: non-integer seed")
            continue
        if seed in historical:
            failures.append(f"seed record bootstrap {variant}: historical R1 seed")
        if seed in all_seeds:
            failures.append(f"seed record bootstrap {variant}: collides with fresh identities")
    fresh_digest = logical_record_digest(
        {v: seeds[v] for v in expected_counts if isinstance(seeds.get(v), list)},
        {
            v: bootstrap[v]
            for v in expected_counts
            if isinstance(bootstrap.get(v), int) and not isinstance(bootstrap.get(v), bool)
        },
        record.get("anchor", ""),
        {v: variant_counts.get(v) for v in expected_counts},
    )
    if fresh_digest != record.get("record_sha256"):
        failures.append("seed record: record_sha256 stale (logical digest mismatch)")


def _protocol_declaration_checks(protocol_text: str, failures: list[str]) -> dict[str, str]:
    try:
        parse_protocol_cardinalities(protocol_text)
    except ContractError as exc:
        failures.append(f"protocol: {exc}")
    try:
        block = parse_protocol_machine_block(protocol_text)
    except ContractError as exc:
        failures.append(f"protocol: {exc}")
        return {}
    budget = derive_budget()
    expected_block_values = {
        "n_0b": str(PRIMARY_N),
        "n_32b": str(PRIMARY_N),
        "n_11b": str(CONTROL_N),
        "n_53b": str(CONTROL_N),
        "n_min_primary": str(N_MIN_PRIMARY),
        "n_min_control": str(N_MIN_CONTROL),
        "replacement_quota_pairs_primary": str(replacement_quota_pairs(PRIMARY_N)),
        "replacement_quota_pairs_control": str(replacement_quota_pairs(CONTROL_N)),
        "confirmatory_runs": str(budget["confirmatory_runs"]),
        "replacement_runs_cap": str(budget["replacement_runs_cap"]),
        "max_runs": str(budget["max_runs"]),
        "wall_hours_per_platform": str(WALL_HOURS_PER_PLATFORM),
        "bootstrap_resamples": str(BOOTSTRAP_RESAMPLES),
        "exclusion_list_size": str(len(HISTORICAL_SEEDS_V1)),
        "integer_policy_name": INTEGER_ROUNDING_POLICY["name"],
    }
    for key, expected in expected_block_values.items():
        actual = block.get(key)
        if actual is not None and actual != expected:
            failures.append(
                f"protocol machine block {key} = {actual!r} != policy {expected!r} "
                "(contradicting declaration)"
            )
    return block


def freeze_consistency_gate(
    protocol_text: str,
    seed_record: dict[str, Any],
) -> dict[str, Any]:
    """Return PASS/FAIL with per-check facts; any mismatch = FREEZE_GATE_FAIL.

    R4: fail-closed against the F1 audit classes (empty/duplicate/historical
    control arrays, stale digest, missing bootstrap, contradicting protocol
    declarations) and derived from the single F4 integer policy.
    """
    failures: list[str] = []
    try:
        protocol_counts = parse_protocol_cardinalities(protocol_text)
    except ContractError as exc:
        failures.append(f"protocol: {exc}")
        protocol_counts = {}
    record_counts = {
        k: int(v) for k, v in (seed_record.get("variant_counts") or {}).items()
        if isinstance(v, int) and not isinstance(v, bool)
    }

    budget = derive_budget()

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
    seeds = seed_record.get("seeds") or {}
    for variant in ("0b", "32b"):
        if len(seeds.get(variant) or []) != PRIMARY_N:
            failures.append(f"seed record {variant} stream length != PRIMARY_N")
    for variant in ("11b", "53b"):
        if len(seeds.get(variant) or []) != CONTROL_N:
            failures.append(f"seed record {variant} stream length != CONTROL_N")

    if budget["confirmatory_runs"] != 296:
        failures.append("budget confirmatory != 296 for 2 primary + 2 control variants")
    if budget["replacement_runs_cap"] != 56:
        failures.append("budget replacement cap != 56 under the floor(0.20*N)-per-cell policy")
    if budget["max_runs"] != 352:
        failures.append("budget max_runs != 352 (296 confirmatory + 56 replacement cap)")
    if N_MIN_PRIMARY != n_min_cell(PRIMARY_N) or N_MIN_PRIMARY * 100 < 80 * PRIMARY_N:
        failures.append("N_min primary violates the ceil(0.80*N) integer policy")
    if N_MIN_CONTROL != n_min_cell(CONTROL_N) or N_MIN_CONTROL * 100 < 80 * CONTROL_N:
        failures.append("N_min control violates the ceil(0.80*N) integer policy")
    if budget["replacement_runs_cap"] * 100 > 20 * budget["confirmatory_runs"]:
        failures.append("replacement cap exceeds the literal 20% bound")

    _deep_record_checks(seed_record, failures)
    _protocol_declaration_checks(protocol_text, failures)

    return {
        "kind": "r4_freeze_consistency_gate",
        "gate": "PASS" if not failures else "FREEZE_GATE_FAIL",
        "failures": failures,
        "protocol_counts": protocol_counts,
        "record_counts": record_counts,
        "budget": budget,
        "integer_rounding_policy": INTEGER_ROUNDING_POLICY["name"],
        "n_min": {"primary": N_MIN_PRIMARY, "control": N_MIN_CONTROL},
    }
