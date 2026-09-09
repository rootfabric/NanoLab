# INFRA — Safe GitHub-hosted CI (HOSTED_CI_R1)

**Revision:** `HOSTED-CI-R1`
**Work Order:** `INFRA1-001` (`project/infra-plan.json` задача «Add hosted harness CI»; файл `docs/work/WO-INFRA1-001.md` в canonical `main` отсутствует — см. §8)
**Execution:** `EX-INFRA1-001-R1` (branch `infra/infra1-hosted-ci-r1`)
**Base SHA:** `7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de` (exact canonical `main`)
**Authority:** [`EXECUTION_BASELINE_R1.md`](EXECUTION_BASELINE_R1.md) (`EXECUTION-BASELINE-R1`, ACCEPTED)
**Machine-readable counterpart:** [`config/infra/hosted-ci.v1.json`](../../config/infra/hosted-ci.v1.json)
**Статус:** `PROPOSED` — Implementer не выставляет ACCEPTED; приёмка — независимый Reviewer/Verifier и Director gate.

---

## 1. Назначение и границы

Первый исполняемый GitHub-hosted workflow для untrusted route: на PR и push в `main` автоматически выполняются дешёвые harness/schema/JSON-проверки на ephemeral hosted runner класса `H0`. Self-hosted научные узлы не участвуют; доступ к ним по построению отсутствует.

Вне границы WO: self-hosted runners, secrets, GPU, paid compute, artifact store, scheduler, `pull_request_target`/`workflow_run`-маршруты, механические negative-control линтеры (это `INFRA1-002`), изменения `project/infra-state.json` и `project/state.json` (Director gate).

## 2. Что включено

`.github/workflows/hosted-ci.yml` — единственный workflow этого этапа:

| Параметр | Значение | Обоснование (baseline) |
|---|---|---|
| Триггеры | `pull_request` → `main` (opened/synchronize/reopened); `push` → `main` | `TR-PR`, `TR-PUSH-MAIN` (§4); fork PR и in-repo PR равноправны — никакой привилегии по авторству (§4.1) |
| Runner | `runs-on: ubuntu-latest` — класс `H0`, hosted labels only | §3: `H0` = `ubuntu-latest`/`ubuntu-24.04`; зарезервированные `nanolab-cpu`/`nanolab-gpu`/`nanolab-hpc-*` и `self-hosted` в `runs-on` отсутствуют (`NC-1`) |
| Permissions | workflow-level `permissions: contents: read`, больше ничего; write-объявлений нет | §5.2, `NC-4` |
| Secrets | не используются ни одним шагом; fork PR их не получает (платформенный инвариант, не обходится) | §5.3, `NC-7` |
| Бюджет | `timeout-minutes: 15` на job = `RC0_HOSTED_VALIDATION` | §6: wall-clock ≤ 15 мин; unbounded jobs запрещены |
| Concurrency | группа `hosted-ci-<event>-<ref>`, `cancel-in-progress: true` | бюджетная гигиена: перезапущенный run наследует тот же бюджет `RC0`, а не суммирует (`NC-6`); снижение спам-нагрузки (§9) |
| Actions | `actions/checkout` @ `93cb6efe18208431cddfb8368fd83d5badbf9bfd` (v5.0.1), `actions/upload-artifact` @ `330a01c490aca151604b8cf639adc76d48f6c5d4` (v5.0.0) — pin по full commit SHA, теги lightweight и указывают точно на эти коммиты (проверено `git ls-remote`) | §9: «pinned actions (обязателен с INFRA1-001)» |
| Checkout | `persist-credentials: false`, `fetch-depth: 0` | токен не остаётся в `.git/config` compute-процесса (§5.4); полная история нужна только для diff-scope Check 3 |
| Fail-close | нет никакого fallback на другой executor при недоступности hosted runner | `NC-5`: отказ = отказ |

### 2.1 Содержимое чеков (один job `rc0-hosted-validation`)

1. **JSON-syntax** — `python3 -m json.tool` по каждому tracked `*.json` (`git ls-files -z '*.json'`): машинные контракты `config/**`, состояние `project/**`, evidence JSON.
2. **Harness check-consistency** — `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .`: перекрёстная согласованность `project/plan.json`, `project/state.json`, goals/catalog/scheduler-policy (DAG, id-множества, frontier).
3. **Work-events integrity** — `PYTHONPATH=scripts python3 -m harness.work_cli validate <dir>` для **изменённых** этим PR/push каталогов `docs/work/executions/EX-*` (diff против merge-base с `origin/main`; для push — `github.event.before`, с fallback на `HEAD~1`; при недоступности базы или отсутствии изменённых каталогов — step корректно пропускается). Обоснование scope — §7.1 ниже.

