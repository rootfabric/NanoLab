# VERIFIER VERDICT — INFRA0-001 (EXECUTION-BASELINE-R1)

**Вердикт: PASS**

- Проверяемый substantive HEAD: `9427ff1c081d20d87a418fec2757916d6ecca859`
  (subject terminal event 0004: `41cd55ca4d3bf20eac7cd8c0f6edb879825dcdfe`).
- Verifier: независимый fresh-агент, ветка `verify/infra0-execution-baseline-r1`.
- Протокол проверок: `docs/infra/evidence/INFRA0-001/VERIFIER_EVIDENCE.md` (CONTINUATION 1–2, эта ветка).
- Метод: verification исполнением — git-проверки, независимая jsonschema-валидация
  (python `jsonschema` Draft 2020-12), механическая сверка документ↔конфиг, secret-скан.

## 1. Результаты проверок

### 1.1 Scope — PASS

- `git diff --name-status 71535d0..9427ff1`: ровно 9 файлов, все additions, все в allowed_paths
  паспорта (`docs/infra/EXECUTION_BASELINE_R1.md`, `config/infra/execution-baseline.v1.json`,
  `docs/work/executions/EX-INFRA0-001-R1/**`). Изменений вне allowed_paths нет.
- `project/infra-state.json`: blob `ec0ce2725f85db1a03fbf1d201a682724297ca50` идентичен на
  base 57c1e63, main 71535d0 и HEAD — байт-идентичен main, Implementer'ом не тронут.
- `.github/workflows` отсутствует (только PR/issue-шаблоны) — workflows не добавлялись.
- Secret-скан полного диффа (AWS/GitHub/Slack/JWT/PEM/generic-шаблоны): **0 находок**.

### 1.2 jsonschema-валидация — PASS (с задокументированным отклонением)

- events 0001–0004 против `work-event.schema.v1.json`: **4/4 OK**
  (Draft202012Validator + FormatChecker).
- Паспорт против `execution-passport.schema.v1.json`: единственная ошибка —
  `checkpoint: 'INFRA0' does not match '^NL[0-8]$'`.
  Отдельная проверка отклонения: паттерн схемы покрывает только научный трек NL; значение `INFRA0`
  семантически верно (совпадает с `project/infra-state.json.frontier` и `project/infra-plan.json`);
  отклонение заранее и явно задокументировано Implementer'ом (branch-passport «Документированные
  отклонения» №1, summary, event 0001/0003); схема не модифицировалась; практический валидатор
  CONTROL_WORK паттерн checkpoint не проверяет. Остальные 11 полей паспорта валидны.
  Квалификация: неблокирующее, кандидат в отдельный control WO (расширение паттерна до
  `^(NL[0-8]|INFRA[0-7])$`).

### 1.3 Сверка baseline-документа с конфигом — PASS (1 подтверждённое текстовое расхождение, LOW)

36/36 механических контрольных точек сходятся: trust zones (3 зоны + инвариант по происхождению
кода); labels (H0 `ubuntu-latest`/`ubuntu-24.04`; `nanolab-cpu`/`nanolab-gpu`/`nanolab-hpc-*`
зарезервированы, не зарегистрированы, 3 правила labels); permissions (repo default read-only target,
per-workflow minimal, PR route `contents: read`, fork PR без secrets); RC-классы (RC0 ≤15 мин,
RC1 ≤60 мин declared, RC2 C0 budget 4 полей, RC3 G0 FORBIDDEN_UNTIL_INFRA5 + fingerprint); 5 правил
бюджетов; artifact-поля (5 provenance-полей, hosted CI артефакты не evidence, durable store INFRA4);
NC-1..NC-7 (угрозы/инварианты/механика INFRA1-002/INFRA2-002/INFRA6 совпадают).

**Подтверждено (FINDING-1, LOW):** §4 (таблица) допускает `G0` в TR-DISPATCH («`H0` или защищённый
`C0`/`G0`»), machine-readable конфиг — `["H0","C0"]`. Это реальное текстовое расхождение, но:
§4.1 сам ограничивает G0 («`C0`, позднее `G0`»); G0 NOT_REGISTERED, activation `INFRA5-001`;
RC3 FORBIDDEN_UNTIL_INFRA5; TR-DISPATCH RESERVED_NOT_ACTIVE (механика — INFRA2-002, до которого G0
физически недоступен). Инвариант trusted-зоны не ослаблен. Приоритет документ>конфиг (§0/§12) снял бы
конфликт формально, поэтому рекомендуется синхронизация строки §4 с конфигом в
`EXECUTION-BASELINE-R2` или bounded repair. Не блокирует.

### 1.4 Subject-цепочка — PASS

