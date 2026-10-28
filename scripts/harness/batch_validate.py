"""One-process equivalents of hosted JSON and work-execution sweeps."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from .work_cli import inspect_execution

EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
PINNED_NON_JSON = {
    "experiments/evidence/E0/E0-R1/fixtures/negative/n001_empty_passport/execution/passport.json": EMPTY,
    "experiments/evidence/E0/E0-R1/fixtures/negative/n002_truncated_json/execution/passport.json": "1de18ae447d83f621e98f64ef928858e9c0b1456144f10b4870bfcea8a3c4a85",
    "docs/work/executions/EX-NL3-002-PARAM-74B-R1/evidence/arm-manifest-74b-run1.stdout.json": EMPTY,
    "docs/work/executions/EX-NL3-002-PARAM-74B-R1/evidence/arm-manifest-74b-run2.stdout.json": EMPTY,
}


def check_json(root: Path) -> dict:
    paths = subprocess.run(["git", "ls-files", "-z", "--", "*.json"], cwd=root, check=True, stdout=subprocess.PIPE).stdout.decode("utf-8").split("\0")
    paths = [p for p in paths if p]
    errors, pinned = [], 0
    if not paths:
        errors.append("no tracked JSON files found")
    for name in paths:
        try:
            payload = (root / name).read_bytes()
            if name in PINNED_NON_JSON:
                if hashlib.sha256(payload).hexdigest() != PINNED_NON_JSON[name]:
                    raise ValueError("pinned non-JSON evidence digest mismatch")
                pinned += 1
            else:
                json.loads(payload.decode("utf-8"))
        except (ValueError, OSError, UnicodeError) as exc:
            errors.append(name + ": " + str(exc))
    return {"ok": not errors, "errors": errors, "checked": len(paths), "pinned_non_json": pinned}


def check_executions(root: Path) -> dict:
    dirs = sorted(p for p in (root / "docs/work/executions").glob("EX-*") if p.is_dir())
    errors, results = [], []
    if not dirs:
        errors.append("no execution directories found")
    for directory in dirs:
        try:
            if directory.is_symlink():
                raise ValueError("symlink execution directory")
            result = inspect_execution(directory)
        except (ValueError, OSError, TypeError, KeyError) as exc:
            result = {"ok": False, "errors": [str(exc)]}
        results.append({"execution": directory.name, **result})
        if not result["ok"]:
            errors.extend(directory.name + ": " + str(e) for e in result["errors"])
    return {"ok": not errors, "errors": errors, "checked": len(dirs), "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["json", "executions"])
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    try:
        result = (check_json if args.mode == "json" else check_executions)(Path(args.root).resolve())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
