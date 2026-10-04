# NL5 v0.2 PREFREEZE HARDENING R4.3 — Fresh Reviewer verdict R4

```text
REVIEW_ID        = NL5-V02-PREFREEZE-HARDENING-R4.3/REVIEWER_VERDICT_R4
REVIEW_VERDICT   = PASS
REVIEWED_BRANCH  = repair/nl5-v02-prefreeze-hardening-r4-r3
REVIEWED_HEAD    = 39cc9809ad4b9ad61b2effd6dbcb8c9067848da0
REVIEWED_TREE    = 10ba8bbffcae06ae7fad7135b2493494b0d4f9b1
BASE_MAIN        = 87298b36431045474d3784adf5cee8c9a64d0fc9
PREVIOUS_REVIEW  = REVIEWER_VERDICT_R3 / FIX_REQUIRED
CLAIM_CEILING    = C0_SOFTWARE_ONLY / PRE-DATA
SCIENTIFIC_RUNS  = 0
CANDIDATE        = PRE-DATA / NOT FROZEN
HG-B             = WAITING_OWNER
R2               = WAITING_HOST / NOT_ACTIVE
NL5              = IN_PROGRESS
NL6-001          = LOCKED
HOSTED_CI        = NOT_RUN
INDEPENDENT_FULL_TEST_RERUN = NOT_RUN (review environment DNS blocked clean clone)
```

## 0. Scope

Fresh exact-head review of the R4.3 control-plane repair. The reviewer independently re-read remote Git refs, exact commit/tree identity, the R4.3 delta, Repair Map R3, authority implementation and the new sequencing regression tests.

The implementer-reported `593 tests OK`, consistency/lint/work-cli results remain implementation evidence. A clean-clone independent rerun was attempted from the review environment but could not be performed because the environment could not resolve github.com; this review therefore does **not** claim an independent full-suite execution fact.

The PASS below is based on exact-head code/protocol review plus inspection of the newly committed regression logic. It does not freeze the protocol, activate R2, authorize a launch, start science, accept NL5 or unlock NL6.

## 1. Binding facts

Verified from Git:

```text
main =
87298b36431045474d3784adf5cee8c9a64d0fc9

R4.3 HEAD =
39cc9809ad4b9ad61b2effd6dbcb8c9067848da0

R4.3 TREE =
10ba8bbffcae06ae7fad7135b2493494b0d4f9b1

R4.3 branch =
repair/nl5-v02-prefreeze-hardening-r4-r3

R4.3 relation to R4.2 =
7 commits ahead / 0 behind
```

The delta is narrowly scoped to Reviewer R3 evidence/prompt, R4.3 execution events/evidence, summary/queue sync, `repro_v02_freeze_contract.py` and R4 regression tests.

## 2. Reviewer R3 finding M-7

### Verdict: PASS

The previous two-commit cycle is mechanically removed.

The accepted authority schema is now **v3**; schema v1/v2 are rejected fail-closed.

The implementation now distinguishes the immutable lifecycle:

```text
S = PRE-FREEZE candidate
H = pre-freeze HG-B/R2 records where applicable
F = FROZEN PACKAGE COMMIT
R = fresh review record pinning F
V = fresh verifier record pinning F
A = readiness/authority evidence binding exact records
```

Key properties confirmed:

1. **F is the authority subject.**
   `subject_head` must resolve to a real Git commit and its actual tree must equal `subject_tree`.

2. **Frozen scientific artifacts belong to F itself.**
   `frozen_subject_binding` requires contract/protocol/seed-record `source_commit == F`, with exact Git blob SHA-1 and SHA-256 checks plus byte equality to validation inputs.

3. **No frozen-package self-SHA is required.**
   `scientific_subject.frozen_subject_head/tree` are explicitly non-authoritative compatibility fields; a canonical FROZEN contract may keep them null. Exact F HEAD/TREE live in external authority/freeze records.

4. **Review and Verify pin the frozen package, not S.**
   `reviewed_head/tree == F/tree(F)` and `verified_head/tree == F/tree(F)` are mandatory.

5. **Post-freeze sequencing is checked mechanically.**
   Freeze/review/verify record source commits must be strict descendants of F using Git ancestry checks. A record inside F, before F or on unrelated history is rejected.

