"""Scoring for NL4 bounded-agent sessions (WO-NL4-001 item 5).

score = |median_angle - target_angle| for runs whose integrity gates pass.

The integrity gates are FROZEN in ``docs/research/E2_PROTO_R1.md`` §4
(Director decision №2) and are hard-coded here on purpose: no action, goal
field or agent proposal can modify them (allowlist.json forbids gate
tampering). Rejected/invalid runs are accounted for honestly: they stay in
the report with ``score = None`` and their own status, never silently
dropped and never averaged in.

stdlib-only; no physics, no engine, no network.
"""
from __future__ import annotations

# Frozen E2_PROTO_R1 §4 frame-validity gates (STRUCTURALLY_INVALID on breach)
LONG_BOND_FRACTION_MAX = 0.1078
PAIRS_FRACTION_V2_MIN = 0.50
DISPLACEMENT_MAX = 20.0

STATUS_OK = "OK"
STATUS_STRUCTURALLY_INVALID = "STRUCTURALLY_INVALID"
STATUS_REJECTED = "REJECTED"
STATUS_NOT_RUN = "NOT_RUN"


def round2(value: float) -> float:
    return round(value + 0.0, 2)


def integrity_status(analysis: dict) -> str:
    """E2_PROTO_R1 §4 gate evaluation on one analysis record."""
    lbf = analysis.get("long_bond_fraction")
    pf = analysis.get("pairs_fraction_v2")
    disp = analysis.get("displacement_max")
    if (
        isinstance(lbf, (int, float))
        and isinstance(pf, (int, float))
        and isinstance(disp, (int, float))
    ):
        if (
            lbf > LONG_BOND_FRACTION_MAX
            or pf < PAIRS_FRACTION_V2_MIN
            or disp > DISPLACEMENT_MAX
        ):
            return STATUS_STRUCTURALLY_INVALID
        return STATUS_OK
    return STATUS_STRUCTURALLY_INVALID


def score_run(analysis: dict, target_angle: float) -> dict:
    """Score one executed run: |median_angle - target| under §4 gates."""
    status = integrity_status(analysis)
    median = analysis.get("median_angle_deg")
    if status != STATUS_OK or not isinstance(median, (int, float)):
        return {
            "status": status,
            "median_angle_deg": median if isinstance(median, (int, float)) else None,
            "score": None,
        }
    return {
        "status": status,
        "median_angle_deg": median,
        # 9-digit rounding keeps canonical-JSON reports byte-stable against
        # binary float noise (same convention as e2.canonical FLOAT_DIGITS)
        "score": round(abs(median - target_angle), 9),
    }


def score_session(report: dict) -> dict:
    """Summarise a controller report: best valid run + honest accounting.

    ``report`` is the canonical controller session report (see
    ``controller.Controller.session_report``). Executed runs are scored;
    rejected proposals and invalid runs are counted, not hidden.
    """
    target = report["goal"]["target_angle_deg"]
    scored = []
    counts = {
        "proposals_total": 0,
        "proposals_rejected": 0,
        "runs_executed": 0,
        "runs_structurally_invalid": 0,
        "runs_scored": 0,
    }
    for entry in report["actions_log"]:
        if entry["action"] == "propose_candidate":
            counts["proposals_total"] += 1
            if not entry["accepted"]:
                counts["proposals_rejected"] += 1
    best = None
    for run in report["runs"]:
        counts["runs_executed"] += 1
        result = score_run(run["analysis"], target)
        if result["status"] == STATUS_STRUCTURALLY_INVALID:
            counts["runs_structurally_invalid"] += 1
        else:
            counts["runs_scored"] += 1
            scored.append((result["score"], run["run_id"], run["candidate_id"]))
    if scored:
        scored.sort(key=lambda item: (item[0], item[1]))
        best = {
            "run_id": scored[0][1],
            "candidate_id": scored[0][2],
            "score": scored[0][0],
        }
    return {
        "target_angle_deg": target,
        "counts": counts,
        "best": best,
        "budget": report["budget"],
    }
