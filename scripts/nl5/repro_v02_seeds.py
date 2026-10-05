"""Deterministic fresh seed generation for NANOLAB_REPRO_V0_2 (candidate R4).

Pre-data tooling (WO-NL5-ACCEPTANCE-POLICY-R2 lineage; pre-freeze hardening
R4 per WO-NL5-V02-PREFREEZE-HARDENING-R4). Revision R3 fixed the R1/R2 defect
where the generator emitted 10 seeds per variant while the protocol required
40 primaries. Revision R4 repairs the audit findings F2/F3:

- F2: ``literal_tree_collision_scan`` scans an explicitly pinned immutable
  Git tree (not the mutable worktree) and distinguishes ``git grep`` exit 0
  (hits) / exit 1 (clean no-match) from every other outcome (missing object,
  non-repository, timeout, broken Git) which raise ``TreeScanError`` — the
  scan can no longer report ``collision_count = 0`` for an incomplete scan.
  Path exclusions are EXACT paths (no prefix semantics), so a documented
  exclusion can never hide a neighbouring evidence file.

- F3: replacement identities never restart at raw ``N+1``. The seed record
  stores per-variant ``indices_consumed`` / ``next_candidate_index`` and a
  pre-generated frozen replacement pool that continues the deterministic
  stream AFTER the last consumed candidate index. Revision R4.1 (reviewer
  correction M-2) additionally proves every published pool bit-exactly:
  :func:`replay_replacement_stream` re-derives the pool from
  ``(anchor, variant, start_index, quota, recorded skips)`` and each
  recorded skip entry is validated as the strict object
  ``{"index", "seed", "reason": "SEED_COLLISION_TREE"}`` whose seed equals
  the deterministic stream seed at that index.

Historical behaviour (R3 record, digest eb4ab3f891e17dd2b456a3870ed73b19e
39d67bf51109b6cb47ca64524ce476b) is preserved: replaying the recorded
skip sets reproduces the committed R3 identities bit-exactly.
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

# Immutable R3 generation exclusion tree (protocol §7: "генерация R3, scan на
# a9d7d07-tree"). Confirmatory identities and the R4 replacement pools are
# generated against THIS pinned tree; any change of the exclusion tree is a new
# explicitly declared generation revision, never silent drift.
R3_EXCLUSION_TREE_PIN = "a9d7d07fa264e9907b67ca244b00ba2da3430b0f"

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


class TreeScanError(RuntimeError):
    """Raised when a literal tree scan cannot be completed (fail-closed, F2).

    This covers: non-repository, unreadable/missing pinned object, ``git grep``
    exit codes other than 0/1, timeouts and undecodable output. A scan that
    ends in this state has NO opinion about collisions.
    """

    def __init__(self, message: str, returncode: int | None = None, stderr: str = "") -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


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


def bootstrap_label(variant: str, index: int) -> str:
    if index < 0:
        raise ValueError("bootstrap index is non-negative")
    return f"bootstrap-{variant}" if index == 0 else f"bootstrap-{variant}-{index:02d}"


def _check_candidate(seed: int, variant: str, index: int, excluded: frozenset[int]) -> None:
    if seed in excluded:
        raise SeedCollisionError(
            f"{variant}: candidate seed {seed} (index {index}) is a documented "
            "historical R1 seed — exclusion list is immutable"
        )


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
    2. a seed whose literal form already occurs in the pinned repository
       evidence tree (tree_collision_scan callback returns True) is SKIPPED —
       the next index is consumed (deterministic continuation), and the skip
       is recorded;
    3. in-stream duplicates raise (distinct labels make this impossible in
       practice; the check is a hard guarantee).

    The outcome reports ``indices_consumed`` and ``next_candidate_index`` so
    that replacement generation (F3) continues after the true cursor, never
    at raw ``count + 1``.
    """
    seeds: list[int] = []
    skipped: list[dict[str, Any]] = []
    index = 0
    while len(seeds) < count:
        index += 1
        seed = derive_seed(anchor, replica_label(variant, index))
        _check_candidate(seed, variant, index, excluded)
        if tree_collision_scan is not None and tree_collision_scan(seed):
            skipped.append({"index": index, "seed": seed, "reason": "SEED_COLLISION_TREE"})
            continue
        if seed in seeds:
            raise ValueError(f"{variant}: duplicate seed within stream at index {index}")
        seeds.append(seed)
    return {
        "seeds": seeds,
        "skipped": skipped,
        "indices_consumed": index,
        "next_candidate_index": index + 1,
    }


