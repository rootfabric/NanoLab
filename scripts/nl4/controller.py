"""Experiment controller for NL4 bounded-agent sessions (WO-NL4-001 item 2).

Deterministic loop: goal-JSON -> agent action -> allowlist validation ->
budget check -> ExecutorAdapter run -> analysis record -> evidence ->
score -> next. The controller is the ONLY component allowed to talk to an
executor; agents propose, they never execute.

Fail-closed posture: an out-of-allowlist action or candidate is rejected and
logged, the execution does NOT happen; budget exhaustion stops the loop
without ever exceeding the cap. Evidence records use the canonical JSON
conventions of the frozen NL3 toolchain (``e2.canonical``) and run IDs of
the real format (``NL4-MOCK-*`` for the mock executor).

stdlib-only; no physics, no engine, no LLM, no network.
"""
from __future__ import annotations

import json
from pathlib import Path

try:
    from e2.canonical import canonical_json
except ImportError:  # pragma: no cover - path setup handled by caller
    from ..e2.canonical import canonical_json

ALLOWLIST_FILENAME = Path(__file__).with_name("allowlist.json")

# Rejection reason codes (stable, part of the evidence contract)
ACTION_NOT_IN_ALLOWLIST = "ACTION_NOT_IN_ALLOWLIST"
MALFORMED_ACTION = "MALFORMED_ACTION"
FORBIDDEN_CANDIDATE_FIELD = "FORBIDDEN_CANDIDATE_FIELD"
UNKNOWN_CANDIDATE_FIELD = "UNKNOWN_CANDIDATE_FIELD"
CANDIDATE_PARAM_NOT_IN_ALLOWLIST = "CANDIDATE_PARAM_NOT_IN_ALLOWLIST"
CANDIDATE_MISSING_REQUIRED_FIELD = "CANDIDATE_MISSING_REQUIRED_FIELD"
UNKNOWN_CANDIDATE = "UNKNOWN_CANDIDATE"
CANDIDATE_ALREADY_RUN = "CANDIDATE_ALREADY_RUN"
BUDGET_EXHAUSTED_SIMULATIONS = "BUDGET_EXHAUSTED_SIMULATIONS"
BUDGET_EXHAUSTED_WALL = "BUDGET_EXHAUSTED_WALL"

ALLOWED_ACTIONS = ("propose_candidate", "request_run", "read_analysis", "stop")


class ControllerError(Exception):
    pass


def load_allowlist(path: Path | None = None) -> dict:
    with (path or ALLOWLIST_FILENAME).open("r", encoding="utf-8") as handle:
        allowlist = json.load(handle)
    if allowlist.get("frozen") is not True:
        raise ControllerError("allowlist must carry frozen: true")
    return allowlist


# ------------------------------------------------------------- goal contract
def parse_goal(goal_json: dict, allowlist: dict) -> dict:
    """Validate a goal-JSON against the frozen allowlist budget contract."""
    if not isinstance(goal_json, dict):
        raise ControllerError("goal must be a JSON object")
    target = goal_json.get("target_angle_deg")
    if not isinstance(target, (int, float)) or isinstance(target, bool):
        raise ControllerError("goal.target_angle_deg must be a number")
    budget_spec = allowlist["budgets"]
    max_sims = goal_json.get("max_simulations")
    if not isinstance(max_sims, int) or isinstance(max_sims, bool):
        raise ControllerError("goal.max_simulations must be an integer")
    if max_sims < budget_spec["max_simulations"]["min"]:
        raise ControllerError("goal.max_simulations below allowlist minimum")
    max_wall = goal_json.get("max_wall_minutes")
    if not isinstance(max_wall, (int, float)) or isinstance(max_wall, bool):
        raise ControllerError("goal.max_wall_minutes must be a number")
    if max_wall < budget_spec["max_wall_minutes"]["min"]:
        raise ControllerError("goal.max_wall_minutes below allowlist minimum")
    gate = goal_json.get("integrity_gate", "E2_PROTO_R1_S4_FROZEN")
    if gate != "E2_PROTO_R1_S4_FROZEN":
        raise ControllerError(
            "goal.integrity_gate is frozen to E2_PROTO_R1_S4_FROZEN; "
            "custom gates are not allowed (WO-NL4-001)"
        )
    return {
        "target_angle_deg": float(target),
        "max_simulations": int(max_sims),
        "max_wall_minutes": float(max_wall),
        "integrity_gate": gate,
    }


