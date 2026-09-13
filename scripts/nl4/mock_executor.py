"""Deterministic mock executor for NL4 infrastructure (WO-NL4-001).

Implements the same ``ExecutorAdapter`` interface the real engine adapter
will implement in NL4-002, but produces pseudo-observables WITHOUT any
physics: every number is a pure function of the canonical candidate JSON
(sha256-derived), so two sessions with the same candidate sequence are
byte-identical. Run IDs use the real format with the ``NL4-MOCK-`` prefix
so evidence tooling cannot mistake them for engine runs.

stdlib-only; never touches oxDNA, the network or an LLM.
"""
from __future__ import annotations

import hashlib

try:
    from .controller import ExecutorAdapter
except ImportError:  # direct module import during early bring-up
    ExecutorAdapter = object

try:
    from e2.canonical import canonical_json
except ImportError:  # pragma: no cover - path setup handled by caller
    from ..e2.canonical import canonical_json


def _digest(candidate: dict) -> str:
    return hashlib.sha256(
        canonical_json(
            {
                "variant": candidate["variant"],
                "steps": candidate["steps"],
                "seed": candidate["seed"],
            }
        ).encode("utf-8")
    ).hexdigest()


def _slice(digest: str, start: int, width: int) -> int:
    return int(digest[start : start + width], 16)


def mock_observables(candidate: dict) -> dict:
    """Deterministic pseudo-observables from fixture parameters (no physics).

    Ranges are chosen so the frozen E2_PROTO_R1 §4 gates split the space:
    most candidates are valid, some breach each gate — scoring and honest
    accounting are therefore exercised on real mock data.
    """
    digest = _digest(candidate)
    return {
        # [20.00, 160.00] deg, 2 decimals
        "median_angle_deg": round(20.0 + _slice(digest, 0, 8) % 14001 / 100.0, 2),
        # [0.0000, 0.1100): breaches lbf <= 0.1078 near the top of the range
        "long_bond_fraction": _slice(digest, 8, 4) % 1101 / 10000.0,
        # [0.30, 1.00]: breaches pf_v2 >= 0.50 below the midpoint
        "pairs_fraction_v2": round(0.30 + _slice(digest, 12, 4) % 71 / 100.0, 2),
        # [0.0, 30.0): breaches disp <= 20.0 on the upper third
        "displacement_max": _slice(digest, 16, 4) % 301 / 10.0,
    }


def mock_wall_seconds(candidate: dict) -> float:
    """Deterministic pseudo wall time (mock executor is instant in reality)."""
    digest = _digest(candidate)
    return round(0.5 + _slice(digest, 20, 4) % 500 / 1000.0, 3)


class MockExecutor(ExecutorAdapter):
    """ExecutorAdapter implementation with deterministic pseudo-results."""

    executor_id = "mock-executor-r1"
    backend = "MOCK (no physics; pseudo-observables from fixture parameters)"

    def estimate_wall_seconds(self, candidate: dict) -> float:
        return mock_wall_seconds(candidate)

    def run(self, candidate: dict, run_seq: int) -> dict:
        run_id = "NL4-MOCK-R%04d" % run_seq
        observables = mock_observables(candidate)
        wall = mock_wall_seconds(candidate)
        return {
            "run_id": run_id,
            "executor": self.executor_id,
            "backend": self.backend,
            "candidate": dict(candidate),
            "input_digest_sha256": _digest(candidate),
            "wall_seconds": wall,
            "analysis": {
                "median_angle_deg": observables["median_angle_deg"],
                "long_bond_fraction": round(observables["long_bond_fraction"], 4),
                "pairs_fraction_v2": observables["pairs_fraction_v2"],
                "displacement_max": round(observables["displacement_max"], 1),
            },
        }
