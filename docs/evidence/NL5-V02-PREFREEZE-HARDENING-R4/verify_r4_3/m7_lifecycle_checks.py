#!/usr/bin/env python3
"""Independent VERIFIER reproduction of the R4.3 M-7 schema v3 lifecycle
S -> F -> R/V -> A in a REAL temporary Git repository (exact HEAD 39cc980).

Positive: subject_head == F, subject_tree == tree(F), frozen artifacts are
exact blobs of F, reviewed/verified head/tree == F/tree(F), record source
commits strictly descend from F, status == DISPATCH_PRECONDITIONS_RECORDED,
machine_launch_authorized == false, launch_gate == HUMAN_PROTECTED_WRITER.

Negative controls: every mutation must be rejected with ContractError and
must never yield a plan, DISPATCH_AUTHORIZED or machine_launch_authorized
true.
"""
import copy, hashlib, json, subprocess, sys, tempfile
from pathlib import Path

WT = Path("/tmp/nl5-verify-431")
sys.path.insert(0, str(WT / "scripts"))

import nl5.repro_v02_freeze_contract as fc  # noqa: E402

EV = WT / "docs/work/executions/EX-NL5-V02-PREFREEZE-HARDENING-R4/evidence"
BASE_CONTRACT = json.loads((EV / "repro-v0-2-freeze-contract-PRE_DATA_R4.json").read_text())
RECORD_BYTES = (EV / "repro-v0-2-seed-record-PRE_DATA_R4.json").read_bytes()
MANIFEST_BYTES = (EV / "r4-1-collision-scan-manifest-R4.json").read_bytes()
DOC_TEXT = (WT / "docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md").read_text()

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (("  | " + str(detail)[:230]) if detail else ""))


