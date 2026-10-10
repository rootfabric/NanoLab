"""Byte-deterministic serialization and float rounding conventions.

Every published report of the hinge-family toolchain must be reproducible
byte-for-byte from the same inputs on any platform: fixed key order (sorted),
no locale dependence, no wall-clock data inside the artifact.
"""
from __future__ import annotations

import json

FLOAT_DIGITS = 9


def round_floats(value):
    """Recursively round floats to FLOAT_DIGITS digits for stable reports."""
    if isinstance(value, float):
        return round(value, FLOAT_DIGITS)
    if isinstance(value, dict):
        return {k: round_floats(v) for k, v in value.items()}
    if isinstance(value, list):
        return [round_floats(v) for v in value]
    return value


def canonical_json(obj) -> str:
    """Byte-deterministic JSON serialization used for every published report."""
    return json.dumps(round_floats(obj), sort_keys=True, indent=2, ensure_ascii=False) + "\n"
