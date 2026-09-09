# Re-Review Addendum R1 — INFRA1-002 (проверка ремонта по REVIEWER_VERDICT R1)

**Роль:** независимый FRESH REVIEWER (тот же метод, контекст имплементёра недоступен).
**Дата:** 2026-09-09. **Вердикт по ремонту:** `PASS` — ремонт R1 принят. Все директивы вердикта R1 (§4) исполнены и подтверждены исполнением; новые findings: MINOR-4 (не блокирует приёмку ремонта, обязательный follow-up) + NOTE-5. Основной вердикт R1 (`FIX_REQUIRED`, `1ca40b6`) считается отработанным.
**Субъект:** substantive ремонтного раунда `74e17c734d600b74e9d25209ab8f609c3ca40244`, tip `5c2e1b2` (events 0005/0006), ветка `infra/infra1-validation-gates-r1`. База диффа ремонта: `0330d15b8af4858596664ed25a9317843c8389df` (subject раунда 1). Вердикт R1 влит merge-коммитом `a6aba22`.
**Метод:** собственный detached-worktree @ `74e17c7` + временный @ `5c2e1b2`;fixtures раунда 1 воспроизведены 1:1 (`REVIEW_LOG_R1.md` §2–§3) плюс 8 дополнительных проб; все прогоны локальные (Python 3.11.8, stdlib-only).

---

## 1. Scope ремонтного диффа `0330d15..74e17c7`

14 файлов: `workflow_lint.py` (+67), `work_cli.py` (+51), оба тест-файла (+134/+152 net), `validation-gates.v1.json` (+29), `VALIDATION_GATES_R1.md` (обновлён, revision и статус не тронуты), `EX-INFRA1-002-R1/**` (events 0002–0004, summary, passport → `HANDOFF_READY` — только статус), а также **влитые вердикты раунда 1** (`REVIEWER_VERDICT.md`, `REVIEW_LOG_R1.md` — авторство reviewer, прецедент INFRA1-001) и **`docs/infra/evidence/INFRA1-002/REPAIR_MAP_R1.md`**. State/science/чужие EX-* — не тронуты; tip добавляет только events 0005/0006 своего execution.

**Оговорка про REPAIR_MAP-путь проверена:** `docs/infra/evidence/INFRA1-002/` вне исходных `allowed_paths` паспорта; отклонение durably задокументировано имплементёром в event `0005-repair-completed` («путь задан директивой ремонта; вне исходных allowed_paths — авторизовано миссией/вердиктом §4.5, история событий не переписывалась»). Размещение Repair Map в evidence-каталоге соответствует протоколу (`AGENTS.md` §10: FIX_REQUIRED исправляется с Repair Map; evidence map — review unit). Принято, нарушением не считается.

## 2. Негативная матрица `REVIEW_LOG_R1` §2–§3 — исполнение проверено

### §2 Линт (обе стороны, exit-коды)

| Проба | Было (R1) | Стало (74e17c7) | Ожидание | Итог |
|---|---|---|---|---|
| Позитив: реальный `hosted-ci.yml` | exit 0 | exit 0, 0 violations | exit 0 | ✅ |
| `runs-on: nanolab-cpu` | exit 1 `NC1_SELF_HOSTED_LABEL` | exit 1 `NC1_SELF_HOSTED_LABEL` | exit 1 | ✅ |
| `runs-on: self-hosted` | exit 1 `NC1_SELF_HOSTED_LABEL` | exit 1 `NC1_SELF_HOSTED_LABEL` | exit 1 | ✅ |
| `probe-alias-valid` (`&cpu`/`*cpu`, обход MAJOR-2) | **exit 0** | **exit 1 `WORKFLOW_UNPARSEABLE`** | exit 1 | ✅ закрыт |
| `probe-on-list` (`on: [push, pull_request_target]`, обход MAJOR-1) | **exit 0** | **exit 1 `NC2_TRIGGERS_UNSUPPORTED_FORM`** | exit 1 | ✅ закрыт |
| `probe-on-scalar` (`on: push`, обход MAJOR-1) | **exit 0** | **exit 1 `NC2_TRIGGERS_UNSUPPORTED_FORM`** | exit 1 | ✅ закрыт |
| `probe-secrets-bracket2` (`secrets['X']`, обход MINOR-1) | **exit 0** | **exit 1 `NC7_SECRETS_REFERENCE`** | exit 1 | ✅ закрыт |
| `probe-multidoc` | exit 1 (слияние док-ов) | exit 1 `WORKFLOW_UNPARSEABLE` (explicit rejection второго `---`) | exit 1 | ✅ |
| `probe-tabs` (исходная фикстура R1: TAB под `on:`) | exit 1 (по NOTE3) | **exit 0** — см. MINOR-4 | exit 1 | ⚠️ расхождение |

