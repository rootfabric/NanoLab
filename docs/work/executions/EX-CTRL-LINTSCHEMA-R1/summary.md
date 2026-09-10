# Summary — EX-CTRL-LINTSCHEMA-R1 (контрольный WO «lint fail-closed hardening + schema sync»)

**Ветка:** `control/lint-schema-sync-r1` · **Base:** `51a479cf2b559d5a734dac0dec4d9933a13cc689` (exact canonical main @ merge PR #29) · **Substantive HEAD:** `7a631d601f9f2d5b9ed5bce45bc035aeafda472b` (tree `e5b8249a765e51933aa04da82aa9a3658b32f985`) · **Статус:** `HANDOFF_READY` (PROPOSED; self-accept запрещён) · **Claim:** `C0_SOFTWARE_ONLY`

Постановка: Director `docs/infra/evidence/INFRA1-002/DIRECTOR_ACCEPTANCE_R1.md` — обязательный follow-up приёмки INFRA1-002 (MINOR-4 + NOTE-5 + schema-sync единым bounded control WO) и блокиратор старта `INFRA2-001`.

## Что сделано

| Коммит | Содержание |
|---|---|
| `37a105d` | START: паспорт `EX-CTRL-LINTSCHEMA-R1` + branch-passport + event `0001` (push до substantive work) |
| `c67546c` | `fix(harness)`: MINOR-4 — TAB в ведущем whitespace любой строки → `WorkflowParseError`/`WORKFLOW_UNPARSEABLE` (dead-code таб-чек удалён); NOTE-5 — `jobs:` отсутствующий/null → `WORKFLOW_JOBS_BLOCK_MISSING`, sequence/scalar → `WORKFLOW_JOBS_UNSUPPORTED_FORM`; сопутствующе: `runs-on: []` → `NC1_RUNS_ON_MISSING`; тесты 35→78 |
| `9d58291` | `fix(schema)`: enum `event_type` + `REVIEW_CORRECTIONS`; `subject_sha` строго 40-hex (описание расхождения); паспорт-паттерн `checkpoint` → `^(NL[0-8]|INFRA[0-7])$`; новый `config/control/harness/README.md` (floor/ceiling, 4 легаси-события) |
| `7a631d6` | `docs(infra)`: фиксация правил в `validation-gates.v1.json` (workflow_lint-ключи, NC-1 rule_ids) и `VALIDATION_GATES_R1.md` (§2.4 Update, §3, §5 59→102, §8.2/§8.4 закрыты); revision/статус не тронуты |
| bookkeeping | events `0002–0004`, `summary.md`, паспорт → `HANDOFF_READY` |

## Результаты по пунктам постановки

1. **MINOR-4** (RE_REVIEW_R1 §6): прежний таб-чек был dead code (`indent` — только ведущие пробелы, срез `[:indent]` не мог содержать TAB; TAB-ключ под `on:` молча перестраивал документ — проба давала exit 0). Теперь TAB в ведущем whitespace **любой** сырой строки (ключи под `on:`/job-ключом, top-level, тело `run: |`, комментарий, tab-only строка, mixed space+TAB) → fail-closed; TAB внутри скаляра-значения допустим. Негативные тесты обоих обязательных размещений — в `MINOR4TabIndentationTests`.
2. **NOTE-5**: `jobs:` не-mapping (sequence — включая обязательную пробу `jobs: [nanolab-cpu]` — scalar) или отсутствующий/null → блокирующее нарушение; job-чеки (NC-1/NC-6/pinning) не могут молча пропускаться; flow-mapping `jobs:` продолжает полноценно линтиться (позитив + негатив NC-1 внутри). Тесты — `NOTE5JobsMappingTests`.
3. **Schema sync** (третий INFRA-прецедент): `work-event.schema.v1.json` — enum + `REVIEW_CORRECTIONS`, `subject_sha` строго `^[0-9a-f]{40}$`; `execution-passport.schema.v1.json` — `checkpoint` `^(NL[0-8]|INFRA[0-7])$`. Сверка с whitelist-легаси `work_cli`: 4 события `EX-NL1-002-R1` (0002–0005, `9cc83e8`) остаются невалидными по схеме — приемлемо, explicit whitelist (`LEGACY_ABBREVIATED_SHA_EVENTS`) выше схемы; расхождение задокументировано в `config/control/harness/README.md` (схема — ceiling, валидатор — floor). После sync: **все легаси `EX-*` валидны 10/10** (whitelist работает), schema-sync каталоги не сломал.

## Локальная верификация (на `7a631d6`, Windows/Python 3.11.8, stdlib-only)

| Чек | Результат |
|---|---|
| 1/5 JSON syntax (115 файлов) | OK, 0 bad |
| 2/5 `check-consistency` | `ok=true`, errors/warnings пусто |
| 3/5 `work_cli validate` EX-* | 10/10 легаси OK + собственный каталог OK |
| 4/5 `workflow_lint --root .` | `ok=true`, 0 violations |
| 5/5 unittest | **102/102 OK** (78 lint + 24 corrections) |

CLI-пробы вне репозитория (`%TEMP%\ctrl-lintschema-probes`, прецедент REVIEW_LOG_R1 §5): TAB под `on:` — было exit 0 → **exit 1 `WORKFLOW_UNPARSEABLE`**; `jobs: [nanolab-cpu]` — **exit 1 `WORKFLOW_JOBS_UNSUPPORTED_FORM`**.

## Открытые риски / ограничения (для review)

1. NC-линт остаётся stdlib subset-парсером: всё вне подмножества — fail closed (`WORKFLOW_UNPARSEABLE`), расширение подмножества — новая ревизия (VALIDATION_GATES §8.5).
2. JSON-схемы — документационный ceiling: механической валидации events/passports против схем нет; enforcement — `work_cli` (floor). Расхождение для 4 легаси-событий — осознанное, задокументировано (README схем, description-поля).
3. `work_order_id: CTRL-LINTSCHEMA` — без plan-задачи (control WO Director authority), self-consistent с execution_id (branch-passport, отклонение 1); `checkpoint: INFRA1` легитимизирован собственным sync паттерна.
4. Конфиг `validation-gates.v1.json`/док — content-update без смены revision `VALIDATION-GATES-R1` (прецедент repair R1: «revision и статус не тронуты»).

## Next action (один)

Один независимый REVIEWER (контрольный WO MEDIUM — одного REVIEWER достаточно) на exact substantive HEAD `7a631d601f9f2d5b9ed5bce45bc035aeafda472b`; затем Human Gate merge в `main`; после merge — старт `INFRA2-001` разблокирован.
