# Verifier Evidence — INFRA1-001 (EX-INFRA1-001-R1)

**Verifier:** independent fresh verifier (не Implementer, не Reviewer ветки; verdict формируется только по фактам Git и собственному исполнению).
**Date (UTC):** см. commit timestamps ветки `verify/infra1-hosted-ci-r1`.
**Subject:** `0ab044b87e3e296942da3307f1b1c5ed0c34f5f1` (substantive HEAD ветки `infra/infra1-hosted-ci-r1`).
**Base:** `7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de` (canonical `main`).
**Verify worktree:** `C:\NanoLab\verify-infra-1-001`, branch `verify/infra1-hosted-ci-r1`, checkout subject.
**Reviewer PASS (не является основанием для этого verdict):** `0f1c348e5de55922b7b26f2addd9413f230abd7b` на `review/infra1-hosted-ci-r1`.

Инструменты верификатора: `git version 2.53.0.windows.1`, `Python 3.11.8`, `jsonschema 4.22.0`, `PyYAML` (Mechanical check script: `scratch/verify-infra1-001/check_workflow.py`, вне репозитория).

---

## 1. Scope / subject

### 1.1 Remote-факты (ls-remote bare repo `C:\NanoLab\.git-store\repo.git`)

- `refs/heads/main` = `7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de` — совпадает с base паспорта.
- `refs/heads/infra/infra1-hosted-ci-r1` = `ff8d86a5d2e6fbf8965318990ae2fa84b38f94af`.
- `refs/heads/review/infra1-hosted-ci-r1` = `0f1c348e5de55922b7b26f2addd9413f230abd7b` (= subject + 1 review-commit).
- `verify/infra1-hosted-ci-r1` до старта верификации не существовал (создан этой верификацией).
- Subject `0ab044b` существует в репо (`git cat-file -t` → `commit`).

### 1.2 Положение subject в ветке

```
git merge-base --is-ancestor 0ab044b87e3e296942da3307f1b1c5ed0c34f5f1 ff8d86a5d2e6fbf8965318990ae2fa84b38f94af
→ exit 0 (subject — предок текущего tip ветки)
```

Tip `ff8d86a` содержит ровно 2 коммита после subject: `5a73707` «harness: record INFRA1-001 implementation and validation», `ff8d86a` «harness: complete INFRA1-001 handoff» — bookkeeping-коммиты исполнения (events 0002–0004, summary.md, обновление паспорта), не входящие в верифицируемый subject. Verdict ниже касается **subject `0ab044b`**; факты tip использованы только там, где это указано явно (§5, схемы events 0002–0004).

### 1.3 Ancestry от base

```
git merge-base --is-ancestor 7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de 0ab044b87e3e296942da3307f1b1c5ed0c34f5f1
→ exit 0
```

Коммиты base..subject (ровно 3):

```
0ab044b docs(infra): document HOSTED_CI_R1 route mapping and machine config
ed2d596 ci(infra1): add hosted RC0 harness validation workflow (H0 only)
a689711 harness: start INFRA1-001 hosted CI execution
```

### 1.4 Изменённые файлы vs allowed_paths

```
git diff --name-status 7f17e9a..0ab044b
A  .github/workflows/hosted-ci.yml
A  config/infra/hosted-ci.v1.json
A  docs/infra/HOSTED_CI_R1.md
A  docs/work/executions/EX-INFRA1-001-R1/branch-passport.md
A  docs/work/executions/EX-INFRA1-001-R1/events/0001-work-order-started.json
A  docs/work/executions/EX-INFRA1-001-R1/passport.json
```

Allowed paths (`docs/work/executions/EX-INFRA1-001-R1/passport.json`): `.github/workflows/**`, `docs/infra/HOSTED_CI_R1.md`, `config/infra/hosted-ci.v1.json`, `docs/work/executions/EX-INFRA1-001-R1/**`.

| Файл | Паттерн allowed_paths | Вне scope? |
|---|---|---|
| `.github/workflows/hosted-ci.yml` | `.github/workflows/**` | нет |
| `config/infra/hosted-ci.v1.json` | `config/infra/hosted-ci.v1.json` | нет |
| `docs/infra/HOSTED_CI_R1.md` | `docs/infra/HOSTED_CI_R1.md` | нет |
| `docs/work/executions/EX-INFRA1-001-R1/*` (3 файла) | `docs/work/executions/EX-INFRA1-001-R1/**` | нет |

