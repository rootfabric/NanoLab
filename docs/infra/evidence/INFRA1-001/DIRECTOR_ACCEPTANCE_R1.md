# Director Acceptance — INFRA1-001 (safe GitHub-hosted CI)

Дата решения: 2026-09-09. Роль: DIRECTOR (главный агент INFRA-линии миссии; явная авторизация владельца на Director-приёмку и merge в `main` получена в сессии).

## Решение

```text
INFRA1-001 = ACCEPTED
checkpoint INFRA1 = IN_PROGRESS (стадия НЕ закрыта: остаётся INFRA1-002 «Add PR validation gates»)
frontier = INFRA1 (без изменений)
next_work_order = INFRA1-002 (READY)
claim = C0_SOFTWARE_ONLY
capabilities.hosted_ci = false — НЕ флипается этим решением (см. «Условия»)
HOSTED_CI_R1 (docs/infra/HOSTED_CI_R1.md + config/infra/hosted-ci.v1.json) = ACCEPTED (был PROPOSED)
```

## Основание

1. **Реализация**: `EX-INFRA1-001-R1` — первый исполняемый workflow репозитория `.github/workflows/hosted-ci.yml` + машинно-читаемая проекция `config/infra/hosted-ci.v1.json` + документация `docs/infra/HOSTED_CI_R1.md`. Маршруты строго TR-PR (`pull_request` → `main`) и TR-PUSH-MAIN (`push` → `main`); `runs-on` исключительно `ubuntu-latest` (класс H0, ни одного self-hosted/reserved label — NC-1); явный workflow-level `permissions: contents: read` без write-объявлений (NC-4); секреты не используются, `persist-credentials: false` (NC-7); `timeout-minutes: 15` = бюджет `RC0_HOSTED_VALIDATION` + concurrency `cancel-in-progress` (NC-6); нет fallback-исполнителя (NC-5, fail closed); оба actions запинены по full commit SHA с независимо верифицированным `git ls-remote` соответствием; forbidden-маршруты (`pull_request_target`, `workflow_run`, `schedule`, tag/release, `workflow_dispatch`) физически отсутствуют; артефакты — только при падении, с provenance-манифестом всех пяти полей §7.1. Runners/secrets/GPU/paid compute — NONE.
2. **Scope**: diff `7f17e9a..0ab044b` — ровно 6 файлов, все в allowed_paths паспорта; `project/infra-state.json`, `project/state.json` blob-неизменны (подтверждено обоими вердиктами); секретов в diff нет. Субъект верификации — substantive HEAD `0ab044b87e3e296942da3307f1b1c5ed0c34f5f1` (tree `a10573f7`); tip `ff8d86a` отличается только bookkeeping-коммитами (events 0002–0004, `summary.md`, статусы паспорта), схемы которых проверены 4/4.
3. **Независимые вердикты**: REVIEWER **PASS** (`0f1c348`; findings MINOR-1..2, NOTE-1..4 — все неблокирующие) и VERIFIER **PASS** (`22394cc`; 52/52 workflow-инвариантов, findings KNOWN/OWNER-ACTION/NOTE, secret-скан 0, JSON 59/59) на exact subject `0ab044b87e3e296942da3307f1b1c5ed0c34f5f1`. Оба вердикта влиты в эту ветку merge-коммитами (`d0411b0`, `cb4dc07`).
4. **Граница ролей соблюдена**: документ и конфиг опубликованы в статусе `PROPOSED`, `ACCEPTED` имплементером нигде не выставлен, `capabilities.hosted_ci` не флипался, state-файлы не тронуты — принятие и перевод статусов происходят только этим Director-решением через принятый merge.
5. **Отклонения, заранее задокументированные имплементёром** (WO-файл отсутствовал в `main`; `checkpoint: INFRA1` против `^NL[0-8]$` в схеме паспорта) — приняты с решениями ниже (NOTE-2, NOTE-1).

## Решения по findings