Все три — stdlib-only, без сети, без секретов, суммарно ≈1–2 мин на hosted VM.

### 2.2 Артефакты

Только ephemeral debug-материал **при падении** job'а: `upload-artifact` `hosted-ci-debug-<run_id>-<attempt>`, retention 7 дней. Перед выкладкой генерируется `manifest.json` (`nanolab.hosted_ci_debug_manifest.v1`) с обязательными provenance-полями baseline §7.1: `sha256`, `size_bytes`, `producer_run_id`, `subject_sha`, `storage_location`; `scientific_evidence: false`. Секреты в логи/артефакты не выводятся. Успешный run артефактов не производит.

## 3. Что исключено (и куда это идёт)

| Исключено | Причина | Куда |
|---|---|---|
| `pull_request_target`, `workflow_run`, `schedule`, tag/release триггеры | `TR-PRT`/`TR-WFRUN` = FORBIDDEN_R1 (§4); TR-SCHEDULE/TR-TAG deferred | не вводятся без новой ревизии baseline |
| Self-hosted labels / runners | `NC-1`, §3 | `INFRA2-001` |
| RC1 job (extended hosted validation, ≤60 мин) | Контракт существует, но ни одна проверка сейчас не требует >15 мин; RC1 обязан быть явно объявлен в workflow при появлении | по потребности, отдельный workflow/шаг с `timeout-minutes: 60` и явным объявлением |
| Механические negative controls (lint `runs-on`/permissions, workflow-graph) | Требуют инфраструктуры линтинга; это заголовочная задача следующего WO | `INFRA1-002` (§8 ниже, NC-мэппинг) |
| Secrets, artifact store, GPU, paid compute | Вне scope этапа | поздние INFRA-стадии |
| Изменение настроек репозитория из этого WO | Настройки GitHub не коммитятся через git; доступ через UI — владелец | §6 ниже (owner actions) |

## 4. Маппинг на baseline

| Раздел `EXECUTION-BASELINE_R1` | Реализация здесь |
|---|---|
| §3 Runner classes / labels (H0) | `runs-on: ubuntu-latest`; ни одного self-hosted label |
| §4 `TR-PR` | `pull_request` → H0, `contents: read`, без secrets |
| §4 `TR-PUSH-MAIN` | `push` (main) → H0, минимальные permissions, таймаут |
| §4 `TR-PRT`/`TR-WFRUN` FORBIDDEN | триггеры физически отсутствуют в workflow |
| §4.1 контракт маршрутизации | hosted-only для обоих маршрутов; fork и in-repo PR без привилегии |
| §5.1 repo default read-only | объявлено как owner action (§6); каждый workflow независимо несёт явный `permissions:` |
| §5.2–5.4 token/secrets | `contents: read`; write запрещён; `persist-credentials: false`; секреты не используются |
| §6 RC0 / правила бюджетов | `timeout-minutes: 15`; concurrency cancel-in-progress; retries не увеличивают бюджет |
| §7 artifact policy | §2.2: manifest с provenance-полями, ephemeral, не scientific evidence |
| §8 NC-1..NC-7 | см. §5 |
| §9 threat matrix (pinned actions) | pin по full commit SHA |

## 5. Negative controls: что заложено сейчас, что в INFRA1-002

**Заложено конструктивно этим WO** (инвариант соблюдён самим видом workflow, но без механического «lint-доказательства»):

| NC | Как соблюдается в `hosted-ci.yml` |
|---|---|
| `NC-1` внешний PR на личной машине | `runs-on: ubuntu-latest` only; self-hosted labels отсутствуют во всех `runs-on` |
| `NC-2` обход границы через цепочку | нет `pull_request_target`, нет `workflow_run`; untrusted артефакты никуда в trusted-зону не передаются |
| `NC-4` эскалация прав из PR route | явный `permissions: contents: read`; ни одного write-блока |
| `NC-5` тихий fail-open | нет fallback/strategy на другой исполнитель |
| `NC-6` расход бюджета через retries | жёсткий job timeout; concurrency cancel-in-progress; rerun наследует те же 15 мин |
| `NC-7` утечка secrets во внешний PR | секреты не используются; fork PR их не получает; обходных триггеров нет |

