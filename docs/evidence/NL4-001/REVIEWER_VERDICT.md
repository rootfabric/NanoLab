# REVIEWER VERDICT — EX-NL4-001-R1

- **Execution:** EX-NL4-001-R1 (WO-NL4-001, checkpoint NL4, risk MEDIUM, claim `C0_SOFTWARE_ONLY`)
- **Exact HEAD:** `4ef7b9c7b7dc60d627ba76387280029bc72235a2` (ветка `work/nl4-001-bounded-agent-r1`; base `4046189`)
- **Дата review:** 2026-09-13 (UTC+10)
- **Reviewer:** независимый REVIEWЕР в fresh-сессии, отдельный worktree `C:\NanoLab\review-nl4-001`, ветка `review/nl4-001-bounded-agent-r1` от exact HEAD. **Independence caveat:** fresh-сессия (нет контекста Implementer), но тот же физический хост и тот же исполнитель-инфраструктура; независимость организационная (разная сессия/ветка), не аппаратная.

## Таблица проверок 1–10

| # | Проверка | Команда / метод | Результат |
|---|---|---|---|
| 1 | Scope (diff только allowed paths) | `git diff --stat 4046189..4ef7b9c` | **OK** — 26 файлов, всё в `docs/work/**` (execution, SESSION_LOG append), `scripts/nl4/**`, `tests/**`; `project/**`, `docs/research/**`, `scripts/e2| hinge_family/**`, `experiments/**` не тронуты (только import `e2.canonical`) |
| 2 | Безопасность allowlist | чтение кода + собственные негативные пробы через CLI `python -m nl4 validate-candidate` и scripted bounded-agent | **OK** — см. векторы ниже |
| 3 | Бюджет-энфорсмент | код (`controller.py` L264–271) + собственный probe (4 запроса при max=2) + `test_nl4_allowlist.py` (sims/wall/mirror) | **OK** — исполнено ровно 2, stop `BUDGET_EXHAUSTED_SIMULATIONS`; wall-запрос отклоняется ДО исполнения |
| 4 | Полный тест-набор | `python -m unittest discover -s tests -t .` | **OK** — stderr: `Ran 287 tests … OK (skipped=1)`; 45 новых `test_nl4_*` подтверждены отдельным прогоном (`Ran 45 … OK`). Stdout содержит JSON-шум от CLI-прогонов в тестах — COSMETIC |
| 5 | Детерминизм/воспроизводимость | `demo --agent random\|grid --target 45 --max-simulations 5` ×2 | **OK** — повторы байт-идентичны; оба вывода байт-идентичны evidence-файлам; random: `32b/100000/203012 → …` best 90.36; grid: `0b/50000×3 → 0b/100000×2` best 24.46 — совпадает с records |
| 6 | Нет физики/сети/LLM | grep `scripts/nl4` на `urllib\|requests\|socket\|http\|openai\|api_key\|wsl\|subprocess` + аудит import'ов | **OK** — единственный grep-хит — слово «requests» в docstring; импорты только stdlib (`json`, `hashlib`, `random`, `itertools`, `argparse`, `pathlib`); mock = чистая функция sha256(canonical candidate JSON) |
| 7 | Scoring | код `scoring.py` vs `docs/research/E2_PROTO_R1.md` §4 (L28–30) | **OK** — константы точно `0.1078 / 0.50 / 20.0`, breach-условия те же (`>`, `<`, `>`); score = `\|median − target\|` (round 9); invalid → `score: None` + счётчики, не теряются |
| 8 | Отклонения от WO | три заявленных — см. ниже | **OK** — все три обоснованы и зафиксированы |
| 9 | Валидаторы | `work_cli validate` / `close`; `python -m harness.cli check-consistency` (из корня, PYTHONPATH=scripts) | **OK** — validate/close: `ok: true`, status HANDOFF_READY, 4 события, терминал HANDOFF_COMPLETED; check-consistency: `ok=true, errors=[]` |
| 10 | Records | events/passport/summary/SESSION_LOG | **OK** — согласованы между собой и с evidence; timestamps монотонны; SESSION_LOG append-only (+6 строк); subject_sha events = 8009f16 (impl-коммит) |

## Негативные пробы allowlist (проверка 2, собственные векторы)

Через CLI (`validate-candidate`):
- `{"variant":"99b"}` → `valid=false, reason=CANDIDATE_PARAM_NOT_IN_ALLOWLIST`, exit 3
- `{"variant":"32b","engine":"oxdna"}` → `valid=false, reason=FORBIDDEN_CANDIDATE_FIELD`, exit 3
- `{"variant":"32b","physics":"lj"}` → `valid=false, reason=FORBIDDEN_CANDIDATE_FIELD`, exit 3
- позитив-контроль `{"variant":"32b","steps":100000}` → `valid=true` (defaults seed=201004), exit 0

Через scripted bounded-agent (action-уровень):
- `{"action":"run_simulation",…}` → rejected `ACTION_NOT_IN_ALLOWLIST`, НЕ форвардед в контроллер, исполнение не произошло
- `propose_candidate` с `engine` → rejected `FORBIDDEN_CANDIDATE_FIELD`
- валидный `32b` при этом исполнен (runs=1) — fail-closed подтверждён end-to-end

