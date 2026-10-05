# NL5 HG-B state-sync repair — Fresh CONTROL/REVIEWER verdict R2

```text
REVIEW_ID =
NL5-HG-B-STATE-SYNC/REVIEWER_R2

VERDICT =
PASS

REVIEWED_BRANCH =
repair/nl5-hg-b-approved-state-sync-r1

REVIEWED_HEAD =
3d8a15c32e903256cd4015fe1109f18b445247b7

REVIEWED_TREE =
5bfb2411d6283420e9067850807c6650725d838b

BASE_HG_B_HEAD =
99a8af949db73da2c841625d89ff3b92f8184822

BASE_MAIN =
3b0dd01e17e374c011007c6b0cdbbb5703bf2360

PREVIOUS_REVIEW =
HG_B_CLOSURE_REVIEW_R1 / FIX_REQUIRED

SCIENTIFIC_RUNS =
0
```

## 1. Scope

Fresh control-integrity review of the narrow M-1 repair only.

The owner decision itself is not re-adjudicated. This review verifies the canonical state sync required by Reviewer R1 and checks that no scientific/status surface drifted.

## 2. M-1 — PASS

At the reviewed exact HEAD:

`project/state.json.open_decisions = []`.

The prior sole entry `NL5-ACCEPTANCE-POLICY` was the owner question already resolved by:

```text
HG-B = APPROVED

NL5 acceptance requires successful fresh external reproduction
under preregistered v0.2 distribution-based rule.
```

Therefore canonical state no longer contradicts the durable HG-B decision record.

No new state schema was introduced.

## 3. State invariants — PASS

Comparing the state file to the HG-B recording base `99a8af9`, all non-decision state remains unchanged:

```text
frontier = NL5
next_work_order = NL5-002

task_status.NL5-002 = WAITING_HUMAN
stage_status.NL5 = IN_PROGRESS

execution.external_reproductions = 0
execution.ai_campaigns = 0
execution.paid_compute_authorized = false

NL6-001 = PLANNED
E5 = NOT_RUN
E6 = NOT_RUN
```

No NL5 acceptance, NL6 unlock, scientific-run authorization, R2 activation or AUTHOR_U1 assignment was introduced.

## 4. Append-only bookkeeping — PASS

- Reviewer R1 branch was integrated with a real `--no-ff` merge; history is preserved.
- Event 0008 is byte-identical to the pre-repair HG-B branch.
- Event 0009 is a valid `CONTINUATION_CHECKPOINT` and binds the substantive state-sync commit `e8c306ca89e1aa7cba9eac576173b057f5399ec9`.
- The execution passport adds only the exact required `project/state.json` path to `allowed_paths`; status remains `HANDOFF_READY`.
- No historical event was rewritten.

## 5. Validation evidence

Implementer/Ubuntu execution evidence at exact repair subject reports:

```text
unittest discover = 593 tests OK
check-consistency = ok:true / 0 errors / 0 warnings
workflow_lint = 0 violations / 0 blocking
work_cli = 49/49 EX-* OK
prefreeze = PREFREEZE_VALIDATION_PASS
dispatch = DISPATCH_BLOCKED
freeze_status = NOT_FROZEN
```

This reviewer independently verified the exact remote Git object identity and the relevant state/event/passport bytes. No independent full test rerun is claimed by this review.

## 6. HG-B closure conclusion

```text
M-1 canonical state sync = PASS
owner decision fidelity  = PASS
append-only integrity     = PASS
state/status ceiling      = PASS
scientific-run ceiling    = PASS

OVERALL = PASS
```

HG-B is now durably and consistently closed as:

```text
HG-B = APPROVED
```

while:

```text
CANDIDATE = PRE-DATA / NOT FROZEN
SCIENTIFIC_RUNS = 0
R2 = WAITING_HOST / NOT_ACTIVE
AUTHOR_U1 = NOT_ASSIGNED
NL5 = IN_PROGRESS
external_reproductions = 0
NL6-001 = LOCKED by dependency
```

## 7. Next

```text
NEXT_ACTOR =
DIRECTOR / integration

NEXT_ACTION =
fast-forward PR #51 product/control branch to exact repaired subject
3d8a15c32e903256cd4015fe1109f18b445247b7,
run TR-PR hosted CI, then Human Gate merge.

AFTER MERGE:
create separate Director Freeze preparation WO for immutable v0.2 package F;
in parallel continue native Ubuntu R2 activation.
```

No separate Verifier is required for this narrow paperwork/state-sync repair under the current control process.
