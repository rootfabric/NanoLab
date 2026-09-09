# INFRA1-001 — Independent Reviewer Verdict R1

Роль: независимый fresh REVIEWER (без доступа к контексту имплементёра; только код, Git-факты и документы). Дата: 2026-09-09. Work Order: `INFRA1-001` «Safe GitHub-hosted CI». Исполнение: `EX-INFRA1-001-R1`.

Предмет ревью: ветка `infra/infra1-hosted-ci-r1`, substantive HEAD `0ab044b87e3e296942da3307f1b1c5ed0c34f5f1` (tree `a10573f73a4e409d68b9b82b5fd15efbcbede3ff`; handoff-вершина `ff8d86a` добавляет только events 0002–0004, `summary.md` и статусы паспорта; base `7f17e9a` = canonical `main`). Цепочка коммитов: `a689711` (START: только passport + event 0001 + branch-passport) → `ed2d596` (workflow) → `0ab044b` (docs/config) → `5a73707` (events 0002/0003) → `ff8d86a` (event 0004 + summary + статусы).

Review выполнялся на ветке `review/infra1-hosted-ci-r1` от exact `0ab044b` в worktree `C:\NanoLab\review-infra-1-001`. Вердикт размещён в `docs/infra/evidence/INFRA1-001/` — по прецеденту INFRA0-001 (track-локальный evidence-root INFRA).

## Verdict

**PASS**

Первый исполняемый workflow репозитория соответствует контрактам `EXECUTION-BASELINE-R1` §4–§7 и не ослабляет границу доверия: обслуживаются только `TR-PR` (`pull_request` → `main`) и `TR-PUSH-MAIN` (`push` → `main`); запрещённые `TR-PRT` (`pull_request_target`) и `TR-WFRUN` (`workflow_run`), а также `schedule`/tag/release физически отсутствуют; `runs-on` — исключительно `ubuntu-latest` (класс `H0`), ни одного self-hosted/reserved label (`NC-1`); явный workflow-level `permissions: contents: read` без write-объявлений (`NC-4`); секреты не используются ни одним шагом (`NC-7`); `timeout-minutes: 15` = бюджет `RC0_HOSTED_VALIDATION` + concurrency `cancel-in-progress` (`NC-6`); fallback на другой исполнитель отсутствует (`NC-5`, fail closed); оба actions запинены по full commit SHA с подтверждённым `git ls-remote` соответствием lightweight-тегов (`NC`-контекст §9 baseline); `persist-credentials: false`; артефакты — только при падении, с manifest'ом всех пяти provenance-полей §7.1. Scope соблюдён (6 файлов — все в allowed_paths; state-файлы байт-неизменны; секретов в diff нет). Все три CI-чека воспроизведены ревьюером локально с теми же результатами. События `0001–0004` схемно-валидны 4/4; паспорт валиден во всех полях, кроме заранее задокументированного отклонения `checkpoint` (см. NOTE-1). Оба machine-readable отклонения (`known_discrepancies` в `hosted-ci.v1.json`) независимо подтверждены и корректно оформлены. Findings MINOR-1..2 / NOTE-1..4 (ниже) границу доверия не ослабляют и PASS не блокируют.

Примечание по словарю: `review-policy.v1.json` допускает `PASS | FAIL | INSUFFICIENT_EVIDENCE`; миссия ревью дополнительно определяет `FIX_REQUIRED`. Вердикт `PASS`; если Director сочтёт MINOR-findings блокирующими — маршрут `FIX_REQUIRED` с Repair Map (повтор того же действия запрещён).

## 1. Scope-границы — OK

Проверено на exact `0ab044b87e3e296942da3307f1b1c5ed0c34f5f1`:

- `git diff --name-only 7f17e9a..0ab044b` → ровно 6 файлов, все в `allowed_paths` паспорта: `.github/workflows/hosted-ci.yml` (→ `.github/workflows/**`), `config/infra/hosted-ci.v1.json`, `docs/infra/HOSTED_CI_R1.md`, `docs/work/executions/EX-INFRA1-001-R1/{passport.json, branch-passport.md, events/0001-work-order-started.json}` (→ `EX-INFRA1-001-R1/**`). Выходов за allowed_paths нет. Статистика: 491 вставка, 0 удалений.
- `git diff 7f17e9a..0ab044b -- project/state.json project/infra-state.json project/plan.json` → пусто (0 строк): научный и инфра state не тронуты — Implementer не флипает `capabilities.hosted_ci` и не двигает frontier (`infra-state.json`: `INFRA1/IN_PROGRESS`, `INFRA1-001/READY`, `capabilities.hosted_ci: false` — ожидаемо до Director gate).
- Сквозной скан добавленного diff'а на секреты (`secret|token|password|api_key|AKIA|ghp_|gho_|ghs_|github_pat|PRIVATE KEY|xox*|sk-…`) → только документальные упоминания политики, ни одного значения. Дополнительно `grep 'secrets\.'` по workflow → 0 совпадений: ни один шаг не потребляет secrets.
- `.github/` на `0ab044b` содержит ровно один workflow (`hosted-ci.yml`); шаблоны `ISSUE_TEMPLATE/*` и `PULL_REQUEST_TEMPLATE.md` — pre-existing с main.
- Durable START-дисциплина: START-коммит `a689711` (parent = base `7f17e9a`) содержит только паспорт, event 0001 и branch-passport; substantive work идёт следующими коммитами. Хронология commit-дат монотонна: `21:38:08 → 21:44:07 → 21:46:47 → 21:49:12 → 21:50:54 +1000`, согласуется с timestamp событий (11:37–11:50 UTC).
- Дифф `0ab044b..ff8d86a` ограничен execution-каталогом: events 0002–0004, `summary.md`, смена `status: STARTED → HANDOFF_READY` в паспорте — substantive-дерево не меняет, что подтверждает binding terminal event ↔ substantive HEAD `0ab044b`.

## 2. Workflow против baseline — OK

Сверка `.github/workflows/hosted-ci.yml` с `EXECUTION-BASELINE-R1` §3–§7 и `execution-baseline.v1.json` (YAML независимо распарсен pyyaml; структурные поля подтверждены):

| Требование baseline | Реализация | Результат |
|---|---|---|
| §4 `TR-PR` | `pull_request: branches: [main], types: [opened, synchronize, reopened]` | OK |
| §4 `TR-PUSH-MAIN` | `push: branches: [main]` | OK |
| §4 `TR-PRT`/`TR-WFRUN` FORBIDDEN_R1; TR-SCHEDULE/TR-TAG deferred | `pull_request_target`, `workflow_run`, `schedule`, tags-, release-триггеры физически отсутствуют; `workflow_dispatch` тоже отсутствует (RESERVED_NOT_ACTIVE соблюдён) | OK |
| §3 `H0` only, `NC-1` | `runs-on: ubuntu-latest`; ни одного `self-hosted`/`nanolab-*` label во всём файле | OK |
| §5.2, `NC-4` | top-level `permissions: contents: read`; write-объявлений нет; другой jobs нет —scope точечный | OK |
| §5.3/5.4, `NC-7` | секреты не используются; `persist-credentials: false` на checkout | OK |
| §6 `RC0` ≤ 15 мин | `timeout-minutes: 15` на job; unbounded-шагов нет | OK |
| §6 `NC-6` (rerun не увеличивает бюджет) | `concurrency: hosted-ci-<event>-<ref>`, `cancel-in-progress: true` | OK |
| §9 pinned actions (обязателен с INFRA1-001) | см. §2.1 ниже — пины верифицированы независимо | OK |
| §5.4 read-only compute | токен не персистится; никаких credentials в шаги не передаётся | OK |
| §7 artifact policy | см. §2.2 ниже | OK |
| `NC-5` fail closed | нет fallback/strategy на другой исполнитель; недоступность hosted = красный check | OK |

### 2.1 Пины actions — независимо верифицированы ls-remote

```text
git ls-remote https://github.com/actions/checkout        refs/tags/v5.0.1 → 93cb6efe18208431cddfb8368fd83d5badbf9bfd  (= пин в workflow, lightweight tag → commit)
git ls-remote https://github.com/actions/upload-artifact refs/tags/v5.0.0 → 330a01c490aca151604b8cf639adc76d48f6c5d4  (= пин в workflow, lightweight tag → commit)
```

Заявление HOSTED_CI_R1.md §2 («теги lightweight и указывают точно на эти коммиты») подтверждено: dereference-строк `^{}` нет — теги указывают непосредственно на закоммиченные SHA, совпадающие с пинами. Ссылки на версии в комментариях (`# v5.0.1`, `# v5.0.0`) соответствуют реальным тегам.

### 2.2 Артефакты — OK

