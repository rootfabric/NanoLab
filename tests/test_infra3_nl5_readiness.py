"""Offline unit tests for the INFRA3 NL5 v0.2 readiness package (WO-INFRA3-NL5-READINESS-R1, issue #65).

Science-free and fully offline: the tests only parse repository JSON/markdown
deliverables and re-derive arithmetic from pinned values. No subprocess, no
network, no oxDNA, no scientific run is triggered by this module. The manifest
under test is a DRY-RUN skeleton: it must never authorize or trigger a
calculation and must carry only honest statuses (HOST_NOT_ASSIGNED / NOT_MET).
"""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "docs" / "infra" / "NL5_V02_DRYRUN_MANIFEST_R1.json"
REPORT_PATH = REPO_ROOT / "docs" / "infra" / "INFRA3_NL5_READINESS_REPORT_R1.md"
CHECKLIST_PATH = REPO_ROOT / "docs" / "infra" / "U1_PROVISIONING_CHECKLIST_R1.md"
WO_PATH = REPO_ROOT / "docs" / "work" / "WO-INFRA3-NL5-READINESS-R1.md"
R2_CONFIG_PATH = REPO_ROOT / "config" / "infra" / "r2-activation.v1.json"
FROZEN_PROTOCOL_PATH = REPO_ROOT / "docs" / "research" / "NANOLAB_REPRO_V0_2_FROZEN_R2.md"
DIRECTOR_FREEZE_PATH = REPO_ROOT / "docs" / "evidence" / "NL5-V02-FREEZE" / "DIRECTOR_FREEZE_R2.json"

HONEST_STATUSES = {"HOST_NOT_ASSIGNED", "NOT_MET"}

ENGINE_PIN = "00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591"
FROZEN_PROTOCOL_SHA256 = "2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d"
FROZEN_PACKAGE_COMMIT = "60da9a846511265a8ac7564da088c3d74cb073f0"
FROZEN_PACKAGE_TREE = "e565c8a6cee9e829fac14008ebc9c2ea1609931d"
EXPECTED_CONFIRMATORY_RUNS = 296  # 2 * (64 + 64 + 10 + 10)
EXPECTED_REPLACEMENT_CAP = 56
EXPECTED_MAX_RUNS = 352


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest() -> dict:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class ManifestParses(unittest.TestCase):
    """The dry-run manifest is valid, machine-readable and honestly framed."""

    def setUp(self) -> None:
        self.manifest = load_manifest()

    def test_manifest_file_exists_and_parses(self) -> None:
        self.assertTrue(MANIFEST_PATH.is_file())
        self.assertIsInstance(self.manifest, dict)

    def test_dry_run_flags_are_absolute(self) -> None:
        self.assertIs(self.manifest["dry_run"], True)
        self.assertEqual(self.manifest["run_mode"], "NONE")
        self.assertEqual(self.manifest["scientific_runs_triggered_by_this_manifest"], 0)

    def test_readiness_class_is_ready_for_host(self) -> None:
        self.assertEqual(self.manifest["readiness_class"], "READY_FOR_HOST")
        self.assertEqual(self.manifest["host_assignment"]["author_u1"], "NOT_ASSIGNED")
        self.assertEqual(self.manifest["host_assignment"]["r2_status"], "WAITING_HOST / NOT_ACTIVE")
        self.assertIs(self.manifest["host_assignment"]["r2_activated"], False)


