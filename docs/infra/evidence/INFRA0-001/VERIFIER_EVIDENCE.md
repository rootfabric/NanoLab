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

## Проверки (CONTINUATION 2 — все завершены)

### 4. Merge 41cd55c вносит только main-коммиты (пройдено)

- `git diff --name-status f880ff6…41cd55c` (что merge принёс в ветку) — 21 файл, все относятся к
  цепочке NL1-001 с main: `scheduler-policy.v1.json` (M), `docs/evidence/NL1-001/**`,
  `docs/research/ENGINE_ENVIRONMENT_R1.md`, `docs/work/WO-NL1-001.md`, `SESSION_LOG.md`,
  `WORK_QUEUE.md`, `EX-NL1-001-R1/**`, `project/state.json` (M).
  Ни один файл ветки (baseline doc, config, EX-INFRA0-001-R1) merge не затронул.
- Сравнение списков с `git diff --name-only f880ff6…71535d0`: единственная разница — 9 файлов самой
  ветки, которых на main нет (в perspective main выглядят как `D`); merge корректно сохранил их
  версии. Посторонних изменений merge не вносит.

### 5. Secret-скан диффа (пройдено, 0 находок)

`git diff 71535d0…9427ff1` (56 787 байт) прогнан по шаблонам: AWS `AKIA…`, GitHub PAT
`ghp_/gho_/github_pat_`, Slack `xox…`, PEM/OPENSSH/PGP private key, generic
`password|secret|token|api_key = …`, JWT. Совпадений: **0**.

### 6. Сверка baseline-документа с config/infra/execution-baseline.v1.json (пройдено; 1 подтверждённое текстовое расхождение)

Механическая сверка (36 контрольных утверждений, python) плюс точечные перепроверки:

- **Trust zones** (§2 vs config.trust_zones): UNTRUSTED / TRUSTED CONTROL / SCIENTIFIC ARTIFACTS —
  состав и исполнения совпадают; инвариант границы по происхождению кода — совпадает (`routing_invariant`).
- **Trigger routes + runner-классы** (§4 vs config.trigger_routes): TR-PR и TR-PUSH-MAIN — `["H0"]`,
  hosted-only ✅; TR-DISPATCH — config `["H0","C0"]`, RESERVED_NOT_ACTIVE, guards (protected
  environment/subject_sha/work_order_id/budget/fail-closed) совпадают с §4 ✅; TR-SCHEDULE/TR-TAG —
  deferred, `["H0"]` ✅; TR-PRT/TR-WFRUN — FORBIDDEN_R1 в обоих источниках ✅.
- **Подтверждённое расхождение (FINDING-1, LOW)**: §4 (таблица, строка TR-DISPATCH) пишет
  «`H0` или защищённый `C0`/`G0`», тогда как config допускает `["H0","C0"]`. Внутренне §4.1 сам
  ограничивает G0 («`C0`, позднее `G0`», строка 94), G0 = NOT_REGISTERED, activation `INFRA5-001`,
  RC3 = FORBIDDEN_UNTIL_INFRA5, TR-DISPATCH = RESERVED_NOT_ACTIVE (механика INFRA2-002). Операционного
  влияния в R1 нет; инвариант trusted-зоны не ослаблен (G0 в dispatch оставался бы protected-dispatch-only).
  Рекомендация: синхронизировать строку §4 с конфигом в EXECUTION-BASELINE-R2 или bounded repair.
- **Labels** (§3 vs config.runner_classes/label_rules): H0 `ubuntu-latest`,`ubuntu-24.04`;
  C0 `nanolab-cpu`, G0 `nanolab-gpu`, H1 `nanolab-hpc-*`; 3 правила labels — совпадают ✅.
- **Permissions/secrets** (§5 vs config.github_token_policy + TR-PR.token_permissions):
  repo default read-only (target INFRA1-001), per-workflow explicit minimal, PR route `contents: read`
  + write forbidden, fork PR без secrets, long-lived credentials forbidden, новые secrets запрещены
  scope WO — совпадают ✅.
- **RC-классы и бюджеты** (§6 vs config.resource_classes/budget_rules): RC0 ≤15 мин H0; RC1 ≤60 мин
  H0 must_be_declared; RC2 C0 budget wall_clock/ram/disk/cpu, числа по измерениям INFRA2/3; RC3 G0
  FORBIDDEN_UNTIL_INFRA5 + fingerprint; 5 правил бюджетов — совпадают ✅.
- **Artifact policy** (§7 vs config.artifact_policy): 5 полей provenance
  (sha256/size_bytes/producer_run_id/subject_sha/storage_location), hosted CI артефакты не scientific
  evidence, raw вне Git требует manifest, reuse требует digest+provenance, rerun проверяет manifest,
  secrets forbidden, durable store INFRA4 — совпадают ✅.
- **NC-1..NC-7** (§8 vs config.negative_controls): 7 контролов, угрозы/инварианты/статусы
  DOCUMENTED_R1 и mechanical_validation (NC-1/2/4/7 → INFRA1-002; NC-3 → INFRA2-002;
  NC-5 → review при INFRA1/2; NC-6 → INFRA6) — совпадают ✅.
- Executor contract: 9 обязательных полей config совпадают с §6.2 ✅.

### 7. Отсутствие объявления принятия capability (пройдено)

- Baseline doc (шапка) и config: `status: PROPOSED`; единственное упоминание ACCEPTED в конфиге —
  non-goal `implementer_does_not_set_ACCEPTED` ✅.
- Паспорт: `status: HANDOFF_READY` (исполнение, enum схемы; не принятие capability) ✅.
- `project/infra-state.json`: blob `ec0ce27…` идентичен main на проверяемом HEAD;
  `checkpoint_status.INFRA0 = PLANNED`, `task_status.INFRA0-001 = READY`, все `capabilities.* = false`
  — Implementer принятие не объявлял ✅.
- `project/state.json` (scientific): blob идентичен main; изменение относительно base 57c1e63
  внесено самим main (принятие NL1-001), не этой веткой ✅.

## Сводка findings

| ID | Серьёзность | Содержание | Блокирует? |
|---|---|---|---|
| FINDING-1 | LOW | §4 таблица TR-DISPATCH упоминает `C0`/`G0`; config = `["H0","C0"]` (§4.1 и RC3 согласуются с конфигом) | Нет — R2/bounded repair |
| FINDING-2 | INFO | `checkpoint: INFRA0` vs схема `^NL[0-8]$` — отклонение заранее задокументировано Implementer'ом; схема не менялась; практический валидатор паттерн не проверяет | Нет — кандидат в control WO |
| FINDING-3 | INFO | Negative test WO (NC-1) зафиксирован документально; механика отложена в `INFRA1-002` по зависимостям infra-plan (в R1 workflows нет — тестировать нечего) — отклонение задокументировано | Нет |

Итог: **PASS** (см. VERIFIER_VERDICT.md).
