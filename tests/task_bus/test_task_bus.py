"""Executable protocol tests; scripted roles are NOT independent AI review."""
from concurrent.futures import ThreadPoolExecutor
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/task_bus.py"
module_spec = importlib.util.spec_from_file_location("task_bus", TOOL)
busmod = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(busmod)


def policy():
    return {"mode": "SANDBOX", "lease_seconds": 60, "max_claims": 16, "max_repairs": 2,
            "actors": {"director-pilot": {"role": "DIRECTOR", "capabilities": ["control"]},
                       "implementer-a": {"role": "IMPLEMENTER", "capabilities": ["json"]},
                       "implementer-b": {"role": "IMPLEMENTER", "capabilities": ["json"]},
                       "reviewer-a": {"role": "REVIEWER", "capabilities": ["review"]},
                       "verifier-a": {"role": "VERIFIER", "capabilities": ["python"]}}}


def spec(base="a" * 40, tid="BUS-SMOKE-001", deps=None):
    return {"id": tid, "kind": "PILOT", "claim_class": "C0_SOFTWARE_ONLY", "base_sha": base,
            "goal": "Check distributed handoff, not scientific validity", "depends_on": deps or [],
            "allowed_paths": [f"docs/work/pilots/{tid}/receipt.json"],
            "capabilities": {"IMPLEMENTER": ["json"], "REVIEWER": ["review"],
                             "VERIFIER": ["python"], "DIRECTOR": ["control"]}}


def subject():
    return {"head": "b" * 40, "tree": "c" * 40, "ref": "work/bus-smoke-001-r1"}


def report(s=None, verdict="PASS"):
    s = s or subject()
    return {"subject_head": s["head"], "subject_tree": s["tree"], "verdict": verdict,
            "summary": "Scripted protocol fixture, not independent review",
            "checks": [{"command": "scripted fixture assertion", "exit_code": 0 if verdict == "PASS" else 1}]}


