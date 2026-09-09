# INFRA0-001 — Independent Reviewer Verdict R1

Роль: независимый fresh REVIEWER (без доступа к контексту имплементёра; только код, Git-факты и документы). Дата: 2026-09-09. Work Order: `INFRA0-001`. Исполнение: `EX-INFRA0-001-R1`.

Предмет ревью: ветка `infra/infra0-execution-baseline-r1` @ `9427ff1c081d20d87a418fec2757916d6ecca859` (substantive HEAD = merge-коммит `41cd55ca4d3bf20eac7cd8c0f6edb879825dcdfe`, merge с `origin/main` `71535d00a2e729349eea2337217a2c591ed9317d`; handoff-коммит `9427ff1` добавляет только terminal event 0004 + статусы паспорта).

Review выполнялся на ветке `review/infra0-execution-baseline-r1` от exact `9427ff1` в worktree `C:\NanoLab\review-infra-0-001`. Размещение вердикта: `docs/infra/evidence/INFRA0-001/` — track-локальный evidence-root для INFRA (зеркалирует существующий паттерн `docs/evidence/<WO>/` научного трека; до этого момента у INFRA evidence-каталога не было).

## Verdict

**PASS**

Baseline `EXECUTION-BASELINE-R1` покрывает все пять критериев приёмки WO-INFRA0-001 и согласован с `SECURITY_MODEL.md`, `EXECUTION_BACKENDS.md`, `ROADMAP.md` и `project/infra-plan.json`; границы доверия определены по происхождению кода (canonical main + explicit protected dispatch), а не по авторству PR; self-hosted scientific compute запрещён везде, кроме `TR-DISPATCH` с exact subject + budget + approval (`RESERVED_NOT_ACTIVE`); выдуманных значений нет (числовые бюджеты только для hosted-классов как контракт; RC2 — отложены до измерений INFRA2/3). Scope соблюдён: весь diff `71535d0..9427ff1` — только allowed_paths паспорта; runner-установок, workflows, secrets, CI-изменений нет; `project/infra-state.json` и `project/state.json` не тронуты. Запреты этапа зафиксированы явно (§10 baseline — 11 non-goals). Статусы корректны: baseline `PROPOSED`, `ACCEPTED` нигде не выставлен, паспорт `HANDOFF_READY`. Findings MINOR-1..4 / NOTE-1..3 (ниже) границу доверия не ослабляют и PASS не блокируют; MINOR-1 (deferral негативного теста в `INFRA1-002`) требует явного решения Director'а при checkpoint proposal.

Примечание по словарю: `review-policy.v1.json` допускает `PASS | FAIL | INSUFFICIENT_EVIDENCE`; миссия ревью дополнительно определяет `FIX_REQUIRED` (state в `harness-policy.v1.json`). Вердикт `PASS`; в случае требования доработок по findings — маршрут `FIX_REQUIRED` с Repair Map, повтор того же действия запрещён.

## 1. Scope-границы — OK

Проверено на exact `9427ff1c081d20d87a418fec2757916d6ecca859`:

- `git diff --name-status 71535d0..9427ff1` → ровно 9 файлов, все добавления (A): `config/infra/execution-baseline.v1.json`, `docs/infra/EXECUTION_BASELINE_R1.md`, `docs/work/executions/EX-INFRA0-001-R1/{passport.json, summary.md, branch-passport.md, events/0001..0004}`. Полное покрытие `allowed_paths` паспорта, выходов за них нет.
- `git diff 71535d0..9427ff1 -- project/infra-state.json project/state.json .github/ config/control/` → пусто: научный и инфра state-файлы, workflows и control-политики не изменены. `git diff --quiet 71535d0 9427ff1 -- project/infra-state.json` → exit 0 (байт-идентичен main).
- `git ls-tree -r 9427ff1` → `.github/` содержит только pre-existing `ISSUE_TEMPLATE/*` и `PULL_REQUEST_TEMPLATE.md`; каталога `workflows` нет.
- Сквозной скан добавленного diff'а на секреты (`AKIA`, `ghp_`, `github_pat_`, `xox*`, `PRIVATE KEY`, `password=`) — совпадений нет.
- Хронология: START-коммит `ff68c12e` (parent = base `57c1e637`, содержит только passport + event 0001) создан до substantive work — durable START-дисциплина соблюдена. Handoff-коммит `9427ff1` изменяет ровно 3 файла: `0004-handoff-completed.json` + статусы `passport.json`/`branch-passport.md` — как заявлено в binding-блоке summary.
- **MINOR-4**: machine-readable конфиг лежит в `config/infra/`, тогда как WO scope разрешает `config/control/infra/**`. Отклонение задокументировано имплементером (branch-passport §2, summary) как явное указание миссии владельца; текст миссии в Git отсутствует, независимо верифицировать его нельзя. Файл входит в `allowed_paths` паспорта, дублей в `config/control/infra/` нет, валиден как JSON. Принято с оговоркой; рекомендация — впредь либо расширять scope WO, либо публиковать mission-указания durably.

## 2. Полнота baseline по критериям приёмки WO — OK

| Критерий/выход WO | Где определён | Результат |
|---|---|---|
| Trusted trigger routes | baseline §4: TR-PR, TR-PUSH-MAIN (hosted-only), TR-DISPATCH (protected, fail-closed guards, RESERVED_NOT_ACTIVE), TR-SCHEDULE/TR-TAG (deferred), TR-PRT (`pull_request_target`) и TR-WFRUN (`workflow_run`) = FORBIDDEN_R1 | ПОЛНО |
| Runner labels | §3: H0 `ubuntu-latest`/`ubuntu-24.04` (платформенные); C0 `nanolab-cpu`, G0 `nanolab-gpu`, H1 `nanolab-hpc-*` — reserved, не зарегистрированы; запрет hosted-labels на self-hosted; запрет self-hosted labels вне TR-DISPATCH | ПОЛНО |
| GitHub permissions | §5: repo default read-only (target, фиксируется в INFRA1-001), per-workflow минимальный `permissions:`, PR route `contents: read` и ничего больше, fork-PR без secrets, без долгоживущих credentials, secrets в этом WO запрещены | ПОЛНО |
| Execution budgets | §6: RC0 ≤15 мин, RC1 ≤60 мин (hosted, контракт), RC2 trusted CPU — budget обязателен в dispatch, числа по измерениям INFRA2/3 (без выдуманных значений), RC3 GPU forbidden до INFRA5; unbounded jobs запрещены; rerun не увеличивает бюджет; paid compute запрещён (`project/state.json:59` подтверждён: `paid_compute_authorized: false`); `parallel_scientific_runtime_limit = 1` (`scheduler-policy.v1.json:7` подтверждён) | ПОЛНО |
| Artifact policy | §7: provenance-поля `sha256/size_bytes/producer_run_id/subject_sha/storage_location` — совпадают с `review-policy.v1.json.artifact_reuse_requires`; hosted-артефакты не scientific evidence; raw вне Git → manifest в Git; rerun проверяет существующий manifest; durable store — не здесь (INFRA4) | ПОЛНО |
| Negative controls | §8: NC-1..NC-7 с угрозой, инвариантом, статусом и назначенной механической проверкой | ПОЛНО (см. MINOR-1) |
| Public PR vs trusted self-hosted routing | §4.1: fork-PR и in-repo PR → только H0 без привилегии по авторству; self-hosted только через explicit dispatch c exact subject + budget + approval; «всё остальное» → self-hosted запрещён | ПОЛНО |
| Machine-readable runner/dispatch policy (output 1) | `config/infra/execution-baseline.v1.json` — полная проекция документа (см. §3) | ЕСТЬ (путь — MINOR-4) |
| Threat model validation matrix (output 2) | §9: 7 actors × vector × asset × control × residual risk | ЕСТЬ |
| Routing contract (output 3) | §4.1 | ЕСТЬ |
| Negative test «untrusted PR не может выбрать self-hosted label» (output 4) | Зафиксирован как инвариант NC-1; механический тест отложен в `INFRA1-002` | ЧАСТИЧНО (MINOR-1) |
| Exact next WO (output 5) | §13 + `infra-plan.json`: `INFRA1-001` «Add hosted harness CI» (depends_on INFRA0-001), далее `INFRA1-002` | ЕСТЬ |