# ------------------------------------------------- candidate validation
def normalize_candidate(candidate, allowlist: dict):
    """Validate one candidate against the frozen allowlist.

    Returns ``(candidate, None)`` on success (with allowlist defaults
    applied) or ``(None, reason_code)`` on rejection.
    """
    spec = allowlist["candidate_params"]
    if not isinstance(candidate, dict):
        return None, MALFORMED_ACTION
    forbidden = set(allowlist["forbidden"]["forbidden_candidate_fields"])
    known = set(spec)
    normalized = {}
    for key in sorted(candidate):
        if key in forbidden:
            return None, FORBIDDEN_CANDIDATE_FIELD
        if key not in known:
            return None, UNKNOWN_CANDIDATE_FIELD
    variant = candidate.get("variant")
    if variant is None:
        return None, CANDIDATE_MISSING_REQUIRED_FIELD
    if variant not in spec["variant"]["values"]:
        return None, CANDIDATE_PARAM_NOT_IN_ALLOWLIST
    normalized["variant"] = variant
    steps = candidate.get("steps", spec["steps"]["default"])
    if steps not in spec["steps"]["values"]:
        return None, CANDIDATE_PARAM_NOT_IN_ALLOWLIST
    normalized["steps"] = steps
    seed = candidate.get("seed", spec["seed"]["default"])
    if seed not in spec["seed"]["values"]:
        return None, CANDIDATE_PARAM_NOT_IN_ALLOWLIST
    normalized["seed"] = seed
    return normalized, None


# ------------------------------------------------------------ executor API
class ExecutorAdapter:
    """Interface between the controller and a run backend (WO-NL4-001 item 2).

    The real engine adapter (NL4-002) implements the same two methods; the
    controller never imports an engine directly.
    """

    executor_id = "executor-adapter"
    backend = "ABSTRACT"

    def estimate_wall_seconds(self, candidate: dict):
        """Deterministic pre-run wall estimate, or None when unknown."""
        return None

    def run(self, candidate: dict, run_seq: int) -> dict:
        raise NotImplementedError