def generate_replacement_pool(
    anchor: str,
    variant: str,
    start_index: int,
    count: int,
    excluded: frozenset[int] = HISTORICAL_SEEDS_V1,
    taken: frozenset[int] = frozenset(),
    tree_collision_scan: Callable[[int], bool] | None = None,
) -> dict[str, Any]:
    """Continue the deterministic stream AFTER the last consumed index (F3).

    The pool must be requested with ``start_index`` = the variant's
    ``next_candidate_index`` (the index after the LAST consumed candidate,
    including skipped ones) — never with raw ``N + 1``. Each pool identity
    is checked against the historical exclusion list, against every already
    taken identity (confirmatory + bootstrap + other pools) and against the
    pinned-tree literal scan, under the same rules as confirmatory
    generation. Outcome-driven selection is impossible by construction: the
    pool is fully determined by (anchor, variant, start_index, count, pins).
    """
    if start_index < 1:
        raise ValueError("replacement start_index must be >= 1 (1-based stream)")
    if count < 0:
        raise ValueError("replacement pool count must be >= 0")
    seeds: list[int] = []
    skipped: list[dict[str, Any]] = []
    index = start_index - 1
    while len(seeds) < count:
        index += 1
        seed = derive_seed(anchor, replica_label(variant, index))
        _check_candidate(seed, variant, index, excluded)
        if seed in taken:
            raise SeedCollisionError(
                f"{variant}: replacement candidate {seed} (index {index}) collides "
                "with an already taken identity — stream invariant violated"
            )
        if tree_collision_scan is not None and tree_collision_scan(seed):
            skipped.append({"index": index, "seed": seed, "reason": "SEED_COLLISION_TREE"})
            continue
        if seed in seeds:
            raise ValueError(f"{variant}: duplicate replacement seed at index {index}")
        seeds.append(seed)
    return {
        "seeds": seeds,
        "skipped": skipped,
        "start_index": start_index,
        "indices_consumed": [start_index, index] if count > 0 else [start_index, start_index - 1],
        "next_candidate_index": index + 1,
    }


def generate_bootstrap_seed(
    anchor: str,
    variant: str,
    excluded: frozenset[int] = HISTORICAL_SEEDS_V1,
    taken: frozenset[int] = frozenset(),
) -> tuple[int, int]:
    """First non-excluded bootstrap identity; returns ``(seed, index)``."""
    index = 0
    while True:
        seed = derive_seed(anchor, bootstrap_label(variant, index))
        if seed not in excluded and seed not in taken:
            return seed, index
        index += 1


