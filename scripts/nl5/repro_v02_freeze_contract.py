"""Versioned machine-readable freeze/dispatch contract for NANOLAB_REPRO_V0_2.

Pre-freeze hardening R4 (WO-NL5-V02-PREFREEZE-HARDENING-R4), repairs audit
finding F1 (fail-open freeze consistency gate) and F4 (integer rounding /
scientific wording drift). R4.1 (fresh independent Reviewer R1 corrections
M-1..M-4) hardens the authority model:

- **Two stages are mechanically separated (M-1).** ``validate_freeze_contract``
  / :func:`freeze_gate` prove INTERNAL CONSISTENCY ONLY
  (``PREFREEZE_VALIDATION_PASS``); they never authorize execution. A
  scientific ``nanolab_v02_dispatch_execution_plan`` is produced exclusively
  by :func:`build_execution_plan`, which additionally requires a validated
  machine-readable ``nanolab_v02_dispatch_authority`` object binding:
  ``freeze_status == FROZEN`` with frozen subject HEAD/TREE pins, a Director
  FREEZE record, HG-B owner approval, fresh review PASS + verify VERIFIED for
  the frozen subject, R2 ACTIVE with both executor legs authorized, and the
  exact contract/seed-record digests. The committed PRE-DATA / NOT FROZEN
  package is therefore ``DISPATCH_BLOCKED`` by construction.

- **Replacement pools are replayed bit-exactly (M-2).** Every pool must
  regenerate from ``(anchor, variant, start_index, quota, recorded skips)``
  via :func:`nl5.repro_v02_seeds.replay_replacement_stream`; each skip entry
  must be the strict object ``{"index", "seed", "reason": "SEED_COLLISION_TREE"}``
  re-deriving from the stream. A dedicated ``replacement_pool_sha256`` and a
  full ``seed_record_r4_sha256`` integrity digest are bound into the
  contract (the historical R3 logical digest is kept as provenance only).

- **Collision-skip legitimacy is bound into the gate (M-3).** The contract
  binds a ``collision_scan_manifest`` by path + SHA-256; the manifest must
  prove every accepted identity CLEAN outside the exact allowlist and every
  recorded skip backed by a real non-allowlisted pinned-tree hit.
  Authoritative entrypoints re-run the pinned scan for every recorded skip:
  a fabricated skip for a clean candidate fails the gate even when contract,
  record and manifest were edited self-consistently. Scan errors, missing
  pinned objects and timeouts are BLOCKED, never treated as clean.

EVERYTHING is validated fail-closed: malformed JSON, missing or extra
fields, wrong types (including ``bool`` where an integer is required),
out-of-range or duplicate seeds, stale digests, missing/extra variants,
N/N_min/quota/wall mismatches, contradictory or duplicated protocol
declarations, unknown revisions and read errors all produce
``FREEZE_GATE_FAIL`` / :class:`ContractError` — never a silent PASS.

CLI (repository root; on hosts where a global ``scripts`` package shadows
the repository namespace use ``PYTHONPATH=scripts``)::

    python3 -m scripts.nl5.repro_v02_freeze_contract prefreeze \
        --contract <contract.json> --protocol <candidate.md> --record <record.json>
    python3 -m scripts.nl5.repro_v02_freeze_contract gate \
        --contract <contract.json> --protocol <candidate.md> --record <record.json>
    python3 -m scripts.nl5.repro_v02_freeze_contract plan \
        --contract <contract.json> --protocol <candidate.md> --record <record.json> \
        --authority <dispatch-authority.json>

Exit codes: 0 = PASS / authorized plan produced (``prefreeze`` exits 0 for
internal-consistency PASS even while dispatch stays blocked); 3 =
FREEZE_GATE_FAIL or DISPATCH_BLOCKED (reasons printed); 4 = contract/read
error (fail-closed).
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
    SCAN_MANIFEST_KIND,
    bootstrap_label,
    check_skip_entry,
    collision_manifest_digest,
    derive_seed,
    normalized_replacement_pools,
    r4_record_digest,
    replacement_pool_digest,
    replay_replacement_stream,
    replay_variant_stream,
    verify_collision_manifest,
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
    "replacement_pool_sha256",
    "seed_record_r4_sha256",
    "collision_scan_manifest",
)

_SUBJECT_KEYS = (
    "candidate_doc_path",
    "candidate_revision",
    "seed_record_path",
    "seed_record_file_sha256",
    "seed_record_logical_sha256",
    "freeze_status",
    "frozen_subject_head",
    "frozen_subject_tree",
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

_MANIFEST_KEYS = ("path", "sha256")

_DISPATCH_AUTHORITY_KIND = "nanolab_v02_dispatch_authority"
_DISPATCH_AUTHORITY_SCHEMA_VERSION = 1
_AUTHORIZED_AUTHOR_EXECUTOR = "AUTHOR_U1"
_AUTHORIZED_EXTERNAL_EXECUTOR = "EXTERNAL_U2"
SYNTHETIC_FIXTURE_MARKER = "SYNTHETIC TEST FIXTURE ONLY"

_DISPATCH_AUTHORITY_TOP_KEYS = (
    "schema_version",
    "kind",
    "authority_revision",
    "fixture",
    "fixture_note",
    "frozen",
    "subject_head",
    "subject_tree",
    "contract_sha256",
    "seed_record_sha256",
    "freeze_record",
    "hg_b_record",
    "review_verdict",
    "verify_verdict",
    "r2_record",
    "author_executor",
    "external_executor",
    "executor_policy",
)
_AUTHORITY_FREEZE_RECORD_KEYS = (
    "path",
    "sha256",
    "director",
    "decision",
    "subject_head",
    "subject_tree",
    "contract_sha256",
    "seed_record_sha256",
)
_AUTHORITY_HG_B_KEYS = ("path", "sha256", "decision", "candidate_revision", "rule_id")
_AUTHORITY_REVIEW_KEYS = ("path", "sha256", "verdict", "reviewed_head", "reviewed_tree")
_AUTHORITY_VERIFY_KEYS = ("path", "sha256", "verdict", "verified_head", "verified_tree")
_AUTHORITY_R2_KEYS = ("path", "sha256", "r2_status", "author_executor", "external_executor")
_AUTHORITY_POLICY_KEYS = ("author_leg_allowed", "external_leg_allowed")


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
    collision_manifest: dict[str, Any] | None = None,
    manifest_file_sha256: str | None = None,
    rerun_scan: bool = False,
) -> dict[str, Any]:
    """Full fail-closed validation. Returns a report; ``gate`` is PASS only
    when ``failures`` is empty. Any malformed/missing/extra/mismatch/unknown
    input lands in ``failures`` — the caller must treat FAIL as terminal.

    IMPORTANT (R4.1, M-1): a PASS here is a ``PREFREEZE_VALIDATION_PASS``
    (internal consistency only). It is NOT dispatch authorization — see
    :func:`validate_dispatch_authority` / :func:`build_execution_plan`.
    """
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

    # R4.1 (M-3): the bound collision-scan manifest. When a pre-loaded
    # manifest is supplied it is verified directly; with a repository root
    # the manifest file is loaded from its contract-bound path. Structural
    # verification is cheap and always runs when the manifest is available;
    # ``rerun_scan`` additionally re-runs the pinned-tree scan for every
    # recorded skip (authoritative freeze/dispatch paths).
    if failures or collision_manifest is not None or repo_root is not None:
        _validate_manifest_binding(
            contract,
            failures,
            manifest=collision_manifest,
            manifest_file_sha256=manifest_file_sha256,
            record=seed_record,
            repo_root=repo_root,
            rerun_root=repo_root if rerun_scan else None,
        )

    return _report(failures, contract)


def dispatch_blockers(contract: dict[str, Any]) -> list[str]:
    """R4.1 (M-1): why this contract is not dispatch-ready right now."""
    subject = contract.get("scientific_subject") or {}
    blockers: list[str] = []
    if subject.get("freeze_status") != "FROZEN":
        blockers.append(
            "freeze_status is NOT_FROZEN: scientific dispatch requires a Director FREEZE "
            "record on this exact subject"
        )
    else:
        blockers.append(
            "no validated nanolab_v02_dispatch_authority object was supplied "
            "(Director FREEZE record + HG-B APPROVED + review PASS + verify VERIFIED + "
            "R2 ACTIVE with both executor legs authorized)"
        )
    return blockers


def _report(failures: list[str], contract: dict[str, Any]) -> dict[str, Any]:
    gate_pass = not failures
    frozen = isinstance(contract.get("scientific_subject"), dict) and (
        contract["scientific_subject"].get("freeze_status") == "FROZEN"
    )
    return {
        "kind": "r4_freeze_contract_gate",
        "contract_revision": contract.get("contract_revision"),
        "gate": "PASS" if gate_pass else "FREEZE_GATE_FAIL",
        "failures": failures,
        # R4.1 (M-1): a consistency PASS is a PRE-FREEZE VALIDATION result.
        # It never authorizes scientific dispatch on its own.
        "validation_stage": "PREFREEZE_VALIDATION_PASS" if gate_pass else "FREEZE_GATE_FAIL",
        "freeze_status": contract.get("scientific_subject", {}).get("freeze_status")
        if isinstance(contract.get("scientific_subject"), dict)
        else None,
        "dispatch_ready": False,
        "dispatch": "DISPATCH_BLOCKED",
        "dispatch_blockers": dispatch_blockers(contract) if gate_pass else [],
        "integer_rounding_policy": INTEGER_ROUNDING_POLICY["name"],
        "budget": derive_budget(
            {v: spec.get("n") for v, spec in contract["variants"].items()}
        ) if isinstance(contract.get("variants"), dict) and contract["variants"] and all(
            isinstance(spec, dict) and _is_int(spec.get("n")) for spec in contract["variants"].values()
        ) else None,
        "frozen_declared": frozen,
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
    # R4.1 (M-1): frozen subject pins. A NOT_FROZEN candidate must carry NO
    # frozen subject binding (null); a FROZEN contract must pin the exact
    # subject HEAD/TREE that the dispatch authority will be validated against.
    frozen = subject.get("freeze_status") == "FROZEN"
    for key in ("frozen_subject_head", "frozen_subject_tree"):
        value = subject.get(key)
        if frozen:
            if not isinstance(value, str) or not _HEX40_RE.match(value or ""):
                failures.append(
                    f"scientific_subject.{key}: must be a full 40-hex pin while freeze_status "
                    "is FROZEN"
                )
        elif value is not None:
            failures.append(
                f"scientific_subject.{key}: must be null while freeze_status is NOT_FROZEN "
                "(a pre-freeze candidate must not claim frozen subject pins)"
            )
    if frozen and isinstance(subject.get("frozen_subject_head"), str) and isinstance(
        subject.get("frozen_subject_tree"), str
    ):
        if subject["frozen_subject_head"] == subject["frozen_subject_tree"]:
            failures.append(
                "scientific_subject: frozen_subject_head and frozen_subject_tree must differ"
            )


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
        # R4.1 (M-2): bit-exact replay of the pool from the deterministic
        # stream. A published pool that is not exactly the stream implied by
        # (anchor, variant, start_index, quota, recorded skips) is a
        # hand-adjusted list, not a deterministic allocation.
        skipped = pool.get("skipped")
        if _is_int(start) and isinstance(skipped, list):
            try:
                replayed_pool = replay_replacement_stream(
                    contract["seed_generation"].get("anchor", DEFAULT_ANCHOR),
                    variant,
                    start,
                    len(pool_seeds),
                    skipped,
                )
            except ValueError as exc:
                failures.append(f"replacement.pools.{variant}: replay error: {exc}")
                continue
            if replayed_pool != pool_seeds:
                failures.append(
                    f"replacement.pools.{variant}: pool identities are NOT the bit-exact "
                    "deterministic stream from start_index with the recorded skips "
                    "(hand-picked seed stream is forbidden, M-2)"
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
        if record_pool.get("skipped") != contract_pools[variant].get("skipped"):
            failures.append(f"seed record replacement pool skipped entries != contract for {variant}")
        consumed = record_pool.get("indices_consumed")
        if _is_int(record_pool.get("start_index")) and _is_int(record_pool.get("next_candidate_index")):
            expected_consumed = [
                record_pool["start_index"],
                record_pool["next_candidate_index"] - 1,
            ]
            if consumed != expected_consumed:
                failures.append(
                    f"seed record replacement pool indices_consumed {consumed!r} != "
                    f"{expected_consumed!r} for {variant}"
                )
    # Bit-exact regeneration from the recorded cursor + skip state (F2/F3 proof).
    for variant in variants:
        skipped = (record.get("skipped_identities") or {}).get(variant) or []
        # R4.1 (M-2/M-3): confirmatory skip entries must be strict collision
        # objects that re-derive from the deterministic stream — a recorded
        # skip is evidence, not an accepted-on-trust cursor adjustment.
        for position, entry in enumerate(skipped):
            failures.extend(
                check_skip_entry(
                    entry, contract["seed_generation"]["anchor"], variant,
                    f"seed record skipped_identities.{variant}[{position}]",
                )
            )
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
    # R4.1 (M-2): full R4 integrity digests. The R3 logical recipe above is
    # provenance only; these digests cover the replacement pools, skips and
    # cursor state as well.
    _validate_integrity(contract, record, failures)
    exclusions = record.get("exclusions_applied")
    if exclusions != sorted(HISTORICAL_SEEDS_V1):
        failures.append("seed record exclusions_applied != frozen historical exclusion list")
    fresh_all = [s for stream in (record.get("seeds") or {}).values() for s in stream]
    if fresh_all and set(fresh_all) & set(HISTORICAL_SEEDS_V1):
        failures.append("historical seed present in published confirmatory arrays")


def _validate_integrity(contract: dict[str, Any], record: dict[str, Any], failures: list[str]) -> None:
    """R4.1 (M-2): replacement-pool + full-record digests, mutually bound."""
    where = "integrity"
    pools_digest = replacement_pool_digest((contract.get("replacement") or {}).get("pools"))
    bound = contract.get("replacement_pool_sha256")
    if not isinstance(bound, str) or not _SHA256_RE.match(bound or ""):
        failures.append(f"{where}: contract replacement_pool_sha256 must be 64-hex sha256")
    elif bound != pools_digest:
        failures.append(
            f"{where}: contract replacement_pool_sha256 {bound} != recomputed {pools_digest} "
            "(stale or hand-edited replacement pools, M-2)"
        )
    record_pools_digest = replacement_pool_digest(record.get("replacement_pools"))
    record_bound = record.get("replacement_pool_sha256")
    if not isinstance(record_bound, str) or not _SHA256_RE.match(record_bound or ""):
        failures.append(f"{where}: seed record replacement_pool_sha256 must be 64-hex sha256")
    elif record_bound != pools_digest:
        failures.append(
            f"{where}: seed record replacement_pool_sha256 {record_bound} != contract pools "
            f"digest {pools_digest} (record/contract pool drift, M-2)"
        )
    if record_bound != bound and isinstance(record_bound, str) and isinstance(bound, str):
        failures.append(f"{where}: replacement_pool_sha256 differs between contract and record")
    full = r4_record_digest(record)
    record_full = record.get("record_r4_sha256")
    if not isinstance(record_full, str) or not _SHA256_RE.match(record_full or ""):
        failures.append(f"{where}: seed record record_r4_sha256 must be 64-hex sha256")
    elif record_full != full:
        failures.append(
            f"{where}: seed record record_r4_sha256 {record_full} != recomputed {full} "
            "(stale full-record digest, M-2)"
        )
    contract_full = contract.get("seed_record_r4_sha256")
    if not isinstance(contract_full, str) or not _SHA256_RE.match(contract_full or ""):
        failures.append(f"{where}: contract seed_record_r4_sha256 must be 64-hex sha256")
    elif contract_full != full:
        failures.append(
            f"{where}: contract seed_record_r4_sha256 {contract_full} != record {full} "
            "(full-record digest drift, M-2)"
        )


def _validate_manifest_binding(
    contract: dict[str, Any],
    failures: list[str],
    manifest: dict[str, Any] | None = None,
    manifest_file_sha256: str | None = None,
    record: dict[str, Any] | None = None,
    repo_root: Path | str | None = None,
    rerun_root: Path | str | None = None,
) -> None:
    """R4.1 (M-3): bind the collision-scan manifest into the gate decision."""
    binding = contract.get("collision_scan_manifest")
    pre = len(failures)
    _require_keys(binding, _MANIFEST_KEYS, "collision_scan_manifest", failures)
    if not isinstance(binding, dict):
        return
    path = binding.get("path")
    if not isinstance(path, str) or not path:
        failures.append("collision_scan_manifest.path: must be a repository-relative path")
    elif path.startswith("/") or ".." in Path(path).parts:
        failures.append("collision_scan_manifest.path: must be a repository-relative path")
    digest = binding.get("sha256")
    if not isinstance(digest, str) or not _SHA256_RE.match(digest or ""):
        failures.append("collision_scan_manifest.sha256: must be 64-hex sha256")
    if len(failures) > pre:
        return
    if manifest is None:
        if repo_root is None:
            # Binding-only check: the manifest file itself is verified by the
            # authoritative entrypoints (freeze_gate / dispatch), which always
            # pass a repository root.
            return
        manifest, manifest_file_sha256, load_failures = _load_manifest_file(
            Path(repo_root) / path
        )
        failures.extend(load_failures)
        if manifest is None:
            return
    if manifest_file_sha256 is not None and digest != manifest_file_sha256:
        failures.append(
            f"collision_scan_manifest: bound sha256 {digest} != manifest file digest "
            f"{manifest_file_sha256} (edited scan facts, M-3)"
        )
    verify_collision_manifest(
        contract,
        manifest,
        failures,
        record=record,
        rerun_root=Path(rerun_root) if rerun_root is not None else None,
    )


def _load_manifest_file(path: Path) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    failures: list[str] = []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        failures.append(f"collision_scan_manifest read error {path}: {exc}")
        return None, None, failures
    file_digest = hashlib.sha256(raw).hexdigest()
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        failures.append(f"collision_scan_manifest is not valid JSON ({path}): {exc}")
        return None, file_digest, failures
    if not isinstance(manifest, dict):
        failures.append(f"collision_scan_manifest must be a JSON object ({path})")
        return None, file_digest, failures
    return manifest, file_digest, failures


# ---------------------------------------------------------------------------
# Two-stage authority (R4.1, M-1): PREFREEZE_VALIDATION vs DISPATCH_READY.
# ---------------------------------------------------------------------------


def freeze_gate(
    contract_path: Path | str,
    protocol_path: Path | str,
    record_path: Path | str | None = None,
    repo_root: Path | str | None = None,
    rerun_scan: bool = True,
) -> dict[str, Any]:
    """Authoritative pre-freeze validation of the full package (fail-closed).

    R4.1 (M-1): this proves INTERNAL CONSISTENCY ONLY — the report's
    ``validation_stage`` is ``PREFREEZE_VALIDATION_PASS`` and ``dispatch`` is
    ``DISPATCH_BLOCKED`` even on PASS. It never authorizes execution. The
    bound collision-scan manifest is verified from the repository and, by
    default, every recorded skip is re-proven against the pinned tree
    (``rerun_scan``; a scan error is BLOCKED, never clean).
    """
    if repo_root is None:
        raise ContractError(
            "freeze_gate requires a repository root: the contract-bound collision scan "
            "manifest must be loaded and verified (fail-closed, M-3)"
        )
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
        repo_root=repo_root, require_record=True, rerun_scan=rerun_scan,
    )


def prefreeze_validation(
    contract_path: Path | str,
    protocol_path: Path | str,
    record_path: Path | str | None = None,
    repo_root: Path | str | None = None,
    rerun_scan: bool = True,
) -> dict[str, Any]:
    """The ONLY gate a PRE-DATA / NOT FROZEN package can pass (R4.1, M-1).

    Returns the consistency report with ``validation_stage =
    PREFREEZE_VALIDATION_PASS`` and ``dispatch = DISPATCH_BLOCKED`` when the
    internal-consistency gate passes. No dispatch plan is produced here.
    """
    report = freeze_gate(
        contract_path, protocol_path, record_path, repo_root=repo_root, rerun_scan=rerun_scan
    )
    if report["gate"] == "PASS":
        report["conclusion"] = (
            "internal consistency holds; the package remains PRE-DATA / NOT FROZEN and "
            "scientific dispatch stays blocked until FROZEN + dispatch authority"
        )
    return report


def load_dispatch_authority(path: Path | str) -> dict[str, Any]:
    """Load a ``nanolab_v02_dispatch_authority`` JSON (fail-closed)."""
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"dispatch authority read error {path}: {exc}") from exc
    try:
        authority = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(f"dispatch authority is not valid JSON ({path}): {exc}") from exc
    if not isinstance(authority, dict):
        raise ContractError("dispatch authority must be a JSON object")
    return authority


def _authority_path_digest(
    repo_root: Path,
    record: dict[str, Any],
    embedded: dict[str, Any],
    where: str,
    failures: list[str],
) -> None:
    """Verify an authority-referenced record file (fail-closed).

    The file at ``record['path']`` must exist, hash to the bound ``sha256``,
    parse as JSON, and carry exactly the fields the authority embeds for it
    (minus the ``path``/``sha256`` binding keys themselves) — the embedded
    decision fields are therefore inseparable from the published record.
    """
    path = record.get("path")
    digest = record.get("sha256")
    if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
        failures.append(f"{where}.path: must be a repository-relative path")
        return
    if not isinstance(digest, str) or not _SHA256_RE.match(digest or ""):
        failures.append(f"{where}.sha256: must be 64-hex sha256")
        return
    target = repo_root / path
    if not target.is_file():
        failures.append(f"{where}: referenced record missing on disk: {target}")
        return
    raw = target.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != digest:
        failures.append(
            f"{where}: referenced record digest mismatch: file {actual} != bound {digest}"
        )
    try:
        on_disk = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        failures.append(f"{where}: referenced record is not valid JSON: {exc}")
        return
    if not isinstance(on_disk, dict):
        failures.append(f"{where}: referenced record must be a JSON object")
        return
    expected = {k: v for k, v in embedded.items() if k not in ("path", "sha256")}
    actual_fields = {k: v for k, v in on_disk.items() if k not in ("path", "sha256")}
    if actual_fields != expected:
        failures.append(
            f"{where}: referenced record content does not match the authority-embedded copy "
            "(the binding must cover the published record bytes)"
        )


def validate_dispatch_authority(
    authority: dict[str, Any],
    contract: dict[str, Any],
    protocol_text: str,
    seed_record: dict[str, Any],
    repo_root: Path | str,
    contract_path: Path | str,
    rerun_scan: bool = True,
    allow_fixture: bool = False,
) -> dict[str, Any]:
    """Validate the machine-readable dispatch authority (R4.1, M-1).

    The authority must machine-bind, for THIS exact contract:

    - ``freeze_status == FROZEN`` with frozen subject HEAD/TREE pins equal to
      the authority pins and to the Director FREEZE record pins;
    - a Director FREEZE record binding the exact contract + seed-record digests;
    - HG-B owner approval (``decision == APPROVED``) for this rule/revision;
    - a fresh review verdict PASS and a fresh verify verdict VERIFIED for the
      frozen subject HEAD/TREE;
    - R2 ACTIVE with BOTH executor legs (``AUTHOR_U1`` / ``EXTERNAL_U2``)
      authorized and allowed by the executor policy;
    - the SHA-256 of the exact contract file and seed record file.

    Every referenced record must exist under ``repo_root`` with the bound
    digest. A ``fixture`` authority is second-class: it is rejected unless
    ``allow_fixture=True`` and the produced plan is marked
    ``synthetic_test_fixture_only``. Any problem raises :class:`ContractError`.
    """
    root = Path(repo_root)
    failures: list[str] = []
    _require_keys(authority, _DISPATCH_AUTHORITY_TOP_KEYS, "dispatch_authority", failures)
    if failures:
        raise ContractError("dispatch authority rejected: " + "; ".join(failures))
    if authority["schema_version"] != _DISPATCH_AUTHORITY_SCHEMA_VERSION:
        failures.append(
            f"dispatch_authority.schema_version {authority['schema_version']!r} != "
            f"{_DISPATCH_AUTHORITY_SCHEMA_VERSION}"
        )
    if authority["kind"] != _DISPATCH_AUTHORITY_KIND:
        failures.append(
            f"dispatch_authority.kind {authority['kind']!r} != {_DISPATCH_AUTHORITY_KIND!r}"
        )
    if not isinstance(authority["authority_revision"], str) or not authority["authority_revision"]:
        failures.append("dispatch_authority.authority_revision: must be a non-empty string")
    fixture = authority["fixture"]
    if not isinstance(fixture, bool):
        failures.append("dispatch_authority.fixture: must be a boolean")
    if fixture is True:
        note = authority.get("fixture_note")
        if not isinstance(note, str) or SYNTHETIC_FIXTURE_MARKER not in note:
            failures.append(
                f"dispatch_authority.fixture_note: a fixture authority must carry the marker "
                f"{SYNTHETIC_FIXTURE_MARKER!r}"
            )
        if not allow_fixture:
            failures.append(
                "dispatch_authority: fixture authorities are not valid for real dispatch "
                "(allow_fixture=True is required even for synthetic use)"
            )
    elif authority.get("fixture_note") not in (None, ""):
        failures.append("dispatch_authority.fixture_note: must be empty for a non-fixture authority")
    if authority["frozen"] is not True:
        failures.append(
            f"dispatch_authority.frozen must be literally true (got {authority['frozen']!r})"
        )
    for key in ("subject_head", "subject_tree"):
        if not isinstance(authority[key], str) or not _HEX40_RE.match(authority[key] or ""):
            failures.append(f"dispatch_authority.{key}: must be a full 40-hex SHA")
    if authority.get("subject_head") == authority.get("subject_tree"):
        failures.append("dispatch_authority: subject_head and subject_tree must differ")
    if not isinstance(authority["contract_sha256"], str) or not _SHA256_RE.match(
        authority["contract_sha256"] or ""
    ):
        failures.append("dispatch_authority.contract_sha256: must be 64-hex sha256")
    if not isinstance(authority["seed_record_sha256"], str) or not _SHA256_RE.match(
        authority["seed_record_sha256"] or ""
    ):
        failures.append("dispatch_authority.seed_record_sha256: must be 64-hex sha256")
    if authority["author_executor"] != _AUTHORIZED_AUTHOR_EXECUTOR:
        failures.append(
            f"dispatch_authority.author_executor must be {_AUTHORIZED_AUTHOR_EXECUTOR!r} "
            f"(got {authority['author_executor']!r})"
        )
    if authority["external_executor"] != _AUTHORIZED_EXTERNAL_EXECUTOR:
        failures.append(
            f"dispatch_authority.external_executor must be {_AUTHORIZED_EXTERNAL_EXECUTOR!r} "
            f"(got {authority['external_executor']!r})"
        )
    policy = authority["executor_policy"]
    _require_keys(policy, _AUTHORITY_POLICY_KEYS, "dispatch_authority.executor_policy", failures)
    if isinstance(policy, dict):
        for key in _AUTHORITY_POLICY_KEYS:
            if policy.get(key) is not True:
                failures.append(
                    f"dispatch_authority.executor_policy.{key} must be literally true "
                    "(both legs must be allowed by executor policy)"
                )

    freeze_record = authority["freeze_record"]
    _require_keys(freeze_record, _AUTHORITY_FREEZE_RECORD_KEYS, "freeze_record", failures)
    hg_b = authority["hg_b_record"]
    _require_keys(hg_b, _AUTHORITY_HG_B_KEYS, "hg_b_record", failures)
    review = authority["review_verdict"]
    _require_keys(review, _AUTHORITY_REVIEW_KEYS, "review_verdict", failures)
    verify = authority["verify_verdict"]
    _require_keys(verify, _AUTHORITY_VERIFY_KEYS, "verify_verdict", failures)
    r2 = authority["r2_record"]
    _require_keys(r2, _AUTHORITY_R2_KEYS, "r2_record", failures)
    if failures:
        raise ContractError("dispatch authority rejected: " + "; ".join(failures))

    if freeze_record.get("decision") != "FREEZE":
        failures.append(
            f"freeze_record.decision must be 'FREEZE' (got {freeze_record.get('decision')!r})"
        )
    if not isinstance(freeze_record.get("director"), str) or not freeze_record.get("director"):
        failures.append("freeze_record.director: must be a non-empty string")
    if freeze_record.get("subject_head") != authority.get("subject_head") or freeze_record.get(
        "subject_tree"
    ) != authority.get("subject_tree"):
        failures.append(
            "freeze subject mismatch: freeze_record subject pins != authority subject pins"
        )
    if freeze_record.get("contract_sha256") != authority.get("contract_sha256"):
        failures.append("freeze_record.contract_sha256 != authority contract_sha256")
    if freeze_record.get("seed_record_sha256") != authority.get("seed_record_sha256"):
        failures.append("freeze_record.seed_record_sha256 != authority seed_record_sha256")
    if hg_b.get("decision") != "APPROVED":
        failures.append(
            f"hg_b_record.decision must be 'APPROVED' (got {hg_b.get('decision')!r}); "
            "HG-B owner approval is a dispatch prerequisite"
        )
    if hg_b.get("candidate_revision") != str(
        contract.get("scientific_subject", {}).get("candidate_revision")
    ):
        failures.append(
            "hg_b_record.candidate_revision != contract candidate_revision (the owner "
            "approval must bind the R4 delta of THIS revision)"
        )
    if hg_b.get("rule_id") != contract.get("rule_id"):
        failures.append("hg_b_record.rule_id != contract rule_id")
    if review.get("verdict") != "PASS":
        failures.append(
            f"review_verdict.verdict must be 'PASS' for the frozen subject (got "
            f"{review.get('verdict')!r})"
        )
    if review.get("reviewed_head") != authority.get("subject_head") or review.get(
        "reviewed_tree"
    ) != authority.get("subject_tree"):
        failures.append("review subject mismatch: review_verdict != authority subject pins")
    if verify.get("verdict") != "VERIFIED":
        failures.append(
            f"verify_verdict.verdict must be 'VERIFIED' for the frozen subject (got "
            f"{verify.get('verdict')!r})"
        )
    if verify.get("verified_head") != authority.get("subject_head") or verify.get(
        "verified_tree"
    ) != authority.get("subject_tree"):
        failures.append("verify subject mismatch: verify_verdict != authority subject pins")
    if r2.get("r2_status") != "ACTIVE":
        failures.append(
            f"r2_record.r2_status must be 'ACTIVE' (got {r2.get('r2_status')!r}); both legs "
            "are HARD_BLOCKED while R2 is WAITING_HOST / NOT_ACTIVE"
        )
    if r2.get("author_executor") != authority.get("author_executor") or r2.get(
        "external_executor"
    ) != authority.get("external_executor"):
        failures.append(
            "executor mismatch: r2_record executors != authority executors"
        )
    subject = contract.get("scientific_subject", {})
    if subject.get("freeze_status") != "FROZEN":
        failures.append(
            f"contract freeze_status is {subject.get('freeze_status')!r}, not FROZEN: a "
            "PRE-DATA / NOT FROZEN package cannot be dispatched"
        )
    if subject.get("frozen_subject_head") != authority.get("subject_head") or subject.get(
        "frozen_subject_tree"
    ) != authority.get("subject_tree"):
        failures.append(
            "frozen subject mismatch: contract frozen_subject pins != authority subject pins"
        )
    if authority.get("seed_record_sha256") != subject.get("seed_record_file_sha256"):
        failures.append(
            "seed record mismatch: authority seed_record_sha256 != contract "
            "seed_record_file_sha256"
        )
    try:
        actual_contract_digest = _sha256_file(Path(contract_path))
    except OSError as exc:
        raise ContractError(f"contract file read error {contract_path}: {exc}") from exc
    if authority.get("contract_sha256") != actual_contract_digest:
        failures.append(
            f"contract digest mismatch: authority contract_sha256 "
            f"{authority.get('contract_sha256')} != actual file {actual_contract_digest}"
        )
    if failures:
        raise ContractError("dispatch authority rejected: " + "; ".join(failures))

    for where, embedded in (
        ("freeze_record", freeze_record),
        ("hg_b_record", hg_b),
        ("review_verdict", review),
        ("verify_verdict", verify),
        ("r2_record", r2),
    ):
        _authority_path_digest(root, embedded, embedded, where, failures)
    if failures:
        raise ContractError("dispatch authority rejected: " + "; ".join(failures))

    gate_report = validate_freeze_contract(
        contract,
        protocol_text=protocol_text,
        seed_record=seed_record,
        repo_root=root,
        require_record=True,
        rerun_scan=rerun_scan,
    )
    if gate_report["gate"] != "PASS":
        raise ContractError(
            "dispatch refused: freeze gate FAIL — " + "; ".join(gate_report["failures"][:8])
        )
    return {
        "status": "DISPATCH_AUTHORIZED",
        "fixture": fixture,
        "synthetic_test_fixture_only": bool(fixture),
        "subject_head": authority["subject_head"],
        "subject_tree": authority["subject_tree"],
        "hg_b": "APPROVED",
        "review": "PASS",
        "verify": "VERIFIED",
        "r2_status": "ACTIVE",
        "author_executor": authority["author_executor"],
        "external_executor": authority["external_executor"],
        "authority_revision": authority["authority_revision"],
    }


def build_execution_plan(
    contract_path: Path | str,
    protocol_path: Path | str,
    record_path: Path | str,
    repo_root: Path | str | None = None,
    authority_path: Path | str | None = None,
    allow_fixture: bool = False,
    rerun_scan: bool = True,
) -> dict[str, Any]:
    """THE dispatch entrypoint (R4.1, M-1): DISPATCH_READY requires authority.

    A plan is produced ONLY when (a) the full freeze gate passes
    (``PREFREEZE_VALIDATION_PASS``) AND (b) a machine-readable
    ``nanolab_v02_dispatch_authority`` validates for this exact contract:
    FROZEN subject + Director FREEZE record + HG-B APPROVED + review PASS +
    verify VERIFIED + R2 ACTIVE with both legs authorized. The committed
    PRE-DATA / NOT FROZEN package is therefore DISPATCH_BLOCKED here — any
    validation or authority failure raises :class:`ContractError` (non-zero
    exit at the CLI); a dispatch cannot bypass the gate by construction.
    """
    if repo_root is None:
        raise ContractError(
            "dispatch requires a repository root (collision-scan manifest verification)"
        )
    if authority_path is None:
        raise ContractError(
            "dispatch refused: DISPATCH_BLOCKED — missing nanolab_v02_dispatch_authority "
            "object (freeze/dispatch requires FROZEN status, Director FREEZE record, HG-B "
            "APPROVED, review PASS, verify VERIFIED and R2 ACTIVE)"
        )
    contract = load_contract(contract_path)
    record = load_seed_record(record_path)
    authority = load_dispatch_authority(authority_path)
    try:
        protocol_text = Path(protocol_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"protocol read error {protocol_path}: {exc}") from exc
    authority_report = validate_dispatch_authority(
        authority,
        contract,
        protocol_text,
        record,
        repo_root=repo_root,
        contract_path=contract_path,
        rerun_scan=rerun_scan,
        allow_fixture=allow_fixture,
    )
    variants = contract["variants"]
    plan: dict[str, Any] = {
        "kind": "nanolab_v02_dispatch_execution_plan",
        "contract_revision": contract["contract_revision"],
        "rule_id": contract["rule_id"],
        "candidate": contract["scientific_subject"],
        "gate_report": {
            "gate": "PASS",
            "validation_stage": "PREFREEZE_VALIDATION_PASS",
            "integer_rounding_policy": INTEGER_ROUNDING_POLICY["name"],
        },
        "dispatch_authority": authority_report,
        "synthetic_test_fixture_only": bool(authority_report["fixture"]),
        "cells": {},
        "budget": contract["run_budget"],
        "replacement_policy": {
            "allowed_only_for": contract["replacement"]["allowed_only_for"],
            "attempt_id_rule": contract["replacement"]["attempt_id_rule"],
            "paired_semantics": contract["replacement"]["paired_semantics"],
            "pair_state_machine": PAIR_STATES,
        },
        "scientific_claim_ceiling": "C1_COMPUTATIONAL_REPRODUCTION (campaign-level; none claimed here)",
        "scientific_outcome": "NOT_EVALUATED",
    }
    if authority_report["fixture"]:
        plan["note"] = SYNTHETIC_FIXTURE_MARKER + " — not a real authorization"
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
# Pair-level replacement ledger (F3 + R4.1 M-4).
# ---------------------------------------------------------------------------

ATTEMPT_ID_RE = re.compile(r"^[A-Za-z0-9._-]+(-R[0-9]+)?$")

PAIR_STATES = (
    "PAIR_RUNNING",
    "PAIR_COMPLETED",
    "PAIR_FAILED_TECHNICAL",
    "PAIR_REPLACED",
    "PAIR_ABORTED",
)
LEGS = ("author", "external")
ATTEMPT_OUTCOMES = ("SCHEDULED", "COMPLETED", "FAILED_TECHNICAL", "ABORTED", "BLOCKED_ENVIRONMENT")
TERMINAL_OUTCOMES = ("COMPLETED", "FAILED_TECHNICAL", "ABORTED", "BLOCKED_ENVIRONMENT")


class ReplacementBudgetExhausted(RuntimeError):
    """Raised when the frozen per-cell replacement quota is exhausted."""


class ReplacementLedger:
    """Append-only PAIR-LEVEL paired attempt/replacement ledger (R4.1, M-4).

    A pair (``pair_id``) owns one frozen ``seed_identity`` and exactly two
    legs (author + external); attempts are globally unique and always bound
    to one pair. A failed pair may receive AT MOST ONE replacement
    assignment; the replacement consumes the next frozen pool identity,
    creates a NEW pair and schedules BOTH of its legs. Repeated requests for
    the same failed pair are rejected without consuming quota or moving the
    pool cursor; incomplete pairs (missing counterpart), variant mismatches,
    seed/pair mismatches and non-technical outcomes are rejected as well.
    Outcome-driven seed selection is impossible by construction: identities
    are consumed from the frozen pool in pool order.
    """

    def __init__(self, quota_pairs_per_variant: dict[str, int], pools: dict[str, list[int]]):
        self._quota = dict(quota_pairs_per_variant)
        self._pools = {v: list(pools[v]) for v in self._quota}
        self._used_pairs = {v: 0 for v in self._quota}
        self._pool_cursor = {v: 0 for v in self._quota}
        self._pairs: dict[str, dict[str, Any]] = {}
        self._seed_owner: dict[tuple[str, int], str] = {}
        self._attempts: dict[str, dict[str, Any]] = {}
        self._ledger: list[dict[str, Any]] = []

    # -- pair lifecycle ----------------------------------------------------

    def open_pair(self, pair_id: str, variant: str, seed_identity: int) -> dict[str, Any]:
        """Open a PAIR_RUNNING pair owning one frozen seed identity."""
        if not isinstance(pair_id, str) or not pair_id:
            raise ValueError("pair_id must be a non-empty string")
        if pair_id in self._pairs:
            raise ValueError(f"pair id {pair_id!r} already exists — pair ids are unique forever")
        if variant not in self._quota:
            raise ValueError(f"unknown variant {variant!r}")
        if not _is_int(seed_identity) or not 0 <= seed_identity < SEED_MAX:
            raise ValueError(f"seed identity {seed_identity!r} is not an int32-positive integer")
        owner = self._seed_owner.get((variant, seed_identity))
        if owner is not None:
            raise ValueError(
                f"seed/pair mismatch: seed identity {seed_identity} already belongs to "
                f"pair {owner!r} — one seed identity belongs to exactly one pair"
            )
        pair = {
            "pair_id": pair_id,
            "variant": variant,
            "seed_identity": seed_identity,
            "state": "PAIR_RUNNING",
            "legs": {},
            "replacement_assigned": False,
            "replacement_identity": None,
            "replacement_pair_id": None,
            "source_pair_id": None,
        }
        self._pairs[pair_id] = pair
        self._seed_owner[(variant, seed_identity)] = pair_id
        self._ledger.append(
            {
                "event": "PAIR_OPENED",
                "pair_id": pair_id,
                "variant": variant,
                "seed_identity": seed_identity,
                "state": "PAIR_RUNNING",
            }
        )
        return dict(pair)

    def record_attempt(self, attempt_id: str, pair_id: str, leg: str, outcome: str) -> None:
        """Bind a real (non-SCHEDULED) attempt outcome to one pair leg."""
        self._bind_attempt(attempt_id, pair_id, leg, outcome, allow_scheduled=False)

    def record_outcome(self, attempt_id: str, outcome: str) -> None:
        """Resolve a SCHEDULED leg (from a replacement pair) to its outcome."""
        attempt = self._attempts.get(attempt_id)
        if attempt is None:
            raise ValueError(f"unknown attempt id {attempt_id!r}")
        if attempt["outcome"] != "SCHEDULED":
            raise ValueError(
                f"attempt {attempt_id!r} already carries outcome {attempt['outcome']!r}; "
                "record_outcome resolves SCHEDULED legs only"
            )
        if outcome not in TERMINAL_OUTCOMES:
            raise ValueError(f"unknown technical outcome {outcome!r}")
        pair = self._pairs[attempt["pair_id"]]
        if pair["state"] != "PAIR_RUNNING":
            raise ValueError(f"pair {pair['pair_id']!r} is {pair['state']}; cannot record outcomes")
        attempt["outcome"] = outcome
        self._apply_pair_state(pair)
        self._ledger.append(
            {
                "event": "ATTEMPT_OUTCOME_RECORDED",
                "attempt_id": attempt_id,
                "pair_id": pair["pair_id"],
                "leg": attempt["leg"],
                "outcome": outcome,
                "pair_state_after": pair["state"],
            }
        )

    def request_replacement(
        self,
        variant: str,
        failed_pair_id: str,
        replacement_pair_id: str,
        author_attempt_id: str,
        external_attempt_id: str,
    ) -> int:
        """One-shot replacement of a terminal FAILED_TECHNICAL pair (M-4).

        Validates the pair state BEFORE consuming anything: both legs must be
        bound (a missing counterpart is not a failed pair), the pair must be
        terminal ``PAIR_FAILED_TECHNICAL``, and it must not already carry a
        replacement assignment. On success the next frozen pool identity is
        consumed in pool order, a NEW pair is created for it, and BOTH legs
        of the new pair are scheduled with fresh globally-unique attempt ids.
        """
        pair = self._pairs.get(failed_pair_id)
        if pair is None:
            raise ValueError(f"unknown pair id {failed_pair_id!r}")
        if pair["variant"] != variant:
            raise ValueError(
                f"variant mismatch: pair {failed_pair_id!r} belongs to {pair['variant']!r}, "
                f"not {variant!r}"
            )
        if pair["state"] == "PAIR_RUNNING":
            bound = sorted(pair["legs"])
            missing = [leg for leg in LEGS if leg not in pair["legs"]]
            raise ValueError(
                f"replacement refused: pair {failed_pair_id!r} is not terminal "
                f"(state {pair['state']}; bound legs {bound}; missing counterpart: {missing}) — "
                "an incomplete pair has no frozen FAILED_TECHNICAL condition"
            )
        if pair["state"] == "PAIR_REPLACED" or pair["replacement_assigned"]:
            raise ValueError(
                f"replacement refused: pair {failed_pair_id!r} already received its single "
                f"replacement assignment (identity {pair['replacement_identity']}, new pair "
                f"{pair['replacement_pair_id']!r}) — repeated replacement for one failed "
                "pair is forbidden"
            )
        if pair["state"] != "PAIR_FAILED_TECHNICAL":
            raise ValueError(
                f"replacement refused: pair {failed_pair_id!r} terminal state is "
                f"{pair['state']!r}; replacements are allowed ONLY for PAIR_FAILED_TECHNICAL"
            )
        if variant not in self._quota:
            raise ValueError(f"unknown variant {variant!r}")
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
        if author_attempt_id == external_attempt_id:
            raise ValueError(
                "replacement refused: author and external legs require two distinct "
                "globally-unique attempt ids (one-leg-only replacement is forbidden)"
            )
        identity = self._pools[variant][cursor]
        # All validation has passed — consume quota/cursor, then mutate state.
        self._pool_cursor[variant] = cursor + 1
        self._used_pairs[variant] += 1
        pair["state"] = "PAIR_REPLACED"
        pair["replacement_assigned"] = True
        pair["replacement_identity"] = identity
        pair["replacement_pair_id"] = replacement_pair_id
        self.open_pair(replacement_pair_id, variant, identity)
        self._pairs[replacement_pair_id]["source_pair_id"] = failed_pair_id
        for leg, attempt_id in (("author", author_attempt_id), ("external", external_attempt_id)):
            self._bind_attempt(attempt_id, replacement_pair_id, leg, "SCHEDULED", allow_scheduled=True)
        self._ledger.append(
            {
                "event": "REPLACEMENT_PAIR_ASSIGNED",
                "variant": variant,
                "failed_pair_id": failed_pair_id,
                "replacement_pair_id": replacement_pair_id,
                "replacement_identity": identity,
                "author_attempt_id": author_attempt_id,
                "external_attempt_id": external_attempt_id,
                "both_legs_scheduled": True,
                "pool_cursor_after": self._pool_cursor[variant],
                "used_pairs": self._used_pairs[variant],
                "quota_pairs": self._quota[variant],
            }
        )
        return identity

    # -- internals ----------------------------------------------------------

    def _bind_attempt(
        self, attempt_id: str, pair_id: str, leg: str, outcome: str, allow_scheduled: bool
    ) -> None:
        if not ATTEMPT_ID_RE.match(attempt_id or ""):
            raise ValueError(f"attempt id {attempt_id!r} violates the attempt id rule")
        if attempt_id in self._attempts:
            other = self._attempts[attempt_id]
            raise ValueError(
                f"attempt id {attempt_id!r} already bound to pair {other['pair_id']!r} "
                f"({other['leg']} leg) — attempt ids are globally unique"
            )
        pair = self._pairs.get(pair_id)
        if pair is None:
            raise ValueError(f"unknown pair id {pair_id!r}")
        if pair["state"] != "PAIR_RUNNING":
            raise ValueError(
                f"pair {pair_id!r} is terminal ({pair['state']}); legs cannot be bound"
            )
        if leg not in LEGS:
            raise ValueError(f"unknown leg {leg!r}; must be one of {LEGS}")
        if leg in pair["legs"]:
            raise ValueError(
                f"pair {pair_id!r} already binds its {leg} leg (attempt "
                f"{pair['legs'][leg]!r}) — author and external legs belong to the pair "
                "exactly once"
            )
        if outcome not in ATTEMPT_OUTCOMES:
            raise ValueError(f"unknown technical outcome {outcome!r}")
        if outcome == "SCHEDULED" and not allow_scheduled:
            raise ValueError(
                "record_attempt requires a real technical outcome; SCHEDULED legs are "
                "created only by request_replacement"
            )
        self._attempts[attempt_id] = {"pair_id": pair_id, "leg": leg, "outcome": outcome}
        pair["legs"][leg] = attempt_id
        self._apply_pair_state(pair)
        self._ledger.append(
            {
                "event": "ATTEMPT_BOUND",
                "attempt_id": attempt_id,
                "pair_id": pair_id,
                "leg": leg,
                "outcome": outcome,
                "pair_state_after": pair["state"],
            }
        )

    def _apply_pair_state(self, pair: dict[str, Any]) -> None:
        if len(pair["legs"]) < len(LEGS):
            pair["state"] = "PAIR_RUNNING"
            return
        outcomes = [self._attempts[attempt_id]["outcome"] for attempt_id in pair["legs"].values()]
        if any(o == "SCHEDULED" for o in outcomes):
            # a replacement pair with unresolved scheduled legs is still RUNNING
            pair["state"] = "PAIR_RUNNING"
            return
        if any(o == "FAILED_TECHNICAL" for o in outcomes):
            pair["state"] = "PAIR_FAILED_TECHNICAL"
        elif any(o in ("ABORTED", "BLOCKED_ENVIRONMENT") for o in outcomes):
            pair["state"] = "PAIR_ABORTED"
        else:
            pair["state"] = "PAIR_COMPLETED"

    # -- read surface ---------------------------------------------------------

    @property
    def ledger(self) -> list[dict[str, Any]]:
        return list(self._ledger)

    def used_pairs(self, variant: str) -> int:
        return self._used_pairs[variant]

    def pool_cursor(self, variant: str) -> int:
        return self._pool_cursor[variant]

    def pair(self, pair_id: str) -> dict[str, Any]:
        pair = self._pairs.get(pair_id)
        if pair is None:
            raise ValueError(f"unknown pair id {pair_id!r}")
        return {
            "pair_id": pair["pair_id"],
            "variant": pair["variant"],
            "seed_identity": pair["seed_identity"],
            "state": pair["state"],
            "legs": dict(pair["legs"]),
            "replacement_assigned": pair["replacement_assigned"],
            "replacement_identity": pair["replacement_identity"],
            "replacement_pair_id": pair["replacement_pair_id"],
            "source_pair_id": pair["source_pair_id"],
        }

    def pair_state(self, pair_id: str) -> str:
        return self.pair(pair_id)["state"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m scripts.nl5.repro_v02_freeze_contract",
        description="R4/R4.1 fail-closed freeze contract gate + gated dispatch (F1/F4, M-1..M-4).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("gate", "prefreeze"):
        child = sub.add_parser(name)
        child.add_argument("--contract", required=True)
        child.add_argument("--protocol", required=True)
        child.add_argument("--record")
        child.add_argument("--repo-root", default=".")
        child.add_argument(
            "--no-scan-rerun",
            action="store_true",
            help="skip the pinned-scan re-run for recorded skips (binding checks still run)",
        )
    plan = sub.add_parser("plan")
    plan.add_argument("--contract", required=True)
    plan.add_argument("--protocol", required=True)
    plan.add_argument("--record", required=True)
    plan.add_argument("--repo-root", default=".")
    plan.add_argument("--authority", required=True, help="nanolab_v02_dispatch_authority JSON")
    plan.add_argument("--no-scan-rerun", action="store_true")
    args = parser.parse_args(argv)
    rerun = not getattr(args, "no_scan_rerun", False)
    try:
        if args.command in ("gate", "prefreeze"):
            entry = prefreeze_validation if args.command == "prefreeze" else freeze_gate
            report = entry(
                args.contract, args.protocol, args.record, repo_root=args.repo_root, rerun_scan=rerun
            )
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["gate"] == "PASS" else 3
        result = build_execution_plan(
            args.contract,
            args.protocol,
            args.record,
            repo_root=args.repo_root,
            authority_path=args.authority,
            rerun_scan=rerun,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ContractError as exc:
        print(json.dumps({"gate": "FREEZE_GATE_FAIL", "error": str(exc)}, ensure_ascii=False))
        return 3
    except OSError as exc:
        print(json.dumps({"gate": "FREEZE_GATE_FAIL", "error": f"read error: {exc}"}, ensure_ascii=False))
        return 4


if __name__ == "__main__":
    sys.exit(main())
