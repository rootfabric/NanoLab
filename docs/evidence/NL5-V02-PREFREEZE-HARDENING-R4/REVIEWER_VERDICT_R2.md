# NL5 v0.2 PREFREEZE HARDENING R4.1 — Reviewer verdict R2

```text
REVIEW_ID        = NL5-V02-PREFREEZE-HARDENING-R4.1/REVIEWER_VERDICT_R2
REVIEW_VERDICT   = FAIL / FIX_REQUIRED
REVIEWED_BRANCH  = repair/nl5-v02-prefreeze-hardening-r4-r1
REVIEWED_HEAD    = 7406b5a1755b7c025f6e10010be48a7fd231c9be
REVIEWED_TREE    = 8c6a9ba988fa3c539a2cecbba816a92d905e0495
BASE_MAIN        = 87298b36431045474d3784adf5cee8c9a64d0fc9
PREVIOUS_REVIEW  = REVIEWER_VERDICT_R1 / FIX_REQUIRED
CLAIM_CEILING    = C0_SOFTWARE_ONLY / PRE-DATA
SCIENTIFIC_RUNS  = 0
CANDIDATE        = PRE-DATA / NOT FROZEN
HG-B             = WAITING_OWNER
R2               = WAITING_HOST / NOT_ACTIVE
NL5              = IN_PROGRESS
NL6-001          = LOCKED
HOSTED_CI        = NOT_RUN
```

## 0. Scope

Fresh exact-subject code/protocol review of R4.1 repair. Git binding facts were re-read from remote refs and exact commit/tree objects. The implementer-reported `557 tests OK` and harness results are accepted as implementation evidence but were not independently re-executed in this reviewer session; hosted CI has not run because TR-PR is intentionally deferred until Reviewer PASS.

R4.1 materially closes the original Reviewer R1 findings M-2 and M-3 and corrects the equivalence wording. However two blocking defects remain in the new M-1/M-4 machinery.

## 1. What is confirmed fixed

### R1 M-2 — replacement replay / integrity

**PASS in review.**

The validator now independently replays replacement pools from deterministic stream state, validates strict skip-entry shape and re-derivation, binds replacement-pool and full R4 record digests, and preserves the R3 logical digest only as historical provenance.

The regression surface includes coordinated contract+record mutation tests, stale digest tests, wrong skip seed/reason/key/cursor tests and clean bit-exact replay.

### R1 M-3 — collision skip legitimacy

**PASS in review.**

The contract binds a collision-scan manifest; accepted fresh identities are covered; skip coverage is machine-checked; authoritative paths can re-run pinned scans; a fabricated skip for a clean identity is required to fail. Scan errors remain fail-closed.

### R1 m-1 — equivalence wording

**PASS in review.**

The candidate now states equivalence as CI90 of the median paired shift lying wholly inside the predeclared equivalence interval. It explicitly distinguishes equivalence from statistical non-significance vs zero and uses standard TOST H0/H1 wording.

### R1 M-1 — prefreeze vs dispatch separation

**Directionally fixed but not complete.**

The committed PRE-DATA package is now `PREFREEZE_VALIDATION_PASS / DISPATCH_BLOCKED`, and `build_execution_plan()` requires a dispatch authority. This is correct. The remaining blocker is the authenticity/existence of the Git subject and authority records, detailed below.

### R1 M-4 — pair-level ledger

**Directionally fixed but not complete.**

Pair-level state, both legs, one-shot replacement intent and replacement-pair chaining are present. The remaining blocker is mutation atomicity, detailed below.

## 2. Blocking findings

### M-5 — Dispatch authority does not validate that the frozen subject HEAD/TREE actually exist in Git

Severity: **MAJOR / BLOCKING**

`validate_dispatch_authority()` currently validates `subject_head` and `subject_tree` only as 40-hex strings and checks that they differ. It then cross-compares those same strings across authority/freeze/review/verify records.

It does **not** mechanically establish:

```text
git object <subject_head> exists and is a commit
git rev-parse <subject_head>^{tree} == subject_tree
contract/protocol/seed-record bytes are the exact blobs of that frozen subject
review/verify/freeze/owner/R2 records come from immutable Git objects or another trusted authority source
```

The synthetic positive fixture demonstrates the gap: it uses artificial heads such as `ffff...ffff` and trees such as `aaaa...aaaa`. That is valid for a fixture, but the production path has no separate Git-object existence check. A non-fixture JSON package with self-consistent strings and on-disk JSON records can therefore satisfy the current checks without the claimed frozen subject being a real Git commit/tree.

Related trust gap: the authority records are accepted from mutable filesystem paths. `_authority_path_digest()` proves only “the file bytes equal the bytes embedded in the authority”. It does not prove owner approval, independent review, verifier independence, Director issuance or R2 activation provenance. The project invariant explicitly distinguishes role strings from independent executor/authority proof; a local JSON saying `APPROVED/PASS/VERIFIED/ACTIVE` is not itself that proof.

**Required repair:**

Add an immutable source binding for every real dispatch authority. At minimum:

1. Verify `subject_head` exists as a Git commit.
2. Resolve its actual tree and require equality to `subject_tree`.
3. Bind protocol, contract and seed record to exact Git blobs from the frozen subject tree (or explicit immutable artifact digests referenced by that commit).
4. Each authority record must carry an immutable source ref, e.g. `source_commit + path + git_blob_sha1 + canonical_sha256`; load bytes from the Git object, not from a mutable working-tree path.
5. Owner HG-B, Reviewer, Verifier and R2 activation records must have an issuer/provenance class that cannot be created merely by changing `fixture=false`. If the project does not yet have a cryptographically/protected trusted writer, then the machine result must honestly be `DISPATCH_PRECONDITIONS_RECORDED`, not `DISPATCH_AUTHORIZED`; the final launch gate must remain an external Human/Protected-Writer gate.
6. Add negative tests:
   - nonexistent but well-formed 40-hex subject head;
   - head exists but supplied tree does not match;
   - authority record bytes only in dirty worktree, not pinned Git object;
   - fake non-fixture HG-B/review/verify/R2 JSON created locally;
   - record source_commit/path/blob mismatch.

This is a control-plane issue, not a scientific-design change.

### M-6 — Pair replacement is not transactionally atomic

Severity: **MAJOR / BLOCKING**

`ReplacementLedger.request_replacement()` performs only partial validation before mutating state.

Current order:

```text
validate source failed pair / quota / pool / author_attempt_id != external_attempt_id
→ increment pool cursor
→ increment used quota
→ mark source pair PAIR_REPLACED
→ set replacement identity/pair id
→ open_pair(replacement_pair_id, ...)
→ bind author scheduled attempt
→ bind external scheduled attempt
```

But `open_pair()` and `_bind_attempt()` can still raise after the quota/cursor/source pair have already been mutated. Examples:

- `replacement_pair_id` already exists;
- replacement seed is already owned by an existing pair;
- author attempt id is invalid or already globally used;
- external attempt id is invalid or already used;
- author leg binds successfully but external leg fails.

In these cases the call raises, but the ledger may already have consumed quota, advanced the pool cursor, changed the source pair to `PAIR_REPLACED`, opened a partial replacement pair, or bound only one leg. That violates the append-only state-machine claim and can produce a one-leg/inconsistent replacement through an error path.

The current tests cover repeated replacement of an already-replaced source pair and the special case `author_attempt_id == external_attempt_id`, but not these post-mutation failure paths.

**Required repair:**

Make replacement assignment atomic.

Preferred implementation:

```text
PHASE 1 — validate all future writes without mutation
  validate replacement_pair_id availability
  validate replacement seed ownership
  validate both attempt-id formats
  validate both attempt ids globally unused
  validate both legs
  validate quota/cursor/pool
  construct full prospective new state/event

PHASE 2 — commit mutation only after every validation passes
```

or implement rollback guaranteed to restore every touched structure.

Add tests asserting **state is byte-for-byte / structurally unchanged after rejection** for:

- duplicate replacement_pair_id;
- duplicate author attempt id;
- duplicate external attempt id;
- invalid author attempt id format;
- invalid external attempt id format;
- replacement seed already owned;
- failure during second-leg binding.

For each test verify:

```text
source pair state unchanged
replacement_assigned unchanged
used_pairs unchanged
pool_cursor unchanged
no new pair
no new attempt
ledger event count unchanged
```

### m-2 — open_pair returns a shallow copy exposing internal legs

Severity: **MINOR, repair with M-6**

`open_pair()` returns `dict(pair)`, but the nested `legs` object is shared with internal state. A caller can mutate `returned["legs"]` and thereby mutate the ledger without going through the state machine.

Return a deep-enough immutable/read-only snapshot (at least `legs=dict(pair["legs"])`) just as `pair()` already does.

Add a test that mutating the value returned by `open_pair()` does not mutate internal state.

## 3. Notes, not blockers

### n-1 — Frozen document phrase matching is brittle

The FROZEN protocol check still relies on raw occurrence of the phrase `NOT FROZEN`. The current candidate has only two such occurrences and can be converted cleanly at freeze time, so this is not a blocker today. Prefer a structured machine field over global phrase semantics before the actual freeze revision.

### n-2 — Hosted CI

No TR-PR hosted run exists yet. This is correct while Reviewer is FAIL. Do not open a merge-ready PR merely to obtain green CI; after repair + Reviewer PASS, open a draft PR and bind hosted CI to the exact product subject/integration subject per harness.

### n-3 — power-gate branch

`repair/nl5-acceptance-policy-r4-power-gate-r1` remains separate and dormant. Keep Director sequencing explicit.

## 4. Review conclusion

```text
R4.1 M-2 replacement replay      = PASS
R4.1 M-3 collision skip proof    = PASS
R4.1 equivalence wording         = PASS
R4.1 prefreeze/dispatch split    = PARTIAL / FIX_REQUIRED (M-5)
R4.1 pair-level ledger           = PARTIAL / FIX_REQUIRED (M-6, m-2)

OVERALL = FIX_REQUIRED
```

No Verifier should run yet.

## 5. Next action

```text
NEXT_ACTOR = IMPLEMENTER
NEXT_WORK  = R4.2 narrow repair
SCOPE      = M-5 Git/provenance binding + M-6 atomic pair replacement + m-2 snapshot safety
```

Preserve all already-correct R4/R4.1 science/protocol parameters:

```text
N = 64/64/10/10
N_min = 52/52/8/8
replacement quotas = 12/12/2/2 pairs
replacement cap = 56 runs
max_runs = 352
delta = 0.5
paired design unchanged
R3 confirmatory identities unchanged
candidate = PRE-DATA / NOT FROZEN
HG-B = WAITING_OWNER
R2 = WAITING_HOST / NOT_ACTIVE
scientific runs = 0
NL5 = IN_PROGRESS
NL6-001 = LOCKED
```

After R4.2: new exact HEAD/TREE → fresh Reviewer. Only Reviewer PASS unlocks Verifier.
