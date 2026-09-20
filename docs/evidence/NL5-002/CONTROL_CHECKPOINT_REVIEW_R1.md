# NL5-002/CONTROL_CHECKPOINT_REVIEW_R1 — Fresh independent control-checkpoint review of `control/nl5-002-terminal-decision-r1` (PR #44)

```text
REVIEW_ID         = NL5-002/CONTROL_CHECKPOINT_REVIEW_R1
REVIEW_DATE_UTC   = 2026-09-20T11:51:14Z (real `date -u` at write time)
REVIEW_VERDICT    = PASS
REVIEWED_HEAD     = 8d1eafd27c276ec26cc4a5cb4fad86c0c6c98713
                    (live-resolved `git rev-parse origin/control/nl5-002-terminal-decision-r1`
                     after a fresh `git fetch origin --prune`; == `8d1eafd` cited in the subject)
REVIEWED_TREE     = 9388bf2ed2c99ff9305bd908ffb670b54ec1061f
REVIEWED_BASE     = 7504b38110aa0694495b037d11f07f9afee467de (== origin/main, PR #43 merge commit)
ROLE              = REVIEWER (fresh independent session; control checkpoint review)
DIFF              = 7504b38110aa0694495b037d11f07f9afee467de..8d1eafd27c276ec26cc4a5cb4fad86c0c6c98713
                    (13 files: project/state.json, scheduler-policy.v1.json, 5 evidence docs,
                     WO-NL5-002-E-R1.md, README, ROADMAP, WORK_QUEUE, AGENT_START, SESSION_LOG)
```

**Note on the subject string.** The review subject cited the base as
`7504b38110aa0694495b037d11f079afee467de` (39 chars — one hex character dropped).
The live-resolved merge commit is `7504b38110aa0694495b037d11f07f9afee467de`
(40 chars; prefix `7504b38` matches the subject string). All checks below use the
live-resolved object.

## Independence statement

This session is a fresh independent REVIEWER. It did not author any commit in the
reviewed diff, did not participate in the control session that produced it, and did
not inherit any verdict from a previous review/verify session. Every fact below was
re-derived mechanically from git objects (rev-parse / cat-file / merge-base / blob
comparison) in a dedicated detached worktree at the exact reviewed HEAD
(`/tmp/review-check-nl5-002`, HEAD = `8d1eafd27c27…`, tree = `9388bf2ed2…`). The
three repository gates (unittest / check-consistency / workflow_lint) were executed
fresh in that worktree by this session. Prior PASS verdicts were verified only as
durable artifacts (refs + evidence-file contents), never as trusted inputs.

## Checklist results

### 1. Canonical state discipline — PASS

Facts (all read from `project/state.json` @ `8d1eafd`):

- `task_status.NL5-002 = "WAITING_HUMAN"` (diff vs base: `"READY"` → `"WAITING_HUMAN"`;
  not ACCEPTED). `WAITING_HUMAN` is a documented allowed status in
  `HARNESS_CONTROL.md` line 17 («Допустимы `FIX_REQUIRED`, `INCONCLUSIVE`, `BLOCKED`,
  `WAITING_HUMAN`, `EPOCH_INVALIDATED`, `CANCELLED»`).
- `stage_status.NL5 = "IN_PROGRESS"`; `execution.external_reproductions = 0`;
  `frontier = "NL5"`; `next_work_order = "NL5-002"`. `NL5-002` is a task id in
  `project/plan.json`, so check-consistency passes with it (confirmed by gate run).
- `task_status.NL6-001 = "PLANNED"` (not READY).
- Key-set equality with `project/plan.json` verified mechanically: task_status keys ==
  plan task-level ids (19/19, no extras/missing); stage_status keys == plan stage ids
  (NL0–NL8, 9/9); experiment_status keys == plan experiment ids (E0–E6, 7/7).
- state.json diff vs base touches ONLY `task_status.NL5-002` and `open_decisions`.

### 2. No scientific claim change anywhere in the diff — PASS

Mechanical scan of every added line of the full diff:

- No sentence claims NL5-002 or NL5 ACCEPTED. The only added-line "ACCEPT" hits are:
  a carried review quoting NL5-001 `ACCEPTED` (historical, true), the phrase
  "acceptable pre-data" (unrelated), and the explicit statement that the
  `NL5=ACCEPTED / external_reproductions=1` transition «НЕ применяется».
- No MATCH claim for 0b or 32b anywhere; added lines state
  `0b = MISMATCH`, `32b = MISMATCH`, `11b = MATCH`, `53b = MATCH`, WO-level
  `MISMATCH` on all surfaces (state.json, scheduler notes, README, ROADMAP,
  WORK_QUEUE, AGENT_START, SESSION_LOG, DIRECTOR_DECISION_R1, WO, freeze record).
- No threshold/envelope change: every envelope/threshold mention is preservative
  («НЕ менять NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE и threshold'ы R1»; «не меняется»).
  The envelope numbers quoted in DIRECTOR_DECISION_R1.md
  ([65.095434789, 67.236579608] / [72.165683993, 74.533109426] /
  [77.4927314, 79.877463339] / [131.049227687, 135.285186059] and statistics
  68.389781796 / 73.560609814 / 75.180138343 / 132.41188514) are byte-identical to
  the frozen B-R2 evidence already on main
  (`docs/work/executions/EX-NL5-002-B-R2/events/0004-external-run-completed.json`,
  `evidence/analysis/campaign_*.json`). No new measured values were introduced.
- 74b: produced nowhere; all added-line 74b mentions are NOT_MEASURED / KNOWN_GAP /
  «ЗАПРЕЩЁН» / forbidden variants. R1 disposition and B-R1
  INCONCLUSIVE+PORTABILITY_FINDING are preserved verbatim on all surfaces
  (32 added-line hits for INCONCLUSIVE, 48 for MISMATCH; WO «Жёсткие запреты» §
  explicitly forbids reclassifying B-R1/B-R2).

### 3. open_decisions — PASS

- The previous NL5-002-DISPOSITION question is gone: `open_decisions` contains exactly
  one item, `NL5-ACCEPTANCE-POLICY` (kind OWNER_DECISION, record =
  DIRECTOR_DECISION_R1.md), whose question text itself records the closed disposition
  ("NL5-002 is closed as terminal verified MISMATCH / NOT accepted ... PR #43 merged
  7504b38") and asks only the genuinely open acceptance-policy question, with optional
  sub-items (timing of bounded packaging repair v0.1.2; availability of optional P3).
- Nothing re-opens a decided question: DIRECTOR_DECISION_R1.md Дополнение 3 §4 lists
  exactly the same three open items and §3 records platform-sensitivity as CHOSEN by
  the owner. "What next" is not posed as an open question on any surface.

### 4. Merge/gate facts asserted in the surfaces — PASS (mechanically verified), one rendering defect noted (FINDING-1)

- PR #43 merge commit live-resolves to `7504b38110aa0694495b037d11f07f9afee467de`,
  which is exactly `origin/main`; its parents are `48c55b3c4acdd2264527083e3072757be8bd9ada`
  and `4c67e211f0db78c90366d32f643de92089ed190c` (second parent = integration head).
- `git merge-base --is-ancestor 4c67e211f0db78c90366d32f643de92089ed190c origin/main`
  → exit 0 (PASS).
- Refs exist on origin with the cited shas:
  `review/nl5-002-integration-r1` = `61edc42a33cead5b1c084525df7c4dcd66177487`;
  `review/nl5-002-e-preregistration-r1` = `1f8c063e6c620ec6f8caa804954bf861eb76f13d`;
  `verify/nl5-002-e-preregistration-r1` = `bd25baf325987656eddd8a5b2ab36065f0170d5c`.
  Their evidence files carry PASS verdicts:
  FRESH_INTEGRATION_REVIEW_R1.md (`REVIEW_VERDICT = PASS`, lines 7 and 154),
  FRESH_PREREGISTRATION_REVIEW_R1.md (`REVIEW_VERDICT = PASS`, lines 5 and 281),
  FRESH_PREREGISTRATION_VERIFY_R1.md (`VERIFY_VERDICT = PASS`, lines 8 and 190).
- WO freeze commit `4d6542fda81084dced2578f3e008c8c8e0705a5a` (tree
  `7651569ac8d0e93c0cc7614cb692945ad5bd0c98`) is an ancestor of the reviewed HEAD
  (`git merge-base --is-ancestor` → PASS).
- FINDING-1 (minor, non-blocking): the full-SHA rendering of the merge commit is
  corrupted in three surface locations — DIRECTOR_DECISION_R1.md lines 154 and 156,
  SESSION_LOG.md line 556 (P2 entry) — as `7504b38110aa0694495b037d11f079afee467de`
  (39 chars; `git cat-file -t` rejects it; one 'f' dropped at position 30 of the true
  sha). Introduced in branch commit `4d6542f`. Not a false fact about reality: every
  load-bearing identifier around it is correct (prefix `7504b38`/`7504b381` used
  consistently in state.json, ROADMAP, README, WORK_QUEUE, AGENT_START, scheduler
  notes; parents pair `48c55b3 + 4c67e21` recorded in the same lines uniquely
  identifies the true merge object), and all mechanical gate facts listed above are
  TRUE. Recommended: bounded one-line-per-location correction in the next control
  commit; no evidence chain depends on the corrupted rendering.
- Hosted-CI run outcomes (35480129676 / 35506654447 SUCCESS) are asserted by the
  surfaces; the `gh` CLI is not available in this environment and the runs were not
  independently re-queried (see Limitations). Everything locally verifiable about the
  merge (object identity, parents, ancestry, tree equality of main vs integration
  head — `641c9cc7…` recorded in the merge commit object) was verified TRUE.

### 5. Freeze discipline — PASS

- WO document blob is IDENTICAL at the freeze commit and at the reviewed HEAD:
  `git rev-parse 4d6542f:docs/work/WO-NL5-002-E-R1.md` =
  `git rev-parse HEAD:docs/work/WO-NL5-002-E-R1.md` =
  `98719af3d2c4294dc25a51918a2b7f0c7fc1cb43`.
- Both preregistration side branches are parented exactly at the WO freeze commit:
  `1f8c063e6c…^@` = `4d6542fda81084dced2578f3e008c8c8e0705a5a` and
  `bd25baf325…^@` = `4d6542fda81084dced2578f3e008c8c8e0705a5a` (single parents each).
- `PREREGISTRATION_FREEZE_R1.md` binds the same subject: WO HEAD
  `4d6542fda81084dced2578f3e008c8c8e0705a5a`, WO TREE
  `7651569ac8d0e93c0cc7614cb692945ad5bd0c98` (lines 11–12), and both gate refs.
- It honestly records dispatch NOT STARTED:
  `PLATFORM_EXECUTION = NOT_STARTED / BLOCKED_ON_P1_AVAILABILITY` (line 109) with
  P1 = author WSL2 environment unavailable (lines 97–100), an explicit resume
  condition (owner grants P1 access → dispatch strictly per frozen WO, else new WO
  revision; lines 110–112), and explicit prohibitions of P1 substitution and of a
  P2-only "half" paired run (lines 113–115).
- No execution directory `EX-NL5-002-E-R1` exists (`docs/work/executions/` has no
  NL5-002-E* entry), and the diff contains no campaign data: the 13 changed files are
  docs/config/state only (no experiments/, no runs/, no trajectory/analysis
  artifacts).

### 6. Surfaces consistency — PASS

- README, ROADMAP, WORK_QUEUE, AGENT_START, SESSION_LOG and the scheduler-policy
  notes all state the same facts, agreeing with state.json and each other:
  NL5-002 = WAITING_HUMAN terminal verified MISMATCH / NOT accepted (canonical
  2026-09-20); platform WO `WO-NL5-002-E-R1` preregistration FROZEN
  (Reviewer `1f8c063` + Verifier `bd25baf` PASS, freeze record
  PREREGISTRATION_FREEZE_R1); dispatch = NOT STARTED / BLOCKED_ON_P1_AVAILABILITY
  with P1-substitution / P2-only-paired-run forbidden; NL6-001/E5 = PLANNED, LOCKED
  until separate NL5 acceptance; open owner questions = NL5 acceptance policy,
  optional v0.1.2, optional P3.
- Scheduler policy: `revision` updated `NL-N5-2026-09-18-R2` → `NL-N5-2026-09-20-R1`;
  both JSON files parse (`json.load` OK); scheduler `current_checkpoint = "NL5"`,
  `next_work_order = "NL5-002"` agree with state.json.
- Pre-existing (not introduced by this diff, out of change scope): ROADMAP writes
  `E1 = SUPPORTED` while state.json `experiment_status.E1 = "RUN"` — this dual
  convention (executed vs hypothesis-supported, from the NL2-002 acceptance) exists
  verbatim on origin/main; unchanged here.

### 7. Gates in a detached worktree at the reviewed HEAD — PASS

Executed by this session in `/tmp/review-check-nl5-002`
(HEAD = `8d1eafd27c276ec26cc4a5cb4fad86c0c6c98713`):

- `python3 -m unittest discover -s tests -t .` → `Ran 369 tests in 11.868s` / `OK`,
  exit 0 (369/369, as expected).
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` → exit 0,
  `"ok": true`, `"errors": []`; echoes the exact reviewed head/tree
  (`8d1eafd27c27…` / `9388bf2ed2…`), frontier NL5, next_work_order NL5-002, counts
  stages 9 / tasks 19 / experiments 7. Benign warning "git metadata unavailable".
- `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` → exit 0, summary
  workflows 1, violations 0, blocking 0.

### 8. Conventional Commits — PASS

All five new commits of the branch (`origin/main..8d1eafd`) follow the Conventional
Commits shape with repo-precedent `control(...)` types:

```text
15dc01a control(nl5-002): DIRECTOR_DECISION_R1 proposal - ...
cdcdad7 control(nl5-002): record hosted CI success on PR #43 head 4c67e21 ...
9c0dd43 control(nl5-002): fresh tooling/integration Verifier PASS (776bb82) - ...
4d6542f control(nl5-002): canonical terminal disposition applied - ...
8d1eafd control(nl5-002-e): PREREGISTRATION_FREEZE_R1 - ...
```

## Verdict

```text
REVIEW_VERDICT = PASS
```

The checkpoint applies the owner-pre-approved mission faithfully: NL5-002 lands as
WAITING_HUMAN with the immutable terminal MISMATCH disposition (NOT accepted), the
platform-sensitivity WO is frozen with both preregistration gates PASS at the exact
WO freeze commit, dispatch is honestly stopped on P1 availability, and no scientific
claim moved anywhere in the diff.

## Limitations and risks (honest)

1. FINDING-1 (documented above): 39-char corrupted full-SHA rendering of the PR #43
   merge commit in DIRECTOR_DECISION_R1.md (2 locations) and SESSION_LOG.md (1
   location); introduced in `4d6542f`; non-blocking because the object is uniquely
   identified by the recorded parents pair and correct prefixes everywhere; bounded
   surface correction recommended in the next control commit.
2. Hosted CI outcomes (runs 35480129676, 35506654447) and the PR-level merge act were
   taken from the recorded surfaces; `gh`/GitHub API re-query was not possible in
   this environment. All git-side counterparts (merge object, parents, ancestry,
   tree, refs) were verified locally and are consistent with the CI claims.
3. P1 unavailability and the outenemy/P2 environment identity are execution-host
   claims recorded by the Director freeze flow; they are not mechanically verifiable
   from a git worktree. The freeze record handles them correctly (honest STOP,
   resume condition, substitution prohibitions), which is the checkable part.
4. The wall-budget feasibility numbers in the preregistration verify (≤72 h/platform)
   are design plausibility claims inherited from B-campaign calibration, not
   measurements of the future campaign.
5. The "git metadata unavailable" warning from check-consistency inside a linked
   worktree is benign: the tool still resolved and echoed the exact reviewed
   head/tree.
6. Pre-existing surface nuance (unchanged by this diff): ROADMAP's `E1 = SUPPORTED`
   vs state.json `experiment_status.E1 = "RUN"` dual convention.
