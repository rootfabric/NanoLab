# Branch Passport — EX-CTRL-LINTSCHEMA-R1

- Branch: `control/lint-schema-sync-r1`
- Work Order: `CTRL-LINTSCHEMA` — пакетный контрольный WO «lint fail-closed hardening + schema sync» (файл `docs/work/WO-*.md` в canonical `main` отсутствует; авторство — Director authority: `docs/infra/evidence/INFRA1-002/DIRECTOR_ACCEPTANCE_R1.md`, «Решения по findings» + «Сводка по пакетному контрольному WO»: MINOR-4 + NOTE-5 + schema-sync — единый bounded control WO, первый пункт control-очереди, обязательный и блокирующий для старта `INFRA2-001`; прецедент отсутствия WO-файла — NOTE-2 `HOSTED_CI_R1.md`, NOTE-3 `VALIDATION_GATES_R1.md`)
- Checkpoint: `INFRA1` — follow-up пакет обязательных условий приёмки INFRA1-002 («ПРИНЯТО КАК ОБЯЗАТЕЛЬНЫЙ FOLLOW-UP», DIRECTOR_ACCEPTANCE_R1; checkpoint INFRA1 = ACCEPTED с условиями, до старта INFRA2-001)
- Base SHA: `51a479cf2b559d5a734dac0dec4d9933a13cc689` (exact canonical `main`; fetch origin, `origin/main` = local `main` = base до старта, дерево чистое)
- Created from canonical main: yes
- Risk class: `MEDIUM` (harness/tooling без scientific claim; routing по директиве миссии: один независимый REVIEWER — быстрый контрольный review)
- Claim class: `C0_SOFTWARE_ONLY`
- Allowed paths: see `passport.json` (`scripts/harness/workflow_lint.py`, `tests/test_infra_workflow_lint.py`, `config/control/harness/work-event.schema.v1.json`, `config/control/harness/execution-passport.schema.v1.json`, `config/control/harness/README.md`, `config/infra/validation-gates.v1.json`, `docs/infra/VALIDATION_GATES_R1.md`, `docs/work/executions/EX-CTRL-LINTSCHEMA-R1/**`)
- Status: `HANDOFF_READY`
- Active experiment campaigns: none (control WO; E0–E6 остаются `NOT_RUN`)
- START commit: `37a105d67e4de52663009ce2c55448fd488dc369` (pushed до substantive work)
- Implementation commits: `c67546ce2eac11ab99cd6f6f9017da4f59bf275f` (MINOR-4 + NOTE-5 lint + тесты), `9d5829126afc30078bca1a59ea40fc0dee7535c8` (schema sync + README схем), `7a631d601f9f2d5b9ed5bce45bc035aeafda472b` (gates doc/config sync)
- Substantive HEAD: `7a631d601f9f2d5b9ed5bce45bc035aeafda472b` (tree `e5b8249a765e51933aa04da82aa9a3658b32f985`; = 0004-handoff-completed.subject_sha)
- Next action: один независимый REVIEWER (контрольный WO MEDIUM) на exact substantive HEAD; затем Human Gate merge; после merge — старт INFRA2-001 разблокирован
- Blocking issue: none

## Scope (из директивы миссии / Director-вердикта)

1. **MINOR-4** (RE_REVIEW_R1 §6, верификатор V-1): таб-чек парсера `_content_lines` — dead code; довести до fail-closed: отклонять TAB в ведущем whitespace любых сырых строк (YAML запрещает таб-индентацию) → `WorkflowParseError`/`WORKFLOW_UNPARSEABLE`; негативные тесты обоих размещений (TAB под `on:` и под job-ключом).
2. **NOTE-5** (RE_REVIEW_R1 §6, верификатор V-2): `jobs:` в не-mapping форме (sequence/scalar/null) или отсутствующий — fail-closed нарушение (job-чеки не должны молча пропускаться); тест: sequence с `nanolab-cpu` → FAIL.
3. **Schema sync** (REVIEWER R1 NOTE-4, верификатор V-3 — третий INFRA-прецедент): `work-event.schema.v1.json` — enum `event_type` + `REVIEW_CORRECTIONS`, `subject_sha` строго 40-hex; `execution-passport.schema.v1.json` — паттерн `checkpoint` `^(NL[0-8]|INFRA[0-7])$`; сверка с whitelist-легаси валидатора (4 события `EX-NL1-002-R1` с 7-hex `9cc83e8` остаются невалидными по схеме — приемлемо, explicit whitelist `LEGACY_ABBREVIATED_SHA_EVENTS` в `work_cli.py` выше схемы) и документирование расхождения в README схем; все валидаторы на всех `EX-*` — 10/10 OK.
4. Полная матрица негативов линта (прежние + новые) + unittest (~70+); все 5 чеков hosted-ci локально; push.

## Вне scope (не трогать)

`project/state.json`, `project/infra-state.json`, `project/infra-plan.json`, science-файлы (`experiments/**`, `docs/evidence/**`), чужие `EX-*`, вердикты (`docs/infra/evidence/**`, `docs/evidence/**`), history rewrite, ACCEPTED-статусы.

## Документированные отклонения (для reviewer)

1. **`work_order_id: CTRL-LINTSCHEMA`** — control WO без задачи в `project/infra-plan.json` (plan-задачи ведут INFRA-трек `INFRA*`); идентификатор self-consistent с `execution_id` `EX-CTRL-LINTSCHEMA-R1` по конвенции `EX-<wo>-R<N>`. Валидатор `work_cli` требует только совпадения `work_order_id` паспорта и событий.
2. **`checkpoint: INFRA1` против исторического паттерна `^NL[0-8]$`** — тот же класс, что EX-INFRA0-001-R1/EX-INFRA1-001-R1/EX-INFRA1-002-R1 (NOTE-4, «третий INFRA-прецедент подряд»); настоящий WO сам закрывает прецедент: `execution-passport.schema.v1.json` паттерн расширяется до `^(NL[0-8]|INFRA[0-7])$`.
3. **Ветке `control/` разрешён любой slug** (`control/<slug>-rN`, PROJECT_CONTROL.md); ветка `control/lint-schema-sync-r1` отражает содержание пакета, `work_order_id` — Director-формулировку.

Правило границ: без self-hosted runner'ов, secrets, GPU, paid compute; state-файлы и science не изменяются (Director gate); merge в `main` — Human Gate.
