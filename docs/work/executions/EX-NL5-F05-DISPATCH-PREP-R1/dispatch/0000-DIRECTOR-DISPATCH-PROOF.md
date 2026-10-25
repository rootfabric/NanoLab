# DIRECTOR DISPATCH PROOF — F05-prep / EX-NL5-F05-DISPATCH-PREP-R1

Append-only Director record (Issue #86 proof protocol; issue-comment API=403, durable proof via Git).

```text
PROGRAM            = NL5-CLOSE-R1
TASK               = NL5-F05 PREPARATORY C0 PART (Issue #86; authority A explicitly OUT OF SCOPE)
OBSERVED MAIN_HEAD = 3b567ae33f247b182b2ae451d2cc4598a9e76019 (fresh fetch 2026-10-25T17:11:36Z; unchanged = F01 BASE)
F01 HANDOFF        = ACCEPTED (documentary): work/nl5-f01-frozen-audit-r1 @ c7c5be6... ; F01 matrix: F05-prep READY (C0 prep) / authority A BLOCKED (F04/R2 ACTIVE/U1)
FROZEN F2          = 60da9a846511265a8ac7564da088c3d74cb073f0 / tree e565c8a6cee9e829fac14008ebc9c2ea1609931d
ROLE / LAUNCHER    = CONTROL-IMPLEMENTER on real DSH subagent session (id appended below)
WORKTREE/BRANCH    = /home/rdpuser/NanoLab/nl5-f05-dispatch-prep / work/nl5-f05-dispatch-prep-r1
BUDGET             = offline validators only; wall <= 4h; science_runs=0; NO authority A creation
SAFE STOP          = authority A draft temptation, science dry-run on real data, forbidden write -> STOP with BLOCKED evidence
```

## Executor identity binding (Director addendum)

```text
DSH_SUBAGENT_ID = 3e3c6aa5-d615-49a0-8b6a-1805d8f7431a
STATUS          = DISPATCHED_RUNNING (separate background session; ACTOR_ID != INDEPENDENT_EXECUTOR_PROOF)
```