Доп. пробы (сверх матрицы): `on:` отсутствует → exit 1 `NC2_TRIGGERS_BLOCK_MISSING` ✅; push-only mapping → exit 0 (NOTE-1 закрыт) ✅; bare `pull_request:` (null types) → exit 1 `NOTE3_PR_TYPES_READY_FOR_REVIEW` ✅; TAB под job-ключом (фикстура ремонта) → exit 1 `WORKFLOW_UNPARSEABLE` ✅; `&&`/`echo "---"` внутри `run: |` block scalar → позитив проходит, shell-конструкции не задеты ✅; `runs-on: [*a, ubuntu-latest]` (alias в flow) → exit 1 unparseable ✅.

### §3 Corrections-aware валидатор

| Проба | Было (R1) | Стало (74e17c7) | Итог |
|---|---|---|---|
| 10/10 `EX-*` validate | 10/10 OK | **10/10 OK** (легаси-whitelist работают, blocking-критерий (b) сохранён) | ✅ |
| Базовый валидатор (`15a2c9b`) на `EX-NL1-002-R1` | exit 3, ровно 5 residual | exit 3, ровно 5 residual (воспроизведено) | ✅ |
| Unmarked post-terminal (`VALIDATION_RECORDED` / `REPAIR_COMPLETED`) | FAIL | FAIL (`must be review-corrections events`) | ✅ без регрессии |
| Второй terminal после corrections; `REVIEW_CORRECTIONS` до handoff | FAIL | FAIL | ✅ |
| `REVIEW_CORRECTIONS` ts 2020 < handoff 2026 (новое) | **OK (дыра)** | **exit 3** `corrections event timestamp must be >= terminal event timestamp` | ✅ закрыто |
| `CONTINUATION_CHECKPOINT` ts < terminal (новое, вне whitelist) | OK | exit 3 | ✅ |
| `REVIEW_CORRECTIONS` от `IMPLEMENTER` | **OK (дыра)** | **exit 3** `must be authored by REVIEWER, VERIFIER or DIRECTOR` | ✅ закрыто |
| `REVIEW_CORRECTIONS` от `REVIEWER`, ts ≥ terminal | — | OK (легитимный путь сохранён) | ✅ |
| Новое событие 7-hex `abc1234` | **OK (дыра)** | **exit 3** `invalid subject_sha (full 40-hex required…)` | ✅ закрыто |
| 39-hex у нового события | OK | exit 3 | ✅ |
| Переиспользование значения `9cc83e8` в другом execution | OK | exit 3 | ✅ |
| Переиспользование легаси-пары `(EX-NL1-002-R1, 0002-…)` в другом execution | OK | exit 3 | ✅ |
| Обычный поток 40-hex, terminal-last | OK | OK | ✅ |
| Tip `5c2e1b2`: собственный `EX-INFRA1-002-R1` (events 0005/0006 — пост-терминальные `CONTINUATION_CHECKPOINT`, ts > handoff, полные SHA) | — | `ok: true` — догфудинг repaired-валидатора | ✅ |

Итог: **18/18 матричных исходов по существу подтверждены** (17 — дословно фиксчурами раунда 1; 18-й — `probe-tabs` — исходом «exit 1» подтверждается для job-уровня размещения таба (фикстура ремонта), но не для исходной фикстуры раунда 1 — см. MINOR-4), плюс 8/8 дополнительных проб.

## 3. MINOR-2: whitelist abbreviated-SHA — независимая сверка