class FrozenProtocolBinding(unittest.TestCase):
    """Manifest pins must equal the canonical frozen artifacts on this base."""

    def setUp(self) -> None:
        self.manifest = load_manifest()

    def test_protocol_sha256_matches_file_on_disk(self) -> None:
        pinned = self.manifest["campaign"]["frozen_protocol"]["sha256"]
        self.assertEqual(pinned, FROZEN_PROTOCOL_SHA256)
        self.assertEqual(sha256_file(FROZEN_PROTOCOL_PATH), FROZEN_PROTOCOL_SHA256)

    def test_frozen_package_commit_and_tree_pinned(self) -> None:
        protocol = self.manifest["campaign"]["frozen_protocol"]
        self.assertEqual(protocol["frozen_package_commit"], FROZEN_PACKAGE_COMMIT)
        self.assertEqual(protocol["frozen_package_tree"], FROZEN_PACKAGE_TREE)

    def test_director_freeze_record_pins_agree_with_manifest(self) -> None:
        with DIRECTOR_FREEZE_PATH.open("r", encoding="utf-8") as handle:
            freeze = json.load(handle)
        self.assertEqual(freeze["subject_head"], FROZEN_PACKAGE_COMMIT)
        self.assertEqual(freeze["subject_tree"], FROZEN_PACKAGE_TREE)
        self.assertEqual(freeze["protocol_sha256"], FROZEN_PROTOCOL_SHA256)
        self.assertEqual(freeze["protocol_path"], self.manifest["campaign"]["frozen_protocol"]["path"])
        contract = self.manifest["campaign"]["authoritative_contract"]
        seed = self.manifest["campaign"]["seed_record"]
        self.assertEqual(freeze["contract_path"], contract["path"])
        self.assertEqual(freeze["contract_sha256"], contract["sha256"])
        self.assertEqual(freeze["seed_record_path"], seed["path"])
        self.assertEqual(freeze["seed_record_sha256"], seed["sha256"])

    def test_engine_pin_matches_canonical_r2_contract(self) -> None:
        self.assertEqual(self.manifest["engine_pin"]["pinned_commit"], ENGINE_PIN)
        with R2_CONFIG_PATH.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        self.assertEqual(config["engine"]["pinned_commit"], ENGINE_PIN)
        flags = self.manifest["engine_pin"]["build_flags"]
        self.assertEqual(flags["CMAKE_BUILD_TYPE"], "Release")
        self.assertEqual(flags["DOUBLE"], "ON")
        self.assertEqual(flags["CUDA"], "OFF")
        self.assertEqual(flags["MPI"], "OFF")


class CampaignNumbers(unittest.TestCase):
    """Campaign arithmetic must re-derive exactly as the frozen protocol declares."""

    def setUp(self) -> None:
        self.manifest = load_manifest()

    def test_budget_numbers_match_frozen_protocol(self) -> None:
        budgets = self.manifest["budgets"]
        self.assertEqual(budgets["confirmatory_runs"], EXPECTED_CONFIRMATORY_RUNS)
        self.assertEqual(budgets["replacement_runs_cap"], EXPECTED_REPLACEMENT_CAP)
        self.assertEqual(budgets["max_runs"], EXPECTED_MAX_RUNS)
        self.assertEqual(budgets["confirmatory_runs"] + budgets["replacement_runs_cap"], budgets["max_runs"])
        self.assertEqual(budgets["wall_hours_per_platform"], 560)
        self.assertEqual(budgets["selected_n"], 64)
        self.assertEqual(budgets["n_min_valid_pairs"], {"primary": 52, "control": 8})
        self.assertEqual(budgets["replacement_quota_pairs_primary"], 12)
        self.assertEqual(budgets["replacement_quota_pairs_control"], 2)

    def test_variant_cardinality_multiplies_to_148_per_leg(self) -> None:
        excluded = {"excluded", "NOT_MEASURED / KNOWN_GAP - production FORBIDDEN until separate arm-manifest-v2 repair WO"}
        total_per_leg = 0
        for variant in self.manifest["calculation_scheme"]["variants"]:
            if variant.get("class") in excluded or variant["variant"] == "74b":
                self.assertEqual(variant["n_per_leg"], 0)
                continue
            total_per_leg += variant["n_per_leg"]
        self.assertEqual(total_per_leg, 148)

    def test_legs_are_exactly_u1_and_u2(self) -> None:
        legs = {leg["leg"]: leg for leg in self.manifest["calculation_scheme"]["legs"]}
        self.assertEqual(set(legs), {"U1", "U2"})
        self.assertEqual(legs["U1"]["role"], "AUTHOR")
        self.assertEqual(legs["U2"]["role"], "EXTERNAL_REPRODUCTION")
        self.assertEqual(legs["U1"]["host_status"], "HOST_NOT_ASSIGNED")

    def test_enumerated_confirmatory_ids_are_unique_and_total_296(self) -> None:
        scheme = self.manifest["calculation_scheme"]
        match = re.fullmatch(r"nl5v02-<leg>-<variant>-r<NNNN>", scheme["run_id_template"])
        self.assertIsNotNone(match, "run_id_template changed; update the enumeration below")
        variants = [v for v in scheme["variants"] if v["variant"] != "74b"]
        run_ids: list[str] = []
        for leg in ("u1", "u2"):
            for variant in variants:
                for replica in range(1, variant["n_per_leg"] + 1):
                    run_ids.append(f"nl5v02-{leg}-{variant['variant']}-r{replica:04d}")
        self.assertEqual(len(run_ids), EXPECTED_CONFIRMATORY_RUNS)
        self.assertEqual(len(set(run_ids)), len(run_ids))

    def test_input_digests_are_pending_placeholders(self) -> None:
        digests = self.manifest["calculation_scheme"]["input_digests"]
        self.assertEqual(digests["status"], "PENDING_DISPATCH")
        self.assertEqual(digests["entries"], [])


