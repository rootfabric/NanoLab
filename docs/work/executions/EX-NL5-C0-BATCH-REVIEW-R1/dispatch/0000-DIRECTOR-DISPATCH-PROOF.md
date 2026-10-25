# DIRECTOR DISPATCH PROOF — Batch Review F02+F03+F05 (C0 handoffs)

Append-only Director record. Reviewer = fresh independent session (separate from all implementers).

```text
BASE          = 3b567ae33f247b182b2ae451d2cc4598a9e76019
SUBJECT F02   = work/nl5-f02-u1-host-r1        @ c38ad687d87bfa0c33d69bfee4fe40020d34ba45
SUBJECT F03   = work/nl5-f03-u2-readiness-r1   @ 1831585fa70169c4e473acfe38e9603e45cfe22c
SUBJECT F05   = work/nl5-f05-dispatch-prep-r1  @ 4c9d8fd30300a2f48504d1b914693f0a66bb3555
DIRECTOR PREV = all three handoffs independently re-verified by Director (HEAD/TREE/scope/SHA-256/harness validations)
VERIFIER      = distinct fresh session AFTER Reviewer PASS (separate dispatch)
BUDGET        = offline review; wall <= 3h; science_runs = 0
SAFE STOP     = any forbidden write or scope breach -> STOP, verdict FAIL with findings
```

## Executor identity binding (Director addendum)

```text
DSH_SUBAGENT_ID = b8eca5d9-8ad0-419d-8092-58da4d471487
STATUS          = DISPATCHED_RUNNING
```
