# NanoLab — Ubuntu CONTROL repair: HG-B canonical-state sync R1

Роль: IMPLEMENTER / CONTROL.

Источник истины:

```text
repo = rootfabric/NanoLab
product branch = control/nl5-hg-b-approved-r1
review branch = review/nl5-hg-b-approved-r1-r1

REVIEWED_HEAD =
99a8af949db73da2c841625d89ff3b92f8184822

REVIEWED_TREE =
c6be3bac7e346fbab6ea55b5e034b6d03224c29b

REVIEW_VERDICT =
FIX_REQUIRED

BLOCKER =
M-1 only
```

Прочитать:

```text
docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_CLOSURE_REVIEW_R1.md
docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.md
docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json
project/state.json
```

## Scope

Исправить ТОЛЬКО canonical-state contradiction:

`project/state.json.open_decisions` всё ещё содержит `NL5-ACCEPTANCE-POLICY`, хотя HG-B уже APPROVED.

Удалить этот resolved decision из `open_decisions`.

НЕ менять:

```text
stage_status.NL5 = IN_PROGRESS
task_status.NL5-002 = WAITING_HUMAN
external_reproductions = 0
NL6-001 = PLANNED / locked by dependency
SCIENTIFIC_RUNS = 0
CANDIDATE = PRE-DATA / NOT FROZEN
R2 = WAITING_HOST / NOT_ACTIVE
AUTHOR_U1 = NOT_ASSIGNED
```

Не создавать новый state schema.

Не создавать новый open decision для packaging/P3 без уже существующего canonical requirement.

## Git

Fresh fetch. Если другой repair уже существует — продолжить его.

Рекомендуемая ветка:

```text
repair/nl5-hg-b-approved-state-sync-r1
```

База — current tip `control/nl5-hg-b-approved-r1`.

Интегрировать reviewer branch `review/nl5-hg-b-approved-r1-r1` через `--no-ff`, без squash/force/rewrite.

## Append-only bookkeeping

Если existing EX passport запрещает `project/state.json`:
- добавить этот exact path в allowed_paths;
- сохранить историю;
- добавить следующий valid CONTINUATION_CHECKPOINT event.

Смысл event:

```text
decision_gate = HG-B
owner_decision = APPROVED
canonical_state_sync = NL5-ACCEPTANCE-POLICY removed from open_decisions
resolution = RESOLVED_BY_HG_B_R1
```

Не менять event 0008.

## Validation

```bash
python3 -m unittest discover -s tests -t . -v
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
```

Validate all EX-* exactly as hosted workflow.

Обязательно повторить prefreeze negative control:

```text
PREFREEZE_VALIDATION_PASS
DISPATCH_BLOCKED
freeze_status = NOT_FROZEN
```

## Handoff

```text
NANOLAB HG-B STATE-SYNC REPAIR HANDOFF

VERDICT =
READY_FOR_REVIEW

BASE =
BRANCH =
HEAD =
TREE =

M-1 =
FIXED

STATE_OPEN_DECISION =
NL5-ACCEPTANCE-POLICY removed / RESOLVED_BY_HG_B_R1

HG-B =
APPROVED

NL5 =
IN_PROGRESS

external_reproductions =
0

NL6-001 =
LOCKED

SCIENTIFIC_RUNS =
0

FREEZE_STATUS =
NOT FROZEN

R2 =
WAITING_HOST / NOT_ACTIVE

TEST_COLLECTION =
CHECK_CONSISTENCY =
WORKFLOW_LINT =
WORK_CLI_ALL_EX =
PREFREEZE =
DISPATCH =

NEXT_ACTOR =
fresh CONTROL/REVIEWER
```

Не merge PR #51. Не freeze protocol. Не запускать science.
