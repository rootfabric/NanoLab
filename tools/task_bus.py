#!/usr/bin/env python3
"""Bounded, cooperative Git task bus. Python 3.10+, Git; no third-party packages.

The queue is an append-only event log on a separate branch. Normal fast-forward
push is the compare-and-swap boundary. This pilot never merges or accepts main.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import uuid

BUS_BRANCH = "control/task-bus-pilot-r1"
QUEUE_PATH = "task-bus/queue.json"
ROLES = ("IMPLEMENTER", "REVIEWER", "VERIFIER", "DIRECTOR")
SHA = re.compile(r"[0-9a-f]{40}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}\Z")
TASK_ID = re.compile(r"BUS-[A-Z0-9-]{1,60}\Z")
MAX_BYTES = 2_000_000


class BusError(Exception):
    """A fail-closed protocol or transport error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BusError(message)


def text(value: object) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 8000


def integer(value: object) -> bool:
    return type(value) is int


def oid(value: object) -> bool:
    return isinstance(value, str) and bool(SHA.fullmatch(value))


def path_ok(value: object) -> bool:
    if not isinstance(value, str) or not value or len(value) > 512:
        return False
    parts = value.rstrip("/").split("/")
    return (not value.startswith("/") and "\\" not in value
            and all(p not in ("", ".", "..", ".git") for p in parts)
            and not any(ord(c) < 32 for c in value))


def encoded(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                      allow_nan=False) + "\n"



def write_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".bus-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def decode(raw: str) -> dict:
    require(len(raw.encode("utf-8")) <= MAX_BYTES, "QUEUE_TOO_LARGE")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(BusError("NONFINITE_JSON")))
    except (ValueError, TypeError) as exc:
        raise BusError("INVALID_JSON") from exc
    require(isinstance(value, dict), "JSON_OBJECT_REQUIRED")
    return value


def validate_policy(policy: dict) -> None:
    require(isinstance(policy, dict) and policy.get("mode") == "SANDBOX", "SANDBOX_ONLY")
    actors = policy.get("actors")
    require(isinstance(actors, dict) and bool(actors), "ACTORS_REQUIRED")
    for name, profile in actors.items():
        require(bool(ID.fullmatch(name)) and isinstance(profile, dict), "INVALID_ACTOR")
        require(profile.get("role") in ROLES, "INVALID_ROLE")
        caps = profile.get("capabilities")
        require(isinstance(caps, list) and all(text(c) for c in caps), "INVALID_CAPABILITIES")
    require(any(a["role"] == "DIRECTOR" for a in actors.values()), "DIRECTOR_REQUIRED")
    require(integer(policy.get("lease_seconds")) and 60 <= policy["lease_seconds"] <= 3600,
            "INVALID_LEASE_DURATION")
    require(integer(policy.get("max_claims")) and 4 <= policy["max_claims"] <= 32,
            "INVALID_CLAIM_BUDGET")
    require(integer(policy.get("max_repairs")) and 0 <= policy["max_repairs"] <= 5,
            "INVALID_REPAIR_BUDGET")


def validate_spec(spec: dict, tasks: dict) -> None:
    require(isinstance(spec, dict), "SPEC_REQUIRED")
    require(isinstance(spec.get("id"), str) and bool(TASK_ID.fullmatch(spec["id"])), "PILOT_ID_REQUIRED")
    require(spec.get("kind") == "PILOT" and spec.get("claim_class") == "C0_SOFTWARE_ONLY",
            "C0_PILOT_ONLY")
    require(text(spec.get("goal")) and oid(spec.get("base_sha")), "GOAL_AND_EXACT_BASE_REQUIRED")
    paths = spec.get("allowed_paths")
    require(isinstance(paths, list) and bool(paths) and all(path_ok(p) for p in paths), "INVALID_SCOPE")
    require(all(p.startswith("docs/work/pilots/" + spec["id"] + "/") for p in paths),
            "PILOT_SCOPE_ONLY")
    deps = spec.get("depends_on")
    require(isinstance(deps, list) and all(isinstance(d, str) and d in tasks for d in deps),
            "DEPENDENCY_MUST_ALREADY_EXIST")
    require(len(set(deps)) == len(deps), "DUPLICATE_DEPENDENCY")
    capabilities = spec.get("capabilities")
    require(isinstance(capabilities, dict) and set(capabilities) == set(ROLES), "ROLE_CAPABILITIES_REQUIRED")
    require(all(isinstance(c, list) and all(text(v) for v in c) for c in capabilities.values()),
            "INVALID_CAPABILITIES")


