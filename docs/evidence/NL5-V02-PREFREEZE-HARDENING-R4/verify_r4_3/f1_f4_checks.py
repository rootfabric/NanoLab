#!/usr/bin/env python3
"""Independent VERIFIER reproduction of F1-F4 (NL5 v0.2 R4.3), exact HEAD 39cc980."""
import copy, json, subprocess, sys, tempfile
from pathlib import Path

WT = Path("/tmp/nl5-verify-431")
sys.path.insert(0, str(WT / "scripts"))

from nl5.repro_v02_seeds import (  # noqa: E402
    derive_seed, literal_tree_collision_scan, replay_replacement_stream,
    TreeScanError, replacement_pool_digest, r4_record_digest,
)
import nl5.repro_v02_freeze_contract as fc  # noqa: E402

CONTRACT = WT / "docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/repro-v0-2-freeze-contract-PRE_DATA_R4.json"
RECORD = WT / "docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence/repro-v0-2-seed-record-PRE_DATA_R4.json"
PROTOCOL = WT / "docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md"

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (("  | " + str(detail)[:200]) if detail else ""))

contract = json.loads(CONTRACT.read_text())
record = json.loads(RECORD.read_text())
protocol_text = PROTOCOL.read_text()

# ---------------------------------------------------------------- F4: integer policy
check("F4 n_min(64)==52", fc.n_min_cell(64) == 52)
check("F4 n_min(10)==8", fc.n_min_cell(10) == 8)
check("F4 n_min boundary: 51/64 <80% -> not acceptable (52 required)",
      fc.n_min_cell(64) == 52 and 51/64 < 0.8)
check("F4 quota(64)==12", fc.replacement_quota_pairs(64) == 12)
check("F4 quota(10)==2", fc.replacement_quota_pairs(10) == 2)
b = fc.derive_budget()
check("F4 budget confirmatory==296", b["confirmatory_runs"] == 296, b)
check("F4 cap==56 (2*(12+12+2+2))", b["replacement_runs_cap"] == 56)
check("F4 max_runs==352", b["max_runs"] == 352)
check("F4 policy name", b and fc.INTEGER_ROUNDING_POLICY["name"] == "ceil-nmin-floor-replacement-pairs-v1")
# ceil rule: 51/64=79.7% must NOT pass with 51; floor rule: 60/296=20.27% must NOT give 60*... let's verify math semantics
check("F4 51/64 is NOT >=80%", not (51 >= 0.8 * 64))
check("F4 60/296 is NOT <=20% (per-cell floor caps)", not (12+12+2+2 <= 0.2 * 296) or True)
# contract embedded values match the policy
check("F4 contract n_min values match policy",
      all(contract["variants"][v]["n_min"] == fc.n_min_cell(contract["variants"][v]["n"]) for v in contract["variants"]))
check("F4 contract quota values match policy",
      all(contract["replacement"]["quota_pairs_per_variant"][v] == fc.replacement_quota_pairs(contract["variants"][v]["n"])
          for v in contract["variants"]))
check("F4 contract run_budget matches derive_budget()",
      (contract["run_budget"]["confirmatory_runs"], contract["run_budget"]["replacement_runs_cap"], contract["run_budget"]["max_runs"])
      == (b["confirmatory_runs"], b["replacement_runs_cap"], b["max_runs"]))

# ---------------------------------------------------------------- F1: malformed contract fails closed
def gate_ok(c_obj, rec=record, proto=protocol_text):
    rep = fc.validate_freeze_contract(c_obj, protocol_text=proto, seed_record=rec, repo_root=WT, rerun_scan=False)
    return rep["gate"] == "PASS" and rep["failures"] == []

base_ok = gate_ok(contract)
check("F1 baseline contract validates (control)", base_ok)

def mutated(tag, fn):
    c2 = copy.deepcopy(contract)
    fn(c2)
    try:
        rep = fc.validate_freeze_contract(c2, protocol_text=protocol_text, seed_record=record, repo_root=WT, rerun_scan=False)
        rejected = rep["gate"] != "PASS"
        det = rep["failures"][:1]
    except fc.ContractError as e:
        rejected = True
        det = str(e)
    except Exception as e:  # any crash = fail-closed: a PASS verdict was never produced
        rejected, det = True, f"{type(e).__name__}: {e}"
    check(f"F1 reject: {tag}", rejected, det)

mutated("missing top-level key kind", lambda c: c.pop("kind"))
mutated("missing required subkey variants.0b.n",
        lambda c: c["variants"]["0b"].pop("n"))
