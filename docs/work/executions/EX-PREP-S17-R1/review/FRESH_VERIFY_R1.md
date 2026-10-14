# FRESH_VERIFY_R1 — independent exact-head verification of work/prep-s17-r1 final state

- `record_kind`: VERIFIER_VERDICT · `issuer_class`: INDEPENDENT_VERIFIER
- **Verdict: VERIFIED** (0 blocking findings; all pins, lineage, delta-discipline, review-chain, integration, machine-gate and claim-ceiling checks pass)
- **verified_head:** `4fe3a6c9aaa39e4d35d3f2f9161c5aa86f177eff` (== `git ls-remote origin refs/heads/work/prep-s17-r1`)
- **verified_tree:** `985adc3cff5623fb8ad88828dd3b09a8f8e77806` (== `git rev-parse 4fe3a6c^{tree}`)
- **Subject branch:** `work/prep-s17-r1` · **Base:** `origin/main` = `32d3c6840341ad3954d5001235a3cc35b8ca0e01`
- Verification date: 2026-10-14T18:24:50Z · Verifier: fresh agent, no prior involvement in this chain

## Method

Fresh clone to `/home/rdpuser/NanoLab/verify-prep-s17-r1`; every pin re-derived via `rev-parse`/`ls-remote`; full diffs inspected; all four machine gates re-executed at the exact FINAL_HEAD; knowledge pack re-validated; import validation independently re-executed against locally pinned Nanobase bytes (sha256 pre-checked against evidence pins) with five negative controls; frozen/protected/scope sweeps at git blob level; GitHub check-runs API queried. Nothing repaired, nothing merged, no force-push, no scientific runs.

## V1 — Pins and lineage: PASS

| Check | Result |
|---|---|
| remote tip of `work/prep-s17-r1` | `4fe3a6c9aaa39e4d35d3f2f9161c5aa86f177eff` == FINAL_HEAD ✓ |
| `4fe3a6c^{tree}` | `985adc3cff5623fb8ad88828dd3b09a8f8e77806` == FINAL_TREE ✓ |
| `origin/main` | `32d3c6840341ad3954d5001235a3cc35b8ca0e01` == BASE ✓ |
| `git merge-base origin/main HEAD` | `32d3c68…` == origin/main ✓ (strict descendant) |
| linear chain base..HEAD (9 commits, all single-parent, 0 merges) | `93cf561 → c78d5ef → 3553e44 → 3cf7818 → d9b7efd → 3e405ab → aacdeb9 → 527f588 → 4fe3a6c` ✓ |
| prior-chain pins | `d9b7efd` (tree `0abed1d`) ✓ · `3e405ab` ✓ · `aacdeb9` ✓ · `527f588` (tree `2428f4c`) ✓ |
| no rewrites | fresh clone; remote tips equal the pinned SHAs; repair tail matches event-0005 subject pin `3e405ab` ✓ |

## V2 — Delta discipline: PASS

`git diff 527f588..4fe3a6c` = exactly one file, `docs/work/WORK_QUEUE.md`, 1 insertion + 1 deletion (one-line replacement of the WO-PREP-S17-R1 row). The replacement adds the declared errata block: *"в этой же строке при R2-ремонте была исправлена одна буква в Acceptance-ячейке R1 ("fresh review PASS" → "fresh re-review PASS") без поэлементного объявления в КОРРЕКЦИЯ R2 — фиксируется здесь"* — i.e. the one-word edit ("fresh review" → "fresh re-review") is declared verbatim. Nothing else changed.

## V3 — Review evidence chain: PASS