**Откладывается в `INFRA1-002` как механические проверки** (lint + negative tests): NC-1 (негативный тест «untrusted route не может выбрать self-hosted label»), NC-2/NC-7 (workflow-graph lint на запрещённые триггеры и мосты), NC-4 (permissions lint), NC-5 (review-подтверждение конфигурации при INFRA1/2), NC-6 (scheduler/queue policy, INFRA6), NC-3 (dispatch-валидатор, INFRA2-002). `INFRA1-002` также закрывает discovered discrepancy §7.1 и решает вопрос repo-settings enforcement.

## 6. Owner actions (настройки репозитория GitHub, вне git)

Выполнить владельцу/admin'у в Settings репозитория (baseline §5.1 фиксирует это за INFRA1-001, но настройка не выражается git-коммитом):

1. **Actions → General → Workflow permissions → Read repository contents and packages permissions** (repo default `GITHUB_TOKEN` = read-only).
2. Branch protection `main`: required PR, required status check `RC0 hosted validation (H0)`, запрет force-push.
3. Не регистрировать self-hosted runner со стандартными hosted labels (§3 правило 2) — актуально с `INFRA2-001`.

## 7. Находки и задокументированные отклонения

1. **`work_cli` terminal-last vs review-corrections (harness discrepancy).** `scripts/harness/work_cli.py` требует, чтобы terminal event (`HANDOFF_COMPLETED` и др.) был последним; в canonical `main` каталоги `EX-INFRA0-001-R1` и `EX-NL1-001-R1` содержат пост-терминальный `CONTINUATION_CHECKPOINT` (`0005-review-corrections.json`) — легитимный идиом «corrections — новым event» из AGENTS.md. Сплошной `validate` всех EX-* в CI был бы вечно красным независимо от PR. Решение этого этапа: Check 3 валидирует **только изменённые** каталоги (diff-scope). Политическое решение — расширить валидатор corrections-aware правилом или формализовать пост-терминальные corrections — отнесено в `INFRA1-002`. Это находка для reviewer, не регрессия.
2. **`docs/work/WO-INFRA1-001.md` отсутствует в `main`.** Авторство WO — Director authority, создание файла вне allowed_paths этого исполнения. Scope исполнен по тексту миссии Implementer'а + задаче `INFRA1-001` из `project/infra-plan.json` + §13.3 baseline.
3. **`tests/task_bus/` на `main` не существует.** Упомянутые в задаче pytest-тесты task bus живут в невлитой ветке (`control/git-task-bus-r1`); в canonical `main` нет ни `tests/`, ни pytest-зависимости, поэтому в hosted-подмножество они не входят (появятся в CI вместе с влитой веткой — кандидат в `INFRA1-002`).
4. **PowerShell-обёртки `CONTROL_*.ps1` не переносятся в Linux-чек как есть.** Обёртки — тонкие прокси к `python -m harness.*`; workflow вызывает питон-модули напрямую (эквивалент `CONTROL_DEVELOPMENT.sh` без зависимости от оболочки). `pwsh` на ubuntu runner доступен, но прямой вызов модуля стабильнее и дешевле.
5. **Паспорт использует `checkpoint: INFRA1`** — паттерн `^NL[0-8]$` в `execution-passport.schema.v1.json` не покрывает INFRA-трек (тот же класс отклонения, что в `EX-INFRA0-001-R1`); практический валидатор паттерн не проверяет; расширение схемы — кандидат в отдельный control WO.

## 8. Стоимость и compute

Публичный репозиторий → GitHub-hosted `ubuntu-latest` = **free tier**, paid compute не расходуется (`paid_compute_authorized = false`). Один job без матрицы, ≈1–2 мин на запуск; concurrency отменяет устаревшие запуски. Никакой научной кампании: E0–E6 остаются `NOT_RUN`; зелёный CI — технический факт, не научный PASS.

## 9. Первый прогон и наблюдение

Workflow активируется первым событием `TR-PR`/`TR-PUSH-MAIN` после merge: открытие PR этой ветки вызовет первый live-прогон `TR-PR` (fork/in-repo поведение идентично; secrets недоступны). Reviewer/Verifier рекомендовано проверить первый лог прогона как evidence: совпадение `subject_sha`, отсутствие warnings в check-consistency, корректный skip/валидация Check 3.

## 10. Следующий шаг

`INFRA1-002 «Add PR validation gates»`: механические negative controls `NC-1`..`NC-7` (workflow lint: `runs-on` labels, permissions, запрещённые триггеры, workflow-graph), corrections-политика для `work_cli`, concurrency/quota-гейты, верификация repo settings (§6), включение task-bus pytest после влития ветки.
