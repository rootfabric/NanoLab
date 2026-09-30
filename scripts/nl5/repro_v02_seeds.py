"""Deterministic fresh seed generation for NANOLAB_REPRO_V0_2_DISTRIBUTIONAL.

Pre-data tooling (WO-NL5-ACCEPTANCE-POLICY-R2): seeds are derived from the
frozen protocol anchor via sha256 — the operator cannot pick "convenient"
values. Historical R1 confirmatory seeds are in a frozen exclusion list; the
generator refuses to emit a seed record containing any excluded value. The
record carries a sha256 digest over the canonical seed payload only (metadata
such as generation time is deliberately outside the digest).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

RULE_ID = "NANOLAB_REPRO_V0_2_DISTRIBUTIONAL"
DEFAULT_ANCHOR = "NANOLAB-REPRO-V0.2-R1"

# Frozen exclusion list: every known R1 confirmatory seed (candidate protocol
# §7). Sources: E1 (T1 + verify), E2 reference, E3-reval, platform study
# S001-S010 (PREREGISTRATION_FREEZE_R1), frozen bootstrap seed.
HISTORICAL_SEEDS_V1: frozenset[int] = frozenset(
    {
        -200619630,  # E1-R1-S001 (T1 verbatim)
        319832093,  # NL2-002 fresh verify rebuild
        201004,  # E2 reference
        202008,  # E2 reference
        203012,  # E2 reference
        204016,  # E3 revalidation
        205020,  # E3 revalidation
        206024,  # E3 revalidation / NL4-003
        902107,  # platform-study frozen bootstrap seed
        1259289227,  # S001
        1358106528,  # S002
        1524307444,  # S003
        601855227,  # S004
        274288237,  # S005
        972234272,  # S006
        1934775205,  # S007
        1747973984,  # S008
        880427736,  # S009
        744386736,  # S010
    }
)

PRIMARY_VARIANTS = ("0b", "32b")
CONTROL_VARIANTS = ("11b", "53b")
DEFAULT_VARIANTS = PRIMARY_VARIANTS + CONTROL_VARIANTS
REPLICAS_PER_CELL = 10
BOOTSTRAP_RESAMPLES = 10_000


def derive_seed(anchor: str, label: str) -> int:
    """Positive int32 seed from the anchor|label sha256 stream (deterministic).

    First 4 digest bytes, big-endian, top bit masked off -> value in [0, 2^31).
    """
    digest = hashlib.sha256(f"{anchor}|{label}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


def replica_label(variant: str, index: int) -> str:
    if index < 1:
        raise ValueError("replica index is 1-based")
    return f"{variant}|replica-{index:04d}"


def generate_variant_seeds(
    anchor: str,
    variant: str,
    count: int = REPLICAS_PER_CELL,
    excluded: frozenset[int] = HISTORICAL_SEEDS_V1,
) -> list[int]:
    seeds = [derive_seed(anchor, replica_label(variant, index)) for index in range(1, count + 1)]
    collisions = sorted(set(seeds) & set(excluded))
    if collisions:
        raise ValueError(f"seed collision with historical R1 seeds: {collisions}")
    if len(set(seeds)) != len(seeds):
        raise ValueError("duplicate seeds within variant stream")
    return seeds


def generate_bootstrap_seed(
    anchor: str,
    variant: str,
    excluded: frozenset[int] = HISTORICAL_SEEDS_V1,
) -> int:
    seed = derive_seed(anchor, f"bootstrap-{variant}")
    if seed in excluded:
        raise ValueError(f"bootstrap seed collides with historical seeds: {seed}")
    return seed


def seed_record(
    anchor: str = DEFAULT_ANCHOR,
    variants: tuple[str, ...] = DEFAULT_VARIANTS,
    replicas_per_cell: int = REPLICAS_PER_CELL,
) -> dict[str, Any]:
    """Full machine-readable seed record for the Director freeze step."""
    payload: dict[str, Any] = {
        "rule_id": RULE_ID,
        "anchor": anchor,
        "algorithm": "seed(v,i) = int(big-endian sha256('{anchor}|{v}|replica-{i:04d}')[:4]) & 0x7FFFFFFF; "
        "bootstrap = sha256('{anchor}|bootstrap-{v}')[:4] & 0x7FFFFFFF",
        "replicas_per_cell": replicas_per_cell,
        "seeds": {},
        "bootstrap_seeds": {},
        "exclusion_list_size": len(HISTORICAL_SEEDS_V1),
        "exclusions_applied": sorted(HISTORICAL_SEEDS_V1),
    }
    all_seeds: list[int] = []
    for variant in variants:
        seeds = generate_variant_seeds(anchor, variant, replicas_per_cell)
        payload["seeds"][variant] = seeds
        payload["bootstrap_seeds"][variant] = generate_bootstrap_seed(anchor, variant)
        all_seeds += seeds
    if len(set(all_seeds)) != len(all_seeds):
        raise ValueError("duplicate seeds across variants")
    canonical = json.dumps(
        {"seeds": payload["seeds"], "bootstrap_seeds": payload["bootstrap_seeds"], "anchor": anchor},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["record_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def write_seed_record(path: Path, anchor: str = DEFAULT_ANCHOR) -> dict[str, Any]:
    record = seed_record(anchor)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record
