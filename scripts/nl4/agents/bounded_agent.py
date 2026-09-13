"""Bounded agent wrapper for external proposals (WO-NL4-001 item 4).

The wrapper receives RAW action proposals from the outside world (a JSON
list — file or STDIN in the CLI; a scripted brain in tests), validates each
against the frozen allowlist BEFORE anything reaches the controller, keeps
its own budget mirror, and records every rejection in a durable
``rejected_actions`` log that enters the session evidence.

An out-of-allowlist proposal is rejected here, logged, and NEVER forwarded:
the execution does not happen. The controller re-validates everything
(defense in depth), so a bug in this wrapper still cannot let an
out-of-allowlist action execute.

The real LLM brain plugs in as any callable/iterable producing raw action
dicts (E3, NL4-002); ``ScriptedBrain`` is the deterministic mock shipped
for tests and demos.
"""
from __future__ import annotations

try:
    from ..controller import (
        ALLOWED_ACTIONS,
        BUDGET_EXHAUSTED_SIMULATIONS,
        normalize_candidate,
    )
except ImportError:  # pragma: no cover
    from nl4.controller import (
        ALLOWED_ACTIONS,
        BUDGET_EXHAUSTED_SIMULATIONS,
        normalize_candidate,
    )


class ScriptedBrain:
    """Deterministic scripted brain: replays a fixed list of raw proposals."""

    def __init__(self, proposals: list):
        self._proposals = list(proposals)
        self._index = 0

    def next_proposal(self):
        if self._index >= len(self._proposals):
            return None
        item = self._proposals[self._index]
        self._index += 1
        return item

    # controller Agent-protocol alias (raw replay, no wrapper validation)
    def next_action(self, observations):
        return self.next_proposal()


class BoundedAgent:
    """Allowlist-validating wrapper around an external (LLM) brain."""

    name = "bounded-agent-r1"

    def __init__(self, brain, goal: dict, allowlist: dict):
        self._brain = brain
        self._goal = goal
        self._allowlist = allowlist
        self._runs_forwarded = 0
        self._forwarded_candidate_ids: set = set()
        self._pending_forwarded = None
        self.rejected_actions: list[dict] = []

    def _reject(self, raw, reason: str) -> None:
        self.rejected_actions.append({"action": raw, "reason": reason})

    def _budget_left(self) -> bool:
        return self._runs_forwarded < self._goal["max_simulations"]

    def next_action(self, observations) -> dict | None:
        while True:
            raw = self._brain.next_proposal()
            if raw is None:
                return {"action": "stop"}
            if not isinstance(raw, dict) or "action" not in raw:
                self._reject(raw, "MALFORMED_ACTION")
                continue
            name = raw["action"]
            if name not in ALLOWED_ACTIONS:
                self._reject(raw, "ACTION_NOT_IN_ALLOWLIST")
                continue
            if name == "propose_candidate":
                candidate, reason = normalize_candidate(raw.get("candidate"), self._allowlist)
                if candidate is None:
                    self._reject(raw, reason)
                    continue
                self._pending_forwarded = candidate
                return {"action": "propose_candidate", "candidate": dict(candidate)}
            if name == "request_run":
                if not self._budget_left():
                    self._reject(raw, BUDGET_EXHAUSTED_SIMULATIONS)
                    continue
                if "candidate" in raw:
                    candidate, reason = normalize_candidate(raw.get("candidate"), self._allowlist)
                    if candidate is None:
                        self._reject(raw, reason)
                        continue
                elif "candidate_id" in raw:
                    candidate = self._pending_forwarded
                    if candidate is None:
                        self._reject(raw, "UNKNOWN_CANDIDATE")
                        continue
                else:
                    candidate = self._pending_forwarded
                    if candidate is None:
                        self._reject(raw, "UNKNOWN_CANDIDATE")
                        continue
                self._runs_forwarded += 1
                return {"action": "request_run", "candidate": dict(candidate)}
            # read_analysis / stop pass through unchanged (read-only/terminal)
            return dict(raw)
