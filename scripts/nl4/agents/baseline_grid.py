"""Grid baseline agent (WO-NL4-001 item 3): exhaustive allowlist sweep.

Enumerates the complete candidate space of the frozen allowlist in canonical
order (variant x steps x seed) and requests one run per candidate until the
space or the budget is exhausted. Deterministic by construction; budget
accounting is the controller's, identical for all agents.
"""
from __future__ import annotations

import itertools


class GridBaseline:
    name = "baseline-grid-r1"

    def __init__(self, goal: dict, allowlist: dict):
        spec = allowlist["candidate_params"]
        self._space = [
            {"variant": variant, "steps": steps, "seed": seed}
            for variant, steps, seed in itertools.product(
                spec["variant"]["values"],
                spec["steps"]["values"],
                spec["seed"]["values"],
            )
        ]
        self._index = 0
        self._pending = None

    def next_action(self, observations) -> dict | None:
        if self._pending is not None:
            candidate = self._pending
            self._pending = None
            return {"action": "request_run", "candidate": dict(candidate)}
        if self._index >= len(self._space):
            return {"action": "stop"}
        candidate = self._space[self._index]
        self._index += 1
        self._pending = candidate
        return {"action": "propose_candidate", "candidate": dict(candidate)}