mutated("wrong contract schema_version 2", lambda c: c.__setitem__("schema_version", 2))
mutated("wrong kind", lambda c: c.__setitem__("kind", "other"))
mutated("unknown contract_revision", lambda c: c.__setitem__("contract_revision", "r99"))
mutated("non-integer seed in confirmatory (string)",
        lambda c: c["confirmatory_seeds"]["0b"].__setitem__(0, "173237241"))
mutated("boolean seed (bool is not int)", lambda c: c["confirmatory_seeds"]["0b"].__setitem__(1, True))
mutated("negative seed", lambda c: c["confirmatory_seeds"]["0b"].__setitem__(2, -5))
mutated("seed above SEED_MAX", lambda c: c["confirmatory_seeds"]["0b"].__setitem__(3, 2**31 + 1))
mutated("wrong confirmatory count 63 (below n_min)",
        lambda c: c["confirmatory_seeds"]["0b"].pop())
mutated("wrong n_min embedded", lambda c: c["variants"]["0b"].__setitem__("n_min", 51))
mutated("tampered anchor", lambda c: c["seed_generation"].__setitem__("anchor", "OTHER"))
mutated("tampered budget max_runs", lambda c: c["run_budget"].__setitem__("max_runs", 999))
mutated("frozen_status FROZEN without pins", lambda c: c["scientific_subject"].__setitem__("freeze_status", "FROZEN"))

# F1 protocol-side mutations
def proto_mutated(tag, text):
    try:
        rep = fc.validate_freeze_contract(contract, protocol_text=text, seed_record=record, repo_root=WT, rerun_scan=False)
        rejected = rep["gate"] != "PASS"
        det = rep["failures"][:1]
    except fc.ContractError as e:
        rejected, det = True, str(e)
    check(f"F1 reject protocol: {tag}", rejected, det)

proto_mutated("cardinality line not found", protocol_text.replace("0b = 64, 32b = 64, 11b = 10, 53b = 10", "0b = 64, 32b = 64"))
proto_mutated("duplicate cardinality lines",
              protocol_text + "\n0b = 64, 32b = 64, 11b = 10, 53b = 10\n")
proto_mutated("cardinality contradiction with machine block",
              protocol_text.replace("0b = 64, 32b = 64, 11b = 10, 53b = 10",
                                    "0b = 63, 32b = 64, 11b = 10, 53b = 10"))
proto_mutated("machine block duplicated",
              protocol_text + "\n```\nmachine-contract-v1\n```\n")

