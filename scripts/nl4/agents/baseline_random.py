"""Random baseline agent (WO-NL4-001 item 3): NO AI, deterministic RNG.

The RNG is seeded from the goal-JSON itself (sha256 of its canonical form),
so the same goal always yields the same proposal trajectory on any machine.
Budget accounting is the controller's, identical for all agents.

The agent emits ``propose_candidate`` followed by ``request_run`` carrying
the same candidate value (the controller resolves it to the pending
proposal), so the action stream is fully self-describing JSON.
"""
from __future__ import annotations

import hashlib
import random

try:
    from e2.canonical import canonical_json
except ImportError:  # pragma: no cover
    from ...e2.canonical import canonical_json


def random_seed_from_goal(goal: dict) -> int:
    payload = {
        "target_angle_deg": goal["target_angle_deg"],
        "max_simulations": goal["max_simulations"],
        "max_wall_minutes": goal["max_wall_minutes"],
    }
    if "integrity_gate" in goal:
        payload["integrity_gate"] = goal["integrity_gate"]
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


class RandomBaseline:
    """Proposes uniformly random allowlisted candidates until stopped.

    Proposes exactly ``goal.max_simulations`` candidates and then stops
    voluntarily; the controller's budget enforcement stays the hard cap.
    """

    name = "baseline-random-r1"

    def __init__(self, goal: dict, allowlist: dict):
        self._rng = random.Random(random_seed_from_goal(goal))
        spec = allowlist["candidate_params"]
        space = [
            {"variant": variant, "steps": steps, "seed": seed}
            for variant in spec["variant"]["values"]
            for steps in spec["steps"]["values"]
            for seed in spec["seed"]["values"]
        ]
        # draw WITHOUT replacement: duplicate candidates would only collect
        # CANDIDATE_ALREADY_RUN rejections and waste the exploration budget
        count = min(goal["max_simulations"], len(space))
        self._draws = self._rng.sample(space, count)
        self._index = 0
        self._pending = None

    def next_action(self, observations) -> dict | None:
        if self._pending is not None:
            candidate = self._pending
            self._pending = None
            return {"action": "request_run", "candidate": dict(candidate)}
        if self._index >= len(self._draws):
            return {"action": "stop"}
        candidate = self._draws[self._index]
        self._index += 1
        self._pending = candidate
        return {"action": "propose_candidate", "candidate": dict(candidate)}