def git(tmp: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(tmp)] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])}: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def wj(tmp: Path, rel: str, obj: dict) -> Path:
    p = Path(tmp) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def build_repo(tmp: Path, mode: str = "v3") -> dict:
    """Build the lifecycle in a real git repo. Modes:
    v3 = correct S -> H -> F -> R -> V -> A; legacy = R4.2 two-commit shortcut."""
    tmp = Path(tmp)
    contract = copy.deepcopy(BASE_CONTRACT)
    contract["scientific_subject"]["freeze_status"] = "NOT_FROZEN"
    contract["scientific_subject"]["frozen_subject_head"] = None
    contract["scientific_subject"]["frozen_subject_tree"] = None
    record_rel = contract["scientific_subject"]["seed_record_path"]
    manifest_rel = contract["collision_scan_manifest"]["path"]
    wj(tmp, "authority/contract.json", contract)
    wj(tmp, manifest_rel, json.loads(MANIFEST_BYTES))
    wj(tmp, record_rel, json.loads(RECORD_BYTES))
    (tmp / "candidate.md").write_text(DOC_TEXT, encoding="utf-8")
    git(tmp, "init", "-q")
    git(tmp, "config", "user.name", "verifier-lifecycle")
    git(tmp, "config", "user.email", "verifier@invalid")
    git(tmp, "add", "-A")
    git(tmp, "commit", "-qm", "S: pre-freeze candidate subject")
    S = git(tmp, "rev-parse", "HEAD")
    S_tree = git(tmp, "rev-parse", "HEAD^{tree}")

    frozen_doc = DOC_TEXT.replace("NOT FROZEN", "FROZEN")
    fcontract = copy.deepcopy(BASE_CONTRACT)
    fcontract["scientific_subject"]["freeze_status"] = "FROZEN"
    fcontract["scientific_subject"]["frozen_subject_head"] = None
    fcontract["scientific_subject"]["frozen_subject_tree"] = None
    fcontract_bytes = (json.dumps(fcontract, ensure_ascii=False, indent=2) + "\n").encode()
    record_sha = sha(RECORD_BYTES)

    if mode == "legacy":
        # R4.2 two-commit shortcut: S reviewed/verified; one evidence commit E
        # holds FROZEN bytes + all records; authority pins S.
        recs = {
            "freeze": {"record_kind": "DIRECTOR_FREEZE_RECORD", "issuer_class": "DIRECTOR",
                       "director": "D-V", "decision": "FREEZE", "subject_head": S,
                       "subject_tree": S_tree, "contract_sha256": sha(fcontract_bytes),
                       "seed_record_sha256": record_sha},
            "hg_b": {"record_kind": "HG_B_OWNER_APPROVAL", "issuer_class": "HUMAN_GATE_OWNER",
                     "decision": "APPROVED", "candidate_revision": "R4",
                     "rule_id": fcontract["rule_id"]},
            "review": {"record_kind": "REVIEWER_VERDICT", "issuer_class": "INDEPENDENT_REVIEWER",
                       "verdict": "PASS", "reviewed_head": S, "reviewed_tree": S_tree},
            "verify": {"record_kind": "VERIFIER_VERDICT", "issuer_class": "INDEPENDENT_VERIFIER",
                       "verdict": "VERIFIED", "verified_head": S, "verified_tree": S_tree},
            "r2": {"record_kind": "R2_ACTIVATION_RECORD", "issuer_class": "R2_HOST",
                   "r2_status": "ACTIVE", "author_executor": "AUTHOR_U1",
                   "external_executor": "EXTERNAL_U2"},
        }
        for name, payload in recs.items():
            wj(tmp, f"authority/{name}.json", payload)
        (tmp / "candidate.md").write_text(frozen_doc, encoding="utf-8")
        wj(tmp, "authority/contract.json", fcontract)
        git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "E: legacy freeze evidence")
        E = git(tmp, "rev-parse", "HEAD")
        E_tree = git(tmp, "rev-parse", "HEAD^{tree}")
        src = {n: E for n in recs}
        F, F_tree = E, E_tree
        subject_head, subject_tree = S, S_tree
    else:
        # commit H: HG-B + R2 (pre-freeze approvals)
        hg = {"record_kind": "HG_B_OWNER_APPROVAL", "issuer_class": "HUMAN_GATE_OWNER",
              "decision": "APPROVED", "candidate_revision": "R4", "rule_id": fcontract["rule_id"]}
        r2 = {"record_kind": "R2_ACTIVATION_RECORD", "issuer_class": "R2_HOST",
              "r2_status": "ACTIVE", "author_executor": "AUTHOR_U1",
              "external_executor": "EXTERNAL_U2"}
        wj(tmp, "authority/hg_b.json", hg)
        wj(tmp, "authority/r2.json", r2)
        git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "H: HG-B approval + R2 activation")
        H = git(tmp, "rev-parse", "HEAD")
        # commit F: FROZEN PACKAGE COMMIT
        (tmp / "candidate.md").write_text(frozen_doc, encoding="utf-8")
        wj(tmp, "authority/contract.json", fcontract)
        git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "F: frozen package commit")
        F = git(tmp, "rev-parse", "HEAD")
        F_tree = git(tmp, "rev-parse", "HEAD^{tree}")
        # commits R, V, A pinning F
        review = {"record_kind": "REVIEWER_VERDICT", "issuer_class": "INDEPENDENT_REVIEWER",
                  "verdict": "PASS", "reviewed_head": F, "reviewed_tree": F_tree}
        verify = {"record_kind": "VERIFIER_VERDICT", "issuer_class": "INDEPENDENT_VERIFIER",
                  "verdict": "VERIFIED", "verified_head": F, "verified_tree": F_tree}
        freeze = {"record_kind": "DIRECTOR_FREEZE_RECORD", "issuer_class": "DIRECTOR",
                  "director": "D-V", "decision": "FREEZE", "subject_head": F,
                  "subject_tree": F_tree, "contract_sha256": sha(fcontract_bytes),
                  "seed_record_sha256": record_sha}
        wj(tmp, "authority/review.json", review)
        git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "R: review record pinning F")
        R = git(tmp, "rev-parse", "HEAD")
        wj(tmp, "authority/verify.json", verify)
        git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "V: verify record pinning F")
        V = git(tmp, "rev-parse", "HEAD")
        wj(tmp, "authority/freeze.json", freeze)
        git(tmp, "add", "-A"); git(tmp, "commit", "-qm", "A: director freeze record pinning F")
        A = git(tmp, "rev-parse", "HEAD")
        src = {"freeze": A, "hg_b": H, "review": R, "verify": V, "r2": H}
        recs = {"freeze": freeze, "hg_b": hg, "review": review, "verify": verify, "r2": r2}
        subject_head, subject_tree = F, F_tree

    def embedded(name: str) -> dict:
        rel = f"authority/{name}.json"
        return {"path": rel, "source_commit": src[name],
                "git_blob_sha1": git(tmp, "rev-parse", f"{src[name]}:{rel}"),
                "canonical_sha256": sha((tmp / rel).read_bytes()),
                **recs[name]}

    authority = {
        "schema_version": 3,
        "kind": "nanolab_v02_dispatch_authority",
        "authority_revision": "verifier-lifecycle-r4-3",
        "fixture": True,
        "fixture_note": "SYNTHETIC TEST FIXTURE ONLY - verifier reproduction, not a real authorization",
        "frozen": True,
        "subject_head": subject_head,
        "subject_tree": subject_tree,
        "contract_sha256": sha(fcontract_bytes),
        "seed_record_sha256": record_sha,
        "frozen_subject_binding": {
            "contract": {"source_commit": F, "path": "authority/contract.json",
                         "git_blob_sha1": git(tmp, "rev-parse", f"{F}:authority/contract.json"),
                         "canonical_sha256": sha(fcontract_bytes)},
            "protocol": {"source_commit": F, "path": "candidate.md",
                         "git_blob_sha1": git(tmp, "rev-parse", f"{F}:candidate.md"),
                         "canonical_sha256": sha(frozen_doc.encode())},
            "seed_record": {"source_commit": F, "path": record_rel,
                            "git_blob_sha1": git(tmp, "rev-parse", f"{F}:{record_rel}"),
                            "canonical_sha256": record_sha},
        },
        "freeze_record": embedded("freeze"),
        "hg_b_record": embedded("hg_b"),
        "review_verdict": embedded("review"),
        "verify_verdict": embedded("verify"),
        "r2_record": embedded("r2"),
        "author_executor": "AUTHOR_U1",
        "external_executor": "EXTERNAL_U2",
        "executor_policy": {"author_leg_allowed": True, "external_leg_allowed": True},
    }
    auth_path = wj(tmp, "authority/dispatch-authority.json", authority)
    return {"tmp": tmp, "S": S, "S_tree": S_tree, "F": F, "F_tree": F_tree,
            "fcontract_bytes": fcontract_bytes, "frozen_doc": frozen_doc,
            "record_rel": record_rel, "auth_path": auth_path, "authority": authority,
            "src": src}


