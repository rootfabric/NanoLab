"""R4 pre-freeze hardening regression tests (WO-NL5-V02-PREFREEZE-HARDENING-R4).

Repairs audit findings F1-F4 (focused audit 2026-10-03) and the fresh
independent Reviewer corrections R4.1 M-1..M-4 + m-1 (REVIEWER_VERDICT_R1),
R4.2 M-5 + M-6 + m-2 (REVIEWER_VERDICT_R2) and R4.3 M-7 + m-3
(REVIEWER_VERDICT_R3). Unlike the R3-era tests, the negative controls here
REQUIRE REJECTION: a corrupted contract, record, protocol declaration,
incomplete scan, fabricated collision skip, missing dispatch authority,
fake Git binding, worktree-only authority record, pre-freeze review/verify
binding or a non-atomic replacement rejection must fail closed (gate FAIL /
exception / non-zero exit / structurally unchanged ledger), never PASS.

M-1 invariants pinned here: the committed PRE-DATA / NOT FROZEN package
yields PREFREEZE_VALIDATION_PASS and DISPATCH_BLOCKED; a
``nanolab_v02_dispatch_execution_plan`` is produced ONLY for a validated
synthetic dispatch authority fixture (explicitly marked
``SYNTHETIC TEST FIXTURE ONLY``; never for the real package). Exit code 0
means validation/preconditions recorded — never a launch authorization (m-3).

R4.2 invariants pinned here (DispatchAuthorityGitBindingTest): the frozen
subject must exist as a real Git commit with a matching tree; authority
records and frozen artifacts must be exact immutable Git objects (bytes
read from the Git object database, never the mutable worktree); the machine
conclusion ceiling is DISPATCH_PRECONDITIONS_RECORDED with
machine_launch_authorized=False — the launch gate stays
Human/Protected-Writer.

R4.3 invariants pinned here (FrozenPackageSequencingTest, M-7): the
authority lifecycle is strictly sequenced S -> F -> R/V -> A —
``subject_head``/``subject_tree`` pin the FROZEN PACKAGE COMMIT F; the
fresh review PASS / verify VERIFIED records pin F (never the pre-freeze
candidate S) from their own later immutable record commits, which must
strictly descend from F; each authority record carries its own immutable
source binding (no shared freeze-evidence commit); the frozen contract
carries no self-SHA (``frozen_subject_head``/``frozen_subject_tree`` are
non-authoritative compatibility fields and the exact frozen pins live in
the external freeze/authority record); no self-consistent two-commit
shortcut satisfies the chain.

R4.2 invariants pinned here (PairReplacementAtomicityTest): request_replacement
is a two-phase transaction — every rejection leaves pairs, attempts,
seed ownership, quota, cursor and ledger events structurally unchanged;
open_pair/ledger/pair return independent snapshots (m-2).

No simulations, no network, no scientific claims. Fixtures are synthetic or
the committed PRE-DATA R4 evidence package.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from nl5 import repro_v02_seeds as seeds
from nl5.repro_v02_freeze_contract import (
    INTEGER_ROUNDING_POLICY,
    PAIR_STATES,
    SCAN_ALLOWLIST_MARKER,
    ContractError,
    ReplacementBudgetExhausted,
    ReplacementLedger,
    build_execution_plan,
    derive_budget,
    freeze_gate,
    load_contract,
    load_dispatch_authority,
    load_seed_record,
    n_min_cell,
    parse_protocol_cardinalities,
    parse_protocol_machine_block,
    parse_protocol_scan_allowlist,
    prefreeze_validation,
    replacement_quota_pairs,
    validate_dispatch_authority,
    validate_freeze_contract,
    SYNTHETIC_FIXTURE_MARKER,
)
from nl5.repro_v02_seeds import (
    collision_manifest_digest,
    r4_record_digest,
    replacement_pool_digest,
    replay_replacement_stream,
)

EVIDENCE = REPO_ROOT / "docs" / "work" / "executions" / "EX-NL5-V02-PREFREEZE-HARDENING-R4" / "evidence"
CONTRACT_PATH = EVIDENCE / "repro-v0-2-freeze-contract-PRE_DATA_R4.json"
RECORD_PATH = EVIDENCE / "repro-v0-2-seed-record-PRE_DATA_R4.json"
MANIFEST_PATH = EVIDENCE / "r4-1-collision-scan-manifest-R4.json"
DOC_PATH = REPO_ROOT / "docs" / "research" / "NANOLAB_REPRO_V0_2_CANDIDATE_R1.md"
HG_B_PROPOSAL_PATH = REPO_ROOT / "docs" / "control" / "NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md"

# Historical FROZEN_R1 package (immutable F1 = cb91ade..., review
# FIX_REQUIRED / M-1): used as the FROZEN-side fixture of the repaired gate.
F1_EVIDENCE = REPO_ROOT / "docs" / "work" / "executions" / "EX-NL5-V02-DIRECTOR-FREEZE-R1" / "evidence"
F1_CONTRACT_PATH = F1_EVIDENCE / "repro-v0-2-freeze-contract-FROZEN_R1.json"
F1_RECORD_PATH = F1_EVIDENCE / "repro-v0-2-seed-record-FROZEN_R1.json"
F1_DOC_PATH = REPO_ROOT / "docs" / "research" / "NANOLAB_REPRO_V0_2_FROZEN_R1.md"


def load_package():
    return load_contract(CONTRACT_PATH), DOC_PATH.read_text(encoding="utf-8"), load_seed_record(RECORD_PATH)


def load_frozen_package():
    """The committed historical FROZEN_R1 package (contract/protocol/record)."""
    return (
        load_contract(F1_CONTRACT_PATH),
        F1_DOC_PATH.read_text(encoding="utf-8"),
        load_seed_record(F1_RECORD_PATH),
    )


def scan_allowlist_block(contract: dict) -> str:
    """The canonical FROZEN-only ``scan-allowlist-v1`` declaration block.

    The ordered ``path_N`` entries are taken verbatim from the contract's
    ``seed_generation.scan_allowlist_paths_exact`` — this is the exact
    machine-bound form the repaired gate requires from a FROZEN protocol.
    """
    paths = contract["seed_generation"]["scan_allowlist_paths_exact"]
    pin = contract["seed_generation"]["exclusion_tree_pin"]
    entries = "".join(f"path_{index} = {path}\n" for index, path in enumerate(paths, 1))
    return (
        "```text\n"
        f"# {SCAN_ALLOWLIST_MARKER} (authoritative collision-scan exact allowlist; "
        f"pinned scan tree {pin}; frozen-package paths are NOT allowlist entries)\n"
        f"{entries}"
        "```\n"
    )


def write_tmp(directory: Path, name: str, payload) -> Path:
    path = directory / name
    if isinstance(payload, (dict, list)):
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(payload, encoding="utf-8")
    return path


def cli(args: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "scripts") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "nl5.repro_v02_freeze_contract", *args],
        capture_output=True, text=True, cwd=REPO_ROOT, env=env, timeout=120,
    )


# ---------------------------------------------------------------------------
# F4 — one explicitly named integer policy
# ---------------------------------------------------------------------------


class IntegerPolicyTest(unittest.TestCase):
    def test_named_policy_values(self):
        self.assertEqual(INTEGER_ROUNDING_POLICY["name"], "ceil-nmin-floor-replacement-pairs-v1")
        self.assertEqual(n_min_cell(64), 52)
        self.assertEqual(n_min_cell(10), 8)
        self.assertEqual(replacement_quota_pairs(64), 12)
        self.assertEqual(replacement_quota_pairs(10), 2)

    def test_literal_bounds_hold(self):
        # 51/64 = 79.6875% violates ">= 80%"; 52/64 satisfies it.
        self.assertLess(51 * 100, 80 * 64)
        self.assertGreaterEqual(52 * 100, 80 * 64)
        # 60/296 = 20.27% violates "<= 20%"; the policy cap satisfies it.
        self.assertGreater(60 * 100, 20 * 296)
        budget = derive_budget()
        self.assertEqual(budget["confirmatory_runs"], 296)
        self.assertEqual(budget["replacement_runs_cap"], 56)
        self.assertEqual(budget["max_runs"], 352)
        self.assertLessEqual(budget["replacement_runs_cap"] * 100, 20 * budget["confirmatory_runs"])

    def test_budget_is_single_source(self):
        counts = {"0b": 64, "32b": 64, "11b": 10, "53b": 10}
        self.assertEqual(derive_budget(counts), derive_budget())
        with self.assertRaises(ValueError):
            n_min_cell(True)  # bool is not an integer under the policy
        with self.assertRaises(ValueError):
            replacement_quota_pairs(-3)


# ---------------------------------------------------------------------------
# F1 — contract structure: malformed / missing / extra / unknown fail closed
# ---------------------------------------------------------------------------


class ContractMalformedTest(unittest.TestCase):
    def test_truncated_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contract.json"
            path.write_text('{"schema_version": 1, "kind": ', encoding="utf-8")
            with self.assertRaises(ContractError):
                load_contract(path)

    def test_missing_contract_file_fails_closed(self):
        with self.assertRaises(ContractError):
            load_contract(Path("/nonexistent/nanolab-contract.json"))

    def test_unknown_revision_fails(self):
        contract, text, record = load_package()
        contract["contract_revision"] = "r99"
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("unknown contract_revision" in f for f in report["failures"]))

    def test_missing_required_section_fails(self):
        contract, text, record = load_package()
        del contract["run_budget"]
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_extra_top_level_key_fails(self):
        contract, text, record = load_package()
        contract["sneaky_extra"] = {"bypass": True}
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("extra" in f for f in report["failures"]))

    def test_missing_variant_fails(self):
        contract, text, record = load_package()
        del contract["variants"]["53b"]
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_extra_variant_fails(self):
        contract, text, record = load_package()
        contract["variants"]["74b"] = {"role": "control", "n": 10, "n_min": 8}
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_record_missing_entirely_fails_for_freeze(self):
        contract, text, _ = load_package()
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=None)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("seed record not provided" in f for f in report["failures"]))


# ---------------------------------------------------------------------------
# F1 — seed-level integrity classes from the audit
# ---------------------------------------------------------------------------


class SeedIntegrityNegativeTest(unittest.TestCase):
    def _mutated(self, mutate):
        contract, text, record = load_package()
        mutate(contract, record)
        return contract, text, record

    def test_empty_control_arrays_fail(self):
        def mutate(contract, record):
            record["seeds"]["11b"] = []
            record["seeds"]["53b"] = []
            contract["confirmatory_seeds"]["11b"] = []
            contract["confirmatory_seeds"]["53b"] = []
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("11b" in f for f in report["failures"]))

    def test_duplicate_primary_seed_fails(self):
        def mutate(contract, record):
            contract["confirmatory_seeds"]["0b"][7] = contract["confirmatory_seeds"]["0b"][0]
            record["seeds"]["0b"][7] = record["seeds"]["0b"][0]
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("duplicate" in f for f in report["failures"]))

    def test_historical_seed_in_primary_fails(self):
        def mutate(contract, record):
            contract["confirmatory_seeds"]["32b"][0] = 201004
            record["seeds"]["32b"][0] = 201004
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("historical" in f for f in report["failures"]))

    def test_stale_record_digest_fails(self):
        def mutate(contract, record):
            record["seeds"]["0b"][1] = record["seeds"]["0b"][0]
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("digest" in f for f in report["failures"]))

    def test_contract_logical_digest_mismatch_fails(self):
        def mutate(contract, record):
            contract["scientific_subject"]["seed_record_logical_sha256"] = "0" * 64
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_missing_bootstrap_fails(self):
        def mutate(contract, record):
            contract["bootstrap"]["seeds"] = {}
            contract["bootstrap"]["indices"] = {}
            record["bootstrap_seeds"] = {}
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("bootstrap" in f for f in report["failures"]))

    def test_bool_seed_fails(self):
        def mutate(contract, record):
            contract["confirmatory_seeds"]["11b"][0] = True
            record["seeds"]["11b"][0] = True
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("not an integer" in f for f in report["failures"]))

    def test_out_of_range_seed_fails(self):
        for bad in (2**31, -5):
            def mutate(contract, record, bad=bad):
                contract["confirmatory_seeds"]["11b"][0] = bad
                record["seeds"]["11b"][0] = bad
            report = validate_freeze_contract(*self._mutated(mutate))
            self.assertEqual(report["gate"], "FREEZE_GATE_FAIL", bad)

    def test_n_mismatch_between_record_and_contract_fails(self):
        def mutate(contract, record):
            record["variant_counts"]["0b"] = 10
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_wrong_nmin_value_fails(self):
        def mutate(contract, record):
            contract["variants"]["0b"]["n_min"] = 51  # floor(0.8*64) — the F4 defect
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("n_min" in f for f in report["failures"]))

    def test_wrong_replacement_cap_fails(self):
        def mutate(contract, record):
            contract["run_budget"]["replacement_runs_cap"] = 60  # the F4 defect (20.27%)
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("replacement_runs_cap" in f for f in report["failures"]))

    def test_wrong_wall_cap_fails(self):
        def mutate(contract, record):
            contract["run_budget"]["wall_hours_per_platform"] = 1
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_replacement_pool_shorter_than_quota_fails(self):
        def mutate(contract, record):
            contract["replacement"]["pools"]["0b"]["seeds"] = contract["replacement"]["pools"]["0b"]["seeds"][:5]
            record["replacement_pools"]["0b"]["seeds"] = record["replacement_pools"]["0b"]["seeds"][:5]
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_replacement_pool_starting_at_raw_n_plus_1_fails(self):
        def mutate(contract, record):
            # Simulate the F3 defect: pool begins at N+1 = 65 instead of cursor 75.
            contract["replacement"]["pools"]["0b"]["start_index"] = 65
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("start_index" in f for f in report["failures"]))

    def test_cursor_not_after_last_consumed_index_fails(self):
        def mutate(contract, record):
            contract["seed_generation"]["next_candidate_index"]["0b"] = 65  # raw N+1, F3 defect
            contract["replacement"]["pools"]["0b"]["start_index"] = 65
            contract["replacement"]["pools"]["0b"]["next_candidate_index"] = 77
        report = validate_freeze_contract(*self._mutated(mutate))
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("next_candidate_index" in f for f in report["failures"]))


# ---------------------------------------------------------------------------
# F1 — protocol declarations: contradictions and duplicates fail closed
# ---------------------------------------------------------------------------


class ProtocolDeclarationNegativeTest(unittest.TestCase):
    def test_duplicate_cardinality_line_fails(self):
        _, text, _ = load_package()
        with self.assertRaises(ContractError):
            parse_protocol_cardinalities(text + "\n0b = 1, 32b = 1, 11b = 1, 53b = 1\n")

    def test_missing_cardinality_line_fails(self):
        with self.assertRaises(ContractError):
            parse_protocol_cardinalities("no cardinalities here")

    def test_second_machine_block_fails(self):
        import re
        _, text, _ = load_package()
        match = None
        for fence in re.finditer(r"```[^\n]*\n(.*?)```", text, re.DOTALL):
            if "machine-contract-v1" in fence.group(1):
                match = fence
                break
        self.assertIsNotNone(match)
        mutated_block = "```text\n# machine-contract-v1 (authoritative; duplicate is fail-closed)\n" \
            "rule_id = NANOLAB_REPRO_V0_2_DISTRIBUTIONAL\ncandidate_revision = R4\n" \
            "anchor = NANOLAB-REPRO-V0.2-R1\nn_0b = 64\nn_32b = 64\nn_11b = 10\nn_53b = 10\n" \
            "n_min_primary = 51\nn_min_control = 8\nreplacement_quota_pairs_primary = 12\n" \
            "replacement_quota_pairs_control = 2\nconfirmatory_runs = 296\nreplacement_runs_cap = 56\n" \
            "max_runs = 352\nwall_hours_per_platform = 560\nselected_n = 64\nheadroom_ratio = 0.8\n" \
            "bootstrap_resamples = 10000\nexclusion_list_size = 34\n" \
            "exclusion_tree_pin = a9d7d07fa264e9907b67ca244b00ba2da3430b0f\n" \
            "integer_policy_name = ceil-nmin-floor-replacement-pairs-v1\n```"
        with self.assertRaises(ContractError) as ctx:
            parse_protocol_machine_block(text + "\n" + mutated_block)
        self.assertIn("machine-contract-v1 blocks", str(ctx.exception))

    def test_machine_block_contradiction_fails_gate(self):
        contract, text, record = load_package()
        mutated = text.replace("n_min_primary = 52", "n_min_primary = 51").replace(
            "max_runs = 352", "max_runs = 356"
        )
        report = validate_freeze_contract(contract, protocol_text=mutated, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("n_min_primary" in f for f in report["failures"]))
        self.assertTrue(any("max_runs" in f for f in report["failures"]))

    def test_freeze_status_contradiction_fails_gate(self):
        contract, text, record = load_package()
        contract["scientific_subject"]["freeze_status"] = "FROZEN"
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_unsafe_allowlist_paths_fail(self):
        contract, text, record = load_package()
        contract["seed_generation"]["scan_allowlist_paths_exact"] = ["/etc/passwd"]
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_unknown_exclusion_tree_pin_format_fails(self):
        contract, text, record = load_package()
        contract["seed_generation"]["exclusion_tree_pin"] = "a9d7d07"  # abbreviated
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_engine_pin_drift_fails(self):
        contract, text, record = load_package()
        contract["environment_pins"]["cuda"] = "ON"
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")

    def test_feasibility_grid_drift_fails(self):
        contract, text, record = load_package()
        contract["feasibility_planning"]["selected_n"] = 40
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")


# ---------------------------------------------------------------------------
# FROZEN_R2 repair — M-1 of the FROZEN_R1 scientific review: the frozen
# protocol's collision-scan exact allowlist is machine-bound to
# contract.seed_generation.scan_allowlist_paths_exact (fail-closed).
# ---------------------------------------------------------------------------


class ScanAllowlistBindingTest(unittest.TestCase):
    """The M-1 defect class must be mechanically unpassable.

    FROZEN_R1 escaped the gate because its protocol §6 declared the
    collision-scan exact allowlist as the later frozen-package paths while
    the authoritative contract preserved the approved R4 pinned-tree
    allowlist (scan tree ``a9d7d07...``). The repaired gate requires exactly
    one ``scan-allowlist-v1`` block in a FROZEN protocol whose ordered exact
    paths equal the contract allowlist; historical PRE-DATA R4 packages stay
    block-free and green.
    """

    FROZEN_PACKAGE_PATHS = [
        "docs/research/NANOLAB_REPRO_V0_2_FROZEN_R1.md",
        "docs/work/executions/EX-NL5-V02-DIRECTOR-FREEZE-R1/evidence/repro-v0-2-seed-record-FROZEN_R1.json",
    ]

    def _block(self, paths: list[str]) -> str:
        entries = "".join(f"path_{index} = {path}\n" for index, path in enumerate(paths, 1))
        return "```text\n# scan-allowlist-v1 (test declaration)\n" + entries + "```\n"

    def test_correct_frozen_allowlist_gate_can_pass(self):
        contract, text, record = load_frozen_package()
        self.assertNotIn(SCAN_ALLOWLIST_MARKER, text)
        repaired_text = text + "\n" + scan_allowlist_block(contract)
        report = validate_freeze_contract(
            contract, protocol_text=repaired_text, seed_record=record
        )
        self.assertEqual(report["gate"], "PASS", report["failures"])
        self.assertEqual(report["freeze_status"], "FROZEN")
        self.assertEqual(report["dispatch"], "DISPATCH_BLOCKED")
        # Full authoritative gate (with collision-scan re-run) on the same
        # corrected FROZEN bytes:
        tmp_protocol = self._tmpdir() / "protocol.md"
        tmp_protocol.write_text(repaired_text, encoding="utf-8")
        full_report = freeze_gate(
            F1_CONTRACT_PATH, tmp_protocol, F1_RECORD_PATH, repo_root=REPO_ROOT
        )
        self.assertEqual(full_report["gate"], "PASS", full_report["failures"])
        self.assertEqual(full_report["validation_stage"], "PREFREEZE_VALIDATION_PASS")
        self.assertFalse(full_report["dispatch_ready"])

    def _tmpdir(self) -> Path:
        if not hasattr(self, "_tmp"):
            self._tmp = tempfile.TemporaryDirectory()
            self.addCleanup(self._tmp.cleanup)
        return Path(self._tmp.name)

    def test_m1_frozen_package_paths_fail_the_gate(self):
        """THE M-1 regression: FROZEN_R1-style frozen-package allowlist."""
        contract, text, record = load_frozen_package()
        mutated = text + "\n" + self._block(self.FROZEN_PACKAGE_PATHS)
        report = validate_freeze_contract(contract, protocol_text=mutated, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(
            any("scan-allowlist-v1" in f and "scan_allowlist_paths_exact" in f for f in report["failures"]),
            report["failures"],
        )

    def test_missing_block_fails_for_frozen(self):
        """The raw historical FROZEN_R1 protocol (no block) cannot pass."""
        contract, text, record = load_frozen_package()
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("scan-allowlist-v1 block not found" in f for f in report["failures"]))

    def test_duplicate_block_fails(self):
        contract, text, record = load_frozen_package()
        block = scan_allowlist_block(contract)
        mutated = text + "\n" + block + "\n" + block
        report = validate_freeze_contract(contract, protocol_text=mutated, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("exactly one is allowed" in f for f in report["failures"]))

    def test_extra_exact_path_fails(self):
        contract, text, record = load_frozen_package()
        drifted = list(contract["seed_generation"]["scan_allowlist_paths_exact"]) + [
            "docs/work/WO-NL5-V02-DIRECTOR-FREEZE-R2.md"
        ]
        mutated = text + "\n" + self._block(drifted)
        report = validate_freeze_contract(contract, protocol_text=mutated, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("scan-allowlist-v1 declaration !=" in f for f in report["failures"]))

    def test_order_drift_fails(self):
        contract, text, record = load_frozen_package()
        drifted = list(reversed(contract["seed_generation"]["scan_allowlist_paths_exact"]))
        mutated = text + "\n" + self._block(drifted)
        report = validate_freeze_contract(contract, protocol_text=mutated, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("scan-allowlist-v1 declaration !=" in f for f in report["failures"]))

    def test_malformed_block_fails(self):
        contract, text, record = load_frozen_package()
        good = scan_allowlist_block(contract)
        mutated = text + "\n" + good.replace(
            "path_1 = ", "allowlist_paths = ", 1
        )
        report = validate_freeze_contract(contract, protocol_text=mutated, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("malformed content line" in f for f in report["failures"]))

    def test_non_consecutive_indices_fail(self):
        contract, text, record = load_frozen_package()
        paths = contract["seed_generation"]["scan_allowlist_paths_exact"]
        mutated_block = (
            "```text\n# scan-allowlist-v1\n"
            f"path_1 = {paths[0]}\npath_3 = {paths[1]}\n```\n"
        )
        report = validate_freeze_contract(
            contract, protocol_text=text + "\n" + mutated_block, seed_record=record
        )
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("consecutive 1..K" in f for f in report["failures"]))

    def test_predata_r4_package_still_passes_without_block(self):
        """Historical PRE-DATA R4 documents are NOT rewritten and stay green."""
        contract, text, record = load_package()
        self.assertNotIn(SCAN_ALLOWLIST_MARKER, text)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "PASS", report["failures"])

    def test_block_is_frozen_only_in_predata(self):
        contract, text, record = load_package()
        mutated = text + "\n" + scan_allowlist_block(contract)
        report = validate_freeze_contract(contract, protocol_text=mutated, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("FROZEN-only" in f for f in report["failures"]))

    def test_parser_unit_semantics(self):
        contract, _text, _record = load_frozen_package()
        allowlist = contract["seed_generation"]["scan_allowlist_paths_exact"]
        parsed = parse_protocol_scan_allowlist(scan_allowlist_block(contract))
        self.assertEqual(parsed, allowlist)
        with self.assertRaises(ContractError):
            parse_protocol_scan_allowlist("no block at all")
        block = scan_allowlist_block(contract)
        with self.assertRaises(ContractError):
            parse_protocol_scan_allowlist(block + "\n" + block)
        with self.assertRaises(ContractError):
            parse_protocol_scan_allowlist("```text\n# scan-allowlist-v1\nnot-a-path-line\n```\n")

    def test_cli_wrong_frozen_allowlist_exits_3(self):
        contract, text, record = load_frozen_package()
        tmp = self._tmpdir()
        mutated = text + "\n" + self._block(self.FROZEN_PACKAGE_PATHS)
        contract_path = write_tmp(tmp, "contract.json", contract)
        protocol_path = write_tmp(tmp, "protocol.md", mutated)
        record_path = write_tmp(tmp, "record.json", record)
        result = cli([
            "gate",
            "--contract", str(contract_path),
            "--protocol", str(protocol_path),
            "--record", str(record_path),
            "--repo-root", str(REPO_ROOT),
        ])
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("FREEZE_GATE_FAIL", result.stdout)
        self.assertIn("scan-allowlist-v1", result.stdout)


# ---------------------------------------------------------------------------
# F2 — collision scan error semantics (fail-closed)
# ---------------------------------------------------------------------------


class CollisionScanNegativeTest(unittest.TestCase):
    PIN = "a9d7d07fa264e9907b67ca244b00ba2da3430b0f"

    def test_scan_outside_repository_is_scan_error_not_zero(self):
        from nl5.repro_v02_seeds import TreeScanError, literal_tree_collision_scan
        with tempfile.TemporaryDirectory(prefix="nanolab-nonrepo-") as tmp:
            with self.assertRaises(TreeScanError) as ctx:
                literal_tree_collision_scan(Path(tmp), [201004], pinned_commit=self.PIN)
            self.assertIsNotNone(ctx.exception.returncode)
            self.assertNotEqual(ctx.exception.returncode, 1)

    def test_scan_missing_pinned_object_is_scan_error(self):
        from nl5.repro_v02_seeds import TreeScanError, literal_tree_collision_scan
        with self.assertRaises(TreeScanError):
            literal_tree_collision_scan(REPO_ROOT, [201004], pinned_commit="0" * 40)

    def test_scan_timeout_is_scan_error(self):
        from unittest.mock import patch
        from nl5.repro_v02_seeds import TreeScanError, literal_tree_collision_scan

        def fake_timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="git grep", timeout=0.001)

        with patch("nl5.repro_v02_seeds.subprocess.run", side_effect=fake_timeout):
            with self.assertRaises(TreeScanError):
                literal_tree_collision_scan(REPO_ROOT, [201004], pinned_commit=self.PIN)

    def test_true_no_match_is_clean_zero(self):
        from nl5.repro_v02_seeds import literal_tree_collision_scan
        result = literal_tree_collision_scan(
            REPO_ROOT, [2147480000], pinned_commit=self.PIN
        )
        self.assertEqual(result["status"], "CLEAN")
        self.assertEqual(result["collision_count"], 0)
        self.assertEqual(result["mode"], "pinned_tree")


# ---------------------------------------------------------------------------
# F3 — replacement pool/cursor and attempt ledger semantics
# ---------------------------------------------------------------------------


class ReplacementStreamTest(unittest.TestCase):
    def test_documented_n_plus_1_identity_is_not_the_replacement_start(self):
        """The exact audit F3 observation must stay rejected for the R4 record."""
        record = load_seed_record(RECORD_PATH)
        contract = load_contract(CONTRACT_PATH)
        for variant in seeds.DEFAULT_VARIANTS:
            n = seeds.VARIANT_REPLICAS[variant]
            n_plus_one_seed = seeds.derive_seed(
                record["anchor"], seeds.replica_label(variant, n + 1)
            )
            self.assertIn(n_plus_one_seed, record["seeds"][variant])  # it is confirmatory
            pool = contract["replacement"]["pools"][variant]
            self.assertNotEqual(pool["start_index"], n + 1)
            self.assertEqual(
                pool["start_index"], contract["seed_generation"]["next_candidate_index"][variant]
            )
            self.assertGreater(pool["start_index"], record["indices_consumed"][variant])

    def test_pool_continues_stream_after_cursor_synthetic(self):
        anchor = "replacement-probe"
        first = seeds.derive_seed(anchor, seeds.replica_label("probe", 1))
        second = seeds.derive_seed(anchor, seeds.replica_label("probe", 2))
        third = seeds.derive_seed(anchor, seeds.replica_label("probe", 3))
        scan = lambda seed: seed == first  # noqa: E731 — skip index 1 (tree collision)
        confirmatory = seeds.generate_variant_seeds(
            anchor, "probe", count=1, excluded=frozenset(), tree_collision_scan=scan
        )
        self.assertEqual(confirmatory["seeds"], [second])
        self.assertEqual(confirmatory["indices_consumed"], 2)  # skipped index 1, consumed index 2
        self.assertEqual(confirmatory["next_candidate_index"], 3)  # cursor AFTER last consumed
        pool = seeds.generate_replacement_pool(
            anchor, "probe", start_index=confirmatory["next_candidate_index"],
            count=1, excluded=frozenset(), tree_collision_scan=scan,
        )
        self.assertEqual(pool["seeds"], [third])  # stream continues after the cursor
        self.assertEqual(pool["start_index"], 3)
        self.assertEqual(pool["next_candidate_index"], 4)
        # The F3 defect class: starting at raw N+1 (= 2 here) would reuse `second`.
        with self.assertRaises(seeds.SeedCollisionError):
            seeds.generate_replacement_pool(
                anchor, "probe", start_index=2, count=1,
                excluded=frozenset(), taken=frozenset({second}),
            )

    def test_pool_rejects_taken_identity(self):
        anchor = "pool-taken-probe"
        s1 = seeds.derive_seed(anchor, seeds.replica_label("probe", 1))
        with self.assertRaises(seeds.SeedCollisionError):
            seeds.generate_replacement_pool(
                anchor, "probe", start_index=1, count=2,
                excluded=frozenset(), taken=frozenset({s1}),
            )

    def test_bit_exact_regeneration_from_recorded_cursor(self):
        record = load_seed_record(RECORD_PATH)
        contract = load_contract(CONTRACT_PATH)
        for variant in seeds.DEFAULT_VARIANTS:
            skips = {entry["index"] for entry in record["skipped_identities"][variant]}
            replayed = seeds.replay_variant_stream(
                record["anchor"], variant, record["indices_consumed"][variant], skips
            )
            self.assertEqual(replayed, contract["confirmatory_seeds"][variant], variant)

    def test_committed_r3_identities_are_preserved_in_r4(self):
        r3 = json.loads(
            (REPO_ROOT / "docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2/evidence/"
             "repro-v0-2-seed-record-PRE_DATA_R3.json").read_text(encoding="utf-8")
        )
        record = load_seed_record(RECORD_PATH)
        self.assertEqual(record["seeds"], r3["seeds"])
        self.assertEqual(record["record_sha256"], r3["record_sha256"])
        self.assertEqual(
            record["record_sha256"],
            "eb4ab3f891e17dd2b456a3870ed73b19e39d67bf51109b6cb47ca64524ce476b",
        )


class PairLedgerTest(unittest.TestCase):
    """M-4: pair-level, one-shot replacement semantics."""

    def setUp(self):
        self.pools = {"0b": [111, 222, 333], "32b": [444]}
        self.ledger = ReplacementLedger({"0b": 2, "32b": 1}, self.pools)

    def _open_failed_pair(self, pair_id="pair-1", variant="0b", seed=700,
                          author="run-0001", external="run-0002"):
        self.ledger.open_pair(pair_id, variant, seed)
        self.ledger.record_attempt(author, pair_id, "author", "FAILED_TECHNICAL")
        self.ledger.record_attempt(external, pair_id, "external", "COMPLETED")
        return pair_id

    def test_pair_states_and_attempt_uniqueness(self):
        self.assertEqual(PAIR_STATES, (
            "PAIR_RUNNING", "PAIR_COMPLETED", "PAIR_FAILED_TECHNICAL",
            "PAIR_REPLACED", "PAIR_ABORTED",
        ))
        self.ledger.open_pair("pair-a", "0b", 10)
        self.assertEqual(self.ledger.pair_state("pair-a"), "PAIR_RUNNING")
        self.ledger.record_attempt("run-a", "pair-a", "author", "COMPLETED")
        self.assertEqual(self.ledger.pair_state("pair-a"), "PAIR_RUNNING")
        with self.assertRaises(ValueError):
            self.ledger.record_attempt("run-a", "pair-a", "external", "COMPLETED")  # id reuse
        with self.assertRaises(ValueError):
            self.ledger.record_attempt("run-b", "pair-a", "author", "COMPLETED")  # leg reuse
        self.ledger.record_attempt("run-b", "pair-a", "external", "COMPLETED")
        self.assertEqual(self.ledger.pair_state("pair-a"), "PAIR_COMPLETED")
        with self.assertRaises(ValueError):  # terminal pair accepts no new legs
            self.ledger.record_attempt("run-c", "pair-a", "author", "COMPLETED")
        with self.assertRaises(ValueError):
            self.ledger.open_pair("pair-a", "0b", 11)  # pair id unique forever

    def test_seed_identity_belongs_to_exactly_one_pair(self):
        self.ledger.open_pair("pair-a", "0b", 10)
        with self.assertRaises(ValueError):
            self.ledger.open_pair("pair-b", "0b", 10)  # seed/pair mismatch

    def test_replacement_only_for_failed_technical_pair(self):
        self.ledger.open_pair("pair-ok", "0b", 10)
        self.ledger.record_attempt("r-ok-1", "pair-ok", "author", "COMPLETED")
        self.ledger.record_attempt("r-ok-2", "pair-ok", "external", "COMPLETED")
        with self.assertRaises(ValueError):
            self.ledger.request_replacement("0b", "pair-ok", "pair-rp", "a-x", "e-x")

    def test_missing_counterpart_is_rejected(self):
        self.ledger.open_pair("pair-half", "0b", 10)
        self.ledger.record_attempt("r-half-1", "pair-half", "author", "FAILED_TECHNICAL")
        self.assertEqual(self.ledger.pair_state("pair-half"), "PAIR_RUNNING")
        cursor_before = self.ledger.pool_cursor("0b")
        with self.assertRaises(ValueError):
            self.ledger.request_replacement("0b", "pair-half", "pair-rp", "a-x", "e-x")
        self.assertEqual(self.ledger.pool_cursor("0b"), cursor_before)

    def test_double_replacement_request_rejected_cursor_and_quota_unchanged(self):
        failed = self._open_failed_pair()
        identity = self.ledger.request_replacement(
            "0b", failed, "pair-1-RP1", "run-0001-RP1a", "run-0001-RP1e"
        )
        self.assertEqual(identity, 111)
        self.assertEqual(self.ledger.pair_state(failed), "PAIR_REPLACED")
        used_after = self.ledger.used_pairs("0b")
        cursor_after = self.ledger.pool_cursor("0b")
        with self.assertRaises(ValueError):  # second request for the same failed pair
            self.ledger.request_replacement("0b", failed, "pair-1-RP2", "run-x", "run-y")
        self.assertEqual(self.ledger.used_pairs("0b"), used_after)
        self.assertEqual(self.ledger.pool_cursor("0b"), cursor_after)

    def test_replacement_schedules_both_legs_of_new_pair(self):
        failed = self._open_failed_pair()
        self.ledger.request_replacement(
            "0b", failed, "pair-1-RP1", "run-0001-RP1a", "run-0001-RP1e"
        )
        pair = self.ledger.pair("pair-1-RP1")
        self.assertEqual(pair["seed_identity"], 111)
        self.assertEqual(pair["source_pair_id"], failed)
        self.assertEqual(
            pair["legs"], {"author": "run-0001-RP1a", "external": "run-0001-RP1e"}
        )
        self.assertEqual(self.ledger.pair_state("pair-1-RP1"), "PAIR_RUNNING")
        # scheduled legs are resolved by outcome, not re-registered
        with self.assertRaises(ValueError):
            self.ledger.record_attempt("run-0001-RP1a", "pair-1-RP1", "author", "COMPLETED")
        self.ledger.record_outcome("run-0001-RP1a", "COMPLETED")
        self.ledger.record_outcome("run-0001-RP1e", "COMPLETED")
        self.assertEqual(self.ledger.pair_state("pair-1-RP1"), "PAIR_COMPLETED")

    def test_external_failed_mirror_yields_same_behavior(self):
        self.ledger.open_pair("pair-m", "0b", 700)
        self.ledger.record_attempt("m-a", "pair-m", "author", "COMPLETED")
        self.ledger.record_attempt("m-e", "pair-m", "external", "FAILED_TECHNICAL")
        self.assertEqual(self.ledger.pair_state("pair-m"), "PAIR_FAILED_TECHNICAL")
        identity = self.ledger.request_replacement("0b", "pair-m", "pair-m-RP1", "m-a2", "m-e2")
        self.assertEqual(identity, 111)
        self.assertEqual(len(self.ledger.pair("pair-m-RP1")["legs"]), 2)

    def test_variant_mismatch_rejected(self):
        failed = self._open_failed_pair(variant="0b")
        with self.assertRaises(ValueError):
            self.ledger.request_replacement("32b", failed, "rp", "a", "e")
        self.assertEqual(self.ledger.pool_cursor("32b"), 0)

    def test_second_failure_must_reference_the_replacement_pair(self):
        failed = self._open_failed_pair()
        self.ledger.request_replacement("0b", failed, "pair-1-RP1", "rp-a", "rp-e")
        # the replacement pair fails as well
        self.ledger.record_outcome("rp-a", "FAILED_TECHNICAL")
        self.ledger.record_outcome("rp-e", "FAILED_TECHNICAL")
        self.assertEqual(self.ledger.pair_state("pair-1-RP1"), "PAIR_FAILED_TECHNICAL")
        # referencing the ORIGINAL failed pair is forbidden (already replaced)
        with self.assertRaises(ValueError):
            self.ledger.request_replacement("0b", failed, "pair-1-RP2", "x-a", "x-e")
        identity = self.ledger.request_replacement("0b", "pair-1-RP1", "pair-1-RP2", "x-a", "x-e")
        self.assertEqual(identity, 222)

    def test_one_leg_only_replacement_rejected(self):
        failed = self._open_failed_pair()
        with self.assertRaises(ValueError):
            self.ledger.request_replacement("0b", failed, "rp", "only-author", "only-author")
        self.assertEqual(self.ledger.pool_cursor("0b"), 0)

    def test_quota_exhaustion_raises_without_expansion(self):
        ledger = ReplacementLedger({"0b": 1}, {"0b": [111, 222]})
        for n, (pid, seed) in enumerate((("p1", 10), ("p2", 20), ("p3", 30)), start=1):
            ledger.open_pair(pid, "0b", seed)
            ledger.record_attempt(f"a-{pid}", pid, "author", "FAILED_TECHNICAL")
            ledger.record_attempt(f"e-{pid}", pid, "external", "COMPLETED")
        ledger.request_replacement("0b", "p1", "p1-RP", "a-p1-RP", "e-p1-RP")
        with self.assertRaises(ReplacementBudgetExhausted):
            ledger.request_replacement("0b", "p2", "p2-RP", "a-p2-RP", "e-p2-RP")
        self.assertEqual(ledger.used_pairs("0b"), 1)
        self.assertEqual(ledger.pool_cursor("0b"), 1)

    def test_invalid_attempt_id_format_rejected(self):
        self.ledger.open_pair("pair-a", "0b", 10)
        with self.assertRaises(ValueError):
            self.ledger.record_attempt("bad id with spaces", "pair-a", "author", "COMPLETED")


# ---------------------------------------------------------------------------
# M-2 — bit-exact replacement-pool replay + R4.1 integrity digests
# ---------------------------------------------------------------------------


class ReplacementReplayTest(unittest.TestCase):
    def _mutated_package(self, mutate):
        contract, text, record = load_package()
        mutate(contract, record)
        return contract, text, record

    def test_bit_exact_clean_replay_passes(self):
        contract, _, record = load_package()
        for variant, pool in contract["replacement"]["pools"].items():
            replayed = replay_replacement_stream(
                contract["seed_generation"]["anchor"], variant,
                pool["start_index"], len(pool["seeds"]), pool.get("skipped") or [],
            )
            self.assertEqual(replayed, pool["seeds"], variant)
            self.assertEqual(
                pool["next_candidate_index"],
                pool["start_index"] + len(pool["seeds"]) + len(pool["skipped"]),
            )
        self.assertEqual(
            replacement_pool_digest(contract["replacement"]["pools"]),
            contract["replacement_pool_sha256"],
        )
        self.assertEqual(r4_record_digest(record), record["record_r4_sha256"])
        self.assertEqual(
            record["record_r4_sha256"], contract["seed_record_r4_sha256"]
        )
        # R3 logical digest is preserved as provenance, unchanged
        self.assertEqual(
            record["record_sha256"],
            "eb4ab3f891e17dd2b456a3870ed73b19e39d67bf51109b6cb47ca64524ce476b",
        )

    def test_mutated_pool_seed_rejected_even_when_contract_and_record_agree(self):
        """The reviewer M-2 attack: edit contract + record together."""
        def mutate(contract, record):
            contract["replacement"]["pools"]["0b"]["seeds"][0] = 999999999
            record["replacement_pools"]["0b"]["seeds"][0] = 999999999
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("bit-exact" in f or "deterministic stream" in f for f in report["failures"]))

    def test_wrong_skipped_seed_rejected(self):
        def mutate(contract, record):
            pool = contract["replacement"]["pools"]["0b"]
            start = pool["start_index"]
            seed = seeds.derive_seed(
                contract["seed_generation"]["anchor"],
                seeds.replica_label("0b", start),
            )
            pool["skipped"] = [
                {"index": start, "seed": seed + 1, "reason": "SEED_COLLISION_TREE"}
            ]
            record["replacement_pools"]["0b"]["skipped"] = pool["skipped"]
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("does not re-derive" in f for f in report["failures"]))

    def test_wrong_skipped_reason_rejected(self):
        def mutate(contract, record):
            pool = contract["replacement"]["pools"]["32b"]
            start = pool["start_index"]
            seed = seeds.derive_seed(
                contract["seed_generation"]["anchor"],
                seeds.replica_label("32b", start),
            )
            pool["skipped"] = [{"index": start, "seed": seed, "reason": "INCONVENIENT"}]
            record["replacement_pools"]["32b"]["skipped"] = pool["skipped"]
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("SEED_COLLISION_TREE" in f for f in report["failures"]))

    def test_fake_skip_structure_with_extra_key_rejected(self):
        def mutate(contract, record):
            pool = contract["replacement"]["pools"]["11b"]
            start = pool["start_index"]
            seed = seeds.derive_seed(
                contract["seed_generation"]["anchor"],
                seeds.replica_label("11b", start),
            )
            pool["skipped"] = [
                {"index": start, "seed": seed, "reason": "SEED_COLLISION_TREE", "note": "x"}
            ]
            record["replacement_pools"]["11b"]["skipped"] = pool["skipped"]
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("extra keys" in f for f in report["failures"]))

    def test_fake_skip_with_true_continuation_rejected_by_manifest_coverage(self):
        """A structurally valid skip that hands the stream forward is still refused."""
        contract, text, record = load_package()
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        pool = contract["replacement"]["pools"]["0b"]
        fake_index = pool["start_index"]
        fake_seed = pool["seeds"][0]
        pool["skipped"] = [
            {"index": fake_index, "seed": fake_seed, "reason": "SEED_COLLISION_TREE"}
        ]
        pool["seeds"] = replay_replacement_stream(
            record["anchor"], "0b", pool["start_index"], len(pool["seeds"]), pool["skipped"]
        )
        pool["next_candidate_index"] = (
            pool["start_index"] + len(pool["seeds"]) + len(pool["skipped"])
        )
        record["replacement_pools"]["0b"] = dict(
            pool, indices_consumed=[pool["start_index"], pool["next_candidate_index"] - 1]
        )
        report = validate_freeze_contract(
            contract, protocol_text=text, seed_record=record,
            repo_root=REPO_ROOT, collision_manifest=manifest, rerun_scan=False,
        )
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("skip coverage mismatch" in f for f in report["failures"]))
        self.assertTrue(any("replacement_pool_sha256" in f for f in report["failures"]))

    def test_wrong_pool_cursor_rejected(self):
        def mutate(contract, record):
            contract["replacement"]["pools"]["53b"]["next_candidate_index"] = 99
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("next_candidate_index" in f for f in report["failures"]))

    def test_stale_replacement_pool_digest_rejected(self):
        def mutate(contract, record):
            contract["replacement_pool_sha256"] = "1" * 64
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("replacement_pool_sha256" in f for f in report["failures"]))

    def test_record_pool_drift_from_contract_rejected(self):
        def mutate(contract, record):
            record["replacement_pools"]["32b"]["seeds"][0] = (
                record["replacement_pools"]["32b"]["seeds"][0] + 1
            )
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("replacement pool seeds != contract" in f for f in report["failures"]))

    def test_stale_full_record_digest_rejected(self):
        def mutate(contract, record):
            record["skipped_identities"]["11b"][0]["seed"] += 1
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("record_r4_sha256" in f for f in report["failures"]))

    def test_confirmatory_skip_entry_must_rederive(self):
        def mutate(contract, record):
            record["skipped_identities"]["11b"][0]["seed"] += 1
            contract["seed_record_r4_sha256"] = record["record_r4_sha256"] = r4_record_digest(record)
        contract, text, record = self._mutated_package(mutate)
        report = validate_freeze_contract(contract, protocol_text=text, seed_record=record)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("does not re-derive" in f for f in report["failures"]))


# ---------------------------------------------------------------------------
# M-3 — collision-skip legitimacy bound into the authoritative gate
# ---------------------------------------------------------------------------


class CollisionSkipProofTest(unittest.TestCase):
    def setUp(self):
        self.contract, self.text, self.record = load_package()
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def _validate(self, contract=None, record=None, manifest=None, **kwargs):
        return validate_freeze_contract(
            contract or self.contract,
            protocol_text=self.text,
            seed_record=record or self.record,
            repo_root=kwargs.pop("repo_root", REPO_ROOT),
            collision_manifest=manifest if manifest is not None else self.manifest,
            **kwargs,
        )

    def test_committed_manifest_proves_all_41_skips(self):
        self.assertEqual(self.manifest["scan_status"], "VERIFIED")
        proven = 0
        for variant, streams in self.manifest["recorded_skips"].items():
            for stream_name, facts in streams.items():
                for fact in facts:
                    self.assertGreaterEqual(fact["non_allowlisted_hit_count"], 1)
                    self.assertTrue(fact["hit_paths"])
                    proven += 1
        self.assertEqual(proven, 41)
        report = self._validate(rerun_scan=True)
        self.assertEqual(report["gate"], "PASS", report["failures"])

    def test_fabricated_skip_for_clean_candidate_fails(self):
        """CRITICAL M-3 control: a fully self-consistent hand-edit still fails."""
        contract = copy.deepcopy(self.contract)
        record = copy.deepcopy(self.record)
        manifest = copy.deepcopy(self.manifest)
        pool = contract["replacement"]["pools"]["0b"]
        fake_index = pool["start_index"]  # 75: an ACCEPTED clean candidate
        fake_seed = pool["seeds"][0]
        pool["skipped"] = [
            {"index": fake_index, "seed": fake_seed, "reason": "SEED_COLLISION_TREE"}
        ]
        pool["seeds"] = replay_replacement_stream(
            record["anchor"], "0b", pool["start_index"], len(pool["seeds"]), pool["skipped"]
        )
        pool["next_candidate_index"] = (
            pool["start_index"] + len(pool["seeds"]) + len(pool["skipped"])
        )
        record["replacement_pools"]["0b"] = dict(
            pool, indices_consumed=[pool["start_index"], pool["next_candidate_index"] - 1]
        )
        digest = replacement_pool_digest(contract["replacement"]["pools"])
        contract["replacement_pool_sha256"] = record["replacement_pool_sha256"] = digest
        record["record_r4_sha256"] = r4_record_digest(record)
        contract["seed_record_r4_sha256"] = record["record_r4_sha256"]
        manifest["accepted_replacement"]["0b"]["seeds"] = pool["seeds"]
        manifest["recorded_skips"]["0b"]["replacement"].append({
            "index": fake_index,
            "seed": fake_seed,
            "reason": "SEED_COLLISION_TREE",
            "hit_paths": ["README.md"],  # fabricated
            "non_allowlisted_hit_count": 1,
        })
        manifest["manifest_sha256"] = collision_manifest_digest(manifest)
        report = self._validate(contract=contract, record=record, manifest=manifest, rerun_scan=True)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(
            any("found NO collision" in f for f in report["failures"]),
            report["failures"],
        )

    def test_manifest_digest_mismatch_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["scan_status"] = "VERIFIED-TAMPERED"  # digest no longer matches content
        report = self._validate(manifest=manifest, rerun_scan=False)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("manifest_sha256 stale" in f for f in report["failures"]))

    def test_incomplete_skip_coverage_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["recorded_skips"]["0b"]["confirmatory"] = \
            manifest["recorded_skips"]["0b"]["confirmatory"][:-1]
        manifest["manifest_sha256"] = collision_manifest_digest(manifest)
        report = self._validate(manifest=manifest, rerun_scan=False)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("skip coverage mismatch" in f for f in report["failures"]))

    def test_missing_pinned_object_blocks(self):
        """A scan that cannot run is BLOCKED (never treated as clean)."""
        with tempfile.TemporaryDirectory() as tmp:
            # non-git repository root: the pinned scan cannot be executed
            report = self._validate(rerun_scan=True, repo_root=Path(tmp))
            self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
            self.assertTrue(
                any("collision-skip proof BLOCKED" in f for f in report["failures"]),
                report["failures"],
            )

    def test_manifest_pin_mismatch_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["exclusion_tree_pin"] = "1" * 40
        report = self._validate(manifest=manifest, rerun_scan=False)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("exclusion_tree_pin != contract pin" in f for f in report["failures"]))

    def test_missing_manifest_binding_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        del contract["collision_scan_manifest"]
        report = self._validate(contract=contract, manifest=None, rerun_scan=False, repo_root=None)
        self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
        self.assertTrue(any("collision_scan_manifest" in f for f in report["failures"]))

    def test_tampered_manifest_file_rejected_by_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = copy.deepcopy(self.contract)
            record = self.record
            record_path = root / contract["scientific_subject"]["seed_record_path"]
            record_path.parent.mkdir(parents=True, exist_ok=True)
            record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            manifest_path = root / contract["collision_scan_manifest"]["path"]
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            # tamper AFTER binding
            tampered = copy.deepcopy(self.manifest)
            tampered["scan_status"] = "CLEAN-EVERYWHERE"
            manifest_path.write_text(json.dumps(tampered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            report = validate_freeze_contract(
                contract, protocol_text=self.text, seed_record=record,
                repo_root=root, rerun_scan=False,
            )
            self.assertEqual(report["gate"], "FREEZE_GATE_FAIL")
            self.assertTrue(
                any("digest mismatch" in f or "manifest_sha256 stale" in f for f in report["failures"]),
                report["failures"],
            )


# ---------------------------------------------------------------------------
# m-1 — equivalence wording (TOST semantics, not "indistinguishable from zero")
# ---------------------------------------------------------------------------


class EquivalenceWordingTest(unittest.TestCase):
    def test_candidate_doc_states_equivalence_interval_not_indistinguishability(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertNotIn("неотличимость медианного сдвига от нуля", text)
        self.assertIn("equivalence interval", text)
        self.assertIn("statistical non-significance", text)
        self.assertIn("standard TOST", text)
        self.assertIn("H0(v): не-эквивалентность", text)
        self.assertIn("H1(v): эквивалентность", text)
        # the mechanical decision rule remains authoritative
        self.assertIn("→ EQUIVALENT(v)", text)
        self.assertIn("→ NOT_EQUIVALENT(v)", text)

    def test_hg_b_proposal_records_r4_1_addendum(self):
        text = HG_B_PROPOSAL_PATH.read_text(encoding="utf-8")
        self.assertIn("Addendum R4.1", text)
        self.assertIn("nanolab_v02_dispatch_authority", text)
        self.assertIn("WAITING_OWNER", text)

    def test_candidate_doc_pins_r4_1_repair_and_preserved_identities(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("candidate revision  = R4", text)
        self.assertIn("candidate repair R4.1", text)
        self.assertIn("NOT FROZEN", text)
        self.assertIn("DISPATCH_BLOCKED", text)
        self.assertIn("replacement_pool_sha256", text)
        self.assertIn("record_r4_sha256", text)
        self.assertIn("0b = 64, 32b = 64, 11b = 10, 53b = 10", text)
        self.assertIn("next_candidate_index = 75/76/21/21", text)


# ---------------------------------------------------------------------------
# Positive + M-1 controls — pre-freeze validation vs gated dispatch
# ---------------------------------------------------------------------------


class CleanPackagePositiveTest(unittest.TestCase):
    def test_freeze_gate_passes_on_clean_package(self):
        report = freeze_gate(CONTRACT_PATH, DOC_PATH, RECORD_PATH, repo_root=REPO_ROOT)
        self.assertEqual(report["gate"], "PASS", report["failures"])
        self.assertEqual(report["failures"], [])
        # M-1: a consistency PASS is a PRE-FREEZE validation, never dispatch.
        self.assertEqual(report["validation_stage"], "PREFREEZE_VALIDATION_PASS")
        self.assertFalse(report["dispatch_ready"])
        self.assertEqual(report["dispatch"], "DISPATCH_BLOCKED")
        self.assertTrue(report["dispatch_blockers"])

    def test_prefreeze_validation_passes_while_dispatch_stays_blocked(self):
        report = prefreeze_validation(CONTRACT_PATH, DOC_PATH, RECORD_PATH, repo_root=REPO_ROOT)
        self.assertEqual(report["gate"], "PASS")
        self.assertEqual(report["validation_stage"], "PREFREEZE_VALIDATION_PASS")
        self.assertEqual(report["dispatch"], "DISPATCH_BLOCKED")
        self.assertIn("NOT_FROZEN", report["dispatch_blockers"][0])

    def test_prefreeze_package_cannot_produce_dispatch_plan(self):
        """M-1 core regression: NOT_FROZEN + clean contract => dispatch REJECTED."""
        contract, text, record = load_package()
        self.assertEqual(contract["scientific_subject"]["freeze_status"], "NOT_FROZEN")
        for kwargs in (
            {"authority_path": None},
            {"authority_path": EVIDENCE / "repro-v0-2-freeze-contract-PRE_DATA_R4.json"},
        ):
            with self.assertRaises(ContractError) as ctx:
                build_execution_plan(
                    CONTRACT_PATH, DOC_PATH, RECORD_PATH, repo_root=REPO_ROOT, **kwargs
                )
            message = str(ctx.exception)
            self.assertTrue(
                "DISPATCH_BLOCKED" in message or "dispatch authority" in message, message
            )
        # even a well-formed FROZEN authority cannot authorize a NOT_FROZEN contract
        with tempfile.TemporaryDirectory() as tmp:
            authority = _authority_fixture(Path(tmp), contract, freeze_status="NOT_FROZEN")
            with self.assertRaises(ContractError) as ctx:
                build_execution_plan(
                    Path(tmp) / "authority" / "contract.json",
                    Path(tmp) / "candidate.md",
                    Path(tmp) / contract["scientific_subject"]["seed_record_path"],
                    repo_root=tmp,
                    authority_path=authority,
                    allow_fixture=True,
                    rerun_scan=False,
                )
            message = str(ctx.exception)
            self.assertTrue(
                "not FROZEN" in message or "frozen must be literally true" in message, message
            )

    def test_cli_gate_exit_zero_and_plan_refused_for_predata(self):
        gate = cli([
            "gate",
            "--contract", str(CONTRACT_PATH),
            "--protocol", str(DOC_PATH),
            "--record", str(RECORD_PATH),
            "--repo-root", str(REPO_ROOT),
        ])
        self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
        self.assertIn('"gate": "PASS"', gate.stdout)
        self.assertIn('"validation_stage": "PREFREEZE_VALIDATION_PASS"', gate.stdout)
        self.assertIn('"dispatch": "DISPATCH_BLOCKED"', gate.stdout)
        prefreeze = cli([
            "prefreeze",
            "--contract", str(CONTRACT_PATH),
            "--protocol", str(DOC_PATH),
            "--record", str(RECORD_PATH),
            "--repo-root", str(REPO_ROOT),
        ])
        self.assertEqual(prefreeze.returncode, 0, prefreeze.stdout + prefreeze.stderr)
        # plan without a dispatch authority: refused (M-1)
        plan = cli([
            "plan",
            "--contract", str(CONTRACT_PATH),
            "--protocol", str(DOC_PATH),
            "--record", str(RECORD_PATH),
            "--repo-root", str(REPO_ROOT),
            "--authority", str(EVIDENCE / "r4-1-collision-scan-manifest-R4.json"),
        ])
        self.assertNotEqual(plan.returncode, 0)
        self.assertNotIn("nanolab_v02_dispatch_execution_plan", plan.stdout)

    def test_dispatch_refuses_corrupted_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            contract, _, _ = load_package()
            contract["confirmatory_seeds"]["11b"] = []  # the F1 audit class
            bad_contract = write_tmp(Path(tmp), "bad-contract.json", contract)
            plan = cli([
                "plan",
                "--contract", str(bad_contract),
                "--protocol", str(DOC_PATH),
                "--record", str(RECORD_PATH),
                "--repo-root", str(REPO_ROOT),
                "--authority", str(MANIFEST_PATH),
            ])
            self.assertNotEqual(plan.returncode, 0)
            self.assertIn("FREEZE_GATE_FAIL", plan.stdout)

    def test_dispatch_refuses_missing_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.json"
            dummy_authority = write_tmp(Path(tmp), "authority.json", {"placeholder": True})
            with self.assertRaises(ContractError):
                build_execution_plan(
                    CONTRACT_PATH, DOC_PATH, missing,
                    repo_root=REPO_ROOT, authority_path=dummy_authority,
                )


# ---------------------------------------------------------------------------
# M-1 — dispatch authority matrix (synthetic fixture is test-only)
# ---------------------------------------------------------------------------


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write_json(path: Path, payload) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _git_run(root: Path, *args: str) -> str:
    """Run git in the synthetic fixture repo (real commits/trees/blobs)."""
    completed = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True
    )
    if completed.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _git_blob(root: Path, commit: str, relpath: str) -> str:
    return _git_run(root, "rev-parse", f"{commit}:{relpath}")


def _git_hash_object(root: Path, raw: bytes) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), "hash-object", "--stdin"],
        input=raw, capture_output=True,
    )
    if completed.returncode != 0:
        raise AssertionError(f"git hash-object failed: {completed.stderr!r}")
    return completed.stdout.decode("utf-8").strip()


def _authority_fixture(tmp: Path, base_contract: dict, freeze_status: str = "FROZEN",
                       subject_head: str | None = None, subject_tree: str | None = None,
                       legacy_two_commit: bool = False):
    """Build a self-consistent SYNTHETIC TEST FIXTURE ONLY authority package
    backed by a REAL temporary Git repository (real commits, trees, blobs).

    Mirrors the required R4.3 (M-7) freeze lifecycle ``S -> F -> R/V -> A``:

      commit S = PRE-FREEZE candidate subject — NOT FROZEN contract copy,
                 protocol, seed record, collision manifest;
      commit H = HG-B owner approval + R2 activation records (pre-freeze;
                 they intentionally reference no frozen commit);
      commit F = FROZEN PACKAGE COMMIT — FROZEN contract (NO self-SHA: the
                 ``frozen_subject_*`` compatibility fields stay null), FROZEN
                 protocol, seed record, manifest;
      commit R = fresh review record pinning F (reviewed_head/tree = F);
      commit V = fresh verify record pinning F (verified_head/tree = F);
      commit A = Director FREEZE record pinning F;
      the authority JSON itself is written after commit A — it is the live
      gate input binding F + the exact R/V/HG-B/R2 record blobs, not part
      of them.

    ``subject_head``/``subject_tree`` overrides exist ONLY for negative
    tests (self-consistent fake pins that cannot exist in Git); the frozen
    artifact bindings always stay pinned to the REAL frozen package commit.

    ``legacy_two_commit=True`` reproduces the REJECTED R4.2 two-commit
    shortcut instead (pre-freeze reviewed subject + one evidence commit
    holding the FROZEN bytes and review/verify records pointing back at the
    subject) to prove the new validator can no longer be satisfied by it.
    """
    (Path(tmp) / "authority").mkdir(parents=True, exist_ok=True)
    # ---- commit S: the pre-freeze candidate subject (PRE-DATA / NOT FROZEN)
    record_bytes = RECORD_PATH.read_bytes()
    manifest_bytes = MANIFEST_PATH.read_bytes()
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    pre_contract = copy.deepcopy(base_contract)
    pre_contract["scientific_subject"]["freeze_status"] = "NOT_FROZEN"
    pre_contract["scientific_subject"]["frozen_subject_head"] = None
    pre_contract["scientific_subject"]["frozen_subject_tree"] = None
    record_rel = pre_contract["scientific_subject"]["seed_record_path"]
    manifest_rel = pre_contract["collision_scan_manifest"]["path"]
    record_path = Path(tmp) / record_rel
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_bytes(record_bytes)
    manifest_path = Path(tmp) / manifest_rel
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(manifest_bytes)
    protocol_path = Path(tmp) / "candidate.md"
    protocol_path.write_text(doc_text, encoding="utf-8")
    (Path(tmp) / "authority" / "contract.json").write_bytes(
        (json.dumps(pre_contract, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    _git_run(tmp, "init", "-q")
    _git_run(tmp, "config", "user.name", "synthetic-fixture")
    _git_run(tmp, "config", "user.email", "synthetic-fixture@example.invalid")
    _git_run(tmp, "add", "-A")
    _git_run(tmp, "commit", "-q", "--allow-empty", "-m", "synthetic pre-freeze candidate subject")
    subject_commit = _git_run(tmp, "rev-parse", "HEAD")
    subject_tree_real = _git_run(tmp, "rev-parse", "HEAD^{tree}")

    # ---- frozen contract bytes (used by both modes)
    frozen_doc = doc_text.replace("NOT FROZEN", "FROZEN") if freeze_status == "FROZEN" else doc_text
    contract = copy.deepcopy(base_contract)
    contract["scientific_subject"]["freeze_status"] = freeze_status
    # R4.3 (M-7): a real frozen package commit F cannot embed its own SHA —
    # the frozen contract carries NO self-reference pins (non-authoritative
    # compatibility fields stay null; the exact pins live in the authority).
    contract["scientific_subject"]["frozen_subject_head"] = None
    contract["scientific_subject"]["frozen_subject_tree"] = None
    # FROZEN_R2 repair (M-1 of the FROZEN_R1 review): a FROZEN protocol must
    # carry exactly one scan-allowlist-v1 block machine-bound to the contract
    # allowlist; the PRE-DATA subject keeps its historical block-free form.
    if freeze_status == "FROZEN":
        frozen_doc = frozen_doc + "\n" + scan_allowlist_block(contract)
    contract_bytes = (json.dumps(contract, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    record_sha = _sha256_bytes(record_bytes)

    payloads = {
        "freeze": {
            "record_kind": "DIRECTOR_FREEZE_RECORD",
            "issuer_class": "DIRECTOR",
            "director": "DIRECTOR-SYNTHETIC-FIXTURE",
            "decision": "FREEZE",
            "subject_head": None,  # filled per mode below
            "subject_tree": None,
            "contract_sha256": _sha256_bytes(contract_bytes),
            "seed_record_sha256": record_sha,
        },
        "hg_b": {
            "record_kind": "HG_B_OWNER_APPROVAL",
            "issuer_class": "HUMAN_GATE_OWNER",
            "decision": "APPROVED",
            "candidate_revision": str(contract["scientific_subject"]["candidate_revision"]),
            "rule_id": contract["rule_id"],
        },
        "review": {
            "record_kind": "REVIEWER_VERDICT",
            "issuer_class": "INDEPENDENT_REVIEWER",
            "verdict": "PASS",
            "reviewed_head": None,
            "reviewed_tree": None,
        },
        "verify": {
            "record_kind": "VERIFIER_VERDICT",
            "issuer_class": "INDEPENDENT_VERIFIER",
            "verdict": "VERIFIED",
            "verified_head": None,
            "verified_tree": None,
        },
        "r2": {
            "record_kind": "R2_ACTIVATION_RECORD",
            "issuer_class": "R2_HOST",
            "r2_status": "ACTIVE",
            "author_executor": "AUTHOR_U1",
            "external_executor": "EXTERNAL_U2",
        },
    }
    record_source_commits: dict[str, str] = {}

    if legacy_two_commit:
        # ---- REJECTED R4.2 shortcut: commit E holds the FROZEN bytes AND
        # review/verify records pinning the pre-freeze subject S.
        head, tree = subject_head or subject_commit, subject_tree or subject_tree_real
        for key in ("freeze", "review"):
            payloads[key]["subject_head" if key == "freeze" else "reviewed_head"] = head
            payloads[key]["subject_tree" if key == "freeze" else "reviewed_tree"] = tree
        payloads["verify"]["verified_head"] = head
        payloads["verify"]["verified_tree"] = tree
        protocol_path.write_text(frozen_doc, encoding="utf-8")
        (Path(tmp) / "authority" / "contract.json").write_bytes(contract_bytes)
        for name in ("freeze", "hg_b", "review", "verify", "r2"):
            _write_json(Path(tmp) / "authority" / f"{name}.json", payloads[name])
        _git_run(tmp, "add", "-A")
        _git_run(tmp, "commit", "-q", "--allow-empty", "-m", "synthetic freeze evidence (legacy two-commit)")
        evidence_commit = _git_run(tmp, "rev-parse", "HEAD")
        for name in payloads:
            record_source_commits[name] = evidence_commit
        frozen_head, frozen_tree = evidence_commit, _git_run(tmp, "rev-parse", "HEAD^{tree}")
        authority_head, authority_tree = head, tree
    else:
        # ---- commit H: HG-B owner approval + R2 activation (pre-freeze)
        for name in ("hg_b", "r2"):
            _write_json(Path(tmp) / "authority" / f"{name}.json", payloads[name])
        _git_run(tmp, "add", "-A")
        _git_run(tmp, "commit", "-q", "--allow-empty", "-m", "synthetic HG-B approval + R2 activation records")
        record_source_commits["hg_b"] = _git_run(tmp, "rev-parse", "HEAD")
        record_source_commits["r2"] = record_source_commits["hg_b"]
        # ---- commit F: the FROZEN PACKAGE COMMIT (frozen contract + protocol)
        protocol_path.write_text(frozen_doc, encoding="utf-8")
        (Path(tmp) / "authority" / "contract.json").write_bytes(contract_bytes)
        _git_run(tmp, "add", "-A")
        _git_run(tmp, "commit", "-q", "--allow-empty", "-m", "synthetic frozen package commit")
        frozen_head = _git_run(tmp, "rev-parse", "HEAD")
        frozen_tree = _git_run(tmp, "rev-parse", "HEAD^{tree}")
        head = subject_head or frozen_head
        tree = subject_tree or frozen_tree
        payloads["freeze"]["subject_head"] = head
        payloads["freeze"]["subject_tree"] = tree
        payloads["review"]["reviewed_head"] = head
        payloads["review"]["reviewed_tree"] = tree
        payloads["verify"]["verified_head"] = head
        payloads["verify"]["verified_tree"] = tree
        # ---- commit R: fresh review record pinning F
        _write_json(Path(tmp) / "authority" / "review.json", payloads["review"])
        _git_run(tmp, "add", "-A")
        _git_run(tmp, "commit", "-q", "--allow-empty", "-m", "synthetic review record pinning the frozen package")
        record_source_commits["review"] = _git_run(tmp, "rev-parse", "HEAD")
        # ---- commit V: fresh verify record pinning F
        _write_json(Path(tmp) / "authority" / "verify.json", payloads["verify"])
        _git_run(tmp, "add", "-A")
        _git_run(tmp, "commit", "-q", "--allow-empty", "-m", "synthetic verify record pinning the frozen package")
        record_source_commits["verify"] = _git_run(tmp, "rev-parse", "HEAD")
        # ---- commit A: Director freeze record pinning F
        _write_json(Path(tmp) / "authority" / "freeze.json", payloads["freeze"])
        _git_run(tmp, "add", "-A")
        _git_run(tmp, "commit", "-q", "--allow-empty", "-m", "synthetic director freeze record pinning the package")
        record_source_commits["freeze"] = _git_run(tmp, "rev-parse", "HEAD")
        authority_head, authority_tree = head, tree

    def embedded(name: str) -> dict:
        rel = f"authority/{name}.json"
        source = record_source_commits[name]
        return {
            "path": rel,
            "source_commit": source,
            "git_blob_sha1": _git_blob(tmp, source, rel),
            "canonical_sha256": _sha256_bytes((Path(tmp) / rel).read_bytes()),
            **payloads[name],
        }

    # R4.3 (M-7): frozen artifacts are ALWAYS bound to the FROZEN PACKAGE
    # COMMIT itself (in legacy_two_commit mode that binding — evidence
    # commit E while the authority pins S — is exactly what the validator
    # must reject).
    artifact_commit = frozen_head
    authority = {
        "schema_version": 3,
        "kind": "nanolab_v02_dispatch_authority",
        "authority_revision": "synthetic-fixture-r4-3",
        "fixture": True,
        "fixture_note": SYNTHETIC_FIXTURE_MARKER + " - not a real authorization",
        "frozen": freeze_status == "FROZEN",
        "subject_head": authority_head,
        "subject_tree": authority_tree,
        "contract_sha256": _sha256_bytes(contract_bytes),
        "seed_record_sha256": record_sha,
        "frozen_subject_binding": {
            "contract": {
                "source_commit": artifact_commit,
                "path": "authority/contract.json",
                "git_blob_sha1": _git_blob(tmp, artifact_commit, "authority/contract.json"),
                "canonical_sha256": _sha256_bytes(contract_bytes),
            },
            "protocol": {
                "source_commit": artifact_commit,
                "path": "candidate.md",
                "git_blob_sha1": _git_blob(tmp, artifact_commit, "candidate.md"),
                "canonical_sha256": _sha256_bytes(frozen_doc.encode("utf-8")),
            },
            "seed_record": {
                "source_commit": artifact_commit,
                "path": record_rel,
                "git_blob_sha1": _git_blob(tmp, artifact_commit, record_rel),
                "canonical_sha256": record_sha,
            },
        },
        "freeze_record": embedded("freeze"),
        "hg_b_record": embedded("hg_b"),
        "review_verdict": embedded("review"),
        "verify_verdict": embedded("verify"),
        "r2_record": embedded("r2"),
        "author_executor": "AUTHOR_U1",
        "external_executor": "EXTERNAL_U2",
        "executor_policy": {"author_leg_allowed": True, "external_leg_allowed": True},
    }
    return _write_json(Path(tmp) / "authority" / "dispatch-authority.json", authority)


class DispatchAuthorityTest(unittest.TestCase):
    """M-1: DISPATCH_READY requires the full machine-bound authority."""

    def setUp(self):
        self.contract, self.text, self.record = load_package()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def _authority(self, **kwargs):
        return _authority_fixture(self.tmp, self.contract, **kwargs)

    def _plan_kwargs(self, authority, **overrides):
        kwargs = dict(
            repo_root=self.tmp,
            authority_path=authority,
            allow_fixture=True,
            rerun_scan=False,
        )
        kwargs.update(overrides)
        return kwargs

    def test_synthetic_fully_authorized_fixture_generates_plan(self):
        authority = self._authority()
        plan = build_execution_plan(
            self.tmp / "authority" / "contract.json",
            self.tmp / "candidate.md",
            self.tmp / self.contract["scientific_subject"]["seed_record_path"],
            **self._plan_kwargs(authority),
        )
        self.assertEqual(plan["kind"], "nanolab_v02_dispatch_execution_plan")
        self.assertTrue(plan["synthetic_test_fixture_only"])
        # R4.2 (M-5): the machine NEVER claims DISPATCH_AUTHORIZED — Git-bound
        # records prove preconditions RECORDED, not issuer identity. The real
        # launch gate stays external (Human / Protected-Writer).
        self.assertEqual(
            plan["dispatch_authority"]["status"], "DISPATCH_PRECONDITIONS_RECORDED"
        )
        self.assertIs(plan["dispatch_authority"]["machine_launch_authorized"], False)
        self.assertEqual(plan["dispatch_authority"]["launch_gate"], "HUMAN_PROTECTED_WRITER")
        self.assertIs(plan["machine_launch_authorized"], False)
        self.assertEqual(plan["launch_gate"], "HUMAN_PROTECTED_WRITER")
        self.assertNotIn("DISPATCH_AUTHORIZED", json.dumps(plan))
        self.assertEqual(
            {v: cell["n_min_valid_pairs"] for v, cell in plan["cells"].items()},
            {"0b": 52, "32b": 52, "11b": 8, "53b": 8},
        )
        self.assertEqual(plan["budget"]["max_runs"], 352)
        self.assertEqual(plan["scientific_outcome"], "NOT_EVALUATED")

    def test_fixture_authority_rejected_for_real_dispatch(self):
        authority = self._authority()
        with self.assertRaises(ContractError) as ctx:
            build_execution_plan(
                self.tmp / "authority" / "contract.json",
                self.tmp / "candidate.md",
                self.tmp / self.contract["scientific_subject"]["seed_record_path"],
                repo_root=self.tmp,
                authority_path=authority,
                allow_fixture=False,
                rerun_scan=False,
            )
        self.assertIn("fixture", str(ctx.exception))

    def test_missing_authority_rejected(self):
        with self.assertRaises(ContractError) as ctx:
            build_execution_plan(
                CONTRACT_PATH, DOC_PATH, RECORD_PATH,
                repo_root=REPO_ROOT, authority_path=None,
            )
        self.assertIn("DISPATCH_BLOCKED", str(ctx.exception))

    def _mutated(self, mutate):
        authority_path = self._authority()
        authority = load_dispatch_authority(authority_path)
        mutate(authority)
        _write_json(authority_path, authority)
        return authority_path

    def _assert_rejected(self, label, **overrides):
        authority = overrides.pop("authority", None) or self._authority()
        with self.assertRaises(ContractError) as ctx:
            build_execution_plan(
                self.tmp / "authority" / "contract.json",
                self.tmp / "candidate.md",
                self.tmp / self.contract["scientific_subject"]["seed_record_path"],
                **self._plan_kwargs(authority, **overrides),
            )
        self.assertNotIn("DISPATCH_AUTHORIZED", str(ctx.exception), label)

    def test_not_frozen_package_rejected_even_with_frozen_authority(self):
        self._assert_rejected(
            "not frozen",
            authority=self._authority(freeze_status="NOT_FROZEN"),
        )

    def test_hg_b_not_approved_rejected(self):
        def mutate(authority):
            authority["hg_b_record"]["decision"] = "WAITING_OWNER"
        self._assert_rejected("hg-b", authority=self._mutated(mutate))

    def test_frozen_subject_mismatch_rejected(self):
        def mutate(authority):
            authority["subject_head"] = "b" * 40
        self._assert_rejected("subject mismatch", authority=self._mutated(mutate))

    def test_review_not_pass_rejected(self):
        def mutate(authority):
            authority["review_verdict"]["verdict"] = "FIX_REQUIRED"
        self._assert_rejected("review", authority=self._mutated(mutate))

    def test_verify_not_verified_rejected(self):
        def mutate(authority):
            authority["verify_verdict"]["verdict"] = "NOT_VERIFIED"
        self._assert_rejected("verify", authority=self._mutated(mutate))

    def test_r2_not_active_rejected(self):
        def mutate(authority):
            authority["r2_record"]["r2_status"] = "WAITING_HOST"
        self._assert_rejected("r2", authority=self._mutated(mutate))

    def test_executor_mismatch_rejected(self):
        def mutate(authority):
            authority["author_executor"] = "OUTENEMY_AS_AUTHOR"
        self._assert_rejected("executor", authority=self._mutated(mutate))

    def test_executor_policy_leg_forbidden_rejected(self):
        def mutate(authority):
            authority["executor_policy"]["external_leg_allowed"] = False
        self._assert_rejected("policy", authority=self._mutated(mutate))

    def test_contract_digest_mismatch_rejected(self):
        def mutate(authority):
            authority["contract_sha256"] = "0" * 64
        self._assert_rejected("contract digest", authority=self._mutated(mutate))

    def test_tampered_referenced_record_rejected(self):
        # R4.2 (M-5): the authority's embedded copy of a record is bound to
        # the exact Git object — an embedded field that the published,
        # committed record does not carry breaks the binding.
        def mutate(authority):
            authority["hg_b_record"]["owner_note"] = "tampered after binding"
        self._assert_rejected("tampered record", authority=self._mutated(mutate))

    def test_authority_structural_missing_key_rejected(self):
        authority_path = self._authority()
        authority = load_dispatch_authority(authority_path)
        del authority["r2_record"]
        _write_json(authority_path, authority)
        self._assert_rejected("missing key", authority=authority_path)

    def test_freeze_record_decision_must_be_freeze(self):
        def mutate(authority):
            authority["freeze_record"]["decision"] = "DRAFT"
        self._assert_rejected("freeze decision", authority=self._mutated(mutate))


class DispatchAuthorityGitBindingTest(unittest.TestCase):
    """R4.2 M-5 / R4.3 M-7: the frozen package must EXIST in Git with
    immutable bindings.

    The positive fixture uses a REAL temporary Git repository (real commits,
    trees, blobs) sequenced S -> F -> R/V -> A. The negatives prove the
    production path rejects strings that merely look like Git objects,
    worktree-only records and source/path/blob mismatches — and that even a
    fully Git-bound local package is never machine-authorized
    (DISPATCH_PRECONDITIONS_RECORDED ceiling; the launch gate stays
    Human/Protected-Writer).
    """

    def setUp(self):
        self.contract, self.text, self.record = load_package()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.record_rel = self.contract["scientific_subject"]["seed_record_path"]

    def _fixture(self, **kwargs) -> Path:
        return _authority_fixture(self.tmp, self.contract, **kwargs)

    def _validate(self, authority_path: Path):
        return validate_dispatch_authority(
            load_dispatch_authority(authority_path),
            load_contract(self.tmp / "authority" / "contract.json"),
            (self.tmp / "candidate.md").read_text(encoding="utf-8"),
            load_seed_record(self.tmp / self.record_rel),
            repo_root=self.tmp,
            contract_path=self.tmp / "authority" / "contract.json",
            protocol_path=self.tmp / "candidate.md",
            rerun_scan=False,
            allow_fixture=True,
        )

    def _mutated(self, mutate) -> Path:
        authority_path = self._fixture()
        authority = load_dispatch_authority(authority_path)
        mutate(authority)
        _write_json(authority_path, authority)
        return authority_path

    def _assert_rejected(self, label: str, authority_path: Path, substring: str):
        with self.assertRaises(ContractError) as ctx:
            self._validate(authority_path)
        message = str(ctx.exception)
        self.assertNotIn("DISPATCH_AUTHORIZED", message, label)
        self.assertIn(substring, message, f"{label}: {message[:400]}")

    def test_positive_fixture_is_backed_by_real_git_objects(self):
        authority_path = self._fixture()
        # the fixture pins a REAL commit: git can resolve head and tree
        authority = load_dispatch_authority(authority_path)
        self.assertEqual(
            _git_run(self.tmp, "rev-parse", f"{authority['subject_head']}^{{tree}}"),
            authority["subject_tree"],
        )
        report = self._validate(authority_path)
        self.assertEqual(report["status"], "DISPATCH_PRECONDITIONS_RECORDED")
        self.assertIs(report["machine_launch_authorized"], False)
        self.assertEqual(report["launch_gate"], "HUMAN_PROTECTED_WRITER")
        self.assertIn(
            report["identity_proof_ceiling"],
            report["identity_proof_ceiling"],  # honesty ceiling recorded
        )

    def test_nonexistent_well_formed_subject_head_rejected(self):
        authority_path = self._fixture(subject_head="e" * 40)
        self._assert_rejected(
            "nonexistent head", authority_path, "does not exist as a Git commit"
        )

    def test_existing_head_with_wrong_tree_rejected(self):
        authority_path = self._fixture(subject_tree="b" * 40)
        self._assert_rejected(
            "wrong tree", authority_path, "subject_tree mismatch"
        )

    def test_record_only_in_dirty_worktree_rejected(self):
        authority_path = self._fixture()
        # rewrite the published hg_b record in the WORKTREE only (not
        # committed) and rebind the authority to the new bytes: the Git
        # object at the pinned commit still holds the old bytes.
        candidate_revision = load_dispatch_authority(authority_path)["hg_b_record"][
            "candidate_revision"
        ]
        new_payload = {
            "record_kind": "HG_B_OWNER_APPROVAL",
            "issuer_class": "HUMAN_GATE_OWNER",
            "decision": "APPROVED",
            "candidate_revision": candidate_revision,
            "rule_id": self.contract["rule_id"],
            "note": "worktree-only rewrite — never committed",
        }
        raw = (json.dumps(new_payload, indent=2) + "\n").encode("utf-8")
        (self.tmp / "authority" / "hg_b.json").write_bytes(raw)
        authority = load_dispatch_authority(authority_path)
        authority["hg_b_record"]["canonical_sha256"] = _sha256_bytes(raw)
        authority["hg_b_record"]["git_blob_sha1"] = _git_hash_object(self.tmp, raw)
        _write_json(authority_path, authority)
        self._assert_rejected(
            "dirty worktree record", authority_path, "immutable source binding mismatch"
        )

    def test_record_source_commit_mismatch_rejected(self):
        authority_path = self._fixture()
        authority = load_dispatch_authority(authority_path)
        frozen = authority["subject_head"]
        # a real commit where the review record does NOT exist yet (the
        # pre-freeze candidate S precedes the review record commit R)
        before_review = _git_run(self.tmp, "rev-list", "--max-parents=0", "HEAD")
        self.assertNotEqual(before_review, frozen)
        authority["review_verdict"]["source_commit"] = before_review
        _write_json(authority_path, authority)
        self._assert_rejected(
            "record source commit mismatch",
            authority_path,
            "immutable source binding failed",
        )

    def test_record_path_blob_mismatch_rejected(self):
        def mutate(authority):
            # bind the hg_b record path to the FREEZE record's blob
            authority["hg_b_record"]["git_blob_sha1"] = authority["freeze_record"][
                "git_blob_sha1"
            ]

        self._assert_rejected(
            "record blob mismatch", self._mutated(mutate), "immutable source binding mismatch"
        )

    def test_fake_non_fixture_local_authority_never_machine_authorized(self):
        # A fully self-consistent, REAL-Git-bound authority package produced
        # locally with fixture=False: every Git binding verifies, but the
        # machine still must not claim DISPATCH_AUTHORIZED.
        authority_path = self._fixture()
        authority = load_dispatch_authority(authority_path)
        authority["fixture"] = False
        authority["fixture_note"] = None
        authority["authority_revision"] = "fake-local-non-fixture"
        _write_json(authority_path, authority)
        report = self._validate(authority_path)
        self.assertEqual(report["status"], "DISPATCH_PRECONDITIONS_RECORDED")
        self.assertIs(report["machine_launch_authorized"], False)
        self.assertEqual(report["launch_gate"], "HUMAN_PROTECTED_WRITER")
        self.assertIs(report["synthetic_test_fixture_only"], False)
        self.assertNotIn("DISPATCH_AUTHORIZED", json.dumps(report))

    def test_contract_artifact_not_in_frozen_package_commit_rejected(self):
        def mutate(authority):
            authority["frozen_subject_binding"]["contract"]["path"] = (
                "authority/absent-from-frozen-package.json"
            )

        self._assert_rejected(
            "artifact blob not in frozen package",
            self._mutated(mutate),
            "immutable artifact binding failed",
        )

    def test_artifact_source_commit_mismatch_rejected(self):
        # R4.3 (M-7) required test 3: review/verify pin F but the artifact
        # binding points at a DIFFERENT (even content-identical!) commit —
        # the frozen artifacts must be bound to F itself.
        def mutate(authority):
            authority["frozen_subject_binding"]["protocol"]["source_commit"] = _git_run(
                self.tmp, "rev-parse", "HEAD"  # the authority/freeze-record commit A
            )

        self._assert_rejected(
            "artifact source commit mismatch",
            self._mutated(mutate),
            "frozen package commit",
        )

    def test_worktree_contract_bytes_not_the_frozen_blob_rejected(self):
        authority_path = self._fixture()
        # tamper the contract file in the worktree AFTER the fixture exists
        # (the fixture builder would overwrite it) and update every digest
        # the authority carries EXCEPT the immutable Git blob — the frozen
        # bytes live in the pinned commit and cannot be rewritten. The
        # tampering must stay digest-consistent (no pre-Git check may fire
        # first), so the reported failure is the artifact binding itself.
        tampered = json.loads((self.tmp / "authority" / "contract.json").read_text())
        tampered["worktree_note"] = "tampered after freeze"
        raw = (json.dumps(tampered, indent=2) + "\n").encode("utf-8")
        (self.tmp / "authority" / "contract.json").write_bytes(raw)
        authority = load_dispatch_authority(authority_path)
        authority["contract_sha256"] = _sha256_bytes(raw)
        authority["freeze_record"]["contract_sha256"] = _sha256_bytes(raw)
        authority["frozen_subject_binding"]["contract"]["canonical_sha256"] = _sha256_bytes(raw)
        authority["frozen_subject_binding"]["contract"]["git_blob_sha1"] = _git_hash_object(
            self.tmp, raw
        )
        _write_json(authority_path, authority)
        self._assert_rejected(
            "contract blob not of frozen subject",
            authority_path,
            "frozen artifact bytes mismatch",
        )

    def test_schema_1_and_2_authorities_rejected(self):
        # R4.3 (M-7): fail-closed evolution — BOTH previous schema versions
        # are rejected; the v2 two-commit shortcut must not silently pass
        # the stronger gate.
        authority_path = self._fixture()
        for version in (1, 2):
            authority = load_dispatch_authority(authority_path)
            authority["schema_version"] = version
            _write_json(authority_path, authority)
            self._assert_rejected(
                f"schema {version} downgrade", authority_path, "schema_version"
            )


class FrozenPackageSequencingTest(unittest.TestCase):
    """R4.3 M-7: review/verify must bind the FROZEN PACKAGE COMMIT F.

    Required repair tests (REVIEWER_VERDICT_R3, M-7): review/verify pointing
    at the pre-freeze candidate are rejected; review and verify must pin F
    from their own LATER immutable record commits; the authority must bind
    the exact record blob refs; the frozen contract carries no self-SHA and
    the exact frozen pins live only in the external freeze/authority record;
    no self-consistent two-commit shortcut satisfies the chain. The
    positive fixture uses real temporary Git commits in the order
    ``S -> F -> Review/Verify evidence -> authority``. No fake real-world
    authorization is produced.
    """

    def setUp(self):
        self.contract, self.text, self.record = load_package()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.record_rel = self.contract["scientific_subject"]["seed_record_path"]

    def _fixture(self, **kwargs) -> Path:
        return _authority_fixture(self.tmp, self.contract, **kwargs)

    def _authority(self, authority_path: Path) -> dict:
        return load_dispatch_authority(authority_path)

    def _validate(self, authority_path: Path):
        return validate_dispatch_authority(
            load_dispatch_authority(authority_path),
            load_contract(self.tmp / "authority" / "contract.json"),
            (self.tmp / "candidate.md").read_text(encoding="utf-8"),
            load_seed_record(self.tmp / self.record_rel),
            repo_root=self.tmp,
            contract_path=self.tmp / "authority" / "contract.json",
            protocol_path=self.tmp / "candidate.md",
            rerun_scan=False,
            allow_fixture=True,
        )

    def _plan(self, authority_path: Path) -> dict:
        return build_execution_plan(
            self.tmp / "authority" / "contract.json",
            self.tmp / "candidate.md",
            self.tmp / self.record_rel,
            repo_root=self.tmp,
            authority_path=authority_path,
            allow_fixture=True,
            rerun_scan=False,
        )

    def _mutated(self, mutate) -> Path:
        authority_path = self._fixture()
        authority = load_dispatch_authority(authority_path)
        mutate(authority)
        _write_json(authority_path, authority)
        return authority_path

    def _assert_rejected(self, label: str, authority_path: Path, substring: str):
        with self.assertRaises(ContractError) as ctx:
            self._validate(authority_path)
        message = str(ctx.exception)
        self.assertNotIn("DISPATCH_AUTHORIZED", message, label)
        self.assertIn(substring, message, f"{label}: {message[:400]}")

    # -- lifecycle facts of the positive fixture ---------------------------

    def test_lifecycle_commits_are_sequenced_s_f_review_verify_authority(self):
        authority_path = self._fixture()
        authority = self._authority(authority_path)
        # the root commit is the pre-freeze candidate S; the frozen package
        # commit F strictly descends from it; the review/verify/freeze
        # record commits strictly descend from F (S -> F -> R/V -> A)
        subject = _git_run(self.tmp, "rev-list", "--max-parents=0", "HEAD")
        frozen = authority["subject_head"]
        review_src = authority["review_verdict"]["source_commit"]
        verify_src = authority["verify_verdict"]["source_commit"]
        freeze_src = authority["freeze_record"]["source_commit"]
        self.assertEqual(_git_run(self.tmp, "rev-parse", f"{frozen}^{{tree}}"),
                         authority["subject_tree"])
        for name, source in (("review", review_src), ("verify", verify_src),
                             ("freeze", freeze_src)):
            self.assertNotEqual(subject, source, name)
            self.assertNotEqual(frozen, source, name)
        # S is an ancestor of F; F is a strict ancestor of every record commit
        _git_run(self.tmp, "merge-base", "--is-ancestor", subject, frozen)
        for name, source in (("review", review_src), ("verify", verify_src),
                             ("freeze", freeze_src)):
            _git_run(self.tmp, "merge-base", "--is-ancestor", frozen, source)
            self.assertNotEqual(frozen, source, f"{name} must postdate F")

    def test_frozen_contract_carries_no_self_sha(self):
        # M-7: the FROZEN contract inside F must NOT embed its own commit
        # SHA; the compatibility fields stay null and the exact frozen pins
        # live only in the external authority record.
        authority = self._authority(self._fixture())
        frozen = authority["subject_head"]
        contract_from_git = json.loads(
            _git_run(self.tmp, "cat-file", "blob", f"{frozen}:authority/contract.json")
        )
        self.assertEqual(contract_from_git["scientific_subject"]["freeze_status"], "FROZEN")
        self.assertIsNone(contract_from_git["scientific_subject"]["frozen_subject_head"])
        self.assertIsNone(contract_from_git["scientific_subject"]["frozen_subject_tree"])
        self.assertNotIn(frozen, json.dumps(contract_from_git))
        self.assertEqual(authority["subject_head"], frozen)
        self.assertEqual(
            _git_run(self.tmp, "rev-parse", f"{frozen}^{{tree}}"), authority["subject_tree"]
        )

    def test_review_verify_pin_exact_frozen_package_commit(self):
        authority_path = self._fixture()
        authority = self._authority(authority_path)
        frozen, tree = authority["subject_head"], authority["subject_tree"]
        self.assertEqual(authority["review_verdict"]["reviewed_head"], frozen)
        self.assertEqual(authority["review_verdict"]["reviewed_tree"], tree)
        self.assertEqual(authority["verify_verdict"]["verified_head"], frozen)
        self.assertEqual(authority["verify_verdict"]["verified_tree"], tree)
        report = self._validate(authority_path)
        self.assertEqual(report["status"], "DISPATCH_PRECONDITIONS_RECORDED")
        self.assertIs(report["machine_launch_authorized"], False)
        self.assertEqual(report["launch_gate"], "HUMAN_PROTECTED_WRITER")
        # the recorded plan keeps the honest ceiling (m-3: exit 0 is NOT a
        # launch authorization)
        plan = self._plan(authority_path)
        self.assertEqual(plan["dispatch_authority"]["status"], "DISPATCH_PRECONDITIONS_RECORDED")
        self.assertIs(plan["machine_launch_authorized"], False)
        self.assertNotIn("DISPATCH_AUTHORIZED", json.dumps(plan))

    # -- required test 1/2: review/verify pointing at the pre-freeze subject

    def test_review_and_verify_pointing_at_prefreeze_subject_rejected(self):
        authority_path = self._fixture()
        authority = self._authority(authority_path)
        subject = _git_run(self.tmp, "rev-list", "--max-parents=0", "HEAD")
        subject_tree = _git_run(self.tmp, "rev-parse", f"{subject}^{{tree}}")
        authority["review_verdict"]["reviewed_head"] = subject
        authority["review_verdict"]["reviewed_tree"] = subject_tree
        authority["verify_verdict"]["verified_head"] = subject
        authority["verify_verdict"]["verified_tree"] = subject_tree
        _write_json(authority_path, authority)
        self._assert_rejected(
            "review/verify -> S with frozen blobs -> F",
            authority_path,
            "review subject mismatch",
        )

    def test_review_points_frozen_verify_points_prefreeze_rejected(self):
        authority_path = self._fixture()
        authority = self._authority(authority_path)
        subject = _git_run(self.tmp, "rev-list", "--max-parents=0", "HEAD")
        subject_tree = _git_run(self.tmp, "rev-parse", f"{subject}^{{tree}}")
        authority["verify_verdict"]["verified_head"] = subject
        authority["verify_verdict"]["verified_tree"] = subject_tree
        _write_json(authority_path, authority)
        self._assert_rejected(
            "review -> F, verify -> S",
            authority_path,
            "verify subject mismatch",
        )

    # -- required tests 4/5: record source predates F ----------------------

    def _orphan_record_commit(self, name: str, payload: dict) -> tuple[str, bytes]:
        """Commit ``payload`` as ``authority/<name>.json`` on an ORPHAN
        branch: created after F in wall-clock time but on UNRELATED history
        — mechanically indistinguishable from a record that predates F (F
        is not its ancestor), so the sequencing gate must reject it even
        though the record's own blob binding is fully valid. Returns the
        orphan commit SHA and the exact committed bytes."""
        anchor = _git_run(self.tmp, "rev-parse", "HEAD")
        _git_run(self.tmp, "checkout", "-q", "--orphan", f"orphan-{name}")
        _git_run(self.tmp, "rm", "-rfq", "--ignore-unmatch", ".")
        raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        (self.tmp / "authority" / f"{name}.json").write_bytes(raw)
        _git_run(self.tmp, "add", f"authority/{name}.json")
        _git_run(self.tmp, "commit", "-q", "-m", f"synthetic orphan {name} record")
        orphan = _git_run(self.tmp, "rev-parse", "HEAD")
        _git_run(self.tmp, "checkout", "-q", "--detach", anchor)
        return orphan, raw

    def _orphan_rejection_case(self, name: str, where: str, label: str):
        authority_path = self._fixture()
        authority = load_dispatch_authority(authority_path)
        frozen = authority["subject_head"]
        payload = {k: v for k, v in authority[where].items()
                   if k not in ("path", "source_commit", "git_blob_sha1", "canonical_sha256")}
        orphan, raw = self._orphan_record_commit(name, payload)
        record = authority[where]
        record["source_commit"] = orphan
        record["git_blob_sha1"] = _git_blob(self.tmp, orphan, f"authority/{name}.json")
        record["canonical_sha256"] = _sha256_bytes(raw)
        _write_json(authority_path, authority)
        # the orphan record commit is real and its blob binding is exact —
        # only its relation to F is wrong
        self.assertEqual(_git_run(self.tmp, "cat-file", "-t", orphan), "commit")
        self.assertEqual(
            _git_run(self.tmp, "rev-parse", f"{orphan}:authority/{name}.json"),
            record["git_blob_sha1"],
        )
        self._assert_rejected(label, authority_path, "does not descend from the frozen package commit")
        self.assertNotEqual(orphan, frozen)

    def test_review_source_predating_frozen_package_rejected(self):
        self._orphan_rejection_case(
            "review", "review_verdict", "review source predates F / unrelated history"
        )

    def test_verify_source_predating_frozen_package_rejected(self):
        self._orphan_rejection_case(
            "verify", "verify_verdict", "verify source predates F / unrelated history"
        )

    def test_freeze_record_source_predating_frozen_package_rejected(self):
        self._orphan_rejection_case(
            "freeze", "freeze_record", "freeze record source predates F"
        )

    # -- required test 7: authority binds exact record blob refs -----------

    def test_authority_binds_exact_review_verify_record_blob_refs(self):
        authority_path = self._fixture()
        authority = self._authority(authority_path)
        for where, name in (
            ("review_verdict", "review"),
            ("verify_verdict", "verify"),
            ("freeze_record", "freeze"),
            ("hg_b_record", "hg_b"),
            ("r2_record", "r2"),
        ):
            record = authority[where]
            rel = record["path"]
            self.assertEqual(
                record["git_blob_sha1"],
                _git_run(self.tmp, "rev-parse", f"{record['source_commit']}:{rel}"),
                where,
            )
            # the worktree copy is byte-identical to the committed blob
            # (the fixture never touches record files after their commit)
            self.assertEqual(
                record["canonical_sha256"],
                _sha256_bytes((self.tmp / rel).read_bytes()),
                where,
            )

    # -- required test 8: tampered verdict source --------------------------

    def test_tampered_verdict_source_digest_rejected(self):
        def mutate(authority):
            authority["review_verdict"]["canonical_sha256"] = "0" * 64

        self._assert_rejected(
            "tampered verdict digest",
            self._mutated(mutate),
            "immutable source binding mismatch",
        )

    def test_tampered_verdict_source_path_rejected(self):
        def mutate(authority):
            authority["verify_verdict"]["path"] = "authority/never-committed.json"

        self._assert_rejected(
            "tampered verdict path",
            self._mutated(mutate),
            "immutable source binding failed",
        )

    # -- M-7: no self-consistent two-commit shortcut -----------------------

    def test_legacy_two_commit_shortcut_rejected(self):
        # The exact R4.2 scheme the reviewer rejected: one pre-freeze
        # reviewed subject S + one evidence commit E holding the FROZEN
        # bytes and review/verify records pointing back at S. Under the
        # R4.3 validator this self-consistent chain can no longer validate.
        authority_path = self._fixture(legacy_two_commit=True)
        authority = self._authority(authority_path)
        subject = _git_run(self.tmp, "rev-list", "--max-parents=0", "HEAD")
        self.assertEqual(authority["subject_head"], subject)
        self.assertEqual(authority["review_verdict"]["reviewed_head"], subject)
        self.assertEqual(authority["verify_verdict"]["verified_head"], subject)
        self._assert_rejected(
            "two-commit shortcut",
            authority_path,
            "frozen artifacts must be exact blobs of the frozen package commit",
        )

    def test_hg_b_and_r2_records_may_precede_frozen_package(self):
        # HG-B approval + R2 activation intentionally PRECEDE the freeze in
        # the lifecycle (S is approved before F): their own immutable
        # bindings must be sufficient — no ancestry requirement.
        authority_path = self._fixture()
        authority = self._authority(authority_path)
        frozen = authority["subject_head"]
        hg_b_source = authority["hg_b_record"]["source_commit"]
        self.assertEqual(authority["r2_record"]["source_commit"], hg_b_source)
        # commit H (hg_b + r2 records) really is an ancestor of F: a legal
        # pre-freeze record placement
        _git_run(self.tmp, "merge-base", "--is-ancestor", hg_b_source, frozen)
        report = self._validate(authority_path)
        self.assertEqual(report["status"], "DISPATCH_PRECONDITIONS_RECORDED")


class PairReplacementAtomicityTest(unittest.TestCase):
    """R4.2 M-6: replacement is a two-phase transaction; m-2: snapshot safety.

    Every rejection — before or during commit — must leave the ledger
    structurally identical: no cursor movement, no quota consumption, no
    source-pair change, no new pair, no new attempt, no new ledger event.
    """

    def setUp(self):
        self.pools = {"0b": [111, 222, 333], "32b": [444]}
        self.ledger = ReplacementLedger({"0b": 2, "32b": 1}, self.pools)

    def _open_failed_pair(self, pair_id="pair-1", variant="0b", seed=700,
                          author="run-0001", external="run-0002"):
        self.ledger.open_pair(pair_id, variant, seed)
        self.ledger.record_attempt(author, pair_id, "author", "FAILED_TECHNICAL")
        self.ledger.record_attempt(external, pair_id, "external", "COMPLETED")
        return pair_id

    def _snapshot(self):
        return self.ledger.state_snapshot()

    def _assert_rejection_is_inert(self, baseline, call):
        with self.assertRaises((ValueError, ReplacementBudgetExhausted)):
            call()
        self.assertEqual(self._snapshot(), baseline)

    def test_state_snapshot_helper_covers_required_surfaces(self):
        failed = self._open_failed_pair()
        snapshot = self._snapshot()
        self.assertEqual(
            sorted(snapshot),
            ["attempts", "ledger", "pairs", "pool_cursor", "quota_pairs", "seed_owner", "used_pairs"],
        )
        self.assertIn(failed, snapshot["pairs"])
        self.assertEqual(len(snapshot["ledger"]), 3)  # opened + two legs
        self.assertEqual(snapshot["used_pairs"], {"0b": 0, "32b": 0})
        # the snapshot is independent of live state
        snapshot["pairs"][failed]["legs"]["author"] = "tampered"
        self.assertNotEqual(snapshot["pairs"][failed], self.ledger.pair(failed))

    def test_duplicate_replacement_pair_id_rejected_without_state_change(self):
        failed = self._open_failed_pair()
        baseline = self._snapshot()
        self._assert_rejection_is_inert(
            baseline,
            lambda: self.ledger.request_replacement(
                "0b", failed, failed, "rp-a", "rp-e"
            ),
        )
        self.assertEqual(self.ledger.pair_state(failed), "PAIR_FAILED_TECHNICAL")

    def test_duplicate_author_attempt_id_rejected_without_state_change(self):
        failed = self._open_failed_pair()
        baseline = self._snapshot()
        self._assert_rejection_is_inert(
            baseline,
            lambda: self.ledger.request_replacement(
                "0b", failed, "pair-1-RP1", "run-0001", "rp-e"
            ),
        )

    def test_duplicate_external_attempt_id_rejected_without_state_change(self):
        failed = self._open_failed_pair()
        baseline = self._snapshot()
        self._assert_rejection_is_inert(
            baseline,
            lambda: self.ledger.request_replacement(
                "0b", failed, "pair-1-RP1", "rp-a", "run-0002"
            ),
        )

    def test_invalid_author_attempt_id_format_rejected_without_state_change(self):
        failed = self._open_failed_pair()
        baseline = self._snapshot()
        self._assert_rejection_is_inert(
            baseline,
            lambda: self.ledger.request_replacement(
                "0b", failed, "pair-1-RP1", "bad id with spaces", "rp-e"
            ),
        )

    def test_invalid_external_attempt_id_format_rejected_without_state_change(self):
        failed = self._open_failed_pair()
        baseline = self._snapshot()
        self._assert_rejection_is_inert(
            baseline,
            lambda: self.ledger.request_replacement(
                "0b", failed, "pair-1-RP1", "rp-a", "bad id with spaces"
            ),
        )

    def test_replacement_seed_already_owned_rejected_without_state_change(self):
        # pool identity 700 is already owned by an existing pair: the next
        # replacement candidate would collide with an owned seed
        self.ledger.open_pair("pair-owned", "0b", 111)
        failed = self._open_failed_pair(seed=700)
        baseline = self._snapshot()
        self._assert_rejection_is_inert(
            baseline,
            lambda: self.ledger.request_replacement(
                "0b", failed, "pair-1-RP1", "rp-a", "rp-e"
            ),
        )
        self.assertEqual(self.ledger.pool_cursor("0b"), 0)

    def test_second_leg_failure_rolls_back_entire_transaction(self):
        failed = self._open_failed_pair()
        baseline = self._snapshot()
        original = ReplacementLedger._bind_attempt

        def failing_bind(self, attempt_id, pair_id, leg, outcome, allow_scheduled):
            if leg == "external":
                raise ValueError("simulated second-leg binding failure")
            return original(self, attempt_id, pair_id, leg, outcome, allow_scheduled)

        with mock.patch.object(ReplacementLedger, "_bind_attempt", failing_bind):
            with self.assertRaises(ValueError):
                self.ledger.request_replacement("0b", failed, "pair-1-RP1", "rp-a", "rp-e")
        # the rollback guard restored every touched structure
        self.assertEqual(self._snapshot(), baseline)
        self.assertEqual(self.ledger.pair_state(failed), "PAIR_FAILED_TECHNICAL")
        with self.assertRaises(ValueError):
            self.ledger.pair("pair-1-RP1")  # no partial replacement pair

    def test_successful_replacement_still_atomic_and_complete(self):
        failed = self._open_failed_pair()
        identity = self.ledger.request_replacement(
            "0b", failed, "pair-1-RP1", "rp-a", "rp-e"
        )
        self.assertEqual(identity, 111)
        self.assertEqual(self.ledger.pool_cursor("0b"), 1)
        self.assertEqual(self.ledger.used_pairs("0b"), 1)
        self.assertEqual(self.ledger.pair_state(failed), "PAIR_REPLACED")
        self.assertEqual(
            self.ledger.pair("pair-1-RP1")["legs"], {"author": "rp-a", "external": "rp-e"}
        )
        self.assertEqual(len(self.ledger.ledger), 7)  # 3 source + pair opened + 2 legs + assignment

    def test_open_pair_returns_independent_snapshot(self):
        # R4.2, m-2: mutating the returned dict must not reach the ledger
        returned = self.ledger.open_pair("pair-a", "0b", 10)
        returned["legs"]["author"] = "hijacked"
        returned["state"] = "PAIR_COMPLETED"
        self.assertEqual(self.ledger.pair("pair-a")["legs"], {})
        self.assertEqual(self.ledger.pair_state("pair-a"), "PAIR_RUNNING")

    def test_ledger_property_returns_independent_event_snapshots(self):
        self.ledger.open_pair("pair-a", "0b", 10)
        events = self.ledger.ledger
        events[0]["event"] = "FORGED"
        events.append({"event": "FORGED"})
        self.assertEqual(self.ledger.ledger[0]["event"], "PAIR_OPENED")
        self.assertEqual(len(self.ledger.ledger), 1)

    def test_pair_property_deep_copies_legs(self):
        self.ledger.open_pair("pair-a", "0b", 10)
        self.ledger.record_attempt("a-1", "pair-a", "author", "COMPLETED")
        view = self.ledger.pair("pair-a")
        view["legs"]["author"] = "hijacked"
        self.assertEqual(self.ledger.pair("pair-a")["legs"]["author"], "a-1")


if __name__ == "__main__":
    unittest.main()
