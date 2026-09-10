# REVIEWER VERDICT — EX-CTRL-LINTSCHEMA-R1 (independent FRESH REVIEWER)

**Work Order:** CTRL-LINTSCHEMA «lint fail-closed hardening + schema sync» (контрольный, пакетный)
**Execution:** `EX-CTRL-LINTSCHEMA-R1`, branch `control/lint-schema-sync-r1`
**Subject (substantive):** `7a631d601f9f2d5b9ed5bce45bc035aeafda472b` (tip `1d1a792` — records-only; base `51a479cf2b559d5a734dac0dec4d9933a13cc689` = canonical `main`)
**Review branch:** `review/ctrl-lintschema-r1` (worktree `C:\NanoLab\review-ctrl-lintschema`, checkout exact subject)
**Контекст имплементёра:** недоступен (fresh review); использовались только артефакты ветки и независимые пробы
**Дата вердикта:** 2026-09-09 (раунд R1)
**Ревьюер:** независимый FRESH REVIEWER, без self-acceptance-полномочий; merge в `main` — Human Gate (не выполнялся)

---

## Вердикт: **PASS**

Контрольный WO выполнен полностью и в границах: MINOR-4 доведён до настоящего fail-closed (dead code устранён, обход воспроизведён на base и устранён на subject), NOTE-5 закрывает silent-skip класса «jobs не-mapping», schema-sync точен и задокументирован, полная негативная матрица и все 5 чеков hosted-ci на subject зелёные. Findings ниже — **не блокирующие** (2 MINOR, 2 NOTE); оба MINOR — кандидаты в следующую пакетную sync-ревизию схем/тестов, а не в данный WO.

---

## 1. Scope (Check 1) — ✅

`git diff 51a479c..7a631d6 --name-status` = ровно 10 файлов, каждый — в `allowed_paths` паспорта:

| Файл | Статус |
|---|---|
| `scripts/harness/workflow_lint.py` | M |
| `tests/test_infra_workflow_lint.py` | M (+297) |
| `config/control/harness/work-event.schema.v1.json` | M |
| `config/control/harness/execution-passport.schema.v1.json` | M |
| `config/control/harness/README.md` | A |
| `config/infra/validation-gates.v1.json` | M |
| `docs/infra/VALIDATION_GATES_R1.md` | M |
| `docs/work/executions/EX-CTRL-LINTSCHEMA-R1/{passport.json, branch-passport.md, events/0001-work-order-started.json}` | A |

Blob-level проверка вне scope: `git diff 51a479c 7a631d6 -- project/ experiments/ docs/evidence/ docs/work/executions/EX-INFRA0-001-R1 EX-INFRA1-001-R1 EX-INFRA1-002-R1 EX-NL1-002-R1 …` — **пусто**; state-файлы, science и чужие `EX-*` не тронуты. Tip `1d1a792` добавляет только records самого `EX-CTRL-LINTSCHEMA-R1` (events 0002–0004, `summary.md`, статус паспорта) — кода и чужих поверхностей не касается; ревью substance выполнено на `7a631d6`.

## 2. MINOR-4: TAB в ведущем whitespace (Check 2) — ✅, dead code устранён

**Подтверждение dead code на base (воспроизведено, независимая проба).** Бинарник `51a479c:scripts/harness/workflow_lint.py` запущен на три TAB-пробы REVIEWER'а:

| Проба (TAB в leading whitespace) | Base 51a479c | Subject 7a631d6 |
|---|---|---|
| под `on:` (`\tpush:`) | exit 1, `NC2_TRIGGERS_BLOCK_MISSING` — **таб-чек не сработал** (0 сообщений), нарушение случайное, от MAJOR-1 | exit 1, `WORKFLOW_UNPARSEABLE` + «tab character in leading whitespace» |
| под job-ключом (`\truns-on:`) | exit 1, `WORKFLOW_UNPARSEABLE` («job must be a mapping») — **таб-чек не сработал** | exit 1, `WORKFLOW_UNPARSEABLE` + «tab character…» |
| top-level ключ (`\tpermissions:`) | **exit 0 — полный обход** (документ молча перестроен, линт зелёный) | exit 1, `WORKFLOW_UNPARSEABLE` + «tab character…» |

На base таб-чек не сработал **ни разу** на всех пробах (срез `stripped_comment[:indent]` из ведущих пробелов не может содержать TAB — классический dead code); на top-level размещении это давало реальный silent-bypass. На subject старый срез удалён (0 вхождений), новая проверка стоит на сырой строке до strip/comment-логики.

