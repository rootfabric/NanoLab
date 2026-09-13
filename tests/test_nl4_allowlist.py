"""Allowlist negative controls for the NL4 toolkit (WO-NL4-001 item 6).

Every out-of-allowlist proposal must be REJECTED and LOGGED, and the
execution must NOT happen. Covered rejection classes (>= 3 distinct):
unknown action, out-of-allowlist candidate parameter, forbidden/unknown
candidate field, budget exhaustion (simulations and wall), seed reuse.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from nl4.agents.bounded_agent import BoundedAgent, ScriptedBrain
from nl4.controller import (
    ACTION_NOT_IN_ALLOWLIST,
    BUDGET_EXHAUSTED_SIMULATIONS,
    BUDGET_EXHAUSTED_WALL,
    CANDIDATE_PARAM_NOT_IN_ALLOWLIST,
    FORBIDDEN_CANDIDATE_FIELD,
    UNKNOWN_CANDIDATE_FIELD,
    Controller,
    load_allowlist,
    normalize_candidate,
)
from nl4.mock_executor import MockExecutor

GOAL = {"target_angle_deg": 45.0, "max_simulations": 5, "max_wall_minutes": 30.0}


def run_scripted(goal, proposals):
    allowlist = load_allowlist()
    agent = BoundedAgent(ScriptedBrain(proposals), goal, allowlist)
    controller = Controller(goal, MockExecutor(), allowlist)
    return controller.run(agent), agent


def run_raw(goal, proposals):
    """Feed raw proposals straight to the controller (defense in depth)."""
    allowlist = load_allowlist()
    agent = ScriptedBrain(proposals)
    controller = Controller(goal, MockExecutor(), allowlist)
    return controller.run(agent)


class AllowlistStructure(unittest.TestCase):
    def test_frozen_actions(self):
        allowlist = load_allowlist()
        self.assertTrue(allowlist["frozen"])
        self.assertEqual(
            sorted(allowlist["actions"]),
            ["propose_candidate", "read_analysis", "request_run", "stop"],
        )
        self.assertEqual(
            allowlist["candidate_params"]["variant"]["values"],
            ["0b", "11b", "32b", "53b", "74b"],
        )
        self.assertEqual(
            allowlist["candidate_params"]["steps"]["values"],
            [50000, 100000, 150000],
        )
        self.assertEqual(
            allowlist["candidate_params"]["seed"]["values"],
            [201004, 202008, 203012],
        )


class CandidateValidationNegatives(unittest.TestCase):
    def setUp(self):
        self.allowlist = load_allowlist()

    def test_variant_outside_allowlist_rejected(self):
        candidate, reason = normalize_candidate(
            {"variant": "99b", "steps": 150000, "seed": 201004}, self.allowlist
        )
        self.assertIsNone(candidate)
        self.assertEqual(reason, CANDIDATE_PARAM_NOT_IN_ALLOWLIST)

    def test_steps_outside_allowlist_rejected(self):
        candidate, reason = normalize_candidate({"variant": "0b", "steps": 12345}, self.allowlist)
        self.assertIsNone(candidate)
        self.assertEqual(reason, CANDIDATE_PARAM_NOT_IN_ALLOWLIST)

    def test_seed_outside_allowlist_rejected(self):
        candidate, reason = normalize_candidate({"variant": "0b", "seed": 1}, self.allowlist)
        self.assertIsNone(candidate)
        self.assertEqual(reason, CANDIDATE_PARAM_NOT_IN_ALLOWLIST)

    def test_forbidden_field_rejected(self):
        candidate, reason = normalize_candidate(
            {"variant": "0b", "physics": "oxdna2-custom"}, self.allowlist
        )
        self.assertIsNone(candidate)
        self.assertEqual(reason, FORBIDDEN_CANDIDATE_FIELD)

    def test_unknown_field_rejected(self):
        candidate, reason = normalize_candidate(
            {"variant": "0b", "temperature": 300}, self.allowlist
        )
        self.assertIsNone(candidate)
        self.assertEqual(reason, UNKNOWN_CANDIDATE_FIELD)

    def test_missing_variant_rejected(self):
        candidate, reason = normalize_candidate({"steps": 150000}, self.allowlist)
        self.assertIsNone(candidate)
        self.assertEqual(reason, "CANDIDATE_MISSING_REQUIRED_FIELD")

    def test_defaults_applied(self):
        candidate, reason = normalize_candidate({"variant": "11b"}, self.allowlist)
        self.assertEqual(
            candidate, {"variant": "11b", "steps": 150000, "seed": 201004}
        )
        self.assertIsNone(reason)


class ControllerNegativeControls(unittest.TestCase):
    def test_unknown_action_rejected_not_executed(self):
        report = run_raw(
            GOAL,
            [
                {"action": "tune_protocol", "temperature": 400},
                {"action": "stop"},
            ],
        )
        rejects = [e for e in report["actions_log"] if not e["accepted"]]
        self.assertEqual(len(rejects), 1)
        self.assertEqual(rejects[0]["action"], "tune_protocol")
        self.assertEqual(rejects[0]["reason"], ACTION_NOT_IN_ALLOWLIST)
        self.assertEqual(report["runs"], [])
        self.assertEqual(report["stop_reason"], "AGENT_STOPPED")

    def test_out_of_allowlist_candidate_rejected_not_executed(self):
        report = run_raw(
            GOAL,
            [
                {"action": "propose_candidate", "candidate": {"variant": "99b"}},
                {"action": "propose_candidate", "candidate": {"variant": "0b", "engine": "bypass"}},
                {"action": "stop"},
            ],
        )
        rejects = [e for e in report["actions_log"] if not e["accepted"]]
        self.assertEqual(len(rejects), 2)
        self.assertEqual(
            sorted(r["reason"] for r in rejects),
            [CANDIDATE_PARAM_NOT_IN_ALLOWLIST, FORBIDDEN_CANDIDATE_FIELD],
        )
        self.assertEqual(report["runs"], [])

    def test_simulation_budget_never_exceeded(self):
        goal = {"target_angle_deg": 45.0, "max_simulations": 2, "max_wall_minutes": 30.0}
        report = run_raw(
            goal,
            [
                {"action": "propose_candidate", "candidate": {"variant": "0b"}},
                {"action": "request_run", "candidate": {"variant": "0b"}},
                {"action": "propose_candidate", "candidate": {"variant": "11b"}},
                {"action": "request_run", "candidate": {"variant": "11b"}},
                # third pair would exceed max_simulations = 2
                {"action": "propose_candidate", "candidate": {"variant": "32b"}},
                {"action": "request_run", "candidate": {"variant": "32b"}},
            ],
        )
        self.assertEqual(len(report["runs"]), 2)
        self.assertLessEqual(report["budget"]["simulations_used"], 2)
        self.assertEqual(report["stop_reason"], BUDGET_EXHAUSTED_SIMULATIONS)

    def test_wall_budget_rejected_before_execution(self):
        goal = {"target_angle_deg": 45.0, "max_simulations": 5, "max_wall_minutes": 0.001}
        report = run_raw(
            goal,
            [
                {"action": "propose_candidate", "candidate": {"variant": "0b"}},
                {"action": "request_run", "candidate": {"variant": "0b"}},
                {"action": "stop"},
            ],
        )
        self.assertEqual(report["runs"], [])
        rejects = [e for e in report["actions_log"] if not e["accepted"]]
        self.assertTrue(any(r["reason"] == BUDGET_EXHAUSTED_WALL for r in rejects))

    def test_duplicate_candidate_rerun_rejected(self):
        report = run_raw(
            GOAL,
            [
                {"action": "propose_candidate", "candidate": {"variant": "0b"}},
                {"action": "request_run", "candidate": {"variant": "0b"}},
                # identical (variant, steps, seed) requested again
                {"action": "propose_candidate", "candidate": {"variant": "0b"}},
                {"action": "request_run", "candidate": {"variant": "0b"}},
                {"action": "stop"},
            ],
        )
        self.assertEqual(len(report["runs"]), 1)
        rejects = [e for e in report["actions_log"] if not e["accepted"]]
        self.assertEqual(
            [(r["action"], r["reason"]) for r in rejects],
            [("request_run", "CANDIDATE_ALREADY_RUN")],
        )


class BoundedAgentNegativeControls(unittest.TestCase):
    def test_out_of_allowlist_never_forwarded(self):
        goal = {"target_angle_deg": 45.0, "max_simulations": 5, "max_wall_minutes": 30.0}
        report, agent = run_scripted(
            goal,
            [
                {"action": "run_engine", "command": "oxDNA"},
                {"action": "propose_candidate", "candidate": {"variant": "hack", "protocol": "custom"}},
                {"action": "propose_candidate", "candidate": {"variant": "0b"}},
                {"action": "request_run", "candidate": {"variant": "0b"}},
                {"action": "stop"},
            ],
        )
        # both raw violations rejected inside the wrapper, logged, never executed
        self.assertEqual(len(agent.rejected_actions), 2)
        self.assertEqual(
            sorted(r["reason"] for r in agent.rejected_actions),
            [ACTION_NOT_IN_ALLOWLIST, FORBIDDEN_CANDIDATE_FIELD],
        )
        self.assertEqual(len(report["runs"]), 1)
        self.assertEqual(report["bounded_agent_rejected"], agent.rejected_actions)

    def test_wrapper_budget_mirror_rejects_excess(self):
        goal = {"target_angle_deg": 45.0, "max_simulations": 2, "max_wall_minutes": 30.0}
        allowlist = load_allowlist()
        proposals = []
        for variant in ("0b", "11b", "32b"):
            proposals.append({"action": "propose_candidate", "candidate": {"variant": variant}})
            proposals.append({"action": "request_run", "candidate": {"variant": variant}})
        agent = BoundedAgent(ScriptedBrain(proposals), goal, allowlist)
        forwarded_requests = 0
        while True:
            action = agent.next_action([])
            if action is None or action == {"action": "stop"}:
                break
            if action["action"] == "request_run":
                forwarded_requests += 1
        self.assertEqual(forwarded_requests, 2)
        self.assertEqual(
            [r["reason"] for r in agent.rejected_actions],
            [BUDGET_EXHAUSTED_SIMULATIONS],
        )


if __name__ == "__main__":
    unittest.main()