- `subject_sha` всех 4 событий существуют и являются коммитами: 57c1e63 (0001), 870f52e (0002, 0003),
  41cd55c (0004); таймлайн событий согласован (0004 привязан к substantive HEAD до handoff-коммита
  9427ff1, содержащего только event 0004 и статусы паспорта — как объявлено в summary).
- base 57c1e63 — предок HEAD (`merge-base --is-ancestor` → 0); создан из exact canonical main.
- Merge 41cd55c (родители f880ff6 + 71535d0) вносит в ветку **только** изменения main-коммитов
  57c1e63..71535d0 (цепочка NL1-001: evidence, WO-NL1-001, scheduler-policy, project/state.json);
  файлы ветки не тронуты, конфликтов с allowed_paths нет.

### 1.5 Отсутствие объявления принятия capability — PASS

- Baseline doc и конфиг: `status: PROPOSED`; ACCEPTED не выставлен (в конфиге упомянут только как
  non-goal `implementer_does_not_set_ACCEPTED`).
- Паспорт: `HANDOFF_READY` (статус исполнения, валидный enum; не принятие capability).
- `project/infra-state.json` не тронут (blob-идентичен main): `INFRA0 = PLANNED`,
  `INFRA0-001 = READY`, все `capabilities.* = false`. Научный `project/state.json` веткой не менялся.
- Runners/workflows/secrets: не создавались (проверено п. 1.1).

## 2. Findings (все неблокирующие)

| ID | Серьёзность | Finding | Рекомендация |
|---|---|---|---|
| FINDING-1 | LOW | §4 таблица TR-DISPATCH упоминает `C0`/`G0`; конфиг — `["H0","C0"]` | Синхронизировать в EXECUTION-BASELINE-R2 / bounded repair |
| FINDING-2 | INFO | `checkpoint: INFRA0` vs `^NL[0-8]$` в execution-passport.schema — задокументированное Implementer'ом отклонение; схема не менялась | Control WO: расширить паттерн на INFRA-трек |
| FINDING-3 | INFO | Negative test WO (untrusted PR не может выбрать self-hosted label) зафиксирован как NC-1 документально; механика — `INFRA1-002` (в R1 workflows нет — механически тестировать нечего); отклонение задокументировано | Закрыть механикой в INFRA1-002, как запланировано |

## 3. Критерии приёмки WO

| Критерий | Статус |
|---|---|
| public PR path и trusted scientific path технически различимы | ✅ TR-PR (H0-only) vs TR-DISPATCH (protected, subject+budget, fail-closed); TR-PRT/TR-WFRUN FORBIDDEN_R1; NC-1/NC-2 |
| self-hosted runner не является default PR executor | ✅ TR-PR/TR-PUSH-MAIN — только H0, `self_hosted_allowed: false`; self-hosted labels запрещены в PR routes |
| permissions/budget/artifact requirements заданы | ✅ §5–§7 + конфиг (token policy, RC0–RC3, executor contract, provenance-поля) |
| никакой scientific claim не меняется | ✅ claim C0_SOFTWARE_ONLY; state-файлы не тронуты; E0–E6 NOT_RUN |
| fresh Reviewer/Verifier проверяют control policy до INFRA1 | ✅ данный Verifier verdict (Reviewer-проход — параллельная роль review/infra0-execution-baseline-r1) |

Required outputs WO: машинно-читаемая политика ✅ (конфиг); threat validation matrix ✅ (§9);
routing contract ✅ (§4.1); negative test — задокументирован как NC-1, механика INFRA1-002
(FINDING-3, не блокирует); exact next WO ✅ (INFRA1-001 «Add hosted harness CI», конфиг §next_work_orders).

## 4. Заключение

Baseline `EXECUTION-BASELINE-R1` полон, внутренне согласован (36/36 механических сверок), scope
исполнения строго ограничен allowed_paths, evidence-цепочка (паспорт + 4 события) валидна и привязана к
проверяемым SHA, границы полномочий Implementer'а соблюдены (PROPOSED, state-файлы нетронуты,
capability не объявлена). Все findings неблокирующие.

**VERDICT: PASS.** Директору: checkpoint proposal INFRA0 допустим после независимого Reviewer-вердикта;
merge — Human Gate; обновление `project/infra-state.json` — только после принятого merge (Director gate).
FINDING-1 включить в бэклог `EXECUTION-BASELINE-R2`; FINDING-2 — в бэклог control-трека;
FINDING-3 отрабатывается планово в INFRA1-002.

Проверка действительна для substantive HEAD `9427ff1c081d20d87a418fec2757916d6ecca859`;
последующие коммиты данной verify-ветки добавляют только evidence-файлы верификации.
