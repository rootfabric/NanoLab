#!/usr/bin/env python3
"""Independent VERIFIER reproduction of R4.1 integrity/authority controls and
R4.2 M-6 transactional ledger state, exact HEAD 39cc980."""
import copy, json, subprocess, sys, tempfile
from pathlib import Path

WT = Path("/tmp/nl5-verify-431")
sys.path.insert(0, str(WT / "scripts"))

import nl5.repro_v02_freeze_contract as fc  # noqa: E402
from nl5.repro_v02_seeds import build_collision_scan_manifest  # noqa: E402

EV = WT / "docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence"
CONTRACT = EV / "repro-v0-2-freeze-contract-PRE_DATA_R4.json"
RECORD = EV / "repro-v0-2-seed-record-PRE_DATA_R4.json"
MANIFEST = EV / "r4-1-collision-scan-manifest-R4.json"
PROTOCOL = WT / "docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md"
PROTO_TEXT = PROTOCOL.read_text()
record = json.loads(RECORD.read_text())

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (("  | " + str(detail)[:220]) if detail else ""))

def gate_reject(name, fn, substr=None):
    """Rejected = exception OR gate report != PASS."""
    try:
        out = fn()
    except Exception as e:
        ok = (substr is None) or (substr in str(e))
        check(name, ok, f"{type(e).__name__}: {str(e)[:170]}")
        return
    ok = isinstance(out, dict) and out.get("gate") != "PASS"
    detail = out.get("failures", [str(out)])[:1] if isinstance(out, dict) else str(out)
    check(name, ok and (substr is None or substr in " ".join(out.get("failures", []))), detail)

def hard_reject(name, fn, substr=None):
    try:
        fn()
        check(name, False, "no exception raised")
    except Exception as e:
        ok = (substr is None) or (substr in str(e))
        check(name, ok, f"{type(e).__name__}: {str(e)[:170]}")

# ---------------- R4.1: PRE-DATA passes only PREFREEZE validation; no launch
contract = json.loads(CONTRACT.read_text())
rep = fc.validate_freeze_contract(contract, protocol_text=PROTO_TEXT,
                                  seed_record=record, repo_root=WT, rerun_scan=False)
check("R4.1 PRE-DATA gate PASS", rep["gate"] == "PASS")
check("R4.1 PRE-DATA stage == PREFREEZE_VALIDATION_PASS", rep["validation_stage"] == "PREFREEZE_VALIDATION_PASS")
check("R4.1 PRE-DATA dispatch == DISPATCH_BLOCKED", rep["dispatch"] == "DISPATCH_BLOCKED")
check("R4.1 PRE-DATA freeze_status NOT_FROZEN", rep["freeze_status"] == "NOT_FROZEN")

hard_reject("R4.1 PRE-DATA plan refused (missing authority)",
            lambda: fc.build_execution_plan(CONTRACT, PROTOCOL, RECORD, repo_root=WT),
            "DISPATCH_BLOCKED")
fake_auth = {"schema_version": 3, "kind": "nanolab_v02_dispatch_authority"}
hard_reject("R4.1 garbage authority rejected",
            lambda: fc.validate_dispatch_authority(fake_auth, contract, PROTO_TEXT, record,
                                                   repo_root=WT, contract_path=CONTRACT),
            "rejected")
env = {"PYTHONPATH": str(WT / "scripts"), "PATH": "/usr/bin:/bin"}
p = subprocess.run([sys.executable, "-m", "nl5.repro_v02_freeze_contract", "plan",
                    "--contract", str(CONTRACT), "--protocol", str(PROTOCOL),
                    "--record", str(RECORD), "--repo-root", ".",
                    "--authority", str(EV / "r4-dispatch-plan-PRE_DATA_R4.json")],
                   cwd=WT, env=env, capture_output=True, text=True)
check("R4.1 CLI plan on PRE-DATA exits 3 (blocked, not authorized)", p.returncode == 3,
      (p.stdout or p.stderr)[:160])
try:
    out = json.loads(p.stdout)
    check("R4.1 CLI plan refusal carries no launch flag",
          "machine_launch_authorized" not in out and out.get("gate") == "FREEZE_GATE_FAIL", out)
except Exception as e:
    check("R4.1 CLI plan refusal carries no launch flag", False, e)

tampered = copy.deepcopy(contract); tampered["rule_id"] = "TAMPERED"
tpath = Path(tempfile.mkdtemp()) / "t.json"; tpath.write_text(json.dumps(tampered))
p2 = subprocess.run([sys.executable, "-m", "nl5.repro_v02_freeze_contract", "prefreeze",
                     "--contract", str(tpath), "--protocol", str(PROTOCOL),
                     "--record", str(RECORD), "--repo-root", ".", "--no-scan-rerun"],
                    cwd=WT, env=env, capture_output=True, text=True)
check("R4.1 CLI prefreeze on tampered contract exits 3", p2.returncode == 3, p2.stdout[:120])