**Собственная матрица TAB-проб на subject (8 проб, все — ожидаемый FAIL):** под `on:`, под job-ключом, top-level ключ, step внутри job (hoist-класс), mixed space+TAB (`" \t"`), TAB перед комментарием, TAB-only «пустая» строка, TAB в теле `run: |` → каждая даёт `WORKFLOW_UNPARSEABLE` (exit 1). Позитив: TAB **внутри** скаляра-значения (`echo "a<TAB>b"`) → OK (правило не переходит границы: ведущий whitespace vs тело скаляра). CLI-сообщение содержит номер строки. **MINOR-4 закрыт.**

## 3. NOTE-5: `jobs:` non-mapping (Check 3) — ✅

Собственные пробы на subject:

| Форма `jobs:` | Результат |
|---|---|
| отсутствующий | FAIL `WORKFLOW_JOBS_BLOCK_MISSING` |
| `jobs:` (null) | FAIL `WORKFLOW_JOBS_BLOCK_MISSING` |
| `jobs:\n  - nanolab-cpu` (sequence) | FAIL `WORKFLOW_JOBS_UNSUPPORTED_FORM` |
| sequence из benign-элементов; sequence из mapping'ов | FAIL `WORKFLOW_JOBS_UNSUPPORTED_FORM` (fail-closed не зависит от содержимого) |
| `jobs: validate` (scalar) | FAIL `WORKFLOW_JOBS_UNSUPPORTED_FORM` |
| `jobs: {validate: {runs-on: nanolab-cpu, …}}` (flow-mapping) | **продолжает линтоваться**: FAIL `NC1_SELF_HOSTED_LABEL`, без `WORKFLOW_JOBS_*` |
| compliant flow-mapping | PASS |
| `runs-on: []` (пустой список) | FAIL `NC1_RUNS_ON_MISSING` (NOTE-5 family); `runs-on: [ubuntu-latest]` → PASS |

Job-уровень (NC-1/NC-6/pinning) больше не может быть молча пропущен ни одной формой `jobs:`. **NOTE-5 закрыт.**

## 4. Schema sync (Check 4) — ✅, расхождение воспроизведено и задокументировано точно

Механическая проверка мини-валидатором draft-2020-12 подмножества (type/const/enum/pattern/minLength/required/properties/additionalProperties/items — все ключевые слова схем):

1. `work-event.schema.v1.json`: `event_type` enum **==** `ALLOWED_EVENTS` валидатора (12 типов, включая `REVIEW_CORRECTIONS`); `subject_sha` = `^[0-9a-f]{40}$`.
2. `execution-passport.schema.v1.json`: `checkpoint` = `^(NL[0-8]|INFRA[0-7])$`; `base_sha` = `^[0-9a-f]{40}$`. Старый паттерн `^NL[0-8]$` отвергает `INFRA1`, новый принимает (проверено на фактическом паспорте) — sync закрыл NOTE-4-прецедент: **все** 11 паспортов `EX-*` с INFRA-checkpoint'ами теперь schema-валидны по checkpoint (см., однако, Finding F1).
3. **Воспроизведение расхождения floor/ceiling:** 4 легаси-события `EX-NL1-002-R1` (0002–0005, `subject_sha: 9cc83e8`) — **schema-невалидны ровно и только по `subject_sha`** (единственная ошибка валидации — несоответствие `^[0-9a-f]{40}$`); при этом `work_cli validate EX-NL1-002-R1` → **OK** (whitelist `LEGACY_ABBREVIATED_SHA_EVENTS` — enforcement floor выше schema-ceiling). Итог по всем `EX-*` через валидатор: **11/11 OK**.
4. **README** (`config/control/harness/README.md`) документирует расхождение точно: таблица всех 4 пар `(execution_id, event_id)` со значением `9cc83e8`, provenance (scan на `a4533ab`, 2026-09-09), иерархия «схема — потолок, валидатор — floor», явное «остаются невалидными по данной схеме — приёмлемо», запрет переиспользования легаси-значения/пары. Проверено на согласованность с фактическим кодом `work_cli` и фактическими событиями — расхождений документ→код→данные нет.
5. `config/infra/validation-gates.v1.json`: ключи `leading_tab_indentation`, `jobs_declaration_required`, `jobs_form`, `runs_on_non_empty_required` добавлены; `negative_controls.NC-1.rule_ids` дополнен `WORKFLOW_JOBS_UNSUPPORTED_FORM`/`WORKFLOW_JOBS_BLOCK_MISSING` с note. Синхронизировано с кодом.

## 5. Полная негативная матрица + unittest (Check 5) — ✅

**Собственные пробы REVIEWER'а (не тесты имплементёра): 44 негатива + 7 позитивов, все — ожидаемый исход.**

