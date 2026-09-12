"""Canonical serialization for all e2 reports.

Single source of truth for byte-deterministic JSON lives in the frozen
NL3-001 toolchain: ``hinge_family.canonical``.
"""
from __future__ import annotations

from hinge_family.canonical import FLOAT_DIGITS, canonical_json, round_floats

__all__ = ["FLOAT_DIGITS", "canonical_json", "round_floats"]