def validate(b, protocol_text=None, contract_path=None):
    return fc.validate_dispatch_authority(
        fc.load_dispatch_authority(b["auth_path"]),
        fc.load_contract(contract_path or b["tmp"] / "authority" / "contract.json"),
        protocol_text if protocol_text is not None else b["frozen_doc"],
        fc.load_seed_record(b["tmp"] / b["record_rel"]),
        repo_root=b["tmp"],
        contract_path=contract_path or b["tmp"] / "authority" / "contract.json",
        protocol_path=b["tmp"] / "candidate.md",
        rerun_scan=False, allow_fixture=True,
    )


def must_reject(name, b, mutate=None, protocol_text=None, substr=None, commit_first=True):
    try:
        if mutate is not None:
            a = fc.load_dispatch_authority(b["auth_path"])
            mutate(a)
            wj(b["tmp"], "authority/dispatch-authority.json", a)
        out = validate(b, protocol_text=protocol_text)
        ok, det = False, f"NOT rejected: status={out.get('status')}"
    except fc.ContractError as e:
        msg = str(e)
        ok = ("DISPATCH_AUTHORIZED" not in msg) and (substr is None or substr in msg)
        det = msg[:200]
    except Exception as e:
        ok, det = False, f"{type(e).__name__}: {str(e)[:150]}"
    check(name, ok, det)


