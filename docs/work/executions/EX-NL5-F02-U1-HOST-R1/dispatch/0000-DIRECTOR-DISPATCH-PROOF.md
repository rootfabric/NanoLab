# DIRECTOR DISPATCH PROOF — F02 / EX-NL5-F02-U1-HOST-R1

Append-only Director record (Issue #83 proof protocol; issue-comment API=403, durable proof via Git).

```text
PROGRAM            = NL5-CLOSE-R1
TASK               = NL5-F02 (Issue #83)
OBSERVED MAIN_HEAD = 3b567ae33f247b182b2ae451d2cc4598a9e76019 (fresh fetch 2026-10-25T17:10:49Z; unchanged = F01 BASE)
F01 HANDOFF        = ACCEPTED (documentary): work/nl5-f01-frozen-audit-r1 @ c7c5be6edbcdb5a304705ff6d53863fa735d7d0c; Director re-verified HEAD/TREE, 5/5 evidence SHA-256, scope, harness validations green
FROZEN F2          = 60da9a846511265a8ac7564da088c3d74cb073f0 (read-only reference)
U1_STATUS          = NOT_ASSIGNED (expected honest outcome: BLOCKED_OWNER_U1 unless owner provided host)
ROLE / LAUNCHER    = HOST-PROVISIONING on real DSH subagent session (id appended below)
WORKTREE/BRANCH    = /home/rdpuser/NanoLab/nl5-f02-u1-host / work/nl5-f02-u1-host-r1
BUDGET             = offline read-only host facts; wall <= 3h; science_runs=0; no apt/global installs
SAFE STOP          = no host allocation found -> BLOCKED_OWNER_U1 evidence; any forbidden-path need -> STOP
```

## Executor identity binding (Director addendum)

```text
DSH_SUBAGENT_ID = (appended after launch)
STATUS          = DISPATCH_PENDING_LAUNCH
```