Структурный аудит (а–г):
- **(а)** Порядок соблюдён: `BoundedAgent.next_action` валидирует каждое сырое предложение (`normalize_candidate`, `ALLOWED_ACTIONS`) ДО возврата контроллеру; контроллер ре-валидирует (defense in depth). Исполнение только через `Controller._handle_request_run` после всех проверок.
- **(б)** Fail-closed подтверждён: неизвестное действие → `ACTION_NOT_IN_ALLOWLIST`; неизвестное поле → `UNKNOWN_CANDIDATE_FIELD`; forbidden-поле → `FORBIDDEN_CANDIDATE_FIELD`; параметр вне enum → `CANDIDATE_PARAM_NOT_IN_ALLOWLIST`. Всё логируется, ничего не исполняется.
- **(в)** В allowlist НЕТ действий, меняющих физику/протоколы/критерии/движок: только `propose_candidate` (enum-кандидат), `request_run`, `read_analysis` (read-only), `stop`. `goal.integrity_gate` жёстко зажат `E2_PROTO_R1_S4_FROZEN` в `parse_goal` — кастомные гейты отклоняются.
- **(г)** `forbidden_candidate_fields` покрывает engine/physics/protocol/criteria (+15 имён включая code/command/network/llm/prompt) и проверяется ДО значений параметров.

## Отклонения от WO (проверка 8)

1. **Повтор (variant,steps,seed) → `CANDIDATE_ALREADY_RUN` вместо SEED_REUSE** — разумно: кандидат однозначно идентифицируется тройкой, повторное исполнение идентичного кандидата не даёт информации и жгло бы бюджет; семантика зафиксирована в `allowlist.json` seed_policy, покрыта тестом `test_duplicate_candidate_rerun_rejected`. WO не предписывал иного. **Принято.**
2. **END_ANALYSIS записан типом `IMPLEMENTATION_COMMITTED`** — проверено: `scripts/harness/work_cli.py` `ALLOWED_EVENTS` = {WORK_ORDER_STARTED, CONTINUATION_CHECKPOINT, IMPLEMENTATION_COMMITTED, VALIDATION_RECORDED, BLOCKER_RECORDED, REPAIR_STARTED, REPAIR_COMPLETED, REVIEW_RECORDED, REVIEW_CORRECTIONS, terminal…}; типа END_ANALYSIS schema действительно не имеет. Семантика зафиксирована в summary события 0003 («END_ANALYSIS EX-NL4-001-R1…»). **Принято.**
3. **Фикс path-insert в `tests/test_e2_pilot.py`** — +3 строки стандартного `sys.path.insert`, файл в allowed `tests/**`, CI-команда без PYTHONPATH теперь зелёная (подтверждено моим прогоном). **Принято.**

## Findings

| # | Severity | Finding |
|---|---|---|
| F1 | **COSMETIC** | JSON-шум в stdout при `unittest discover`: тесты, гоняющие CLI-команды `nl4` (demo/validate-candidate), печатают canonical-JSON отчёты прямо в stdout без capture (наблюдено: 288 строк stdout при прогоне 45 nl4-тестов). Функциональный вердикт корректно читается по stderr-итогу (`Ran 287 … OK`). Рекомендация (не блокер): capture stdout в CLI-тестах. |
| F2 | **LOW** | `Controller._handle_request_run`: при self-describing повторе уже исполненного кандидата отдаётся `CANDIDATE_ALREADY_RUN` только если он всё ещё числится в `self.candidates`; для request_run по `candidate_id` повторного исполнения закрыто явно. Дубликаты покрыты тестом; поведение консервативно (rejected, не исполнено). Информационное замечание к NL4-002. |
| F3 | **INFO** | Wall-бюджет в mockе точен (estimate == факт), т.к. `MockExecutor.estimate_wall_seconds` возвращает ту же детерминированную величину, что и run. Реальный адаптер NL4-002 обязан декларировать консервативную оценку — риск корректно зафиксирован в summary самим Implementer. |
| F4 | **INFO** | `check-consistency` требует запуска из корня репо с `PYTHONPATH=scripts` (или `python -m harness.cli` из `scripts/` с корректным cwd) — запуск «в лоб» файлом даёт ImportError. Не дефект данного WO (утилита существовала до него), но стоит захватить в README/CI-инвокацию. |

## Вердикт

# PASS

Все 10 обязательных проверок пройдены на exact HEAD `4ef7b9c`; собственные негативные пробы (кандидат- и action-уровень) подтверждают fail-closed семантику allowlist; бюджет жёсткий и не превышается; демо воспроизводимы байт-в-байт и совпадают с evidence; код чист от физики/сети/LLM; гейты точно соответствуют frozen E2_PROTO_R1 §4; все три отклонения от WO обоснованы и задокументированы. Findings — только COSMETIC/LOW/INFO, ни один не блокирует.

## Claim ceiling

- **`C0_SOFTWARE_ONLY` — подтверждён.** Всё, что исполнено, — детерминированные mock-прогоны (`NL4-MOCK-*`, sha256-псевдо-наблюдаемые); `physics_runs = 0`; `scientific_outcome = NOT_EVALUATED` заявлен корректно и не завышен.
- **Безопасность allowlist — главный риск-фокус (risk MEDIUM):** в границах данного WO (software-only, mock-исполнитель) валидация выполняется до исполнения, неизвестное/запрещённое отклоняется fail-closed и логируется, гейты и integrity_gate неизменяемы из action-space. Claim об уровне безопасности реального движка (NL4-002, oxDNA через ExecutorAdapter) этим review НЕ делается — он потребует отдельной проверки реального адаптера.
- Результаты baselines (90.36 / 24.46) — псевдо-данные, к науке не относятся (заявлено честно).
