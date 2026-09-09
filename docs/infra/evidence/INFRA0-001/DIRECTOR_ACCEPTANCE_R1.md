# Director Acceptance — INFRA0-001 (compute trust and execution baseline)

Дата решения: 2026-09-09. Роль: DIRECTOR (главный агент INFRA-линии миссии; явная авторизация владельца на Director-приёмку и merge в `main` получена в сессии).

## Решение

```text
INFRA0-001 = ACCEPTED
checkpoint INFRA0 = ACCEPTED (frontier INFRA0 закрыт; единственная задача стадии)
frontier = INFRA1 (INFRA1 = IN_PROGRESS)
next_work_order = INFRA1-001 «Add hosted harness CI» (READY)
claim = C0_SOFTWARE_ONLY (baseline — software/policy-документ; научных claims нет)
capabilities = все false (hosted CI, self-hosted runner, artifact store, GPU и пр. НЕ установлены)
```

## Основание

1. **Реализация**: `EX-INFRA0-001-R1` — baseline `EXECUTION-BASELINE-R1` (`docs/infra/EXECUTION_BASELINE_R1.md`) + machine-readable проекция `config/infra/execution-baseline.v1.json`: 7 trigger routes (TR-PR/TR-PUSH-MAIN hosted-only; TR-DISPATCH protected, `RESERVED_NOT_ACTIVE`; TR-PRT/TR-WFRUN `FORBIDDEN_R1`), runner-классы H0/C0/G0/H1 с зарезервированными labels (self-hosted не зарегистрирован), токен-политика (repo default read-only — target, PR route `contents: read`), resource classes RC0–RC3 (paid compute запрещён; RC2-числа — только по измерениям INFRA2/3), artifact policy с 5 provenance-полями, negative controls NC-1..NC-7, threat matrix §9, 11 явных non-goals §10.
2. **Scope**: diff `71535d0..9427ff1` — ровно 9 файлов, все в allowed_paths паспорта; `project/infra-state.json`, `project/state.json`, `.github/`, control-политики не тронуты; runners/workflows/secrets/paid compute — NONE; durable START-дисциплина соблюдена (`ff68c12` до substantive work).
3. **Независимые вердикты**: REVIEWER **PASS** (`41c1382`; findings MINOR-1..4, NOTE-1..3) и VERIFIER **PASS** (`40d6c4a`; FINDING-1..3, все неблокирующие; 36/36 doc↔config сверок, jsonschema events 4/4, secret-скан 0 находок) на exact subject `9427ff1c081d20d87a418fec2757916d6ecca859`. Оба вердикта влиты в эту ветку merge-коммитами.
4. **Corrections**: findings MINOR-2/3 исправлены erratum-коммитом `42db4cc` (+ event `0005-review-corrections`, actor DIRECTOR; старые события не редактировались).
5. **Граница ролей соблюдена**: baseline опубликован в статусе `PROPOSED`, `ACCEPTED` имплементером нигде не выставлен, state-файлы не тронуты — принятие происходит только этим Director-решением через принятый merge.

## Решения по findings