**6/6 файлов внутри allowed_paths; файлов вне allowed_paths — 0; удалений — 0.**

### 1.5 Неизменность state-файлов (Director gate)

```
git rev-parse 7f17e9a:project/state.json      → 66df364e01edabf15b1048a987a85e3027598b42
git rev-parse 0ab044b:project/state.json      → 66df364e01edabf15b1048a987a85e3027598b42  (идентичен)
git rev-parse 7f17e9a:project/infra-state.json → 17bb432f9e8666cacbd5b2a01c118a31591d731a
git rev-parse 0ab044b:project/infra-state.json → 17bb432f9e8666cacbd5b2a01c118a31591d731a  (идентичен)
```

`project/state.json` и `project/infra-state.json` на уровне blob идентичны base. В subject `capabilities.hosted_ci = false`, `INFRA1-001 = READY`, `next_work_order = INFRA1-001` (фронт INFRA не продвинут Implementer'ом).

### 1.6 Скан секретов

Скан добавленных строк subject-диффа (`git diff 7f17e9a..0ab044b`) по паттернам: `AKIA[0-9A-Z]{16}`, `ASIA[0-9A-Z]{16}`, `ghp_…`, `github_pat_…`, `xox…`, `sk-…`, `AIza…`, `-----BEGIN … PRIVATE KEY` → **0 совпадений**.

Дополнительный keyword-скан (`api_key|password|passwd|secret|token|credential`, без учета регистра) → 24 строки; все — декларации политики и негативные утверждения (`persist-credentials: false`, `secrets_used: []`, `secrets_in_artifacts: false`, «no secrets», owner-action о read-only GITHUB_TOKEN и т.п.). Реальных секретов/credential-материала нет. **Итог: 0 секретов.**

---

## 2. Workflow-инварианты (механическая проверка hosted-ci.yml)

Метод: парсинг `.github/workflows/hosted-ci.yml` через PyYAML (`yaml.safe_load`, ключ `on` извлечён с учётом YAML 1.1 boolean-коэрции) + перекрёстная сверка с `config/infra/hosted-ci.v1.json` и `config/infra/execution-baseline.v1.json`. Скрипт верификатора: `python check_workflow.py <worktree>` → **TOTAL=52 PASS=52 FAIL=0, exit 0**.

Ключевые инварианты (все PASS):

| Инвариант | Факт в workflow |
|---|---|
| Запрещённые триггеры | `pull_request_target`, `workflow_run`, `schedule`, `release`, `workflow_dispatch` отсутствуют в `on:` (5/5 absent) |
| Разрешённые триггеры | ровно `pull_request` (branches `["main"]`, types `["opened","synchronize","reopened"]`) и `push` (branches `["main"]`, ключ `tags` отсутствует, прочих ключей нет) |
| `runs-on` | единственный job `rc0-hosted-validation`: `ubuntu-latest`; self-hosted/`nanolab-*` labels — 0 |
| Permissions | workflow-level ровно `{contents: read}`; job-level permissions-блоков нет |
| `timeout-minutes` | 15 (единственный job) |
| Checkout | `actions/checkout@93cb6efe…` (full 40-hex SHA), `persist-credentials: false`, `fetch-depth: 0` |
| Артефакты | `actions/upload-artifact@330a01c4…` только при `if: failure()`, `retention-days: 7` |
| Concurrency | `cancel-in-progress: true` |
| Secrets | литеральное `${{ secrets` в тексте workflow — 0 вхождений |
| `uses`-шаги | ровно 2 (checkout, upload-artifact), оба pinned по full SHA |

Сверка `config/infra/hosted-ci.v1.json` ↔ workflow (все PASS): name, triggers (по-полю), `forbidden_triggers_absent`, permissions, routes `[TR-PR, TR-PUSH-MAIN]`, `runs_on ["ubuntu-latest"]`, `timeout_minutes 15`, `resource_class RC0_HOSTED_VALIDATION`, `runner_class H0`, pins checkout/upload (SHA+version+persist_credentials+fetch_depth+retention_days), `status: PROPOSED`, `secrets_used: []`, `fork_pr_secrets_available: false`, `write_permissions_granted: false`.

Сверка с EXECUTION-BASELINE-R1 (machine-readable `execution-baseline.v1.json`, все PASS):

- Маршруты: `TR-PR` (events `pull_request`) → `allowed_runner_classes ["H0"]`; `TR-PUSH-MAIN` (refs `refs/heads/main`) → `["H0"]`; workflow обслуживает ровно эти два маршрута.
- Запреты: `TR-PRT` и `TR-WFRUN` = `FORBIDDEN_R1` — соответствующие триггеры в workflow физически отсутствуют.
- Labels: класс `H0` = `["ubuntu-latest","ubuntu-24.04"]`; workflow использует `ubuntu-latest` ∈ H0; self-hosted labels отсутствуют (NC-1 конструктивно).
- Resource class: `RC0_HOSTED_VALIDATION` (runner `H0`, `max_wall_clock_minutes = 15`) ↔ `timeout-minutes: 15`; `resource_classes_used = ["RC0_HOSTED_VALIDATION"]`, `RC1_HOSTED_EXTENDED` объявлен не используемым.

## 3. Пины actions (live `git ls-remote --tags` GitHub)

```
git ls-remote --tags https://github.com/actions/checkout refs/tags/v5.0.1
93cb6efe18208431cddfb8368fd83d5badbf9bfd   refs/tags/v5.0.1      → exit 0

git ls-remote --tags https://github.com/actions/upload-artifact refs/tags/v5.0.0
330a01c490aca151604b8cf639adc76d48f6c5d4   refs/tags/v5.0.0      → exit 0

git ls-remote --tags … 'refs/tags/v5.0.1^{}' / 'refs/tags/v5.0.0^{}' → пусто (теги lightweight,
указывают точно на коммит; аннотированного объекта-тега нет)
```

| Action | Ожидание в workflow/config | ls-remote | Совпадение |
|---|---|---|---|
| `actions/checkout` v5.0.1 | `93cb6efe18208431cddfb8368fd83d5badbf9bfd` | `93cb6efe18208431cddfb8368fd83d5badbf9bfd` | ✅ точное |
| `actions/upload-artifact` v5.0.0 | `330a01c490aca151604b8cf639adc76d48f6c5d4` | `330a01c490aca151604b8cf639adc76d48f6c5d4` | ✅ точное |

---

## 4. Локальное воспроизведение чеков workflow

Среда верификатора: Windows, `Python 3.11.8` (анлог `python3` из workflow). Рабочий каталог — verify-worktree.

### 4.1 Check 1 — JSON-syntax по всем tracked `*.json`

```
$files = git ls-files '*.json'                    → 59 файлов
foreach: python -m json.tool <file> (stdout > null)
итог: json-tool-ok=59 failed=0                    → все 59 OK, exit 0 у каждого
```

### 4.2 Check 2 — harness control consistency

```
PYTHONPATH=scripts python -m harness.cli check-consistency --root .
→ exit 0
{"schema":"nanolab.control_development_output.v1","command":"CHECK_CONSISTENCY","ok":true,
 "errors":[],"warnings":[],"frontier":"NL1","next_work_order":"NL1-002",
 "head":"<verify-HEAD>","tree":"<tree>", "counts":{"stages":9,"tasks":18,"experiments":7}}
```

Примечание: команда исполнена на verify-ветке (HEAD сместился на evidence-коммиты верификатора относительно subject); верифицируемые контракты (`project/plan.json`, `project/state.json`, goals/catalog/scheduler) не менялись (blob-доказательство в §1.5, changes покрыты только `docs/infra/evidence/INFRA1-001/**`).

### 4.3 Check 3 — work events integrity (`work_cli validate EX-INFRA1-001-R1`)

```
PYTHONPATH=scripts python -m harness.work_cli validate docs/work/executions/EX-INFRA1-001-R1
→ exit 0
{"schema":"nanolab.control_work_output.v1","command":"VALIDATE","ok":true,"errors":[],
 "execution_id":"EX-INFRA1-001-R1","work_order_id":"INFRA1-001","status":"STARTED",
 "passport_sha256":"7b5a831fc5ba6888b128554d00ed9efb6e59be1e61446450d19839497bb1e37e",
 "event_types":["WORK_ORDER_STARTED"],"has_terminal_handoff":false,"has_summary":false}
```

Валидация прямой директорией (без diff-scope из workflow Check 3) — результат корректен: исполнение на subject-этапе содержит только событие STARTED; терминального handoff/summary ещё нет — это факты subject, а не дефект. Задокументированное расхождение «terminal-last vs review-corrections» (HOSTED_CI_R1.md §7.1, `known_discrepancies` в конфиге) верификатором подтверждено как корректно описанное: каталоги `EX-INFRA0-001-R1`/`EX-NL1-001-R1` на `main` содержат пост-терминальный `0005-review-corrections.json`, поэтому blanket-валидация в CI была бы вечно красной; Check 3 в workflow корректно скоупит только изменённые EX-* каталоги.

## 5. Схемы (jsonschema, Draft 2020-12 + FormatChecker)

Валидатор: `jsonschema 4.22.0`, `Draft202012Validator(..., format_checker=FormatChecker())`.

| Документ | Схема | Результат |
|---|---|---|
| `events/0001-work-order-started.json` (subject) | `work-event.schema.v1.json` | **PASS** (0 ошибок; `timestamp_utc` валиден как date-time; `subject_sha` = base `7f17e9a…` — корректно для START-события) |
| `events/0002-implementation-committed.json` (tip `ff8d86a`, вне subject) | `work-event.schema.v1.json` | **PASS** |
| `events/0003-validation-recorded.json` (tip, вне subject) | `work-event.schema.v1.json` | **PASS** |
| `events/0004-handoff-completed.json` (tip, вне subject) | `work-event.schema.v1.json` | **PASS** |
| `passport.json` (subject) | `execution-passport.schema.v1.json` | **1 отклонение — известное, задокументированное**: `checkpoint: "INFRA1"` не матчится паттерном `^NL[0-8]$` |

Отклонение паспорта: схема написана только для научного трека `NL0–NL8` и не покрывает INFRA; значение `INFRA1` семантически корректно (= `project/infra-state.json.frontier`); отклонение задокументировано Implementer'ом в `branch-passport.md` (отклонение №1) и в event 0001, того же класса, что принятый прецедент `EX-INFRA0-001-R1`; практический валидатор `work_cli` паттерн checkpoint не проверяет (§4.3 — ok=true). Расширение схемы вынесено в отдельный control WO (кандидат), схема в этом исполнении не менялась (и не могла — вне allowed_paths). Верификатор классифицирует как **известное, задокументированное, не блокирующее** отклонение.

## 6. Отсутствие capability-заявки и self-accept

### 6.1 `hosted_ci` нигде не `true`

```
git grep -n 'hosted_ci' 0ab044b --  → 8 вхождений, из них с "true" — 0
```

Единственная декларация capability: `project/infra-state.json: "hosted_ci": false` (blob идентичен base, §1.5). Остальные 7 вхождений — имена схем/артефактов (`hosted_ci_debug_bundle`, `nanolab.hosted_ci_debug_manifest.v1`, `infra_hosted_ci_config`) и текст документации, не заявления capability.

### 6.2 `ACCEPTED` не объявлен

Добавленные subject-строки с `ACCEPTED` (4) — все ссылочные/негативные:
1. workflow-комментарий «Authority: EXECUTION-BASELINE-R1, ACCEPTED» — ссылка на факт приёмки baseline (Director, INFRA0), не заявка по INFRA1-001;
2. HOSTED_CI_R1.md — та же authority-ссылка;
3. «Статус: PROPOSED — Implementer не выставляет ACCEPTED» — явный запрет self-accept;
4. event 0001 summary — «INFRA0-001 ACCEPTED» (факт предыдущей задачи из `infra-state.json`).

Машиночитаемый статус нового конфига: `config/infra/hosted-ci.v1.json → "status": "PROPOSED"`; документ: `HOSTED_CI_R1.md → Статус: PROPOSED`. `project/infra-state.json`: `INFRA1-001 = READY`, `INFRA1 = IN_PROGRESS`, `next_work_order = INFRA1-001` — фронт не продвинут (blob идентичен base). **Capability-заявки нет, self-accept нет.**
