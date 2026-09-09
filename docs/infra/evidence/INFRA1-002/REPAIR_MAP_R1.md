# Repair Map R1 — INFRA1-002 (по вердикту REVIEWER `FIX_REQUIRED`)

**Основание:** [`REVIEWER_VERDICT.md`](REVIEWER_VERDICT.md) (FIX_REQUIRED, `1ca40b6`) + [`REVIEW_LOG_R1.md`](REVIEW_LOG_R1.md) §2–§3; вердикт влит merge-коммитом в ветку ремонта.
**Субъект review:** substantive `0330d15b8af4858596664ed25a9317843c8389df`, tip `97ac978` (раунд 1).
**Ветка ремонта:** `infra/infra1-validation-gates-r1` (та же); merge вердикта: `a6aba22`.
**Метод ремонта:** точечный, без пересмотра архитектуры (вердикт §4); пробы reviewer'а воспроизведены 1:1 (`probe-*` формы во временном каталоге, вне репозитория — тем же методом, что у reviewer'а).

## R→Fix карта

| Finding | Директива ремонта | Реализация | Тесты/пробы |
|---|---|---|---|
| **MAJOR-1** — `on:` scalar/flow-форма и отсутствие `on:` выводили триггеры из-под линта (`on: [push, pull_request_target]` → exit 0) | non-dict `on:` → fail-closed либо проверка элементов; + правило «`on:` обязан присутствовать» | `workflow_lint.py`: ветка триггеров переписана — `on:` отсутствует/null → **`NC2_TRIGGERS_BLOCK_MISSING`**; `on:` не-mapping (scalar/flow/прочее) → **`NC2_TRIGGERS_UNSUPPORTED_FORM`** (fail closed; проверка элементов списка сознательно не делается — форма вне поддерживаемого подмножества); NC-2/NC-7/NOTE-3 правила выполняются только внутри mapping-ветки, которая теперь единственная допустимая | unittest: `MAJOR1TriggerFormTests` ×4 (flow с forbidden-триггером, scalar, missing, null); матрица: `probe-on-list`, `probe-on-scalar` — были exit 0 → **exit 1** |
| **MAJOR-2** — anchors/aliases в `runs-on` (`&cpu` / `*cpu`) молча проходили | `&`/`*`-токены в `runs-on` или любых разобранных скалярах → fail-closed | `workflow_lint.py`: rejection на уровне парсера — plain scalar, начинающийся с `&`/`*` (anchor/alias), и mapping-key `&anchor`/`*alias`/merge key `<<` → `WorkflowParseError` → **`WORKFLOW_UNPARSEABLE`** (блокирующее; покрывает ВСЕ поля, не только `runs-on`; GitHub резолвит anchors, поэтому fail-closed корректнее выборочной проверки); `&`/`*` внутри quoted scalars и внутри `run: \|` block scalars не трогаются (shell `&&`, globs) | unittest: `MAJOR2AnchorAliasTests` ×5 (anchor+alias в runs-on, alias, anchor в другом поле, merge key, `&&`-в-run-скрипте позитив); матрица: `probe-alias-valid` (оба job'а reviewer'а) — был exit 0 → **exit 1** |
| **MINOR-1** — `secrets['X']` bracket-форма не ловилась | добавить bracket-альтернативу в regex; env-индирекцию принять и задокументировать | `workflow_lint.py`: `SECRETS_REFERENCE = \bsecrets\s*(?:\.[A-Za-z_]\w*|\[)` — покрывает dot и bracket (одиночные/двойные кавычки); env-индирекция задокументирована как принятое ограничение (док §3 + конфиг `documented_non_lintable`) | unittest: `MINOR1SecretsBracketTests` ×3 (single-quote, double-quote, dot-форма регресс); матрица: `probe-secrets-bracket2` — был exit 0 → **exit 1** |
| **MINOR-2** — tolerance `subject_sha` 7..40 применён ко всем событиям | ограничить tolerance легаси («whitelist значений из EX-NL1-002-R1», директива ремонта этого же WO) | `work_cli.py`: subject_sha — **строго 40-hex** для всех; abbreviated 7–39 hex только для exact-пары `(execution_id, event_id)` из `LEGACY_ABBREVIATED_SHA_EVENTS` (4 события `EX-NL1-002-R1`, все `9cc83e8`; harvest — полный скан `EX-*/events/*.json` canonical `a4533ab`, других сокращённых SHA нет); переиспользование значения/пар-и-event_id в другом исполнении — FAIL; конфиг: `subject_sha_pattern = ^[0-9a-f]{40}$` + явный whitelist с provenance | unittest: `SubjectShaLegacyScopeTests` ×5 (произвольный 7-hex, 8–39-hex, легаси-пара OK, легаси-значение в другом исполнении FAIL, легаси-event_id в другом исполнении FAIL); матрица: новое событие с `abc1234` — было OK → **exit 3** |
| **MINOR-3** — рыхлая семантика corrections (role/timestamp-vs-handoff) | corrections timestamp ≥ terminal; `REVIEW_CORRECTIONS` роль-ограничение (не IMPLEMENTER) | `work_cli.py`: (a) **`corrections timestamp must be >= terminal event timestamp`** для всех новых corrections-событий; `LEGACY_TIMESTAMP_EXEMPT_CORRECTIONS` — 4 пре-существующих пост-терминальных события canonical main (фактически требование нарушало только `EX-NL1-002-R1`/0005: 11:16:30Z < 11:30:00Z; EX-INFRA0-001-R1/0005 = 11:27:06 ≥ 10:28:20 и EX-NL1-001-R1/0005 = 09:40 ≥ 08:20 соответствовали и внесены для полноты); (b) **`REVIEW_CORRECTIONS` authored только REVIEWER/VERIFIER/DIRECTOR**, от IMPLEMENTER — hard error (легаси-событий типа REVIEW_CORRECTIONS в canonical main нет — grandfathering не требуется) | unittest: `CorrectionsTimestampVsTerminalTests` ×4 + `ReviewCorrectionsRoleTests` ×2; матрица: ts-2020-проба и IMPLEMENTER-проба — было OK → **exit 3**; EX-NL1-002-R1 остаётся OK (10/10) |
| **NOTE-1** — NOTE-3-правило ложно срабатывало на push-only workflow | уточнить формулировку (вердикт §3; в директиве ремонта не входит — выполнено как рекомендованный точечный фикс) | `workflow_lint.py`: правило `NOTE3_PR_TYPES_READY_FOR_REVIEW` применяется только при наличии `pull_request` в `on:`-mapping; bare `pull_request:` (null → GitHub default types без ready_for_review) по-прежнему FAIL | unittest: `NOTE1TriggerGuardTests` ×2 (push-only — ok; bare pull_request — FAIL) |
| **NOTE-3 (парсер)** — multi-doc молча сливался (over-detection) | вердикт §3: «явно отвергать multi-doc» (рекомендация; выполнено) | `workflow_lint.py`: второй `---`/`...` маркер на уровне колонки 0 → `WorkflowParseError` (multi-document не поддержан, fail closed); первый leading `---` и `---` внутри block scalar (indented) допустимы | unittest: `MultiDocumentTests` ×1 (второй документ с pull_request_target+nanolab-cpu+write отклонён целиком, без merged-violations); матрица: `probe-multidoc` — exit 1 как и раньше, но теперь по explicit rejection |
| **NOTE-2** — timestamps хвоста vs terminal | вердикт: известное ограничение | закрыт введением MINOR-3-правила с легаси-exemption (см. выше) | unittest + матрица |
| **NOTE-4** — schema enum/pattern sync | отложить в control WO | без изменений; остаётся в `non_goals` конфига и доке §2.4 | — |
| Вердикт §4.5 — обновить док и конфиг «только новой фиксацией находок, без переписывания истории» | — | `VALIDATION_GATES_R1.md` §2.1/§2.2/§3/§5/§7/§8 обновлены (revision остаётся `VALIDATION-GATES-R1`, статус `PROPOSED`; история событий не редактировалась); `validation-gates.v1.json` дополнен новыми правилами, whitelist'ами с provenance и accepted-limitations | json-syntax check |