| Check | Result |
|---|---|
| `3370be0630e18d2a995a6b1b369284c257401072` on `review/prep-s17-r1` | exists; verdict **FAIL** (1 blocking + 6 minor); reviewed `d9b7efd`/`0abed1d` ✓ |
| `74e6bc9580ddb309df7f21574c30d19b1e5776eb` on `review/prep-s17-r1` (remote tip) | exists; verdict **PASS** (0 blocking, 1 minor MINOR-R2-1); descendant of `3370be0` ✓ |
| `FRESH_REVIEW_R2.json` pins | `reviewed_head` = `527f588207f96371ff664b830eedcc575746f194` ✓, `reviewed_tree` = `2428f4ccfb3ad331b160a9a9613ef4f09009ef5f` == `git rev-parse 527f588^{tree}` ✓ |
| Blocking resolution | `tests/test_knowledge_pack_import.py` present (9 tests; 32+9 = 41 new; suite 679 = 638 base + 41 — re-confirmed by this verification's own gate run) ✓ |

Ancestry note: the review branch is rooted at the R1 subject `d9b7efd` (repo convention — review evidence grows on top of the reviewed subject), so `74e6bc9` is **not** a git-ancestor-descendant of `527f588`/`3e405ab`; the R2 binding is carried inside `FRESH_REVIEW_R2.json`, whose head/tree pins match git exactly. Recorded as an observation, not a finding.

## V4 — Integration integrity: PASS

| Check | Result |
|---|---|
| `project/state.json` blob | `b819755783119ecc56be50cab1bc736c09c85b24` — byte-identical to origin/main ✓ |
| frozen sweep (case-insensitive `frozen` in `git ls-tree -r origin/main --name-only`) | 15 paths, blob-level mismatches: **0** ✓ |
| protected runtime dirs `scripts/{e2,nl4,nl5,r2,hinge_family}` | `git diff origin/main HEAD --name-only -- <dirs>` → empty ✓ |
| diff scope vs origin/main | 20 files, all inside allowed surfaces: WO doc, WORK_QUEUE.md, `EX-PREP-S17-R1/**` (11), `docs/research/S17_*` (2), `scripts/knowledge_pack/**` (3), `tests/test_knowledge_pack*.py` (2) ✓ |

## V5 — Machine gates re-run at FINAL_HEAD: PASS

| Gate | Command | Exit | Observed |
|---|---|---|---|
| unittest | `python3 -m unittest discover -s tests -t .` | 0 | `Ran 679 tests in 50.374s / OK` (expected 679 OK) ✓ |
| check-consistency | `PYTHONPATH=scripts python3 -m harness.cli check-consistency` | 0 | `ok: true`, tasks **19**, stages 9, experiments 7; head/tree == pins ✓ |
| workflow_lint | `PYTHONPATH=scripts python3 -m harness.workflow_lint` | 0 | **blocking 0**, violations 0 ✓ |
| work_cli validate | over all `docs/work/executions/EX-*/` | 0 per dir | **56/56 ok:true, 0 FAIL**; EX-PREP-S17-R1 `ok:true`, HANDOFF_READY, single terminal + sanctioned corrections tail (0005) ✓ |

## V6 — Claim ceiling: PASS

- `validate_pack(docs/research/S17_KNOWLEDGEPACK.json)` → `[]` (exit 0).
- Pack `claim_level` = `PINNED_IMPORT_VERIFIED`; `MODEL_REPRODUCED` appears only in ceiling/rejection context (contract denylist, audit doc, WO constraints). No NL5-acceptance, no E5-executed, no R2-active, no U1-assigned, no runs>0 claims in any changed surface. The single grep hit is a *precondition* statement that explicitly records the opposite current state (`NL5-002=WAITING_HUMAN`, `AUTHOR_U1=NOT_ASSIGNED`, `R2=WAITING_HOST/NOT_ACTIVE`).
- UNKNOWN/UNVERIFIED discipline intact: 7 explicit `missing_inputs`, 6 `known_limitations`; sulcgroup/hinges rights = UNKNOWN/no-license, REFERENCE_ONLY, nothing vendored.
- Digests: all 6 topology/configuration SHA-256 values in `evidence/s17-import-validation-R2.json` match the pack `input_file_manifest`; `pull_release23.zip` `size_bytes` = 20 691 250 829 (minor-1 fix present).
- Independent re-execution (local pinned Nanobase bytes, sha256 pre-checked): NE 14343/161 digest `c227e0b5…`, NE_NB 14011/163 digest `5e7610a8…`, nNE 14343/163 digest `20c39126…` — **all three match evidence R2**.
- Negative controls (own re-execution): non-UTF-8 corruption raises `ImportValidationError`; four linkage corruptions (bogus n3 index, cleared n5, adjacent n3 swap, reciprocal rewire) all yield `ok=false` with chain-integrity `TopologyError` **and** a structural digest differing from baseline — the linkage-sensitivity claimed by repair R2 (minor-6 fix) is real.

## V7 — CI: no check-runs (structural, by design)

`GET /repos/rootfabric/NanoLab/commits/4fe3a6c…/check-runs` → `total_count: 0`; combined status `pending` with 0 statuses; no PR exists for `work/prep-s17-r1`. `hosted-ci.yml` serves **only** `pull_request → main` (TR-PR) and `push → main` (TR-PUSH-MAIN); branch pushes without an open PR intentionally register zero check-runs. CI will execute when the Human-Gate PR to main is opened. Recorded as N/A-structural, not a gate failure.

## Notes / observations (all non-blocking)

1. Review-branch ancestry: `74e6bc9` rooted at `d9b7efd`, R2 binding via evidence-JSON pins (verified exact).
2. Erratum wording says "одна буква" while the task/minor calls it one word — the same edit ("fresh review PASS" → "fresh re-review PASS") is declared verbatim; cosmetic phrasing only.
3. WORK_QUEUE R1 row (preserved prose) says "20 позиций манифеста"; the manifest holds 21 entries at **both** `d9b7efd` and FINAL_HEAD (12 Nanobase + 5 Zenodo + 4 GitHub) — pre-existing cosmetic count, no R2 drift.
4. WORK_QUEUE R1 row says "NL6-001 = LOCKED" while `state.json` has `NL6-001="PLANNED"`; plan.json gates NL6-001 on `depends_on: [NL5-002]` (WAITING_HUMAN), so the substantive restriction holds; conservative wording in preserved R1 prose only.
5. The task brief stated git identity `CONTROL <control@nanolab.local>` was configured globally; it was unset in this environment — verifier set it (repo-local + global) to the pinned identity before committing.

## Verdict

**VERIFIED** — FINAL_HEAD `4fe3a6c9aaa39e4d35d3f2f9161c5aa86f177eff` / FINAL_TREE `985adc3cff5623fb8ad88828dd3b09a8f8e77806` satisfies every pinned check V1–V6; V7 is structurally N/A pending the Human-Gate PR. Merge to `main` remains a Human Gate.
