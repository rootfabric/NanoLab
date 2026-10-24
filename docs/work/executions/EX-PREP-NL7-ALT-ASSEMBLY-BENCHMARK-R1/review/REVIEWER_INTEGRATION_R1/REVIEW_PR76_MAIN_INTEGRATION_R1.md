# REVIEW PR #76 MAIN INTEGRATION R1 — Independent Reviewer Report

**Role:** fresh independent REVIEWER-76 (main-integration gate) per Issue #77 handoff 2026-10-23.
**Reviewer session ID:** `REVIEWER-76-INT-R1-cb193b02`
**Executor:** fresh checkout `~/NanoLab-review76` on native Ubuntu host, separate from any Implementer/Director session. No Implementer/Verifier work performed in this session.
**Claim ceiling of this review:** C0 SOFTWARE ONLY. Zero scientific runs.

---

## 1. Subject identity (independently derived, not trusted from handoff)

```text
HEAD      = cf413b053677de17beaf2dcf3ce9b86868361b3e   (merge commit, 2 parents)
TREE      = 560dc913a71a237d3c452a5a2e492e213b232911
PARENT_1  = 9fed48a88bb60d5bdfa4a8280e22366366e42f69   (original independently reviewed PR #76 candidate head)
PARENT_2  = 862c7c579cc667c7ed2bae85b4b4fbbb3dfa8fba   (= accepted main, PR #73 merge)
MERGE_BASE(P1,P2) = fb3148b46a9638167168a46cb170902a4ad9e8d2
```

- Fresh `git clone` + `git fetch --all --prune` + `git checkout --detach cf413b0…`; working tree porcelain-clean.
- `origin/main` still `862c7c5…`; `refs/pull/76/head` still `cf413b0…`; PR state `open`, `mergeable=true`, `mergeable_state=clean`.
- **SUBJECT_DRIFT = NONE.** All control-point hashes match the handoff exactly.
- Merge commit metadata: author/committer `root <yglamazdin@gmail.com>`; Conventional-Commit message `merge(nl7): reconcile PR #76 with accepted S17 main without source drift`.

## 2. Git history integrity

- `main` IS ancestor of HEAD (via parent 2); parent 1 IS ancestor of HEAD; merge-base `fb3148b` is ancestor of main.
- **No history rewrite / no force-push:** all 18 previously documented PR #76 heads (3a7acbb…, b7300b2…, a17ecba…, 415ebfd…, 06569ea…, 8330558…, 0fed72f…, d088f9e…, 559f872…, 3d0b55b…, 5e5712e…, a780293…, b094518…, a8b3512…, 2e199d6…, d59258a…, 022a7a3…, 9fed48a…) were independently checked with `git merge-base --is-ancestor` — **18/18 are ancestors of cf413b0**. PR #73 head `baac1378` is an ancestor of current `main` (merge commit `862c7c5`, parents `fb3148b`+`19971a9`).

## 3. Tree reconciliation (blob-level, byte-exact)

Diff-path structure (name-status counts):

```text
base(fb3148b) -> parent1(9fed48a):  56 paths = 55 A + 1 M(docs/work/WORK_QUEUE.md) + 0 D   (PR #76 adds exactly 55 files)
base(fb3148b) -> main(862c7c5):     99 paths = 98 A + 1 M(docs/work/WORK_QUEUE.md) + 0 D   (S17 main side)
main(862c7c5)  -> HEAD(cf413b0):    56 paths = 55 A + 1 M(docs/work/WORK_QUEUE.md) + 0 D
parent1(9fed48a)-> HEAD(cf413b0):   99 paths = 98 A + 1 M(docs/work/WORK_QUEUE.md) + 0 D
```

1. **All accepted `main` files preserved:** full `git ls-tree -r` scan of main (2501 paths) comparing every blob at HEAD — **0 drift** (only intended exception: `docs/work/WORK_QUEUE.md`).
2. **All 55 PR #76 new files preserved:** each added path's blob at parent1 equals its blob at HEAD — **55/55 OK, 0 mismatches** (list in `evidence/pr76_55_blob_identity.txt`).
3. **No lost / extraneous / accidentally changed files:** path-set equality proven — HEAD tree = 2556 paths = exact union of main (2501) and parent1 (2458); the two added-file sets are disjoint (0 common paths). `diff union HEAD` is empty.
4. Science-canonical state blobs identical to main: `project/state.json`, `project/plan.json`, `project/infra-state.json`, `project/infra-plan.json` — all IDENTICAL.

## 4. WORK_QUEUE.md reconciliation

```text
queue blob @ base   fb3148b: 3d511a284caa9623163ca430832262fbcdfb7cfa  (67,261 bytes)
queue blob @ main   862c7c5: 6d278ea6cce6b70375ab136da90b16fae5eaee8e  (80,329 bytes)
queue blob @ parent1 9fed48a: a95c98f1d1f37b1a2670e02d029eb5a23f34df35  (68,156 bytes)
queue blob @ HEAD   cf413b0: f5555fd1079da6acc00051b18d03ea2480fbe286  (81,224 bytes)
```