class ReducerTests(unittest.TestCase):
    def setUp(self):
        self.doc = {"schema_version": 1, "policy": policy(), "events": []}
        self.seq, self.at = 0, 1000
        self.send("director-pilot", "open", spec())

    def send(self, actor, op, data=None, tid="BUS-SMOKE-001", event_id=None):
        self.seq += 1
        self.at += 1
        event = {"id": event_id or f"event-{self.seq}", "actor": actor, "op": op,
                 "task": tid, "at": self.at, "data": data or {}}
        self.doc, tasks, duplicate = busmod.append(self.doc, event)
        return tasks[tid], event, duplicate

    def claim(self, actor="implementer-a"):
        task, event, _ = self.send(actor, "claim")
        return event["id"]

    def finish(self, actor, token, verdict="PASS", s=None):
        data = {"token": token, "report": report(s, verdict)}
        if actor.startswith("implementer"):
            data["subject"] = s or subject()
        return self.send(actor, "finish", data)[0]

    def implemented(self):
        self.finish("implementer-a", self.claim())

    def test_full_four_role_cycle_is_only_sandbox_complete(self):
        self.implemented()
        for actor in ("reviewer-a", "verifier-a", "director-pilot"):
            task = self.finish(actor, self.claim(actor))
        self.assertEqual(task["phase"], "COMPLETED_SANDBOX")
        self.assertEqual(len(set(task["approvals"].values())), 4)
        self.assertEqual(len(self.doc["events"]), 9)

    def test_competing_claim_is_denied(self):
        self.claim()
        with self.assertRaisesRegex(busmod.BusError, "NOT_CLAIMABLE"):
            self.claim("implementer-b")

    def test_wrong_role_cannot_claim(self):
        with self.assertRaisesRegex(busmod.BusError, "NOT_CLAIMABLE"):
            self.claim("reviewer-a")

    def test_unknown_actor_denied(self):
        with self.assertRaisesRegex(busmod.BusError, "ACTOR_NOT_ALLOWED"):
            self.claim("stranger")

    def test_capability_filter_enforced(self):
        self.doc["policy"]["actors"]["implementer-b"]["capabilities"] = []
        with self.assertRaisesRegex(busmod.BusError, "CAPABILITY_MISMATCH"):
            self.claim("implementer-b")

    def test_expired_lease_requires_director_reclaim(self):
        old = self.claim()
        self.at += 61
        with self.assertRaisesRegex(busmod.BusError, "LEASE_EXPIRED"):
            self.finish("implementer-a", old)
        with self.assertRaisesRegex(busmod.BusError, "NOT_CLAIMABLE"):
            self.claim("implementer-b")
        self.send("director-pilot", "reclaim", {"reason": "Owner disappeared"})
        self.claim("implementer-b")
        with self.assertRaisesRegex(busmod.BusError, "STALE_OR_FOREIGN"):
            self.finish("implementer-a", old)

    def test_early_or_worker_reclaim_denied(self):
        self.claim()
        with self.assertRaisesRegex(busmod.BusError, "LEASE_NOT_EXPIRED"):
            self.send("director-pilot", "reclaim", {"reason": "Too early"})
        with self.assertRaisesRegex(busmod.BusError, "DIRECTOR_REASON"):
            self.send("implementer-b", "reclaim", {"reason": "Not director"})

    def test_heartbeat_extends_current_lease(self):
        token = self.claim()
        before = busmod.replay(self.doc)["BUS-SMOKE-001"]["lease"]["until"]
        self.at += 20
        task, _, _ = self.send("implementer-a", "heartbeat", {"token": token})
        self.assertGreater(task["lease"]["until"], before)

    def test_release_fences_old_token(self):
        token = self.claim()
        self.send("implementer-a", "release", {"token": token, "reason": "Yield"})
        self.claim()
        with self.assertRaisesRegex(busmod.BusError, "STALE_OR_FOREIGN"):
            self.finish("implementer-a", token)

    def test_idempotent_replay_preserves_original_receipt(self):
        self.claim()
        old = copy.deepcopy(self.doc["events"][-1])
        old["at"] += 1000
        document, tasks, duplicate = busmod.append(self.doc, old)
        self.assertTrue(duplicate)
        self.assertEqual(len(document["events"]), 2)
        self.assertEqual(tasks["BUS-SMOKE-001"]["claims"], 1)

    def test_idempotency_collision_denied(self):
        self.claim()
        old = copy.deepcopy(self.doc["events"][-1])
        old["actor"] = "implementer-b"
        with self.assertRaisesRegex(busmod.BusError, "IDEMPOTENCY_KEY_COLLISION"):
            busmod.append(self.doc, old)

    def test_review_cannot_change_subject(self):
        self.implemented()
        token = self.claim("reviewer-a")
        wrong = subject()
        wrong["head"] = "d" * 40
        with self.assertRaisesRegex(busmod.BusError, "SUBJECT_MISMATCH"):
            self.finish("reviewer-a", token, s=wrong)

    def test_repair_clears_approvals_but_preserves_failure(self):
        self.implemented()
        task = self.finish("reviewer-a", self.claim("reviewer-a"), "FAIL")
        self.assertEqual(task["phase"], "IMPLEMENTER")
        self.assertEqual(task["approvals"], {})
        self.assertIsNone(task["subject"])
        self.assertIn('"FAIL"', busmod.encoded(self.doc))
        self.implemented()
        self.assertEqual(busmod.replay(self.doc)["BUS-SMOKE-001"]["phase"], "REVIEWER")

    def test_insufficient_evidence_blocks_and_resumes_same_role(self):
        self.implemented()
        task = self.finish("reviewer-a", self.claim("reviewer-a"), "INSUFFICIENT_EVIDENCE")
        self.assertEqual(task["phase"], "BLOCKED")
        task, _, _ = self.send("director-pilot", "resume", {"reason": "Missing evidence is available"})
        self.assertEqual(task["phase"], "REVIEWER")

    def test_director_invalidates_stale_candidate(self):
        self.implemented()
        token = self.claim("reviewer-a")
        task, _, _ = self.send("director-pilot", "invalidate", {"reason": "Candidate branch moved"})
        self.assertEqual(task["phase"], "IMPLEMENTER")
        with self.assertRaisesRegex(busmod.BusError, "STALE_OR_FOREIGN"):
            self.finish("reviewer-a", token)

    def test_block_resume_and_cancel(self):
        token = self.claim()
        self.send("implementer-a", "block", {"token": token, "reason": "Environment unavailable"})
        self.send("director-pilot", "resume", {"reason": "Environment restored"})
        task, _, _ = self.send("director-pilot", "cancel", {"reason": "Budget withdrawn"})
        self.assertEqual(task["phase"], "CANCELLED")
        with self.assertRaisesRegex(busmod.BusError, "TASK_TERMINAL"):
            self.claim()

    def test_failed_command_cannot_have_pass_verdict(self):
        token = self.claim()
        bad = report()
        bad["checks"][0]["exit_code"] = 1
        with self.assertRaisesRegex(busmod.BusError, "PASS_WITH_FAILED_CHECK"):
            self.send("implementer-a", "finish", {"token": token, "report": bad, "subject": subject()})

    def test_repair_budget_is_enforced(self):
        self.doc["policy"]["max_repairs"] = 0
        self.implemented()
        with self.assertRaisesRegex(busmod.BusError, "REPAIR_BUDGET_EXHAUSTED"):
            self.finish("reviewer-a", self.claim("reviewer-a"), "FAIL")

    def test_claim_budget_is_enforced(self):
        self.doc["policy"]["max_claims"] = 4
        for _ in range(4):
            token = self.claim()
            self.send("implementer-a", "release", {"token": token, "reason": "Yield"})
        with self.assertRaisesRegex(busmod.BusError, "CLAIM_BUDGET_EXHAUSTED"):
            self.claim()

    def test_dependency_must_exist_and_complete(self):
        new = spec(tid="BUS-DEPENDENT", deps=["BUS-SMOKE-001"])
        self.send("director-pilot", "open", new, tid=new["id"])
        with self.assertRaisesRegex(busmod.BusError, "DEPENDENCY_NOT_COMPLETE"):
            self.send("implementer-a", "claim", tid=new["id"])
        missing = spec(tid="BUS-MISSING", deps=["BUS-NOPE"])
        with self.assertRaisesRegex(busmod.BusError, "DEPENDENCY_MUST_ALREADY_EXIST"):
            self.send("director-pilot", "open", missing, tid=missing["id"])

    def test_scientific_tasks_and_broad_scopes_are_rejected(self):
        for change in ({"id": "NL0-003"}, {"allowed_paths": ["project/state.json"]},
                       {"allowed_paths": ["docs/work/pilots/BUS-OTHER/../state.json"]},
                       {"claim_class": "C1_COMPUTATIONAL_REPRODUCTION"}):
            new = spec(tid="BUS-OTHER")
            new.update(change)
            with self.assertRaises(busmod.BusError):
                self.send("director-pilot", "open", new, tid=new["id"])

    def test_nonmonotonic_history_and_duplicate_ids_rejected(self):
        broken = copy.deepcopy(self.doc)
        broken["events"].append(copy.deepcopy(broken["events"][0]))
        with self.assertRaisesRegex(busmod.BusError, "DUPLICATE_EVENT_ID"):
            busmod.replay(broken)
        self.claim()
        broken = copy.deepcopy(self.doc)
        broken["events"][-1]["at"] = 1
        with self.assertRaisesRegex(busmod.BusError, "NONMONOTONIC_EVENT_TIME"):
            busmod.replay(broken)

    def test_json_ambiguities_rejected(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '[]', 'null', '{"x":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(busmod.BusError):
                busmod.decode(raw)

    def test_no_self_acceptance_or_skipped_stages(self):
        self.implemented()
        with self.assertRaisesRegex(busmod.BusError, "NOT_CLAIMABLE"):
            self.claim("director-pilot")
        with self.assertRaisesRegex(busmod.BusError, "NOT_CLAIMABLE"):
            self.claim("implementer-a")


class GitIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="nanolab-bus-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.run_git(self.root, "init", "--bare", "--initial-branch=main", str(self.remote))
        self.seed = self.root / "seed"
        self.run_git(self.root, "clone", str(self.remote), str(self.seed))
        self.configure(self.seed)
        (self.seed / "README.md").write_text("Synthetic test repository; not NanoLab main.\n")
        self.run_git(self.seed, "add", ".")
        self.run_git(self.seed, "commit", "-m", "test: seed")
        self.run_git(self.seed, "push", "origin", "main")
        self.base = self.run_git(self.seed, "rev-parse", "HEAD")
        self.repos = {}
        for actor in policy()["actors"]:
            repo = self.root / actor
            self.run_git(self.root, "clone", str(self.remote), str(repo))
            self.configure(repo)
            self.repos[actor] = repo
        self.director = self.client("director-pilot")
        self.director.initialize({"schema_version": 1, "policy": policy(), "events": []}, self.base)
        self.director.transact("director-pilot", "open", "BUS-SMOKE-001", spec(self.base), "open-smoke")

    @staticmethod
    def run_git(cwd, *args):
        p = subprocess.run(["git", "-C", str(cwd), *args], text=True, capture_output=True, timeout=20)
        if p.returncode:
            raise AssertionError(p.stderr)
        return p.stdout.rstrip("\n")

    def configure(self, repo):
        self.run_git(repo, "config", "user.name", "Synthetic Role")
        self.run_git(repo, "config", "user.email", "synthetic@example.invalid")

    def client(self, actor):
        return busmod.GitBus(self.repos[actor])

    def make_candidate(self, extra=None):
        repo = self.seed
        self.run_git(repo, "checkout", "-b", "work/bus-smoke-001-r1", self.base)
        path = repo / "docs/work/pilots/BUS-SMOKE-001/receipt.json"
        path.parent.mkdir(parents=True)
        path.write_text(busmod.encoded({"schema_version": 1, "task_id": "BUS-SMOKE-001",
                                       "message": "NanoLab distributed workflow smoke", "values": [1, 2, 3],
                                       "sum": 6, "scientific_claim": False}), encoding="utf-8")
        if extra:
            p = repo / extra
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("out of scope")
        self.run_git(repo, "add", ".")
        self.run_git(repo, "commit", "-m", "test: formal receipt")
        self.run_git(repo, "push", "origin", "HEAD")
        return {"head": self.run_git(repo, "rev-parse", "HEAD"),
                "tree": self.run_git(repo, "rev-parse", "HEAD^{tree}"), "ref": "work/bus-smoke-001-r1"}

    def test_independent_clones_full_cycle_and_main_untouched(self):
        s = self.make_candidate()
        self.assertEqual(busmod.smoke_check(self.seed)["verdict"], "PASS")
        for actor in ("implementer-a", "reviewer-a", "verifier-a", "director-pilot"):
            client = self.client(actor)
            claim = client.transact(actor, "claim", "BUS-SMOKE-001", {})
            data = {"token": claim["event"]["id"], "report": report(s)}
            if actor == "implementer-a":
                data["subject"] = s
            result = client.transact(actor, "finish", "BUS-SMOKE-001", data)
        self.assertEqual(result["task"]["phase"], "COMPLETED_SANDBOX")
        self.assertEqual(self.run_git(self.remote, "rev-parse", "main"), self.base)
        self.assertFalse(self.client("director-pilot").inbox("director-pilot")["canonical_acceptance"])

    def race(self, items):
        barrier = threading.Barrier(len(items))
        def run(item):
            actor, task = item
            client, first = self.client(actor), True
            original = client.push
            def synchronized_push(head):
                nonlocal first
                if first:
                    first = False
                    barrier.wait(timeout=20)
                original(head)
            client.push = synchronized_push
            try:
                return client.transact(actor, "claim", task, {}, "claim-" + actor)
            except busmod.BusError as exc:
                return str(exc)
        with ThreadPoolExecutor(max_workers=len(items)) as pool:
            return list(pool.map(run, items))

    def test_actual_concurrent_claim_has_exactly_one_winner(self):
        results = self.race([("implementer-a", "BUS-SMOKE-001"), ("implementer-b", "BUS-SMOKE-001")])
        self.assertEqual(sum(isinstance(r, dict) for r in results), 1, results)
        _, doc = self.director.load()
        self.assertEqual(sum(e["op"] == "claim" for e in doc["events"]), 1)

    def test_concurrent_different_tasks_retry_without_losing_events(self):
        self.director.transact("director-pilot", "open", "BUS-SECOND", spec(self.base, "BUS-SECOND"))
        results = self.race([("implementer-a", "BUS-SMOKE-001"), ("implementer-b", "BUS-SECOND")])
        self.assertTrue(all(isinstance(r, dict) for r in results), results)
        _, doc = self.director.load()
        self.assertEqual(len(doc["events"]), 4)

    def test_lost_push_ack_is_recovered_without_duplicate(self):
        client = self.client("implementer-a")
        original = client.push
        def lost_ack(head):
            original(head)
            raise busmod.BusError("Simulated response loss after successful push")
        client.push = lost_ack
        result = client.transact("implementer-a", "claim", "BUS-SMOKE-001", {}, "lost-ack")
        self.assertTrue(result["duplicate"])
        _, doc = self.director.load()
        self.assertEqual(len(doc["events"]), 2)

    def test_lost_ack_at_final_attempt_is_recovered(self):
        client = self.client("implementer-a")
        original = client.push
        def lost_ack(head):
            original(head)
            raise busmod.BusError("Simulated lost ACK")
        client.push = lost_ack
        result = client.transact("implementer-a", "claim", "BUS-SMOKE-001", {}, "last-ack", attempts=1)
        self.assertTrue(result["duplicate"])

    def test_drifted_remote_ref_blocks_handoff(self):
        s = self.make_candidate()
        client = self.client("implementer-a")
        token = client.transact("implementer-a", "claim", "BUS-SMOKE-001", {})["event"]["id"]
        self.run_git(self.seed, "commit", "--allow-empty", "-m", "test: drift")
        self.run_git(self.seed, "push", "origin", "HEAD")
        with self.assertRaisesRegex(busmod.BusError, "CANDIDATE_REF_DRIFT"):
            client.transact("implementer-a", "finish", "BUS-SMOKE-001", {"token": token, "subject": s, "report": report(s)})
        self.assertEqual(len(self.director.load()[1]["events"]), 2)

    def test_wrong_tree_is_rejected(self):
        s = self.make_candidate()
        s["tree"] = "f" * 40
        with self.assertRaisesRegex(busmod.BusError, "CANDIDATE_TREE_MISMATCH"):
            self.director.check_subject(s, spec(self.base))

    def test_out_of_scope_change_rejected(self):
        s = self.make_candidate("project/state.json")
        with self.assertRaisesRegex(busmod.BusError, "CANDIDATE_OUT_OF_SCOPE"):
            self.director.check_subject(s, spec(self.base))

    def test_whitespace_filename_cannot_bypass_scope(self):
        s = self.make_candidate(" docs/work/pilots/BUS-SMOKE-001/receipt.json")
        with self.assertRaisesRegex(busmod.BusError, "CANDIDATE_OUT_OF_SCOPE"):
            self.director.check_subject(s, spec(self.base))

    def test_symlink_candidate_and_local_smoke_are_rejected(self):
        s = self.make_candidate()
        path = self.seed / "docs/work/pilots/BUS-SMOKE-001/receipt.json"
        path.unlink()
        try:
            path.symlink_to("../../../../README.md")
        except OSError:
            self.skipTest("Platform does not permit unprivileged symlinks")
        with self.assertRaisesRegex(busmod.BusError, "SMOKE_SYMLINK_DENIED"):
            busmod.smoke_check(self.seed)
        self.run_git(self.seed, "add", ".")
        self.run_git(self.seed, "commit", "-m", "test: symlink negative control")
        self.run_git(self.seed, "push", "origin", "HEAD")
        s.update(head=self.run_git(self.seed, "rev-parse", "HEAD"),
                 tree=self.run_git(self.seed, "rev-parse", "HEAD^{tree}"))
        with self.assertRaisesRegex(busmod.BusError, "REGULAR_DATA_FILES"):
            self.director.check_subject(s, spec(self.base))

    def test_inherited_git_directory_cannot_redirect_bus_writes(self):
        with patch.dict(os.environ, {"GIT_DIR": str(self.root / "does-not-exist"),
                                    "GIT_WORK_TREE": str(self.seed)}):
            result = self.client("implementer-a").transact("implementer-a", "claim", "BUS-SMOKE-001", {})
        self.assertTrue(result["committed"])

    def test_dirty_worktree_and_index_are_preserved(self):
        repo = self.repos["implementer-a"]
        (repo / "README.md").write_text("staged unrelated work")
        self.run_git(repo, "add", "README.md")
        (repo / "README.md").write_text("unstaged unrelated work")
        before = self.run_git(repo, "status", "--porcelain")
        cached = self.run_git(repo, "diff", "--cached")
        self.client("implementer-a").transact("implementer-a", "claim", "BUS-SMOKE-001", {})
        self.assertEqual(self.run_git(repo, "status", "--porcelain"), before)
        self.assertEqual(self.run_git(repo, "diff", "--cached"), cached)

    def test_cli_claim_receipt_and_idempotent_retry(self):
        command = [sys.executable, str(TOOL), "--repo", str(self.repos["implementer-a"]),
                   "--actor", "implementer-a", "--message-id", "cli-claim", "claim", "BUS-SMOKE-001"]
        for duplicate in (False, True):
            p = subprocess.run(command, text=True, capture_output=True, timeout=30)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["duplicate"], duplicate)
        receipt = self.repos["implementer-a"] / ".git/task-bus-receipts/implementer-a/BUS-SMOKE-001.json"
        self.assertEqual(json.loads(receipt.read_text())["token"], "cli-claim")

    def test_duplicate_init_is_rejected(self):
        with self.assertRaisesRegex(busmod.BusError, "BUS_ALREADY_EXISTS"):
            self.director.initialize({"schema_version": 1, "policy": policy(), "events": []}, self.base)

    def test_main_cannot_be_used_as_bus_branch(self):
        with self.assertRaisesRegex(busmod.BusError, "DEDICATED_BUS_BRANCH_REQUIRED"):
            busmod.GitBus(self.seed, branch="main")

    def test_smoke_negative_control_and_strict_boolean_types(self):
        self.make_candidate()
        path = self.seed / "docs/work/pilots/BUS-SMOKE-001/receipt.json"
        expected = json.loads(path.read_text())
        for key, value in (("sum", 7), ("scientific_claim", 0), ("schema_version", True)):
            bad = dict(expected)
            bad[key] = value
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(busmod.BusError, "SMOKE_CONTRACT_MISMATCH"):
                busmod.smoke_check(self.seed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
