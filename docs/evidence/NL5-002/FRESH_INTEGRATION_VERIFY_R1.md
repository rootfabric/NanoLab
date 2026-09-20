# FRESH_INTEGRATION_VERIFY_R1 — NL5-002 (независимая fresh tooling/integration-head верификация integration/nl5-002-r1 после bounded tooling repair)

Verify id: `NL5-002/FRESH_INTEGRATION_VERIFY_R1`
Дата verify (UTC): 2026-09-20
Verifier: fresh independent Verifier (отдельная сессия; implementer repair'а, scientific-verify, review и предыдущие verifier-сессии этой цепочки не выполнял, их вердикты не наследовались)

Subject: integration-ветка `integration/nl5-002-r1` (PR #43) после bounded tooling repair (два коммита: `616ecea` "work_cli external execution profile" и `932481e` "batch-timestamp repeats check reaches external profile", слитые в `4c67e21`). Проверяется ТОЛЬКО tooling/integration-поверхность: canonical gates, tooling-дельта против инвариантов external execution profile, negative controls валидатора, валидность всех опубликованных `EX-*`.

```
VERIFY_VERDICT = PASS
VERIFIED_INTEGRATION_HEAD = 4c67e211f0db78c90366d32f643de92089ed190c
VERIFIED_TREE = 641c9cc71545b0bafda039ee0c37c437a638d117
HOSTED_CI = 35480129676 SUCCESS (run на PR #43 head 4c67e21; сверено Director через GitHub API при подготовке верификации)
UNIT_TESTS = 369 tests, OK (exit 0)
CHECK_CONSISTENCY = PASS
WORKFLOW_LINT = PASS
EXTERNAL_PROFILE_POSITIVE = PASS
NEGATIVE_CONTROLS = PASS
STANDARD_PROFILE_REGRESSION = PASS
```

## 1. Independence statement

- Verifier — fresh-сессия. Все факты ниже получены самостоятельно: живой `git fetch origin`, собственный worktree, собственные запуски gates/валидатора, negative controls — на одноразовых копиях в `/tmp/nc-*/` (в Git не коммитились, после проверки оставлены в `/tmp`).
- Научный Fresh Verifier PASS @ `4116468` (merge `1935907`) — чужой вердикт: он НЕ проверялся, НЕ пересчитывался и не является результатом этой верификации. Здесь проверяется только tooling-состояние integration HEAD.
- Репозиторий и существующие worktrees (`main`, `integration-nl5-002`, `nl5-002-decision`, …) не изменялись. Работа велась в собственном worktree `/home/rdpuser/NanoLab/verify-nl5-002-integration`.

## 2. Subject binding (exact-head checkout)

Команды: `git --git-dir=/home/rdpuser/NanoLab/.git-store/repo.git fetch origin`; `worktree add --detach …/verify-nl5-002-integration 4c67e211…`; в worktree: `git fetch origin`, `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, `git rev-parse origin/integration/nl5-002-r1`, `git status --porcelain`.

| Проверка | Факт | Ожидание | Исход |
|---|---|---|---|
| `git rev-parse HEAD` | `4c67e211f0db78c90366d32f643de92089ed190c` | `4c67e211f0db78c90366d32f643de92089ed190c` | **match** |
| `git rev-parse HEAD^{tree}` | `641c9cc71545b0bafda039ee0c37c437a638d117` | зафиксирован | — |
| `git rev-parse origin/integration/nl5-002-r1` | `4c67e211f0db78c90366d32f643de92089ed190c` | тот же SHA | **match** |
| `git status --porcelain` | пусто | пусто | **match** |
| `origin/main` | `48c55b3c4acdd2264527083e3072757be8bd9ada` | canonical main | **match** |
| repair-коммиты в lineage | `git merge-base --is-ancestor 616ecea…` → ok; `…932481e…` → ok | оба предки HEAD | **match** |

Subject drift: NONE.

## 3. Canonical gates (фактические результаты)

| Gate | Команда (в корне verify-worktree) | Фактический результат | Exit code |
|---|---|---|---|
| Unit tests | `python3 -m unittest discover -s tests -t .` | `Ran 369 tests in 11.443s` / `OK` | 0 |
| Check-consistency | `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | `ok: true`, `errors: []`, warnings: `["git metadata unavailable"]`; `head`/`tree` в выводе = `4c67e21…`/`641c9cc7…`; counts: stages 9, tasks 19, experiments 7 | 0 |
| Workflow lint | `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | `ok: true`, workflows 1 (`hosted-ci.yml`), `violations: 0`, **`blocking: 0`** | 0 |

## 4. Review tooling-дельты — 7 инвариантов external execution profile

Дельта: `git diff 33935ae..4c67e21` — ровно 3 файла: `config/control/harness/work-event.schema.v1.json` (+2/−2), `scripts/harness/work_cli.py` (+55/−4), `tests/test_work_cli_external_profile.py` (новый, +165). Номера строк — по итоговому `scripts/harness/work_cli.py` @ `4c67e21`.

### Инвариант 1 — opener ровно один, первый лексически — ПОДТВЕРЖДЁН

- Строка 136: `event_files = sorted(events_dir.glob("*.json"))` — события читаются в лексическом порядке файлов.
- Строка 203: `is_external_profile = bool(event_types) and event_types[0] == EXTERNAL_OPENER` — профиль открывается РОВНО первым лексически event'ом; `EXTERNAL_EXECUTOR_DISPATCHED` на любой другой позиции профиль не открывает (fail-closed: тогда директория остаётся standard, где этот тип unsupported, см. инвариант 5).
- Строки 214–215: `if event_types.count(EXTERNAL_OPENER) != 1: errors.append("external execution profile requires exactly one EXTERNAL_EXECUTOR_DISPATCHED opener")` — count != 1 → error.

### Инвариант 2 — terminal ровно один — ПОДТВЕРЖДЁН

- Строки 216–217: `if event_types.count(EXTERNAL_TERMINAL) != 1: errors.append("external execution profile requires exactly one EXTERNAL_RUN_COMPLETED terminal event")` — и 0, и ≥2 терминалов дают error. Подтверждено negative control'ом NC-EXT-2 (второй terminal с корректным id/порядком падает именно с этим сообщением, других ошибок нет).

### Инвариант 3 — CONTINUATION append-only; post-terminal errata; mutation-защита — ПОДТВЕРЖДЁН (с одной оговоркой)

- Строки 27, 229: `CONTINUATION` — член `EXTERNAL_ALLOWED_EVENTS`; `has_post_terminal_corrections = terminal_idx >= 0 and any(item == "CONTINUATION" for item in event_types[terminal_idx + 1:])` — post-terminal `CONTINUATION` (записи прогресса/errata) — предусмотренная форма, маркер уже поднят на опубликованной EX-NL5-002-B-R2 (`0005-timestamp-errata` после terminal `0004`).
- Произвольная substantive mutation старых events механически ломает integrity-инварианты, проверяемые ДО ветвления профиля (строки 143–199, одинаково для обоих профилей):
  - required fields: `event_id, event_type, execution_id, work_order_id, actor_role, subject_sha, summary` (строки 143, 149–151);
  - event_id/filename binding: `path.stem != event.get("event_id")` → error (152–153);
  - execution_id/work_order_id binding к паспорту (154–157);
  - subject_sha строго 40-hex (кроме exact whitelisted legacy-пар) (158–161);
  - timestamp присутствует/парсится/не placeholder (165–172);
  - lexical order: `ids != sorted(ids)` (174–175);
  - duplicate event_id (176–177);
  - batch-timestamp repeats ≥3 (185–199).
  Подтверждено экспериментально: NC-EXT-5b1…b6 (удаление `summary`, event_id≠filename, execution_id-mismatch, дубликат id, сломанный порядок, не-40-hex subject_sha) — каждая мутация даёт FAIL с точной ошибкой.
- Оговорка (честно): механические проверки work_cli не детектируют правку свободного текста `summary` внутри иного структурно валидного события — этот класс мутаций держит git-иммутабельность опубликованных событий + append-only дисциплина (corrections только новым event), а не сам валидатор. В перечисленные инвариантом классы мутаций (id/binding/порядок/поля/hashes) валидатор fail-closed.

### Инвариант 4 — ORCHESTRATOR только в external profile — ПОДТВЕРЖДЁН

- Строка 17: `ALLOWED_ROLES = {"IMPLEMENTER", "SCIENTIFIC_OPERATOR", "REVIEWER", "VERIFIER", "DIRECTOR"}` — ORCHESTRATOR в standard-наборе отсутствует.
- Строка 28: `EXTERNAL_ALLOWED_ROLES = {"ORCHESTRATOR"}`; строки 204–205, 209–211: набор ролей выбирается профилем, проверка по каждому event.
- Подтверждено тестом `test_orchestrator_in_standard_directory_fails` и NC-EXT-4 (ORCHESTRATOR в standard C-R1 → `unsupported actor_role`, exit 3).

### Инвариант 5 — standard profile не ослаблен — ПОДТВЕРЖДЁН

- Прежние standard-правила сохранены без изменений: `WORK_ORDER_STARTED` первым (233–234) и ровно один (235–236); не более одного terminal/handoff (237–239); после terminal — только corrections-класс `CONTINUATION_CHECKPOINT`/`REVIEW_CORRECTIONS` (245–257); `REVIEW_CORRECTIONS` только после terminal и только от REVIEWER/VERIFIER/DIRECTOR (258–262); монотонность/не-раньше-terminal для corrections-timestamps с legacy-whitelist (263–277).
- External-словарь в standard отклоняется: `CONTINUATION`, `EXTERNAL_EXECUTOR_DISPATCHED`, `EXTERNAL_RUN_COMPLETED` ∉ `ALLOWED_EVENTS` (строка 16) → `unsupported event_type` (206–208). Подтверждено NC-EXT-3 и тестом `test_external_vocabulary_in_standard_directory_fails`. (Легаси-`CONTINUATION_CHECKPOINT` в standard остаётся допустимым corrections-типом — это другой тип, не external-словарь.)
- Перенос per-event role/type проверок (раньше внутри per-file-цикла, теперь строки 206–211 после batch-timestamp repeats check) не меняет исход: все проверки накапливают ошибки в один список без short-circuit, `ok = not errors`; порядок проверок на множество ошибок и итог не влияет. Эмпирически: старый валидатор (`work_cli.py` @ `33935ae`, извлечён `git show`) vs новый на всех 42 `EX-*` — для всех 40 standard-директорий вердикт и sorted error-множество ИДЕНТИЧНЫ; изменились ровно EX-NL5-002-B-R1/B-R2 (FAIL→PASS — целевой scope repair'а, fix hosted-ci Check 3).

### Инвариант 6 — schema не permissive-anything; ceiling-дисциплина — ПОДТВЕРЖДЁН

- `work-event.schema.v1.json`: `event_type.enum` расширен ровно тремя типами — `EXTERNAL_EXECUTOR_DISPATCHED`, `CONTINUATION`, `EXTERNAL_RUN_COMPLETED` (итого 15); `actor_role.enum` расширен ровно одним значением — `ORCHESTRATOR` (итого 6). Никакие прочие ограничения схемы не ослаблены (pattern `subject_sha` `^[0-9a-f]{40}$` и legacy-оговорка без изменений).
- Ceiling-описание в самой схеме: описание `event_type` фиксирует, что external-профиль "enforced by scripts/harness/work_cli.py with ORCHESTRATOR as the only actor role, exactly one dispatch opener and exactly one EXTERNAL_RUN_COMPLETED terminal"; описание `actor_role`: "ORCHESTRATOR is reserved for external executor campaigns (external execution profile)". Иерархия «схема — ceiling, work_cli — enforcement floor» задокументирована в `config/control/harness/README.md` (раздел «Иерархия: схема (ceiling) и валидатор (floor)»). Наблюдение: сам README новых external-типов/ORCHESTRATOR поимённо не упоминает — авторитетное описание профиля living в schema + work_cli (§ README это покрывает как floor); на исход верификации не влияет (инвариант требовал описание в schema, README — «если есть»).

### Инвариант 7 — per-event integrity одинакова для обоих профилей — ПОДТВЕРЖДЁН

- Все per-event проверки (required fields 143–151, filename binding 152–153, passport-binding 154–157, subject_sha 158–161, timestamps 165–172, lexical order 174–175, duplicates 176–177) и batch-timestamp repeats check (185–199, добавлен к external в `932481e`, комментарий 182–184 «Shared by BOTH profiles … runs before the external/standard branch so external executor campaigns cannot bypass it») выполняются ДО выбора профиля (строка 203). Ветвится только vocabulary/role-набор (204–211) и структурные правила (213–231 external / 233–277 standard).
- Подтверждено тестом `test_batch_timestamp_repeats_check_reaches_external_profile` и симметрией NC-EXT-5b (external) ↔ NC-STD-PARITY (standard).

## 5. Negative controls (копии в /tmp, disposable; мутировались только копии)

Команда: `PYTHONPATH=scripts python3 -m harness.work_cli validate <dir>` (exit 0 = OK, exit 3 = FAIL).

| Контроль | Мутация (на копии) | Ожидание | Фактическая ошибка валидатора | Exit | Контроль |
|---|---|---|---|---|---|
| NC-EXT-1 | B-R2: event_type первого события → `CONTINUATION`, роль ORCHESTRATOR | FAIL | `unsupported event_type` (все external-события) + `unsupported actor_role` (профиль не открыт → standard, external-словарь и роль там unsupported) | 3 | PASS |
| NC-EXT-2 | B-R2: добавлен второй `EXTERNAL_RUN_COMPLETED` (id `0006-external-run-completed-duplicate`, уникальный id/timestamp, lexical order соблюдён) | FAIL, ровно про count | `external execution profile requires exactly one EXTERNAL_RUN_COMPLETED terminal event` (единственная ошибка — падение именно из-за count) | 3 | PASS |
| NC-EXT-3 | C-R1: event_type `0002` → `CONTINUATION` | FAIL | `0002-implementation-committed.json: unsupported event_type` | 3 | PASS |
| NC-EXT-4 | C-R1: `actor_role=ORCHESTRATOR` на `0001` | FAIL | `0001-work-order-started.json: unsupported actor_role` | 3 | PASS |
| NC-EXT-5a | B-R2 как опубликована (post-terminal `0005-timestamp-errata`) | PASS (errata-форма) | ошибок нет; `has_post_terminal_corrections=true` | 0 | PASS |
| NC-EXT-5b1 | B-R2: удалено обязательное поле `summary` (event 0002) | FAIL | `0002-…: missing summary` | 3 | PASS |
| NC-EXT-5b2 | B-R2: `event_id=0002-tampered-id` в файле `0002-continuation-….json` | FAIL | `filename must equal event_id + .json` | 3 | PASS |
| NC-EXT-5b3 | B-R2: `execution_id=EX-NL5-002-B-R3-FAKE` (event 0002) | FAIL | `execution_id differs from passport` | 3 | PASS |
| NC-EXT-5b4 | B-R2: дубликат event_id (копия 0002 в файл `0006-duplicate-control.json`) | FAIL | `filename must equal event_id + .json`; `events are not lexically ordered`; `duplicate event_id` | 3 | PASS |
| NC-EXT-5b5 | B-R2: обмен event_id между 0002/0003 (сломан lexical order) | FAIL | `filename must equal event_id + .json` (×2); `events are not lexically ordered` | 3 | PASS |
| NC-EXT-5b6 | B-R2: `subject_sha=deadbeef` | FAIL | `invalid subject_sha (full 40-hex required; …)` | 3 | PASS |
| NC-STD-PARITY-1 | C-R1 (standard): удалён `summary` | FAIL (паритет с external) | `0001-work-order-started.json: missing summary` | 3 | PASS |
| NC-STD-PARITY-2 | C-R1 (standard): `subject_sha=48c55b3` (abbrev, не-legacy) | FAIL (паритет с external) | `invalid subject_sha (full 40-hex required; …)` | 3 | PASS |
| NC-STD | Нетронутые EX-NL3-002-R1, EX-NL1-002-R1, EX-INFRA1-002-R1 | PASS | ошибок нет | 0 | PASS |

Negative-control директории (`/tmp/nc-ext*`, `/tmp/nc-std*`) оставлены в `/tmp`, в Git не коммитились.

## 6. Валидация всех опубликованных EX-* (42 директории)

Цикл `for d in docs/work/executions/EX-*: work_cli validate` — **42/42 ok=True, exit 0**. Profile-детекция по содержимому: `EXTERNAL_EXECUTOR_DISPATCHED` открывает профиль (строка 203, `event_types[0]`), path-исключений в коде нет (grep по `NL5|B-R1|B-R2|dirname|startswith` — совпадений с логикой профилирования нет; профиль выбирается исключительно по events).

| Execution | ok | profile | terminal | post-terminal corrections |
|---|---|---|---|---|
| EX-NL5-002-A-R1 | true | standard_work_order | true | false |
| EX-NL5-002-B-R1 | true | **external_execution** | true | false |
| EX-NL5-002-B-R2 | true | **external_execution** | true | **true** (`0005-timestamp-errata`) |
| EX-NL5-002-C-R1 | true | standard_work_order | true | false |
| EX-NL5-002-C2-R1 | true | standard_work_order | true | false |

Остальные 37 (EX-BUS-001-R1 … EX-POST-MVP-ROUTE-R1): все ok=True, profile=standard_work_order (полный список: EX-BUS-001-R1, EX-BUS-002-R1, EX-CTRL-LINTSCHEMA-R1, EX-DIR1-R1, EX-INFRA0-001-R1, EX-INFRA1-001-R1, EX-INFRA1-002-R1, EX-NL0-001-R1, EX-NL0-002-R1, EX-NL0-002-R1-REPAIR1, EX-NL0-003-R1, EX-NL1-001-R1, EX-NL1-002-R1, EX-NL1-002-R1-REPAIR1, EX-NL2-001-R1, EX-NL2-002-R1, EX-NL2-003-R1, EX-NL3-001-R1, EX-NL3-002A-R1, EX-NL3-002-PARAM-11B-R1, EX-NL3-002-PARAM-32B-R1, EX-NL3-002-PARAM-53B-R1, EX-NL3-002-PARAM-74B-R1, EX-NL3-002-PILOT-R1, EX-NL3-002-PROTO-R1, EX-NL3-002-R1, EX-NL3-002-SUMMARY-R1, EX-NL4-001-R1, EX-NL4-002-E3-LLM-R1, EX-NL4-002-E3-MECH-R1, EX-NL4-002-E3-REVAL-R1, EX-NL4-003-R1, EX-NL5-001-A-R1, EX-NL5-001-B-R1, EX-NL5-001-B-REPAIR-R1, EX-NL5-001-C-R1, EX-NL5-001-D-R1).

## 7. Ограничения верификации (что НЕ входит)

- Этот вердикт — ТОЛЬКО tooling/integration-верификация HEAD `4c67e21` (gates, валидатор, schema-дисциплина, structural integrity events). Он НЕ пересматривает и не заменяет научный вердикт: **FRESH_VERIFY_R1 PASS @ `4116468` с MISMATCH-исходом кампании остаётся действующим научным вердиктом**; классификация/статистика/артефакты здесь не пересчитывались.
- **NL5-002 NOT accepted**; внешние научные прогоны не воспроизведены этим verifier'ом: **external_reproductions = 0**. Acceptance/ Human Gate — вне scope.
- HOSTED_CI = 35480129676 SUCCESS принят как факт, сверенный Director через GitHub API при подготовке верификации (у verifier-сессии независимого API-доступа к GitHub Actions нет; локальный `workflow_lint` blocking=0 — мой собственный результат).
- Свободно-текстовые правки `summary` в иначе валидных опубликованных событиях work_cli механически не детектирует (см. §4, инвариант 3, оговорка) — этот класс удерживает git-иммутабельность + append-only дисциплина, не валидатор.

## 8. Вердикт

Все проверки пройдены: unit tests 369 OK; check-consistency ok=true errors=[]; workflow_lint blocking=0; все 7 инвариантов external execution profile подтверждены по коду и эмпирике; все 15 negative controls дали ожидаемый исход; все 42 EX-* валидны, B-R1/B-R2 детектируются как external_execution по содержимому, standard-профиль не ослаблен (побитовая эквивалентность вердиктов на старом валидаторе для standard-директорий).

```
VERIFY_VERDICT = PASS
```