- **MINOR-1**: Required output №4 WO («Negative test: untrusted PR route не может выбрать self-hosted scientific label») реализован документально (NC-1, `mechanical_validation = INFRA1-002`), механического теста в этом WO нет. Отклонение задокументировано (branch-passport §3, summary) и методологически обосновано: в R1 не существует ни одного workflow — механическому lint/negative-тесту нечего проверять, а `infra-plan.json` помещает gates в `INFRA1-002` сразу после появления CI. Однако формально это недовыполненный required output, а acceptance «public PR path и trusted scientific path технически различимы» выполняется пока на уровне контракта, не механики. Решение о принятии deferral — за Director'ом при checkpoint proposal; для acceptance `INFRA1-002` механический NC-1-тест обязан стать блокирующим критерием.
- Выдуманных значений не обнаружено: платформенные labels реальные; self-hosted labels — явно `reserved`, не заявлены как существующие; числовые бюджеты только для hosted-классов и помечены контрактом; RC2-числа корректно отложены до измерений (дисциплина «не догадка»).

## 3. Соответствие SECURITY_MODEL / ROADMAP и согласованность конфига — OK (с MINOR-3)

- Hard rules 1–10 `SECURITY_MODEL.md` — каждое имеет явное покрытие в baseline §4–§8 (проверено построчно; например, правило 3 → guards TR-DISPATCH, правила 7–8 → §7.1/§7.4, правило 9 → §6.4, правило 10 → §10.8).
- Allowed trigger model `SECURITY_MODEL.md` («только workflow_dispatch из canonical main либо trusted job-controller») = TR-DISPATCH; автоматический self-hosted на PR запрещён дважды (§4.1, NC-1/NC-7) — совпадает с hard rule `AGENTS.md`.
- Границы INFRA0 vs INFRA1–7 соответствуют `ROADMAP.md` (строка INFRA0: threat model, runner trust model, branch/dispatch policy, resource classes — все четыре присутствуют) и зависимостям `infra-plan.json` (активации H0/C0/G0/H1 = INFRA1/2/5/7-001; infra-state frontier INFRA0, задача READY, capabilities все `false` — не противоречит).
- Machine-readable конфиг консистентен документу по: trust zones, runner classes/labels, trigger routes (7/7), token policy, resource classes (4/4), budget rules (5/5), executor contract fields, artifact policy, negative controls (7/7), explicit non-goals (11/11), next WOs, acceptance path. JSON валиден (`python -m json.tool` OK).
- **MINOR-3**: doc/config расхождение по TR-DISPATCH: документ §4 допускает «`H0` или защищённый `C0`/`G0`», конфиг перечисляет `allowed_runner_classes: ["H0", "C0"]` (G0 опущен). По правилу приоритетов §0 (документ > конфиг) оперативна версия документа, но конфиг — вход будущих линтеров INFRA1-002/dispatch-валидатора INFRA2-002. Практической дыры нет (G0 не существует до INFRA5, RC3 forbidden до INFRA5, §4.1 уточняет «C0, позднее G0»), однако расхождение следует устранить в следующей ревизии baseline (рекомендация: привести §4 к формулировке §4.1 или добавить G0 в конфиг с флагом, привязанным к INFRA5).

## 4. События/паспорт: схема, монотонность, subject_sha, статусы — OK (с NOTE-1)

Независимо воспроизведено (jsonschema Draft202012 + FormatChecker, Python 3.11.8 / jsonschema 4.22.0):