class GatesAndNegativeControls(unittest.TestCase):
    """Gate entries are complete, uniquely identified and honest."""

    def setUp(self) -> None:
        self.manifest = load_manifest()
        self.gates = self.manifest["gates"]
        self.controls = self.manifest["negative_controls"]

    def test_gate_and_control_ids_unique(self) -> None:
        gate_ids = [gate["id"] for gate in self.gates]
        control_ids = [nc["id"] for nc in self.controls]
        self.assertEqual(gate_ids, ["U1", "U2", "U3", "U4", "U5"])
        self.assertEqual(control_ids, ["NC-U1", "NC-U2", "NC-U3", "NC-U4", "NC-U5"])
        self.assertEqual(len(set(gate_ids + control_ids)), 10)

    def test_every_gate_entry_is_complete(self) -> None:
        required = {"id", "name", "description", "check_command", "check_artifact", "pass_condition", "host_required", "status"}
        for gate in self.gates + self.controls:
            for field in required:
                self.assertIn(field, gate, f"{gate.get('id')} missing {field}")
                self.assertTrue(str(gate[field]).strip(), f"{gate.get('id')}.{field} is empty")
            self.assertEqual(gate["host_required"], "U1")

    def test_all_statuses_are_honest_no_pass_anywhere(self) -> None:
        for gate in self.gates + self.controls:
            self.assertIn(gate["status"], HONEST_STATUSES, f"{gate['id']} claims a status it did not earn")

    def test_check_commands_are_deferred_tooling_invocations(self) -> None:
        expected_tool = {
            "U1": "r2.cli build-engine",
            "U2": "reproduce.py verify",
            "U3": "r2.cli gate",
            "U4": "r2.cli gate",
            "U5": "harness",
        }
        for gate in self.gates:
            self.assertIn(expected_tool[gate["id"]], gate["check_command"], f"{gate['id']} check_command drifted")
        for control in self.controls:
            self.assertIn("r2.cli nc-", control["check_command"])

    def test_dispatch_is_blocked_and_launch_gate_protected(self) -> None:
        dispatch = self.manifest["dispatch"]
        self.assertEqual(dispatch["status"], "BLOCKED")
        self.assertIs(dispatch["machine_launch_authorized"], False)
        self.assertEqual(dispatch["launch_gate"], "HUMAN_PROTECTED_WRITER")
        self.assertIn("AUTHOR_U1 = NOT_ASSIGNED (no physical host)", dispatch["blockers"])


