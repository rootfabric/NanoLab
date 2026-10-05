# NL5 HG-B closure — Fresh CONTROL/REVIEWER verdict R1

```text
REVIEW_ID = NL5-HG-B-CLOSURE/REVIEWER_R1
VERDICT = FIX_REQUIRED
REVIEWED_BRANCH = control/nl5-hg-b-approved-r1
REVIEWED_HEAD = 99a8af949db73da2c841625d89ff3b92f8184822
REVIEWED_TREE = c6be3bac7e346fbab6ea55b5e034b6d03224c29b
BASE_MAIN = 3b0dd01e17e374c011007c6b0cdbbb5703bf2360
PR = #51
HOSTED_CI = 37254999220 SUCCESS
SCIENTIFIC_RUNS = 0
```

## Confirmed PASS

Owner decision MD/JSON correctly records `HG-B = APPROVED`. Approved R4 parameters match the authoritative pre-freeze contract: N 64/64/10/10, N_min 52/52/8/8, replacement quotas 12/12/2/2, confirmatory 296, replacement cap 56, max_runs 352, delta 0.5, paired TOST and integer policy `ceil-nmin-floor-replacement-pairs-v1`.

The proposal history is append-only; event 0008 is schema-valid; no freeze/science/R2 activation occurred; NL5 remains IN_PROGRESS; external_reproductions remains 0; NL6 remains locked; PRE-DATA remains PREFREEZE_VALIDATION_PASS / DISPATCH_BLOCKED. PR #51 hosted CI is green.

## Blocking finding M-1 — canonical state still says the decision is open

`project/state.json.open_decisions` still contains:

```text
id = NL5-ACCEPTANCE-POLICY
kind = OWNER_DECISION
question = whether NL5 acceptance requires
           (a) a new preregistered reproduction rule
           or (b) another owner-defined criterion
```

That is exactly the question HG-B has now answered:

```text
HG-B = APPROVED
NL5 acceptance requires successful fresh external reproduction
under preregistered v0.2 distribution-based rule.
```

So durable truth is contradictory:

```text
owner decision / proposal / WORK_QUEUE:
HG-B CLOSED = APPROVED

project/state.json:
NL5-ACCEPTANCE-POLICY still OPEN
```

No new schema is required. The existing `open_decisions` field already represents this exact owner decision.

## Required narrow repair

1. Remove `NL5-ACCEPTANCE-POLICY` from `project/state.json.open_decisions`.
2. Do not invent a new state schema.
3. Do not mark NL5 accepted.
4. Preserve:
   - `stage_status.NL5 = IN_PROGRESS`
   - `task_status.NL5-002 = WAITING_HUMAN`
   - `execution.external_reproductions = 0`
   - NL6-001 remains locked by dependency.
5. Do not create new optional packaging/P3 decision IDs unless an existing canonical rule explicitly requires them.
6. Make the state sync append-only/corrections-safe in the existing execution bookkeeping. If the execution passport requires path authorization, add `project/state.json` explicitly and record the next valid continuation event:
   `HG-B owner decision canonical-state sync / NL5-ACCEPTANCE-POLICY resolved by HG-B R1`.
7. Re-run full unittest, check-consistency, workflow_lint, all EX-* work_cli validation and the PRE-DATA DISPATCH_BLOCKED negative control.

## Conclusion

```text
HG-B decision content       = PASS
scientific/status boundaries = PASS
Git/CI integrity            = PASS
canonical state closure     = FIX_REQUIRED

OVERALL = FIX_REQUIRED
NEXT_ACTOR = IMPLEMENTER / CONTROL
NEXT_ACTION = narrow canonical-state sync, then fresh review
```

Verifier is not required for this narrow paperwork/state-sync repair unless repository rules newly require it.
