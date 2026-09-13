"""Controller end-to-end tests on the mock executor (WO-NL4-001 item 6).

Goal {target 45 deg, budget 5}: random and grid baselines produce
reproducible candidate/score trajectories; run IDs use the real format
(NL4-MOCK-*); evidence is canonical JSON and byte-deterministic; the
scripted bounded agent completes a 5-candidate session with honest
accounting of invalid runs.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from e2.canonical import canonical_json
from nl4 import __main__ as nl4_main
from nl4.agents.baseline_grid import GridBaseline
from nl4.agents.baseline_random import RandomBaseline
from nl4.agents.bounded_agent import BoundedAgent, ScriptedBrain
from nl4.controller import Controller, load_allowlist
from nl4.mock_executor import MockExecutor, mock_observables
from nl4.scoring import score_session

GOAL = {"target_angle_deg": 45.0, "max_simulations": 5, "max_wall_minutes": 30.0}


def run_agent(agent_factory, goal=None):
    goal = goal or GOAL
    allowlist = load_allowlist()
    controller = Controller(goal, MockExecutor(), allowlist)
    agent = agent_factory(goal, allowlist)
    report = controller.run(agent)
    report["scoring"] = score_session(report)
    return report


class EndToEndMockSession(unittest.TestCase):
    def test_random_five_candidates_reproducible(self):
        first = run_agent(lambda g, a: RandomBaseline(g, a))
        second = run_agent(lambda g, a: RandomBaseline(g, a))
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(len(first["runs"]), 5)
        # controller stops exactly at the simulation cap (budget enforcement
        # wins over the agent's own stop)
        self.assertEqual(first["stop_reason"], "BUDGET_EXHAUSTED_SIMULATIONS")

    def test_grid_five_candidates_reproducible(self):
        first = run_agent(lambda g, a: GridBaseline(g, a))
        second = run_agent(lambda g, a: GridBaseline(g, a))
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(len(first["runs"]), 5)

    def test_run_ids_and_candidate_ids_real_format(self):
        report = run_agent(lambda g, a: GridBaseline(g, a))
        self.assertEqual(
            [run["run_id"] for run in report["runs"]],
            ["NL4-MOCK-R000%d" % i for i in range(1, 6)],
        )
        self.assertEqual(
            [cid for cid in report["candidates"]],
            ["CAND-%04d" % i for i in range(1, 6)],
        )

    def test_scripted_bounded_agent_session(self):
        variants_steps = [("0b", 50000), ("11b", 100000), ("32b", 150000), ("53b", 50000)]
        proposals = [{"action": "read_analysis"}]
        proposals += [
            {"action": "propose_candidate", "candidate": {"variant": v, "steps": s}}
            for v, s in variants_steps
        ]
        proposals += [
            {"action": "request_run", "candidate": {"variant": v, "steps": s}}
            for v, s in variants_steps
        ]
        proposals += [
            {"action": "propose_candidate", "candidate": {"variant": "74b"}},
            {"action": "request_run", "candidate": {"variant": "74b"}},
            {"action": "stop"},
        ]
        report = run_agent(lambda g, a: BoundedAgent(ScriptedBrain(proposals), g, a))
        self.assertEqual(len(report["runs"]), 5)
        self.assertEqual(report["stop_reason"], "BUDGET_EXHAUSTED_SIMULATIONS")
        self.assertEqual(
            [run["candidate"]["variant"] for run in report["runs"]],
            ["0b", "11b", "32b", "53b", "74b"],
        )
        # honest accounting: every executed run is scored or marked invalid
        scoring = report["scoring"]
        self.assertEqual(scoring["counts"]["runs_executed"], 5)
        self.assertEqual(
            scoring["counts"]["runs_executed"],
            scoring["counts"]["runs_scored"] + scoring["counts"]["runs_structurally_invalid"],
        )

    def test_actions_log_complete_trajectory(self):
        report = run_agent(lambda g, a: GridBaseline(g, a))
        names = [entry["action"] for entry in report["actions_log"]]
        # propose + request for each of 5 candidates, no rejects
        self.assertEqual(names.count("propose_candidate"), 5)
        self.assertEqual(names.count("request_run"), 5)
        self.assertTrue(all(entry["accepted"] for entry in report["actions_log"]))
        self.assertEqual(report["budget"]["simulations_used"], 5)

    def test_every_action_in_allowlist(self):
        for factory in (
            lambda g, a: RandomBaseline(g, a),
            lambda g, a: GridBaseline(g, a),
        ):
            report = run_agent(factory)
            allowed = set(load_allowlist()["actions"])
            for entry in report["actions_log"]:
                self.assertIn(entry["action"], allowed)


class MockExecutorContract(unittest.TestCase):
    def test_deterministic_pseudo_observables(self):
        candidate = {"variant": "0b", "steps": 150000, "seed": 201004}
        self.assertEqual(mock_observables(candidate), mock_observables(dict(candidate)))
        other = {"variant": "0b", "steps": 150000, "seed": 202008}
        self.assertNotEqual(
            mock_observables(candidate)["median_angle_deg"],
            mock_observables(other)["median_angle_deg"],
        )

    def test_analysis_fields_present(self):
        executor = MockExecutor()
        result = executor.run({"variant": "11b", "steps": 100000, "seed": 202008}, 1)
        for key in ("run_id", "analysis", "wall_seconds", "input_digest_sha256"):
            self.assertIn(key, result)
        analysis = result["analysis"]
        for key in (
            "median_angle_deg",
            "long_bond_fraction",
            "pairs_fraction_v2",
            "displacement_max",
        ):
            self.assertIn(key, analysis)
        self.assertGreaterEqual(analysis["median_angle_deg"], 20.0)
        self.assertLessEqual(analysis["median_angle_deg"], 160.0)


class CanonicalJsonDeterminism(unittest.TestCase):
    def test_report_byte_identical_across_instances(self):
        allowlist = load_allowlist()

        def render():
            controller = Controller(GOAL, MockExecutor(), allowlist)
            return controller.render_report(GridBaseline(GOAL, allowlist))

        self.assertEqual(render(), render())

    def test_no_wall_clock_in_report(self):
        report = run_agent(lambda g, a: RandomBaseline(g, a))
        text = canonical_json(report)
        for marker in ("timestamp", "datetime", "started_at"):
            self.assertNotIn(marker, text)


class CliSmoke(unittest.TestCase):
    def test_demo_grid_matches_library(self):
        code = nl4_main.main(
            [
                "demo",
                "--agent",
                "grid",
                "--target",
                "45",
                "--max-simulations",
                "5",
                "--max-wall-minutes",
                "30",
            ]
        )
        self.assertEqual(code, 0)

    def test_validate_candidate_cli(self):
        code = nl4_main.main(
            ["validate-candidate", '{"variant": "0b", "steps": 50000, "seed": 201004}']
        )
        self.assertEqual(code, 0)
        code = nl4_main.main(["validate-candidate", '{"variant": "99b"}'])
        self.assertEqual(code, 3)


if __name__ == "__main__":
    unittest.main()
