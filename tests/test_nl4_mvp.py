"""Tests for the NL4 user-facing MVP (WO-NL4-003): strategy determinism,
verdict logic and report-generation determinism, all on mocks (no engine,
no network, no LLM)."""
from __future__ import annotations

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from nl4.controller import Controller, load_allowlist  # noqa: E402
from nl4.mock_executor import MockExecutor, mock_observables  # noqa: E402
from nl4.mvp import (  # noqa: E402
    DEFAULT_REVALIDATION_SEED,
    InformedGreedyAgent,
    bootstrap_ci_median,
    build_report,
    compute_verdict,
    controller_goal,
    parse_user_goal,
    plan_candidates,
    published_best_gap,
    render_markdown,
)
from nl4.scoring import score_session  # noqa: E402
from e2.canonical import canonical_json  # noqa: E402

GOAL = {"target_angle": 90, "max_simulations": 3, "steps": 50000, "revalidation_runs": 1}


class TestGoalParsing(unittest.TestCase):
    def test_valid_goal(self):
        parsed = parse_user_goal(GOAL)
        self.assertEqual(parsed["target_angle"], 90.0)
        self.assertEqual(parsed["max_simulations"], 3)
        self.assertEqual(parsed["steps"], 50000)

    def test_rejects_bad_steps(self):
        with self.assertRaises(ValueError):
            parse_user_goal(dict(GOAL, steps=12345))

    def test_rejects_out_of_range_target(self):
        with self.assertRaises(ValueError):
            parse_user_goal(dict(GOAL, target_angle=270))

    def test_controller_goal_mapping(self):
        cg = controller_goal(parse_user_goal(GOAL))
        self.assertEqual(cg["target_angle_deg"], 90.0)
        self.assertEqual(cg["max_simulations"], 3)
        self.assertEqual(cg["max_wall_minutes"], 4 * 72)
        self.assertEqual(cg["integrity_gate"], "E2_PROTO_R1_S4_FROZEN")


class TestInformedGreedyStrategy(unittest.TestCase):
    def test_published_nearest_first_90deg(self):
        # |median - 90|: 32b 11.91 < 11b 16.07 < 0b 24.13 < 53b 42.36
        plan = plan_candidates(parse_user_goal(GOAL))
        self.assertEqual(
            plan,
            [
                {"variant": "32b", "steps": 50000, "seed": 201004},
                {"variant": "11b", "steps": 50000, "seed": 202008},
                {"variant": "0b", "steps": 50000, "seed": 203012},
            ],
        )

    def test_deterministic(self):
        a = plan_candidates(parse_user_goal(GOAL))
        b = plan_candidates(parse_user_goal(json.loads(json.dumps(GOAL))))
        self.assertEqual(canonical_json(a), canonical_json(b))

    def test_74b_never_proposed(self):
        for extra in (1, 2, 3, 4):
            plan = plan_candidates(parse_user_goal(dict(GOAL, max_simulations=extra)))
            self.assertNotIn("74b", [c["variant"] for c in plan])

    def test_agent_stream_matches_plan(self):
        plan = plan_candidates(parse_user_goal(GOAL))
        agent = InformedGreedyAgent(plan)
        actions = []
        while True:
            action = agent.next_action([])
            if action is None or action["action"] == "stop":
                break
            actions.append(action)
        self.assertEqual(len(actions), 6)  # propose + request per candidate
        for i in range(3):
            self.assertEqual(actions[2 * i]["action"], "propose_candidate")
            self.assertEqual(actions[2 * i + 1]["action"], "request_run")
            self.assertEqual(actions[2 * i]["candidate"], plan[i])
            self.assertEqual(actions[2 * i + 1]["candidate"], plan[i])


