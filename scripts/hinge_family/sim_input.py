"""Parser and preregistered-value checks for the author simulation input file.

The pinned ``pro_CPU.in`` uses a ``key = value`` line format (comments are
``#`` lines). The preregistered values come from E2-SETUP-R1 section 5
(OBSERVED facts of the pinned file recorded by NL0-001) and are machine-
confirmed on every run; deviations are errors, never warnings.
"""
from __future__ import annotations

PREREGISTERED = {
    "interaction_type": "DNA2",
    "salt_concentration": "0.5",
    "T": "300K",
    "steps": "2e7",
    "backend": "CPU",
    "backend_precision": "double",
}


class SimInputError(Exception):
    pass


def parse_sim_input(text: str) -> dict:
    values = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in line:
            raise SimInputError(f"sim input line without '=': {line!r}")
        key, _, value = line.partition("=")
        key = key.strip()
        if key in values:
            raise SimInputError(f"sim input has duplicate key {key!r}")
        values[key] = value.strip()
    return values


def check_preregistered(values: dict) -> dict:
    mismatches = []
    for key, expected in sorted(PREREGISTERED.items()):
        actual = values.get(key)
        if actual != expected:
            mismatches.append({"key": key, "expected": expected, "actual": actual})
    if mismatches:
        raise SimInputError(f"preregistered sim-input values mismatch: {mismatches!r}")
    return {
        "confirmed_keys": sorted(PREREGISTERED),
        "default_topology": values.get("topology"),
        "default_conf_file": values.get("conf_file"),
    }
