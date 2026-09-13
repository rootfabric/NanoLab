"""Agents for NL4 sessions: baselines (random/grid) and the bounded wrapper.

All agents share one protocol consumed by ``nl4.controller.Controller``:

    agent.name                      -> str (evidence identity)
    agent.next_action(observations) -> action dict | None (None = stop)

Observations are the analysis records published so far (read-only copies).
Baselines ignore them by design (no adaptive behaviour); the bounded agent
brain may read them. Budget accounting is identical for every agent and
lives in the controller, never in the agent.
"""
from .baseline_grid import GridBaseline
from .baseline_random import RandomBaseline
from .bounded_agent import BoundedAgent, ScriptedBrain

__all__ = ["GridBaseline", "RandomBaseline", "BoundedAgent", "ScriptedBrain"]
