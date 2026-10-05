# NL5 v0.2 PREFREEZE HARDENING R4.2 — Reviewer verdict R3

```text
REVIEW_ID        = NL5-V02-PREFREEZE-HARDENING-R4.2/REVIEWER_VERDICT_R3
REVIEW_VERDICT   = FAIL / FIX_REQUIRED
REVIEWED_BRANCH  = repair/nl5-v02-prefreeze-hardening-r4-r2
REVIEWED_HEAD    = e58ac8225562995963c414e66b9b6ce6ea9ad55e
REVIEWED_TREE    = 7f9f063e266d74cc7d6c6646a3022184a06bc976
BASE_MAIN        = 87298b36431045474d3784adf5cee8c9a64d0fc9
PREVIOUS_REVIEW  = REVIEWER_VERDICT_R2 / FIX_REQUIRED
CLAIM_CEILING    = C0_SOFTWARE_ONLY / PRE-DATA
SCIENTIFIC_RUNS  = 0
CANDIDATE        = PRE-DATA / NOT FROZEN
HG-B             = WAITING_OWNER
R2               = WAITING_HOST / NOT_ACTIVE
NL5              = IN_PROGRESS
NL6-001          = LOCKED
HOSTED_CI        = NOT_RUN
INDEPENDENT_TEST_RERUN = NOT_RUN (review environment has no network clone path)
```

## 0. Scope

Fresh exact-head review of R4.2. Git binding was independently re-read from the remote repository: HEAD/TREE match the handoff and the branch is exactly 7 commits ahead of the R4.1 reviewed subject.

The implementer-reported `580 tests OK`, consistency/lint/work-cli results are retained as implementation evidence. I did not independently reproduce the full suite because the reviewer execution environment cannot resolve github.com for a clean clone; no claim of independent test execution is made.

M-6 and m-2 are closed by code inspection and their regression design. M-5 is substantially improved, but the new provenance model still contains one control-plane cycle that prevents Reviewer PASS.

## 1. Confirmed PASS surfaces

### R2 M-6 — atomic pair replacement

**PASS.**

`request_replacement()` now validates every foreseeable mutation target before state change: source pair state, quota/cursor, new pair id, replacement seed ownership, both attempt-id formats/uniqueness and distinct legs.

The commit phase is additionally protected by a full state snapshot/rollback guard. A second-leg/internal failure restores pairs, attempts, seed ownership, quota/cursor and event ledger.

This closes the previous partial-mutation defect.

### R2 m-2 — snapshot safety

**PASS.**

`open_pair()` returns an independent nested `legs` mapping; `pair()` and `ledger` also return independent snapshots. Public snapshot mutation no longer reaches internal state.

### R2 M-5 — Git object existence / immutable byte binding

**PARTIAL PASS.**

The following are now correctly implemented:

- `subject_head` must be a real Git commit;
- actual `subject_head^{tree}` must equal `subject_tree`;
- authority records are loaded from Git object database, not mutable worktree;
- record path/blob SHA-1/SHA-256 are checked;
- contract/protocol/record bytes are immutably bound;
- schema downgrade fails closed;
- the machine no longer claims `DISPATCH_AUTHORIZED`;
- ceiling is honestly `DISPATCH_PRECONDITIONS_RECORDED` / `machine_launch_authorized=false` / `HUMAN_PROTECTED_WRITER`.

These changes should be preserved.

## 2. Blocking finding

### M-7 — Review/Verifier verdicts are bound to the pre-freeze commit, not to the frozen package bytes

Severity: **MAJOR / BLOCKING**

The project freeze chain requires a fresh Reviewer and fresh Verifier **after freeze**, on the FROZEN protocol/package.

The R4.2 synthetic model explicitly constructs:

```text
commit R = reviewed subject
           PRE-FREEZE contract + protocol + seed record

commit E = freeze-evidence commit
           FROZEN contract + FROZEN protocol + authority records
```

But the Review and Verify records stored in E contain:

```text
reviewed_head / reviewed_tree = R
verified_head / verified_tree = R
```