- **30 «прежних» негативов** (регрессия не введена): NC-1 ×5 (nanolab-cpu, self-hosted, префикс `nanolab-hpc-*`, динамическое `${{ }}`, отсутствующий runs-on); NC-2 ×8 (pull_request_target, workflow_run, schedule, workflow_dispatch, release, внешний reusable workflow **на job-уровне**, `on: push`, `on: [push, pull_request_target]`, отсутствующий/null `on:`); NC-4 ×2; NC-7 ×3 (`secrets.X`, `secrets['X']`, `secrets["X"]`); NC-6 ×2; pinning ×1 (`@v5`); NOTE-3 ×1; fail-closed parser ×7 (anchor, alias, merge key `<<`, multi-document, job-не-mapping, unexpected indent, `...`+контент). Каждый — FAIL с ожидаемым rule_id.
- **Новые негативы:** TAB ×7 + jobs-формы ×7 (см. §2/§3).
- **Позитивы:** compliant workflow; реальный `.github/workflows/hosted-ci.yml` → 0 нарушений; TAB внутри скаляра; `runs-on` списком; compliant jobs flow-mapping.
- Замечание к пробе NC2_EXTERNAL: `uses:` внешнего reusable workflow — **job-level** правило; на step-уровне внешнее `uses:` корректно ловится `PIN_ACTION_FULL_SHA` (обе формы блокирующие).

**unittest:** `python -m unittest discover -s tests -t .` → **Ran 102 tests, OK** (24 corrections + 78 lint; соответствует §5 VALIDATION_GATES_R1.md). Негативные тесты MINOR-4 присутствуют в тестах имплементёра для обоих требуемых размещений (под `on:` и под job-ключом) — собственные пробы подтверждают консистентность.

## 6. Все 5 чеков hosted-ci на subject (Check 6) — ✅ зелёные

| # | Чек | Результат (subject 7a631d6) |
|---|---|---|
| 1 | JSON-syntax всех tracked `*.json` | **115/115 OK**, exit 0 |
| 2 | `harness.cli check-consistency --root .` | `ok=true`, 0 errors/warnings, exit 0 |
| 3 | `harness.work_cli validate` всех `EX-*` | **11/11 OK** (10 легаси + `EX-CTRL-LINTSCHEMA-R1`), exit 0 |
| 4 | `harness.workflow_lint --root .` | `ok=true`, 1 workflow, **0 violations**, exit 0 |
| 5 | `python -m unittest discover -s tests -t .` | **Ran 102, OK**, exit 0 |

NOTE по числам миссии: «JSON 118/118» соответствует **tip** `1d1a792` (+3 JSON-события); на substantive subject — 115. «work_cli 10/10» — легаси-набор; на subject их 11 (добавлен сам `EX-CTRL-LINTSCHEMA-R1` с валидным passport+START-событием). Оба набора зелёные, противоречия нет (детали — NOTE N1).

## 7. События и паспорт (Check 7) — ✅, класс отклонения задокументирован

- **`checkpoint` в паспорте = `INFRA1`, не `CTRL`.** Паттерн `^(NL[0-8]|INFRA[0-7])$` принимает `INFRA1` (механически: мини-валидатор — passport schema-valid; старый `^NL[0-8]$` отвергал бы). Т.е. фактического отклонения «CTRL вне паттерна» **нет**: контрольный WO легитимно унаследовал checkpoint follow-up-пакета INFRA1 (обоснование — `branch-passport.md`, DIRECTOR_ACCEPTANCE_R1).
- Если в будущем control-исполнению понадобится `checkpoint: CTRL` — это будет тот же известный класс «schema-ceiling отстаёт от фактов» (как NOTE-4); кандидат в **пакетную sync-ревизию схем**: добавить `CTRL[0-9]*` (или эквивалент) в паттерн отдельной ревизией, не редактированием текущей. На момент ревью — не требуется.
- `work_order_id: CTRL-LINTSCHEMA` — вне `project/infra-plan.json` (plan ведёт INFRA-трек), self-consistent с `EX-CTRL-LINTSCHEMA-R1`; валидатор требует только согласованности passport↔events (выполняется, 11/11 OK); отклонение задокументировано имплементёром (`branch-passport.md`, «Документированные отклонения» п.1) — принято ревьюером.
- Событие `0001-work-order-started` (WORK_ORDER_STARTED, IMPLEMENTER, subject_sha 40-hex) — schema-валидно; filename==event_id, порядок, единственность START — OK (входит в 11/11).

## 8. Self-acceptance / claims (Check 8) — ✅ отсутствуют