def literal_tree_collision_scan(
    repo_root: Path,
    seeds: list[int],
    exclude_paths: tuple[str, ...] = (),
    pinned_commit: str | None = None,
    timeout: float = 300,
) -> dict[str, Any]:
    """Pinned-tree literal collision scan (F2, fail-closed).

    Searches each seed's decimal literal form in an immutable Git tree. When
    ``pinned_commit`` is given, the pinned tree/object is scanned
    (``git grep -F -l -e <needle> <commit> --``); uncommitted worktree edits
    cannot hide or invent hits. Without ``pinned_commit`` the tracked
    worktree is scanned — this mode is NON-authoritative and exists only for
    tests/diagnostics; generation and freeze paths must always pin.

    ``git grep`` exit semantics (fail-closed):
      0                -> hits found (parsed);
      1                -> clean no-match for this needle;
      anything else, a missing pinned object, a non-repository, a timeout or
      undecodable output -> ``TreeScanError``. A failed scan NEVER reports
      ``collision_count = 0``.

    ``exclude_paths`` is an EXACT relative-path allowlist (the only legitimate
    places a seed may appear: the seed record and the candidate protocol
    document). Exact equality is used — no prefix matching — so a documented
    exclusion cannot hide a neighbouring evidence file. Excluded hits are
    reported separately as ``excluded_hits`` for transparency.
    """
    root = Path(repo_root)
    git_base = ["git", "-C", str(root)]
    if pinned_commit is not None:
        try:
            checked = subprocess.run(
                git_base + ["cat-file", "-e", f"{pinned_commit}^{{commit}}"],
                capture_output=True, text=True, timeout=timeout, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TreeScanError(
                f"pinned object check timed out after {timeout}s for {pinned_commit}",
                returncode=None, stderr=str(exc),
            ) from exc
        except OSError as exc:
            raise TreeScanError(
                f"pinned object check could not execute git: {exc}",
                returncode=None, stderr=str(exc),
            ) from exc
        if checked.returncode != 0:
            raise TreeScanError(
                f"pinned object {pinned_commit} is not available in {root}",
                returncode=checked.returncode, stderr=checked.stderr.strip(),
            )
    hits: dict[str, list[str]] = {}
    excluded_hits: dict[str, list[str]] = {}
    exact_exclusions = set(exclude_paths)
    for seed in seeds:
        needle = str(seed)
        argv = git_base + ["grep", "-I", "-F", "-l", "-e", needle]
        if pinned_commit is not None:
            argv += [pinned_commit, "--"]
        else:
            argv += ["--"]
        try:
            completed = subprocess.run(
                argv, capture_output=True, text=True, timeout=timeout, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise TreeScanError(
                f"tree scan timed out after {timeout}s for needle {needle}",
                returncode=None, stderr=str(exc),
            ) from exc
        except OSError as exc:
            raise TreeScanError(
                f"tree scan could not execute git for needle {needle}: {exc}",
                returncode=None, stderr=str(exc),
            ) from exc
        if completed.returncode not in (0, 1):
            raise TreeScanError(
                f"git grep failed for needle {needle} (exit {completed.returncode}); "
                "scan is incomplete — refusing to report a collision count",
                returncode=completed.returncode, stderr=completed.stderr.strip(),
            )
        files = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        if pinned_commit is not None:
            prefix = f"{pinned_commit}:"
            files = [path[len(prefix):] if path.startswith(prefix) else path for path in files]
        outside = sorted(path for path in files if path not in exact_exclusions)
        inside = sorted(path for path in files if path in exact_exclusions)
        if outside:
            hits[needle] = outside
        if inside:
            excluded_hits[needle] = inside
    return {
        "scanned": len(seeds),
        "collisions": hits,
        "collision_count": len(hits),
        "excluded_hits": excluded_hits,
        "pinned_commit": pinned_commit,
        "mode": "pinned_tree" if pinned_commit is not None else "worktree_non_authoritative",
        "exclude_paths_exact": sorted(exact_exclusions),
        "status": "COLLISIONS" if hits else "CLEAN",
    }


def make_pinned_tree_scanner(
    repo_root: Path,
    pinned_commit: str,
    exclude_paths: tuple[str, ...] = (),
    timeout: float = 300,
) -> Callable[[int], bool]:
    """Build a fail-closed ``tree_collision_scan`` callback on a pinned tree.

    Any scan error raises ``TreeScanError`` (propagated by the generator) —
    generation can never silently treat an incomplete scan as "no collision".
    """
    def scan(seed: int) -> bool:
        result = literal_tree_collision_scan(
            repo_root, [seed], exclude_paths=exclude_paths,
            pinned_commit=pinned_commit, timeout=timeout,
        )
        return result["collision_count"] > 0

    return scan


def seed_record(
    anchor: str = DEFAULT_ANCHOR,
    variants: tuple[str, ...] = DEFAULT_VARIANTS,
    variant_replicas: dict[str, int] | None = None,
    tree_collision_scan: Callable[[int], bool] | None = None,
    replacement_quota_pairs: dict[str, int] | None = None,
    exclusion_tree_pin: str | None = None,
    generation_revision: str | None = None,
    scan_context_paths: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Full machine-readable seed record for the Director freeze step.

    R4 shape: besides the R3 fields (confirmatory identities, skips,
    bootstrap), the record carries the F3 replacement cursor state
    (``indices_consumed`` / ``next_candidate_index``), pre-generated frozen
    replacement pools (``replacement_quota_pairs`` per variant, in paired
    identities), the immutable ``exclusion_tree_pin`` the streams were
    generated against, and the exact scan allowlist. ``record_sha256`` keeps
    the R3 logical recipe (seeds + bootstrap + anchor + variant_counts), so
    the R4 record's logical digest equals the committed R3 digest when the
    confirmatory identities are unchanged.
    """
    counts = dict(VARIANT_REPLICAS if variant_replicas is None else variant_replicas)
    payload: dict[str, Any] = {
        "rule_id": RULE_ID,
        "anchor": anchor,
        "algorithm": "seed(v,i) = int(big-endian sha256('{anchor}|{v}|replica-{i:04d}')[:4]) & 0x7FFFFFFF; "
        "bootstrap = sha256('{anchor}|bootstrap-{v}')[:4] & 0x7FFFFFFF "
        "(bootstrap index retry -01, -02, ... while colliding)",
        "variant_counts": {variant: counts[variant] for variant in variants},
        "primary_replicas": PRIMARY_REPLICAS,
        "control_replicas": CONTROL_REPLICAS,
        "fresh_seed_total": sum(counts[variant] for variant in variants),
        "bootstrap_seed_total": len(variants),
        "seeds": {},
        "skipped_identities": {},
        "bootstrap_seeds": {},
        "bootstrap_indices": {},
        "indices_consumed": {},
        "next_candidate_index": {},
        "exclusion_list_size": len(HISTORICAL_SEEDS_V1),
        "exclusions_applied": sorted(HISTORICAL_SEEDS_V1),
        "tree_collision_rule": "consume index order; skip identities whose literal form "
        "occurs in the pinned exclusion tree; record skips; scan errors are fatal "
        "(fail-closed, F2)",
        "exclusion_tree_pin": exclusion_tree_pin,
        "generation_revision": generation_revision,
        "scan_context_paths_exact": list(scan_context_paths),
    }
    all_seeds: list[int] = []
    for variant in variants:
        outcome = generate_variant_seeds(
            anchor, variant, counts[variant], tree_collision_scan=tree_collision_scan
        )
        payload["seeds"][variant] = outcome["seeds"]
        payload["skipped_identities"][variant] = outcome["skipped"]
        payload["indices_consumed"][variant] = outcome["indices_consumed"]
        payload["next_candidate_index"][variant] = outcome["next_candidate_index"]
        all_seeds += outcome["seeds"]
    if len(set(all_seeds)) != len(all_seeds):
        raise ValueError("duplicate seeds across variants")
    taken = frozenset(all_seeds) | frozenset(HISTORICAL_SEEDS_V1)
    for variant in variants:
        seed, index = generate_bootstrap_seed(anchor, variant, excluded=taken)
        payload["bootstrap_seeds"][variant] = seed
        payload["bootstrap_indices"][variant] = index
        taken = taken | {seed}
    if replacement_quota_pairs is not None:
        payload["replacement_quota_pairs"] = {
            variant: int(replacement_quota_pairs[variant]) for variant in variants
        }
        payload["replacement_pools"] = {}
        for variant in variants:
            start = payload["next_candidate_index"][variant]
            pool = generate_replacement_pool(
                anchor,
                variant,
                start_index=start,
                count=payload["replacement_quota_pairs"][variant],
                excluded=HISTORICAL_SEEDS_V1,
                taken=taken,
                tree_collision_scan=tree_collision_scan,
            )
            payload["replacement_pools"][variant] = pool
            taken = taken | set(pool["seeds"])
    else:
        payload["replacement_quota_pairs"] = None
        payload["replacement_pools"] = None
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


def replay_variant_stream(
    anchor: str,
    variant: str,
    indices_consumed: int,
    skipped_indices: set[int],
) -> list[int]:
    """Bit-exact regeneration of a recorded stream from its cursor state.

    Rebuilds the identities the deterministic stream MUST have produced at
    the accepted indices (the complement of the skipped indices). Used by the
    freeze contract gate to prove that a published record is exactly the
    pre-declared stream — not a hand-adjusted list.
    """
    bad = [i for i in skipped_indices if not 1 <= i <= indices_consumed]
    if bad:
        raise ValueError(f"{variant}: skipped indices outside consumed range: {sorted(bad)}")
    accepted = [i for i in range(1, indices_consumed + 1) if i not in skipped_indices]
    return [derive_seed(anchor, replica_label(variant, i)) for i in accepted]


def write_seed_record(
    path: Path, anchor: str = DEFAULT_ANCHOR, tree_collision_scan: Callable[[int], bool] | None = None
) -> dict[str, Any]:
    record = seed_record(anchor, tree_collision_scan=tree_collision_scan)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


# ---------------------------------------------------------------------------
# R4.1 (reviewer corrections M-2/M-3): bit-exact replacement replay,
# integrity digests and the machine-bound collision-scan manifest.
# ---------------------------------------------------------------------------

SKIP_REASON_TREE = "SEED_COLLISION_TREE"
SCAN_MANIFEST_KIND = "nanolab_v02_collision_scan_manifest"
SCAN_MANIFEST_SCHEMA_VERSION = 1


def canonical_json(value: Any) -> str:
    """Stable serialization used by every R4.1 digest (sort_keys, compact)."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_skip_entry(entry: Any, anchor: str, variant: str, where: str) -> list[str]:
    """Validate one recorded skip as the strict object the protocol requires.

    Exact key set ``{"index", "seed", "reason"}``; integer types (no bool);
    ``reason`` must be exactly ``SEED_COLLISION_TREE``; and the recorded seed
    must equal the deterministic stream seed ``derive(anchor, variant, index)``
    — a skip entry that does not re-derive is a fabrication, not a collision.
    Returns a list of failure strings (empty = valid).
    """
    failures: list[str] = []
    if not isinstance(entry, dict):
        return [f"{where}: skip entry must be an object, got {type(entry).__name__}"]
    expected_keys = {"index", "seed", "reason"}
    missing = sorted(expected_keys - set(entry))
    extra = sorted(set(entry) - expected_keys)
    if missing:
        failures.append(f"{where}: skip entry missing keys {missing}")
    if extra:
        failures.append(f"{where}: skip entry has unknown extra keys {extra}")
    index = entry.get("index")
    seed = entry.get("seed")
    if not _is_plain_int(index) or index < 1:
        failures.append(f"{where}: skip index must be a positive integer, got {index!r}")
    if not _is_plain_int(seed) or not 0 <= seed < 2**31:
        failures.append(f"{where}: skip seed must be an int32-positive integer, got {seed!r}")
    if entry.get("reason") != SKIP_REASON_TREE:
        failures.append(
            f"{where}: skip reason must be {SKIP_REASON_TREE!r}, got {entry.get('reason')!r}"
        )
    if failures:
        return failures
    derived = derive_seed(anchor, replica_label(variant, index))
    if seed != derived:
        failures.append(
            f"{where}: recorded skip seed {seed} != derived stream seed {derived} "
            f"for {variant} index {index} (the skip does not re-derive)"
        )
    return failures


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def replay_replacement_stream(
    anchor: str,
    variant: str,
    start_index: int,
    quota: int,
    skipped_entries: list[Any],
) -> list[int]:
    """Bit-exact regeneration of a frozen replacement pool (R4.1, M-2).

    Replays ``for index from start_index: derive seed; drop only recorded
    skips (each validated against the derived stream) until ``quota``
    identities are accepted`` and returns the accepted identities. Every
    skip entry must be the strict collision object; a recorded seed that
    does not equal the derived stream seed, a wrong reason, an index before
    ``start_index``, duplicate indices or a skip recorded after the last
    consumed index all raise :class:`ValueError`.
    """
    if not _is_plain_int(start_index) or start_index < 1:
        raise ValueError(f"{variant}: replacement start_index must be a positive integer")
    if not _is_plain_int(quota) or quota < 0:
        raise ValueError(f"{variant}: replacement quota must be a non-negative integer")
    skips: dict[int, int] = {}
    for position, entry in enumerate(skipped_entries):
        where = f"{variant} replacement skip entry {position}"
        failures = check_skip_entry(entry, anchor, variant, where)
        if failures:
            raise ValueError("; ".join(failures))
        index = entry["index"]
        if index < start_index:
            raise ValueError(
                f"{where}: skip index {index} precedes pool start_index {start_index}"
            )
        if index in skips:
            raise ValueError(f"{where}: duplicate skip index {index}")
        skips[index] = entry["seed"]
    accepted: list[int] = []
    index = start_index - 1
    while len(accepted) < quota:
        index += 1
        seed = derive_seed(anchor, replica_label(variant, index))
        if index in skips:
            if skips[index] != seed:
                raise ValueError(
                    f"{variant}: recorded skip seed {skips[index]} != derived stream seed "
                    f"{seed} at replacement index {index}"
                )
            continue
        accepted.append(seed)
    trailing = sorted(i for i in skips if i > index)
    if trailing:
        raise ValueError(
            f"{variant}: skip indices recorded after the last consumed replacement "
            f"index {index}: {trailing}"
        )
    return accepted


def normalized_replacement_pools(pools: Any) -> dict[str, Any]:
    """Project pools to the four canonical fields shared by contract/record."""
    normalized: dict[str, Any] = {}
    if not isinstance(pools, dict):
        return normalized
    for variant, pool in pools.items():
        if not isinstance(pool, dict):
            normalized[variant] = pool
            continue
        normalized[variant] = {
            "seeds": pool.get("seeds"),
            "skipped": pool.get("skipped"),
            "start_index": pool.get("start_index"),
            "next_candidate_index": pool.get("next_candidate_index"),
        }
    return normalized


def replacement_pool_digest(pools: Any) -> str:
    """R4.1 integrity digest over the frozen replacement pools (M-2).

    Computed over the normalized pool content (seeds + skipped entries +
    cursors). A coordinated hand edit of contract and record cannot keep
    this digest AND the bit-exact stream replay valid at the same time.
    """
    return _sha256_text(canonical_json({"replacement_pools": normalized_replacement_pools(pools)}))


R4_RECORD_DIGEST_FIELDS = (
    "anchor",
    "variant_counts",
    "seeds",
    "skipped_identities",
    "bootstrap_seeds",
    "bootstrap_indices",
    "indices_consumed",
    "next_candidate_index",
    "replacement_quota_pairs",
    "replacement_pools",
    "exclusion_tree_pin",
    "generation_revision",
    "scan_context_paths_exact",
)


def r4_record_digest(record: dict[str, Any]) -> str:
    """Full R4 record integrity digest (R4.1, M-2).

    Covers the confirmatory identities AND the replacement pools, skips and
    cursor state. The historical R3 ``record_sha256`` (confirmatory-only
    logical recipe) is preserved unchanged as provenance; this digest is the
    R4 integrity protection the R3 recipe never provided.
    """
    payload = {field: record.get(field) for field in R4_RECORD_DIGEST_FIELDS}
    return _sha256_text(canonical_json(payload))


def build_collision_scan_manifest(
    repo_root: Path,
    exclusion_tree_pin: str,
    allowlist_paths: list[str],
    confirmatory_seeds: dict[str, list[int]],
    replacement_pools: dict[str, Any],
    skipped_identities: dict[str, list[Any]],
    timeout: float = 300,
) -> dict[str, Any]:
    """Produce the machine-bound collision-scan manifest (R4.1, M-3).

    Scans the pinned immutable tree for (a) every accepted confirmatory and
    replacement identity — must be CLEAN outside the exact allowlist — and
    (b) every recorded ``SEED_COLLISION_TREE`` skip (confirmatory AND
    replacement-pool skips) — must show >= 1 non-allowlisted literal hit,
    else :class:`TreeScanError` propagates (fail-closed). The returned
    manifest carries ``manifest_sha256`` over its canonical content; the
    authoritative freeze contract binds that digest, so any later edit of
    the published scan facts is detectable.
    """
    manifest: dict[str, Any] = {
        "schema_version": SCAN_MANIFEST_SCHEMA_VERSION,
        "kind": SCAN_MANIFEST_KIND,
        "exclusion_tree_pin": exclusion_tree_pin,
        "scan_mode": "pinned_tree",
        "allowlist_paths_exact": sorted(allowlist_paths),
        "accepted_confirmatory": {},
        "accepted_replacement": {},
        "recorded_skips": {},
    }
    exclusions = tuple(sorted(allowlist_paths))
    for variant, stream in confirmatory_seeds.items():
        result = literal_tree_collision_scan(
            repo_root, list(stream), exclude_paths=exclusions,
            pinned_commit=exclusion_tree_pin, timeout=timeout,
        )
        manifest["accepted_confirmatory"][variant] = {
            "seeds": list(stream),
            "status": result["status"],
            "collisions_outside_allowlist": result["collision_count"],
            "excluded_hits": result["excluded_hits"],
        }
    for variant, pool in replacement_pools.items():
        pool_seeds = pool.get("seeds") if isinstance(pool, dict) else None
        result = literal_tree_collision_scan(
            repo_root, list(pool_seeds or []), exclude_paths=exclusions,
            pinned_commit=exclusion_tree_pin, timeout=timeout,
        )
        manifest["accepted_replacement"][variant] = {
            "seeds": list(pool_seeds or []),
            "status": result["status"],
            "collisions_outside_allowlist": result["collision_count"],
            "excluded_hits": result["excluded_hits"],
        }
    for variant in confirmatory_seeds:
        manifest["recorded_skips"][variant] = {
            "confirmatory": _prove_skips(
                repo_root, exclusions, exclusion_tree_pin,
                skipped_identities.get(variant) or [], variant, timeout,
            ),
            "replacement": _prove_skips(
                repo_root, exclusions, exclusion_tree_pin,
                (replacement_pools.get(variant) or {}).get("skipped") or [],
                variant, timeout,
            ),
        }
    manifest["scan_status"] = "VERIFIED"
    manifest["manifest_sha256"] = ""
    manifest["manifest_sha256"] = collision_manifest_digest(manifest)
    return manifest


def _prove_skips(
    repo_root: Path,
    exclusions: tuple[str, ...],
    exclusion_tree_pin: str,
    entries: list[Any],
    variant: str,
    timeout: float,
) -> list[dict[str, Any]]:
    """Scan each recorded skip of one stream; every skip needs a real hit."""
    proven: list[dict[str, Any]] = []
    for entry in entries:
        failures = check_skip_entry(entry, DEFAULT_ANCHOR, variant, f"{variant} skip")
        if failures:
            raise TreeScanError(
                f"recorded skip entry failed re-derivation: {'; '.join(failures)}"
            )
        result = literal_tree_collision_scan(
            repo_root, [entry["seed"]], exclude_paths=exclusions,
            pinned_commit=exclusion_tree_pin, timeout=timeout,
        )
        hit_paths = sorted(
            path for seed_hits in result["collisions"].values() for path in seed_hits
        )
        proven.append(
            {
                "index": entry["index"],
                "seed": entry["seed"],
                "reason": entry["reason"],
                "hit_paths": hit_paths,
                "non_allowlisted_hit_count": result["collision_count"],
            }
        )
    return proven


def collision_manifest_digest(manifest: dict[str, Any]) -> str:
    """SHA-256 over the canonical manifest content (self field excluded)."""
    payload = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    return _sha256_text(canonical_json(payload))


def verify_collision_manifest(
    contract: dict[str, Any],
    manifest: Any,
    failures: list[str],
    record: dict[str, Any] | None = None,
    rerun_root: Path | None = None,
    timeout: float = 300,
) -> None:
    """Bind the scan manifest into the freeze/dispatch decision (R4.1, M-3).

    Structural + coverage checks always run: exact kind/pin/allowlist, full
    coverage of accepted confirmatory + replacement identities and of every
    recorded skip, digest integrity. With ``rerun_root`` the gate additionally
    RE-RUNS the pinned-tree scan for every recorded skip — a fabricated
    "collision" for a clean deterministic candidate is rejected even when the
    contract, record and manifest were edited self-consistently. Any git
    error, missing pinned object or timeout is BLOCKED (fail-closed), never
    treated as clean. Appends failure strings to ``failures``; pre-existing
    failures from unrelated checks do not short-circuit manifest verification.
    """
    where = "collision_scan_manifest"
    local: list[str] = []
    if not isinstance(manifest, dict):
        failures.append(f"{where}: manifest must be an object")
        return
    if manifest.get("schema_version") != SCAN_MANIFEST_SCHEMA_VERSION:
        local.append(f"{where}: schema_version must be {SCAN_MANIFEST_SCHEMA_VERSION}")
    if manifest.get("kind") != SCAN_MANIFEST_KIND:
        local.append(f"{where}: kind must be {SCAN_MANIFEST_KIND!r}")
    pin = contract.get("seed_generation", {}).get("exclusion_tree_pin")
    if manifest.get("exclusion_tree_pin") != pin:
        local.append(f"{where}: exclusion_tree_pin != contract pin")
    allowlist = sorted(contract.get("seed_generation", {}).get("scan_allowlist_paths_exact") or [])
    if sorted(manifest.get("allowlist_paths_exact") or []) != allowlist:
        local.append(f"{where}: allowlist_paths_exact != contract allowlist")
    if manifest.get("scan_status") != "VERIFIED":
        local.append(f"{where}: scan_status must be VERIFIED")
    if manifest.get("manifest_sha256") != collision_manifest_digest(manifest):
        local.append(f"{where}: manifest_sha256 stale (digest mismatch)")
    if local:
        failures.extend(local)
        return

    confirmatory = contract.get("confirmatory_seeds") or {}
    pools = (contract.get("replacement") or {}).get("pools") or {}
    accepted_c = manifest.get("accepted_confirmatory")
    accepted_r = manifest.get("accepted_replacement")
    recorded = manifest.get("recorded_skips")
    for section, expected in (("accepted_confirmatory", confirmatory), ("accepted_replacement", pools)):
        block = manifest.get(section)
        if not isinstance(block, dict) or set(block) != set(expected):
            failures.append(f"{where}.{section}: must cover exactly the contract variants")
            continue
    if not isinstance(accepted_c, dict) or not isinstance(accepted_r, dict) or not isinstance(recorded, dict):
        return
    for variant, stream in confirmatory.items():
        block = accepted_c[variant]
        if block.get("seeds") != stream:
            failures.append(f"{where}.accepted_confirmatory.{variant}: seeds != contract identities")
        if block.get("collisions_outside_allowlist") != 0 or block.get("status") != "CLEAN":
            failures.append(
                f"{where}.accepted_confirmatory.{variant}: accepted identities must scan CLEAN "
                "outside the exact allowlist"
            )
    for variant, pool in pools.items():
        block = accepted_r[variant]
        if block.get("seeds") != pool.get("seeds"):
            failures.append(f"{where}.accepted_replacement.{variant}: seeds != contract pool")
        if block.get("collisions_outside_allowlist") != 0 or block.get("status") != "CLEAN":
            failures.append(
                f"{where}.accepted_replacement.{variant}: accepted identities must scan CLEAN "
                "outside the exact allowlist"
            )
    recorded_skips_by_variant = (record or {}).get("skipped_identities") or {}
    for variant, pool in pools.items():
        block = recorded.get(variant)
        if not isinstance(block, dict) or set(block) != {"confirmatory", "replacement"}:
            failures.append(
                f"{where}.recorded_skips.{variant}: must cover exactly the confirmatory and "
                "replacement skip streams"
            )
            continue
        expected_streams = {
            "confirmatory": {
                entry.get("index"): entry
                for entry in (recorded_skips_by_variant.get(variant) or [])
                if isinstance(entry, dict)
            },
            "replacement": {
                entry.get("index"): entry
                for entry in (pool.get("skipped") or [])
                if isinstance(entry, dict)
            },
        }
        for stream_name, expected_entries in expected_streams.items():
            proven_entries = block.get(stream_name)
            if not isinstance(proven_entries, list):
                failures.append(f"{where}.recorded_skips.{variant}.{stream_name}: missing coverage")
                continue
            proven_by_index = {
                fact.get("index"): fact for fact in proven_entries if isinstance(fact, dict)
            }
            if len(proven_by_index) != len(proven_entries):
                failures.append(
                    f"{where}.recorded_skips.{variant}.{stream_name}: duplicate skip indices"
                )
                continue
            if set(proven_by_index) != set(expected_entries):
                missing = sorted(set(expected_entries) - set(proven_by_index))
                extra = sorted(set(proven_by_index) - set(expected_entries))
                failures.append(
                    f"{where}.recorded_skips.{variant}.{stream_name}: skip coverage mismatch "
                    f"(missing indices {missing}; unproven extra indices {extra})"
                )
                continue
            for index, entry in sorted(expected_entries.items()):
                fact = proven_by_index[index]
                _verify_skip_fact(contract, manifest, failures, f"{where}.recorded_skips."
                                  f"{variant}.{stream_name}[index {index}]", entry, fact)
    if rerun_root is not None:
        _rerun_skip_scans(contract, manifest, failures, rerun_root, timeout)


def _verify_skip_fact(
    contract: dict[str, Any],
    manifest: dict[str, Any],
    failures: list[str],
    where: str,
    entry: dict[str, Any],
    fact: dict[str, Any],
) -> None:
    """One recorded skip must be backed by a real non-allowlisted hit."""
    if entry.get("seed") != fact.get("seed") or entry.get("reason") != fact.get("reason"):
        failures.append(f"{where}: index/seed/reason != recorded skip")
    if fact.get("reason") != SKIP_REASON_TREE:
        failures.append(f"{where}: reason must be {SKIP_REASON_TREE!r}")
    hits = fact.get("hit_paths")
    count = fact.get("non_allowlisted_hit_count")
    if not isinstance(hits, list) or not hits:
        failures.append(
            f"{where}: hit_paths must record the actual pinned-tree hits"
        )
    if not _is_plain_int(count) or count < 1:
        failures.append(
            f"{where}: a legitimate collision skip requires >= 1 non-allowlisted hit"
        )
    allowlist = set(manifest.get("allowlist_paths_exact") or [])
    if isinstance(hits, list) and any(
        path in allowlist for path in hits if isinstance(path, str)
    ):
        failures.append(
            f"{where}: hits inside the exact allowlist do not prove a tree collision"
        )


def _rerun_skip_scans(
    contract: dict[str, Any],
    manifest: dict[str, Any],
    failures: list[str],
    rerun_root: Path,
    timeout: float,
) -> None:
    """Re-run the pinned scan for every recorded skip (fail-closed, M-3).

    This is the anti-bias proof: a candidate that does NOT actually collide
    in the pinned tree can never carry a legitimate SEED_COLLISION_TREE
    skip, even when contract, record and manifest were edited
    self-consistently.
    """
    pin = contract.get("seed_generation", {}).get("exclusion_tree_pin")
    exclusions = tuple(sorted(contract.get("seed_generation", {}).get("scan_allowlist_paths_exact") or []))
    anchor = contract.get("seed_generation", {}).get("anchor", DEFAULT_ANCHOR)
    recorded = manifest.get("recorded_skips")
    if not isinstance(recorded, dict):
        return
    for variant, streams in recorded.items():
        if not isinstance(streams, dict):
            continue
        for stream_name, proven in streams.items():
            if not isinstance(proven, list):
                continue
            for position, fact in enumerate(proven):
                if not isinstance(fact, dict):
                    continue
                index = fact.get("index")
                seed = fact.get("seed")
                where = (
                    f"collision_scan_manifest.recorded_skips.{variant}.{stream_name}[{position}]"
                )
                derived_failures = check_skip_entry(
                    {"index": index, "seed": seed, "reason": fact.get("reason")},
                    anchor, variant, where,
                )
                failures.extend(derived_failures)
                try:
                    result = literal_tree_collision_scan(
                        rerun_root, [seed], exclude_paths=exclusions,
                        pinned_commit=pin, timeout=timeout,
                    )
                except TreeScanError as exc:
                    failures.append(
                        f"{where}: collision-skip proof BLOCKED (scan error: {exc})"
                    )
                    continue
                if result["collision_count"] < 1:
                    failures.append(
                        f"{where}: re-run of the pinned-tree scan found NO collision for skip "
                        f"seed {seed} (index {index}) — the recorded skip is not a legitimate "
                        "SEED_COLLISION_TREE (FREEZE_GATE_FAIL, anti-bias integrity)"
                    )
