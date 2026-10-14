#!/usr/bin/env python3
"""Standalone reproduction helper shipped inside a NanoLab component package.

Contract (docs/release/RELEASE_CONTRACT_V0_1.md in the NanoLab repo):
  * works from the PACKAGE ONLY, without internal knowledge of the author
    repository (fresh-environment rule, NL5-002);
  * stdlib-only (no third-party dependencies);
  * verify: recompute SHA-256 of every file listed in RELEASE_MANIFEST.json
    and compare sizes — detects a tampered/truncated package;
  * plan: print the per-card reproduction plan (engine pins, steps, expected
    values, rights constraints) so an external executor can run the engine
    without author knowledge;
  * this helper NEVER downloads upstream inputs and NEVER runs the physics
    engine by itself in v0.1; input retrieval and engine execution follow the
    per-card rights/reproduction sections and are executed by the external
    reproducer (clean-room, NL5-001-C / NL5-002).

Exit codes: 0 = ok, 3 = verification failure, 2 = usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

MANIFEST_NAME = "RELEASE_MANIFEST.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(pkg_root: Path) -> dict:
    errors: list[str] = []
    manifest_path = pkg_root / MANIFEST_NAME
    if not manifest_path.is_file():
        return {"mode": "verify", "ok": False, "errors": [f"{manifest_path}: manifest not found"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest.get("files", []):
        rel, expected = entry["path"], entry["sha256"]
        path = pkg_root / rel
        if not path.is_file():
            errors.append(f"missing file: {rel}")
            continue
        if (size := path.stat().st_size) != entry["size_bytes"]:
            errors.append(f"size mismatch: {rel} ({size} != {entry['size_bytes']})")
        if (digest := _sha256(path)) != expected:
            errors.append(f"sha256 mismatch: {rel} ({digest} != {expected})")
    return {"mode": "verify", "ok": not errors, "files": len(manifest.get("files", [])), "errors": errors}


def plan(pkg_root: Path) -> dict:
    plans: list[dict] = []
    errors: list[str] = []
    cards = sorted((pkg_root / "families").rglob("*.card.json")) if (pkg_root / "families").is_dir() else []
    if not cards:
        errors.append("no component cards found under families/")
    for path in cards:
        card = json.loads(path.read_text(encoding="utf-8"))
        measured = card.get("measurement_status")
        entry = {
            "card": path.relative_to(pkg_root).as_posix(),
            "component_id": card.get("component_id"),
            "measurement_status": measured,
            "claim_ceiling": card.get("claim_ceiling"),
            "rights_mode": (card.get("rights") or {}).get("rights_mode"),
            "engine_commit": (card.get("protocol_pins") or {}).get("engine_commit"),
            "steps": (card.get("reproduction") or {}).get("steps", []),
            "expected": (card.get("reproduction") or {}).get("expected", {}),
        }
        if measured == "NOT_MEASURED":
            entry["note"] = "NO MEASUREMENT TO REPRODUCE (KNOWN_GAP); do not fabricate values"
        plans.append(entry)
    return {"mode": "plan", "ok": not errors, "plans": plans, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NanoLab component package reproduction helper")
    parser.add_argument("--package-root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("mode", choices=["verify", "plan", "self-test"])
    args = parser.parse_args(argv)
    pkg_root = Path(args.package_root).resolve()

    if args.mode == "verify":
        report = verify(pkg_root)
    elif args.mode == "plan":
        report = plan(pkg_root)
    else:
        report = {"mode": "self-test", "verify": verify(pkg_root), "plan": plan(pkg_root)}
        report["ok"] = report["verify"].get("ok", False) and report["plan"].get("ok", False)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 3


if __name__ == "__main__":
    sys.exit(main())
