"""Scoring math tests for the NL4 toolkit (WO-NL4-001 item 6).

score = |median_angle - target| with the frozen E2_PROTO_R1 §4 integrity
gates (lbf <= 0.1078, pf_v2 >= 0.50, disp <= 20.0); invalid and rejected
runs are accounted honestly (score = None, counted, never averaged in).
All expected numbers below are exact.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from nl4.scoring import (
    LONG_BOND_FRACTION_MAX,
    PAIRS_FRACTION_V2_MIN,
    DISPLACEMENT_MAX,
    integrity_status,
    score_run,
    score_session,
)


def analysis(median, lbf=0.05, pf=0.90, disp=5.0):
    return {
        "median_angle_deg": median,
        "long_bond_fraction": lbf,
        "pairs_fraction_v2": pf,
        "displacement_max": disp,
    }


class FrozenGateConstants(unittest.TestCase):
    def test_match_e2_proto_r1_section4(self):
        self.assertEqual(LONG_BOND_FRACTION_MAX, 0.1078)
        self.assertEqual(PAIRS_FRACTION_V2_MIN, 0.50)
        self.assertEqual(DISPLACEMENT_MAX, 20.0)


class IntegrityStatus(unittest.TestCase):
    def test_valid_frame(self):
        self.assertEqual(integrity_status(analysis(60.0)), "OK")

    def test_lbf_gate_breach(self):
        self.assertEqual(integrity_status(analysis(60.0, lbf=0.1079)), "STRUCTURALLY_INVALID")
        self.assertEqual(integrity_status(analysis(60.0, lbf=0.1078)), "OK")

    def test_pf_v2_gate_breach(self):
        self.assertEqual(integrity_status(analysis(60.0, pf=0.4999)), "STRUCTURALLY_INVALID")
        self.assertEqual(integrity_status(analysis(60.0, pf=0.50)), "OK")

    def test_disp_gate_breach(self):
        self.assertEqual(integrity_status(analysis(60.0, disp=20.1)), "STRUCTURALLY_INVALID")
        self.assertEqual(integrity_status(analysis(60.0, disp=20.0)), "OK")

    def test_missing_fields_invalid(self):
        self.assertEqual(integrity_status({"median_angle_deg": 60.0}), "STRUCTURALLY_INVALID")


class ScoreRunMath(unittest.TestCase):
    def test_exact_scores(self):
        self.assertEqual(score_run(analysis(50.0), 45.0)["score"], 5.0)
        self.assertEqual(score_run(analysis(40.0), 45.0)["score"], 5.0)
        self.assertEqual(score_run(analysis(45.0), 45.0)["score"], 0.0)
        self.assertEqual(score_run(analysis(132.36), 45.0)["score"], 87.36)

    def test_invalid_run_score_none(self):
        result = score_run(analysis(50.0, lbf=0.2), 45.0)
        self.assertIsNone(result["score"])
        self.assertEqual(result["status"], "STRUCTURALLY_INVALID")
        self.assertEqual(result["median_angle_deg"], 50.0)

    def test_floats_rounded_consistently(self):
        # |65.87 - 45.0| = 20.87 exactly at 2 decimals
        self.assertEqual(score_run(analysis(65.87), 45.0)["score"], 20.87)


class SessionAccounting(unittest.TestCase):
    def _report(self):
        return {
            "goal": {"target_angle_deg": 45.0},
            "budget": {"max_simulations": 5, "max_wall_minutes": 30.0,
                       "simulations_used": 5, "wall_seconds_used": 4.2},
            "actions_log": [
                {"action": "propose_candidate", "accepted": True},
                {"action": "request_run", "accepted": True},
                {"action": "propose_candidate", "accepted": False, "reason": "CANDIDATE_PARAM_NOT_IN_ALLOWLIST"},
                {"action": "propose_candidate", "accepted": True},
                {"action": "request_run", "accepted": True},
                {"action": "propose_candidate", "accepted": True},
                {"action": "request_run", "accepted": True},
            ],
            "runs": [
                {"run_id": "NL4-MOCK-R0001", "candidate_id": "CAND-0001",
                 "analysis": analysis(50.0)},
                {"run_id": "NL4-MOCK-R0002", "candidate_id": "CAND-0002",
                 "analysis": analysis(40.0)},
                {"run_id": "NL4-MOCK-R0003", "candidate_id": "CAND-0003",
                 "analysis": analysis(44.0, lbf=0.5)},
            ],
        }

    def test_honest_counts_and_best(self):
        summary = score_session(self._report())
        counts = summary["counts"]
        self.assertEqual(counts["proposals_total"], 4)
        self.assertEqual(counts["proposals_rejected"], 1)
        self.assertEqual(counts["runs_executed"], 3)
        self.assertEqual(counts["runs_structurally_invalid"], 1)
        self.assertEqual(counts["runs_scored"], 2)
        # best over valid runs only; ties broken by run_id
        self.assertEqual(summary["best"]["run_id"], "NL4-MOCK-R0001")
        self.assertEqual(summary["best"]["score"], 5.0)

    def test_no_valid_runs_best_is_none(self):
        report = self._report()
        for run in report["runs"]:
            run["analysis"] = analysis(50.0, pf=0.1)
        self.assertIsNone(score_session(report)["best"])


if __name__ == "__main__":
    unittest.main()
