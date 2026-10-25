# [VERIFIER-76] Независимая exact-head верификация PR #76 — VERDICT: FAILED

**Роль:** независимый fresh exact-head Verifier (отдельная сессия; не Reviewer, не Implementer, не Director этой ветки).
**Checkout:** `/home/rdpuser/NanoLab/verify-pr76-r1` (read-only по subject; собственные артефакты — `verify-evidence/` и `/tmp`). 0 научных запусков, 0 сетевых загрузок исходников; сеть — только read-only GitHub API для CI identity.
**Дата:** 2026-10-21 UTC.

## 0. Резюме вердикта

**VERDICT: FAILED** — для заявленного финального tip `d59258a` обязательная команда `work_cli validate` НЕ зелёная (exit 3), и hosted CI на этом точном SHA — **FAILURE**. Оба отказа вызваны одним дефектом docs-only вердикт-коммита Director'а: event `0007` использует изобретённый `event_type: REVIEW_PASS`, которого нет в словаре harness (`scripts/harness/work_cli.py`). При этом **сам review-предмет Reviewer (2e199d6) воспроизводится полностью** — все содержательные утверждения Reviewer подтверждены моими независимыми пробами. Во время верификации ветка сдвинулась: Director уже запушил repair-коммит `022a7a3` (исправление event_type + event 0008 с записью CI-негатива), CI на нём SUCCESS, все мои локальные проверки на нём зелёные. Требуется свежий exact-head Verifier-проход по `022a7a3`.

## 1. Точные величины и таймлайн binding

| Величина | Ожидание (mission) | Факт | Статус |
|---|---|---|---|
| HEAD | `d59258a60c5e95e188f7e1a1e9a37b9723c2962e` | `d59258a60c5e95e188f7e1a1e9a37b9723c2962e` | ✅ (на момент старта) |
| TREE | `d3fdb48f88c3d1dc603c81e1c9e0fbd14a1f9057` | `d3fdb48f88c3d1dc603c81e1c9e0fbd14a1f9057` | ✅ |
| Remote tip (первая проверка) | == HEAD | `d59258a60c5e…` | ✅ |
| Remote tip (повторная проверка в конце сессии) | == HEAD | **`022a7a376864f3dce4f92b6959e73fb298fbbca2`** | ❌ **ветка сдвинулась во время верификации** |
| Рабочее дерево | чистое | `git status --porcelain` пуст | ✅ |
| merge-base с main | `fb3148b…` | `fb3148b46a9638167168a46cb170902a4ad9e8d2` | ✅ ветка — потомок main |
| TREE review-предмета 2e199d6 | — | `9e8cd2c7a2ddbf5616b38e6922a14f458cac1e8b` | ✅ совпадает с Reviewer |
| `fb3148b^{tree}` | `1275a3fa…` | `1275a3faba16b6e9528651b12deec83b4337d6f0` | ✅ base_tree_sha в паспорте верен |

**Таймлайн race:** `git ls-remote` на старте верификации вернул `d59258a` (binding OK). Хостед-прогоны: run `39598714603` на `d59258a` (12:19:45Z, **failure**) и run `39599152605` на `022a7a3` (12:23:02Z, success) — repair-коммит был запушен параллельно с моей сессией. Формальный вердикт даётся по заявленному subject `d59258a`.

## 2. Родословная и docs-only дельта

- `git diff 2e199d6..d59258a --stat`: **17 файлов, 1047 вставок, 0 удалений** — все внутри `docs/work/executions/EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1/` (event 0007 + review/REVIEWER_R1/ evidence). Кода и тестов дельта не касается. ✅
- Полный diff от main (`fb3148b..HEAD`): 32 файла = 15 файлов review-предмета 2e199d6 + 17 файлов docs-only дельты (сходится с «15 files» у Reviewer). Состав: `docs/research/` (audit + pack), execution-dir, `docs/work/WO-…md`, `docs/work/WORK_QUEUE.md`, `scripts/knowledge_pack/alt_pair_source_gate.py`, `tests/test_alt_pair_source_gate.py`. ✅
- Дифф `d59258a..022a7a3` (repair, вне моего subject): 2 файла, оба events в том же execution-dir; изменение event 0007 — ровно одна строка `"event_type": "REVIEW_PASS"` → `"REVIEW_CORRECTIONS"`, остальной контент идентичен.

## 3. Обязательные команды (subject d59258a)

| # | Команда | Exit | Наблюдение | Вывод |
|---|---|---|---|---|
| 1 | `python3 -m unittest discover -s tests -t .` | **0** | `Ran 837 tests in 59.320s` / `OK` | ✅ 837/837, совпадает с ожиданием и с Reviewer |
| 2 | `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | **0** | `ok: true, errors: []`, head/tree = предмету | ✅ |
| 3 | `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | **0** | `violations: 0, blocking: 0` | ✅ |
| 4 | `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1` | **3** | `ok: false`; errors: `0007-review-pass.json: unsupported event_type`; `events after terminal/handoff must be review-corrections events (…): 0007-review-pass.json` | ❌ **НЕ зелёная** (см. §5) |
| 5 | `PYTHONPATH=scripts python3 -m knowledge_pack.alt_pair_source_gate docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json --candidate S23_NARCISSUS_ECHO --root .` | **2** | `outcome: BLOCKED_SOURCE`, 5× `SOURCE_BYTES_NOT_OBSERVED`, `scientific_runs: 0` | ✅ ожидаемый fail-closed (не дефект) |

