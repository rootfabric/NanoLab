"""Inventory and semantics classification of artificial restraints.

Answers (bounded, honest): which artificial restraints does an upstream
setup declare, are they part of the physical model or initialization-only,
and must they stay on during a production run?

Sources:
* an oxDNA production input (key-level semantics from the frozen table below);
* optional author init/relax scripts scanned line-by-line for restraint
  keywords (observations only, no interpretation beyond the keywords).

Frozen semantics table v1 (E2_OBSERVABLES_R1-adjacent control facts):
``external_forces`` = true means an external forces file is applied during the
run. Whether individual forces inside such a file are scoped to initialization
only (oxDNA per-force start/end fields) cannot be decided from the input file
alone -> open question U-rest-1, resolvable only from the actual forces file
(digest-gated download-on-run, G1 = B).
"""
from __future__ import annotations

import argparse
import re

try:
    from .canonical import canonical_json
    from .digests import sha256_text
except ImportError:
    from canonical import canonical_json
    from digests import sha256_text

from hinge_family.sim_input import parse_sim_input

FORCE_SEMANTICS = {
    "external_forces": "PRODUCTION switch: loads the external forces file for the run",
    "external_forces_file": "PRODUCTION companion path of external_forces",
}

INIT_SCRIPT_KEYWORDS = (
    "external_forces",
    "mutual_trap",
    "trap",
    "spring",
    "relax",
    "mindist",
    "ARM",
    "RESTRAINT",
)

KEYWORD_LINE = re.compile("|".join(re.escape(k) for k in INIT_SCRIPT_KEYWORDS), re.IGNORECASE)


def inventory_input(text: str) -> dict:
    values = parse_sim_input(text)
    declared = {}
    for key in sorted(values):
        if key in FORCE_SEMANTICS or any(t in key.lower() for t in ("trap", "force")):
            declared[key] = {
                "value": values[key],
                "semantics": FORCE_SEMANTICS.get(
                    key,
                    "SUSPECT (force-named key; not in frozen semantics table)",
                ),
            }
    external_active = values.get("external_forces", "0").lower() in ("1", "true", "yes")
    if external_active:
        status = "EXTERNAL_FORCES_DECLARED_ACTIVE"
    elif declared:
        status = "FORCE_KEYS_PRESENT_INACTIVE"
    else:
        status = "NO_EXTERNAL_FORCES_DECLARED"
    return {
        "input_sha256": sha256_text(text),
        "input_keys_total": len(values),
        "restraint_keys": declared,
        "status": status,
        "open_questions": (
            ["U-rest-1: per-force init/end scoping inside the external forces file cannot be classified from the input file alone"]
            if external_active
            else []
        ),
    }


def inventory_script(text: str, source_name: str) -> dict:
    observations = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if KEYWORD_LINE.search(line):
            observations.append({"line": lineno, "text": line.strip()[:200]})
    return {
        "source_name": source_name,
        "source_sha256": sha256_text(text),
        "lines_total": len(text.splitlines()),
        "keyword_observations": observations,
    }


def combined(input_text: str, scripts: dict) -> dict:
    inv = inventory_input(input_text)
    script_reports = [inventory_script(text, name) for name, text in sorted(scripts.items())]
    hits = [
        {"source_name": r["source_name"], **obs}
        for r in script_reports
        for obs in r["keyword_observations"]
    ]
    if inv["status"] == "EXTERNAL_FORCES_DECLARED_ACTIVE" or hits:
        verdict = "RESTRAINTS_PRESENT: classify every listed occurrence before the E2 production run; a hinge angle held by external restraints is not a physical result"
    else:
        verdict = "NO_RESTRAINTS_OBSERVED: production input declares no external forces and scanned scripts contain no restraint keywords"
    return {
        "schema_version": 1,
        "kind": "restraints_inventory",
        "production_input": inv,
        "scanned_scripts": script_reports,
        "verdict": verdict,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="inventory restraints in a sim input and optional init scripts")
    parser.add_argument("input_path")
    parser.add_argument("--script", action="append", default=[], help="author init/relax script to scan (repeatable)")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    with open(args.input_path, "r", encoding="utf-8", newline="") as handle:
        input_text = handle.read()
    scripts = {}
    for path in args.script:
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as handle:
            scripts[path.replace("\\", "/").split("/")[-1]] = handle.read()
    report = combined(input_text, scripts)
    rendered = canonical_json(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
