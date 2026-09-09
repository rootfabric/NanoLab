# Verifier Verdict — INFRA1-002 «Add PR validation gates» (RE_REVIEW_R1)

**Роль:** независимый FRESH VERIFIER (контекст имплементёра и reviewer'а при работе не использовался; факты — Git + собственное исполнение).
**Дата:** 2026-09-09. **Вердикт:** `PASS` — ремонт R1 принят, поставка готова к Director checkpoint `INFRA1-002` и Human Gate merge.
**Субъект:** substantive HEAD `74e17c734d600b74e9d25209ab8f609c3ca40244` (ветка `infra/infra1-validation-gates-r1`); tip `5c2e1b21342e851e0eb867abcb06da79301d2d52` отличается только пост-терминальными events `0005/0006` собственного execution (проверено diff'ом: +2 файла, +56 строк). **Base:** `15a2c9b1b5c095e24e2e1c24afd77feef5361102`.
**Метод:** собственный worktree `C:\NanoLab\verify-infra-1-002` @ `74e17c7` (ветка `verify/infra1-validation-gates-r1`); все пробы — собственные фикстуры во временном каталоге `%TEMP%\nfv-infra1-002` (вне репозитория), собственный probe-раннер; все прогоны локальные (Windows, Python 3.11.8, stdlib-only). Пробы reviewer'а не копировались — матрица составлена заново.

---

## 1. Scope и subject

| Проверка | Результат |
|---|---|
| Ancestry | `git merge-base --is-ancestor 15a2c9b 74e17c7` → **rc=0** |
| Merge-base с каноническим main | `merge-base 15a2c9b origin/main` = `15a2c9b` (`origin/main` = `a4533ab` = base + PR #27, science addendum; INFRA-поверхность diff PR не затрагивает — чистый PR) |
| Diff `15a2c9b..74e17c7` | **17 файлов** (2 M, 15 A): `.github/workflows/hosted-ci.yml`, `config/infra/validation-gates.v1.json`, `docs/infra/VALIDATION_GATES_R1.md`, `docs/work/executions/EX-INFRA1-002-R1/**` (passport, summary, events 0001–0004), `scripts/harness/work_cli.py`, `scripts/harness/workflow_lint.py`, `tests/__init__.py`, `tests/test_infra_workflow_lint.py`, `tests/test_work_cli_corrections.py` |
| Соответствие allowed_paths паспорта | Все 17 файлов внутри `allowed_paths`, **кроме 3 файлов evidence** — см. ниже |
| Файлы вне allowed_paths | (1) `REVIEWER_VERDICT.md` + `REVIEW_LOG_R1.md` — вошли merge-коммитом `a6aba22` (первый родитель `97ac978`, второй `1ca40b6` review-ветки; авторство REVIEWER, прецедент INFRA1-001); (2) `REPAIR_MAP_R1.md` — путь durably задокументирован имплементёром в event `0005-repair-completed` («вне исходных allowed_paths — авторизовано миссией/вердиктом §4.5»); размещение Repair Map в evidence-каталоге соответствует протоколу (AGENTS.md §10). **Нарушением не считается** |
| State-файлы (blob-сравнение base↔HEAD) | `project/state.json` `629ac9e1`, `project/plan.json` `c3e854da`, `project/infra-state.json` `d9b0be08`, `project/infra-plan.json` `fc0357ec`, `config/infra/hosted-ci.v1.json` `c6d52e3a`, `docs/SCIENTIFIC_METHOD.md` `2feeebcb` — **все blob-идентичны**; `git diff 15a2c9b..74e17c7 -- project/ experiments/ config/control/ docs/SCIENTIFIC_METHOD.md` — **пусто** (science и state не тронуты; ACCEPTED `hosted-ci.v1.json` не редактировался — заявка §4.3 дока подтверждена) |
| Tip vs substantive | `74e17c7..5c2e1b2` — только `events/0005-repair-completed.json`, `events/0006-repair-validation.json` |

## 2. NC-линт — собственная негативная матрица (30 проб, все исполнены)

Собственный compliant-каркас (`verifier-probe`: mapping `on:` с `ready_for_review`, `permissions: contents: read`, pinned action, timeout 10) + точечные мутации. Каждая негативная проба — ожидание «exit≠0 + указанный rule_id»; матрица 30/30 ожидаемых исходов (probe-раннер: `mismatches=0`).

| Проба (собственная) | Исход | rule_id |
|---|---|---|
| Позитив: **реальный** `hosted-ci.yml` | **exit 0**, 0 violations | — |
| Позитив: push-only mapping (NOTE-1 fix) | exit 0 | — |
| `pull_request_target` в mapping `on:` | exit 1 | `NC2_FORBIDDEN_TRIGGER` |
| `workflow_run` в mapping `on:` | exit 1 | `NC2_FORBIDDEN_TRIGGER` |
| `schedule` в mapping `on:` | exit 1 | `NC2_TRIGGER_NEEDS_BASELINE_REVISION` |
| `on: push` (scalar, MAJOR-1) | exit 1 | `NC2_TRIGGERS_UNSUPPORTED_FORM` |
| `on: [push, pull_request_target]` (flow, MAJOR-1) | exit 1 | `NC2_TRIGGERS_UNSUPPORTED_FORM` |
| `on: [push]` (flow, чистый — форма сама блокируется) | exit 1 | `NC2_TRIGGERS_UNSUPPORTED_FORM` |
| `on:` отсутствует (MAJOR-1) | exit 1 | `NC2_TRIGGERS_BLOCK_MISSING` |
| `on:` null (MAJOR-1) | exit 1 | `NC2_TRIGGERS_BLOCK_MISSING` |
| `runs-on: &cpu nanolab-cpu` + `runs-on: *cpu` (MAJOR-2) | exit 1 | `WORKFLOW_UNPARSEABLE` |
| `runs-on: self-hosted` | exit 1 | `NC1_SELF_HOSTED_LABEL` |
| `runs-on: nanolab-gpu` | exit 1 | `NC1_SELF_HOSTED_LABEL` |
| `runs-on: nanolab-hpc-cpu-01` (префикс) | exit 1 | `NC1_SELF_HOSTED_LABEL` |
| `runs-on: ${{ … }}` (динамика) | exit 1 | `NC1_DYNAMIC_RUNS_ON` |
| job со `steps` без `runs-on` | exit 1 | `NC1_RUNS_ON_MISSING` |
| `secrets['DEPLOY_TOKEN']` (одинарные кавычки, MINOR-1) | exit 1 | `NC7_SECRETS_REFERENCE` |
| `secrets["DEPLOY_TOKEN"]` (двойные) | exit 1 | `NC7_SECRETS_REFERENCE` |
| `secrets.DEPLOY_TOKEN` (dot, регресс) | exit 1 | `NC7_SECRETS_REFERENCE` |
| workflow `permissions: contents: write` | exit 1 | `NC4_WRITE_PERMISSION` |
| job-level `pull-requests: write` | exit 1 | `NC4_WRITE_PERMISSION` |
| `permissions:` отсутствует | exit 1 | `NC4_PERMISSIONS_BLOCK_MISSING` |
| `timeout-minutes: 0` (ниже [1,60]) | exit 1 | `BUDGET_TIMEOUT_BOUNDS` |
| `timeout-minutes: 61` | exit 1 | `BUDGET_TIMEOUT_BOUNDS` |
| без `timeout-minutes` | exit 1 | `BUDGET_TIMEOUT_REQUIRED` |
| action по тегу `@v5` (вместо SHA) | exit 1 | `PIN_ACTION_FULL_SHA` |
| multi-doc (`---` второй документ с `pull_request_target`+`nanolab-cpu`) | exit 1 | `WORKFLOW_UNPARSEABLE` (explicit rejection) |
| внешний reusable `uses: evil-org/…@main` | exit 1 | `NC2_EXTERNAL_REUSABLE_WORKFLOW` |
| TAB-ключ job'а (исследование, см. FINDING V-1) | **exit 0** | (нет — см. V-1) |
| TAB под `on:` (исследование) | exit 1 | `WORKFLOW_UNPARSEABLE` |

Бывшие обходы раунда 1 (MAJOR-1/MAJOR-2/MINOR-1, multi-doc) независимо подтверждены закрытыми; blocking-критерий (a) — «untrusted PR route не может выбрать self-hosted label» — воспроизведён в обе стороны.

## 3. Corrections-aware `work_cli` — исполнение

Каталог проб: копии `EX-INFRA1-002-R1` во временном каталоге; каждая негативная проба — ожидание exit 3 + конкретная ошибка. **13/13 групп исходов подтверждены.**

| Проба (собственная) | Исход |
|---|---|
| `validate` всех 10 `EX-*` репозитория | **10/10 OK**, exit 0 |
| Позитив-контроль фикстуры (копия без мутаций) | OK |
| Unmarked post-terminal (`VALIDATION_RECORDED` после handoff) | **exit 3**: «events after terminal/handoff must be review-corrections events …» |
| `REVIEW_CORRECTIONS` ts 2020 < terminal 2026 | **exit 3**: «corrections event timestamp must be >= terminal event timestamp» |
| `REVIEW_CORRECTIONS` от `actor_role=IMPLEMENTER` | **exit 3**: «must be authored by REVIEWER, VERIFIER or DIRECTOR, not by IMPLEMENTER» |
| Новое событие с 7-hex `abc1234` | **exit 3**: «invalid subject_sha (full 40-hex required …)» |
| Легаси-**значение** `9cc83e8` вне легаси-пары | **exit 3**: «invalid subject_sha» |
| Легаси-**пара** `(execution, 0002-campaign-runs-completed)` в другом execution | **exit 3**: «invalid subject_sha» |
| Второй terminal после corrections (регресс) | exit 3: «more than one terminal/handoff event» |
| `REVIEW_CORRECTIONS` до handoff (регресс) | exit 3: «allowed only after the terminal/handoff event» |
| Убывающие ts внутри хвоста (регресс) | exit 3: «timestamps must be non-decreasing» |
| Легитимный путь: `REVIEW_CORRECTIONS` от VERIFIER, ts ≥ terminal, 40-hex | **OK**, `has_post_terminal_corrections=true` |
| Tip `5c2e1b2`: собственный execution c corrections-хвостом 0005/0006 | **OK**, `has_post_terminal_corrections=true`, хвост `[HANDOFF_COMPLETED → CONTINUATION_CHECKPOINT → CONTINUATION_CHECKPOINT]` |

Блокирующий критерий (b) воспроизведён: обычный поток не ослаблен, corrections-класс семантически строг (MINOR-2/MINOR-3 закрыты).

## 4. Полные чеки (на `74e17c7`, воспроизведены)

| Чек | Результат |
|---|---|
| 1. JSON-syntax, все tracked `*.json` | **111/111 OK**, 0 bad |
| 2. `harness.cli check-consistency` | `ok=true`, errors/warnings пусто; head `74e17c7…`, tree `c85a9277…` (= заявка REPAIR_MAP) |
| 3. `work_cli validate` 10 `EX-*` | **10/10 OK** |
| 4. `workflow_lint --root .` | `ok=true`, 0 violations, `config_revision=VALIDATION-GATES-R1` |
| 5. `python -m unittest discover -s tests -t .` | **Ran 59 tests — OK** |

## 5. Схемы и события EX-INFRA1-002-R1

- Поток на substantive HEAD: `0001 WORK_ORDER_STARTED` (13:02:30Z, subject = base `15a2c9b…`) → `0002/0003` → `0004 HANDOFF_COMPLETED` (13:21:10Z, subject = substantive раунда 1 `0330d15…`) — валидатор: `ok=true`.
- Corrections-хвост на tip `5c2e1b2`: `0005-repair-completed` (13:55:08Z ≥ 13:21:10Z) + `0006-repair-validation` (13:58:30Z ≥ 13:55:08Z, неубывающие), оба `CONTINUATION_CHECKPOINT` от `IMPLEMENTER` (роль-ограничение действует только для `REVIEW_CORRECTIONS` — корректно), оба с полным 40-hex `subject_sha=74e17c7…` — **repaired-валидатор принимает**, `ok=true` (собственный execution догфудит собственные правила — подтверждено).
- Задокументированные floor/ceiling-расхождения с control-схемами подтверждены фактом: `work-event.schema.v1.json` — enum без `REVIEW_CORRECTIONS` (строка 13), `subject_sha` pattern `^[0-9a-f]{40}$` (строка 15) против 4 легаси-событий `EX-NL1-002-R1` c `9cc83e8`; `execution-passport.schema.v1.json` — `checkpoint` `^NL[0-8]$` против `"INFRA1"` в паспорте. Механической валидации events по JSON-схеме нет — живого конфликта нет; sync осознанно отложен в control WO (конфиг `non_goals`, док §2.4/§8). К сведению Director'у (см. FINDING V-3).

## 6. Capability-declaration / self-acceptance — отсутствуют

- `project/infra-state.json` blob-идентичен base; `"hosted_ci": false` **не флипнут**.
- Статус конфига `validation-gates.v1.json` и дока `VALIDATION_GATES_R1.md` — `PROPOSED`; паспорт — `HANDOFF_READY`; все вхождения «ACCEPTED» в diff — ссылки на предыдущие authority (`EXECUTION-BASELINE-R1`, `hosted-ci.v1.json` R1) и явная строка «Implementer не выставляет ACCEPTED».
- Решения о приёмке в diff не вносятся; review-вердикты authored независимым REVIEWER на review-ветке; верификатор (эта ревизия) решение Director не подменяет.

## 7. Findings верификатора

- **V-1 (MINOR, подтверждает MINOR-4 RE_REVIEW_R1)** — таб-чек парсера мёртвый код (срез `[:indent]` состоит только из ведущих пробелов); эмпирика моей матрицы: TAB-индентированный ключ job'а → **exit 0** (job молча уходит в top-level, job-правила пропускаются), TAB под `on:` → `WORKFLOW_UNPARSEABLE`. Направление fail-safe (GitHub отвергает TAB-индентацию целиком — файл неисполним, NC-обхода нет), но заявка «tabs → fail closed» не держится во всех размещениях. Follow-up уже durably зафиксирован re-review (ревизия линта до INFRA2-001) — не блокирует приёмку ремонта.
- **V-2 (NOTE, подтверждает NOTE-5 RE_REVIEW_R1)** — `jobs:` в не-mapping форме пропускает job-правила; эмпирика: sequence под `jobs:` с `runs-on: nanolab-cpu` → exit 0. Тот же fail-safe класс (GitHub такой файл не исполнит); кандидат в тот же пакет «fail-closed на schema-невалидных формах».
- **V-3 (NOTE, уже задокументировано)** — schema sync (enum `REVIEW_CORRECTIONS`, 40-hex, паспорт-паттерн `(NL|INFRA)[0-7]`): расхождения фактически подтверждены (§5); третий INFRA-прецедент подряд — кандидату накапливать повторения больше не стоит, пакетный control WO до INFRA2-001 целесообразен.
- **К сведению** — base drift миссии воспроизведён (`origin/main` = `a4533ab` = base + PR #27; merge-base = base): задокументирован имплементёром (event 0001, док §8.1), не нарушение.

## 8. Вердикт

**`PASS`.** Scope чист (17 файлов = allowed_paths + 2 durably задокументированных отклонения protocol-класса); state/science/чужие executions не тронуты (blob-факты); blocking-критерии приёмки (a) и (b) воспроизведены исполнением в обе стороны (26 негативных линт-проб + 9 валидаторных FAIL/OK-проб + 5 штатных чеков); все директивы ремонта REVIEWER_VERDICT R1 §4 (MAJOR-1, MAJOR-2, MINOR-1, MINOR-2/MINOR-3, обновление дока/конфига без переписывания истории) подтверждены; corrections-хвост 0005/0006 собственного исполнения принимается repaired-валидатором. Findings V-1/V-2/V-3 — не блокирующие, follow-up'ы уже durably зафиксированы (RE_REVIEW_R1 MINOR-4/NOTE-5; schema sync — control WO).

**Рекомендация:** Director checkpoint `INFRA1-002` (закрытие вместе с вопросом checkpoint `INFRA1`), затем Human Gate merge в `main`. Follow-up'ы MINOR-4/NOTE-5/schema-sync — обязательны к следующей ревизии линта **до INFRA2-001** (NC-1 — защитник label-namespace при активации self-hosted). Научных утверждений вердикт не содержит: зелёные чеки — технический факт, не научный PASS.

**Exact HEADs:** subject верификации `74e17c734d600b74e9d25209ab8f609c3ca40244`; branch tip `5c2e1b21342e851e0eb867abcb06da79301d2d52`; эта ревизия — ветка `verify/infra1-validation-gates-r1` (см. `git log`).