# ================= POSITIVE =================
base = Path(tempfile.mkdtemp())
b = build_repo(base)
F, F_tree = b["F"], b["F_tree"]
check("M-7 lifecycle: S -> H -> F -> R -> V -> A real commits exist", bool(F and F_tree))
check("M-7 F strictly descends from S (not equal)", F != b["S"] and
      subprocess.run(["git", "-C", str(b["tmp"]), "merge-base", "--is-ancestor", b["S"], F]).returncode == 0)
check("M-7 tree(F) == F_tree pinned by git", git(b["tmp"], "rev-parse", f"{F}^{{tree}}") == F_tree)
a = fc.load_dispatch_authority(b["auth_path"])
check("M-7 authority.subject_head == F", a["subject_head"] == F)
check("M-7 authority.subject_tree == tree(F)", a["subject_tree"] == F_tree)
check("M-7 reviewed_head == F and reviewed_tree == tree(F)",
      a["review_verdict"]["reviewed_head"] == F and a["review_verdict"]["reviewed_tree"] == F_tree)
check("M-7 verified_head == F and verified_tree == tree(F)",
      a["verify_verdict"]["verified_head"] == F and a["verify_verdict"]["verified_tree"] == F_tree)
for name in ("contract", "protocol", "seed_record"):
    e = a["frozen_subject_binding"][name]
    path = e["path"]
    blob = git(b["tmp"], "rev-parse", f"{F}:{path}")
    raw = subprocess.run(["git", "-C", str(b["tmp"]), "cat-file", "blob", blob],
                         capture_output=True).stdout
    check(f"M-7 frozen artifact {name} is an exact immutable blob of F",
          e["source_commit"] == F and e["git_blob_sha1"] == blob and sha(raw) == e["canonical_sha256"])
for name in ("review", "verify", "freeze"):
    r = a[f"{name}_verdict"] if name != "freeze" else a["freeze_record"]
    sc = r["source_commit"]
    desc = subprocess.run(["git", "-C", str(b["tmp"]), "merge-base", "--is-ancestor", F, sc],
                          capture_output=True)
    check(f"M-7 {name} record source commit {sc[:8]} STRICTLY descends from F",
          desc.returncode == 0 and sc != F)
desc_hg = subprocess.run(["git", "-C", str(b["tmp"]), "merge-base", "--is-ancestor", b["src"]["hg_b"], F],
                         capture_output=True)
check("M-7 hg_b/r2 records precede F (pre-freeze approvals, binding-checked only)",
      desc_hg.returncode == 0)

rep = validate(b)
check("M-7 POSITIVE validates", rep["status"] == "DISPATCH_PRECONDITIONS_RECORDED", rep)
check("M-7 status == DISPATCH_PRECONDITIONS_RECORDED", rep["status"] == "DISPATCH_PRECONDITIONS_RECORDED")
check("M-7 machine_launch_authorized == false", rep["machine_launch_authorized"] is False)
check("M-7 launch_gate == HUMAN_PROTECTED_WRITER", rep["launch_gate"] == "HUMAN_PROTECTED_WRITER")
check("M-7 review PASS / verify VERIFIED / r2 ACTIVE / hg_b APPROVED",
      (rep["review"], rep["verify"], rep["r2_status"], rep["hg_b"]) == ("PASS", "VERIFIED", "ACTIVE", "APPROVED"))
check("M-7 fixture plan is second-class (synthetic_test_fixture_only)", rep["synthetic_test_fixture_only"] is True)
check("M-7 identity_proof_ceiling documented", "GIT_IMMUTABLE_RECORDS_ONLY" in rep["identity_proof_ceiling"])

