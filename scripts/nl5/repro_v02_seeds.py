"""Deterministic fresh seed generation for NANOLAB_REPRO_V0_2 (candidate R3).

Pre-data tooling (WO-NL5-ACCEPTANCE-POLICY-R2, repair R3). Revision R3 fixes
the R1/R2 defect where the generator emitted 10 seeds per variant while the
protocol required 40 primaries: the per-variant replica counts are now an
explicit machine contract (VARIANT_REPLICAS) shared with the protocol text
and enforced by tests and the freeze consistency gate.

Deterministic tree-collision continuation rule (fixed BEFORE any grid/result
computation, protocol §7): candidate seed identities are consumed in index
order per variant; an identity whose literal decimal representation already
occurs in the repository evidence tree (SEED_COLLISION) is SKIPPED and the
next index is consumed, until the variant quota is filled. The generator
never hand-picks replacements; skips are recorded in the seed record.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

RULE_ID = "NANOLAB_REPRO_V0_2_DISTRIBUTIONAL"
DEFAULT_ANCHOR = "NANOLAB-REPRO-V0.2-R1"

# Machine contract (protocol §8, revision R3): per-variant fresh replica counts.
PRIMARY_VARIANTS = ("0b", "32b")
CONTROL_VARIANTS = ("11b", "53b")
DEFAULT_VARIANTS = PRIMARY_VARIANTS + CONTROL_VARIANTS
PRIMARY_REPLICAS = 64
CONTROL_REPLICAS = 10
VARIANT_REPLICAS: dict[str, int] = {
    "0b": PRIMARY_REPLICAS,
    "32b": PRIMARY_REPLICAS,
    "11b": CONTROL_REPLICAS,
    "53b": CONTROL_REPLICAS,
}
FRESH_SEED_TOTAL = sum(VARIANT_REPLICAS.values())  # 148 (64+64+10+10; grid-selected N=64)
BOOTSTRAP_RESAMPLES = 10_000

# Frozen exclusion list: every documented R1 confirmatory seed (34; protocol §7).
HISTORICAL_SEEDS_V1: frozenset[int] = frozenset(
    {
        -200619630, 319832093, 201004, 202008, 203012,
        204016, 205020, 206024, 902107,
        510101, 520202, 530303,
        410273, 520931, 638257, 741953, 852607, 963541,
        174329, 285637, 396421, 507283, 618457, 729613,
        1259289227, 1358106528, 1524307444, 601855227, 274288237,
        972234272, 1934775205, 1747973984, 880427736, 744386736,
    }
)


class SeedCollisionError(RuntimeError):
    """Raised when the exclusion gate forbids a candidate seed."""


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
    count: int,
    excluded: frozenset[int] = HISTORICAL_SEEDS_V1,
    tree_collision_scan: Callable[[int], bool] | None = None,
) -> dict[str, Any]:
    """Consume the deterministic index stream under the pre-declared rules.

    Rules (protocol §7, fixed pre-data):
    1. a seed equal to any excluded historical value is forbidden — the
       generator raises (exclusion list is immutable, no continuation past it);
    2. a seed whose literal form already occurs in the repository evidence
       tree (tree_collision_scan callback returns True) is SKIPPED — the next
       index is consumed (deterministic continuation), and the skip is
       recorded;
    3. in-stream duplicates raise (distinct labels make this impossible in
       practice; the check is a hard guarantee).
    """
    seeds: list[int] = []
    skipped: list[dict[str, Any]] = []
    index = 0
    while len(seeds) < count:
        index += 1
        seed = derive_seed(anchor, replica_label(variant, index))
        if seed in excluded:
            raise SeedCollisionError(
                f"{variant}: candidate seed {seed} (index {index}) is a documented "
                "historical R1 seed — exclusion list is immutable"
            )
        if tree_collision_scan is not None and tree_collision_scan(seed):
            skipped.append({"index": index, "seed": seed, "reason": "SEED_COLLISION_TREE"})
            continue
        if seed in seeds:
            raise ValueError(f"{variant}: duplicate seed within stream at index {index}")
        seeds.append(seed)
    return {"seeds": seeds, "skipped": skipped, "indices_consumed": index}


def generate_bootstrap_seed(
    anchor: str,
    variant: str,
    excluded: frozenset[int] = HISTORICAL_SEEDS_V1,
    taken: frozenset[int] = frozenset(),
) -> int:
    index = 0
    while True:
        label = f"bootstrap-{variant}" if index == 0 else f"bootstrap-{variant}-{index:02d}"
        seed = derive_seed(anchor, label)
        if seed not in excluded and seed not in taken:
            return seed
        index += 1


def seed_record(
    anchor: str = DEFAULT_ANCHOR,
    variants: tuple[str, ...] = DEFAULT_VARIANTS,
    variant_replicas: dict[str, int] | None = None,
    tree_collision_scan: Callable[[int], bool] | None = None,
) -> dict[str, Any]:
    """Full machine-readable seed record for the Director freeze step."""
    counts = dict(VARIANT_REPLICAS if variant_replicas is None else variant_replicas)
    payload: dict[str, Any] = {
        "rule_id": RULE_ID,
        "anchor": anchor,
        "algorithm": "seed(v,i) = int(big-endian sha256('{anchor}|{v}|replica-{i:04d}')[:4]) & 0x7FFFFFFF; "
        "bootstrap = sha256('{anchor}|bootstrap-{v}')[:4] & 0x7FFFFFFF",
        "variant_counts": {variant: counts[variant] for variant in variants},
        "primary_replicas": PRIMARY_REPLICAS,
        "control_replicas": CONTROL_REPLICAS,
        "fresh_seed_total": sum(counts[variant] for variant in variants),
        "bootstrap_seed_total": len(variants),
        "seeds": {},
        "skipped_identities": {},
        "bootstrap_seeds": {},
        "exclusion_list_size": len(HISTORICAL_SEEDS_V1),
        "exclusions_applied": sorted(HISTORICAL_SEEDS_V1),
        "tree_collision_rule": "consume index order; skip identities whose literal form "
        "occurs in the repository evidence tree; record skips",
    }
    all_seeds: list[int] = []
    for variant in variants:
        outcome = generate_variant_seeds(
            anchor, variant, counts[variant], tree_collision_scan=tree_collision_scan
        )
        payload["seeds"][variant] = outcome["seeds"]
        payload["skipped_identities"][variant] = outcome["skipped"]
        all_seeds += outcome["seeds"]
    if len(set(all_seeds)) != len(all_seeds):
        raise ValueError("duplicate seeds across variants")
    taken = frozenset(all_seeds) | frozenset(HISTORICAL_SEEDS_V1)
    for variant in variants:
        payload["bootstrap_seeds"][variant] = generate_bootstrap_seed(anchor, variant, excluded=taken)
    canonical = json.dumps(
        {
            "seeds": payload["seeds"],
            "bootstrap_seeds": payload["bootstrap_seeds"],
            "anchor": anchor,
            "variant_counts": payload["variant_counts"],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["record_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def write_seed_record(
    path: Path, anchor: str = DEFAULT_ANCHOR, tree_collision_scan: Callable[[int], bool] | None = None
) -> dict[str, Any]:
    record = seed_record(anchor, tree_collision_scan=tree_collision_scan)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def literal_tree_collision_scan(
    repo_root: Path,
    seeds: list[int],
    exclude_paths: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Whole-tree literal search: does each seed's decimal form occur in the tree?

    Deterministic and mechanical (``git grep -F`` over the worktree). A hit
    means SEED_COLLISION -> freeze prohibited (protocol §7). Freeze-time scans
    pass ``exclude_paths`` for the seed record and the candidate protocol
    document — the only legitimate places a seed may appear (precedent:
    platform-study verifier counted WO-file hits as the expected location).
    """
    root = Path(repo_root)
    hits: dict[str, list[str]] = {}
    for seed in seeds:
        needle = str(seed)
        completed = subprocess.run(
            ["git", "-C", str(root), "grep", "-F", "-l", "--", needle],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        files = [
            line
            for line in completed.stdout.splitlines()
            if line.strip() and not any(line.startswith(prefix) for prefix in exclude_paths)
        ]
        if files:
            hits[needle] = files
    return {"scanned": len(seeds), "collisions": hits, "collision_count": len(hits)}
