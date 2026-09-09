# INFRA — Compute Trust and Execution Baseline R1

**Revision:** `EXECUTION-BASELINE-R1`
**Work Order:** `INFRA0-001` (`docs/work/WO-INFRA0-001.md`)
**Execution:** `EX-INFRA0-001-R1` (branch `infra/infra0-execution-baseline-r1`)
**Base SHA:** `57c1e63733ea3b10f991c0f9609c426dc75b17a5` (exact canonical `main`)
**Machine-readable counterpart:** [`config/infra/execution-baseline.v1.json`](../../config/infra/execution-baseline.v1.json)
**Статус:** `PROPOSED` — документ предложен Implementer'ом и **не принят**: acceptance `INFRA0` — Director gate, обновление `project/infra-state.json` Implementer'ом запрещено.

---

## 0. Назначение и границы документа

Этот документ фиксирует исполняемый security/control baseline вычислительной инфраструктуры NanoLab **до** создания любых GitHub workflows и self-hosted runners. Он определяет:

- доверенные trigger-маршруты (trusted trigger routes) и запреты маршрутизации;
- классы runner'ов и зарезервированные labels;
- permissions `GITHUB_TOKEN` и политику secrets;
- execution budgets / resource classes;
- artifact policy;
- negative controls (инварианты, нарушение которых обязано быть технически невозможным);
- контракт маршрутизации «публичный PR vs доверенный self-hosted».

Чего документ **не** делает — см. §10 «Явные запреты этапа». Это документационный Work Order: ни один runner, workflow, secret или artifact store в его рамках не создаётся.

Приоритет источников при конфликте: канонический `main` (`AGENTS.md` hard rules, `docs/infra/SECURITY_MODEL.md`) → настоящий baseline R1 → machine-readable конфиг. Изменение baseline возможно только новой ревизией (`EXECUTION-BASELINE-R2+`) в отдельном bounded Work Order.

## 1. Источники

| Источник | Что взято |
|---|---|
| `AGENTS.md` hard rules | `PUBLIC PR CODE MUST NOT AUTOMATICALLY RUN ON TRUSTED SELF-HOSTED SCIENTIFIC NODES`; `INFRASTRUCTURE PROVIDES CAPABILITY; IT DOES NOT DECLARE SCIENTIFIC TRUTH` |
| `docs/infra/SECURITY_MODEL.md` | trust zones, hard rules 1–10, allowed trigger model, isolation target |
| `docs/infra/EXECUTION_BACKENDS.md` | классы backend'ов H0/C0/G0/H1, executor contract |
| `docs/infra/ROADMAP.md` | границы INFRA0 vs INFRA1–INFRA7 |
| `project/infra-plan.json` / `project/infra-state.json` | зависимости задач, `capabilities = false`, `paid_compute_authorized` (scientific state) |
| `config/control/harness/*.v1.json` | risk/review policy, artifact reuse fields, human gates |

## 2. Trust zones и границы доверия

```text
UNTRUSTED
  код public fork / external PR, артефакты чужих сборок
       ↓ исполняется ТОЛЬКО на
  GitHub-hosted ephemeral runner (H0)

TRUSTED CONTROL
  canonical main + explicit protected dispatch
       ↓ (и только так)
  self-hosted NanoLab runner (C0/G0, пока не зарегистрированы)

SCIENTIFIC ARTIFACTS
  raw trajectories / checkpoints / models
       ↓
  отдельное storage с digest/provenance (INFRA4, сейчас отсутствует)
```

Инвариант границы: **решение о переходе в доверенную зону принимает происхождение кода (canonical main + explicit protected dispatch), а не авторство, членство или содержимое PR.** Любой механизм, позволяющий внешнему коду влиять на выбор исполнителя, является нарушением baseline.

## 3. Runner classes и labels

| Класс | Тип | Labels | Статус в R1 | Активация |
|---|---|---|---|---|
| `H0` | GitHub-hosted ephemeral | `ubuntu-latest`, `ubuntu-24.04` | доступен платформенно; workflows появятся в INFRA1 | `INFRA1-001` |
| `C0` | self-hosted CPU | `nanolab-cpu` (reserved) | **НЕ зарегистрирован**; label запрещён в `runs-on` любых workflow | `INFRA2-001` |
| `G0` | self-hosted GPU | `nanolab-gpu` (reserved) | **НЕ зарегистрирован** | `INFRA5-001` |
| `H1` | HPC / remote scheduler | `nanolab-hpc-*` (reserved namespace) | **НЕ зарегистрирован** | `INFRA7-001` |

Правила labels:

