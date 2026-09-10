#!/usr/bin/env python3
"""E0-R1 geometry_check.py -- mechanical geometric analysis of SYNTHETIC fixtures.

Instrument of campaign E0-R1 (protocol E0-PROTO-R1, WO NL2-001).
Frozen BEFORE any run; changes invalidate the campaign subject (exact-head rule).

Purpose (E0 doc "geometric tests"): compute distances/angles on small artificial
geometries with analytically known values; degenerate input (zero-length arm)
must be classified ANGLE_UNDEFINED and must not yield a numeric angle.

Unit conventions (preregistered):
  - coordinates: plain floats, no units attached (SYNTHETIC geometry);
  - distances: same abstract units as coordinates;
  - angles: degrees in [0, 180], computed via atan2(|a x b|, a . b).

The tool only COMPUTES; pass/fail decisions live in protocol.json (frozen
expectations) and are applied by tools/e0_runner.py.

Usage: python geometry_check.py <fixture.json>
Exit codes: 0 = computed (see stdout JSON), 2 = usage/parse error.
"""
from __future__ import annotations

import json
import math
import sys
from typing import Any


def vec_sub(a: list[float], b: list[float]) -> list[float]:
    return [a[i] - b[i] for i in range(3)]


def dot(a: list[float], b: list[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def norm(a: list[float]) -> float:
    return math.sqrt(dot(a, a))


def compute_distance(vertices: dict[str, Any], query: dict[str, Any]) -> dict[str, Any]:
    p = vertices[query["points"][0]]
    q = vertices[query["points"][1]]
    value = norm(vec_sub(p, q))
    return {"query_id": query["id"], "type": "distance", "value": value, "verdict": "DEFINED"}


def compute_angle(vertices: dict[str, Any], query: dict[str, Any]) -> dict[str, Any]:
    vertex = vertices[query["vertex"]]
    arm_a = vec_sub(vertices[query["arms"][0]], vertex)
    arm_b = vec_sub(vertices[query["arms"][1]], vertex)
    len_a, len_b = norm(arm_a), norm(arm_b)
    if len_a == 0.0 or len_b == 0.0:
        return {
            "query_id": query["id"],
            "type": "angle_deg",
            "value": None,
            "verdict": "ANGLE_UNDEFINED",
            "zero_arm_lengths": [len_a, len_b],
        }
    cos_angle = dot(arm_a, arm_b) / (len_a * len_b)
    # clamp against float round-off beyond [-1, 1]
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle_deg = math.degrees(math.atan2(norm(cross(arm_a, arm_b)), cos_angle))
    return {"query_id": query["id"], "type": "angle_deg", "value": angle_deg, "verdict": "DEFINED"}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: geometry_check.py <fixture.json>", file=sys.stderr)
        return 2
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        fixture = json.load(handle)
    if not fixture.get("synthetic") or fixture.get("kind") != "SYNTHETIC_TEST_GEOMETRY":
        print("fixture is not marked as SYNTHETIC_TEST_GEOMETRY", file=sys.stderr)
        return 2
    vertices = fixture["vertices"]
    results = []
    for query in fixture["queries"]:
        if query["type"] == "distance":
            results.append(compute_distance(vertices, query))
        elif query["type"] == "angle_deg":
            results.append(compute_angle(vertices, query))
        else:
            print(f"unknown query type: {query['type']}", file=sys.stderr)
            return 2
    print(json.dumps({"fixture": sys.argv[1], "synthetic": True, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