Оба шага (`Build debug artifact manifest`, `Upload debug artifacts`) под `if: failure()` — успешный run артефактов не производит. Manifest `nanolab.hosted_ci_debug_manifest.v1` содержит все обязательные provenance-поля baseline §7.1 / `review-policy.v1.json.artifact_reuse_requires`: `sha256`, `size_bytes`, `producer_run_id`, `subject_sha`, `storage_location`; `scientific_evidence: false`; retention 7 дней; в `ci-debug/` пишутся только результаты чеков и fingerprint без секретов (`runner_os`, `event_name`, `subject_sha`, версии python/git). Содержимое соответствует «ephemeral debug material, не scientific evidence».

### 2.3 Поверхность script-injection — OK

Все `${{ }}`-выражения вынесены из `run:`-блоков: `github.event.before` передаётся через `env:` (`EVENT_BEFORE`), `run_id`/`run_attempt` — через `env:`/`with:`. Прямой интерполяции недоверенных контекстов в shell нет — классический вектор инъекции в PR-триггерах закрыт по построению. Shell-гигиена: каждый `run` открывается `set -euo pipefail`; edge-кейсы Check 3 обработаны (пустой `github.event.before`/нулевой SHA → fallback `HEAD~1` → skip; удалённый каталог → SKIP; пустой diff → skip с exit 0).

## 3. Воспроизведение чеков ревьюером — OK

Локально (Windows, Python 3.11.8; имплементёр валидировал в WSL Ubuntu 24.04 / Python 3.12.3 — результаты совпадают):

```text
Check 1  python -m json.tool по каждому tracked *.json (git ls-files)  → 59/59 OK @ 0ab044b
Check 2  PYTHONPATH=scripts python -m harness.cli check-consistency --root .
         → ok=true, errors=[], warnings=[]; frontier NL1; head=0ab044b; tree=a10573f7
Check 3  PYTHONPATH=scripts python -m harness.work_cli validate docs/work/executions/EX-INFRA1-001-R1
         → ok=true, errors=[] (exit 0)
```

Проверка обоснованности diff-scope Check 3 (probe на canonical main, @0ab044b):

```text
work_cli validate docs/work/executions/EX-INFRA0-001-R1 → exit 3: "terminal/handoff event must be last"
work_cli validate docs/work/executions/EX-NL1-001-R1    → exit 3: "terminal/handoff event must be last"
```

Находка имплементёра подтверждена независимо: в обоих каталогах main за `HANDOFF_COMPLETED` следует пост-терминальный `CONTINUATION_CHECKPOINT` (review-corrections), который правило terminal-last `work_cli.py` (строки 83–87) помечает ошибкой. Сплошная валидация всех `EX-*` была бы вечно красной на main независимо от PR. Решение «валидировать только изменённые каталоги» — корректная, fail-closed интерполяция; ограничение результата см. MINOR-2.

## 4. События/паспорт против схем — OK (с NOTE-1)

Независимо воспроизведено (jsonschema Draft202012, Python 3.11.8 / jsonschema 4.22.0; полный набор событий извлечён из git-объекта `ff8d86a`):

- Events `0001–0004`: **SCHEMA-OK 4/4** против `config/control/harness/work-event.schema.v1.json` (required-поля, enum `event_type`/`actor_role`, паттерны `event_id`/`subject_sha`, `additionalProperties: false`).
- `passport.json`: валиден по всем полям, **кроме NOTE-1**: `checkpoint: "INFRA1"` не матчит `^NL[0-8]$` в `execution-passport.schema.v1.json`. Отклонение заранее задокументировано имплементёром (branch-passport §1 отклонений, event 0001, HOSTED_CI_R1.md §7.5) — тот же класс, что принятый в EX-INFRA0-001-R1. Практический валидатор паттерн не проверяет (подтверждено чтением `scripts/harness/work_cli.py`); схема не менялась (вне allowed_paths).
- `work_cli validate` по полному набору @ `ff8d86a`: `ok=true`, event_types `WORK_ORDER_STARTED → IMPLEMENTATION_COMMITTED → VALIDATION_RECORDED → HANDOFF_COMPLETED`, terminal последний, `summary.md` присутствует, `status: HANDOFF_READY`.
- Цепочка subject_sha: 0001 = base `7f17e9a` (ancestor main — exit 0); 0002/0003 = substantive `0ab044b` (tree `a10573f7` совпадает); 0004 = `0ab044b` — terminal корректно привязан к substantive HEAD, а не к handoff-коммиту. Timestamps событий строго монотонны и согласованы с commit-датами.
- Статусная дисциплина: `ACCEPTED` нигде не выставлен; конфиг и документ в статусе `PROPOSED`; merge в `main` и обновление `project/infra-state.json` корректно оставлены Director/Human Gate.