plan = fc.build_execution_plan(b["tmp"] / "authority" / "contract.json", b["tmp"] / "candidate.md",
                               b["tmp"] / b["record_rel"], repo_root=b["tmp"],
                               authority_path=b["auth_path"], allow_fixture=True, rerun_scan=False)
check("M-7 plan carries machine_launch_authorized=false", plan["machine_launch_authorized"] is False)
check("M-7 plan carries launch_gate HUMAN_PROTECTED_WRITER", plan["launch_gate"] == "HUMAN_PROTECTED_WRITER")
check("M-7 plan is synthetic-fixture-only (never a real authorization)", plan["synthetic_test_fixture_only"] is True)
check("M-7 plan scientific_outcome NOT_EVALUATED", plan["scientific_outcome"] == "NOT_EVALUATED")

# ================= NEGATIVES =================
def fresh(name, mode="v3"):
    d = Path(tempfile.mkdtemp())
    bb = build_repo(d, mode=mode)
    return bb

def mutated(name, substr=None, **kw):
    bb = fresh(name)
    def _mut(a):
        kw["fn"](a)
    must_reject(name, bb, mutate=_mut, substr=substr)

# 1. schema v1 / v2 rejected
for v in (1, 2):
    bb = fresh(f"schema v{v}")
    must_reject(f"M-7 NEG schema v{v} authority rejected",
                bb, mutate=lambda a, v=v: a.__setitem__("schema_version", v),
                substr=f"schema_version {v!r} != 3")

# 2. review/verify pin S while artifacts bind F
def pin_S_review(a):
    a["review_verdict"]["reviewed_head"] = b["S"]
    a["review_verdict"]["reviewed_tree"] = b["S_tree"]
    # keep the embedded copy consistent so the rejection is about sequencing, not content
    rel = "authority/review.json"
    rec = {k: v for k, v in a["review_verdict"].items() if k not in
           ("path", "source_commit", "git_blob_sha1", "canonical_sha256")}
    wj(b["tmp"], rel, rec)
    a["review_verdict"]["source_commit"] = git(b["tmp"], "rev-parse", "HEAD")
    a["review_verdict"]["git_blob_sha1"] = git(b["tmp"], "rev-parse", f"HEAD:{rel}")
    a["review_verdict"]["canonical_sha256"] = sha((b["tmp"] / rel).read_bytes())
bb = fresh("review pins S")
must_reject("M-7 NEG review->S (artifacts->F) rejected", bb, mutate=pin_S_review, substr="review")

def pin_S_verify(a):
    a["verify_verdict"]["verified_head"] = b["S"]
    a["verify_verdict"]["verified_tree"] = b["S_tree"]
    rel = "authority/verify.json"
    rec = {k: v for k, v in a["verify_verdict"].items() if k not in
           ("path", "source_commit", "git_blob_sha1", "canonical_sha256")}
    wj(b["tmp"], rel, rec)
    a["verify_verdict"]["source_commit"] = git(b["tmp"], "rev-parse", "HEAD")
    a["verify_verdict"]["git_blob_sha1"] = git(b["tmp"], "rev-parse", f"HEAD:{rel}")
    a["verify_verdict"]["canonical_sha256"] = sha((b["tmp"] / rel).read_bytes())
bb = fresh("verify pins S")
must_reject("M-7 NEG verify->S (artifacts->F) rejected", bb, mutate=pin_S_verify, substr="verify")

# 3. review -> F, verify -> S
bb = fresh("review F / verify S")
must_reject("M-7 NEG review->F but verify->S rejected", bb, mutate=pin_S_verify, substr="verify")

# 4. artifact binding -> another commit (authority/evidence commit instead of F)
bb = fresh("artifact->other commit")
must_reject("M-7 NEG artifact binding -> non-F commit rejected", bb,
            mutate=lambda a: a["frozen_subject_binding"]["contract"].__setitem__("source_commit", a["freeze_record"]["source_commit"]),
            substr="exact blobs of")

