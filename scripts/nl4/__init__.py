"""NanoLab NL4 bounded-agent toolkit (WO-NL4-001, EX-NL4-001-R1).

Frozen, stdlib-only infrastructure for the NL4 AI loop, prepared BEFORE
the E3 campaign (which is a separate Work Order, NL4-002):

* ``allowlist.json``   -- frozen action/candidate/budget contract
* ``controller``       -- deterministic goal -> candidates -> runs -> score loop
* ``mock_executor``    -- ExecutorAdapter with deterministic pseudo-results
                          (run IDs NL4-MOCK-*, no physics)
* ``agents``           -- baselines (random/grid, no AI) + bounded wrapper
* ``scoring``          -- |median_angle - target| under frozen E2_PROTO_R1 §4 gates

No LLM keys, no network, no oxDNA runs: campaign NOT_EVALUATED here.
Canonical JSON and gate constants come from the frozen NL3 toolchain by
import only (scripts/e2, scripts/hinge_family are not modified).
"""
from .controller import Controller, ExecutorAdapter, load_allowlist, parse_goal
from .mock_executor import MockExecutor, mock_observables
from .scoring import score_run, score_session

__all__ = [
    "Controller",
    "ExecutorAdapter",
    "MockExecutor",
    "load_allowlist",
    "parse_goal",
    "mock_observables",
    "score_run",
    "score_session",
]