- Независимый скан всех `docs/work/executions/EX-*/events/*.json`: сокращённые SHA — **ровно 4** события, все `EX-NL1-002-R1` (0002–0005), все со значением `9cc83e8`; других сокращённых/невалидных нет; легаси-событий типа `REVIEW_CORRECTIONS` нет (роль-ограничение grandfathering'а не требует — подтверждено). Harvest-claim REPAIR_MAP/config (`legacy_harvest_provenance`, canonical `a4533ab`) согласуется с фактом.
- Whitelist точный по паре `(execution_id, event_id)`: и значение, и пара в чужом execution → FAIL (пробы 10/11). Все новые события → строго 40-hex; `subject_sha_pattern` в конфиге возвращён к `^[0-9a-f]{40}$` с явным whitelist'ом и provenance. Легаси-каталог остаётся OK (10/10) — blocking-критерий (b) не деградировал.

## 4. MINOR-3: семантика corrections — исполнена

ts ≥ terminal для всех новых corrections-событий (`LEGACY_TIMESTAMP_EXEMPT_CORRECTIONS` — 4 легаси-события, из них фактически нарушало только `EX-NL1-002-R1`/0005; сверено), роль `REVIEW_CORRECTIONS` = `REVIEWER/VERIFIER/DIRECTOR` (IMPLEMENTER → hard error), легитимный corrections-путь REVIEWER+ts≥terminal сохранён. Конфиг-блок `corrections_semantic_requirements` синхронизирован.

## 5. Пять чеков на ремонтном HEAD (воспроизведено)

JSON-syntax **111/111 OK**; `check-consistency` exit 0; `work_cli validate` **10/10 EX-* OK**; `workflow_lint --root .` — 0 violations, exit 0; `unittest discover` — **Ran 59 tests, OK** (34 → 59: +25 тестов на новые правила, включая обязательные негативы MAJOR-1/MAJOR-2/MINOR-1/MINOR-2/MINOR-3, NOTE-1/NOTE-3-fixes и multi-doc rejection). Тест-классы соответствуют REPAIR_MAP (`MAJOR1TriggerFormTests`, `MAJOR2AnchorAliasTests`, `MINOR1SecretsBracketTests`, `SubjectShaLegacyScopeTests`, `CorrectionsTimestampVsTerminalTests`, `ReviewCorrectionsRoleTests`, `NOTE1TriggerGuardTests`, `MultiDocumentTests`).

## 6. Новые findings

### MINOR-4 — таб-чек парсера — dead code; «tabs → fail closed» выполняется не для всех размещений (follow-up обязателен)
В `_content_lines` проверка `"\t" in stripped_comment[:indent]` **никогда не срабатывает**: `indent` — число ведущих ПРОБЕЛОВ (`lstrip(" ")`), срез `[:indent]` состоит только из них; строка, начинающаяся с TAB, даёт `indent=0` и пустой срез. Следствия (воспроизведено): TAB-индентация под `on:` молча перестраивает документ (моя исходная фикстура `probe-tabs` R1: было exit 1 — и то по NOTE3-перестраховке, не по таб-чеку; стало exit 0); TAB под job-ключом даёт `WORKFLOW_UNPARSEABLE` (заявленный REPAIR_MAP исход — верен для их размещения фикстуры). Направление fail-safe: GitHub отвергает TAB-индентацию как невалидный YAML целиком, поэтому обойти NC-1/NC-2 табами нельзя (файл не исполнится); риск — точность fail-closed-заявки линта и расхождение матричной строки «probe-tabs → WORKFLOW_UNPARSEABLE» с исходной фикстурой раунда 1. Также поправляю собственную строку `REVIEW_LOG_R1` §2 (таб: «exit 1, unparseable» — неточно: exit 1 давал NOTE3). **Ремонт (малый):** отклонять TAB в ведущем whitespace сырой строки (например, regex `^[ ]*\t`) → `WorkflowParseError`; + негативные тесты обоих размещений. Срок: следующая ревизия линта / контрольный WO, **до INFRA2-001** (NC-1 — защитник label-namespace при активации self-hosted).

### NOTE-5 — schema-невалидные формы (`jobs:` не-mapping/отсутствует) пропускают job-правила
`lint_document` проверяет jobs только при `isinstance(jobs, dict)`; список/null → job-чеки молча пропущены. Тот же класс «fail-safe, т.к. GitHub отвергает такой файл», что MINOR-4; кандидат в тот же пакет «fail-closed на schema-невалидных формах» (`on:` уже закрыт MAJOR-1-ремонтом).

## 7. Вердикт

**PASS по ремонту R1.** MAJOR-1, MAJOR-2, MINOR-1, MINOR-2, MINOR-3 закрыты и подтверждены исполнением; NOTE-1/NOTE-3(парсер)/NOTE-2 закрыты сверх директивы; NOTE-4 (schema sync) — законно отложен в control WO; doc/config обновлены фиксацией находок без переписывания истории; scope чист, оговорка REPAIR_MAP-пути durably задокументирована; собственный execution ремонтного раунда успешно проходит repaired-валидатор (догфудинг). Новый MINOR-4 (+NOTE-5) не подрывает ни один закрытый обход (табы не дают исполняемого файла на GitHub) и не блокирует приёмку ремонта, но обязателен к фиксации в следующей ревизии линта до INFRA2-001.

Дальше: Verifier на exact substantive `74e17c734d600b74e9d25209ab8f609c3ca40244` → Director checkpoint `INFRA1-002` → Human Gate merge. Не смержить до Director-решения.

**Exact HEADs:** substantive ремонта `74e17c734d600b74e9d25209ab8f609c3ca40244`; tip `5c2e1b2`; этот аддендум — ветка `review/infra1-validation-gates-r1` (см. git log).