# ---------------- R4.1: manifest/path/digest binding tampering rejected
gate_reject("R4.1 tampered manifest digest in contract rejected",
            lambda: fc.validate_freeze_contract({**contract, "collision_scan_manifest": {
                "path": contract["collision_scan_manifest"]["path"], "sha256": "0" * 64}},
                protocol_text=PROTO_TEXT, seed_record=record, repo_root=WT, rerun_scan=False),
            "bound sha256")
gate_reject("R4.1 tampered manifest path rejected (points at non-manifest file)",
            lambda: fc.validate_freeze_contract({**contract, "collision_scan_manifest": {
                "path": "docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md",
                "sha256": contract["collision_scan_manifest"]["sha256"]}},
                protocol_text=PROTO_TEXT, seed_record=record, repo_root=WT, rerun_scan=False))
manifest = json.loads(MANIFEST.read_text())
fails = []
from nl5.repro_v02_seeds import verify_collision_manifest
verify_collision_manifest(contract, manifest, fails, record=record, rerun_root=None)
check("R4.1 untampered manifest verifies (control, structural+digest)", not fails, fails[:2])
m_t = copy.deepcopy(manifest); m_t["allowlist_paths_exact"] = ["evil"]
fails2 = []
verify_collision_manifest(contract, m_t, fails2, record=record)
check("R4.1 tampered manifest allowlist rejected", bool(fails2), fails2[:2])
# fake collision skip (recorded skip whose seed scans CLEAN at the pinned tree) -> fail closed
pools = {v: record["replacement_pools"][v] for v in ("0b", "32b", "11b", "53b")}
sk = copy.deepcopy(record["skipped_identities"])
sk["0b"] = sk["0b"] + [{"index": 424242, "seed": 2147483000, "reason": "SEED_COLLISION_TREE"}]
hard_reject("R4.1 fake collision skip rejected by manifest build (scans CLEAN -> error)",
            lambda: build_collision_scan_manifest(
                WT, contract["seed_generation"]["exclusion_tree_pin"],
                list(contract["seed_generation"]["scan_allowlist_paths_exact"]),
                contract["confirmatory_seeds"], pools, sk))

# ---------------- R4.2 M-6: transactional ledger
# p1 owns a CONFIRMATORY seed (999) outside the replacement pool [111, 222]
L = fc.ReplacementLedger({"0b": 2}, {"0b": [111, 222]})
L.open_pair("p1", "0b", 999)
snap0 = L.state_snapshot()
hard_reject("M-6 duplicate pair id rejected", lambda: L.open_pair("p1", "0b", 123), "already exists")
hard_reject("M-6 unknown variant rejected", lambda: L.open_pair("px", "99b", 333), "unknown variant")
hard_reject("M-6 replacement on unknown pair rejected",
            lambda: L.request_replacement("0b", "nope", "p9", "a1", "e1"), "unknown pair")
check("M-6 state unchanged after early rejects", L.state_snapshot() == snap0)

snap1 = L.state_snapshot()
hard_reject("M-6 author attempt with SCHEDULED outcome rejected",
            lambda: L.record_attempt("p1-a", "p1", "author", "SCHEDULED"), "SCHEDULED")
hard_reject("M-6 invalid attempt id format",
            lambda: L.record_attempt("bad id!", "p1", "author", "COMPLETED"), "attempt id rule")
check("M-6 state unchanged after attempt rejects", L.state_snapshot() == snap1)
L.record_attempt("p1-a", "p1", "author", "FAILED_TECHNICAL")
snap1b = L.state_snapshot()
hard_reject("M-6 duplicate author leg binding",
            lambda: L.record_attempt("tmp-a2", "p1", "author", "COMPLETED"), "already binds its author leg")
check("M-6 state unchanged after duplicate-leg reject", L.state_snapshot() == snap1b)
snap2 = L.state_snapshot()
hard_reject("M-6 replacement refused while pair incomplete",
            lambda: L.request_replacement("0b", "p1", "p2", "p2-a", "p2-e"), "not terminal")
check("M-6 state unchanged after incomplete-pair reject", L.state_snapshot() == snap2)
L.record_attempt("p1-e", "p1", "external", "FAILED_TECHNICAL")
check("M-6 both legs failed -> PAIR_FAILED_TECHNICAL", L.pair_state("p1") == "PAIR_FAILED_TECHNICAL")

identity = L.request_replacement("0b", "p1", "p2", "p2-a", "p2-e")
check("M-6 replacement consumed next pool identity in order", identity == 111 and L.pool_cursor("0b") == 1)
check("M-6 replacement pair has both SCHEDULED legs",
      L.pair("p2")["legs"] == {"author": "p2-a", "external": "p2-e"})
snap3 = L.state_snapshot()
hard_reject("M-6 second replacement for same failed pair rejected",
            lambda: L.request_replacement("0b", "p1", "p3", "p3-a", "p3-e"), "single replacement assignment")
check("M-6 state unchanged after one-shot violation", L.state_snapshot() == snap3)

