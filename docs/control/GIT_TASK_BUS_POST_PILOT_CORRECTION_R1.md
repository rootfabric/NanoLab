# Git Task Bus — Post-Pilot Correction R1

Revision: `NL-BUS-POST-PILOT-R1`, 2026-09-09.
Status: mandatory control amendment for `control/git-task-bus-r1` until a newer canonical revision supersedes it.

## 1. Frozen live-pilot result

`BUS-SMOKE-001` must not be rerun without a new explicit Work Order.

```text
BUS-SMOKE-001 LIVE PILOT = PASS
BUS-SMOKE-001 TERMINAL   = COMPLETED_SANDBOX
BUS-001 ACCEPTANCE       = NOT YET
```

Exact frozen pilot subject:

```text
BASE = 95b1319600bcc64572d84c0456acb927802ab806
HEAD = d5bfc55956722e241151e0ef6db5299ee7e55123
TREE = 07dc90857bb40f9bb7e4d991ff782d5ebbc044c3
BUS  = control/task-bus-pilot-r1 @ 6e95891db110438c3a888aec9af7721ccdb63ceb
```

The pilot demonstrated the bounded workflow:

```text
DIRECTOR open
-> IMPLEMENTER
-> REVIEWER
-> VERIFIER
-> DIRECTOR
-> COMPLETED_SANDBOX
```

It also demonstrated a single winning competing claim, exact subject binding, durable Git-only handoffs, negative controls, and Director recovery from Git state.

`COMPLETED_SANDBOX` is not `ACCEPTED`, does not close an NL/INFRA checkpoint, and does not authorize production activation or merge.

## 2. Mandatory state synchronization

Human-facing state must agree with the authoritative bus history. Any text still claiming `READY_FOR_LIVE_TRIAL`, `live trial NOT_RUN`, or `P1 pending` is stale and must be corrected to:

```text
P1 = PASS
BUS-SMOKE-001 = COMPLETED_SANDBOX
NOT ACCEPTED
NOT PRODUCTION
HUMAN GATE REQUIRED
```

Do not rewrite or delete prior failed/intermediate evidence; supersede stale status explicitly.

## 3. Hash evidence terminology

Do not call a platform working-tree hash a universal immutable artifact hash.

Record separately:

```text
GIT_BLOB_SHA1
CANONICAL_BLOB_SHA256
CHECKOUT_SHA256
```

Definitions:

- `GIT_BLOB_SHA1`: Git object identity.
- `CANONICAL_BLOB_SHA256`: SHA-256 of the exact bytes stored in the Git blob.
- `CHECKOUT_SHA256`: SHA-256 of the materialized working-tree file; this may vary due to line-ending conversion.

For `BUS-SMOKE-001/receipt.json` the Git blob identity is:

```text
GIT_BLOB_SHA1 = 379c597d940fa9ded54ed9549d63a68ad48ead48
```

The previously reported `2393d4eeea591b3896fa34ee45fa42a6c697cf17b336b4d8188d437ba257c9d6` is a Windows checkout hash and must be labeled `CHECKOUT_SHA256`, not canonical blob hash.

## 4. Identity boundary

```text
different actor_id != proof of independent model/session
```

The current bus proves protocol role separation, not cryptographic executor independence.

Use distinct terms:

```text
ROLE_SEPARATION_CONFIRMED
INDEPENDENT_EXECUTOR_IDENTITY_PROVEN
```

The first is supported by the pilot. The second is not yet proven.

Production work must add an explicit identity mechanism such as protected writer credentials, signed attestations, trusted launcher identity, server-side authorization, or executor-issued job/session identity.

## 5. Required gates before P2

Do not start P2 production activation merely because `BUS-SMOKE-001` passed.

Required sequence:

```text
P0  Mechanical implementation/tests              DONE
P1  Real BUS-SMOKE-001 multi-agent pilot          PASS
P1.1 State/evidence synchronization               NEXT
P1.2 Fresh BUS-001 implementation Reviewer        REQUIRED
P1.3 Fresh exact-head BUS-001 Verifier             REQUIRED
P1.4 Human Gate / canonical activation             REQUIRED
P2  Production policy + protected writer          LOCKED UNTIL P1.1-P1.4
P3  Roadmap -> Work Order adapters                 LATER
P4  Bounded launcher + identity proofs + budgets   LATER
P5  Parallel tasks / conflicts / scale campaign    LATER
```

## 6. Fresh BUS-001 implementation review

Create a bounded review Work Order (`BUS-REVIEW-001` or the next valid Harness ID).

Subject: live `control/git-task-bus-r1` exact HEAD/TREE. The previously observed HEAD `ae8b91d467e745e9d2bd8aa6c8e255210fba9071` is historical after this amendment and must not be reused without a fresh `git fetch` and live resolution.

Reviewer checks the broker itself, not only the receipt pilot:

```text
tools/task_bus.py
tests/task_bus/
config/control/task-bus/
docs/control/GIT_TASK_BUS_RU.md
docs/control/GIT_TASK_BUS_PROMPTS_RU.md
DIRECTOR.md
AGENTS.md integration
```

Minimum adversarial areas:

```text
competing claims
stale/expired/foreign lease
retry after lost acknowledgement
duplicate message ID / collision
non-fast-forward race
candidate branch drift
HEAD/TREE/base ancestry mismatch
unauthorized path
symlink/submodule/executable injection
Reviewer modifying candidate
actor reuse across approvals
FAIL -> Implementer repair
Verifier FAIL after Reviewer PASS
repair/claim budget exhaustion
BLOCKED/resume
Director reclaim
malformed/duplicate JSON keys
oversized queue
clock/lease edge cases
concurrent writers
Windows line-ending behavior
safe.bareRepository behavior
fresh-clone recovery
```

Old `40/40`, previous reports, and `BUS-SMOKE-001 PASS` are historical evidence only and must not replace fresh execution.

## 7. Fresh Verifier

After Reviewer PASS, a separate Fresh Verifier must validate the same exact subject with a fresh checkout and record:

```text
BUS_001_VERIFICATION = PASS | FAIL | NOT_VERIFIED
```

Any subject drift after review or verification invalidates the corresponding gate for the new HEAD.

## 8. Human Gate and merge

Production merge is eligible only when all are true:

```text
LIVE_PILOT = PASS
HOUSEKEEPING_SYNC = PASS
IMPLEMENTATION_REVIEW = PASS
EXACT_HEAD_VERIFICATION = PASS
PR_HEAD == VERIFIED_HEAD
NO_UNRESOLVED_BLOCKERS
HUMAN_GATE = APPROVED
```

After merge:

```text
fresh main
confirm expected ancestry
run canonical regression
confirm AGENTS.md -> DIRECTOR.md entrypoint
confirm Task Bus tooling is available from canonical main
```

Only after successful canonical activation may P2 become the active implementation step.

## 9. Prohibitions

```text
DO NOT rerun BUS-SMOKE-001 without a new Work Order
DO NOT merge control/task-bus-pilot-r1 into main
DO NOT treat COMPLETED_SANDBOX as ACCEPTED
DO NOT infer independent executor identity from actor names
DO NOT reuse PASS after subject drift
DO NOT manually edit queue.json
DO NOT force-push the bus branch
DO NOT hide or rewrite failed attempts
DO NOT begin P2 before P1.1-P1.4
DO NOT modify scientific/canonical project state as part of this correction
```

## 10. Completion outcomes

After P1.1-P1.3 the Director may report only one of:

```text
BUS-001 = READY_FOR_HUMAN_GATE
BUS-001 = FIX_REQUIRED
BUS-001 = NOT_VERIFIED
```

Do not report `BUS-001 = ACCEPTED` until the Human Gate, canonical merge, and post-merge verification are actually complete.
