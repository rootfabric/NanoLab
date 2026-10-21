"""S17 R2 recovery evidence: digest recovered files and verify byte relations.

WO-PREP-S17-R2 stage A/E. This tool turns a bounded local recovery session
(pinned-URL downloads, ZIP central-directory range extractions) into a
deterministic, machine-readable evidence record:

* ``files``: each entry declares a label and a local path; the tool records
  size + SHA-256 of the actual bytes (fail-closed on missing files).
* ``relations``: declared byte-level identities (e.g. "recovered
  ``hinge23/nNE1/linked.top`` is byte-identical to the R1 pin of
  ``s17/nanobase/structure/nNE.top``") are verified against the digests and
  get an explicit verdict; a broken expectation is a recorded ``VIOLATED``
  fact, never silently dropped.

The tool never writes the recovered bytes into Git; it only records digests,
sizes and verdicts. Claim discipline: a byte identity is a static file fact
and never implies a scientific result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


class RecoveryError(Exception):
    pass


def digest_file(path: Path) -> dict:
    if not path.is_file():
        raise RecoveryError(f"declared recovery file is missing: {path}")
    data = path.read_bytes()
    return {"size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def run(spec: dict) -> dict:
    if not isinstance(spec, dict) or not isinstance(spec.get("files"), list):
        raise RecoveryError("spec must contain a 'files' list")
    labels: dict[str, dict] = {}
    problems: list[str] = []
    for i, item in enumerate(spec["files"]):
        where = f"files[{i}]"
        if not isinstance(item, dict) or not {"label", "path"} <= set(item):
            raise RecoveryError(f"{where}: entries must have label and path")
        label = item["label"]
        if label in labels:
            raise RecoveryError(f"{where}: duplicate label {label!r}")
        try:
            rec = digest_file(Path(item["path"]))
            rec.update({k: item[k] for k in item if k in ("origin_url", "origin_note", "role")})
            labels[label] = rec
        except RecoveryError as exc:
            problems.append(str(exc))
            labels[label] = {"error": str(exc)}
    relations = []
    for i, rel in enumerate(spec.get("relations", [])):
        where = f"relations[{i}]"
        if not isinstance(rel, dict) or not {"kind", "left", "right"} <= set(rel):
            raise RecoveryError(f"{where}: relations need kind/left/right")
        if rel["kind"] != "byte_identity":
            raise RecoveryError(f"{where}: unsupported relation kind {rel['kind']!r}")
        left = labels.get(rel["left"], {})
        right = labels.get(rel["right"], {})
        verdict = "PENDING"
        detail = None
        if "error" in left or "error" in right:
            verdict = "NOT_EVALUABLE"
            detail = left.get("error") or right.get("error")
        else:
            same = left.get("sha256") == right.get("sha256")
            verdict = "CONFIRMED" if same else "VIOLATED"
            detail = {"left_sha256": left.get("sha256"), "right_sha256": right.get("sha256")}
        out = {"kind": rel["kind"], "left": rel["left"], "right": rel["right"],
               "verdict": verdict, "detail": detail}
        if "note" in rel:
            out["note"] = rel["note"]
        relations.append(out)
    return {
        "schema_version": 1,
        "kind": "s17_r2_recovery_evidence",
        "claim": "static file facts only (digests and byte identities); never a scientific result",
        "files": labels,
        "relations": relations,
        "problems": problems,
    }


def build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="S17 R2 recovery evidence builder (offline)")
    p.add_argument("--input", type=Path, required=True, help="spec JSON (files + relations)")
    p.add_argument("--out", type=Path, required=True, help="output evidence JSON path")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_cli().parse_args(argv)
    spec = json.loads(args.input.read_text(encoding="utf-8"))
    try:
        result = run(spec)
    except RecoveryError as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr)
        return 3
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    violated = [r for r in result["relations"] if r["verdict"] == "VIOLATED"]
    print(f"files: {len(result['files'])}, relations: {len(result['relations'])}, "
          f"problems: {len(result['problems'])}, violated: {len(violated)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
