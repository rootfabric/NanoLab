"""Baseline determinism tests for the NL4 toolkit (WO-NL4-001 item 6).

Two independent sessions with the same goal must produce byte-identical
canonical reports for both the random baseline (goal-seeded RNG) and the
grid baseline (exhaustive canonical-order sweep). Budget accounting is
identical: both stop within max_simulations.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from e2.canonical import canonical_json
from nl4.agents.baseline_grid import GridBaseline
from nl4.agents.baseline_random import RandomBaseline, random_seed_from_goal
from nl4.controller import Controller, load_allowlist
from nl4.mock_executor import MockExecutor

GOAL = {"target_angle_deg": 45.0, "max_simulations": 5, "max_wall_minutes": 30.0}


def session(agent_factory, goal):
    allowlist = load_allowlist()
    controller = Controller(goal, MockExecutor(), allowlist)
    report = controller.run(agent_factory(goal, allowlist))
    return canonical_json(report), report


class RandomBaselineDeterminism(unittest.TestCase):
    def test_two_runs_identical(self):
        first, _ = session(lambda g, a: RandomBaseline(g, a), GOAL)
        second, _ = session(lambda g, a: RandomBaseline(g, a), GOAL)
        self.assertEqual(first, second)

    def test_goal_seeded_rng_reproducible(self):
        self.assertEqual(random_seed_from_goal(GOAL), random_seed_from_goal(dict(GOAL)))
        other = dict(GOAL, target_angle_deg=60.0)
        self.assertNotEqual(random_seed_from_goal(GOAL), random_seed_from_goal(other))

    def test_budget_respected(self):
        _, report = session(lambda g, a: RandomBaseline(g, a), GOAL)
        self.assertLessEqual(report["budget"]["simulations_used"], 5)


class GridBaselineDeterminism(unittest.TestCase):
    def test_two_runs_identical(self):
        first, _ = session(lambda g, a: GridBaseline(g, a), GOAL)
        second, _ = session(lambda g, a: GridBaseline(g, a), GOAL)
        self.assertEqual(first, second)

    def test_canonical_order_and_budget(self):
        _, report = session(lambda g, a: GridBaseline(g, a), GOAL)
        self.assertEqual(len(report["runs"]), 5)
        self.assertEqual(report["stop_reason"], "BUDGET_EXHAUSTED_SIMULATIONS")
        expected = [
            {"variant": "0b", "steps": 50000, "seed": 201004},
            {"variant": "0b", "steps": 50000, "seed": 202008},
            {"variant": "0b", "steps": 50000, "seed": 203012},
            {"variant": "0b", "steps": 100000, "seed": 201004},
            {"variant": "0b", "steps": 100000, "seed": 202008},
        ]
        self.assertEqual([run["candidate"] for run in report["runs"]], expected)
        self.assertEqual(
            [run["run_id"] for run in report["runs"]],
            ["NL4-MOCK-R0001", "NL4-MOCK-R0002", "NL4-MOCK-R0003", "NL4-MOCK-R0004", "NL4-MOCK-R0005"],
        )

    def test_full_space_sweep_stops_voluntarily(self):
        goal = {"target_angle_deg": 45.0, "max_simulations": 50, "max_wall_minutes": 30.0}
        _, report = session(lambda g, a: GridBaseline(g, a), goal)
        # 5 variants x 3 steps x 3 seeds = 45 candidates < budget 50
        self.assertEqual(len(report["runs"]), 45)
        self.assertEqual(report["stop_reason"], "AGENT_STOPPED")

    def test_grid_and_random_use_same_accounting(self):
        _, grid_report = session(lambda g, a: GridBaseline(g, a), GOAL)
        _, random_report = session(lambda g, a: RandomBaseline(g, a), GOAL)
        self.assertEqual(grid_report["budget"]["max_simulations"], random_report["budget"]["max_simulations"])
        self.assertEqual(
            sorted(grid_report["actions_log"][0].keys()),
            sorted(random_report["actions_log"][0].keys()),
        )


if __name__ == "__main__":
    unittest.main()
