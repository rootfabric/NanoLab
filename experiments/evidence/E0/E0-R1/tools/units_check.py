#!/usr/bin/env python3
"""E0-R1 units_check.py -- mechanical units-conversion table check (pinned engine fact).

Instrument of campaign E0-R1 (protocol E0-PROTO-R1, WO NL2-001).
Frozen BEFORE any run; changes invalidate the campaign subject (exact-head rule).

Reference table (single entry, provenance -- NOT re-derived here):
  T = 20C  ->  T_oxDNA = 0.097717 (internal units of pinned oxDNA
  00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591)
  Source of the value: docs/research/ENGINE_ENVIRONMENT_R1.md section 6,
  engine log line "Converting temperature ... (0.097717)" (OBSERVED, NL1-001
  ACCEPTED). This tool treats the recorded pinned-engine fact as the only
  reference; it does NOT re-implement or re-fit any conversion formula.

Acceptance band (preregistered BEFORE any run, derived from engine print
precision, not from results): the engine prints 6 significant digits, so the
half-ULP of the last printed digit is 0.5e-6:
  ACCEPTED  iff  |claimed_T_oxDNA - 0.097717| <= 5e-7
  REJECTED  otherwise
Values outside the table for input_T are REJECTED_INPUT_UNKNOWN (wrong-unit
probes; e.g. a Kelvin value must not silently match a Celsius row).

Usage: python units_check.py <fixture.json> [<fixture.json> ...]
Prints one JSON verdict per fixture; exit codes: 0 = all fixtures evaluated,
2 = usage/parse error. Pass/fail of the experiment case is decided by
tools/e0_runner.py against frozen protocol expectations.
"""
from __future__ import annotations

import json
import sys

REFERENCE_TABLE = {
    # input_T (pinned-engine input syntax) -> T in oxDNA internal units
    "20C": 0.097717,
}
ACCEPT_TOLERANCE = 5e-7  # half-ULP of the 6th printed significant digit (preregistered)


def evaluate(fixture_path: str) -> dict:
    with open(fixture_path, "r", encoding="utf-8") as handle:
        fixture = json.load(handle)
    input_t = fixture["input_T"]
    claimed = fixture["claimed_T_oxDNA"]
    if input_t not in REFERENCE_TABLE:
        verdict = "REJECTED_INPUT_UNKNOWN"
        delta = None
    else:
        reference = REFERENCE_TABLE[input_t]
        delta = claimed - reference
        verdict = "ACCEPTED" if abs(delta) <= ACCEPT_TOLERANCE else "REJECTED"
    return {
        "fixture": fixture_path,
        "input_T": input_t,
        "claimed_T_oxDNA": claimed,
        "reference_T_oxDNA": REFERENCE_TABLE.get(input_t),
        "delta": delta,
        "tolerance": ACCEPT_TOLERANCE,
        "verdict": verdict,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: units_check.py <fixture.json> [...]", file=sys.stderr)
        return 2
    verdicts = []
    for path in sys.argv[1:]:
        verdicts.append(evaluate(path))
    print(json.dumps({"verdicts": verdicts, "reference_provenance": "docs/research/ENGINE_ENVIRONMENT_R1.md section 6 (oxDNA 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591, log OBSERVED)"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