while the actual frozen contract/protocol bytes validated for dispatch live in E and differ from R (at minimum `NOT FROZEN → FROZEN` plus frozen-subject binding fields).

Therefore the machine currently proves:

```text
R was reviewed and verified
E contains frozen bytes
```

but does **not** prove:

```text
the frozen bytes in E were reviewed and verified
```

This means `DISPATCH_PRECONDITIONS_RECORDED` can be returned even though the stated prerequisite “fresh review PASS + verify VERIFIED for the frozen subject” has not actually been recorded for the immutable frozen package.

The code comment acknowledges the cycle:

> subject = reviewed commit, evidence = freeze commit

but that model is not equivalent to the documented freeze chain.

There is a second structural symptom: all five authority records are forced to share one `freeze-evidence commit`. A Reviewer/Verifier verdict about that same commit cannot be contained inside it without self-reference. This makes “review/verify the exact frozen package” impossible in the current two-commit scheme.

**Required repair: break the cycle with separate immutable stages.**

Recommended model:

```text
S = approved pre-freeze candidate subject
    PRE-DATA / NOT FROZEN

F = frozen package commit
    exact FROZEN protocol/contract/seed record
    no requirement to contain its own commit SHA

R/V = later immutable reviewer/verifier records
      reviewed_head = F
      reviewed_tree = tree(F)
      verified_head = F
      verified_tree = tree(F)

A = authority / readiness evidence
    references F + immutable Review/Verify/HG-B/R2 records
```

The frozen contract should not need to embed its own Git commit SHA. Move exact `frozen_subject_head/tree` binding to an external freeze/authority record, or replace the self-referential field with a non-self-referential package identifier/digest.

The final authority validator must require:

1. the frozen package commit F exists;
2. contract/protocol/seed-record bytes are exact blobs of F;
3. review PASS record immutably references F HEAD/TREE;
4. verify VERIFIED record immutably references F HEAD/TREE;
5. Review/Verify record source commits are later than / descendants of F (or at minimum separate immutable commits with explicit subject F);
6. authority/readiness evidence is later and references those exact records;
7. no self-consistent two-commit shortcut may satisfy this chain.

Do **not** require all records to live in one evidence commit. Each record should carry its own immutable source binding.

### Required tests for M-7

Add at least:

- review/verify point to pre-freeze S while frozen artifacts are F → reject;
- review points F, verify points S → reject;
- review/verify point F but artifact binding points different commit → reject;
- review/verify source records exist only in F itself → reject if that implies self-review evidence cycle;
- review and verify records in later immutable commits, both pin F → pass;
- authority evidence references exact record blob refs from those later commits → pass;
- ancestry/order mismatch (record source predates F or unrelated history) → reject.

## 3. Minor finding

### m-3 — CLI/docstring still says “authorized plan produced”

The module header still documents:

```text
Exit codes: 0 = PASS / authorized plan produced
```

while R4.2 intentionally removed machine authorization and returns only `DISPATCH_PRECONDITIONS_RECORDED` with `machine_launch_authorized=false`.

Change wording to something like:

```text
0 = validation/preconditions recorded; launch still requires HUMAN_PROTECTED_WRITER
```

This is documentation/control semantics, not a scientific change.

## 4. Review conclusion

```text
R4.2 M-6 transactional ledger       = PASS
R4.2 m-2 snapshot safety            = PASS
R4.2 Git object/byte binding        = PASS
R4.2 trust ceiling                  = PASS
R4.2 frozen review/verify binding   = FIX_REQUIRED (M-7)

OVERALL = FIX_REQUIRED
```

No Verifier should run yet.

## 5. Next action

```text
NEXT_ACTOR = IMPLEMENTER
NEXT_WORK  = R4.3 narrow control-plane repair
SCOPE      = M-7 frozen-package review/verify sequencing + m-3 wording only
```

Preserve all science/protocol parameters and all already-passing R4/R4.1/R4.2 repair surfaces.

After R4.3: publish a new exact HEAD/TREE → fresh Reviewer. Only Reviewer PASS unlocks Verifier.
