"""Versioned machine-readable freeze/dispatch contract for NANOLAB_REPRO_V0_2.

Pre-freeze hardening R4 (WO-NL5-V02-PREFREEZE-HARDENING-R4), repairs audit
finding F1 (fail-open freeze consistency gate) and F4 (integer rounding /
scientific wording drift).

The machine-readable contract JSON is the SINGLE authoritative source for
freeze/dispatch. It mechanically binds: rule/revision + scientific subject
pins; variant set with primary/control classification; per-variant N, N_min
and the exact integer rounding policy; confirmatory + frozen replacement
pools; seed anchor/algorithm with consumed indices and the replacement
cursor; bootstrap seeds/configuration; historical exclusions with the
immutable exclusion-tree pin and the exact path allowlist; per-cell paired
attempt/replacement quotas with the total run cap and wall cap; analyzer /
convention / environment pins; feasibility planning evidence; and execution
plan cardinalities.

EVERYTHING is validated fail-closed: malformed JSON, missing or extra
fields, wrong types (including ``bool`` where an integer is required),
out-of-range or duplicate seeds, stale digests, missing/extra variants,
N/N_min/quota/wall mismatches, contradictory or duplicated protocol
declarations, unknown revisions and read errors all produce
``FREEZE_GATE_FAIL`` / :class:`ContractError` — never a silent PASS.

The dispatch entrypoint (:func:`build_execution_plan`) re-runs the full
gate before producing a plan; there is no code path that returns an
execution plan from an unvalidated contract.

CLI (repository root; on hosts where a global ``scripts`` package shadows
the repository namespace use ``PYTHONPATH=scripts``)::

    python3 -m scripts.nl5.repro_v02_freeze_contract gate \
        --contract <contract.json> --protocol <candidate.md> [--record <record.json>]
    python3 -m scripts.nl5.repro_v02_freeze_contract plan \
        --contract <contract.json> --protocol <candidate.md> --record <record.json>

Exit codes: 0 = PASS / plan produced; 3 = FREEZE_GATE_FAIL (failures list
printed); 4 = contract/read error (fail-closed).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from nl5.repro_v02_seeds import (
    BOOTSTRAP_RESAMPLES,
    CONTROL_VARIANTS,
    DEFAULT_ANCHOR,
    HISTORICAL_SEEDS_V1,
    PRIMARY_VARIANTS,
    RULE_ID,
    bootstrap_label,
    derive_seed,
    replay_variant_stream,
)

CONTRACT_SCHEMA_VERSION = 1
CONTRACT_KIND = "nanolab_v02_freeze_contract"
KNOWN_CONTRACT_REVISIONS = ("r4",)

PRIMARY_N = 64
CONTROL_N = 10
REPLACEMENT_RUNS_PER_PAIR = 2  # paired legs: author + external platform
WALL_HOURS_PER_PLATFORM = 560
N_MIN_RATIO = 0.80
REPLACEMENT_RATIO = 0.20
SEED_MAX = 2**31

# ---------------------------------------------------------------------------
# F4: one explicitly named integer rounding policy for every surface.
# ---------------------------------------------------------------------------

INTEGER_ROUNDING_POLICY = {
    "name": "ceil-nmin-floor-replacement-pairs-v1",
    "n_min_rule": "n_min_cell = ceil(0.80 * N_cell)  (literal '>= 80%' semantics)",
    "replacement_quota_rule": (
        "replacement_quota_pairs = floor(0.20 * N_cell) per variant cell "
        "(literal '<= 20%' semantics, counted in paired identities)"
    ),
    "replacement_runs_per_pair": REPLACEMENT_RUNS_PER_PAIR,
    "total_cap_rule": (
        "replacement_runs_cap = sum over variants of "
        "replacement_runs_per_pair * quota_pairs(variant); "
        "max_runs = confirmatory_runs + replacement_runs_cap"
    ),
    "note": "51/64 = 79.6875% is NOT >= 80%; the ceil rule yields N_min = 52. "
    "60/296 = 20.27% is NOT <= 20%; per-cell floor quotas yield a 56-run cap.",
}


def n_min_cell(n_cell: int) -> int:
    """F4 policy: literal '>= 80%' — smallest integer satisfying the bound."""
    if not isinstance(n_cell, int) or isinstance(n_cell, bool) or n_cell <= 0:
        raise ValueError("n_cell must be a positive integer")
    return math.ceil(N_MIN_RATIO * n_cell)


def replacement_quota_pairs(n_cell: int) -> int:
    """F4 policy: literal '<= 20%' — largest integer satisfying the bound."""
    if not isinstance(n_cell, int) or isinstance(n_cell, bool) or n_cell <= 0:
        raise ValueError("n_cell must be a positive integer")
    return math.floor(REPLACEMENT_RATIO * n_cell)


def derive_budget(variant_counts: dict[str, int] | None = None) -> dict[str, int]:
    """Budget derived ONLY from the integer policy (single source, F4)."""
    counts = (
        dict(variant_counts)
        if variant_counts is not None
        else {v: (PRIMARY_N if v in PRIMARY_VARIANTS else CONTROL_N) for v in PRIMARY_VARIANTS + CONTROL_VARIANTS}
    )
    confirmatory = sum(2 * counts[v] for v in counts)
    replacement_cap = sum(REPLACEMENT_RUNS_PER_PAIR * replacement_quota_pairs(counts[v]) for v in counts)
    return {
        "confirmatory_runs": confirmatory,
        "replacement_runs_cap": replacement_cap,
        "max_runs": confirmatory + replacement_cap,
        "wall_hours_per_platform": WALL_HOURS_PER_PLATFORM,
    }


class ContractError(RuntimeError):
    """Fail-closed contract error (malformed input, read error, gate FAIL)."""


# ---------------------------------------------------------------------------
# Protocol text parsing (single authoritative declaration, F1).
# ---------------------------------------------------------------------------

CARDINALITY_RE = re.compile(
    r"(?m)^[^`\n]*?0b\s*=\s*(\d+)\s*,\s*32b\s*=\s*(\d+)\s*,\s*"
    r"11b\s*=\s*(\d+)\s*,\s*53b\s*=\s*(\d+)[^\n]*$"
)
MACHINE_BLOCK_MARKER = "machine-contract-v1"

MACHINE_BLOCK_KEYS = (
    "rule_id",
    "candidate_revision",
    "anchor",
    "n_0b",
    "n_32b",
    "n_11b",
    "n_53b",
    "n_min_primary",
    "n_min_control",
    "replacement_quota_pairs_primary",
    "replacement_quota_pairs_control",
    "confirmatory_runs",
    "replacement_runs_cap",
    "max_runs",
    "wall_hours_per_platform",
    "selected_n",
    "headroom_ratio",
    "bootstrap_resamples",
    "exclusion_list_size",
    "exclusion_tree_pin",
    "integer_policy_name",
)


def parse_protocol_cardinalities(protocol_text: str) -> dict[str, int]:
    """All four cardinalities; duplicated/contradictory declarations fail."""
    matches = CARDINALITY_RE.findall(protocol_text)
    if not matches:
        raise ContractError("protocol cardinality contract line not found")
    if len(matches) > 1:
        raise ContractError(
            f"protocol declares {len(matches)} cardinality lines; exactly one is allowed"
        )
    values = [int(v) for v in matches[0]]
    return dict(zip(("0b", "32b", "11b", "53b"), values))


def parse_protocol_machine_block(protocol_text: str) -> dict[str, str]:
    """Parse THE authoritative machine block from the candidate document.

    The block is a fenced code block containing the ``machine-contract-v1``
    marker line and ``key = value`` lines. Zero or multiple such blocks are a
    contract error (contradicting authoritative declarations are forbidden).
    """
    blocks: list[dict[str, str]] = []
    for fence in re.finditer(r"```[^\n]*\n(.*?)```", protocol_text, re.DOTALL):
        body = fence.group(1)
        if MACHINE_BLOCK_MARKER not in body:
            continue
        fields: dict[str, str] = {}
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            fields[key.strip()] = value.strip()
        blocks.append(fields)
    if not blocks:
        raise ContractError("protocol machine-contract-v1 block not found")
    if len(blocks) > 1:
        raise ContractError(
            f"protocol contains {len(blocks)} machine-contract-v1 blocks; exactly one is allowed"
        )
    block = blocks[0]
    missing = [key for key in MACHINE_BLOCK_KEYS if key not in block]
    if missing:
        raise ContractError(f"protocol machine block missing keys: {missing}")
    extra = sorted(set(block) - set(MACHINE_BLOCK_KEYS))
    if extra:
        raise ContractError(f"protocol machine block has unknown keys: {extra}")
    return block


# ---------------------------------------------------------------------------
# Strict value checks (fail-closed, F1).
# ---------------------------------------------------------------------------


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _check_seed_value(seed: Any, label: str, failures: list[str]) -> None:
    if not _is_int(seed):
        failures.append(f"{label}: seed is not an integer (got {type(seed).__name__})")
        return
    if not 0 <= seed < SEED_MAX:
        failures.append(f"{label}: seed {seed} outside int32-positive range [0, 2^31)")


def _expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _require_keys(obj: Any, required: tuple[str, ...], where: str, failures: list[str]) -> None:
    if not isinstance(obj, dict):
        failures.append(f"{where}: expected object")
        return
    missing = [key for key in required if key not in obj]
    extra = sorted(set(obj) - set(required))
    if missing:
        failures.append(f"{where}: missing keys {missing}")
    if extra:
        failures.append(f"{where}: unknown extra keys {extra}")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logical_record_digest(seeds_by_variant: dict[str, list[int]], bootstrap_seeds: dict[str, int],
                          anchor: str, variant_counts: dict[str, int]) -> str:
    canonical = json.dumps(
        {
            "seeds": seeds_by_variant,
            "bootstrap_seeds": bootstrap_seeds,
            "anchor": anchor,
            "variant_counts": variant_counts,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# The R4 freeze/dispatch gate (F1).
# ---------------------------------------------------------------------------

_TOP_KEYS = (
    "schema_version",
    "kind",
    "contract_revision",
    "rule_id",
    "scientific_subject",
    "variants",
    "integer_rounding_policy",
    "seed_generation",
    "confirmatory_seeds",
    "bootstrap",
    "replacement",
    "historical_exclusions",
    "run_budget",
    "analyzer_pins",
    "feasibility_planning",
    "environment_pins",
)

_SUBJECT_KEYS = (
    "candidate_doc_path",
    "candidate_revision",
    "seed_record_path",
    "seed_record_file_sha256",
    "seed_record_logical_sha256",
    "freeze_status",
)
_GENERATION_KEYS = (
    "anchor",
    "algorithm",
    "exclusion_tree_pin",
    "generation_revision",
    "scan_allowlist_paths_exact",
    "indices_consumed",
    "next_candidate_index",
)
_BOOTSTRAP_KEYS = ("resamples", "scheme", "rng", "seeds", "indices")
_REPLACEMENT_KEYS = (
    "allowed_only_for",
    "quota_pairs_per_variant",
    "pools",
    "attempt_id_rule",
    "paired_semantics",
)
_EXCLUSION_KEYS = ("list_size", "seeds")
_BUDGET_KEYS = ("confirmatory_runs", "replacement_runs_cap", "max_runs", "wall_hours_per_platform")
_ANALYZER_KEYS = ("package", "package_version", "analyzer", "quantile_method", "delta")
_FEASIBILITY_KEYS = ("n_grid", "selected_n", "headroom_ratio", "evidence_path", "evidence_sha256")
_ENVIRONMENT_KEYS = (
    "engine_source",
    "engine_commit",
    "cmake_build_type",
    "double",
    "cuda",
    "mpi",
    "platforms",
)
_POLICY_KEYS = (
    "name",
    "n_min_rule",
    "replacement_quota_rule",
    "replacement_runs_per_pair",
    "total_cap_rule",
)
_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_contract(path: Path | str) -> dict[str, Any]:
    """Load the contract JSON; any read/parse problem fails closed."""
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"contract read error {path}: {exc}") from exc
    try:
        contract = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(f"contract is not valid JSON ({path}): {exc}") from exc
    if not isinstance(contract, dict):
        raise ContractError("contract must be a JSON object")
    return contract


def load_seed_record(path: Path | str) -> dict[str, Any]:
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"seed record read error {path}: {exc}") from exc
    try:
        record = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(f"seed record is not valid JSON ({path}): {exc}") from exc
    if not isinstance(record, dict):
        raise ContractError("seed record must be a JSON object")
    return record


def validate_freeze_contract(
    contract: dict[str, Any],
    protocol_text: str | None = None,
    seed_record: dict[str, Any] | None = None,
    repo_root: Path | str | None = None,
    require_record: bool = True,
) -> dict[str, Any]:
    """Full fail-closed validation. Returns a report; ``gate`` is PASS only
    when ``failures`` is empty. Any malformed/missing/extra/mismatch/unknown
    input lands in ``failures`` — the caller must treat FAIL as terminal."""
    failures: list[str] = []

    _require_keys(contract, _TOP_KEYS, "contract", failures)
    if failures:
        return _report(failures, contract)

    if contract["schema_version"] != CONTRACT_SCHEMA_VERSION:
        failures.append(f"contract schema_version {contract['schema_version']!r} != {CONTRACT_SCHEMA_VERSION}")
    if contract["kind"] != CONTRACT_KIND:
        failures.append(f"contract kind {contract['kind']!r} != {CONTRACT_KIND!r}")
    if contract["contract_revision"] not in KNOWN_CONTRACT_REVISIONS:
        failures.append(
            f"unknown contract_revision {contract['contract_revision']!r}; known: {KNOWN_CONTRACT_REVISIONS}"
        )
    if contract["rule_id"] != RULE_ID:
        failures.append(f"contract rule_id {contract['rule_id']!r} != {RULE_ID!r}")

    _validate_subject(contract["scientific_subject"], failures)
    _validate_variants(contract["variants"], failures)
    _validate_policy(contract["integer_rounding_policy"], failures)
    _validate_generation(contract["seed_generation"], contract["variants"], failures)
    confirmatory = _validate_seed_arrays(contract, failures)
    _validate_bootstrap(contract["bootstrap"], contract["variants"], confirmatory, failures)
    _validate_replacement(contract, confirmatory, failures)
    _validate_exclusions(contract["historical_exclusions"], failures)
    _validate_budget(contract, failures)
    _validate_analyzer(contract["analyzer_pins"], failures)
    _validate_feasibility(contract["feasibility_planning"], failures)
    _validate_environment(contract["environment_pins"], failures)

    if protocol_text is not None:
        _validate_protocol(contract, protocol_text, failures)

    if seed_record is not None:
        _validate_record_binding(contract, seed_record, failures)
    elif require_record:
        failures.append("seed record not provided: freeze/dispatch requires the exact record binding")

    if repo_root is not None and contract["scientific_subject"].get("seed_record_file_sha256"):
        record_path = (Path(repo_root) / contract["scientific_subject"]["seed_record_path"])
        if not record_path.is_file():
            failures.append(f"seed record file missing on disk: {record_path}")
        else:
            actual = _sha256_file(record_path)
            if actual != contract["scientific_subject"]["seed_record_file_sha256"]:
                failures.append(
                    f"seed record file sha256 mismatch: file {actual} != contract "
                    f"{contract['scientific_subject']['seed_record_file_sha256']}"
                )

    return _report(failures, contract)


def _report(failures: list[str], contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "r4_freeze_contract_gate",
        "contract_revision": contract.get("contract_revision"),
        "gate": "PASS" if not failures else "FREEZE_GATE_FAIL",
        "failures": failures,
        "integer_rounding_policy": INTEGER_ROUNDING_POLICY["name"],
        "budget": derive_budget(
            {v: spec.get("n") for v, spec in contract["variants"].items()}
        ) if isinstance(contract.get("variants"), dict) and contract["variants"] and all(
            isinstance(spec, dict) and _is_int(spec.get("n")) for spec in contract["variants"].values()
        ) else None,
    }


def _validate_subject(subject: Any, failures: list[str]) -> None:
    _require_keys(subject, _SUBJECT_KEYS, "scientific_subject", failures)
    if not isinstance(subject, dict) or failures:
        return
    for key in ("candidate_doc_path", "seed_record_path"):
        value = subject[key]
        if not isinstance(value, str) or not value:
            failures.append(f"scientific_subject.{key}: must be a non-empty string")
        elif value.startswith("/") or ".." in Path(value).parts:
            failures.append(f"scientific_subject.{key}: must be a repository-relative path")
    if not _is_int(subject["candidate_revision"]) and not isinstance(subject["candidate_revision"], str):
        failures.append("scientific_subject.candidate_revision: must be string or int")
    if subject["seed_record_file_sha256"] is not None:
        if not isinstance(subject["seed_record_file_sha256"], str) or not _SHA256_RE.match(
            subject["seed_record_file_sha256"]
        ):
            failures.append("scientific_subject.seed_record_file_sha256: must be 64-hex sha256 or null")
    if not isinstance(subject["seed_record_logical_sha256"], str) or not _SHA256_RE.match(
        subject["seed_record_logical_sha256"]
    ):
        failures.append("scientific_subject.seed_record_logical_sha256: must be 64-hex sha256")
    if subject["freeze_status"] not in ("NOT_FROZEN", "FROZEN"):
        failures.append("scientific_subject.freeze_status must be NOT_FROZEN or FROZEN")


def _validate_variants(variants: Any, failures: list[str]) -> None:
    if not isinstance(variants, dict):
        failures.append("variants: expected object")
        return
    expected_roles = {"0b": "primary", "32b": "primary", "11b": "control", "53b": "control"}
    if set(variants) != set(expected_roles):
        failures.append(
            f"variants: set {sorted(variants)} != expected {sorted(expected_roles)} "
            "(missing or extra variants are fail-closed)"
        )
        return
    for variant, role in expected_roles.items():
        spec = variants[variant]
        _require_keys(spec, ("role", "n", "n_min"), f"variants.{variant}", failures)
        if not isinstance(spec, dict):
            continue
        if spec.get("role") != role:
            failures.append(f"variants.{variant}.role must be {role!r}")
        expected_n = PRIMARY_N if role == "primary" else CONTROL_N
        if spec.get("n") != expected_n or not _is_int(spec.get("n")):
            failures.append(f"variants.{variant}.n must be {expected_n}")
            continue
        expected_n_min = n_min_cell(expected_n)
        if spec.get("n_min") != expected_n_min or not _is_int(spec.get("n_min")):
            failures.append(
                f"variants.{variant}.n_min must be ceil(0.80*{expected_n}) = {expected_n_min} "
                f"(integer policy; {spec.get('n_min')!r} is not the policy derivation)"
            )


def _validate_policy(policy: Any, failures: list[str]) -> None:
    _require_keys(policy, _POLICY_KEYS, "integer_rounding_policy", failures)
    if not isinstance(policy, dict):
        return
    if policy.get("name") != INTEGER_ROUNDING_POLICY["name"]:
        failures.append(
            f"integer_rounding_policy.name {policy.get('name')!r} != "
            f"{INTEGER_ROUNDING_POLICY['name']!r} (unknown or drifted policy)"
        )
    for key in ("n_min_rule", "replacement_quota_rule", "total_cap_rule"):
        if not isinstance(policy.get(key), str) or not policy.get(key):
            failures.append(f"integer_rounding_policy.{key}: must be a non-empty string")
    if policy.get("replacement_runs_per_pair") != REPLACEMENT_RUNS_PER_PAIR:
        failures.append(
            f"integer_rounding_policy.replacement_runs_per_pair must be {REPLACEMENT_RUNS_PER_PAIR}"
        )


def _validate_generation(generation: Any, variants: Any, failures: list[str]) -> None:
    _require_keys(generation, _GENERATION_KEYS, "seed_generation", failures)
    if not isinstance(generation, dict) or not isinstance(variants, dict):
        return
    if generation.get("anchor") != DEFAULT_ANCHOR:
        failures.append(f"seed_generation.anchor {generation.get('anchor')!r} != {DEFAULT_ANCHOR!r}")
    if not isinstance(generation.get("algorithm"), str) or not generation.get("algorithm"):
        failures.append("seed_generation.algorithm: must be a non-empty string")
    pin = generation.get("exclusion_tree_pin")
    if not isinstance(pin, str) or not _HEX40_RE.match(pin or ""):
        failures.append("seed_generation.exclusion_tree_pin: must be a full 40-hex commit SHA")
    if not isinstance(generation.get("generation_revision"), str) or not generation.get("generation_revision"):
        failures.append("seed_generation.generation_revision: must be a non-empty string")
    allowlist = generation.get("scan_allowlist_paths_exact")
    if not isinstance(allowlist, list) or not allowlist or not all(
        isinstance(p, str) and p and not p.startswith("/") and ".." not in Path(p).parts for p in allowlist
    ):
        failures.append(
            "seed_generation.scan_allowlist_paths_exact: must be a non-empty list of exact "
            "repository-relative paths (no prefixes, no traversal)"
        )
    for key in ("indices_consumed", "next_candidate_index"):
        cursors = generation.get(key)
        if not isinstance(cursors, dict) or set(cursors) != set(variants):
            failures.append(f"seed_generation.{key}: must cover exactly the contract variants")
            continue
        for variant, value in cursors.items():
            if not _is_int(value) or value < 1:
                failures.append(f"seed_generation.{key}.{variant}: must be a positive integer")
    consumed = generation.get("indices_consumed")
    nxt = generation.get("next_candidate_index")
    if isinstance(consumed, dict) and isinstance(nxt, dict):
        for variant in set(consumed) & set(nxt):
            if _is_int(consumed.get(variant)) and _is_int(nxt.get(variant)):
                if nxt[variant] != consumed[variant] + 1:
                    failures.append(
                        f"seed_generation cursor {variant}: next_candidate_index "
                        f"{nxt[variant]} != indices_consumed {consumed[variant]} + 1"
                    )
            if _is_int(consumed.get(variant)) and isinstance(variants, dict):
                n = variants.get(variant, {}).get("n")
                if _is_int(n) and consumed[variant] < n:
                    failures.append(
                        f"seed_generation.indices_consumed.{variant} {consumed[variant]} < N {n}"
                    )


def _validate_seed_arrays(contract: dict[str, Any], failures: list[str]) -> dict[str, list[int]]:
    arrays = contract.get("confirmatory_seeds")
    variants = contract.get("variants")
    if not isinstance(arrays, dict) or not isinstance(variants, dict):
        failures.append("confirmatory_seeds: expected object keyed by variant")
        return {}
    if set(arrays) != set(variants):
        failures.append(
            f"confirmatory_seeds: variant set {sorted(arrays)} != contract variants {sorted(variants)}"
        )
        return {}
    result: dict[str, list[int]] = {}
    for variant, stream in arrays.items():
        n = variants.get(variant, {}).get("n") if isinstance(variants.get(variant), dict) else None
        if not isinstance(stream, list):
            failures.append(f"confirmatory_seeds.{variant}: expected array")
            continue
        if not _is_int(n) or len(stream) != n:
            failures.append(f"confirmatory_seeds.{variant}: length {len(stream)} != N {n}")
        for position, seed in enumerate(stream):
            _check_seed_value(seed, f"confirmatory_seeds.{variant}[{position}]", failures)
        if len(set(stream)) != len(stream):
            dupes = sorted({s for s in stream if _is_int(s) and stream.count(s) > 1})
            failures.append(f"confirmatory_seeds.{variant}: duplicate seeds {dupes}")
        result[variant] = stream
    seen: dict[int, str] = {}
    for variant, stream in result.items():
        for seed in stream:
            if seed in seen:
                failures.append(f"confirmatory seed {seed} duplicated across {seen[seed]} and {variant}")
            else:
                seen[seed] = variant
    return result


def _validate_bootstrap(bootstrap: Any, variants: Any, confirmatory: dict[str, list[int]],
                        failures: list[str]) -> None:
    _require_keys(bootstrap, _BOOTSTRAP_KEYS, "bootstrap", failures)
    if not isinstance(bootstrap, dict) or not isinstance(variants, dict):
        return
    if bootstrap.get("resamples") != BOOTSTRAP_RESAMPLES or not _is_int(bootstrap.get("resamples")):
        failures.append(f"bootstrap.resamples must be {BOOTSTRAP_RESAMPLES}")
    if bootstrap.get("scheme") != "PAIRED":
        failures.append("bootstrap.scheme must be PAIRED")
    if bootstrap.get("rng") != "python random.Random(bootstrap_seed_v)":
        failures.append("bootstrap.rng must be pinned to python random.Random(bootstrap_seed_v)")
    seeds = bootstrap.get("seeds")
    indices = bootstrap.get("indices")
    if not isinstance(seeds, dict) or set(seeds) != set(variants):
        failures.append("bootstrap.seeds must cover exactly the contract variants (missing bootstrap is fail-closed)")
        return
    if not isinstance(indices, dict) or set(indices) != set(variants):
        failures.append("bootstrap.indices must cover exactly the contract variants")
        return
    taken = {s for stream in confirmatory.values() for s in stream}
    for variant in seeds:
        seed = seeds[variant]
        _check_seed_value(seed, f"bootstrap.seeds.{variant}", failures)
        if _is_int(seed):
            if seed in taken:
                failures.append(f"bootstrap.seeds.{variant} {seed} collides with a confirmatory identity")
            if _is_int(seed) and seed in HISTORICAL_SEEDS_V1:
                failures.append(f"bootstrap.seeds.{variant} {seed} is a historical R1 seed")
            index = indices[variant]
            if not _is_int(index) or index < 0:
                failures.append(f"bootstrap.indices.{variant}: must be a non-negative integer")
            elif derive_seed(DEFAULT_ANCHOR, bootstrap_label(variant, index)) != seed:
                failures.append(
                    f"bootstrap.seeds.{variant} does not regenerate from its recorded index {index}"
                )
        if _is_int(seed):
            taken.add(seed)
    if len(set(seeds.values())) != len(seeds):
        failures.append("bootstrap seeds are not unique across variants")


def _validate_replacement(contract: dict[str, Any], confirmatory: dict[str, list[int]],
                          failures: list[str]) -> None:
    replacement = contract.get("replacement")
    variants = contract.get("variants")
    _require_keys(replacement, _REPLACEMENT_KEYS, "replacement", failures)
    if not isinstance(replacement, dict) or not isinstance(variants, dict):
        return
    if replacement.get("allowed_only_for") != "FAILED_TECHNICAL":
        failures.append(
            "replacement.allowed_only_for must be FAILED_TECHNICAL "
            "(never outcome-driven seed selection)"
        )
    for key in ("attempt_id_rule", "paired_semantics"):
        if not isinstance(replacement.get(key), str) or not replacement.get(key):
            failures.append(f"replacement.{key}: must be a non-empty string")
    quotas = replacement.get("quota_pairs_per_variant")
    pools = replacement.get("pools")
    if not isinstance(quotas, dict) or set(quotas) != set(variants):
        failures.append("replacement.quota_pairs_per_variant must cover exactly the contract variants")
        return
    if not isinstance(pools, dict) or set(pools) != set(variants):
        failures.append("replacement.pools must cover exactly the contract variants")
        return
    taken = {s for stream in confirmatory.values() for s in stream}
    bootstrap = contract.get("bootstrap")
    if isinstance(bootstrap, dict) and isinstance(bootstrap.get("seeds"), dict):
        taken |= {s for s in bootstrap["seeds"].values() if _is_int(s)}
    for variant in quotas:
        quota = quotas[variant]
        n = variants[variant].get("n") if isinstance(variants.get(variant), dict) else None
        if not _is_int(quota) or not _is_int(n) or quota != replacement_quota_pairs(n):
            failures.append(
                f"replacement.quota_pairs_per_variant.{variant} must be "
                f"floor(0.20*N) = {replacement_quota_pairs(n) if _is_int(n) else '?'}"
            )
            continue
        pool = pools[variant]
        _require_keys(pool, ("seeds", "skipped", "start_index", "next_candidate_index"),
                      f"replacement.pools.{variant}", failures)
        if not isinstance(pool, dict):
            continue
        pool_seeds = pool.get("seeds")
        if not isinstance(pool_seeds, list):
            failures.append(f"replacement.pools.{variant}.seeds: expected array")
            continue
        if len(pool_seeds) != quota:
            failures.append(
                f"replacement.pools.{variant}: {len(pool_seeds)} identities != quota {quota} "
                "(pool must be pre-generated to the full per-cell quota)"
            )
        for position, seed in enumerate(pool_seeds):
            _check_seed_value(seed, f"replacement.pools.{variant}.seeds[{position}]", failures)
            if _is_int(seed):
                if seed in taken:
                    failures.append(
                        f"replacement.pools.{variant} seed {seed} collides with a taken identity"
                    )
                if seed in HISTORICAL_SEEDS_V1:
                    failures.append(f"replacement.pools.{variant} seed {seed} is a historical R1 seed")
                taken.add(seed)
        if len(set(pool_seeds)) != len(pool_seeds):
            failures.append(f"replacement.pools.{variant}: duplicate identities within pool")
        start = pool.get("start_index")
        nxt = pool.get("next_candidate_index")
        generation = contract.get("seed_generation")
        if _is_int(start) and isinstance(generation, dict):
            expected_start = generation.get("next_candidate_index", {}).get(variant)
            if start != expected_start:
                failures.append(
                    f"replacement.pools.{variant}.start_index {start} != seed_generation "
                    f"next_candidate_index {expected_start} (raw N+1 restarts are forbidden, F3)"
                )
        if _is_int(start) and _is_int(nxt):
            expected_next = start + quota + len(pool.get("skipped") or [])
            if nxt != expected_next:
                failures.append(
                    f"replacement.pools.{variant}: next_candidate_index {nxt} != "
                    f"start {start} + quota {quota} + skips {len(pool.get('skipped') or [])}"
                )


def _validate_exclusions(exclusions: Any, failures: list[str]) -> None:
    _require_keys(exclusions, _EXCLUSION_KEYS, "historical_exclusions", failures)
    if not isinstance(exclusions, dict):
        return
    seeds = exclusions.get("seeds")
    if not isinstance(seeds, list):
        failures.append("historical_exclusions.seeds: expected array")
        return
    if len(seeds) != len(HISTORICAL_SEEDS_V1):
        failures.append(
            f"historical_exclusions.seeds size {len(seeds)} != frozen list {len(HISTORICAL_SEEDS_V1)}"
        )
    if set(seeds) != set(HISTORICAL_SEEDS_V1):
        failures.append("historical_exclusions.seeds content != frozen 34-seed R1 exclusion list")
    if seeds != sorted(seeds):
        failures.append("historical_exclusions.seeds must be sorted (canonical form)")
    if exclusions.get("list_size") != len(HISTORICAL_SEEDS_V1):
        failures.append(f"historical_exclusions.list_size must be {len(HISTORICAL_SEEDS_V1)}")


def _validate_budget(contract: dict[str, Any], failures: list[str]) -> None:
    budget = contract.get("run_budget")
    _require_keys(budget, _BUDGET_KEYS, "run_budget", failures)
    if not isinstance(budget, dict):
        return
    expected = derive_budget(
        {v: spec.get("n") for v, spec in contract["variants"].items()}
    )
    for key, value in expected.items():
        actual = budget.get(key)
        if not _is_int(actual) or actual != value:
            failures.append(f"run_budget.{key} {actual!r} != policy derivation {value}")
    if _is_int(budget.get("wall_hours_per_platform")) and budget["wall_hours_per_platform"] <= 0:
        failures.append("run_budget.wall_hours_per_platform must be positive")
    if _is_int(budget.get("max_runs")) and _is_int(budget.get("confirmatory_runs")):
        if budget["max_runs"] < budget["confirmatory_runs"]:
            failures.append("run_budget.max_runs < confirmatory_runs")


def _validate_analyzer(analyzer: Any, failures: list[str]) -> None:
    _require_keys(analyzer, _ANALYZER_KEYS, "analyzer_pins", failures)
    if not isinstance(analyzer, dict):
        return
    for key in ("package", "package_version", "analyzer"):
        if not isinstance(analyzer.get(key), str) or not analyzer.get(key):
            failures.append(f"analyzer_pins.{key}: must be a non-empty string")
    if analyzer.get("quantile_method") != "linear":
        failures.append("analyzer_pins.quantile_method must be 'linear' (pinned)")
    if str(analyzer.get("delta")) != "0.5":
        failures.append("analyzer_pins.delta must be '0.5' (fixed a priori)")


def _validate_feasibility(feasibility: Any, failures: list[str]) -> None:
    _require_keys(feasibility, _FEASIBILITY_KEYS, "feasibility_planning", failures)
    if not isinstance(feasibility, dict):
        return
    grid = feasibility.get("n_grid")
    if not isinstance(grid, list) or not all(_is_int(v) and v > 0 for v in grid) or len(grid) != 6:
        failures.append("feasibility_planning.n_grid must be the declared 6-value grid")
    if grid and sorted(grid) != grid:
        failures.append("feasibility_planning.n_grid must be sorted ascending")
    if feasibility.get("selected_n") not in (grid or []):
        failures.append("feasibility_planning.selected_n must be a member of the declared grid")
    ratio = feasibility.get("headroom_ratio")
    if not isinstance(ratio, (int, float)) or isinstance(ratio, bool) or abs(ratio - 0.80) > 1e-9:
        failures.append("feasibility_planning.headroom_ratio must be 0.80")
    if not isinstance(feasibility.get("evidence_path"), str) or not feasibility.get("evidence_path"):
        failures.append("feasibility_planning.evidence_path: must be a non-empty string")
    if feasibility.get("evidence_sha256") is not None and not (
        isinstance(feasibility.get("evidence_sha256"), str)
        and _SHA256_RE.match(feasibility["evidence_sha256"])
    ):
        failures.append("feasibility_planning.evidence_sha256: must be 64-hex sha256 or null")


def _validate_environment(environment: Any, failures: list[str]) -> None:
    _require_keys(environment, _ENVIRONMENT_KEYS, "environment_pins", failures)
    if not isinstance(environment, dict):
        return
    if not isinstance(environment.get("engine_source"), str) or not environment.get("engine_source"):
        failures.append("environment_pins.engine_source: must be a non-empty string")
    commit = environment.get("engine_commit")
    if not isinstance(commit, str) or not _HEX40_RE.match(commit or ""):
        failures.append("environment_pins.engine_commit: must be a full 40-hex commit SHA")
    for key, expected in (
        ("cmake_build_type", "Release"),
        ("double", "ON"),
        ("cuda", "OFF"),
        ("mpi", "OFF"),
    ):
        if environment.get(key) != expected:
            failures.append(f"environment_pins.{key} must be {expected!r}")
    if not isinstance(environment.get("platforms"), str) or not environment.get("platforms"):
        failures.append("environment_pins.platforms: must be a non-empty string")


def _validate_protocol(contract: dict[str, Any], protocol_text: str, failures: list[str]) -> None:
    variants = contract["variants"]
    if not isinstance(variants, dict) or set(variants) != {"0b", "32b", "11b", "53b"}:
        # Variant-set failures are already recorded; the protocol cross-check
        # below needs the exact expected set to be meaningful.
        failures.append("protocol cross-check skipped: contract variant set invalid")
        return
    try:
        counts = parse_protocol_cardinalities(protocol_text)
    except ContractError as exc:
        failures.append(f"protocol cardinalities: {exc}")
        counts = None
    if counts is not None:
        for variant, value in counts.items():
            expected = variants[variant]["n"] if isinstance(variants.get(variant), dict) else None
            if value != expected:
                failures.append(f"protocol N for {variant} = {value} != contract {expected}")
    try:
        block = parse_protocol_machine_block(protocol_text)
    except ContractError as exc:
        failures.append(f"protocol machine block: {exc}")
        return
    variants = contract["variants"]
    expected_block = {
        "rule_id": contract["rule_id"],
        "candidate_revision": str(contract["scientific_subject"]["candidate_revision"]),
        "anchor": contract["seed_generation"]["anchor"],
        "n_0b": str(variants["0b"]["n"]),
        "n_32b": str(variants["32b"]["n"]),
        "n_11b": str(variants["11b"]["n"]),
        "n_53b": str(variants["53b"]["n"]),
        "n_min_primary": str(variants["0b"]["n_min"]),
        "n_min_control": str(variants["11b"]["n_min"]),
        "replacement_quota_pairs_primary": str(
            contract["replacement"]["quota_pairs_per_variant"]["0b"]
        ),
        "replacement_quota_pairs_control": str(
            contract["replacement"]["quota_pairs_per_variant"]["11b"]
        ),
        "confirmatory_runs": str(contract["run_budget"]["confirmatory_runs"]),
        "replacement_runs_cap": str(contract["run_budget"]["replacement_runs_cap"]),
        "max_runs": str(contract["run_budget"]["max_runs"]),
        "wall_hours_per_platform": str(contract["run_budget"]["wall_hours_per_platform"]),
        "selected_n": str(contract["feasibility_planning"]["selected_n"]),
        "headroom_ratio": str(contract["feasibility_planning"]["headroom_ratio"]),
        "bootstrap_resamples": str(contract["bootstrap"]["resamples"]),
        "exclusion_list_size": str(contract["historical_exclusions"]["list_size"]),
        "exclusion_tree_pin": contract["seed_generation"]["exclusion_tree_pin"],
        "integer_policy_name": contract["integer_rounding_policy"]["name"],
    }
    for key, expected in expected_block.items():
        actual = block.get(key)
        if actual != expected:
            failures.append(
                f"protocol machine block {key} = {actual!r} != contract {expected!r} "
                "(contradicting authoritative declarations are fail-closed)"
            )
    frozen_phrase = "NOT FROZEN"
    doc_says_frozen_candidate = contract["scientific_subject"]["freeze_status"] == "NOT_FROZEN"
    if doc_says_frozen_candidate and frozen_phrase not in protocol_text:
        failures.append("contract freeze_status NOT_FROZEN but protocol text does not declare NOT FROZEN")
    if not doc_says_frozen_candidate and frozen_phrase in protocol_text:
        failures.append("contract freeze_status FROZEN but protocol text still declares NOT FROZEN")


def _validate_record_binding(contract: dict[str, Any], record: dict[str, Any], failures: list[str]) -> None:
    variants = contract["variants"]
    subject = contract["scientific_subject"]
    if not isinstance(variants, dict) or set(variants) != {"0b", "32b", "11b", "53b"}:
        failures.append("record cross-check skipped: contract variant set invalid")
        return
    if not isinstance(subject, dict):
        failures.append("record cross-check skipped: scientific_subject invalid")
        return
    if record.get("rule_id") != contract["rule_id"]:
        failures.append("seed record rule_id != contract")
    if record.get("anchor") != contract["seed_generation"]["anchor"]:
        failures.append("seed record anchor != contract")
    if record.get("variant_counts") != {v: spec["n"] for v, spec in variants.items()}:
        failures.append("seed record variant_counts != contract variant N values")
    if record.get("seeds") != contract["confirmatory_seeds"]:
        failures.append("seed record confirmatory arrays != contract confirmatory_seeds (drift)")
    if record.get("bootstrap_seeds") != contract["bootstrap"]["seeds"]:
        failures.append("seed record bootstrap seeds != contract bootstrap.seeds")
    if record.get("bootstrap_indices") != contract["bootstrap"]["indices"]:
        failures.append("seed record bootstrap indices != contract bootstrap.indices")
    if record.get("indices_consumed") != contract["seed_generation"]["indices_consumed"]:
        failures.append("seed record indices_consumed != contract cursor state")
    if record.get("next_candidate_index") != contract["seed_generation"]["next_candidate_index"]:
        failures.append("seed record next_candidate_index != contract cursor state")
    if record.get("exclusion_tree_pin") != contract["seed_generation"]["exclusion_tree_pin"]:
        failures.append("seed record exclusion_tree_pin != contract pin")
    if record.get("replacement_quota_pairs") != contract["replacement"]["quota_pairs_per_variant"]:
        failures.append("seed record replacement quotas != contract quotas")
    record_pools = record.get("replacement_pools") or {}
    contract_pools = contract["replacement"]["pools"]
    for variant in contract_pools:
        record_pool = record_pools.get(variant) if isinstance(record_pools, dict) else None
        if not isinstance(record_pool, dict):
            failures.append(f"seed record replacement pool missing for {variant}")
            continue
        if record_pool.get("seeds") != contract_pools[variant]["seeds"]:
            failures.append(f"seed record replacement pool seeds != contract for {variant}")
        if record_pool.get("start_index") != contract_pools[variant]["start_index"]:
            failures.append(f"seed record replacement pool start_index != contract for {variant}")
        if record_pool.get("next_candidate_index") != contract_pools[variant]["next_candidate_index"]:
            failures.append(f"seed record replacement pool cursor != contract for {variant}")
    # Bit-exact regeneration from the recorded cursor + skip state (F2/F3 proof).
    for variant in variants:
        skipped = (record.get("skipped_identities") or {}).get(variant) or []
        skip_indices = {entry["index"] for entry in skipped if isinstance(entry, dict)}
        consumed = contract["seed_generation"]["indices_consumed"][variant]
        try:
            replayed = replay_variant_stream(
                contract["seed_generation"]["anchor"], variant, consumed, skip_indices
            )
        except ValueError as exc:
            failures.append(f"regeneration replay {variant}: {exc}")
            continue
        if replayed != contract["confirmatory_seeds"][variant]:
            failures.append(
                f"regeneration replay {variant}: stream at consumed indices {consumed} with the "
                "recorded skips does not reproduce the published identities (drift or hand-edit)"
            )
    digest = logical_record_digest(
        record.get("seeds", {}),
        record.get("bootstrap_seeds", {}),
        record.get("anchor", ""),
        record.get("variant_counts", {}),
    )
    if digest != record.get("record_sha256"):
        failures.append("seed record logical digest stale (record_sha256 mismatch)")
    if digest != subject["seed_record_logical_sha256"]:
        failures.append("seed record logical digest != contract seed_record_logical_sha256")
    exclusions = record.get("exclusions_applied")
    if exclusions != sorted(HISTORICAL_SEEDS_V1):
        failures.append("seed record exclusions_applied != frozen historical exclusion list")
    fresh_all = [s for stream in (record.get("seeds") or {}).values() for s in stream]
    if fresh_all and set(fresh_all) & set(HISTORICAL_SEEDS_V1):
        failures.append("historical seed present in published confirmatory arrays")


# ---------------------------------------------------------------------------
# Dispatch entrypoint (mandatory gate; bypass is impossible by construction).
# ---------------------------------------------------------------------------


def freeze_gate(
    contract_path: Path | str,
    protocol_path: Path | str,
    record_path: Path | str | None = None,
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    """Load + validate the full freeze/dispatch package (fail-closed)."""
    contract = load_contract(contract_path)
    try:
        protocol_text = Path(protocol_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"protocol read error {protocol_path}: {exc}") from exc
    record = None
    if record_path is not None:
        record = load_seed_record(record_path)
    elif contract.get("scientific_subject", {}).get("freeze_status") == "FROZEN":
        raise ContractError("frozen contract requires an explicit seed record binding")
    return validate_freeze_contract(
        contract, protocol_text=protocol_text, seed_record=record,
        repo_root=repo_root, require_record=True,
    )


def build_execution_plan(
    contract_path: Path | str,
    protocol_path: Path | str,
    record_path: Path | str,
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    """THE dispatch entrypoint: only a fully PASSing freeze package yields a plan.

    Any validation failure raises :class:`ContractError` (non-zero exit at the
    CLI) — a corrupted contract cannot be dispatched around the gate.
    """
    contract = load_contract(contract_path)
    record = load_seed_record(record_path)
    try:
        protocol_text = Path(protocol_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"protocol read error {protocol_path}: {exc}") from exc
    report = validate_freeze_contract(
        contract, protocol_text=protocol_text, seed_record=record, repo_root=repo_root
    )
    if report["gate"] != "PASS":
        raise ContractError("dispatch refused: freeze gate FAIL — " + "; ".join(report["failures"][:8]))
    variants = contract["variants"]
    plan: dict[str, Any] = {
        "kind": "nanolab_v02_dispatch_execution_plan",
        "contract_revision": contract["contract_revision"],
        "rule_id": contract["rule_id"],
        "candidate": contract["scientific_subject"],
        "gate_report": {
            "gate": "PASS",
            "integer_rounding_policy": INTEGER_ROUNDING_POLICY["name"],
        },
        "cells": {},
        "budget": contract["run_budget"],
        "replacement_policy": {
            "allowed_only_for": contract["replacement"]["allowed_only_for"],
            "attempt_id_rule": contract["replacement"]["attempt_id_rule"],
            "paired_semantics": contract["replacement"]["paired_semantics"],
        },
        "scientific_claim_ceiling": "C1_COMPUTATIONAL_REPRODUCTION (campaign-level; none claimed here)",
        "scientific_outcome": "NOT_EVALUATED",
    }
    for variant, spec in variants.items():
        plan["cells"][variant] = {
            "role": spec["role"],
            "n_pairs": spec["n"],
            "n_min_valid_pairs": spec["n_min"],
            "runs_per_platform": spec["n"],
            "confirmatory_identities": contract["confirmatory_seeds"][variant],
            "bootstrap_seed": contract["bootstrap"]["seeds"][variant],
            "replacement_quota_pairs": contract["replacement"]["quota_pairs_per_variant"][variant],
            "replacement_pool_identities": contract["replacement"]["pools"][variant]["seeds"],
            "replacement_pool_cursor": {
                "next_candidate_index": contract["replacement"]["pools"][variant]["next_candidate_index"]
            },
        }
    return plan


# ---------------------------------------------------------------------------
# Replacement ledger (F3 semantics: attempt ids + FAILED_TECHNICAL-only).
# ---------------------------------------------------------------------------

ATTEMPT_ID_RE = re.compile(r"^[A-Za-z0-9._-]+(-R[0-9]+)?$")


class ReplacementBudgetExhausted(RuntimeError):
    """Raised when the frozen per-cell replacement quota is exhausted."""


class ReplacementLedger:
    """Append-only paired attempt/replacement ledger for one campaign.

    - attempt IDs are unique forever (reuse raises);
    - replacements are allowed ONLY for frozen ``FAILED_TECHNICAL`` outcomes
      (any other outcome raises — outcome-driven seed selection is forbidden);
    - replacement identities are consumed from the frozen pool in pool order
      (deterministic; never chosen from outcomes);
    - per-cell quota is frozen; exhausting it raises instead of expanding.
    """

    def __init__(self, quota_pairs_per_variant: dict[str, int], pools: dict[str, list[int]]):
        self._quota = dict(quota_pairs_per_variant)
        self._pools = {v: list(pools[v]) for v in self._quota}
        self._used_pairs = {v: 0 for v in self._quota}
        self._pool_cursor = {v: 0 for v in self._quota}
        self._attempts: dict[str, dict[str, Any]] = {}
        self._ledger: list[dict[str, Any]] = []

    def register_attempt(self, attempt_id: str, variant: str, leg: str, outcome: str) -> None:
        if not ATTEMPT_ID_RE.match(attempt_id):
            raise ValueError(f"attempt id {attempt_id!r} violates the attempt id rule")
        if attempt_id in self._attempts:
            raise ValueError(
                f"attempt id {attempt_id!r} already used for "
                f"{self._attempts[attempt_id]['variant']}/{self._attempts[attempt_id]['leg']} — "
                "attempt id reuse is forbidden"
            )
        if outcome not in ("COMPLETED", "FAILED_TECHNICAL", "ABORTED", "BLOCKED_ENVIRONMENT"):
            raise ValueError(f"unknown technical outcome {outcome!r}")
        self._attempts[attempt_id] = {"variant": variant, "leg": leg, "outcome": outcome}
        self._ledger.append(
            {"attempt_id": attempt_id, "variant": variant, "leg": leg, "outcome": outcome}
        )

    def request_replacement(self, variant: str, failed_attempt_id: str) -> int:
        """Consume the next frozen pool identity for a FAILED_TECHNICAL pair."""
        attempt = self._attempts.get(failed_attempt_id)
        if attempt is None:
            raise ValueError(f"unknown attempt id {failed_attempt_id!r}")
        if attempt["variant"] != variant:
            raise ValueError(f"attempt {failed_attempt_id!r} belongs to {attempt['variant']}, not {variant}")
        if attempt["outcome"] != "FAILED_TECHNICAL":
            raise ValueError(
                f"replacement refused: attempt {failed_attempt_id!r} outcome is "
                f"{attempt['outcome']!r}; replacements are allowed ONLY for FAILED_TECHNICAL"
            )
        if self._used_pairs[variant] >= self._quota[variant]:
            raise ReplacementBudgetExhausted(
                f"{variant}: frozen replacement quota {self._quota[variant]} pairs exhausted "
                "— cell stops with an honest classification, no silent expansion"
            )
        cursor = self._pool_cursor[variant]
        if cursor >= len(self._pools[variant]):
            raise ReplacementBudgetExhausted(
                f"{variant}: frozen replacement pool exhausted at cursor {cursor}"
            )
        identity = self._pools[variant][cursor]
        self._pool_cursor[variant] = cursor + 1
        self._used_pairs[variant] += 1
        self._ledger.append(
            {
                "event": "REPLACEMENT_PAIR_ASSIGNED",
                "variant": variant,
                "failed_attempt_id": failed_attempt_id,
                "replacement_identity": identity,
                "pool_cursor_after": self._pool_cursor[variant],
                "used_pairs": self._used_pairs[variant],
                "quota_pairs": self._quota[variant],
            }
        )
        return identity

    @property
    def ledger(self) -> list[dict[str, Any]]:
        return list(self._ledger)

    def used_pairs(self, variant: str) -> int:
        return self._used_pairs[variant]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m scripts.nl5.repro_v02_freeze_contract",
        description="R4 fail-closed freeze/dispatch contract gate (F1/F4).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("gate", "plan"):
        child = sub.add_parser(name)
        child.add_argument("--contract", required=True)
        child.add_argument("--protocol", required=True)
        child.add_argument("--record")
        child.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)
    try:
        if args.command == "gate":
            record_path = args.record
            report = freeze_gate(
                args.contract, args.protocol, record_path, repo_root=args.repo_root
            )
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["gate"] == "PASS" else 3
        plan = build_execution_plan(
            args.contract,
            args.protocol,
            args.record,  # type: ignore[arg-type]
            repo_root=args.repo_root,
        )
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    except ContractError as exc:
        print(json.dumps({"gate": "FREEZE_GATE_FAIL", "error": str(exc)}, ensure_ascii=False))
        return 3
    except OSError as exc:
        print(json.dumps({"gate": "FREEZE_GATE_FAIL", "error": f"read error: {exc}"}, ensure_ascii=False))
        return 4


if __name__ == "__main__":
    sys.exit(main())