- Events `0001`–`0004`: **SCHEMA_OK** против `config/control/harness/work-event.schema.v1.json` — 0 ошибок по каждому (required-поля, enum event_type/actor_role, паттерны event_id/subject_sha, format date-time, additionalProperties: false).
- `passport.json`: валиден по всем полям, кроме **NOTE-1**: `checkpoint: "INFRA0"` не матчит паттерн `^NL[0-8]$` в `execution-passport.schema.v1.json` — строго валидатор схемы даёт FAIL. Отклонение заранее и корректно задокументировано имплементером (branch-passport §1, event 0001, summary): схема написана только для научного трека; практический валидатор паттерн не проверяет (подтверждено чтением `scripts/harness/work_cli.py` — проверяет presence, но не паттерн); схема не менялась (вне allowed_paths). Кандидат в control WO: расширить паттерн до `(NL|INFRA)[0-7]`.
- Монотонность: event_id 0001→0004 без пропусков и дубликатов; timestamps `10:19:06Z → 10:25:02Z → 10:27:40Z → 10:28:20Z` строго возрастают; согласуются с commit-датами ветки (`ff68c12` 20:19:41+10 … `9427ff1` 20:29:04+10). Первое событие — `WORK_ORDER_STARTED`, единственное; terminal `HANDOFF_COMPLETED` — последнее (`CONTROL_WORK.ps1 validate`: `has_terminal_handoff: true`).
- subject_sha ↔ реальные коммиты (все существуют, `git cat-file -t` = commit): 0001 = `57c1e637…` (base; parent START-коммита, ancestor `main@71535d0` — exit 0); 0002 = `870f52e3…` (implementation; tree `aba753e2…` — совпадает с заявленным); 0003 = `870f52e3…` (валидации на implementation HEAD); 0004 = `41cd55ca…` (substantive HEAD — merge; tree `db4ea454…` — совпадает; parents `f880ff6` + `71535d0` — merge состава подтверждён).
- Статусы: паспорт `HANDOFF_READY` (валидный enum), baseline и конфиг — `PROPOSED` синхронно; `ACCEPTED` не выставлен нигде (grep: упоминания только как запреты/условия); `project/infra-state.json`: frontier INFRA0, INFRA0-001 READY, capabilities все false — ожидаемо для Implementer'а без Director gate.

## 5. Явные запреты этапа — OK

- Baseline §10 фиксирует 11 non-goals, конфиг — `explicit_non_goals` (11, попарно совпадают). Все пункты «Не разрешено» из WO покрыты: runner-установки (§10.1), scientific campaign E1/E2 (§10.9, E0–E6 NOT_RUN), repository secrets (§10.3, + факт SECRETS_ADDED=NONE в summary), `project/state.json` (§10.10), автоматический self-hosted для public PR (§10.4 — «запрещено в принципе»).
- Фактическая поверхность: RUNNERS_REGISTERED=NONE, WORKFLOWS_ADDED=NONE, SECRETS_ADDED=NONE, PAID_COMPUTE=NONE — подтверждено независимым осмотром дерева и diff'а (§1).
- Граница ролей соблюдена: `ACCEPTED`/флип `capabilities` не выставлены; merge в `main` и обновление `project/infra-state.json` корректно оставлены Director/Human Gate (§13, acceptance_path конфига). Self-acceptance отсутствует.

## Независимые валидации (воспроизведено ревьюером)

```text
python -m json.tool — 8/8 OK (passport, events 0001–0004, execution-baseline.v1.json,
                      infra-plan.json, infra-state.json)
jsonschema Draft202012 — events 0001–0004: SCHEMA_OK 4/4;
                        passport: FAIL только checkpoint ^NL[0-8]$ (NOTE-1, задокументировано)
.\CONTROL_WORK.ps1 validate docs/work/executions/EX-INFRA0-001-R1
                      → ok=true, errors=[], has_terminal_handoff=true
.\CONTROL_DEVELOPMENT.ps1 -CheckConsistency
                      → ok=true, errors=[], warnings=[]
git merge-base --is-ancestor 57c1e63 71535d0 → exit 0
git diff --name-status 71535d0..9427ff1 → 9 файлов (A), все в allowed_paths
git diff (state/.github/config-control) 71535d0..9427ff1 → пусто
git cat-file / rev-parse — деревья aba753e2, db4ea454 и parents 41cd55c подтверждены
scan diff на secret-паттерны → 0 совпадений
```