На subject: `docs/infra/evidence/CTRL-LINTSCHEMA/` не существует (вердикт пишу только я); в `EX-CTRL-LINTSCHEMA-R1` — единственное START-событие, паспорт `IN_PROGRESS`; `VALIDATION_GATES_R1.md` остаётся `PROPOSED`. На tip — только IMPLEMENTER-records (`IMPLEMENTATION_COMMITTED`, `VALIDATION_RECORDED`, `HANDOFF_COMPLETED`); ни одного `REVIEW_RECORDED`/`REVIEW_CORRECTIONS`, ни одного ACCEPTED-статуса, `claim_class: C0_SOFTWARE_ONLY`, scientific claim'ов нет («зелёные чеки — технический факт» — сформулировано корректно). Implementer self-acceptance не производил.

---

## Findings

### F1 — MINOR (пре-существующий; кандидат в пакетную sync-ревизию схем)
Паспорта repair-исполнений `EX-NL0-002-R1-REPAIR1` и `EX-NL1-002-R1-REPAIR1` несут поля `repair_of` и `verdict_repaired`, запрещённые `execution-passport.schema.v1.json` (`additionalProperties: false`) → **оба паспорта schema-невалидны** (проверено мини-валидатором; поля существуют на base `51a479c`, данным WO не вводились и не трогались). README «Известное расхождение floor/ceiling» перечисляет только 4 легаси 7-hex события — список известных расхождений **неполон в части паспортов**. Функционального конфликта нет (механической валидации паспортов против схемы нет; `work_cli` проверяет лишь required-поля). Рекомендация: в следующую пакетную sync-ревизию схем добавить `repair_of`/`verdict_repaired` (опциональные, `type: string`, `minLength`) в passport-схему — или зафиксировать их в README как осознанное расхождение, симметрично 7-hex-кейсу.

### F2 — MINOR (документация тестов)
`VALIDATION_GATES_R1.md` §5 в перечне MINOR-4 негативов упоминает «тело `run: |`», но выделенного теста на это размещение в `tests/test_infra_workflow_lint.py` нет (класс `MINOR4TabIndentationTests`: 7 негативов других размещений + 1 позитив). Само правило кейс покрывает — независимая проба ревьюера (TAB в теле `run: |`) → `WORKFLOW_UNPARSEABLE`. Расхождение — только в формулировке списка тестов; рекомендация: добавить тест либо уточнить формулировку (следующая ревизия документа).

### N1 — NOTE (сверка чисел с миссией)
На subject: tracked `*.json` = **115** (118 — состояние tip: +3 JSON-события); `work_cli` = **11/11** (10/10 — легаси-набор до добавления `EX-CTRL-LINTSCHEMA-R1`). Существенного влияния на вердикт нет — оба набора зелёные; зафиксировано для точности записей.

### N2 — NOTE (класс «checkpoint: CTRL»)
Фактически не встречается (паспорт несёт `INFRA1`, валидный после sync). Если control-трек в будущем введёт `checkpoint: CTRL*` — расширение паттерна оформить пакетной sync-ревизией схем (как этот WO), не точечным редактированием. Прецедент процесса, созданный данным WO (sync отдельным control WO + README-документирование), для этого пригоден.

---

## Локальная верификация ревьюера (воспроизводимость)

Worktree `C:\NanoLab\review-ctrl-lintschema` @ `7a631d6`; Python 3.11.8, stdlib-only, сеть не использовалась. Прогоны: 5 чеков hosted-ci (см. §6, все exit 0); собственная probe-матрица 44+/7+ (probe-скрипт во временном каталоге вне репозитория `C:\NanoLab\.review-tmp\ctrl-lintschema\`, эфемерен; все пробы воспроизводимы по описаниям §2–§5); base-бинарник извлечён `git show 51a479c:scripts/harness/workflow_lint.py` для dead-code-воспроизведения; мини-валидатор схем — stdlib `json`+`re` (draft-2020-12 подмножество ключевых слов, покрывающее обе схемы полностью). Все числовые утверждения вердикта — из этих прогонов, не из документов имплементёра.

## Границы и следующий шаг

- Ревьюер **не мержит**; merge в `main` — Human Gate. Ветка `review/ctrl-lintschema-r1` содержит только этот вердикт.
- Findings F1/F2 не блокируют приёмку WO (вне его scope; sync-прецедент данным WO создан). Рекомендация Director'у: принять WO, включить F1 (+F2 по желанию) в следующую пакетную control-ревизию; после merge — разблокируется `INFRA2-001` (по DIRECTOR_ACCEPTANCE_R1).
- Next action: **DIRECTOR** — checkpoint-решение по `EX-CTRL-LINTSCHEMA-R1` (PASS ревьюера; Human Gate merge).