# 5a. review source on SIBLING (unrelated) history with a VALID blob binding
bb = fresh("review sibling")
def sibling_review(a):
    d = bb["tmp"]
    rel = "authority/review.json"
    rec = {k: v for k, v in a["review_verdict"].items() if k not in
           ("path", "source_commit", "git_blob_sha1", "canonical_sha256")}
    git(d, "checkout", "-q", "-b", "sibling", bb["src"]["hg_b"])  # branch off pre-freeze H
    wj(d, rel, rec)                                               # same bytes as the real R record
    git(d, "add", "-A"); git(d, "commit", "-qm", "sibling review record")
    sib = git(d, "rev-parse", "HEAD")
    a["review_verdict"]["source_commit"] = sib
    a["review_verdict"]["git_blob_sha1"] = git(d, "rev-parse", f"{sib}:{rel}")
    a["review_verdict"]["canonical_sha256"] = sha((d / rel).read_bytes())
    git(d, "checkout", "-q", "master")
must_reject("M-7 NEG review source on unrelated/sibling history (valid binding) rejected", bb,
            mutate=sibling_review, substr="does not descend")
# 5b. review source at a nonexistent commit -> fail-closed at the binding layer
bb = fresh("review source missing")
must_reject("M-7 NEG review source commit predating/nonexistent rejected (fail-closed)", bb,
            mutate=lambda a: a["review_verdict"].__setitem__("source_commit", "0" * 40),
            substr="review_verdict")

# 6. verify source unrelated (orphan commit pinning F)
bb = fresh("verify source orphan")
def orphan_verify(a):
    d = bb["tmp"]
    rel = "authority/verify.json"
    rec = {k: v for k, v in a["verify_verdict"].items() if k not in
           ("path", "source_commit", "git_blob_sha1", "canonical_sha256")}
    git(d, "checkout", "--orphan", "orphan-v")
    git(d, "rm", "-rfq", "--ignore-unmatch", ".")
    wj(d, rel, rec)
    git(d, "add", "-A"); git(d, "commit", "-qm", "orphan verify record")
    orphan = git(d, "rev-parse", "HEAD")
    a["verify_verdict"]["source_commit"] = orphan
    a["verify_verdict"]["git_blob_sha1"] = git(d, "rev-parse", f"{orphan}:{rel}")
    a["verify_verdict"]["canonical_sha256"] = sha((d / rel).read_bytes())
    git(d, "checkout", "-q", "master")
must_reject("M-7 NEG verify source on unrelated history rejected", bb, mutate=orphan_verify,
            substr="does not descend")

# 7. freeze source inside F (self-reference); the record blob cannot exist at F,
# so the binding layer rejects fail-closed (the sequencing self-reference check
# is unreachable for any real Git state by construction)
bb = fresh("freeze inside F")
must_reject("M-7 NEG freeze_record.source_commit == F rejected (fail-closed)", bb,
            mutate=lambda a: a["freeze_record"].__setitem__("source_commit", a["subject_head"]),
            substr="freeze_record")

# 8. freeze source predates F
bb = fresh("freeze predates F")
must_reject("M-7 NEG freeze_record.source_commit predating F rejected (fail-closed)", bb,
            mutate=lambda a: a["freeze_record"].__setitem__("source_commit", "0" * 40),
            substr="freeze_record")

# 9. tampered review path/blob/digest
bb = fresh("review path tamper")
must_reject("M-7 NEG tampered review path rejected", bb,
            mutate=lambda a: a["review_verdict"].__setitem__("path", "authority/nope.json"),
            substr="review_verdict")
bb = fresh("review blob tamper")
must_reject("M-7 NEG tampered review blob sha1 rejected", bb,
            mutate=lambda a: a["review_verdict"].__setitem__("git_blob_sha1", "1" * 40),
            substr="review_verdict")
bb = fresh("review digest tamper")
must_reject("M-7 NEG tampered review canonical digest rejected", bb,
            mutate=lambda a: a["review_verdict"].__setitem__("canonical_sha256", "2" * 64),
            substr="review_verdict")
