# DIRECTOR DISPATCH PROOF — F01 / EX-NL5-F01-FROZEN-AUDIT-R1

Append-only Director record (Issue #82 «Director proof protocol»). Issue-comment API
недоступна из этой среды (fine-grained PAT: 403 on issue comments, проверено 2026-10-25),
поэтому proof публикуется здесь (durable Git evidence) вместо комментария к Issue #82.

```text
PROGRAM            = NL5-CLOSE-R1
TASK               = NL5-F01 (Issue #82)
DIRECTOR_SESSION   = DSH session e49ea301c3d2 (central agent, model session)
OBSERVED MAIN_HEAD = 3b567ae33f247b182b2ae451d2cc4598a9e76019   (fresh fetch 2026-10-25)
OBSERVED MAIN_TREE = 560dc913a71a237d3c452a5a2e492e213b232911
FROZEN F2_HEAD     = 60da9a846511265a8ac7564da088c3d74cb073f0  (ancestor of main: YES)
FROZEN F2_TREE     = e565c8a6cee9e829fac14008ebc9c2ea1609931d
HG_B               = APPROVED (HG_B_OWNER_DECISION_R1, main)
U1_HOST            = NOT_ASSIGNED (NATIVE_UBUNTU_EXECUTION_POLICY_R1)
R2_STATUS          = WAITING_HOST / NOT_ACTIVE
NL5-002            = WAITING_HUMAN; old terminal MISMATCH preserved append-only
external_reproductions = 0
```

## Independent Director verification before dispatch (recomputed, not trusted from reports)

```text
git merge-base --is-ancestor 60da9a8… main            -> exit 0
git rev-parse 60da9a8…^{tree}                          -> e565c8a6cee9e829fac14008ebc9c2ea1609931d
sha256(git show F2:docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md)             = 2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d
sha256(git show F2:…/repro-v0-2-freeze-contract-FROZEN_R2.json)               = 7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a
sha256(git show F2:…/repro-v0-2-seed-record-FROZEN_R2.json)                   = 8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28
```

All three match `DIRECTOR_FREEZE_R2.json` byte-for-byte → FROZEN_R2 integrity independently CONFIRMED at dispatch time.

## Dispatch

```text
ROLE            = IMPLEMENTER-AUDITOR (read-only control)
LAUNCHER        = DSH subagent tool (real separate background session)
EXECUTOR_ID     = <appended below after launch by Director addendum commit>
WORKTREE        = /home/rdpuser/NanoLab/nl5-f01-audit
BRANCH          = work/nl5-f01-frozen-audit-r1 (base 3b567ae, non-force push only)
WO              = docs/work/WO-NL5-F01-FROZEN-AUDIT-R1.md (this branch)
ALLOWED PATHS   = WO file; docs/work/executions/EX-NL5-F01-FROZEN-AUDIT-R1/**; WORK_QUEUE.md (1 append)
FORBIDDEN       = canonical state jsons; frozen package mutation; scripts/tests; science runs;
                  paid compute; force-push; direct main write; production Task Bus P2
BUDGET          = offline audit only; wall <= 4h; science_runs = 0
PLANNED AUDIT   = fresh fetch; recompute blob SHA1 + canonical SHA256 (protocol/contract/seed);
                  ancestry/authority chain; feasibility grid N=64 read-back; freeze gate PASS +
                  DISPATCH_BLOCKED check; U1/R2 status; NL5-002 MISMATCH preservation;
                  subagent capability/identity profiling; dup-implementation scan of open PRs
SAFE STOP       = any hash mismatch / forbidden-path need / missing data -> BLOCKED evidence,
                  no fabricated session ids, no READY verdict for F06/F07
```

## Executor identity binding (Director addendum)

```text
DSH_SUBAGENT_ID = 454dea06-3e76-4c1e-80bd-d5287bc2cae0
LAUNCHED_AT_UTC = 2026-10-25T11:10:00Z (approximately; launcher returned id synchronously)
STATUS          = DISPATCHED_RUNNING (separate background session; its own context and commits)
NOTE            = per DIRECTOR.md invariant ACTOR_ID != INDEPENDENT_EXECUTOR_PROOF:
                  this id proves protocol role separation, not an independent
                  model/credential; production identity proof remains a separate gate
```
