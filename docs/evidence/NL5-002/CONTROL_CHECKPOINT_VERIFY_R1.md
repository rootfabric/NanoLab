# CONTROL_CHECKPOINT_VERIFY_R1 — NL5-002 Terminal Decision: Independent Verify R1

Verify id                = NL5-002/CONTROL_CHECKPOINT_VERIFY_R1
Date (UTC)               = 2026-09-20T12:07:30Z
Verifier                 = fresh independent verifier session (not the author, not the Director,
                           not the Reviewer of CONTROL_CHECKPOINT_REVIEW_R1; no shared conversation,
                           no inherited verdicts; own detached worktree /tmp/verify-nl5-002-terminal-decision)
VERIFY_VERDICT           = PASS

VERIFIED_HEAD            = c55229a5619a1d944f1c6f360e5f4e3a254a49c4
VERIFIED_TREE            = 8dbffb7a29beb1318c3f92b8134209b86438dd99
REVIEWED_HEAD_BINDING    = 8d1eafd27c276ec26cc4a5cb4fad86c0c6c98713 (ancestor of VERIFIED_HEAD; post-review delta = exactly one bounded fix commit c55229a, 2 files / 3 lines, SHA-rendering only)

Subject                  = origin/control/nl5-002-terminal-decision-r1 (PR #44), live-resolved by this
                           verifier after `git fetch origin --prune`; live head == expected
                           c55229a5619a1d944f1c6f360e5f4e3a254a49c4 (no drift).
Branch base (whole branch) = 7504b38110aa0694495b037d11f07f9afee467de (== origin/main, PR #43 merge commit) — confirmed live.

Independence statement: this verify was executed by a fresh session that performed every check itself
(fetch, live ref resolution, GitHub API queries, unittest/consistency/lint runs, blob comparisons, diffs).
From docs/evidence/NL5-002/CONTROL_CHECKPOINT_REVIEW_R1.md on review/nl5-002-terminal-decision-r1
(@ 9c5d296c61298b8ae62ffb9cdeaa3ee5ab8d2a3e) ONLY the binding fields REVIEWED_HEAD / REVIEWED_TREE /
REVIEWED_BASE were read (grep-bounded); the reviewer's verdict and reasoning were NOT read and NOT used.

## Per-check results

### Check 1 — Subject binding: PASS
- Live `origin/control/nl5-002-terminal-decision-r1` = c55229a5619a1d944f1c6f360e5f4e3a254a49c4
  (tree 8dbffb7a29beb1318c3f92b8134209b86438dd99) — equals expected subject.
- PR #44 live (GitHub API, unauthenticated): state=open, merged=false,
  head_sha=c55229a5619a1d944f1c6f360e5f4e3a254a49c4 (head_ref control/nl5-002-terminal-decision-r1),
  base=main@7504b38110aa0694495b037d11f07f9afee467de — equals live branch head.
- Binding fields read: REVIEWED_HEAD = 8d1eafd27c276ec26cc4a5cb4fad86c0c6c98713,
  REVIEWED_TREE = 9388bf2ed2c99ff9305bd908ffb670b54ec1061f,
  REVIEWED_BASE = 7504b38110aa0694495b037d11f07f9afee467de (== origin/main).
- `git merge-base --is-ancestor 8d1eafd… c55229a…` → PASS (REVIEWED_HEAD is ancestor of verified HEAD).
- Commits after REVIEWED_HEAD: exactly ONE — c55229a "control(nl5-002): fix truncated merge-commit SHA
  rendering in surfaces …". `git diff --stat 8d1eafd c55229a`:
    docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md | 4 ++--
    docs/work/SESSION_LOG.md                      | 2 +-
    2 files changed, 3 insertions(+), 3 deletions(-)
  Full patch inspected line-by-line: ONLY the 3 SHA-string lines changed, each correcting the corrupted
  40-hex rendering `7504b38110aa0694495b037d11f079afee467de` → `7504b38110aa0694495b037d11f07f9afee467de`
  (truncated/corrupted glyph) in DIRECTOR_DECISION_R1.md (2 lines) and SESSION_LOG.md (1 line).
  Delta is exactly the bounded surface fix.

### Check 2 — Machine state validation at exact HEAD: PASS
Executed in own detached worktree at c55229a (tree 8dbffb7a confirmed by `git rev-parse`):
- `python3 -m unittest discover -s tests -t .` → `Ran 369 tests in 11.295s`, result `OK`, exit 0.
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` → ok=true, errors=[],
  head echo = c55229a5619a1d944f1c6f360e5f4e3a254a49c4, tree echo = 8dbffb7a29beb1318c3f92b8134209b86438dd99
  (both equal VERIFIED_HEAD / VERIFIED_TREE); frontier=NL5, next_work_order=NL5-002.
  (Warning "git metadata unavailable" / branch=null emitted by the tool in this detached worktree; the
  head/tree echoes still match the verified values exactly — see limitations.)
- `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` → ok=true, workflows=1, violations=0,
  blocking=0.
- `python3 -c` JSON-parse: project/state.json OK; config/control/harness/scheduler-policy.v1.json OK.

### Check 3 — state.json semantics: PASS
- task_status["NL5-002"] = "WAITING_HUMAN" (== WAITING_HUMAN; != ACCEPTED — terminal verified MISMATCH,
  NOT accepted).
- stage_status["NL5"] = "IN_PROGRESS".
- execution.external_reproductions = 0.
- frontier = "NL5"; next_work_order = "NL5-002".
- task_status["NL6-001"] = "PLANNED".
- Key sets exactly equal plan.json ids: task_status (19 ids) == plan.tasks ids; stage_status (9 ids:
  NL0–NL8) == plan.stages ids; experiment_status (7 ids: E0–E6) == plan.experiments ids.
- open_decisions: contains exactly one entry, id "NL5-ACCEPTANCE-POLICY" (OWNER_DECISION);
  "NL5-002-DISPOSITION" absent (by id and by raw JSON text).

### Check 4 — Immutability scan (git diff 7504b38..c55229a): PASS
Changed files (13): README.md, config/control/harness/scheduler-policy.v1.json, docs/ROADMAP.md,
docs/evidence/NL5-002-E/FRESH_PREREGISTRATION_REVIEW_R1.md (A),
docs/evidence/NL5-002-E/FRESH_PREREGISTRATION_VERIFY_R1.md (A),
docs/evidence/NL5-002-E/PREREGISTRATION_FREEZE_R1.md (A),
docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md (A),
docs/evidence/NL5-002/FRESH_INTEGRATION_REVIEW_R1.md (A),
docs/work/AGENT_START.md, docs/work/SESSION_LOG.md, docs/work/WO-NL5-002-E-R1.md (A),
docs/work/WORK_QUEUE.md, project/state.json.
- No change to any file under releases/, docs/work/executions/, experiments/, scripts/, tests/, and none
  to config/control/harness/work-event.schema.v1.json — confirmed by name-grep over the full diff: none.
- Scientific evidence docs vs base (blob compare):
    docs/evidence/NL5-002/FRESH_REVIEW_R1.md         UNCHANGED (blob bbf43a29d5d1d02b0647b34c69872ae9ec81d1d4)
    docs/evidence/NL5-002/FRESH_VERIFY_R1.md         UNCHANGED (blob 004452ae6341914da35e6184a01e08bfbd477099)
    docs/evidence/NL5-002/DIRECTOR_PRE_MERGE_R1.md   UNCHANGED (blob 4b73925b659c737b38c0204cc7c8354cd3cae0d7)
    docs/evidence/NL5-002/FRESH_INTEGRATION_VERIFY_R1.md  absent at base AND at HEAD (see limitations —
      the file exists only on the unmerged branch verify/nl5-002-integration-r1 @ 776bb82, blob
      8729150e510aa8b5ede8e79c5bb2e7196258eb45); absent-at-both-ends = unchanged, no base evidence doc
      was modified.
- Merged scientific facts quoted without alteration in changed surfaces: DIRECTOR_DECISION_R1.md states
  `0b = MISMATCH · 11b = MATCH · 32b = MISMATCH · 53b = MATCH · 74b = NOT_MEASURED/KNOWN_GAP` —
  matches the immutable science exactly. All 11 quoted envelope/median values
  (65.095434789, 67.236579608, 72.165683993, 74.533109426, 73.560609814, 75.180138343, 77.4927314,
  79.877463339, 131.049227687, 135.285186059, 132.41188514) each found verbatim in 2 base-era science
  docs at 7504b38.

### Check 5 — Freeze chain at exact HEAD: PASS
- docs/work/WO-NL5-002-E-R1.md blob at HEAD = 98719af3d2c4294dc25a51918a2b7f0c7fc1cb43 ==
  blob at 4d6542fda81084dced2578f3e008c8c8e0705a5a (byte-identical WO).
- `git merge-base --is-ancestor 4d6542f… c55229a…` → PASS.
- Origin refs (live after fetch): review/nl5-002-e-preregistration-r1 @ 1f8c063e6c620ec6f8caa804954bf861eb76f13d
  (parent = 4d6542fda81084dced2578f3e008c8c8e0705a5a ✓);
  verify/nl5-002-e-preregistration-r1 @ bd25baf325987656eddd8a5b2ab36065f0170d5c
  (parent = 4d6542fda81084dced2578f3e008c8c8e0705a5a ✓).
- docs/evidence/NL5-002-E/PREREGISTRATION_FREEZE_R1.md at HEAD binds:
  `WO HEAD (freeze commit) = 4d6542fda81084dced2578f3e008c8c8e0705a5a`,
  `WO TREE = 7651569ac8d0e93c0cc7614cb692945ad5bd0c98`,
  `DISPATCH = NOT STARTED`, `PLATFORM_EXECUTION = NOT_STARTED / BLOCKED_ON_P1_AVAILABILITY` (honest stop;
  P1 = author WSL2 environment).
- `git ls-tree -r HEAD docs/work/executions/ | grep EX-NL5-002-E` → no matches: no EX-NL5-002-E-*
  execution exists.

### Check 6 — Tooling review gate existence: PASS
- origin ref review/nl5-002-integration-r1 @ 61edc42a33cead5b1c084525df7c4dcd66177487 (live).
- Parent = 4c67e211f0db78c90366d32f643de92089ed190c ✓.
- Its evidence file docs/evidence/NL5-002/FRESH_INTEGRATION_REVIEW_R1.md on that branch contains
  `REVIEW_VERDICT = PASS` and `REVIEWED_INTEGRATION_HEAD = 4c67e211f0db78c90366d32f643de92089ed190c`.

### Check 7 — Merge facts: PASS
- origin/main = 7504b38110aa0694495b037d11f07f9afee467de (live).
- Merge commit parents: 48c55b3c4acdd2264527083e3072757be8bd9ada + 4c67e211f0db78c90366d32f643de92089ed190c ✓.
- `git merge-base --is-ancestor 4c67e211f0db78c90366d32f643de92089ed190c origin/main` → PASS.

### Check 8 — Hosted CI (GitHub API, unauthenticated): PASS
| Run | Head SHA | Branch | Event | Status | Conclusion |
|-----|----------|--------|-------|--------|------------|
| 35509262809 | c55229a5619a1d944f1c6f360e5f4e3a254a49c4 (verified HEAD) | control/nl5-002-terminal-decision-r1 | pull_request | completed | success |
| 35508445407 | 8d1eafd27c276ec26cc4a5cb4fad86c0c6c98713 (REVIEWED_HEAD) | control/nl5-002-terminal-decision-r1 | pull_request | completed | success |
| 35506654447 | 7504b38110aa0694495b037d11f07f9afee467de (post-merge main) | main | push | completed | success |
| 35480129676 | 4c67e211f0db78c90366d32f643de92089ed190c (integration head) | integration/nl5-002-r1 | pull_request | completed | success |
(Also observed on the branch: run 35507177404 @ 4d6542f — completed/success; supplementary.)

### Check 9 — Conventional Commits: PASS
6 commits on the branch after base 7504b38, all Conventional (`control(scope): …`):
- 15dc01add46e0b3be58da5de29ba4c39f0a9abc2 control(nl5-002): DIRECTOR_DECISION_R1 proposal …
- cdcdad736408ef84cc3298de1211f9af7e68def6 control(nl5-002): record hosted CI success …
- 9c0dd4305d045af65728dee76c88ba3b6ce69c99 control(nl5-002): fresh tooling/integration Verifier PASS …
- 4d6542fda81084dced2578f3e008c8c8e0705a5a control(nl5-002): canonical terminal disposition applied …
- 8d1eafd27c276ec26cc4a5cb4fad86c0c6c98713 control(nl5-002-e): PREREGISTRATION_FREEZE_R1 …
- c55229a5619a1d944f1c6f360e5f4e3a254a49c4 control(nl5-002): fix truncated merge-commit SHA rendering …

## Honest limitations
1. docs/evidence/NL5-002/FRESH_INTEGRATION_VERIFY_R1.md (named in the immutability set) does not exist in
   main's tree at base 7504b38 nor at verified HEAD; it exists only on the unmerged branch
   verify/nl5-002-integration-r1 @ 776bb82 (blob 8729150e…). The check therefore resolves vacuously
   (absent at both ends = unchanged); the three named docs that do exist are blob-identical to base.
2. check-consistency emitted warning "git metadata unavailable" (branch=null) in this detached worktree;
   its head/tree echoes still equal VERIFIED_HEAD/VERIFIED_TREE exactly, so the required echo-equality
   holds. All other gates in the tool run clean.
3. The reviewer's verdict in CONTROL_CHECKPOINT_REVIEW_R1.md was deliberately not read (only
   REVIEWED_HEAD/REVIEWED_TREE/REVIEWED_BASE, per binding protocol); the PASS here is this verifier's own
   computation, not an endorsement inherited from the review.
4. CI conclusions are GitHub-reported hosted outcomes (api.github.com, unauthenticated); local 369-test
   rerun was executed on this verifier's Linux environment only.
5. This verify validates disposition/freeze bookkeeping at exact HEAD. It does not re-run external
   executions (none exist: EX-NL5-002-E-* absent) and does not alter the immutable science
   (0b MISMATCH, 11b MATCH, 32b MISMATCH, 53b MATCH, 74b NOT_MEASURED).

## Verdict
VERIFY_VERDICT = PASS. Subject binding holds (PR #44 == live branch == c55229a; REVIEWED_HEAD ancestor;
post-review delta = exactly the bounded 3-line SHA-rendering fix), machine state is green at exact HEAD
(369 tests OK, consistency ok, lint blocking=0), state semantics encode WAITING_HUMAN / NOT accepted,
freeze chain intact (WO frozen at 4d6542f, dispatch NOT STARTED / BLOCKED_ON_P1_AVAILABILITY, no
executions), immutability respected, merge facts and CI success verified.