## 5. Оценка находок имплементёра — все подтверждены, решения обоснованы

1. **`work_cli` terminal-last vs review-corrections** — подтверждено независимо (§3). Diff-scoped Check 3 — разумное техническое решение этапа; перенос policy-решения (corrections-aware валидатор или формализация пост-терминальных corrections) в `INFRA1-002` корректен: это изменение валидатора/конвенции, а не CI-маршрута. Остаточный эффект зафиксирован как MINOR-2.
2. **Отсутствие `docs/work/WO-INFRA1-001.md`** — подтверждено (`git ls-tree 7f17e9a docs/work/`: есть только WO-INFRA0-001 и WO-NL*). Создание WO — Director authority и вне allowed_paths паспорта; исполнение по миссии + `project/infra-plan.json` (задача `INFRA1-001 «Add hosted harness CI»`, depends_on ACCEPTED `INFRA0-001`) + baseline §13.3 — обоснованно и задокументировано. Урок прежний (INFRA0 MINOR-4): mission-указания должны публиковаться durably.
3. **`tests/task_bus` вне main** — подтверждено (`tests/` на `7f17e9a` отсутствует; ветка `control/git-task-bus-r1` существует и не влита). Исключение pytest из hosted-подмножества корректно: чеков, которые нельзя исполнить на main, в CI включать нельзя.
4. **Owner-actions (repo settings)** — обоснованно: repo default token permissions и branch protection не выражаются git-коммитом; baseline §5.1 сам относит настройку к INFRA1-001, но механика — UI владельца. Митигация в коде выполнена: каждый workflow независимо несёт явный `permissions:`-блок, поэтому до флипа repo default effective scope этого workflow уже read-only. Владельцу остаётся: (а) repo default read-only, (б) branch protection `main` с required check `RC0 hosted validation (H0)` и запретом force-push, (в) впредь не вешать hosted-labels на self-hosted runners.
5. **Checkpoint `INFRA1` vs `^NL[0-8]$`** — подтверждено schema-валидацией (§4); см. NOTE-1.

## 6. Security-оценка routed-политики (security-критичный WO)

Маршрутизация untrusted→trusted не имеет дыр в этом workflow:

- **Граница по происхождению кода соблюдена**: fork-PR и in-repo PR равноправны (`pull_request` без фильтров авторства), оба исполняются только на ephemeral `H0`; самохостинг недостижим — ни label, ни dispatch-триггера, ни workflow-моста в репозитории нет.
- **`NC-2`/`NC-7` обходы отсутствуют**: `pull_request_target` и `workflow_run` запрещены и физически отсутствуют; untrusted-артефакты (`ci-debug`) уходят только в GitHub Actions artifact store, не в trusted-зону.
- **Эскалация прав невозможна в рамках токена**: `contents: read` + `persist-credentials: false`; write-поверхности нет.
- **Бюджетная гигиена**: жёсткий job-timeout 15 мин + cancel-in-progress; rerun наследует тот же RC0-бюджет; paid compute не расходуется (public repo → free tier; `paid_compute_authorized = false` не затронут).
- **Residual risks (все — вне кода этого WO и уже трекаются)**: (а) до INFRA1-002 инварианты NC-1..NC-7 соблюдены конструктивно, но не защищены механическим линтом — защита маршрута = review-дисциплина (NOTE-4); (б) branch protection ещё не включена — до owner-action прямой push в main проходит без required check (NOTE-4/§5.4); (в) живой прогон на hosted runner ещё не выполнялся — первый TR-PR прогон обязан стать evidence (см. Next action).

## Независимые валидации (воспроизведено ревьюером)

```text
git ls-remote checkout/v5.0.1, upload-artifact/v5.0.0 → точное соответствие пинам (lightweight tags)
python -m json.tool — 59/59 tracked *.json OK @ 0ab044b
PYTHONPATH=scripts python -m harness.cli check-consistency --root . → ok=true, errors=[], warnings=[]
PYTHONPATH=scripts python -m harness.work_cli validate EX-INFRA1-001-R1 → ok=true (exit 0);
                       probe EX-INFRA0-001-R1 / EX-NL1-001-R1 → exit 3 terminal-last (обосновывает diff-scope)
jsonschema Draft202012 — events 0001–0004: SCHEMA-OK 4/4; passport: FAIL только checkpoint ^NL[0-8]$ (NOTE-1)
pyyaml — workflow structural gate: triggers/permissions/runs-on/timeout/concurrency подтверждены
git diff --name-only 7f17e9a..0ab044b → 6 файлов, все в allowed_paths; state-файлы: 0 строк diff
scan diff на secret-паттерны → 0 значений; grep 'secrets\.' по workflow → 0
git ls-tree 7f17e9a → WO-INFRA1-001.md отсутствует; tests/ отсутствует; ветка control/git-task-bus-r1 не влита
git merge-base --is-ancestor 7f17e9a 0ab044b → exit 0 (base = canonical main)
```