1. Зарезервированные self-hosted labels (`nanolab-cpu`, `nanolab-gpu`, `nanolab-hpc-*`) допустимы в `runs-on` **только** у workflows, исполняющих route `TR-DISPATCH` (§4) с обязательными guards.
2. Self-hosted runner регистрируется с **только** этими labels; запрещено вешать на него стандартные hosted labels (`self-hosted`, `ubuntu-latest` и т.п.), чтобы случайный `runs-on: ubuntu-latest` не попал на доверенную машину.
3. `C0` работает non-root, без интерактивных пользовательских секретов, в disposable workspace/container (isolation target из `SECURITY_MODEL.md`; детальная конфигурация — `INFRA2-001`, не здесь).

## 4. Trusted trigger routes

| ID | Триггер | Источник кода | Разрешённые классы | Guards | Статус |
|---|---|---|---|---|---|
| `TR-PR` | `pull_request` (fork и in-repo) | любой публичный PR | `H0` только | `permissions: contents: read`; без secrets; без cache-инъекций в trusted-зону | контракт действует; механические gate — `INFRA1-002` |
| `TR-PUSH-MAIN` | `push` в `main` | canonical main | `H0` только | минимальные permissions; тайм-ауты | контракт действует; механика — `INFRA1-001/002` |
| `TR-DISPATCH` | `workflow_dispatch` из workflow в canonical `main` | canonical main | `H0` или защищённый `C0`/`G0` | protected environment с required reviewers; exact `subject_sha` + `work_order_id` + resource budget в payload; без них — fail closed | **RESERVED_NOT_ACTIVE** (нет workflows/runner'ов) |
| `TR-SCHEDULE` | `schedule` | canonical main | `H0` только | фиксированный budget | отложено; при введении — отдельная ревизия baseline |
| `TR-TAG` | `push` tag / release | canonical main | `H0` только | publishing flow — отдельно | отложено |
| `TR-PRT` | `pull_request_target` | — | — | — | **FORBIDDEN_R1**: известный вектор утечки secrets/выполнения чужого кода с повышенными правами; снятие запрета — только explicit новый WO с pinned-controls паттерном |
| `TR-WFRUN` | `workflow_run` как мост untrusted→trusted | — | — | — | **FORBIDDEN_R1**: запрещено передавать код/артефакты из untrusted run в trusted route через цепочку workflows |

### 4.1 Контракт маршрутизации: публичный PR vs доверенный self-hosted

| Происхождение кода | Маршрут | Исполнитель |
|---|---|---|
| PR из fork | `TR-PR` | только `H0` |
| PR из ветки этого же репозитория | `TR-PR` | только `H0` (никакой привилегии по авторству) |
| push в `main` | `TR-PUSH-MAIN` | `H0` |
| explicit dispatch c exact subject + budget + approval | `TR-DISPATCH` | разрешён защищённый self-hosted (`C0`, позднее `G0`) |
| всё остальное | — | self-hosted scientific compute **запрещён** |

Self-hosted scientific node никогда не является default PR executor. Автоматический запуск self-hosted на каждый public PR запрещён (hard rule `AGENTS.md` + `SECURITY_MODEL.md` правило 2).

## 5. GitHub permissions и secrets

1. Дефолтные permissions `GITHUB_TOKEN` в репозитории целевое состояние — **read-only** (фиксируется настройкой репозитория при `INFRA1-001`); каждый workflow дополнительно объявляет минимальный явный блок `permissions:`.
2. Route `TR-PR`: `contents: read`, больше ничего; write-правила (`contents: write`, `pull-requests: write` и т.д.) в PR route запрещены.
3. Secrets недоступны route `TR-PR` (стандартное поведение GitHub для fork PR — инвариант, который запрещено обходить через `pull_request_target`, см. `NC-7`).
4. Долгоживущие credentials не передаются simulation/compute процессам (`SECURITY_MODEL.md` правило 6); trusted compute job по возможности получает read-only доступ к repository contents.
5. Добавление repository secrets в этом Work Order запрещено (scope WO). Будущие secrets — минимальные, по одному назначению, с отдельной политикой ротации (поздняя ревизия baseline).

## 6. Execution budgets и resource classes

| Класс | Назначение | Ограничения R1 | Статус |
|---|---|---|---|
| `RC0_HOSTED_VALIDATION` | harness/schema/unit checks, лёгкий CPU smoke | hosted `H0`; wall-clock ≤ 15 мин; артефакты отладочные | контракт; активация `INFRA1-001` |
| `RC1_HOSTED_EXTENDED` | расширенная hosted-валидация | hosted `H0`; wall-clock ≤ 60 мин; объявляется явно в workflow | контракт; активация `INFRA1-*` |
| `RC2_TRUSTED_CPU` | доверенный CPU scientific job | self-hosted `C0`; budget (wall-clock/RAM/disk/CPU) обязателен в dispatch payload; численные значения фиксируются `INFRA2/INFRA3` по измерениям, не догадкой | RESERVED_NOT_ACTIVE |
| `RC3_TRUSTED_GPU` | GPU job | `G0` + fingerprint из `EXECUTION_BACKENDS.md` | forbidden до `INFRA5` |

Правила бюджетов:

1. Unbounded jobs запрещены: каждый route обязан иметь wall-clock timeout и stop conditions (executor contract в `EXECUTION_BACKENDS.md`).
2. Каждый trusted job несёт `job_id`, `work_order_id`, `subject_sha`, budget, command, expected outputs (executor contract); dispatch без этих полей отклоняется (`NC-3`).
3. Retry/re-run не увеличивает бюджет; увеличение бюджета = новый dispatch/human gate (`NC-6`).
4. Paid/cloud compute запрещён: `paid_compute_authorized = false` в `project/state.json`; budget expansion — human gate (`harness-policy.v1.json`).
5. Параллелизм scientific runtime ограничен `scheduler-policy.v1.json` (`parallel_scientific_runtime_limit = 1`);trusted compute не обходит scheduler policy.

## 7. Artifact policy

1. Обязательные поля provenance любого переиспользуемого артефакта (совпадают с `review-policy.v1.json`): `sha256`, `size_bytes`, `producer_run_id`, `subject_sha`, `storage_location`.
2. Артефакты hosted CI (`upload-artifact` и аналоги) — эphemeral debug-материал; **они не являются scientific evidence** и не единственное хранилище научных данных.
3. Raw trajectories/chekpoints могут жить вне Git, но manifest с SHA-256, размером и location обязан быть в Git (`AGENTS.md`).
4. Переиспользование raw артефакта требует digest + provenance; повтор job обязан проверять существующий run/manifest до нового вычисления (`SECURITY_MODEL.md` правила 7–8).
5. В логах и артефактах запрещены секреты и credentials; логи могут публиковаться как evidence.
6. Durable artifact store не разворачивается в этом Work Order — это `INFRA4-001/002`. Настоящий раздел фиксирует только контракт, которому будущий store обязан соответствовать.

## 8. Negative controls

Инварианты, которые обязаны быть технически необходи­мыми к нарушению. В R1 они зафиксированы документально; механические проверки (lint/CI-негативные тесты) — required output `INFRA1-002` (negative test из WO: «untrusted PR route не может выбрать self-hosted scientific label»).

| ID | Угроза | Инвариант | Статус R1 | Механическая проверка |
|---|---|---|---|---|
| `NC-1` | Внешний PR выполняется на личной машине | ни один workflow в route `TR-PR`/`TR-PUSH-MAIN` не содержит self-hosted labels в `runs-on` | DOCUMENTED | `INFRA1-002` lint + negative test |
| `NC-2` | Обход границы через цепочку workflows | untrusted код/артефакты не переносятся в trusted route (`pull_request_target`, `workflow_run` мосты запрещены) | DOCUMENTED | `INFRA1-002` workflow-graph lint |
| `NC-3` | Доверенный запуск без подотчётности | `TR-DISPATCH` без `subject_sha` + `work_order_id` + budget — отклоняется (fail closed) | DOCUMENTED | валидатор dispatch payload (`INFRA2-002`) |
| `NC-4` | Эскалация прав из PR route | токен PR route не может писать (contents/events/releases) | DOCUMENTED | permissions lint (`INFRA1-002`) |
| `NC-5` | Тихий fail-open на другой исполнитель | недоступность `H0` не переключает проверки на self-hosted; отказ = отказ (fail closed) | DOCUMENTED | review конфигурации при `INFRA1/2` |
| `NC-6` | Расход бюджета через retries | re-run наследует бюджет; увеличение = новый dispatch/gate | DOCUMENTED | scheduler/queue policy (`INFRA6`) |
| `NC-7` | Утечка secrets во внешний PR | secrets недоступны fork-PR; обход через `pull_request_target` запрещён как триггер | DOCUMENTED | `NC-2` lint + review |

Ни один workflow сейчас в репозитории не активен — поверхность атаки отсутствует по построению; это осознанный fail-safe порядок INFRA0.

## 9. Threat validation matrix

| Actor | Vector | Asset под угрозой | Control | Residual risk |
|---|---|---|---|---|
| Автор внешнего fork PR | вредоносный код в PR | доверенный хост runner, secrets | `TR-PR` → только `H0`; `NC-1`, `NC-7` | низкий (ephemeral VM) |
| Компрометированный third-party GitHub Action | злое действие в цепочке | runner, токен | минимальный `permissions:`, pinned actions (обязателен с `INFRA1-001`), review зависимостей | средний → снижается pinning |
| Утёкший токен с write-правами | изменение workflows/routes | граница trusted route | read-only дефолт, protected branches/environments, human gates | средний |
| Спам/resource-атака через PR | массовые запуски CI | бюджет, очередь | `RC0` лимиты, hosted-only, позже — concurrency limits (`INFRA1-002`) | низкий/средний |
| AI-агент внутри проекта | бесконтрольный расход compute, обход маршрутов | бюджет, доверенные узлы | Work Order scope, budget gates, `NC-3`, `NC-6`; автономность ограничена `HARNESS_AUTONOMOUS_EXECUTION_RU.md` | низкий/средний |
| Компрометация self-hosted runner | pivot на хост/сеть владельца | хост, персональные данные | non-root, disposable workspace, без user secrets, отдельные labels (§3.3) — детализация `INFRA2-001` | принимается после INFRA2 hardening |
| Insider/owner error | случайный self-hosted label в PR workflow | граница доверия | `NC-1` lint, review, `TR-PRT`/`TR-WFRUN` запрет | низкий |

## 10. Явные запреты этапа (что НЕ делается в INFRA0-001)

1. Не устанавливается и не регистрируется ни один self-hosted runner (на личном сервере или где-либо ещё) — `INFRA2-001`.
2. Не добавляются и не активируются файлы `.github/workflows/*` — минимальный hosted CI и validation gates — `INFRA1-001/002`.
3. Не добавляются repository secrets и не создаются credentials/tokens.
4. Не включается автоматический self-hosted execution для public PR — запрещено в принципе (не только в этом этапе).
5. Не разворачивается artifact store / cache service — `INFRA4`.
6. Не подключается GPU — `INFRA5`; не разворачиваются scheduler/queue/AiiDA — `INFRA6`; не подключаются HPC/внешние провайдеры — `INFRA7`.
7. Не запускается платный/облачный compute; не расширяются бюджеты (human gate).
8. Не запускаются физические wet-lab/hardware эксперименты (`CRITICAL`, отдельный human/domain gate).
9. Не запускается никакая scientific campaign (E0–E6 остаются `NOT_RUN`); baseline не создаёт и не повышает scientific claim.
10. Implementer не изменяет `project/infra-state.json` и `project/state.json`: перевод `INFRA0-001` из `READY` в `IMPLEMENTED/ACCEPTED` и флип `capabilities.*` — Director gate через принятый merge в `main`.
11. Implementer не выставляет `ACCEPTED` и не self-accept: независимый Reviewer/Verifier проверяют baseline до перехода к `INFRA1` (acceptance WO).

## 11. Соответствие hard rules

| Hard rule (`AGENTS.md`) | Как обеспечивается |
|---|---|
| `PUBLIC PR CODE MUST NOT AUTOMATICALLY RUN ON TRUSTED SELF-HOSTED SCIENTIFIC NODES` | §4.1: `TR-PR` → `H0` только; self-hosted только через `TR-DISPATCH`; `NC-1`, `NC-2` |
| `INFRASTRUCTURE PROVIDES CAPABILITY; IT DOES NOT DECLARE SCIENTIFIC TRUTH` | §10.9–10.10; зелёный job ≠ научный PASS |
| `RAW ARTIFACT REUSE REQUIRES DIGEST + PROVENANCE` | §7.1, §7.4 |
| `NEGATIVE / FAILED / INCONCLUSIVE RESULTS MUST BE PRESERVED` | §8 negative controls; validation events сохраняют фактические результаты проверок |
| `IMPLEMENTER CANNOT SELF-ACCEPT` | статус `PROPOSED`; acceptance — Director gate |
| budget/human gates | §6.4; `harness-policy.v1.json` |

## 12. Machine-readable baseline

`config/infra/execution-baseline.v1.json` — нормативная машина-читаемая проекция этого документа (тот же revision `EXECUTION-BASELINE-R1`). Он является входом для механических проверок `INFRA1-002` (lint `runs-on`, permissions, запрет `pull_request_target`/`workflow_run`-мостов) и для валидатора trusted dispatch `INFRA2-002`. Файл следует стилю control-политик `config/control/harness/*.v1.json` (`schema_version`, `revision`, идентификаторы английские); отдельная JSON Schema для него в R1 не вводится — его валидность проверяется `python -m json.tool` и review. При расхождении текста документа и JSON приоритет у этого документа до принятия следующей ревизии.

## 13. Следующие шаги

1. Независимый Reviewer, затем Verifier (MEDIUM routing по `risk-policy.v1.json`) проверяют baseline по exact HEAD этой ветки.
2. Director checkpoint proposal + human merge gate в `main`; только после принятия — обновление `project/infra-state.json` владельцем/директором.
3. `INFRA1-001 «Add hosted harness CI»` — первый hosted workflow по контрактам §4–§6 (TR-PR/TR-PUSH-MAIN на `H0`, минимальные permissions, pinned actions).
4. `INFRA1-002 «Add PR validation gates»` — механические negative controls `NC-1`…`NC-7` (включая negative test из WO: untrusted PR route не может выбрать self-hosted scientific label).