def apply(tasks: dict, policy: dict, event: dict) -> None:
    """Deterministic reducer; mutates only the caller-owned projection."""
    require(isinstance(event, dict) and set(event) == {"id", "actor", "op", "task", "at", "data"},
            "INVALID_EVENT_FIELDS")
    require(isinstance(event["id"], str) and bool(ID.fullmatch(event["id"])), "INVALID_EVENT_ID")
    require(integer(event["at"]) and event["at"] >= 0 and isinstance(event["data"], dict), "INVALID_EVENT")
    actor, op, tid, at, data = (event[k] for k in ("actor", "op", "task", "at", "data"))
    require(isinstance(actor, str) and actor in policy["actors"], "ACTOR_NOT_ALLOWED")
    require(isinstance(tid, str) and bool(TASK_ID.fullmatch(tid)), "INVALID_TASK_ID")
    role = policy["actors"][actor]["role"]
    if op == "open":
        require(role == "DIRECTOR" and tid not in tasks, "OPEN_DENIED")
        validate_spec(data, tasks)
        require(tid == data["id"], "TASK_ID_MISMATCH")
        tasks[tid] = {"spec": copy.deepcopy(data), "phase": "IMPLEMENTER", "lease": None,
                      "subject": None, "approvals": {}, "claims": 0, "repairs": 0,
                      "blocker": None, "resume_phase": None}
        return
    require(tid in tasks, "UNKNOWN_TASK")
    task = tasks[tid]
    require(task["phase"] not in ("COMPLETED_SANDBOX", "CANCELLED"), "TASK_TERMINAL")
    lease = task["lease"]
    if op in ("reclaim", "resume", "cancel", "invalidate"):
        require(role == "DIRECTOR" and text(data.get("reason")), "DIRECTOR_REASON_REQUIRED")
        if op == "reclaim":
            require(lease is not None and at >= lease["until"], "LEASE_NOT_EXPIRED")
            task["lease"] = None
        elif op == "resume":
            require(task["phase"] == "BLOCKED", "NOT_BLOCKED")
            task["phase"], task["resume_phase"], task["blocker"] = task["resume_phase"], None, None
        elif op == "invalidate":
            require(task["subject"] is not None, "NO_SUBJECT_TO_INVALIDATE")
            require(task["repairs"] < policy["max_repairs"], "REPAIR_BUDGET_EXHAUSTED")
            task.update(phase="IMPLEMENTER", lease=None, subject=None, approvals={},
                        repairs=task["repairs"] + 1, blocker=None, resume_phase=None)
        else:
            task.update(phase="CANCELLED", lease=None, blocker=data["reason"])
        return
    if op == "claim":
        require(not data, "CLAIM_HAS_NO_PAYLOAD")
        require(task["phase"] == role and lease is None, "TASK_NOT_CLAIMABLE")
        require(all(tasks[d]["phase"] == "COMPLETED_SANDBOX" for d in task["spec"]["depends_on"]),
                "DEPENDENCY_NOT_COMPLETE")
        require(set(task["spec"]["capabilities"][role]) <= set(policy["actors"][actor]["capabilities"]),
                "CAPABILITY_MISMATCH")
        require(task["claims"] < policy["max_claims"], "CLAIM_BUDGET_EXHAUSTED")
        task["claims"] += 1
        task["lease"] = {"actor": actor, "token": event["id"], "until": at + policy["lease_seconds"]}
        return
    require(lease is not None and lease["actor"] == actor and data.get("token") == lease["token"],
            "STALE_OR_FOREIGN_LEASE")
    require(at < lease["until"], "LEASE_EXPIRED")
    require(task["phase"] == role, "ROLE_MISMATCH")
    if op == "heartbeat":
        lease["until"] = at + policy["lease_seconds"]
    elif op == "release":
        require(text(data.get("reason")), "REASON_REQUIRED")
        task["lease"] = None
    elif op == "block":
        require(text(data.get("reason")), "REASON_REQUIRED")
        task.update(resume_phase=task["phase"], phase="BLOCKED", lease=None, blocker=data["reason"])
    elif op == "finish":
        report = data.get("report")
        require(isinstance(report, dict) and text(report.get("summary")), "REPORT_REQUIRED")
        verdict = report.get("verdict")
        require(verdict in ("PASS", "FAIL", "INSUFFICIENT_EVIDENCE"), "INVALID_VERDICT")
        require(oid(report.get("subject_head")) and oid(report.get("subject_tree")), "EXACT_SUBJECT_REQUIRED")
        checks = report.get("checks")
        require(isinstance(checks, list) and bool(checks) and all(
            isinstance(c, dict) and text(c.get("command")) and integer(c.get("exit_code")) for c in checks),
            "CHECKS_REQUIRED")
        require(verdict != "PASS" or all(c["exit_code"] == 0 for c in checks), "PASS_WITH_FAILED_CHECK")
        if role == "IMPLEMENTER":
            require(verdict == "PASS", "IMPLEMENTER_USE_BLOCK_FOR_FAILURE")
            subject = data.get("subject")
            require(isinstance(subject, dict) and set(subject) == {"head", "tree", "ref"}
                    and oid(subject["head"]) and oid(subject["tree"])
                    and text(subject["ref"]) and subject["ref"].startswith("work/"), "INVALID_SUBJECT")
            task["subject"] = copy.deepcopy(subject)
        subject = task["subject"]
        require(subject is not None and report["subject_head"] == subject["head"]
                and report["subject_tree"] == subject["tree"], "SUBJECT_MISMATCH")
        if verdict == "INSUFFICIENT_EVIDENCE":
            task.update(resume_phase=role, phase="BLOCKED", lease=None, blocker=report["summary"])
        elif verdict == "FAIL":
            require(role in ("REVIEWER", "VERIFIER"), "REJECTION_ROLE_REQUIRED")
            require(task["repairs"] < policy["max_repairs"], "REPAIR_BUDGET_EXHAUSTED")
            task.update(phase="IMPLEMENTER", lease=None, subject=None, approvals={},
                        repairs=task["repairs"] + 1)
        else:
            require(actor not in task["approvals"].values(), "ROLE_SEPARATION_REQUIRED")
            task["approvals"][role] = actor
            if role == "DIRECTOR":
                require(set(task["approvals"]) == set(ROLES), "APPROVALS_MISSING")
                task["phase"] = "COMPLETED_SANDBOX"
            else:
                task["phase"] = ROLES[ROLES.index(role) + 1]
            task["lease"] = None
    else:
        raise BusError("UNKNOWN_OPERATION")