- Final blob `f5555fd1…` **matches the integrator's published claim byte-for-byte**.
- MAIN queue has BASE as an exact byte prefix (cmp OK).
- **`FINAL == MAIN + ORIGINAL_PR76_APPEND` byte-exact (cmp OK).** Also `FINAL == BASE + MAIN_APPEND + PR76_APPEND` byte-exact.
- PR76_APPEND = 895 bytes = exactly the two original NL7 records (R1.0 and R1.1), appended in original order, **occurring exactly once** in the final file and **zero times** in the main queue (no duplication). MAIN_APPEND occurs exactly once.

`FINAL_WORK_QUEUE = MAIN_WORK_QUEUE + ORIGINAL_PR76_APPEND` — **PROVEN**.

## 5. S17-R3 × NL7 compatibility (code review + independent falsifiers)

Shared-surface check: both directions depend on the same strict parsers `hinge_family/oxdna_topology.py` / `oxdna_conf.py`; no import cycles or duplicate parsers; test suites are disjoint (`tests/` diff main→HEAD adds only `tests/test_alt_pair_source_gate.py`).

Direction semantics re-derived from `oxdna_topology.py`: row = `<strand> <base> <n3> <n5>`, `n3` toward the strand's 3′ side, `n5` toward 5′, `-1` = none. The gate's `_verified_terminal_segment` requires `n3 == -1` for a 3p terminus (traverses via `n5`, returns bases reversed → conventional 5′→3′) and `n5 == -1` for 5p (traverses via `n3`); occupancy indexing `rows[cursor][3 if 3p else 2]` is consistent. **n3/n5 and 3′/5′ handling is CORRECT** (independently exercised by probes P4–P6/P9 below).