# p3: another failed pair for attempt-id / pair-id rejections (owns 888, outside pool)
L.open_pair("p3", "0b", 888)
L.record_attempt("p3-a", "p3", "author", "FAILED_TECHNICAL")
L.record_attempt("p3-e", "p3", "external", "FAILED_TECHNICAL")
snap4 = L.state_snapshot()
hard_reject("M-6 duplicate author attempt id across pairs",
            lambda: L.request_replacement("0b", "p3", "p9", "p2-a", "x-e"), "globally unique")
hard_reject("M-6 duplicate external attempt id across pairs",
            lambda: L.request_replacement("0b", "p3", "p9", "x-a", "p2-e"), "globally unique")
hard_reject("M-6 invalid external attempt id",
            lambda: L.request_replacement("0b", "p3", "p9", "x-a", "bad e!"), "attempt id rule")
hard_reject("M-6 author/external attempt id collision",
            lambda: L.request_replacement("0b", "p3", "p9", "same", "same"), "distinct")
hard_reject("M-6 duplicate replacement pair id via request_replacement",
            lambda: L.request_replacement("0b", "p3", "p2", "p7-a", "p7-e"), "already exists")
hard_reject("M-6 replacement seed already owned (open_pair)",
            lambda: L.open_pair("p-owned", "0b", 111), "already belongs to pair")
check("M-6 state unchanged after all attempt-id/pair-id/seed rejects", L.state_snapshot() == snap4)

# forced second-leg binding failure DURING commit -> full rollback
L2 = fc.ReplacementLedger({"0b": 2}, {"0b": [22, 33]})
L2.open_pair("q1", "0b", 11)
L2.record_attempt("q1-a", "q1", "author", "FAILED_TECHNICAL")
L2.record_attempt("q1-e", "q1", "external", "FAILED_TECHNICAL")
snapL2 = L2.state_snapshot()
orig_bind = L2._bind_attempt
calls = {"n": 0}
def failing_bind(attempt_id, pair_id, leg, outcome, allow_scheduled):
    calls["n"] += 1
    if calls["n"] == 2:
        raise RuntimeError("forced second-leg binding failure")
    return orig_bind(attempt_id, pair_id, leg, outcome, allow_scheduled)
L2._bind_attempt = failing_bind
try:
    L2.request_replacement("0b", "q1", "q2", "q2-a", "q2-e")
    check("M-6 forced second-leg failure raised", False, "no exception")
except RuntimeError as e:
    check("M-6 forced second-leg failure raised", "forced" in str(e))
check("M-6 rollback restores state bit-for-bit after mid-commit failure",
      L2.state_snapshot() == snapL2)
check("M-6 cursor/quota untouched after rollback", L2.pool_cursor("0b") == 0 and L2.used_pairs("0b") == 0)
identity2 = L2.request_replacement("0b", "q1", "q2", "q2-a", "q2-e")
check("M-6 retry after rollback succeeds atomically", identity2 == 22 and L2.pool_cursor("0b") == 1)

# quota exhaustion is honest
L3 = fc.ReplacementLedger({"0b": 1}, {"0b": [22]})
L3.open_pair("r1", "0b", 21)
L3.record_attempt("r1-a", "r1", "author", "FAILED_TECHNICAL")
L3.record_attempt("r1-e", "r1", "external", "FAILED_TECHNICAL")
L3.request_replacement("0b", "r1", "r2", "r2-a", "r2-e")
L3.record_outcome("r2-a", "FAILED_TECHNICAL"); L3.record_outcome("r2-e", "FAILED_TECHNICAL")
hard_reject("M-6/F3 quota exhausted -> ReplacementBudgetExhausted",
            lambda: L3.request_replacement("0b", "r2", "r3", "r3-a", "r3-e"), "exhausted")

# public snapshot isolation
snap = L.state_snapshot()
snap["pairs"]["p1"]["legs"]["author"] = "TAMPERED"
snap["attempts"]["p1-a"]["outcome"] = "TAMPERED"
snap["ledger"].append({"event": "FAKE"})
snap["pool_cursor"]["0b"] = 99
check("M-6 public state_snapshot is isolated (mutations never reach ledger)",
      L.pair("p1")["legs"]["author"] != "TAMPERED" and L.pool_cursor("0b") != 99
      and all(ev.get("event") != "FAKE" for ev in L.ledger))
led = L.ledger; led[0]["event"] = "TAMPERED"
check("M-6 public ledger property is isolated", L.ledger[0]["event"] != "TAMPERED")
pr = L.pair("p1"); pr["legs"]["external"] = "TAMPERED"
check("M-6 public pair() view is isolated (m-2)", L.pair("p1")["legs"]["external"] != "TAMPERED")
check("M-6 pool consumed strictly in order (no outcome-driven selection)",
      L.pool_cursor("0b") == 1 and L2.pool_cursor("0b") == 1)

n_pass = sum(1 for _, ok, _ in results if ok)
print(f"\n== R4.1/R4.2 verifier: {n_pass}/{len(results)} checks passed ==")
sys.exit(0 if n_pass == len(results) else 1)