def replay(document: dict) -> dict:
    require(isinstance(document, dict) and set(document) == {"schema_version", "policy", "events"}
            and type(document["schema_version"]) is int and document["schema_version"] == 1, "INVALID_DOCUMENT")
    validate_policy(document["policy"])
    require(isinstance(document["events"], list), "EVENTS_REQUIRED")
    tasks, seen, last = {}, set(), 0
    for event in document["events"]:
        require(isinstance(event, dict) and isinstance(event.get("id"), str), "INVALID_EVENT")
        require(event["id"] not in seen, "DUPLICATE_EVENT_ID")
        require(integer(event.get("at")) and event["at"] >= last, "NONMONOTONIC_EVENT_TIME")
        apply(tasks, document["policy"], event)
        seen.add(event["id"])
        last = event["at"]
    return tasks


def append(document: dict, event: dict) -> tuple[dict, dict, bool]:
    tasks = replay(document)
    for old in document["events"]:
        if old["id"] == event["id"]:
            require(all(old[k] == event[k] for k in ("actor", "op", "task", "data")), "IDEMPOTENCY_KEY_COLLISION")
            return document, tasks, True
    result = copy.deepcopy(document)
    result["events"].append(event)
    return result, replay(result), False


class GitBus:
    """Git plumbing only: never checks out, resets, rebases or force-pushes."""
    def __init__(self, repo: str | Path, remote: str = "origin", branch: str = BUS_BRANCH):
        self.repo, self.remote, self.branch = Path(repo).resolve(), remote, branch
        require(bool(re.fullmatch(r"[A-Za-z0-9_.-]+", remote)) and not remote.startswith("-"), "INVALID_REMOTE")
        require(branch.startswith("control/task-bus-") and not branch.endswith("/"), "DEDICATED_BUS_BRANCH_REQUIRED")
        self.git("check-ref-format", "refs/heads/" + branch)

    def git(self, *args: str, data: str | None = None, env: dict | None = None) -> str:
        merged = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            merged.pop(key, None)
        merged.update({"GIT_TERMINAL_PROMPT": "0", "GIT_NO_REPLACE_OBJECTS": "1"})
        if env:
            merged.update(env)
        try:
            p = subprocess.run(["git", "-C", str(self.repo), *args], input=data,
                               text=True, encoding="utf-8", stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=merged, timeout=45)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BusError("GIT_TRANSPORT_UNAVAILABLE") from exc
        require(p.returncode == 0, "GIT_FAILED: " + p.stderr.strip()[-1200:])
        return p.stdout.rstrip("\n")

    def fetch(self, branch: str) -> str:
        self.git("check-ref-format", "refs/heads/" + branch)
        local = "refs/task-bus/" + uuid.uuid4().hex
        try:
            self.git("fetch", "--no-tags", "--no-write-fetch-head", self.remote,
                     "refs/heads/" + branch + ":" + local)
            return self.git("rev-parse", local + "^{commit}")
        finally:
            self.git("update-ref", "-d", local)

    def load(self) -> tuple[str, dict]:
        head = self.fetch(self.branch)
        document = decode(self.git("show", head + ":" + QUEUE_PATH))
        replay(document)
        return head, document

    def commit(self, parent: str, document: dict, message: str) -> str:
        raw = encoded(document)
        require(len(raw.encode("utf-8")) <= MAX_BYTES, "QUEUE_TOO_LARGE")
        with tempfile.TemporaryDirectory(prefix="nanolab-bus-index-") as tmp:
            env = {"GIT_INDEX_FILE": str(Path(tmp) / "index"),
                   "GIT_AUTHOR_NAME": "NanoLab Task Bus", "GIT_AUTHOR_EMAIL": "task-bus@users.noreply.github.com",
                   "GIT_COMMITTER_NAME": "NanoLab Task Bus", "GIT_COMMITTER_EMAIL": "task-bus@users.noreply.github.com"}
            self.git("read-tree", parent, env=env)
            blob = self.git("hash-object", "-w", "--stdin", data=raw)
            self.git("update-index", "--add", "--cacheinfo", "100644," + blob + "," + QUEUE_PATH, env=env)
            tree = self.git("write-tree", env=env)
            return self.git("commit-tree", tree, "-p", parent, "-m", message, env=env)

    def push(self, head: str) -> None:
        self.git("push", "--porcelain", self.remote, head + ":refs/heads/" + self.branch)

    def initialize(self, document: dict, base: str) -> str:
        require(oid(base), "EXACT_BASE_REQUIRED")
        replay(document)
        require(not document["events"], "INIT_REQUIRES_EMPTY_LOG")
        remote = self.git("ls-remote", "--heads", self.remote, "refs/heads/" + self.branch)
        require(not remote, "BUS_ALREADY_EXISTS")
        head = self.commit(base, document, "harness(bus): initialize sandbox queue")
        self.push(head)
        return head

    def check_subject(self, subject: dict, spec: dict) -> None:
        require(isinstance(subject, dict) and oid(subject.get("head")) and oid(subject.get("tree")), "INVALID_SUBJECT")
        branch = subject.get("ref")
        require(isinstance(branch, str) and branch.startswith("work/"), "WORK_BRANCH_REQUIRED")
        head = self.fetch(branch)
        require(head == subject["head"], "CANDIDATE_REF_DRIFT")
        require(self.git("rev-parse", head + "^{tree}") == subject["tree"], "CANDIDATE_TREE_MISMATCH")
        base = spec["base_sha"]
        self.git("merge-base", "--is-ancestor", base, head)
        paths = self.git("diff", "--no-renames", "--name-only", "-z", base, head, "--").split("\0")
        paths = [p for p in paths if p]
        require(bool(paths), "EMPTY_CANDIDATE")
        allowed = spec["allowed_paths"]
        require(all(any(p == a or (a.endswith("/") and p.startswith(a)) for a in allowed) for p in paths),
                "CANDIDATE_OUT_OF_SCOPE")
        entries = self.git("ls-tree", "-r", "-z", head, "--", *paths).split("\0")
        require(all(entry.startswith("100644 blob ") for entry in entries if entry),
                "CANDIDATE_REQUIRES_REGULAR_DATA_FILES")

    def transact(self, actor: str, op: str, task: str, data: dict,
                 message_id: str | None = None, attempts: int = 5) -> dict:
        event_id = message_id or uuid.uuid4().hex
        require(isinstance(event_id, str) and bool(ID.fullmatch(event_id)), "INVALID_EVENT_ID")
        for attempt in range(attempts):
            parent, document = self.load()
            last = document["events"][-1]["at"] if document["events"] else 0
            now = int(time.time())
            require(last <= now + 60, "CLOCK_SKEW_OVER_60_SECONDS")
            event = {"id": event_id, "actor": actor, "op": op, "task": task,
                     "at": max(now, last), "data": data}
            updated, tasks, duplicate = append(document, event)
            if duplicate:
                old = next(e for e in document["events"] if e["id"] == event_id)
                return {"committed": True, "duplicate": True, "bus_head": parent,
                        "event": old, "task": tasks[task]}
            if op == "finish":
                before = replay(document)[task]
                subject = data.get("subject") if before["phase"] == "IMPLEMENTER" else before["subject"]
                self.check_subject(subject, before["spec"])
            child = self.commit(parent, updated, "harness(bus): " + op + " " + task + " " + event_id)
            try:
                self.push(child)
                return {"committed": True, "duplicate": False, "bus_head": child,
                        "event": event, "task": tasks[task]}
            except BusError:
                # Re-read and re-apply. Also detects a successful push with a lost ACK.
                if attempt == attempts - 1:
                    head, final = self.load()
                    old = next((e for e in final["events"] if e["id"] == event_id), None)
                    if old is not None:
                        _, state, _ = append(final, event)
                        return {"committed": True, "duplicate": True, "bus_head": head,
                                "event": old, "task": state[task]}
                    raise BusError("PUBLISH_NOT_CONFIRMED_RETRY_SAME_MESSAGE_ID")
        raise BusError("NO_TRANSPORT_ATTEMPTS")

    def inbox(self, actor: str) -> dict:
        head, document = self.load()
        require(actor in document["policy"]["actors"], "ACTOR_NOT_ALLOWED")
        profile, tasks, now = document["policy"]["actors"][actor], replay(document), int(time.time())
        rows = []
        for tid, task in tasks.items():
            phase, lease = task["phase"], task["lease"]
            action = "WAIT_EXTERNAL"
            if phase in ("COMPLETED_SANDBOX", "CANCELLED", "BLOCKED"):
                action = phase
            elif lease:
                if lease["until"] <= now:
                    action = "RECLAIM" if profile["role"] == "DIRECTOR" else "WAIT_RECLAIM"
                elif lease["actor"] == actor:
                    action = "CONTINUE"
            elif all(tasks[d]["phase"] == "COMPLETED_SANDBOX" for d in task["spec"]["depends_on"]):
                if task["claims"] >= document["policy"]["max_claims"]:
                    action = "BUDGET_EXHAUSTED"
                elif profile["role"] == phase and set(task["spec"]["capabilities"][phase]) <= set(profile["capabilities"]):
                    action = "CLAIM"
                elif profile["role"] == "DIRECTOR":
                    action = "DISPATCH_OR_WAIT"
            rows.append({"id": tid, "phase": phase, "action": action, "lease": lease,
                         "subject": task["subject"], "blocker": task["blocker"],
                         "spec": task["spec"], "claims": task["claims"], "repairs": task["repairs"]})
        return {"bus_head": head, "mode": "SANDBOX", "canonical_acceptance": False,
                "actor": actor, "tasks": rows}


