# NL5 v0.2 PREFREEZE HARDENING R4.3 — Fresh independent VERIFIER verdict R1

```text
VERIFIER_ID      = NL5-V02-PREFREEZE-HARDENING-R4.3/VERIFIER_VERDICT_R1
VERDICT          = VERIFIED
VERIFIED_BRANCH  = repair/nl5-v02-prefreeze-hardening-r4-r3
VERIFIED_HEAD    = 39cc9809ad4b9ad61b2effd6dbcb8c9067848da0
VERIFIED_TREE    = 10ba8bbffcae06ae7fad7135b2493494b0d4f9b1
REVIEW_BRANCH    = review/nl5-v02-prefreeze-hardening-r4-3-r4 (tip f564aa7a; F + 3 review-record commits)
REVIEW_VERDICT   = PASS (recorded by fresh Reviewer; NOT used as evidence — every fact below reproduced independently)
VERIFIER_BRANCH  = verify/nl5-v02-prefreeze-hardening-r4-3-r1 (created from exact VERIFIED_HEAD; product branch untouched)
HOSTED_CI        = NOT_RUN (no TR-PR exists for 39cc9809; draft PR is the NEXT integration gate per repo process)
SCIENTIFIC_RUNS  = 0
CANDIDATE        = PRE-DATA / NOT FROZEN
HG-B             = WAITING_OWNER
AUTHOR_U1        = NOT_ASSIGNED
R2               = WAITING_HOST / NOT_ACTIVE
external_reproductions = 0
NL5              = IN_PROGRESS
NL6-001          = LOCKED (PLANNED, depends_on NL5-002)
CLAIM_CEILING    = C0_SOFTWARE_ONLY / PRE-DATA
```

## 0. Method

Fresh independent verification per `docs/work/prompts/UBUNTU_AGENT_NL5_R4_3_VERIFIER_R1.md`
(read from review commit f564aa7a). Clean worktree at exact HEAD
`/tmp/nl5-verify-431` (HEAD == VERIFIED_HEAD, tree == VERIFIED_TREE, status clean).
No implementer/reviewer result was trusted: all facts re-executed on the exact
subject. Product branch `repair/nl5-v02-prefreeze-hardening-r4-r3` was not
modified. main was not merged, the protocol was not frozen, no scientific
campaign was started, no NL5/R2 status was raised.

## 1. Full real test surface (reproduced, exact HEAD)