## Повторная негативная матрица (REVIEW_LOG_R1 §2–§3, все пробы)

18/18 ожидаемых исходов (прогон `probe_matrix.py`, временный каталог, вне репозитория;详情 в event `0006-repair-validation`):

| Проба | Было (раунд 1) | Стало | Ожидание вердикта |
|---|---|---|---|
| Позитив: реальный hosted-ci.yml | exit 0 | exit 0, 0 violations | exit 0 ✓ |
| `runs-on: nanolab-cpu` / `self-hosted` | exit 1 | exit 1 `NC1_SELF_HOSTED_LABEL` | exit 1 ✓ |
| `probe-alias-valid` (`&cpu`/`*cpu`) | **exit 0 (обход)** | **exit 1** `WORKFLOW_UNPARSEABLE` (anchor/alias) | exit 1 ✓ |
| `probe-on-list` (`on: [push, pull_request_target]`) | **exit 0 (обход)** | **exit 1** `NC2_TRIGGERS_UNSUPPORTED_FORM` | exit 1 ✓ |
| `probe-on-scalar` (`on: push`) | **exit 0 (обход)** | **exit 1** `NC2_TRIGGERS_UNSUPPORTED_FORM` | exit 1 ✓ |
| `probe-secrets-bracket2` (`secrets['X']`) | **exit 0 (обход)** | **exit 1** `NC7_SECRETS_REFERENCE` | exit 1 ✓ |
| `probe-multidoc` | exit 1 (merged) | exit 1 `WORKFLOW_UNPARSEABLE` (explicit rejection) | exit 1 ✓ |
| `probe-tabs` | exit 1 | exit 1 `WORKFLOW_UNPARSEABLE` | exit 1 ✓ |
| Базовый валидатор на `EX-NL1-002-R1` | exit 3, 5 residual | exit 3, 5 residual (воспроизведено) | exit 3 ✓ |
| Репаренный валидатор: 10/10 EX-* | 10/10 | **10/10** (легаси-whitelist работают) | 10/10 ✓ |
| Unmarked post-terminal / второй terminal / `REVIEW_CORRECTIONS` до handoff | FAIL | FAIL (без регрессии) | FAIL ✓ |
| `REVIEW_CORRECTIONS` ts 2020 < handoff 2026 | **OK (дыра)** | **exit 3** (`>= terminal`) | FAIL ✓ |
| `REVIEW_CORRECTIONS` от `IMPLEMENTER` | **OK (дыра)** | **exit 3** (роль) | FAIL ✓ |
| Новое событие с 7-hex `abc1234` | **OK (дыра)** | **exit 3** (invalid subject_sha) | FAIL ✓ |

## Чеки после ремонта (локально, HEAD ремонтного раунда)

JSON 111/111 OK · consistency ok=true · work_cli 10/10 EX-* OK · lint 0 violations · unittest **59/59** OK (было 34; +25 на новые правила).

## Не исправлено (осознанно, по вердикту)

- NOTE-4 / schema sync (enum `REVIEW_CORRECTIONS`, 40-hex pattern, passport `^NL[0-8]$` → `(NL|INFRA)[0-7]`) — control WO (вердикт §4.4).
- Env-индирекция секретов — принятое не-линтабельное ограничение (MINOR-1), задокументировано.
- `checkpoint: INFRA1` паспорта — известный третий прецедент (NOTE-4), валидатор паттерн не проверяет.