def smoke_check(root: Path) -> dict:
    path = root / "docs/work/pilots/BUS-SMOKE-001/receipt.json"
    current = Path(root)
    for part in path.relative_to(root).parts:
        current = current / part
        require(not current.is_symlink(), "SMOKE_SYMLINK_DENIED")
    raw = path.read_bytes()
    actual = decode(raw.decode("utf-8"))
    expected = {"schema_version": 1, "task_id": "BUS-SMOKE-001",
                "message": "NanoLab distributed workflow smoke", "values": [1, 2, 3],
                "sum": 6, "scientific_claim": False}
    require(encoded(actual) == encoded(expected), "SMOKE_CONTRACT_MISMATCH")
    return {"verdict": "PASS", "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default=BUS_BRANCH)
    parser.add_argument("--actor", default="director-pilot")
    parser.add_argument("--message-id", help="Keep identical across retries after an uncertain result")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    history = sub.add_parser("history")
    history.add_argument("task")
    init = sub.add_parser("init")
    init.add_argument("--policy", required=True)
    init.add_argument("--base", required=True)
    opening = sub.add_parser("open")
    opening.add_argument("--spec", required=True)
    checking = sub.add_parser("smoke-check")
    checking.add_argument("root", type=Path)
    for name in ("claim", "heartbeat", "release", "reclaim", "block", "resume", "cancel", "invalidate", "finish"):
        cmd = sub.add_parser(name)
        cmd.add_argument("task")
        cmd.add_argument("--token", help="Normally read automatically from the local claim receipt")
        if name in ("release", "reclaim", "block", "resume", "cancel", "invalidate"):
            cmd.add_argument("--reason", required=True)
        if name == "finish":
            cmd.add_argument("--report", required=True)
            cmd.add_argument("--candidate-ref", help="Required only for the IMPLEMENTER handoff")
    args = parser.parse_args(argv)
    try:
        if args.command == "smoke-check":
            print(encoded(smoke_check(args.root)), end="")
            return 0
        bus = GitBus(args.repo, args.remote, args.branch)
        if args.command == "status":
            result = bus.inbox(args.actor)
        elif args.command == "history":
            head, document = bus.load()
            require(args.actor in document["policy"]["actors"], "ACTOR_NOT_ALLOWED")
            require(args.task in replay(document), "UNKNOWN_TASK")
            result = {"bus_head": head, "task": args.task,
                      "events": [e for e in document["events"] if e["task"] == args.task]}
        elif args.command == "init":
            policy = decode(Path(args.policy).read_text(encoding="utf-8"))
            result = {"bus_head": bus.initialize({"schema_version": 1, "policy": policy, "events": []}, args.base)}
        else:
            if args.command == "open":
                data = decode(Path(args.spec).read_text(encoding="utf-8"))
                task = data["id"]
            else:
                task, data = args.task, {}
            require(bool(ID.fullmatch(args.actor)) and bool(TASK_ID.fullmatch(task)), "INVALID_ID")
            receipt_path = bus.git("rev-parse", "--git-path", "task-bus-receipts/" + args.actor + "/" + task + ".json")
            receipt = Path(receipt_path)
            if not receipt.is_absolute():
                receipt = bus.repo / receipt
            if args.command in ("heartbeat", "release", "block", "finish"):
                saved = decode(receipt.read_text(encoding="utf-8")) if not args.token else None
                if saved is not None:
                    require(saved.get("remote") == args.remote and saved.get("branch") == args.branch
                            and saved.get("actor") == args.actor and saved.get("task") == task, "CLAIM_RECEIPT_MISMATCH")
                data["token"] = args.token or saved["token"]
            if hasattr(args, "reason"):
                data["reason"] = args.reason
            if args.command == "finish":
                data["report"] = decode(Path(args.report).read_text(encoding="utf-8"))
                if args.candidate_ref:
                    data["subject"] = {"ref": args.candidate_ref, "head": data["report"]["subject_head"],
                                       "tree": data["report"]["subject_tree"]}
            # Deterministic retry ID for local recovery when the caller omitted one.
            identity = {"actor": args.actor, "op": args.command, "task": task, "data": data}
            pending = receipt.with_suffix(".pending.json")
            message_id = args.message_id
            if message_id is None and pending.exists():
                saved_pending = decode(pending.read_text(encoding="utf-8"))
                if saved_pending["identity"] == identity:
                    message_id = saved_pending["id"]
            message_id = message_id or uuid.uuid4().hex
            pending.parent.mkdir(parents=True, exist_ok=True)
            write_atomic(pending, {"id": message_id, "identity": identity})
            result = bus.transact(args.actor, args.command, task, data, message_id)
            if args.command == "claim":
                lease = result["task"]["lease"]
                require(lease is not None and lease["actor"] == args.actor and lease["token"] == message_id
                        and lease["until"] > int(time.time()), "REPLAYED_CLAIM_NO_LONGER_ACTIVE")
                write_atomic(receipt, {"token": message_id, "task": task, "actor": args.actor,
                                       "remote": args.remote, "branch": args.branch})
            pending.unlink(missing_ok=True)
        print(encoded(result), end="")
        return 0
    except (BusError, OSError, UnicodeError, KeyError, TypeError, ValueError) as exc:
        print(encoded({"error": str(exc)}), end="", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
