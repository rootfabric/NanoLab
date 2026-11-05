# NanoLab — Project Control Center

**Control plane:** `NL-PC0-2026-09-08-R1`  
**Harness foundation:** `NL-H0-2026-09-08-R1`  
**Canonical owner:** `main`

NanoLab использует адаптированный control/harness-подход из `rootfabric/distributed-world-simulator`: центральная ветка объявляет состояние проекта, рабочие ветки публикуют факты исполнения, а Git является долговременной памятью проекта.

## Канонические источники

Историческая научная DNA линия:

```text
README.md
docs/VISION.md
docs/ROADMAP.md
project/plan.json
project/state.json
config/control/harness/project-goals.v1.json
config/control/harness/checkpoint-catalog.v1.json
```

Независимая atomistic product линия (candidate P0–P6):

```text
project/product-plan.json
project/product-state.json
project/operations/ATOMISTIC-*.json
```

P0–P3 — ближайший инженерный продукт; P4–P6 — conditional research. Их acceptance не наследуется от NL0–NL8. Старые `project/state.json`, counters, goals/catalog и frozen protocols не переписываются ради нового UI или расчёта. Product tasks читаются дополнительно к старому NL frontier; `drive` уже показывает их через совместимые C0 operations cards.

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

## Независимые frontiers

```text
HISTORICAL DNA SCIENTIFIC
NL0 → NL1 → ... → NL8
owned by project/state.json

ATOMISTIC PRODUCT
P0 → P1 → ... → P6
owned by project/product-plan.json + product-state.json

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
checkpoint      = историческая scientific граница NL0..NL8
product stage   = независимая atomistic граница P0..P6
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

## Узкий engineering launch profile

[WO-ATOMISTIC-PRODUCT-R1](docs/work/WO-ATOMISTIC-PRODUCT-R1.md) явно разрешает implementation validation нового atomistic adapter в disposable Linux, isolated venv: один material/model, ≤4096 atoms, ≤2000 MD steps/run, ≤8 actual pilot runs, ≤1200 секунд compute, ≤2 GiB результатов суммарно, последовательно. Это реальные расчёты модели с ceiling `SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`. Machine limits и stops — `project/product-plan.json`; actual budget ledger/evidence ведёт adapter, roadmap не подставляет run counters.

Это дополнение scope только данной mission: никаких paid compute/U1/U2 mutations/NL5/E5 dispatch; контейнер не становится U1/U2. Все future scientific/material campaigns требуют собственного protocol/model validation и принятой среды. Existing operations schema остаётся C0-only; карточка, READY и зелёный CI не дают launch authority. P0/validated P1 не принимаются successful exit или trajectory viewer; P1 engineering delivery учитывается отдельно и не блокируется открытым P0 reference. WIP ≤3 substantive tasks, consumer/demo/budget/stop обязательны; неизменный blocker не вызывает повторный аудит.
