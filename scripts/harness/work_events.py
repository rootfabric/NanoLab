"""Validated, append-only writer for new C0 work records (not experiment runs)."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from .work_cli import inspect_execution, load, ALLOWED_EVENTS, TERMINAL


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def subject(root: Path, ref: str) -> str:
    value = subprocess.run(["git", "rev-parse", "--verify", "--end-of-options", ref + "^{commit}"], cwd=root,
                           check=True, capture_output=True, text=True).stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("subject is not a real commit")
    return value


def safe_target(root: Path, target: Path) -> Path:
    root = root.resolve()
    target = Path(os.path.abspath(target))
    parent = root / "docs/work/executions"
    if target.parent != parent or not re.fullmatch(r"EX-[A-Z0-9-]+", target.name):
        raise ValueError("target must be docs/work/executions/EX-<ID> within root")
    for part in (root / "docs", root / "docs/work", parent, target, target / "events", target / "passport.json", target / "summary.md"):
        if part.is_symlink():
            raise ValueError("symlink in work record path")
    return target


@contextmanager
def locked(target):
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = target.parent / ("." + target.name + ".writer.lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


def text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def event(passport, seq, kind, role, sha, summary, evidence_refs, next_action):
    if not summary.strip():
        raise ValueError("summary must not be empty")
    if kind not in ALLOWED_EVENTS:
        raise ValueError("unsupported event type")
    if role == "IMPLEMENTER" and kind in {"REVIEW_RECORDED", "REVIEW_CORRECTIONS"}:
        raise ValueError("implementer cannot issue independent review records")
    return {"schema_version": 1, "event_id": f"{seq:04d}-" + kind.lower().replace("_", "-"),
            "sequence": seq, "timestamp_source": "machine", "timestamp_utc": utc_now(),
            "execution_id": passport["execution_id"], "work_order_id": passport["work_order_id"],
            "event_type": kind, "actor_role": role, "subject_sha": sha, "summary": summary,
            "evidence_refs": evidence_refs, "next_action": next_action}


def ensure_valid(directory):
    result = inspect_execution(directory)
    if not result["ok"]:
        raise ValueError("; ".join(result["errors"]))
    return result


def start(root, target, *, work_order, checkpoint, risk, allowed_paths, sha, summary, next_action):
    target = safe_target(root, target)
    sha = subject(root, sha)
    if not work_order.strip() or not allowed_paths or any(not p.strip() for p in allowed_paths):
        raise ValueError("work_order and allowed_paths are required")
    if checkpoint not in {f"NL{i}" for i in range(9)} | {f"INFRA{i}" for i in range(8)}:
        raise ValueError("invalid checkpoint")
    if risk not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        raise ValueError("invalid risk")
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=root, check=True, capture_output=True, text=True).stdout.strip() or "detached/" + sha
    passport = {"schema_version": 1, "execution_id": target.name, "work_order_id": work_order,
                "checkpoint": checkpoint, "base_sha": sha, "branch": branch, "risk_class": risk,
                "claim_class": "C0_SOFTWARE_ONLY", "allowed_paths": allowed_paths, "started_at_utc": utc_now(),
                "status": "STARTED", "event_ordering": "sequence-v1"}
    first = event(passport, 1, "WORK_ORDER_STARTED", "IMPLEMENTER", sha, summary, [], next_action)
    with locked(target):
        if target.exists():
            raise ValueError("execution already exists; records are never overwritten")
        with tempfile.TemporaryDirectory(dir=target.parent, prefix=".work-start-") as temp:
            staged = Path(temp) / target.name
            (staged / "events").mkdir(parents=True)
            (staged / "passport.json").write_text(text(passport), encoding="utf-8")
            (staged / "events" / (first["event_id"] + ".json")).write_text(text(first), encoding="utf-8")
            ensure_valid(staged)
            staged.rename(target)
    return ensure_valid(target)


def append(root, target, *, kind, role, sha, summary, evidence_refs=(), next_action=None):
    target = safe_target(root, target)
    sha = subject(root, sha)
    with locked(target):
        ensure_valid(target)
        passport = load(target / "passport.json")
        if passport.get("event_ordering") != "sequence-v1":
            raise ValueError("writer requires a NEW sequence-v1 C0 execution; do not migrate history")
        paths = sorted((target / "events").glob("*.json"))
        if len(paths) >= 9999:
            raise ValueError("event sequence exhausted")
        new = event(passport, len(paths) + 1, kind, role, sha, summary, list(evidence_refs), next_action)
        if kind in TERMINAL and (not (target / "summary.md").is_file() or not (target / "summary.md").read_text(encoding="utf-8").strip()):
            raise ValueError("finish requires a non-empty summary.md")
        with tempfile.TemporaryDirectory(dir=target.parent, prefix=".work-append-") as temp:
            staged = Path(temp)
            (staged / "events").mkdir()
            shutil.copyfile(target / "passport.json", staged / "passport.json")
            for path in paths:
                if path.is_symlink() or not path.is_file():
                    raise ValueError("unsafe event path")
                shutil.copyfile(path, staged / "events" / path.name)
            if (target / "summary.md").exists():
                shutil.copyfile(target / "summary.md", staged / "summary.md")
            candidate = staged / "events" / (new["event_id"] + ".json")
            candidate.write_text(text(new), encoding="utf-8")
            ensure_valid(staged)
            # Atomic no-overwrite publication on the same filesystem. Lock serializes writers.
            os.link(candidate, target / "events" / candidate.name)
    return ensure_valid(target)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["start", "record", "finish", "correct"])
    parser.add_argument("execution_dir")
    parser.add_argument("--root", default=".")
    parser.add_argument("--subject", default="HEAD")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--next-action")
    parser.add_argument("--work-order")
    parser.add_argument("--checkpoint", default="NL5")
    parser.add_argument("--risk", choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"], default="MEDIUM")
    parser.add_argument("--allow", action="append", default=[])
    parser.add_argument("--role", choices=["IMPLEMENTER", "REVIEWER", "VERIFIER", "DIRECTOR"], default="IMPLEMENTER")
    parser.add_argument("--event-type", choices=sorted(ALLOWED_EVENTS))
    parser.add_argument("--evidence", action="append", default=[])
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    target = Path(args.execution_dir)
    if not target.is_absolute():
        target = root / target
    try:
        if args.mode == "start":
            result = start(root, target, work_order=args.work_order or "", checkpoint=args.checkpoint, risk=args.risk,
                           allowed_paths=args.allow, sha=args.subject, summary=args.summary, next_action=args.next_action)
        else:
            defaults = {"record": "CONTINUATION_CHECKPOINT", "finish": "HANDOFF_COMPLETED",
                        "correct": "CONTINUATION_CHECKPOINT" if args.role == "IMPLEMENTER" else "REVIEW_CORRECTIONS"}
            kind = args.event_type or defaults[args.mode]
            if args.mode == "finish" and kind not in TERMINAL:
                raise ValueError("finish must be a handoff/blocked/cancelled event")
            if args.mode != "finish" and kind in TERMINAL:
                raise ValueError("terminal events require finish")
            result = append(root, target, kind=kind, role=args.role, sha=args.subject, summary=args.summary,
                            evidence_refs=args.evidence, next_action=args.next_action)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    print(json.dumps({"command": args.mode.upper(), **result}, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
