# VERIFIER EVIDENCE — INFRA0-001 (независимая проверка, R1)

Verifier: независимый fresh-агент (verify/infra0-execution-baseline-r1).
Проверяемый HEAD: `9427ff1c081d20d87a418fec2757916d6ecca859`.
Этот файл — протокол проверок; итоговый вердикт: `VERIFIER_VERDICT.md`.

## Выполненные проверки (CONTINUATION 1)

### 1. Scope (пройдено)

- `git diff --name-status 71535d0..9427ff1` → ровно 9 файлов, все `A`, все в allowed_paths паспорта:
  `config/infra/execution-baseline.v1.json`, `docs/infra/EXECUTION_BASELINE_R1.md`,
  `docs/work/executions/EX-INFRA0-001-R1/**` (passport.json, branch-passport.md, summary.md, events 0001–0004).
  Вне allowed_paths изменений нет.
- Blob-сравнение через `git rev-parse <sha>:project/infra-state.json`:
  @57c1e63 = @71535d0 = @9427ff1 = `ec0ce2725f85db1a03fbf1d201a682724297ca50` — файл байт-идентичен main, Implementer'ом не тронут.
- `project/state.json`: @71535d0 = @9427ff1 = `66df364e01edabf15b1048a987a85e3027598b42`; отличие от @57c1e63 — изменение, внесённое самим main (принятие NL1-001, 5+/5-), не веткой.
- `.github/` содержит только PULL_REQUEST_TEMPLATE.md и ISSUE_TEMPLATE/; каталога `.github/workflows` нет — workflows не добавлялись.

### 2. jsonschema-валидация (пройдено с задокументированным отклонением)

Валидатор: python `jsonschema` Draft202012Validator + FormatChecker, схемы
`config/control/harness/work-event.schema.v1.json` и `execution-passport.schema.v1.json`.

- events 0001-work-order-started → **OK**
- events 0002-implementation-committed → **OK**
- events 0003-validation-recorded → **OK**
- events 0004-handoff-completed → **OK**
- passport.json → **FAIL ровно по одному полю**: `checkpoint: 'INFRA0' does not match '^NL[0-8]$'`.

Трактовка checkpoint-отклонения (проверено отдельно): паттерн схемы `^NL[0-8]$` написан только для
научного трека и семантически не покрывает INFRA-трек; значение `INFRA0` соответствует
`project/infra-state.json.frontier = INFRA0` и названию checkpoint'а в `project/infra-plan.json`.
Отклонение заранее и явно задокументировано Implementer'ом (branch-passport.md «Документированные
отклонения» №1 и summary.md). Схема не модифицировалась (вне allowed_paths). Остальные 11 полей
паспорта валидны. Для вердикта: не блокирующее отклонение; кандидат — отдельный control WO на
расширение паттерна (например `^(NL[0-8]|INFRA[0-7])$`).

### 3. Subject-цепочка (частично, продолжение в CONTINUATION 2)

- `git cat-file -t`: 57c1e63…, 870f52e…, 41cd55c… — существуют, тип `commit`.
- `git merge-base --is-ancestor 57c1e63 9427ff1` → exit 0: base — предок HEAD.
- Merge `41cd55c` имеет родителей `f880ff6d5cb3c4f3e4f2534ac45761287f5a8599` (ветка) и
  `71535d00a2e729349eea2337217a2c591ed9317d` (origin/main) — соответствует branch-passport.
- main-коммиты 57c1e63..71535d0 — цепочка NL1-001 (dd4692d…71535d0), к INFRA0-001 не относятся,
  конфликтов с allowed_paths не создают.

## Ожидаемые проверки (CONTINUATION 2)

- Merge 41cd55c вносит только main-коммиты (diff f880ff6→41cd55c == diff f880ff6→71535d0).
- Secret-скан диффа (шаблоны ключей/токенов) → ожидание 0 находок.
- Сверка baseline-документа §2–§8 с config/infra/execution-baseline.v1.json (trust zones, routes+runner
  классы, labels, permissions, RC-классы, artifact-поля, NC-1..7), включая кандидатуру расхождения §4
  (G0 в TR-DISPATCH) vs конфиг `["H0","C0"]`.
- Отсутствие объявления принятия capability: `PROPOSED`/`HANDOFF_READY` без `ACCEPTED`;
  `project/infra-state.json` не тронут (подтверждено п.1), capabilities.* = false.