## Findings

- **MINOR-1** — Required output WO №4 «negative test» реализован документально (NC-1); механическая проверка отложена в `INFRA1-002`. Deferral задокументирован и обоснован отсутствием workflows в R1, но требует явного решения Director'а; acceptance `INFRA1-002` обязан включать механический NC-1-тест как блокирующий критерий.
- **MINOR-2** — Baseline §8, вводная фраза: «Инварианты, которые обязаны быть технически необходи­мыми к нарушению» — инвертированный смысл (должно быть «невозможными» = technically impossible to violate), плюс артефакт U+00AD (soft hyphen) внутри слова. Инварианты в самой таблице NC однозначны, смысловой ошибки контроля нет, но формулировка в security-документе должна быть исправлена исправляющим коммитом или в R2.
- **MINOR-3** — Doc/config: §4 допускает G0 в TR-DISPATCH, конфиг ограничивает `["H0","C0"]`. По приоритету §0 действует документ; конфликт безвреден до INFRA5 (RC3 forbidden), но должен быть устранён до того, как конфиг станет входом линтеров INFRA1-002.
- **MINOR-4** — Конфиг в `config/infra/` вне буквального WO scope (`config/control/infra/**`); отклонение задокументировано со ссылкой на mission владельца, которая по Git не верифицируется. Принято (файл в allowed_paths, дублей нет); впредь — фиксировать такие указания durably.
- **NOTE-1** — `checkpoint: INFRA0` против `^NL[0-8]$` в схеме паспорта: строгое schema-несоответствие, задокументированное имплементером; практический валидатор не проверяет. Кандидат в control WO (паттерн `(NL|INFRA)[0-7]`).
- **NOTE-2** — Имя ветки `infra/infra0-execution-baseline-r1` отличается от предложенного в WO (`infra/infra0-security-control-r1`); соответствует шаблону `infra/<checkpoint>-<slug>-rN` из PROJECT_CONTROL; WO формулировал ветку как «предлагаемую». Замечаний нет.
- **NOTE-3** — Опечатки/гигиена текста: §7.2 «эphemeral» (смешанные алфавиты), §7.3 «chekpoints», §6.5 «`…= 1`);trusted» без пробела. Не влияют на смысл.

## Claim ceiling

`C0_SOFTWARE_ONLY` (подтверждён): baseline — software/policy-документ и машинно-читаемая проекция; научных утверждений не содержит, scientific claim не создаёт и не повышает (`E0–E6 NOT_RUN`; научный frontier не затронут — `project/state.json` не изменён). Вердикт относится к baseline как к PROPOSED-политике на exact HEAD `9427ff1`; он не объявляет capability принятой и не заменяет Director checkpoint, Human merge gate и последующие механические контролы INFRA1-002/INFRA2-002. Фактическое существование/безопасность будущих runner'ов этим вердиктом не утверждается.

## Next action (одно)

Независимый VERIFIER: fresh checkout exact `9427ff1c081d20d87a418fec2757916d6ecca859`, воспроизвести команды раздела «Независимые валидации» и сверить trees/subject_sha/allowed_paths, выставить вердикт рядом (VERIFIER_VERDICT) с проверкой claim ceiling; затем Director checkpoint proposal INFRA0 (с явным решением по MINOR-1), merge — Human Gate, обновление `project/infra-state.json` — только после принятого merge. MINOR-2/3 и NOTE-1/3 — исправляющим коммитом или в `EXECUTION-BASELINE-R2`.