Контрольная точка review-предмета: тот же `work_cli validate` на extraction `2e199d6` (git archive → `/tmp`, checkout не изменялся) → **exit 0, ok:true, HANDOFF_READY** — в точности запись Reviewer cmd4 (`cmd3_cmd4.meta.txt`: exit_code=0). Т.е. деградацию вносит именно вердикт-коммит `d59258a`.

## 4. CI identity (GitHub API, read-only)

| SHA | Run | Conclusion | Комментарий |
|---|---|---|---|
| **`d59258a60c5e…` (мой subject, ожидавшийся tip)** | `39598714603` / job `119217437169` | **FAILURE** ❌ | «RC0 hosted validation (H0)», check-runs total_count=1. Упал step «Check 3/5 — execution passports and work events integrity (all EX-*)»; в скачанном логе — ровно те же две ошибки валидатора event 0007 и строка `FAIL docs/work/executions/EX-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1`. Требование mission «CI SUCCESS на точном tip» **не выполнено** |
| `2e199d6` (review-предмет) | `39548593361` | SUCCESS ✅ | перепроверено мной независимо (check-run `completed/success`) — совпадает с Reviewer |
| `022a7a3` (repair, вне subject) | `39599152605` | SUCCESS ✅ | см. §7 |

## 5. Корневая причина отказа (атрибуция)

Event `0007-review-pass.json` (добавлен docs-only вердикт-коммитом `d59258a` AFTER Reviewer PASS):
- `"event_type": "REVIEW_PASS"` — значения нет в `ALLOWED_EVENTS` и нет в post-terminal классе `CORRECTIONS_EVENTS = {CONTINUATION_CHECKPOINT, REVIEW_CORRECTIONS}` (`scripts/harness/work_cli.py:11–16`);
- легальной орфографией для post-terminal review-маркера роли DIRECTOR является `REVIEW_CORRECTIONS` (`REVIEW_CORRECTIONS_ALLOWED_ROLES` включает DIRECTOR);
- прецедентов `REVIEW_PASS` нигде в `docs/work/executions/` нет;
- отказ воспроизведён тремя независимыми путями: (а) мой локальный запуск → exit 3; (б) hosted CI log того же SHA → те же два errors + `FAIL`; (в) Director сам зафиксировал это в event `0008` repair-коммита («event 0007 used invented event_type REVIEW_PASS, which is outside the harness vocabulary»).

Дефект один и тот же локально и в CI; это **дефект вердикт-коммита, а не review-предмета** и не гейта. По критерию mission («все команды зелёные, CI SUCCESS на точном tip») — **FAILED**.

## 6. Независимые пробы (мои собственные, не копии Reviewer)

Скрипт `verify-evidence/verifier76_probe_gate.py` (synthetic-фикстуры, offline, 0 science): **3/3 PASS**
- **P-NEG-1 (негатив):** `a_index=2` (внутренний индекс 12nt стрэнда) → `BLOCKED_SOURCE`, reason `anchor is not a 3p strand terminus (internal anchor)` ✅
- **P-NEG-2 (негатив):** `b_index=3` (внутренний индекс) → `BLOCKED_SOURCE`, `internal anchor` ✅
- **P-POS-1 (позитив / false-positive контроль):** валидные раздельные терминальные сегменты (`ACGTAC`/`GTACGT`, реверс-комплементарная пара, терминалы 3p/3p, непересекающиеся) → `TEST_FIXTURE_STATIC_INPUTS_OK`, `scientific_runs: 0` ✅ (preflight-only, наука не заявлена)

Дополнительно сверено: `git rev-parse fb3148b^{tree}` = `1275a3faba16b6e9528651b12deec83b4337d6f0` = заявленный в паспорте `base_tree_sha` (история исправления 3a7acbb→5e5712e подтверждается). Существование review-evidence Reviewer подтверждено; SHA-256 всех 16 файлов `review/REVIEWER_R1/` записаны в `verify-evidence/verifier76_review_sha256.txt`.

Примечание к пробам: первые две итерации моего probe-скрипта падали из-за моих собственных ошибок фикстуры (strand id 0 вместо 1; сегмент без реверса в файловый порядок 3′→5′) — гейт честно их отвергал на structural preflight; после исправления фикстур пробы попали в целевые пути кода. Это задокументировано как подтверждение чувствительности гейта, не как его дефект.

## 7. Сведения о repair-коммите 022a7a3 (вне моего формального subject; справочно)