## Findings

- **MINOR-1 — Числовая неточность evidence-записи «58/58 JSON».** Event 0002, 0004 и `summary.md` приводят «58/58 tracked *.json OK» в привязке к substantive HEAD `0ab044b`; фактически на `0ab044b` tracked JSON — **59** (56 на base; 58 — это промежуточный `ed2d596`, где `hosted-ci.v1.json` ещё не закоммичен; event 0002 честно оговаривает «на момент валидации», но summary/0004 привязывают число к `0ab044b`). Существество не затронуто — ревьюером воспроизведено 59/59 OK; рекомендация: одна исправляющая строка в evidence или фикс в INFRA1-002-документации, чтобы аудит по exact HEAD не спотыкался.
- **MINOR-2 — Diff-scoped Check 3 блокирует легитимные corrections.** Любой PR, изменяющий `EX-INFRA0-001-R1` или `EX-NL1-001-R1`, попадёт под terminal-last правило и получит красный Check 3 — до поставки corrections-aware валидатора пост-терминальные corrections в эти каталоги технически невносимы через PR (fail-closed трение, не дыра). Решение уже назначено в INFRA1-002; рекомендация — приоритизировать corrections-политику валидатора как первый пункт INFRA1-002 и секвенировать любые corrections-ветки после неё.
- **NOTE-1 — `checkpoint: INFRA1` vs `^NL[0-8]$`.** Строгое schema-несоответствие, заранее задокументированное (тот же класс, что принятый NOTE-1 вердикта INFRA0-001). Кандидат в control WO: расширить паттерн до `(NL|INFRA)[0-7]` — сейчас это уже два INFRA-исполнения подряд с одним и тем же известным отклонением.
- **NOTE-2 — WO-файл отсутствует в main.** Принято с той же оговоркой, что MINOR-4 вердикта INFRA0-001: scope верифицируется по infra-plan/baseline, но mission-текст недоступен независимой проверке. Рекомендация Director'у — backfill `docs/work/WO-INFRA1-001.md` при checkpoint proposal и впредь публиковать mission-указания durably.
- **NOTE-3 — `pull_request.types` без `ready_for_review`.** PR, открытый как draft и переведённый в ready, не перепроведёт check до следующего synchronize (opened/synchronize/reopened уже покрыты). На безопасность не влияет; замечание для INFRA1-002 lint-эталона.
- **NOTE-4 — Механические negative controls и branch protection ещё отсутствуют.** Это соответствует плану (INFRA1-002 + owner actions), но до их поставки маршрут защищён только review-дисциплиной: ни один линт не запретит будущий коммит с self-hosted label или `pull_request_target`, а main не имеет required check. Рекомендация: трактовать INFRA1-002 как prerequisite для любого расширения CI-поверхности, owner-actions §6 HOSTED_CI_R1.md выполнить до/при merge.

## Claim ceiling

`C0_SOFTWARE_ONLY` (подтверждён): результат — CI-workflow, machine-readable конфиг и документация; научных утверждений не содержит, scientific claim не создаёт и не повышает (`E0–E6 NOT_RUN`; `project/state.json` не затронут; «зелёный CI — технический факт, не научный PASS»). Вердикт относится к исполнению на exact HEAD `0ab044b87e3e296942da3307f1b1c5ed0c34f5f1`; он не объявляет capability `hosted_ci` принятой, не заменяет Director checkpoint и Human merge gate, и не утверждает безопасность будущих изменений workflow (см. NOTE-4).

## Next action (одно)

Независимый VERIFIER: fresh checkout exact `0ab044b87e3e296942da3307f1b1c5ed0c34f5f1`, воспроизвести команды раздела «Независимые валидации», сверить allowed_paths/pins/subject_sha и выставить вердикт рядом (VERIFIER_VERDICT); затем Director checkpoint proposal INFRA1-001 (с явным решением по MINOR-1/MINOR-2 и NOTE-1/NOTE-2), merge PR — Human Gate с проверкой первого live `TR-PR` прогона как evidence; обновление `project/infra-state.json` — только после принятого merge; далее INFRA1-002, начиная с corrections-политики `work_cli` (MINOR-2) и механических NC-lint.