class TestVerdictLogic(unittest.TestCase):
    def _row(self, run_id, score):
        return {"run_id": run_id, "score": score, "integrity_status": "OK" if score is not None else "STRUCTURALLY_INVALID"}

    def test_found(self):
        rows = [self._row("R1", 5.0), self._row("R2", 12.0)]
        rev = {"score": 5.5, "integrity_status": "OK"}
        v = compute_verdict(rows, rev, 90.0)
        self.assertEqual(v["verdict"], "FOUND")
        self.assertEqual(v["reasons"], [])
        self.assertEqual(v["published_best_gap_deg"], published_best_gap(90.0))

    def test_not_found_when_revalidation_worse_than_published(self):
        rows = [self._row("R1", 11.0)]
        rev = {"score": 12.5, "integrity_status": "OK"}
        v = compute_verdict(rows, rev, 90.0)
        self.assertEqual(v["verdict"], "NOT_FOUND")
        self.assertIn("REVALIDATED_SCORE_NOT_BELOW_PUBLISHED_BEST", v["reasons"])

    def test_not_found_on_gate_fail(self):
        rows = [self._row("R1", None), self._row("R2", None)]
        rev = {"score": 5.0, "integrity_status": "OK"}
        v = compute_verdict(rows, rev, 90.0)
        self.assertEqual(v["verdict"], "NOT_FOUND")
        self.assertIn("NO_VALID_CANDIDATE_RUN", v["reasons"])

    def test_not_found_on_revalidation_gate_fail(self):
        rows = [self._row("R1", 5.0)]
        rev = {"score": None, "integrity_status": "STRUCTURALLY_INVALID"}
        v = compute_verdict(rows, rev, 90.0)
        self.assertEqual(v["verdict"], "NOT_FOUND")
        self.assertIn("REVALIDATION_GATE_FAIL", v["reasons"])

    def test_not_found_when_no_revalidation(self):
        rows = [self._row("R1", 5.0)]
        v = compute_verdict(rows, None, 90.0)
        self.assertEqual(v["verdict"], "NOT_FOUND")

    def test_published_best_gap_is_32b_for_90(self):
        self.assertAlmostEqual(published_best_gap(90.0), abs(78.091845516 - 90.0), places=9)


class TestReportGeneration(unittest.TestCase):
    def _mock_session(self):
        user_goal = parse_user_goal(GOAL)
        plan = plan_candidates(user_goal)
        controller = Controller(controller_goal(user_goal), MockExecutor(), load_allowlist())
        report = controller.run(InformedGreedyAgent(plan))
        scoring = score_session(report)
        best = scoring["best"]
        best_candidate = None
        for run in report["runs"]:
            if run["run_id"] == best["run_id"]:
                best_candidate = dict(run["candidate"])
        rev_candidate = dict(best_candidate)
        rev_candidate["seed"] = DEFAULT_REVALIDATION_SEED
        observables = mock_observables(rev_candidate)
        revalidation = {
            "run_id": "E3-MVP-REV001",
            "candidate": rev_candidate,
            "input_digest_sha256": "0" * 64,
            "wall_seconds": 1.0,
            "analysis": observables,
        }
        provenance = {
            "repo_commit": "0" * 40,
            "engine": "MOCK",
            "engine_source_commit": "MOCK",
            "allowlist_revision": "nl4-allowlist-r1",
            "goal_file": "user-goal.json",
        }
        return build_report(user_goal, report, revalidation, {}, provenance)

    def test_report_deterministic(self):
        a = canonical_json(self._mock_session())
        b = canonical_json(self._mock_session())
        self.assertEqual(a, b)

    def test_report_structure(self):
        report = self._mock_session()
        for key in (
            "goal",
            "runs",
            "angle_distribution",
            "gates",
            "chosen",
            "revalidation",
            "confidence",
            "provenance",
            "limitations",
            "reproduction",
            "verdict",
        ):
            self.assertIn(key, report)
        self.assertEqual(len(report["runs"]), 3)
        self.assertEqual(report["revalidation"]["candidate"]["seed"], DEFAULT_REVALIDATION_SEED)
        self.assertIn(report["verdict"]["verdict"], ("FOUND", "NOT_FOUND"))

    def test_markdown_deterministic_and_stable(self):
        md1 = render_markdown(self._mock_session())
        md2 = render_markdown(self._mock_session())
        self.assertEqual(md1, md2)
        self.assertIn("# MVP-отчёт NL4", md1)
        self.assertIn("## Verdict", md1)
        self.assertIn("E3-MVP-REV001", md1)

    def test_bootstrap_ci_deterministic(self):
        values = [float(i) for i in range(1, 38)]
        self.assertEqual(bootstrap_ci_median(values), bootstrap_ci_median(values))


if __name__ == "__main__":
    unittest.main()