| Проверка | Результат |
|---|---|
| TREE | `20ab4d60b24adfe3752959b392a2a3a1a82e403a` |
| Дифф от d59258a | docs-only: event 0007 (event_type→REVIEW_CORRECTIONS) + event 0008 (REVIEW_CORRECTIONS, DIRECTOR, фиксирует CI-негатив 39598714603) |
| unittest (клон в /tmp) | `Ran 837 tests in 58.708s` / `OK`, exit 0 |
| `work_cli validate` | **exit 0, ok:true**, event_types: […, REVIEW_CORRECTIONS, REVIEW_CORRECTIONS] |
| `check-consistency` / `workflow_lint` | ok:true / violations 0 |
| gate на реальном pack | exit 2 BLOCKED_SOURCE (fail-closed сохранён) |
| Hosted CI | run `39599152605` = SUCCESS на `022a7a376864` |

Все локальные проверки на `022a7a3` зелёные; дефект полностью устранён. Однако по протоколу exact-head верификации это должен подтвердить **свежий Verifier-проход, заявляющий exact subject `022a7a3…` / TREE `20ab4d60…`** — моё формальное решение по mission-предмету от этого не меняется.

## 8. Scope и гигиена

- Diff от main **не трогает** `project/state.json`, `project/plan.json`, `releases/` (frozen NL5), научные статусы — проверено `git diff fb3148b..HEAD --name-only` против этих путей (пусто). ✅
- Сфабрикованных `.top`/`.dat` в дереве ветки нет (`git diff … | grep -E '\.(top|dat)$'` пуст; synthetic-фикстуры существуют только во временных каталогах тестов/проб). ✅
- Секретов в диффе нет: литеральных `ghp_*`/`github_pat_*` токенов нет; единственные совпадения по «token» — текст `PUBLICATION_BLOCKED.md` (шаблон команды извлечения токена из `~/.git-credentials` БЕЗ самого значения и сообщения GraphQL об отказе). ✅
- 0 научных запусков; claim ceiling (BIBLIOGRAPHIC / BLOCKED_SOURCE) нигде не повышен; receipts гейта: `C0_INPUT_FILE_PREFLIGHT_ONLY; NO SIMULATION; NO ASSEMBLY_VALIDATED`. ✅

## 9. Расхождения с Reviewer

Содержательных расхождений с вердиктом Reviewer **нет**: все его ключевые утверждения (837/837 OK; consistency ok; lint 0; work_cli ok:true на 2e199d6; gate exit 2 fail-closed; нетерминальный индекс отклоняется; валидные раздельные терминалы принимаются; base_tree_sha 1275a3fa…; CI SUCCESS на 2e199d6; docs-only дельта; нет fabricated .top/.dat; нет секретов) воспроизведены моими независимыми командами и пробами.

Единственное уточнение (не ошибка Reviewer, а изменение состояния ПОСЛЕ его PASS): assertion «work_cli validate ok:true» верен для его subject `2e199d6`, но **не для финального tip `d59258a`** — вердикт-коммит, опубликованный после review, сломал tool-level валидность пакета и не был никем повторно верифицирован до моей сессии.

## 10. Вердикт

### VERDICT: FAILED (для заявленного exact subject `d59258a60c5e95e188f7e1a1e9a37b9723c2962e` / TREE `d3fdb48f…`)

**Основания (воспроизводимы):**
1. `work_cli validate` на tip → exit 3, ok:false (event 0007 `REVIEW_PASS` вне словаря harness) — обязательная команда не зелёная.
2. Hosted CI H0 на том же SHA → FAILURE (run 39598714603), та же корневая причина, подтверждена логом.
3. Точное binding нарушено по ходу сессии: remote tip ветки теперь `022a7a376864…` (repair-коммит), т.е. верифицируемый subject больше не является tip.

**Что НЕ подорвано:** review-предмет `2e199d6` (код, тесты, evidence, claim-дисциплина) полностью воспроизводится; вердикт Reviewer PASS по своему subject подтверждён; repair `022a7a3` локально и в CI зелёный.

**Next action:** fresh exact-head VERIFIER-проход по `022a7a376864f3dce4f92b6959e73fb298fbbca2` / TREE `20ab4d60b24adfe3752959b392a2a3a1a82e403a`; затем READY_FOR_HUMAN_GATE. Merge в `main` — по-прежнему Human Gate.

**Артефакты верификации:** `verify-evidence/verifier76_unittest.log` (837 OK @ d59258a), `verifier76_unittest_022a7a3.log` (837 OK @ 022a7a3), `verifier76_workcli_subject.log` (exit 0 @ 2e199d6), `verifier76_workcli_022a7a3.log` (exit 0 @ 022a7a3), `verifier76_checkruns.json` + `verifier76_job.json` + `verifier76_ci_log.txt` (CI identity и лог отказа), `verifier76_probe_gate.py`/`.out` (3/3), `verifier76_review_sha256.txt` (16 файлов Reviewer).

**Публикация в Issue #77:** одиночная попытка `gh issue comment 77 --repo rootfabric/NanoLab --body-file verify-evidence/VERIFY_PR76_R1.md` → GraphQL «Resource not accessible by personal access token (addComment)», exit 1. Ожидаемо (у токена нет Issues:write); ретраев нет — публикацию берёт на себя Director.

— VERIFIER-76, независимая сессия
