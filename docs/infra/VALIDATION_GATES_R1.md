# INFRA — PR Validation Gates (VALIDATION_GATES_R1)

**Revision:** `VALIDATION-GATES-R1`
**Work Order:** `INFRA1-002` («Add PR validation gates», `project/infra-plan.json`; файл `docs/work/WO-INFRA1-002.md` в `main` отсутствует — авторство WO Director authority, scope ведётся по миссии Implementer'а + `project/infra-plan.json` + `EXECUTION-BASELINE-R1` §13.4, прецедент NOTE-2 `HOSTED_CI_R1.md`)
**Execution:** `EX-INFRA1-002-R1` (branch `infra/infra1-validation-gates-r1`)
**Base SHA:** `15a2c9b1b5c095e24e2e1c24afd77feef5361102` (exact; см. §8.1 о drift снимка миссии)
**Authority:** [`EXECUTION_BASELINE_R1.md`](EXECUTION_BASELINE_R1.md) (`EXECUTION-BASELINE-R1`, ACCEPTED)
**Machine-readable counterpart:** [`config/infra/validation-gates.v1.json`](../../config/infra/validation-gates.v1.json) (эталон линта) + поправки к [`config/infra/hosted-ci.v1.json`](../../config/infra/hosted-ci.v1.json) (см. §4.3)
**Статус:** `PROPOSED` — Implementer не выставляет ACCEPTED; приёмка — независимый Reviewer/Verifier и Director gate.

---

## 1. Назначение и границы

Закрыть два **блокирующих критерия приёмки INFRA1-002** из [`docs/infra/evidence/INFRA1-001/DIRECTOR_ACCEPTANCE_R1.md`](evidence/INFRA1-001/DIRECTOR_ACCEPTANCE_R1.md) и поставить механические negative controls `EXECUTION-BASELINE-R1` §8 на конвейер:

1. **Corrections-aware `work_cli`** (MINOR-2 вердикта, «первый пункт WO»): валидатор work-events принимает пост-терминальные review-corrections события после handoff, если они семантически валидны, не ломая terminal-last для обычного потока. Снимает постоянную красноту Check 3 (exit 3) на каталогах `EX-INFRA0-001-R1`, `EX-NL1-001-R1`, `EX-NL1-002-R1`.
2. **Механический NC-1-тест** (MINOR-1, наследовано из INFRA0-001): untrusted PR route не может выбрать self-hosted label — линт workflow-инвариантов с блокирующим статусом + негативный тест (`runs-on: nanolab-cpu` → MUST FAIL).

Вне границы WO: self-hosted runners, secrets, branch protection / repo settings (owner actions, `HOSTED_CI_R1.md` §6), scheduler/quota (INFRA6), dispatch-валидатор NC-3 (INFRA2-002), изменения `project/infra-state.json` и `project/state.json` (Director gate), любые правки существующих execution-каталогов (events immutable) и science-файлов.

## 2. Corrections-aware `work_cli` (`scripts/harness/work_cli.py`)

### 2.1 Правило

Пусть `t` — позиция единственного terminal/handoff события (`HANDOFF_COMPLETED`/`WORK_ORDER_BLOCKED`/`WORK_ORDER_CANCELLED`; ограничение «≤1 terminal» сохранено). Тогда:

| Правило | Содержание |
|---|---|
| **Класс corrections-событий** | явный класс `CORRECTIONS_EVENTS = {CONTINUATION_CHECKPOINT, REVIEW_CORRECTIONS}`. `REVIEW_CORRECTIONS` — новый выделенный marker-тип (формализация идиомы «corrections — новым event» из AGENTS.md); `CONTINUATION_CHECKPOINT` остаётся в классе как легаси-написание, уже опубликованное в canonical main |
| **Пост-терминальное разрешение** | события после `t` валидны **только** если принадлежат классу corrections; любое пост-терминальное событие вне класса — hard error `events after terminal/handoff must be review-corrections events (…)` — маркер пропустить нельзя (негативный тест обязателен, §5) |
| **Размещение marker-типа** | `REVIEW_CORRECTIONS` допустим только после terminal; до handoff — error (`REVIEW_CORRECTIONS is allowed only after the terminal/handoff event`) |
| **Роль автора marker-типа** (repair R1, MINOR-3) | `REVIEW_CORRECTIONS` authored только `REVIEWER`/`VERIFIER`/`DIRECTOR`; от `IMPLEMENTER` — hard error (implementer не self-issue review corrections) |
| **Семантическая валидность** | все обычные полевые проверки применяются к corrections-событиям в полном объёме (execution_id/work_order_id совпадают с паспортом, actor_role, уникальные лексически упорядоченные event_id, subject_sha — валидный git SHA). Дополнительно: `timestamp_utc` обязан присутствовать и парситься (ISO-8601); timestamps внутри corrections-хвоста неубывающие; **corrections timestamp ≥ terminal timestamp** (repair R1, MINOR-3; исключение — 4 пре-существующих события, см. §2.2) |
| **Обычный поток не ослаблен** | для исполнений без пост-терминальных corrections поведение идентично прежнему: terminal-last обязателен; событие после handoff без marker-класса — FAIL |

Сравнение «corrections timestamp ≥ terminal timestamp» введено repair R1 (MINOR-3) для всех **новых** corrections-событий. До repair R1 сравнение не проводилось (легаси-кейс `EX-NL1-002-R1` 0005: 11:16:30Z предшествует handoff-записи 0004 11:30:00Z — handoff-событие писалось позже фактического коммита evidence). Четыре пре-существующих пост-терминальных corrections события canonical main внесены в `LEGACY_TIMESTAMP_EXEMPT_CORRECTIONS`; фактическое исключение требовалось только для `EX-NL1-002-R1`/0005, остальные три уже ему удовлетворяют и внесены для полноты. Монотонность хвоста действует без исключений.

### 2.2 subject_sha: строго 40-hex; tolerance — только для exact legacy-событий (repair R1, MINOR-2)

`work-event.schema.v1.json` требует `^[0-9a-f]{40}$`, но в immutable-событиях canonical main (`EX-NL1-002-R1` 0002–0005) опубликованы сокращённые SHA (`9cc83e8`). Старые события редактировать запрещено. Первоначальная поставка применяла tolerance `7..40` hex ко **всем** событиям — REVIEWER (MINOR-2) отклонил: tolerance должен быть легаси-ограничен. Решение после ремонта: **строго 40-hex для всех событий**; abbreviated 7–39 hex принимается **только** для exact-пары `(execution_id, event_id)`, внесённой в `LEGACY_ABBREVIATED_SHA_EVENTS` (4 события `EX-NL1-002-R1`; harvest проверен сканом `docs/work/executions/EX-*/events/*.json` на canonical `a4533ab`, 2026-09-09 — других сокращённых SHA в canonical main нет). Переиспользование легаси-значения или event_id в другом исполнении tolerated не является (покрыто тестами). Passport `base_sha` — только 40-hex. Схема осталась 40-hex — floor/ceiling расхождение для 4 легаси-событий задокументировано (sync — control WO, §2.4).

### 2.3 Результат на canonical-каталогах

| Каталог | До | После |
|---|---|---|
| `EX-INFRA0-001-R1` | FAIL: `terminal/handoff event must be last` | **OK** (`has_post_terminal_corrections=true`) |
| `EX-NL1-001-R1` | FAIL: `terminal/handoff event must be last` | **OK** (`true`) |
| `EX-NL1-002-R1` | FAIL: **5 residual ошибок** (4× `invalid subject_sha` в 0002–0005 + terminal-last; 0006 — пост-терминальный CONTINUATION_CHECKPOINT) | **OK** (0 ошибок, `true`) |
| остальные 7 EX-* | OK | OK (без изменений) |

Вывод `inspect_execution` дополнен полем `has_post_terminal_corrections` (additive, схема вывода `nanolab.control_work_output.v1` не менялась).

### 2.4 Синхронизация схем — сознательно отложена

`work-event.schema.v1.json` (enum без `REVIEW_CORRECTIONS`, pattern 40-hex) и `execution-passport.schema.v1.json` (паттерн `^NL[0-8]$` против `checkpoint: INFRA1` — NOTE-1) не правились: control-схемы — отдельная authority (прецедент NOTE-1 Director-вердикта INFRA1-001: «расширение схемы — кандидат в отдельный control WO»). Ни один механизм сейчас не валидирует events против JSON-схемы механически; расхождение зафиксировано здесь и в конфиге (`non_goals`).

## 3. Механический NC-линт (`scripts/harness/workflow_lint.py`)

Структурный линт всех `.github/workflows/*.y*ml`; эталон значений — `config/infra/validation-gates.v1.json` (`workflow_lint`-блок), сам скрипт значений не дублирует. Stdlib-only, без сети; YAML читается минимальным парсером workflow-подмножества (block/flow коллекции, quoted scalars, block scalars `|`/`>` для `run:`-скриптов, комментарии, `${{ }}` как opaque-текст). **Fail closed** (формулировка усилена по REVIEWER-вердикту §4.5): всё, что парсер не понимает, ИЛИ что резолвится GitHub иначе, чем видит линт, — блокирующее нарушение, а не пропуск. Конкретно: непарсируемый файл → `WORKFLOW_UNPARSEABLE`; YAML anchors/aliases/merge keys (`&`/`*`/`<<`) → fail-closed на уровне парсера (MAJOR-2: GitHub резолвит alias, линт обязан молчать только вместе с файлом); multi-document файлы → отклоняются (NOTE-3); `on:` отсутствует или не-mapping (`on: push`, `on: [push, pull_request_target]`) → блокирующее нарушение (MAJOR-1: scalar/flow-форма не линтабельна и не может обходить NC-2).

| Rule ID | NC | Суть | Блокирующий |
|---|---|---|---|
| `NC1_SELF_HOSTED_LABEL` | NC-1 | `runs-on` содержит `self-hosted`, `nanolab-cpu`, `nanolab-gpu` или префикс `nanolab-hpc-*` | да (**blocking criterion**) |
| `NC1_DYNAMIC_RUNS_ON` | NC-1 | `${{ }}`-выражение в `runs-on` (динамический выбор исполнителя) | да |
| `NC1_RUNS_ON_MISSING` | NC-1 | job со `steps` без явного `runs-on` | да |
| `NC2_FORBIDDEN_TRIGGER` | NC-2/NC-7 | триггеры `pull_request_target`, `workflow_run` (FORBIDDEN_R1, baseline §4) | да |
| `NC2_TRIGGER_NEEDS_BASELINE_REVISION` | NC-2 | зарезервированные триггеры `schedule`, `workflow_dispatch`, `release` до новой ревизии baseline | да |
| `NC2_TRIGGERS_UNSUPPORTED_FORM` | NC-2/NC-7 (repair R1, MAJOR-1) | `on:` в scalar/flow-форме — триггеры не линтабельны, fail closed | да |
| `NC2_TRIGGERS_BLOCK_MISSING` | fail-closed (repair R1, MAJOR-1) | `on:` отсутствует / null — trigger surface обязан быть явным | да |
| `NC2_EXTERNAL_REUSABLE_WORKFLOW` | NC-2 | job-level `uses:` вне `./` (внешний reusable workflow как обход линта) | да |
| `NC4_PERMISSIONS_BLOCK_MISSING` | NC-4 | нет явного workflow-level `permissions:` | да |
| `NC4_WRITE_PERMISSION` | NC-4 | уровень `write` в любом `permissions:` (workflow/job) | да |
| `NC7_SECRETS_REFERENCE` | NC-7 | ссылка `secrets.X` **или `secrets['X']`/`secrets["X"]`** (repair R1, MINOR-1) в любом скаляре workflow | да |
| `BUDGET_TIMEOUT_REQUIRED` / `BUDGET_TIMEOUT_BOUNDS` | NC-6 | каждый job обязан иметь целочисленный `timeout-minutes` в [1, 60] (unbounded jobs запрещены, §6 baseline) | да |
| `PIN_ACTION_FULL_SHA` | supply-chain (§9) | внешние actions пинятся full 40-hex commit SHA; `docker://` — digest | да |
| `NOTE3_PR_TYPES_READY_FOR_REVIEW` | NOTE-3 | при наличии `pull_request`-триггера: `types` явно содержит `ready_for_review` (scope уточнён repair R1 по NOTE-1: push-only workflow правило не задевает) | да |
| `WORKFLOW_UNPARSEABLE` | NC-1/NC-2 | файл не разобран парсером, включая anchors/aliases/merge keys и multi-document (repair R1) | да |

Принятые не-линтабельные ограничения (документировано): индирекция секретов через `env:` не обнаруживается статически (MINOR-1, принято); NC-5 — review-пункт; NC-3 — INFRA2-002; полный NC-6 — INFRA6.

## 4. Изменения `hosted-ci.yml` (TR-PR / TR-PUSH-MAIN поверхность не менялась)

### 4.1 Триггеры

`pull_request.types` = `[opened, synchronize, reopened, ready_for_review]` — **NOTE-3 закрыт** (эталон линта синхронизирован с фактом).

### 4.2 Чеки (3 → 5, все блокирующие, stdlib-only, суммарно ≈1–2 мин, RC0)

1. JSON-syntax всех tracked `*.json` (без изменений);
2. `harness.cli check-consistency` (без изменений);
3. `harness.work_cli validate` — **scope расширен** с diff-scoped до **всех** `docs/work/executions/EX-*`: corrections-aware валидатор убрал причину diff-scope (false-red на легаси-corrections), сплошная валидация снова зелёная и fail-closed;
4. **новый** `harness.workflow_lint` — механические NC-1..NC-7, blocking (NC-1 — блокирующий критерий приёмки);
5. **новый** `python3 -m unittest discover -s tests -t .` — тесты самих гейт-механизмов (§5).

Checkout сохраняет `persist-credentials: false`, `fetch-depth: 0`; forbidden-маршруты и H0-only `runs-on` не менялись.

### 4.3 Отношение к `config/infra/hosted-ci.v1.json` (ACCEPTED, R1)

Файл R1 **не редактировался** («изменение содержимого — только новой ревизией»): он остаётся исторической проекцией INFRA1-001. Дельты (types, чеки 4–5, scope Check 3) зафиксированы как machine-readable поправки в `config/infra/validation-gates.v1.json` → `amends_hosted_ci_r1`. Приоритет: hard rules → baseline doc → `hosted-ci.v1.json` → `validation-gates.v1.json`.

## 5. Тесты (`tests/`, stdlib `unittest`, 59 шт. после repair R1, `python3 -m unittest discover -s tests -t .`)

`tests/test_work_cli_corrections.py` (24):

- кейс **EX-NL1-002-R1** — 5 residual ошибок → `ok=true`, `has_post_terminal_corrections=true` (плюс EX-INFRA0-001-R1, EX-NL1-001-R1 → OK); тесты автоматически skip на неполном checkout;
- **негатив (обязательный)**: событие после corrections-терминала **без marker** (пост-терминальное `VALIDATION_RECORDED` / `IMPLEMENTATION_COMMITTED` после corrections) → FAIL с `review-corrections`-ошибкой; `REVIEW_CORRECTIONS` до handoff → FAIL; второй terminal после corrections → FAIL;
- семантическая валидность corrections: невалидный `subject_sha` → FAIL; непарсимый `timestamp_utc` → FAIL; убывающие timestamps в хвосте → FAIL;
- repair R1 (MINOR-2): произвольный 7-hex → FAIL; 8–39-hex → FAIL; легаси-пара `(EX-NL1-002-R1, 0005-resource-evidence-committed)` с `9cc83e8` → OK; легаси-значение в другом исполнении → FAIL; легаси-event_id в другом исполнении → FAIL;
- repair R1 (MINOR-3): corrections ts < terminal ts → FAIL (≥ terminal — OK); легаси-exempt событие с ранним ts → OK; новое событие в легаси-каталоге с ранним ts → FAIL; `REVIEW_CORRECTIONS` от `IMPLEMENTER` → FAIL, от `VERIFIER` → OK;
- обычный поток: terminal-last OK; событие после terminal без corrections → FAIL.

`tests/test_infra_workflow_lint.py` (35):

- **негатив (обязательный NC-1)**: fixture с `runs-on: nanolab-cpu` → MUST FAIL (`NC1_SELF_HOSTED_LABEL`); плюс `self-hosted`, префикс `nanolab-hpc-*`, динамическое `${{ }}`-выражение, отсутствующий `runs-on`;
- repair R1 (MAJOR-1): `on: [push, pull_request_target]` → FAIL (`NC2_TRIGGERS_UNSUPPORTED_FORM`); `on: push` → FAIL; отсутствующий `on:` → FAIL (`NC2_TRIGGERS_BLOCK_MISSING`); `on:` null → FAIL;
- repair R1 (MAJOR-2): `runs-on: &cpu nanolab-cpu` / `runs-on: *cpu` → FAIL (`WORKFLOW_UNPARSEABLE`, anchor/alias); anchor в другом поле → FAIL; merge key `<<` → FAIL; `&&` внутри `run: |` НЕ является anchor (позитив);
- NC-2: `pull_request_target`, `workflow_run`, `schedule`, внешний reusable workflow → FAIL;
- NC-4/NC-6/NC-7: отсутствие `permissions:`, `contents: write`, ссылка `secrets.*`, нет таймаута, таймаут 120 → FAIL;
- repair R1 (MINOR-1): `secrets['X']` и `secrets["X"]` → FAIL (`NC7_SECRETS_REFERENCE`); dot-форма по-прежнему → FAIL;
- NOTE-3: `pull_request.types` без `ready_for_review` / без `types` / bare `pull_request:` → FAIL; repair R1 (NOTE-1): push-only workflow без `pull_request` → правило не срабатывает;
- pinning: action по тегу `@v5` → FAIL;
- fail-closed: нечитаемый YAML → `WORKFLOW_UNPARSEABLE`; repair R1 (NOTE-3): multi-document файл → FAIL (второй документ больше не сливается);
- позитив: минимальный compliant workflow → 0 нарушений; **реальный** `.github/workflows/hosted-ci.yml` → 0 нарушений.

## 6. Маппинг на blocking-критерии приёмки

| Критерий (`DIRECTOR_ACCEPTANCE_R1`) | Реализация | Доказательство |
|---|---|---|
| (a) механический NC-1-тест: untrusted PR route не может выбрать self-hosted label | линт `NC1_*` blocking в Check 4/5 + негативный тест `runs-on: nanolab-cpu` MUST FAIL | §3, §5; локальный прогон §7 |
| (b) corrections-aware `work_cli` | правило §2 (класс + marker + семантика), EX-NL1-002-R1 5→0, негативные тесты | §2.3, §5 |

## 7. Локальная верификация

Все пять чеков выполнены локально (Windows/Python 3.11). После repair R1 (на HEAD ремонтного раунда — см. events 0005/0006): (1) JSON-syntax 111 tracked `*.json` — OK; (2) `check-consistency` — `ok=true`; (3) `work_cli validate` всех 10 EX-* — 10/10 OK; (4) `workflow_lint --root .` — `ok=true`, 0 violations; (5) unittest **59/59** — OK. Дополнительно выполнена **повторная негативная матрица REVIEWER'а** (`REVIEW_LOG_R1.md` §2–§3, те же probe-формы во временном каталоге, вне репозитория): 18/18 ожидаемых исходов — включая бывшие обходы `probe-alias-valid` (was exit 0 → exit 1 `WORKFLOW_UNPARSEABLE`), `probe-on-list`/`probe-on-scalar` (was exit 0 → exit 1 `NC2_TRIGGERS_UNSUPPORTED_FORM`), `probe-secrets-bracket2` (was exit 0 → exit 1 `NC7_SECRETS_REFERENCE`), multi-doc (обход устранён: отклонение вместо слияния), а также пробы MINOR-2/MINOR-3 (было OK → теперь FAIL). Базовый валидатор (`git show 15a2c9b:scripts/harness/work_cli.py`) на `EX-NL1-002-R1` — exit 3, ровно 5 residual ошибок (воспроизведено). Первоначальные значения раунда 1 — в events 0002/0003.

## 8. Находки и задокументированные отклонения

1. **Base drift снимка миссии.** Миссия именует `15a2c9b` «main»; фактически: локальный ref `main` (worktree `C:\NanoLab\main`) = `6796531` (отстаёт, не обновлялся — вне скоупа), `origin/main` после fetch = `a4533ab` = base + PR #27 (science acceptance addendum NL1-002; INFRA-поверхность не затрагивает). Ветка срезана **от exact `15a2c9b1b5c095e24e2e1c24afd77feef5361102`** по директиве миссии; merge-base с `origin/main` = base → diff PR чистый, не содержит science-коммитов. Описание «INFRA1-001 ACCEPTED, next INFRA1-002» верно на base.
2. **Сокращённые SHA в легаси-events** — repair R1 (MINOR-2): строго 40-hex для всех событий; abbreviated принимается только для exact 4 легаси-событий `EX-NL1-002-R1` (whitelist `(execution_id, event_id)`, §2.2); schema-sync — control WO (§2.4).
3. **`WO-INFRA1-002.md` отсутствует в `main`** — как в INFRA1-001 (NOTE-2), authorship Director.
4. **`checkpoint: INFRA1` против `^NL[0-8]$`** — третий INFRA-прецедент подряд (NOTE-1), валидатор паттерн не проверяет; кандидат в control WO.
5. **Парсер YAML — собственный subset-парсер** (stdlib-only требование чеков). Непонятный синтаксис = блокирующее нарушение (fail closed), а не silent-skip; repair R1 дополнил rejection: anchors/aliases/merge keys (`&`/`*`/`<<`) и multi-document файлы отклоняются явно (GitHub резолвит их иначе, чем видел бы линт); расширение подмножества — новая ревизия конфига/кода.
6. **NC-5 не линтится** — осознанно: mechanical validation по baseline — review при INFRA1/2; появление любого fallback-механизма должно добавить lint-правило до активации.

## 8.1 Стоимость и compute

Публичный репозиторий → GitHub-hosted `ubuntu-latest` = free tier, `paid_compute_authorized = false`. Пять чеков stdlib-only ≈1–2 мин — бюджет `RC0_HOSTED_VALIDATION` (≤15 мин) не превышен; concurrency и failure-only артефакты унаследованы. Научная кампания не запускалась: E0–E6 остаются `NOT_RUN`; зелёные чеки — технический факт, не научный PASS.

## 9. Следующий шаг

Независимый Reviewer → Verifier на exact substantive HEAD этой ветки (MEDIUM routing), затем Director checkpoint `INFRA1-002` и Human Gate merge. После принятия: checkpoint `INFRA1` закрывается решением Director (вместе с вопросом флипа `capabilities.hosted_ci` при наличии live-evidence прогона новых чеков); владелец — owner actions `HOSTED_CI_R1.md` §6; далее `INFRA2-001` (NC-1-линт уже защищает label-namespace).