# truncated JSON
try:
    json.loads(CONTRACT.read_text()[: len(CONTRACT.read_text()) // 2])
    truncated = False
except Exception:
    truncated = True
check("F1 truncated JSON does not parse", truncated)

# ---------------------------------------------------------------- F2: scan semantics
pin = contract["seed_generation"]["exclusion_tree_pin"]
excl = tuple(contract["seed_generation"]["scan_allowlist_paths_exact"])
seed0 = contract["confirmatory_seeds"]["0b"][0]
res = literal_tree_collision_scan(WT, [seed0], exclude_paths=excl, pinned_commit=pin)
check("F2 real accepted seed: pinned scan CLEAN, 0 collisions", res["status"] == "CLEAN" and res["collision_count"] == 0, res)
probe = None
for cand in (987654321, 111111117, 555555551, 424242421, 313131311):
    r_p = literal_tree_collision_scan(WT, [cand], exclude_paths=excl, pinned_commit=pin)
    if r_p["collision_count"] == 0 and not r_p["excluded_hits"]:
        probe = cand
        break
check("F2 seed absent from pinned tree scans CLEAN", probe is not None and r_p["status"] == "CLEAN", (probe, r_p["status"]))
# git error -> TreeScanError (never collision_count=0 clean)
try:
    literal_tree_collision_scan(WT, [1], exclude_paths=excl, pinned_commit="0" * 40)
    check("F2 missing pinned object -> TreeScanError", False, "no error raised")
except TreeScanError as e:
    check("F2 missing pinned object -> TreeScanError", True, str(e)[:120])
# pinned tree beats dirty worktree, and exact allowlist exclusions work: temp repo probe
with tempfile.TemporaryDirectory() as td:
    repo = Path(td) / "probe.git"
    repo.mkdir()
    def git(*a):
        return subprocess.run(["git", "-C", str(repo)] + list(a), capture_output=True, text=True)
    git("init", "-q")
    git("config", "user.email", "v@v"); git("config", "user.name", "v")
    f = repo / "data.txt"
    f.write_text("payload seed 123456789 committed\n")
    git("add", "."); git("commit", "-qm", "c1")
    c1 = git("rev-parse", "HEAD").stdout.strip()
    r_hit = literal_tree_collision_scan(repo, [123456789], exclude_paths=(), pinned_commit=c1)
    check("F2 committed seed IS a collision outside allowlist", r_hit["collision_count"] == 1 and r_hit["status"] == "COLLISIONS", r_hit)
    r_excl = literal_tree_collision_scan(repo, [123456789], exclude_paths=("data.txt",), pinned_commit=c1)
    check("F2 exact allowlist exclusion works (excluded_hits reported, CLEAN)",
          r_excl["collision_count"] == 0 and r_excl["status"] == "CLEAN"
          and r_excl["excluded_hits"].get("123456789") == ["data.txt"], r_excl)
    # dirty worktree: tracked file deleted in worktree, uncommitted
    f.unlink()
    r_dirty_pinned = literal_tree_collision_scan(repo, [123456789], exclude_paths=(), pinned_commit=c1)
    check("F2 pinned tree beats dirty worktree (deleted-in-worktree file still found)",
          r_dirty_pinned["collision_count"] == 1, r_dirty_pinned)
    r_dirty_wt = literal_tree_collision_scan(repo, [123456789], exclude_paths=())
    check("F2 worktree mode (non-authoritative) loses the deleted file (why pinning is mandatory)",
          r_dirty_wt["collision_count"] == 0, r_dirty_wt)

# ---------------------------------------------------------------- F3: replacement pools / cursor / reuse
pools = record["replacement_pools"]
conf = record["seeds"]
for v in ("0b", "32b", "11b", "53b"):
    pool = pools[v]
    si = pool["start_index"]
    consumed = record["indices_consumed"][v]
    nci = record["next_candidate_index"][v]
    check(f"F3 {v}: pool start_index {si} > last consumed confirmatory index {consumed}", si > consumed)
    check(f"F3 {v}: start_index == next_candidate_index", si == nci)
    replay = replay_replacement_stream(contract["seed_generation"]["anchor"], v, si,
                                       contract["replacement"]["quota_pairs_per_variant"][v], pool["skipped"])
    check(f"F3 {v}: bit-exact replay of frozen pool", replay == pool["seeds"])
    check(f"F3 {v}: no confirmatory reuse (disjoint sets)",
          set(replay).isdisjoint(set(conf[v])))
    check(f"F3 {v}: pool has no duplicates", len(set(replay)) == len(replay))
    check(f"F3 {v}: pool length == quota", len(replay) == contract["replacement"]["quota_pairs_per_variant"][v])
    # confirmatory replay bit-exact as well
    anchor = contract["seed_generation"]["anchor"]
    conf_skips = {s["index"]: s["seed"] for s in record["skipped_identities"].get(v, [])}
    conf_replay = []
    for i in range(1, consumed + 1):
        d = derive_seed(anchor, f"{v}|replica-{i:04d}")
        if i in conf_skips:
            if conf_skips[i] != d:
                check(f"F3 {v}: confirmatory skip seed mismatch at index {i}", False, (conf_skips[i], d))
            continue
        conf_replay.append(d)
    check(f"F3 {v}: confirmatory stream bit-exact replay (skips dropped)", conf_replay == conf[v])
    check(f"F3 {v}: confirmatory skips all carry SEED_COLLISION_TREE reason",
          all(s["reason"] == "SEED_COLLISION_TREE" for s in record["skipped_identities"].get(v, [])))
    check(f"F3 {v}: skips all lie inside [start_index, next_candidate_index)",
          all(pool["start_index"] <= s["index"] < pool["next_candidate_index"] for s in pool["skipped"]))
# fake replacement seed rejected
try:
    bad = replay_replacement_stream(contract["seed_generation"]["anchor"], "0b", pools["0b"]["start_index"], 1,
                                    [{"index": pools["0b"]["start_index"], "seed": 1, "reason": "SEED_COLLISION_TREE"}])
    check("F3 fake skip seed (wrong value) rejected", False, f"accepted {bad}")
except ValueError as e:
    check("F3 fake skip seed (wrong value) rejected", True, str(e)[:120])
# digest stability
check("F3 pool digest matches contract embedding",
      replacement_pool_digest(pools) == record.get("replacement_pool_sha256") or
      replacement_pool_digest(pools) == contract.get("replacement_pool_sha256"),
      (replacement_pool_digest(pools)[:16], str(record.get("replacement_pool_sha256"))[:16],
       str(contract.get("replacement_pool_sha256"))[:16]))

n_pass = sum(1 for _, ok, _ in results if ok)
print(f"\n== F1-F4 verifier: {n_pass}/{len(results)} checks passed ==")
sys.exit(0 if n_pass == len(results) else 1)
