# NanoLab — Project Control Center

**Control plane:** `NL-PC0-2026-09-08-R1`  
**Harness foundation:** `NL-H0-2026-09-08-R1`  
**Canonical owner:** `main`

NanoLab использует адаптированный control/harness-подход из `rootfabric/distributed-world-simulator`: центральная ветка объявляет состояние проекта, рабочие ветки публикуют факты исполнения, а Git является долговременной памятью проекта.

## Канонические источники

```text
README.md
docs/VISION.md
docs/ROADMAP.md
project/plan.json
project/state.json
config/control/harness/project-goals.v1.json
config/control/harness/checkpoint-catalog.v1.json
```

При конфликте между старым отчётом, чатом и текущим `main` побеждает `main`.

## Инварианты

```text
MAIN DECLARES PROJECT STATE
BRANCHES REPORT EXECUTION FACTS
GIT IS DURABLE MEMORY; CHAT IS NOT
WORK ORDER IS THE EXECUTION UNIT
EXPERIMENT RUN IS THE SCIENTIFIC EXECUTION UNIT
COMMIT IS THE RECOVERY UNIT
EVIDENCE MAP IS THE REVIEW UNIT
IMPLEMENTER CANNOT SELF-ACCEPT
SCIENTIFIC CLAIM MUST NOT EXCEED ITS EVIDENCE
NEGATIVE AND INCONCLUSIVE RESULTS ARE DURABLE RESULTS
RAW DATA MUST BE ADDRESSABLE BY DIGEST
```

## Основная ветка

`main` — единственная каноническая ветка проекта. Новая разработка начинается от свежего `origin/main`.

Разрешённые рабочие префиксы:

```text
work/<work-order>-<slug>-rN
experiment/<experiment>-<slug>-rN
repair/<work-order>-<slug>-rN
control/<slug>-rN
docs/<slug>-rN
```

Прямой push в `main`, force-push и destructive history rewrite не являются штатным путём.

## Единицы управления

```text
checkpoint      = продуктовая/научная граница NL0..NL8
work order      = ограниченная задача
experiment run  = один замороженный вычислительный опыт
commit          = точка восстановления
evidence map    = пакет review
exception       = единица внимания человека
```

## Научный результат отделён от технического

Успешный exit code означает только, что программа завершилась. Для каждого опыта отдельно фиксируются:

```text
execution_outcome:
  COMPLETED | FAILED_TECHNICAL | ABORTED | BLOCKED_ENVIRONMENT

scientific_outcome:
  SUPPORTED | NOT_SUPPORTED | INCONCLUSIVE | NOT_EVALUATED | INVALIDATED
```

Нельзя переводить технический успех в научный `SUPPORTED` без анализа и review.

## Приёмка checkpoint

Checkpoint считается принятым только когда в каноническом `main` находится durable acceptance record, связанный с exact subject/evidence. Документ, локальный PASS, сообщение агента или один удачный run сами по себе checkpoint не закрывают.

До отдельного изменения policy merge в `main` остаётся Human Gate. Рутинные ветка/commit/non-force push/draft PR/evidence внутри Work Order не требуют повторного разрешения владельца.