| Finding | Решение Director'а |
|---|---|
| **MINOR-1** (REVIEWER; = verifier FINDING-3): required output WO №4 «negative test: untrusted PR route не может выбрать self-hosted scientific label» реализован документально (NC-1), механический тест отложен в `INFRA1-002` | **ПРИНЯТО С УСЛОВИЕМ.** Deferral обоснован: в R1 в репозитории не существует ни одного workflow — механическому negative-тесту нечего проверять; `infra-plan.json` помещает validation gates в `INFRA1-002` сразу после появления CI. **Условие (binding): механический NC-1-тест (lint `runs-on` всех workflow route TR-PR/TR-PUSH-MAIN на отсутствие self-hosted labels + негативный сценарий) является блокирующим критерием приёмки `INFRA1-002`**; без него `INFRA1-002` не может быть принят. До исполнения этого условия acceptance «public PR path и trusted scientific path технически различимы» считается выполненным на уровне контракта, не механики. |
| **MINOR-2**: §8 вводная фраза — инвертированный смысл + артефакт U+00AD | **ИСПРАВЛЕНО** erratum `42db4cc`: формулировка приведена к «Инварианты, нарушение которых обязано быть технически невозможным», soft hyphen удалён (скан = 0). |
| **MINOR-3** (= verifier FINDING-1): §4 допускал `G0` в TR-DISPATCH, конфиг — `["H0","C0"]` | **ИСПРАВЛЕНО** erratum `42db4cc`: строка §4 синхронизирована с конфигом (G0 — только после активации `INFRA5-001`); расхождение устранено до того, как конфиг станет входом линтеров `INFRA1-002`. |
| **MINOR-4**: конфиг в `config/infra/` вне буквального WO scope | **ПРИНЯТО К СВЕДЕНИЮ.** Отклонение задокументировано имплементером, файл в allowed_paths паспорта, дублей нет. Директива впредь: mission-указания владельца, отклоняющие путь от WO, фиксировать durably (в ветке/паспорте). |
| **NOTE-1** (в т.ч. verifier FINDING-2): `checkpoint: INFRA0` против `^NL[0-8]$` в `execution-passport.schema.v1.json` | **ПРИНЯТО К СВЕДЕНИЮ.** Задокументированное имплементером отклонение; схема не менялась. Кандидат в отдельный control WO: расширить паттерн до `^(NL[0-8]|INFRA[0-7])$`. Не блокирует. |
| **NOTE-2**: имя ветки отличается от предложенного в WO | **ПРИНЯТО К СВЕДЕНИЮ.** Соответствует шаблону `infra/<checkpoint>-<slug>-rN`; WO предлагал ветку, не предписывал. |
| **NOTE-3**: опечатки §7.2/§7.3/§6.5 | **ПРИНЯТО К СВЕДЕНИЮ.** Смысла не меняют; исправление — в плановой ревизии `EXECUTION-BASELINE-R2`, отдельным churn-коммитом границу доверия не трогаем. |

## Условия, с которыми принято

- Все `capabilities.*` в `project/infra-state.json` остаются `false`: ни hosted CI, ни self-hosted runner, ни artifact store не установлены. ACCEPTED — это принятие **документированного baseline-контракта**, не наличие инфраструктуры.
- Механический NC-1-тест — блокирующий критерий приёмки `INFRA1-002` (см. MINOR-1).
- Baseline-документ и конфиг переводятся в статус `ACCEPTED` этим решением; изменение содержимого — только новой ревизией `EXECUTION-BASELINE-R2+` в отдельном bounded WO.
- `TR-DISPATCH` остаётся `RESERVED_NOT_ACTIVE`: любой запуск на будущем self-hosted runner требует exact subject + budget + approval по §4; автоматический self-hosted execution для public PR запрещён в принципе.
- Научный трек не затронут: `project/state.json` без изменений, `E0–E6 = NOT_RUN`, `physics_runs = 0`; INFRA-merge не повышает scientific claim.

## Claim ceiling

`C0_SOFTWARE_ONLY` (подтверждён обоими независимыми вердиктами): baseline — software/policy-документ и его machine-readable проекция; научных утверждений не содержит и не создаёт. Настоящее решение не объявляет существование/безопасность будущих runner'ов и CI:capability активируется соответствующими INFRA1+ Work Orders после фактической установки и проверки, а не этим merge.

## Следующее действие

`INFRA1-001` (READY): «Add hosted harness CI» — первый hosted workflow по контрактам baseline §4–§6 (TR-PR/TR-PUSH-MAIN только на `H0`, минимальные `permissions:`, pinned actions); затем `INFRA1-002` — механические negative controls NC-1..NC-7 (с блокирующим NC-1-тестом). После закрытия INFRA1-001/INFRA1-002 — checkpoint `INFRA1`.
