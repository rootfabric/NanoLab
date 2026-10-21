# [VERIFIER-73] Независимая exact-head верификация PR #73 — VERDICT: VERIFIED (subject 7c99802)

**Verifier:** VERIFIER-73 (независимая сессия; не Reviewer REVIEWER-73, не Implementer/Author, не Director этой ветки)
**Даты:** 2026-10-21 (UTC); верификация v1 @ 7a1bb28 → **FAILED** (один blocker), повторная верификация v2 @ нового tip 7c99802 → **VERIFIED**
**Режим:** read-only верификация subject, offline C0; 0 scientific runs; 0 paid compute
**Checkout:** /home/rdpuser/NanoLab/verify-pr73-r1 (изоляция соблюдена; собственные write-артефакты — только `verify-evidence/` и `/tmp`)
**Reviewed subject (PASS Reviewer):** `baac1378b3de604cdad99c546e1cf9d9b5b000b3`

---

## Часть 1. Верификация v1 @ 7a1bb28 — FAILED (историческая запись, сохранена)

| Параметр | Значение |
| --- | --- |
| HEAD / TREE | `7a1bb285d096a0b804b362e5718f421eb7f7c1b7` / `e3a984ed042f3e400ac3a7abab85d12177ec4561` — совпали с заявленными, дерево чистое |
| unittest | exit 0, **930 tests OK** |
| check-consistency / workflow_lint | exit 0 / exit 0 (ok:true, blocking 0) |
| `work_cli validate EX-S17-STACK-INTEGRATION-R1` | **exit 3, ok:false** — event 0006 `event_type: "REVIEW_PASS"` вне словаря `scripts/harness/work_cli.py` (post-terminal допускает только CONTINUATION_CHECKPOINT/REVIEW_CORRECTIONS); на baac137 та же команда — ok:true |
| Hosted CI на 7a1bb28 | **FAILURE** (#39598725537, job `RC0 hosted validation (H0)`, шаг «Check 3/5 — execution passports and work events integrity (all EX-*)») — та же корневая причина |
| 55-blob сверка | ✅ 53 match + 2 annotated superseded = 55 |
| Негативные контроли, scope | ✅ (тамперы отклонены, NOT_RECONSTRUCTED сохранён, scope чист) |

**Blocker v1 (единственный):** docs-only вердикт-коммит 7a1bb28 внёс событие с несуществующим event_type → обязательная команда validate красная + hosted CI красная. VERDICT v1: **FAILED**. После этого Director опубликовал append-only фикс-коммит 7c99802 (event_type исправлен; негатив CI зафиксирован новым событием 0007), что и стало новым subject верификации v2.

---

## Часть 2. Верификация v2 @ 7c99802 (финальный кандидат на merge)

### 0. Subject binding

| Параметр | Заявлено | Фактически | Совпадение |
| --- | --- | --- | --- |
| HEAD | `7c99802cd010f6c2a848c024b03d11c41cb3dcd0` | `git rev-parse HEAD` → идентично | ✅ |
| TREE | `9f7c704ce83722cb998aa168bee1e8dc070d64d7` | `git rev-parse 'HEAD^{tree}'` → идентично | ✅ |
| Remote tip | = HEAD | `git ls-remote origin integration/s17-r3-repair-assembly-cli-r1` → `7c99802…` | ✅ |
| Working tree | чистое | `git status --porcelain` → только untracked `verify-evidence/` (мои артефакты) | ✅ |

Родословная: `git merge-base HEAD fb3148b` = `fb3148b46a9638167168a46cb170902a4ad9e8d2` (base main — предок); `baac137` и `7a1bb28` — предки `7c99802` (`--is-ancestor` ✅). Линейная цепочка: fb3148b → … → baac137 → 7a1bb28 → 7c99802, без rewrite.

### 1. Диффы фикс-коммита

- **`baac137..7c99802`:** 15 файлов, ВСЕ внутри `docs/work/executions/EX-S17-STACK-INTEGRATION-R1/` (events 0006/0007, аннотация source-blob-map, 12 файлов review-evidence REVIEWER_R1). Код/тесты от reviewed subject не отличимы. ✅
- **`7a1bb28..7c99802`:** ровно 2 поверхности: (1) event 0006 — **единственная изменённая строка** `event_type: "REVIEW_PASS"` → `"REVIEW_CORRECTIONS"` (проверено прямым diff двух blob'ов: отличий больше нет); (2) новый файл `events/0007-fix-event-type-vocabulary.json`. ✅ — точно как заявлено.

### 2. Обязательные команды

| Команда | Exit code | Результат |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -t .` | **0** | **Ran 930 tests in 61.847s — OK** (лог: `verify-evidence/unittest_7c99802_stderr.log`) |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | **0** | `ok: true`, errors: [], warning `git metadata unavailable` (ожидаемое окружение, review M3); head/tree = 7c99802/9f7c704 определены корректно, frontier NL5 |
| `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | **0** | `ok: true`, violations: 0, blocking: 0 |
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-S17-STACK-INTEGRATION-R1` | **0** | ✅ **`ok: true`, `HANDOFF_READY`**, errors: []; цепочка: WORK_ORDER_STARTED → CONTINUATION_CHECKPOINT → VALIDATION_RECORDED → HANDOFF_COMPLETED → CONTINUATION_CHECKPOINT → REVIEW_CORRECTIONS (0006) → REVIEW_CORRECTIONS (0007) |
| Доп. validate 4 родственных execution-диров | 0 ×4 | `EX-PREP-S17-R3`, `-REPAIR-R1`, `-OVERHANG-ERRATUM-R1`, `EX-S17-STATIC-ASSEMBLY-HARDENING-R1` — все ok |

### 3. Сверка 55 записей source-blob-map.json на tip 7c99802

```text
MATCH = 53   DIFFER = 2   PROBLEMS = 0   TOTAL = 55   →  53 + 2 = 55 ✅
```

- 53 пути: `blob_sha1` карты == `git rev-parse HEAD:<path>`.
- Ровно 2 отличающихся — ожидаемые, аннотации валидны (и `superseded_by_erratum.commit`, и `head_blob_sha1` совпадают с git):
  - `docs/research/S17_R3_COMPONENT_FOLLOWER.json`: map `c44374a9…` vs HEAD `3a09fab4…`, commit `4f9583d84f0047f21f8dc22eddaea4e592788e01` ✅
  - `tests/test_s17_r3_assembly.py`: map `91729bb9…` vs HEAD `074619eb…`, commit `1bfafb959b6f7cda695a560bc46082bfc83117df` ✅
- Claims карты: `scientific_runs: 0`, `source_real_follower: NOT_RECONSTRUCTED`, `claim_ceiling: PINNED_IMPORT_VERIFIED` ✅

### 4. CI identity (GitHub API)

| SHA | Run | Статус |
| --- | --- | --- |
| **`7c99802cd010f6c2a848c024b03d11c41cb3dcd0` (верифицируемый tip)** | `hosted-ci` #39599164149 | ✅ **completed / SUCCESS** — job `RC0 hosted validation (H0)`: success |
| 7a1bb28 (предыдущий tip) | #39598725537 | FAILURE — негатив, зафиксирован событием 0007 (ожидаемо) |
| baac137 (reviewed subject) | #39525811063 | SUCCESS |

### 5. Негативные контроли (свежие прогоны на 7c99802)

**(a) Deliberate tamper, реальный CLI-путь** (`/tmp/tamper_ctl2`, копия примера; чистый baseline: exit 0, `ASSEMBLED_STATIC_ONLY` + `GEOMETRY_UNVERIFIED`):

| Tamper | Результат |
| --- | --- |
| 1 символ sequence (чужая база) → **exit 2, `BLOCKED_INFERRED_INTERFACE`** («sequences are not complementary, max RC match 11 nt < 12») ✅ |
| лишний нуклеотид в overhang (класс erratum 20→21nt) → **exit 2, `BLOCKED_INFERRED_INTERFACE`** ✅ |
| реальная S17-пара, unit-путь: `test_real_recipe_after_20nt_erratum_is_valid_and_tampering_still_refused` → **OK** (21nt ре-тампер → `BLOCKED_SOURCE`) ✅ |

Логи: `verify-evidence/tamperA2.log`, `tamperB2.log`. Fail-closed не ослаблен.

**(b) NOT_RECONSTRUCTED:** `tests.test_s17_r3_assembly` — **71 тест OK** (включая `test_missing_follower_structure`, `test_f01_structureless_pair_keeps_not_reconstructed_over_port_gate`, `test_real_s17_pair_remains_not_reconstructed`); `tests.test_s17_r3_overhang_erratum` — 4/4 OK (включая `test_no_spurious_physical_port_or_science_claim`); claims карты: 0 scientific runs, NOT_RECONSTRUCTED. ✅

### 6. Scope на 7c99802

- `git diff fb3148b..HEAD`: 88 A + 1 M; **`project/state.json` и `project/plan.json` не затронуты** (state.json байт-идентичен main), **`releases/` (frozen NL5) не затронут** (0 файлов) ✅
- Секреты: grep diff — единственное совпадение — тестовая строка `"/etc/passwd"` в path-traversal тесте кода; секретов нет ✅
- Научные статусы: frontier NL5, next NL5-002; NL6/NL7 не затронуты; claim ceiling `PINNED_IMPORT_VERIFIED`, 0 runs — повышения нет ✅

### 7. Суждение о законности фикс-паттерна (запрошено явно)

**Паттерн:** словарная ошибка в машинно-валидируемом поле события 0006 исправлена НОВЫМ коммитом (не force-push): оригинальный blob 0006 (`a26d13f`) остаётся адресуемым на 7a1bb28, негативный CI-результат зафиксирован отдельным новым событием 0007 (REVIEW_CORRECTIONS, actor DIRECTOR — роль из allowed set), изменена ровно одна строка, содержательная часть события не тронута.

**Суждение: LEGITIMATE (допустимо) с той же оговоркой класса M2.** Обоснование:
1. **История не переписана:** 7a1bb28 достижим как предок (`--is-ancestor` ✅), нет force-push/rewrite — «GIT IS DURABLE MEMORY» соблюдён; оригинал 0006 верифицируем навсегда.
2. **Негатив не скрыт:** CI-failure задокументирован событием 0007 и commit message — hard rule «NEGATIVE / FAILED / INCONCLUSIVE RESULTS MUST BE PRESERVED» соблюдён.
3. **Альтернативы не было:** append-only «corrections-only новым событием» не лечит невалидный event_type — пакет остаётся machine-invalid (validate exit 3, CI красный), т.е. ветка принципиально не могла пройти обязательный гейт без правки этого поля. Правка минимальна (1 строка).
4. **Класс прецедента тот же, что уже признан Reviewer'ом допустимым с оговоркой (M2):** правка событий, созданных минутами ранее внутри этого же неслитого PR и никогда не входивших в канонический main.
5. **Граница применимости (важно):** этот паттерн законен ТОЛЬКО pre-merge. После попадания событий в канонический `main` такой edit был бы недопустим — тогда обязателен новый event + (при словарной ошибке) механизм класса LEGACY_*-grandfather, как это сделано для `EX-NL5-002-E-R1` в `work_cli.py`.

**Caveat (не блокер):** исключение по-прежнему не кодифицировано в control-документах — владельцу следует явным решением зафиксировать в `AGENTS.md`/`docs/control/` правило «pre-merge machine-vocabulary correction допускается новым коммитом с фиксацией негатива отдельным событием», иначе прецедент (уже второй в этом PR после 0003/0004) может тиражироваться на слитые ветки.

### 8. Итоговая таблица v2

| # | Проверка | Результат |
| --- | --- | --- |
| 1 | Exact HEAD/TREE/remote binding, чистое дерево | ✅ 7c99802 / 9f7c704 / 7c99802 |
| 2a | unittest | ✅ exit 0, 930 OK |
| 2b | check-consistency | ✅ exit 0, ok:true |
| 2c | workflow_lint | ✅ exit 0, blocking 0 |
| 2d | work_cli validate EX-S17-STACK-INTEGRATION-R1 | ✅ exit 0, ok:true, HANDOFF_READY |
| 3 | 55-blob сверка | ✅ 53 + 2 = 55 |
| 4 | ancestry / docs-only дельта / фикс ровно 1 строка + event 0007 | ✅ |
| 5 | CI на 7c99802 | ✅ SUCCESS (#39599164149) |
| 6a | Негативные тамперы | ✅ отказ ×3 (BLOCKED_INFERRED_INTERFACE ×2, BLOCKED_SOURCE) |
| 6b | NOT_RECONSTRUCTED | ✅ сохранён |
| 7 | Scope | ✅ чист |
| 8 | Законность фикс-паттерна | ✅ LEGITIMATE с оговоркой (policy-кодификация остаётся за владельцем) |

## VERDICT

## **VERIFIED**

Все обязательные команды зелёные на точном tip `7c99802cd010f6c2a848c024b03d11c41cb3dcd0` (tree `9f7c704ce83722cb998aa168bee1e8dc070d64d7`); 55-проверка сошлась (53+2); hosted CI H0 — SUCCESS на этом SHA; негативные контроли отрабатывают отказ; scope чист; NOT_RECONSTRUCTED и claim ceiling не нарушены; append-only фикс-паттерн признан законным с non-blocking оговоркой о кодификации policy. Найденный и исправленный дефект v1 (7a1bb28) полностью задокументирован в самой ветке (event 0007 + CI #39598725537).

**Ограничения верификации:** offline C0; hosted CI не переисполнялся локально (кроме обязательных команд, исполненных локально); Dataset S1 не перекачивался. VERIFIED — это техническая exact-head верификация C0-кандидата; она не заменяет Human Gate на merge и не повышает научных статусов.

**Next action:** Human Gate на merge PR #73 (subject 7c99802) по записи владельца в Issue #74.

**Evidence:** `verify-evidence/tamperA2.log`, `tamperB2.log`, `clean_run.log`, `unittest_7c99802_stderr.log`, `unittest_summary_stderr.log` (v1), плюс записи Части 1.