bb = fresh("verify digest tamper")
must_reject("M-7 NEG tampered verify canonical digest rejected", bb,
            mutate=lambda a: a["verify_verdict"].__setitem__("canonical_sha256", "3" * 64),
            substr="verify_verdict")
# embedded copy != published record bytes
bb = fresh("embedded review drift")
must_reject("M-7 NEG embedded review fields diverging from immutable record bytes rejected", bb,
            mutate=lambda a: a["review_verdict"].__setitem__("verdict", "FAIL"),
            substr="review_verdict")

# 10. nonexistent F
bb = fresh("nonexistent F")
def fake_F(a):
    fake = "e" * 39 + "1"
    a["subject_head"] = fake
    a["subject_tree"] = "f" * 39 + "2"
    for key, hk, tk in (("freeze_record", "subject_head", "subject_tree"),
                        ("review_verdict", "reviewed_head", "reviewed_tree"),
                        ("verify_verdict", "verified_head", "verified_tree")):
        a[key][hk] = fake
        a[key][tk] = "f" * 39 + "2"
must_reject("M-7 NEG nonexistent F rejected", bb, mutate=fake_F, substr="does not exist")

# 11. wrong tree(F) — self-consistent wrong tree pin across authority + records
bb = fresh("wrong tree")
def wrong_tree(a):
    a["subject_tree"] = "a" * 40
    a["freeze_record"]["subject_tree"] = "a" * 40
    a["review_verdict"]["reviewed_tree"] = "a" * 40
    a["verify_verdict"]["verified_tree"] = "a" * 40
must_reject("M-7 NEG self-consistent wrong subject_tree rejected", bb, mutate=wrong_tree,
            substr="subject_tree mismatch")

# 12. worktree-only frozen bytes (protocol text not the F blob)
bb = fresh("worktree-only bytes")
mutated_doc = bb["frozen_doc"] + "\nWORKTREE-ONLY EDIT\n"
try:
    validate(bb, protocol_text=mutated_doc)
    check("M-7 NEG worktree-only frozen protocol bytes rejected", False, "validated")
except fc.ContractError as e:
    check("M-7 NEG worktree-only frozen protocol bytes rejected",
          "not the frozen subject's bytes" in str(e) and "DISPATCH_AUTHORIZED" not in str(e), str(e)[:180])

# 13. legacy R4.2 two-commit shortcut REJECTED
bb = fresh("legacy two-commit", mode="legacy")
must_reject("M-7 NEG legacy R4.2 two-commit shortcut REJECTED", bb, substr="frozen")

# 14. subject_head pointing at a Git TREE, not a commit (self-consistent pins)
bb = fresh("tree as subject")
def tree_subject(a):
    tree_sha = git(bb["tmp"], "rev-parse", f"{bb['S']}^{{tree}}")
    a["subject_head"] = tree_sha
    a["freeze_record"]["subject_head"] = tree_sha
    a["review_verdict"]["reviewed_head"] = tree_sha
    a["verify_verdict"]["verified_head"] = tree_sha
must_reject("M-7 NEG subject_head pointing at a non-commit rejected", bb, mutate=tree_subject,
            substr="does not exist as a Git commit")

# 15. non-fixture authority via CLI plan path is refused (allow_fixture=False)
try:
    fc.build_execution_plan(bb["tmp"] / "authority" / "contract.json", bb["tmp"] / "candidate.md",
                            bb["tmp"] / bb["record_rel"], repo_root=bb["tmp"],
                            authority_path=bb["auth_path"], allow_fixture=False, rerun_scan=False)
    check("M-7 NEG fixture authority refused for real dispatch (allow_fixture=False)", False, "plan produced")
except fc.ContractError as e:
    check("M-7 NEG fixture authority refused for real dispatch (allow_fixture=False)",
          "allow_fixture" in str(e) and "DISPATCH_AUTHORIZED" not in str(e), str(e)[:170])

n_pass = sum(1 for _, ok, _ in results if ok)
print(f"\n== R4.3 M-7 verifier: {n_pass}/{len(results)} checks passed ==")
sys.exit(0 if n_pass == len(results) else 1)