| Command | Result |
|---|---|
| `python3 -m unittest discover -s tests -t . -v` | **Ran 593 tests — OK** (0 failures, 0 errors, 0 skipped; 43.7s) |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | ok=true; 9 stages / 19 tasks / 7 experiments; 0 errors, 0 warnings |
| `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | ok; 1 workflow, 0 violations (0 blocking) |
| hosted CI Check 1 (JSON syntax sweep, replicated) | 1303 tracked *.json — 0 failures; 4 pinned non-JSON evidence paths digest-checked OK |
| hosted CI Check 3 (`work_cli validate`, all EX-* loop, replicated) | **49/49 EX-* dirs OK** |

(Actual count reported as required; not forced to the historical 593 — it is 593.)

## 2. F1–F4 independent reproduction — 79/79 checks PASS

Script: `verify_r4_3/f1_f4_checks.py`, output `f1_f4_checks.out`.

- **F1 fail-closed**: 19 malformed/partial mutations of the committed contract
  and protocol each rejected (missing keys, schema_version≠1, wrong kind,
  unknown revision, non-int/bool/negative/oversized seeds, count below N,
  wrong embedded n_min, tampered anchor/budget, FROZEN-without-pins, missing /
  duplicate / contradicting cardinality lines, duplicated machine block,
  truncated JSON).
- **F2 pinned-tree scan**: missing pinned object → `TreeScanError` (never a
  fake CLEAN); committed seed outside allowlist = COLLISIONS; exact-path
  allowlist exclusion verified; **pinned tree beats dirty worktree**
  (tracked file deleted in worktree still found in pinned scan); worktree
  (non-authoritative) mode demonstrably loses the same file; real accepted
  seeds scan CLEAN on pinned `a9d7d07`.
- **F3 replacement pools**: bit-exact replay of all four frozen pools from
  `start_index` 75/76/21/21 (= `next_candidate_index`, strictly after consumed
  confirmatory indices 74/75/20/20); pools disjoint from confirmatory seeds
  (no reuse), no duplicates, lengths == quotas 12/12/2/2; confirmatory stream
  itself replays bit-exact with recorded skips re-derived; fake skip seed
  rejected; `replacement_pool_sha256` matches contract embedding
  (`369a63c0…`).
- **F4 integer policy** `ceil-nmin-floor-replacement-pairs-v1`: N_min 52/8
  (ceil 0.80; 51/64 = 79.7% is NOT ≥ 80%), quotas 12/12/2/2 (floor 0.20),
  replacement cap 56, confirmatory 296, **max_runs 352**; contract-embedded
  values == policy derivation.

## 3. R4.1 integrity/authority controls — PASS (within 46/46)

Script: `verify_r4_3/r41_r42_checks.py`, output `r41_r42_checks.out`.

- Committed PRE-DATA package: `PREFREEZE_VALIDATION_PASS` +
  `DISPATCH_BLOCKED`, `freeze_status NOT_FROZEN`; `plan` refused
  (ContractError `DISPATCH_BLOCKED`; CLI exit 3; refusal carries **no**
  launch flag). PRE-DATA cannot yield launch authorization.
- Manifest tampering: bound digest edit, bound path edit, content edit —
  all rejected; untampered manifest verifies (control).
- Fake collision skip (well-formed entry, clean seed): rejected
  (re-derivation/scans fail closed).
- Replacement pools bit-exact replay: PASS (see F3).

## 4. R4.2 M-6 transactional ledger + snapshot isolation — 46/46 PASS

Same script. After **every** rejection `state_snapshot()` compared equal
(no cursor/quota/pair/attempt/ledger change): duplicate pair id; unknown
variant; unknown pair; SCHEDULED as real outcome; invalid attempt-id format;
duplicate author/external leg; replacement on incomplete pair; second
replacement for the same failed pair (one-shot); duplicate author attempt id
across pairs; duplicate external attempt id across pairs; author/external id
collision; duplicate replacement pair id; replacement seed already owned.
Forced second-leg binding failure **mid-commit** → full bit-for-bit rollback,
cursor/quota untouched, retry then succeeds atomically. Quota exhaustion →
`ReplacementBudgetExhausted` (honest stop). Public `state_snapshot()`,
`ledger`, `pair()` are isolated deep copies.

## 5. R4.3 M-7 sequencing (main verifier gate) — 47/47 checks PASS

Script: `verify_r4_3/m7_lifecycle_checks.py`, output `m7_lifecycle_checks.out`.
Mechanically reproduced in a REAL temporary Git repository the lifecycle
`S → H (HG-B+R2) → F → R → V → A` with real commits, trees and blobs.

Positive (all verified via git plumbing AND the schema v3 validator):

- `subject_head == F`; `subject_tree == tree(F)` (`git rev-parse F^{tree}`);
  F strictly descends from pre-freeze S.
- **frozen contract/protocol/seed-record are exact immutable Git blobs OF F**
  (source_commit == F; `git rev-parse F:path` blob sha1; bytes sha256 match).
- **reviewed_head == F / reviewed_tree == tree(F)**;
  **verified_head == F / verified_tree == tree(F)**.
- **review/verify/freeze record source commits strictly descend from F**
  (merge-base --is-ancestor, ≠ F); HG-B/R2 pre-freeze approvals precede F.
- Result: **status = DISPATCH_PRECONDITIONS_RECORDED**;
  **machine_launch_authorized = false**; **launch_gate = HUMAN_PROTECTED_WRITER**;
  review PASS / verify VERIFIED / R2 ACTIVE / HG-B APPROVED;
  `synthetic_test_fixture_only = true`;
  `identity_proof_ceiling = GIT_IMMUTABLE_RECORDS_ONLY`.
- Execution plan (fixture): `machine_launch_authorized=false`,
  `HUMAN_PROTECTED_WRITER`, scientific_outcome NOT_EVALUATED.

Negative controls (each ContractError-rejected, message never contains
`DISPATCH_AUTHORIZED`): schema v1 → reject; schema v2 → reject;
review→S with artifacts→F → reject; verify→S → reject; review→F but verify→S →
reject; artifact binding→non-F commit → reject; review source on
sibling/unrelated history with VALID blob binding → `does not descend` reject;
verify source on orphan history → reject; review/verify/freeze source
nonexistent or predating F → fail-closed reject; freeze source == F →
fail-closed reject; tampered review path / blob sha1 / canonical digest /
verify digest → reject; embedded fields diverging from immutable record bytes
→ reject; nonexistent F → reject; self-consistent wrong `tree(F)` →
`subject_tree mismatch` reject; **worktree-only frozen bytes** (protocol text
not the F blob) → reject; **legacy R4.2 two-commit shortcut → REJECT**
(artifacts bound to evidence commit ≠ pinned subject; review/verify pinned the
pre-freeze subject); subject_head pointing at a Git tree → reject; fixture
authority refused for real dispatch (`allow_fixture=False`).

## 6. Trust ceiling — proven

Executable-code sweep of `scripts/` (+ tools): `DISPATCH_AUTHORIZED` occurs
ONLY in docstrings/comments; the only dispatch statuses produced are
`DISPATCH_PRECONDITIONS_RECORDED` and `DISPATCH_BLOCKED`;
`machine_launch_authorized` is only ever the literal `False` (validator return
+ plan); `launch_gate` only `HUMAN_PROTECTED_WRITER`; `dispatch_ready` only
literal `false`. Test-suite occurrences of `DISPATCH_AUTHORIZED` are
exclusively negative assertions (`assertNotIn`). No production path returns
`DISPATCH_AUTHORIZED` or `machine_launch_authorized = true`.

## 7. Status boundaries (exact subject)

- `project/state.json`: frontier NL5, `NL5 = IN_PROGRESS`, `NL6-001 = PLANNED`
  (locked behind NL5 acceptance), `NL5-002 = WAITING_HUMAN` (terminal
  MISMATCH / NOT accepted).
- Contract + WORK_QUEUE: CANDIDATE = **PRE-DATA / NOT FROZEN**;
  NEW_SCIENTIFIC_RUNS = **0**; external_reproductions = **0**;
  HG-B = **WAITING_OWNER**; AUTHOR_U1 = **NOT_ASSIGNED**;
  R2 = **WAITING_HOST / NOT_ACTIVE**; NL6-001 = **LOCKED**.
- `WINDOWS_WSL_EXECUTOR = HISTORICAL_ONLY`, `WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO`
  (no Windows/WSL new science); outenemy remains EXTERNAL_U2_ONLY (external
  reproduction, never author host).
- Package digests re-hashed on exact HEAD: contract `46e3c959…`, seed record
  `8e844bff…`, scan manifest `77ef5b6a…` — byte-identical to the committed
  R4.3 evidence claims.

## 8. Hosted CI

`HOSTED_CI = NOT_RUN`: no TR-PR exists for VERIFIED_HEAD `39cc9809`
(git ls-remote shows no pull ref containing it; gh API not authenticated — no
run fabricated). The repository process defines hosted CI (TR-PR) as the NEXT
integration gate; per the verifier prompt this verifier may finish VERIFIED
before hosted CI, which is explicitly recorded here. Draft PR → TR-PR hosted
CI → Director readiness → Human Gate happens only after this verdict.

## 9. Verdict

```text
VERDICT = VERIFIED

NEXT_ACTOR  = DIRECTOR / integration preparation
NEXT_ACTION = draft PR on exact reviewed+verified product subject
              (repair/nl5-v02-prefreeze-hardening-r4-r3 @ 39cc9809,
               tree 10ba8bbf)
              -> TR-PR hosted CI
              -> Director readiness
              -> Human Gate
```

Boundaries respected: main not merged; protocol not frozen; no scientific
campaign started; NL5/R2 statuses not raised; product subject not modified.