class Controller:
    """Deterministic goal -> candidates -> runs -> analysis -> score loop."""

    controller_id = "nl4-controller-r1"

    def __init__(self, goal_json: dict, executor: ExecutorAdapter, allowlist: dict | None = None):
        self.allowlist = allowlist if allowlist is not None else load_allowlist()
        self.goal = parse_goal(goal_json, self.allowlist)
        self.executor = executor
        self.actions_log: list[dict] = []
        self.candidates: dict[str, dict] = {}
        self.runs: list[dict] = []
        self._candidate_seq = 0
        self._run_seq = 0
        self.wall_seconds_used = 0.0
        self.stop_reason = None

    # ------------------------------------------------------------ helpers
    def _log(self, seq, action, accepted, reason=None, **extra):
        entry = {
            "seq": seq,
            "action": action,
            "accepted": accepted,
            "reason": reason,
        }
        entry.update(extra)
        self.actions_log.append(entry)

    def simulations_remaining(self) -> int:
        return self.goal["max_simulations"] - len(self.runs)

    def budget_exhausted(self) -> bool:
        return (
            self.simulations_remaining() <= 0
            or self.wall_seconds_used >= self.goal["max_wall_minutes"] * 60.0
        )

    # ------------------------------------------------------------- the loop
    def run(self, agent) -> dict:
        observations: list[dict] = []
        # hard safety cap: no action storm can spin the loop forever
        action_cap = 32 + 16 * self.goal["max_simulations"]
        stop_reason = "ACTION_LOOP_CAP"
        while True:
            if self.budget_exhausted():
                stop_reason = (
                    "BUDGET_EXHAUSTED_SIMULATIONS"
                    if self.simulations_remaining() <= 0
                    else "BUDGET_EXHAUSTED_WALL"
                )
                break
            if len(self.actions_log) >= action_cap:
                break
            action = agent.next_action(observations)
            if action is None:
                stop_reason = "AGENT_STOPPED"
                break
            if not isinstance(action, dict) or "action" not in action:
                self._log(len(self.actions_log) + 1, str(action), False, MALFORMED_ACTION)
                continue
            name = action["action"]
            if name not in ALLOWED_ACTIONS:
                self._log(len(self.actions_log) + 1, name, False, ACTION_NOT_IN_ALLOWLIST)
                continue
            if name == "stop":
                self._log(len(self.actions_log) + 1, "stop", True)
                stop_reason = "AGENT_STOPPED"
                break
            if name == "read_analysis":
                self._log(len(self.actions_log) + 1, "read_analysis", True, reads=len(observations))
                continue
            if name == "propose_candidate":
                self._handle_propose(action)
                continue
            if name == "request_run":
                done = self._handle_request_run(action, observations)
                if done:
                    stop_reason = done
                    break
                continue
        self.stop_reason = stop_reason
        return self.session_report(agent)

    def _handle_propose(self, action: dict) -> None:
        seq = len(self.actions_log) + 1
        candidate, reason = normalize_candidate(action.get("candidate"), self.allowlist)
        if candidate is None:
            self._log(seq, "propose_candidate", False, reason)
            return
        self._candidate_seq += 1
        candidate_id = "CAND-%04d" % self._candidate_seq
        self.candidates[candidate_id] = candidate
        self._log(seq, "propose_candidate", True, None, candidate_id=candidate_id, candidate=dict(candidate))

    def _handle_request_run(self, action: dict, observations: list):
        seq = len(self.actions_log) + 1
        candidate_id = action.get("candidate_id")
        wanted = None
        if candidate_id is None and "candidate" in action:
            # self-describing reference: resolve the pending proposal with
            # exactly these parameters (first proposed, not yet executed)
            wanted, reason = normalize_candidate(action.get("candidate"), self.allowlist)
            if wanted is None:
                self._log(seq, "request_run", False, reason)
                return None
            for cid, cand in sorted(self.candidates.items()):
                if cand == wanted:
                    candidate_id = cid
                    break
        candidate = self.candidates.get(candidate_id)
        if candidate is None:
            # an exact match that was already executed is a duplicate request
            if wanted is not None and any(
                cand == wanted for cand in self.candidates.values()
            ):
                self._log(seq, "request_run", False, CANDIDATE_ALREADY_RUN)
                return None
            self._log(seq, "request_run", False, UNKNOWN_CANDIDATE)
            return None
        if any(run["candidate_id"] == candidate_id for run in self.runs):
            self._log(seq, "request_run", False, CANDIDATE_ALREADY_RUN)
            return None
        if self.simulations_remaining() <= 0:
            self._log(seq, "request_run", False, BUDGET_EXHAUSTED_SIMULATIONS)
            return BUDGET_EXHAUSTED_SIMULATIONS
        estimate = self.executor.estimate_wall_seconds(candidate)
        limit_seconds = self.goal["max_wall_minutes"] * 60.0
        if estimate is not None and self.wall_seconds_used + estimate > limit_seconds:
            self._log(seq, "request_run", False, BUDGET_EXHAUSTED_WALL)
            return BUDGET_EXHAUSTED_WALL
        self._run_seq += 1
        result = self.executor.run(candidate, self._run_seq)
        self.wall_seconds_used = round(self.wall_seconds_used + result["wall_seconds"], 6)
        run_record = {
            "run_id": result["run_id"],
            "candidate_id": candidate_id,
            "candidate": dict(candidate),
            "input_digest_sha256": result["input_digest_sha256"],
            "wall_seconds": result["wall_seconds"],
            "analysis": result["analysis"],
            "executor": result["executor"],
            "backend": result["backend"],
        }
        self.runs.append(run_record)
        observations.append(
            {
                "run_id": result["run_id"],
                "candidate_id": candidate_id,
                "candidate": dict(candidate),
                "analysis": result["analysis"],
            }
        )
        self._log(
            seq,
            "request_run",
            True,
            None,
            candidate_id=candidate_id,
            run_id=result["run_id"],
        )
        return None

    # -------------------------------------------------------------- report
    def session_report(self, agent) -> dict:
        report = {
            "schema_version": 1,
            "kind": "nl4_session_report",
            "controller_id": self.controller_id,
            "allowlist_revision": self.allowlist["revision"],
            "agent": getattr(agent, "name", type(agent).__name__),
            "executor": {
                "executor_id": self.executor.executor_id,
                "backend": self.executor.backend,
            },
            "goal": dict(self.goal),
            "budget": {
                "max_simulations": self.goal["max_simulations"],
                "max_wall_minutes": self.goal["max_wall_minutes"],
                "simulations_used": len(self.runs),
                "wall_seconds_used": round(self.wall_seconds_used, 6),
            },
            "stop_reason": self.stop_reason,
            "actions_log": self.actions_log,
            "candidates": {cid: dict(c) for cid, c in sorted(self.candidates.items())},
            "runs": self.runs,
        }
        rejected = getattr(agent, "rejected_actions", None)
        if rejected is not None:
            report["bounded_agent_rejected"] = rejected
        return report

    def render_report(self, agent) -> str:
        return canonical_json(self.session_report(agent))
