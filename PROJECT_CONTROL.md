# NanoLab — Project Control Center

**Control plane:** `NL-PC0-2026-09-08-R1`  
**Harness foundation:** `NL-H0-2026-09-08-R1`  
**Canonical owner:** `main`

NanoLab использует адаптированный control/harness-подход из `rootfabric/distributed-world-simulator`: центральная ветка объявляет состояние проекта, рабочие ветки публикуют факты исполнения, а Git является долговременной памятью проекта.

## Канонические источники

Научная/product линия:

```text
README.md
docs/VISION.md
docs/ROADMAP.md
project/plan.json
project/state.json
config/control/harness/project-goals.v1.json
config/control/harness/checkpoint-catalog.v1.json
```

Параллельная вычислительная capability линия:

```text
docs/infra/ROADMAP.md
project/infra-plan.json
project/infra-state.json
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
INFRASTRUCTURE PROVIDES CAPABILITY; IT DOES NOT OWN SCIENTIFIC TRUTH
```

## Два независимых frontiers

```text
SCIENTIFIC / PRODUCT
NL0 → NL1 → ... → NL8
owned by project/state.json

COMPUTE CAPABILITY
INFRA0 → INFRA1 → ... → INFRA7
owned by project/infra-state.json
```

INFRA по умолчанию не является hard gate scientific roadmap. Scientific Work Order может явно потребовать конкретную INFRA capability, если без неё нельзя корректно выполнить заявленный experiment/validation.

Зелёный CI, runner или GPU job никогда сам по себе не повышает scientific claim и не закрывает `NL*` checkpoint.

## Основная ветка

`main` — единственная каноническая ветка проекта. Новая разработка начинается от свежего `origin/main`.

Разрешённые рабочие префиксы:

```text
work/<work-order>-<slug>-rN
experiment/<experiment>-<slug>-rN
repair/<work-order>-<slug>-rN
infra/<infra-checkpoint>-<slug>-rN
control/<slug>-rN
docs/<slug>-rN
```

Прямой push в `main`, force-push и destructive history rewrite не являются штатным путём.

Не поддерживать вечную расходящуюся `infra` branch: после accepted INFRA checkpoint следующий major этап стартует от свежего canonical `main`.

## Единицы управления

```text
checkpoint      = продуктовая/научная граница NL0..NL8
infra checkpoint= вычислительная capability граница INFRA0..INFRA7
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

Для INFRA acceptance проверяется capability/security/reproducibility evidence. Для scientific acceptance проверяется scientific evidence. Эти verdicts не взаимозаменяемы.

До отдельного изменения policy merge в `main` остаётся Human Gate. Рутинные ветка/commit/non-force push/draft PR/evidence внутри Work Order не требуют повторного разрешения владельца.