| Finding | Решение Director'а |
|---|---|
| **MINOR-1** (REVIEWER): evidence-записи «58/58 tracked JSON» в event `0004` и `summary.md` привязаны к substantive HEAD `0ab044b`, где фактически **59** tracked JSON (56 на base; 58 — промежуточный `ed2d596`, где `hosted-ci.v1.json` ещё не закоммичен; event `0002` честно оговаривает «на момент валидации») | **ERRATUM ЗАФИКСИРОВАН ЭТИМ ВЕРДИКТОМ.** Правильное значение на exact `0ab044b`: **59/59 OK** — независимо воспроизведено и ревьюером, и верификатором. Существество (валидность всех JSON) не затронуто. **Старые события `0002`/`0004` и `summary.md` НЕ редактируются** (immutable execution log). Formal event-level correction (`CONTINUATION_CHECKPOINT` в `EX-INFRA1-001-R1`) сознательно **отложена до INFRA1-002**: по MINOR-2 текущий diff-scoped Check 3 с правилом terminal-last пометил бы такой пост-терминальный event ошибкой и заблокировал бы собственный PR этого checkpoint'а; corrections-события секвенируются после corrections-aware валидатора. Этот вердикт — authoritative Director-запись erratum'а. |
| **MINOR-2** (REVIEWER): diff-scope Check 3 блокирует легитимные post-terminal corrections в `EX-INFRA0-001-R1`/`EX-NL1-001-R1` до поставки corrections-aware валидатора | **ПРИНЯТО С ПРИОРИТЕТОМ.** Corrections-политика `work_cli` (corrections-aware валидатор или формализация пост-терминальных corrections) — **первый пункт `INFRA1-002`** и **блокирующий критерий его приёмки** наряду с механическим NC-1-тестом (условие MINOR-1 вердикта INFRA0-001). Любые corrections-ветки в указанные каталоги не открывать до поставки. До этого момента fail-closed трение признаётся приемлемым (не дыра). |
| **NOTE-1** (обе стороны): `checkpoint: "INFRA1"` против `^NL[0-8]$` в `execution-passport.schema.v1.json` | **ПРИНЯТО К СВЕДЕНИЮ** (заранее задокументированное отклонение; второй INFRA-прецедент подряд). Кандидат в отдельный control WO: расширить паттерн до `(NL\|INFRA)[0-7]`. Не блокирует; валидатор паттерн фактически не проверяет. |
| **NOTE-2** (REVIEWER/VERIFIER): `docs/work/WO-INFRA1-001.md` отсутствовал в `main` | **ЗАКРЫТО ЭТИМ CHECKPOINT'ОМ**: backfill `docs/work/WO-INFRA1-001.md` опубликован отдельным коммитом (authorship Director; основание — миссия владельца + `project/infra-plan.json` + baseline §13.3). Директива INFRA0 MINOR-4 действует впредь: mission-указания фиксировать durably с самого старта. |
| **NOTE-3** (REVIEWER): `pull_request.types` без `ready_for_review` | **ПРИНЯТО К СВЕДЕНИЮ.** В эталон-список линтов `INFRA1-002` (механический lint-эталон workflow). На безопасность не влияет. |
| **NOTE-4** (REVIEWER; verifier FINDING-4 OWNER-ACTION): механические NC-линты и branch protection отсутствуют; маршрут до INFRA1-002 защищён review-дисциплиной | **ПРИНЯТО С УСЛОВИЕМ.** `INFRA1-002` трактуется как **prerequisite любого расширения CI-поверхности**. Owner actions (repo default `GITHUB_TOKEN` read-only; branch protection `main` с required check `RC0 hosted validation (H0)` и запретом force-push) остаются за владельцем по `HOSTED_CI_R1.md` §6 и выполняются по возможности до/при следующих merge. До их исполнения каждый workflow обязан независимо нести явный `permissions:`-блок (как сделано). |
| **VERIFIER FINDING-5** (tip = subject + 2 bookkeeping-коммита) | **ПРИНЯТО К СВЕДЕНИЮ.** Решение принято по фактическому состоянию ветки `ff8d86a`; bookkeeping ограничен `docs/work/executions/EX-INFRA1-001-R1/`, содержательных расхождений с subject по верифицированным инвариантам вердикты не зафиксировали. |

## Условия, с которыми принято

- **`capabilities.hosted_ci` остаётся `false`.** Условие флипа (явно): capability `hosted_ci` может стать `true` только отдельным последующим Director-решением после того, как (а) **первый live TR-PR/TR-PUSH-MAIN прогон нового workflow на hosted runner наблюдён как evidence** (зелёный лог чеков — «зелёный CI — технический факт, не научный PASS»), и (б) выполнены сопутствующие **INFRA1-002/owner UI-действия** (repo default read-only, branch protection — `HOSTED_CI_R1.md` §6). Этот merge сам активирует workflow и триггерит первые live-прогоны (TR-PR на PR checkpoint'а, TR-PUSH-MAIN на merge-коммите); их результат фиксируется в SESSION_LOG/отчёте миссии, но флип этим решением **не производится**.
- Документ `HOSTED_CI_R1.md` и конфиг `hosted-ci.v1.json` переводятся в статус `ACCEPTED` этим решением; изменение содержимого — только новой ревизией в отдельном bounded WO.
- `TR-DISPATCH` остаётся `RESERVED_NOT_ACTIVE`; публичный PR-код не может автоматически исполняться на trusted self-hosted узлах (в репо их нет).
- Научный трек не затронут: `project/state.json` без изменений, `E0–E6 = NOT_RUN`, `physics_runs = 0`; INFRA-merge не повышает scientific claim.

## Claim ceiling

`C0_SOFTWARE_ONLY` (подтверждён обоими независимыми вердиктами): результат — CI-workflow, machine-readable конфиг и документация; научных утверждений не содержит и не создаёт. Настоящее решение не объявляет безопасность будущих изменений workflow и не активирует ни одну capability: `hosted_ci` активируется соответствующим последующим решением после фактического live-прогона и owner/INFRA1-002-действий, а не этим merge.

## Следующее действие

`INFRA1-002` «Add PR validation gates» (READY), порядок внутри WO: (1) corrections-aware политика `work_cli` — первый пункт (MINOR-2, блокирующий критерий); (2) механические negative controls NC-1..NC-7 — NC-1-тест блокирующий (наследованное условие INFRA0 MINOR-1), NOTE-3 (`ready_for_review`) в lint-эталон; (3) candidate: включение pytest-чеков после влития `control/git-task-bus-r1`. Владельцу: owner actions `HOSTED_CI_R1.md` §6. После закрытия INFRA1-002 — checkpoint `INFRA1` (закрытие стадии) с решением о флипе `capabilities.hosted_ci` при наличии live-evidence.