class NoScientificRunIsTriggered(unittest.TestCase):
    """Negative controls of this package: the manifest cannot launch anything."""

    def setUp(self) -> None:
        self.manifest = load_manifest()
        self.raw = MANIFEST_PATH.read_text(encoding="utf-8")

    def test_manifest_contains_no_execute_now_directive(self) -> None:
        forbidden_markers = ['"command_to_run_now"', '"execute"', '"autostart"', '"schedule"']
        for marker in forbidden_markers:
            self.assertNotIn(marker, self.raw)

    def test_reserved_execution_ids_are_marked_blocked(self) -> None:
        for execution_id in self.manifest["dispatch"]["blocked_execution_ids"]:
            self.assertIn(execution_id, self.manifest["attempt_semantics"]["execution_ids"])
        self.assertEqual(self.manifest["dispatch"]["status"], "BLOCKED")

    def test_outenemy_is_never_author(self) -> None:
        split = self.manifest["platform_split"]
        self.assertIn("EXTERNAL_U2_ONLY", split["U2_independent_reproduction_only"])
        self.assertIn("NEVER authors", split["U2_independent_reproduction_only"])
        self.assertEqual(self.manifest["boundaries"]["outenemy_role"], "EXTERNAL_U2_ONLY")

    def test_windows_fallback_forbidden(self) -> None:
        self.assertIs(self.manifest["boundaries"]["windows_allowed_for_new_science"], False)
        self.assertEqual(self.manifest["boundaries"]["silent_windows_fallback"], "FORBIDDEN")

    def test_excluded_platforms_declared(self) -> None:
        excluded = " ".join(self.manifest["calculation_scheme"]["excluded_platforms"])
        self.assertIn("Windows", excluded)
        self.assertIn("WSL2", excluded)

    def test_boundaries_disallow_canonical_state_changes(self) -> None:
        does_not = " ".join(self.manifest["boundaries"]["this_manifest_does_not"])
        self.assertIn("project/state.json", does_not)
        self.assertIn("project/infra-state.json", does_not)
        self.assertIn("project/plan.json", does_not)
        self.assertIn("acceptance criteria", does_not)

    def test_74b_production_is_forbidden_in_scheme(self) -> None:
        variant_74b = next(v for v in self.manifest["calculation_scheme"]["variants"] if v["variant"] == "74b")
        self.assertIn("FORBIDDEN", variant_74b["status"])


class CompanionDocuments(unittest.TestCase):
    """WO / checklist / report exist and carry the honest outcome class."""

    def test_documents_exist(self) -> None:
        for path in (WO_PATH, CHECKLIST_PATH, REPORT_PATH):
            self.assertTrue(path.is_file(), f"missing {path.name}")

    def test_report_declares_host_not_assigned(self) -> None:
        text = REPORT_PATH.read_text(encoding="utf-8")
        self.assertIn("HOST_NOT_ASSIGNED", text)
        self.assertIn("READY_FOR_HOST", text)
        self.assertIn("AUTHOR_U1            = NOT_ASSIGNED", text)

    def test_report_numbers_agree_with_manifest(self) -> None:
        text = REPORT_PATH.read_text(encoding="utf-8")
        self.assertIn("296", text)
        self.assertIn("352", text)
        self.assertIn("56", text)
        self.assertIn(FROZEN_PROTOCOL_SHA256, text)

    def test_checklist_forbids_outenemy_as_u1(self) -> None:
        text = CHECKLIST_PATH.read_text(encoding="utf-8")
        self.assertIn("U1 ≠ U2", text)
        self.assertIn("EXTERNAL_U2_ONLY", text)
        self.assertIn("HOST_NOT_ASSIGNED", text)

    def test_wo_declares_dry_run_and_claim_ceiling(self) -> None:
        text = WO_PATH.read_text(encoding="utf-8")
        self.assertIn("DRY-RUN ONLY", text)
        self.assertIn("C0_SOFTWARE_ONLY", text)
        self.assertIn("READY_FOR_HOST", text)

    def test_r2_config_still_forbids_outenemy_hostname(self) -> None:
        with R2_CONFIG_PATH.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        self.assertIn("outenemy", config["host_eligibility"]["forbidden_hostnames"])
        self.assertEqual(config["host_eligibility"]["outenemy_role"], "EXTERNAL_U2_ONLY")


if __name__ == "__main__":
    unittest.main()
