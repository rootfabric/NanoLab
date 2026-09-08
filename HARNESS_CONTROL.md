# NanoLab — Harness Control

**Revision:** `NL-H0-2026-09-08-R1`  
**Canonical owner:** `main`

Это короткая точка входа для работы агентов. Полные правила:

```text
PROJECT_CONTROL.md
docs/control/DEVELOPMENT_HARNESS_RU.md
docs/control/HARNESS_REVIEW_AND_EVIDENCE_RU.md
docs/control/HARNESS_AUTONOMOUS_EXECUTION_RU.md
docs/control/EXPERIMENT_HARNESS_RU.md
docs/control/BRANCHING_AND_GIT_RU.md
```

Machine contracts находятся в `config/control/harness/`.

## Жизненный цикл Work Order

```text
PLANNED → DISPATCHED → IN_PROGRESS → IMPLEMENTED → VERIFYING → VERIFIED
→ REVIEWING → AUDITED → CHECKPOINT_PROPOSED → ACCEPTED
```

Допустимые ответвления: `FIX_REQUIRED`, `INCONCLUSIVE`, `BLOCKED`, `WAITING_HUMAN`, `EPOCH_INVALIDATED`, `CANCELLED`.

## Жизненный цикл Experiment Run

```text
PRE_REGISTERED → READY → STARTED → PREPARING → RUNNING
→ CHECKPOINTED* → ANALYZING → COMPLETED → REVIEWING
→ ACCEPTED | REJECTED | INCONCLUSIVE
```

Технические аварии идут в `FAILED_TECHNICAL`, недоступная среда — в `BLOCKED_ENVIRONMENT`. Старые события не редактируются: исправление публикуется новым event.

## Control surface

```text
./CONTROL_DEVELOPMENT.sh --overview
./CONTROL_DEVELOPMENT.sh --check-consistency
./CONTROL_DEVELOPMENT.sh --status
./CONTROL_DEVELOPMENT.sh --plan
./CONTROL_DEVELOPMENT.sh --drive

.\CONTROL_DEVELOPMENT.ps1 -Overview
.\CONTROL_DEVELOPMENT.ps1 -CheckConsistency
.\CONTROL_DEVELOPMENT.ps1 -Status
.\CONTROL_DEVELOPMENT.ps1 -Plan
.\CONTROL_DEVELOPMENT.ps1 -Drive
```

Experiment evidence:

```text
./CONTROL_EXPERIMENT.sh validate <run-dir>
./CONTROL_EXPERIMENT.sh status <run-dir>
./CONTROL_EXPERIMENT.sh close <run-dir>
```

`close` проверяет полноту evidence; он не объявляет научный результат истинным.

## Human gates

По умолчанию требуют человека: merge/direct push `main`, force-push/history rewrite, destructive deletion, foundation authority change, CRITICAL scientific work, новый физический wet-lab/hardware experiment и выход за утверждённый budget.