Independent adversarial probes (my own fixtures, not the repo's tests — `evidence/probe_r12_v2.py/.out`):

```text
P1 valid fixture with unwrapped-PBC coordinates (x0=1000/2000 vs box 30) -> TEST_FIXTURE_STATIC_INPUTS_OK  (no false rejection)
P2 NaN simulation box            -> BLOCKED_SOURCE
P3 zero-length orientation       -> BLOCKED_SOURCE
P4 A/B-swapped reuse of same 5p termini (two pairs, roles swapped) -> BLOCKED_SOURCE, "nucleotide already assigned"
P5 internal (non-terminal) anchor, in-bounds index                  -> BLOCKED_SOURCE, "internal anchor"
P6 correct sequence declared at wrong polarity (5p terminus as 3p)  -> BLOCKED_SOURCE, polarity reason
P7 same-size SHA-256 tamper      -> BLOCKED_SOURCE, "SHA-256 mismatch"
P8 rights=RESTRICTED             -> BLOCKED_SOURCE, "RIGHTS_NOT_CLEARED"
P9 topology-unbound overhang index (numeric-in-bounds, not a terminus) -> BLOCKED_SOURCE
```

Path/size/digest controls (`_read_verified_file`): absolute path, `..` traversal, symlink, >16 MiB cap, declared-size mismatch, non-64-hex digest — all rejected fail-closed (covered by the 42 module tests, all green in the 972 run). Unknown sources (`status=UNKNOWN` with concrete pins forbidden) and unconfirmed rights can never produce a PASS; the real source pack correctly yields `BLOCKED_SOURCE`.

Test-count arithmetic: main alone has 930 `test_` methods; HEAD has 972 = 930 + 42 new (module `tests/test_alt_pair_source_gate.py`, 42 methods). All pre-existing test files are blob-identical to main → **no S17 or NL5 regression surface touched**.

## 6. Mandatory tests and harness (this session, exact tree cf413b0)

```text
python3 -m unittest discover -s tests -t .                         -> Ran 972 tests in 54.467s — OK, exit 0
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .   -> exit 0
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .            -> exit 0 (blocking: 0)
PYTHONPATH=scripts python3 -m harness.work_cli validate \
  docs/work/executions/EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1            -> exit 0
PYTHONPATH=scripts python3 -m knowledge_pack.alt_pair_source_gate \
  docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json \
  --candidate S23_NARCISSUS_ECHO --root .                                -> BLOCKED_SOURCE, exit 2
```

The real-source `BLOCKED_SOURCE`/exit-2 is the **correct fail-closed** result (SOURCE_BYTES_NOT_OBSERVED for Narcissus/Echo topology+configuration; Nanobase CAD bytes and licenses unconfirmed).

## 7. Hosted CI on exact HEAD (GitHub API, read-only)

- Run `39868768984` (`hosted-ci`, event `pull_request`, branch `work/prep-nl7-alt-assembly-benchmark-r1`): `head_sha = cf413b053677de17beaf2dcf3ce9b86868361b3e`, **status completed / conclusion success**.
- Check-run "RC0 hosted validation (H0)": completed/success; steps Check 1/5 … Check 5/5 (machine contracts JSON, harness consistency, passports/events integrity, workflow negative-control lint NC-1..NC-7, validation-gate unit tests) — **all success**; 0 failed steps.
- Local independent 972/972 regression on the same tree corroborates the hosted result.

## 8. Prior non-blocking findings N1–N5 (carry-over assessment)

- **N1** (non-dict manifest root → uncaught `AttributeError` in `evaluate()`, exit 1 instead of clean exit 2): **still present, reproduced independently** (`evidence/probe_n1_n4.out`: `[]`/`"str"`/`null` → exit 1 + traceback; never 0 — fail-closed preserved, diagnostics dirty). Code blob unchanged from the previously reviewed subject, so this remains the known deferred item. NON-BLOCKING.
- **N2** (stale top-level pins in `evidence-map.json` reflect R1.0; R1.1/R1.2 amendments are accurate): blob unchanged; assessment carries over. NON-BLOCKING (doc hygiene).
- **N3** (WORK_QUEUE lacks an R1.2 row): still true at HEAD — the append contains exactly the R1.0 and R1.1 records (verbatim per integration mandate); R1.2 is documented in event 0006 + evidence-map + summary. NON-BLOCKING (doc-sync, must not be "fixed" by editing the verbatim append).
- **N4** (`Path("./x")` normalizes away the `.` part-check): cosmetic; probe P-N4 shows such a path still fails closed ("missing or outside-root source file"); digest pin binds content. NON-BLOCKING.
- **N5** (RED-run logs expired on GitHub Actions): historical; run existence/head-SHAs were API-verified earlier and RED behaviors are re-covered by the repo's 42 negative tests plus my independent probes P2–P9. NON-BLOCKING.

## 9. Blocking findings

**NONE.** No defect requiring repair of the integration was found.

New non-blocking observations (this review):
- **R-N1:** the two appended NL7 queue rows still say "33 new tests" (R1.0-era count; module now has 42). This is faithful verbatim preservation of the original PR #76 append, consistent with the integration mandate; a future append-only queue record may note the current count. No action required for this merge.
- **R-N2:** GitHub combined commit-status API for cf413b0 reports `pending` with 0 statuses (branch gating uses the single required check-run, which is green; `mergeable_state=clean`). Cosmetic API semantics only.

## 10. Scientific constraints confirmed

```text
SCIENCE_RUNS        = 0   (no MD, relaxation, E5, or any scientific computation was run by this review)
S17_FOLLOWER        = NOT_RECONSTRUCTED   (S17 summary and receipts unchanged from accepted main)
NL7_SOURCE          = BIBLIOGRAPHIC / BLOCKED_SOURCE  (pack claim_ceiling=BIBLIOGRAPHIC, scientific_runs=0; gate fail-closed on real pack)
ASSEMBLY_VALIDATED  = false   (S17 receipt claim: "Never ASSEMBLY_VALIDATED")
NL5 / NL6 / NL7     = UNCHANGED (state/plan/infra blobs identical to main)
```

## 11. Verdict

### FINAL VERDICT: **PASS**

The two-parent merge `cf413b053677de17beaf2dcf3ce9b86868361b3e` (TREE `560dc913a71a237d3c452a5a2e492e213b232911`) preserves every accepted `main` blob, preserves all 55 PR #76 blobs byte-identically, reconciles `docs/work/WORK_QUEUE.md` as exact `MAIN + ORIGINAL_PR76_APPEND`, adds no extraneous or lost files, keeps both parent histories intact without rewrite, passes the full 972-test regression locally on the exact tree, passes all harness checks, and is covered by hosted CI success on the exact SHA. Prior deferred non-blocking findings N1–N5 remain non-blocking and are documented above.

This PASS covers **integration reconciliation only**. Per the Issue #77 handoff, a **distinct fresh exact-head VERIFIER** must independently confirm the same HEAD/TREE, Git identity, queue proof and regression before the owner-authorized Director merge. This report is not a merge authorization and does not raise any scientific status.

## 12. Evidence index (committed in branch `review/pr76-main-integration-r1`)

```text
docs/work/executions/EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1/review/REVIEWER_INTEGRATION_R1/
  REVIEW_PR76_MAIN_INTEGRATION_R1.md      (this report)
  evidence/session.meta.txt               (session ID, host, tool versions, commands)
  evidence/git_identity.txt               (HEAD/TREE/parents/ancestry/no-rewrite 18/18)
  evidence/tree_reconciliation.txt        (diff counts, 55/55 blob identity, 0 main drift, path-set equality)
  evidence/work_queue_reconciliation.txt  (4 blob SHAs, byte-exact cmp results, SHA-256 of all snapshots)
  evidence/pr76_55_blob_identity.txt      (per-file blob equality list)
  evidence/unittest_972.log               (Ran 972 tests — OK)
  evidence/harness_check_consistency.log / harness_workflow_lint.log / harness_work_cli_validate.log
  evidence/gate_real_source_pack.out      (BLOCKED_SOURCE, exit 2)
  evidence/commands_exitcodes_ci.txt      (exit codes + hosted CI facts)
  evidence/probe_r12_v2.py / .out         (independent P1–P9 falsifiers incl. unwrapped-PBC positive)
  evidence/probe_n1_n4.py / .out          (N1/N4 carry-over reproduction)
  evidence/SHA256SUMS.txt                 (digests of all evidence files)
```
