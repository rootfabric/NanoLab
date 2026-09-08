# NanoLab — Harness Control

**Revision:** `NL-H0-2026-09-08-R1`  
**Canonical owner:** `main`

Точка входа для работы агентов. Полные правила находятся в `PROJECT_CONTROL.md` и `docs/control/`.

Machine contracts находятся в `config/control/harness/`.

## Work Order lifecycle

```text
PLANNED → DISPATCHED → IN_PROGRESS → IMPLEMENTED → VERIFYING → VERIFIED
→ REVIEWING → AUDITED → CHECKPOINT_PROPOSED → ACCEPTED
```

Допустимы `FIX_REQUIRED`, `INCONCLUSIVE`, `BLOCKED`, `WAITING_HUMAN`, `EPOCH_INVALIDATED`, `CANCELLED`.

## Experiment Run lifecycle

```text
PRE_REGISTERED → READY → STARTED → PREPARING → RUNNING → CHECKPOINTED*
→ ANALYZING → COMPLETED → REVIEWING → ACCEPTED | REJECTED | INCONCLUSIVE
```

Технические аварии: `FAILED_TECHNICAL`; недоступная среда: `BLOCKED_ENVIRONMENT`.

## Control surface

```text
./CONTROL_DEVELOPMENT.sh --overview|--check-consistency|--status|--plan|--drive
./CONTROL_WORK.sh validate|status|close <execution-dir>
./CONTROL_EXPERIMENT.sh validate|status|close <run-dir>
```

Windows: аналогичные `CONTROL_DEVELOPMENT.ps1`, `CONTROL_WORK.ps1`, `CONTROL_EXPERIMENT.ps1`.

`CONTROL_WORK close` требует durable START и terminal handoff + `summary.md`. `CONTROL_EXPERIMENT close` требует terminal execution, analysis и review. Эти команды проверяют completeness evidence, но не self-accept scientific truth.

## Human gates

По умолчанию: merge/direct push `main`, force-push/history rewrite, destructive deletion, foundation authority change, CRITICAL scientific work, новый physical wet-lab/hardware experiment и budget expansion.