6. **Authority records no longer need one impossible shared evidence commit.**
   Each record has its own immutable `source_commit/path/git_blob_sha1/canonical_sha256/record_kind/issuer_class`.

7. **HG-B/R2 pre-freeze placement is not falsely rejected.**
   They receive immutable binding checks but are not forced to postdate F, matching the documented lifecycle.

8. **Legacy R4.2 shortcut is explicitly regression-tested as REJECTED.**
   The test suite constructs the former self-consistent two-commit model and requires failure.

This closes the exact control-plane cycle identified in Reviewer R3.

## 3. Reviewer R3 finding m-3

### Verdict: PASS

The misleading phrase `authorized plan produced` was removed.

The current semantics state that exit 0 means validation/preconditions recorded while:

```text
machine_launch_authorized = false
launch_gate = HUMAN_PROTECTED_WRITER
status = DISPATCH_PRECONDITIONS_RECORDED
```

A prepared execution plan is explicitly not a launch authorization.

## 4. Previously accepted surfaces

No regression found in the narrow R4.3 delta. The following remain accepted by this review:

```text
F1 fail-closed contract hardening
F2 immutable collision scan
F3 replacement cursor/pools
F4 integer rounding policy

R4.1 M-2 replacement bit-exact replay
R4.1 M-3 collision-skip legitimacy
R4.1 TOST/equivalence wording

R4.2 M-6 transactional pair replacement
R4.2 m-2 snapshot safety
R4.2 Git object / immutable byte binding
R4.2 trust ceiling
```

Science/protocol parameters remain unchanged:

```text
N = 64 / 64 / 10 / 10
N_min = 52 / 52 / 8 / 8
replacement quotas = 12 / 12 / 2 / 2 pairs
replacement cap = 56 runs
max_runs = 352
delta = 0.5
paired design unchanged
R3 confirmatory identities unchanged
```

## 5. Test / CI evidence status

Implementation evidence recorded at the exact R4.3 line:

```text
python3 -m unittest discover -s tests -t . -> 593 tests OK
check-consistency -> ok
workflow_lint -> blocking 0
work_cli validate -> 49/49 EX-* OK
prefreeze -> PREFREEZE_VALIDATION_PASS / DISPATCH_BLOCKED
hosted CI -> NOT_RUN
```

The new `FrozenPackageSequencingTest` surface is structurally aligned with M-7 and covers the required negative classes, including:

- review/verify pinning pre-freeze S;
- mixed F/S review/verify pins;
- wrong frozen artifact commit;
- review/verify/freeze record source predating or unrelated to F;
- exact immutable record blob bindings;
- tampered source path/digest;
- nonexistent F / wrong tree;
- worktree-only frozen bytes;
- schema downgrade;
- legacy R4.2 two-commit shortcut.

Independent full-suite rerun is deferred to the next Verifier / hosted CI stage because the reviewer environment could not obtain a clean clone.

## 6. Reviewer conclusion

```text
REVIEW_VERDICT = PASS

R4_TOOLING = REVIEW_PASS
CANDIDATE = PRE-DATA / NOT FROZEN
HG-B = WAITING_OWNER
R2 = WAITING_HOST / NOT_ACTIVE
SCIENTIFIC_RUNS = 0
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED
```

No scientific or project-state acceptance follows from this PASS.

## 7. Next action

```text
NEXT_ACTOR = fresh independent VERIFIER

NEXT_ACTION =
verify exact HEAD 39cc9809ad4b9ad61b2effd6dbcb8c9067848da0
tree 10ba8bbffcae06ae7fad7135b2493494b0d4f9b1

Verifier must independently:
- reproduce the critical negative controls F1-F4 / M-1..M-7;
- execute the real stdlib test collection;
- execute harness consistency/lint/work-cli;
- verify PRE-DATA package remains DISPATCH_BLOCKED;
- verify schema v3 S→F→R/V→A synthetic positive and legacy-shortcut negative;
- check no scientific runs/status inflation;
- record exact HEAD/TREE.

Only VERIFIED unlocks draft PR / TR-PR hosted CI and Director readiness.
```
