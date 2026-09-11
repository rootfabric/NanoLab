# Branch Passport — EX-DIR1-R1

- Branch: `control/ci-taskbus-coverage-r1`
- Work Order: `DIR-1` — контрольный WO «hosted-ci Check 5/5 не собирает `tests/task_bus`» (finding DIR-1 MEDIUM из очереди `docs/evidence/BUS-SMOKE-001/DIRECTOR_ACCEPTANCE_P14_R1.md`, «Очередь accumulated findings»; файл WO в `project/infra-plan.json` отсутствует — прецедент контрольного WO без plan-задачи: EX-CTRL-LINTSCHEMA-R1)
- Checkpoint: `INFRA1` — hosted-ci capability train (INFRA1-001/002): фикс относится к validation-покрытию Check 5/5; паттерн паспорта `^(NL[0-8]|INFRA[0-7])$` допускает INFRA-чекпоинт (расширение схем control WO EX-CTRL-LINTSCHEMA-R1)
- Base SHA: `e26672c1a0e0344269ff0dc4d15374ec583c7192` (exact canonical `main` = merge PR #35; fetch origin, `origin/main` = local `main` = base до старта, дерево чистое)
- Created from canonical main: yes
- Risk class: `MEDIUM` (меняется исполнительная поверхность CI — Check 5/5 начинает реально исполнять 40 task_bus-тестов; без self-hosted/secrets/GPU; routing по директиве миссии: быстрый контрольный review, merge — Human Gate оркестратора)
- Claim class: `C0_SOFTWARE_ONLY`
- Allowed paths: see `passport.json` (`tests/task_bus/__init__.py`, `docs/evidence/DIR1/**`, `docs/work/executions/EX-DIR1-R1/**`)
- Status: `IN_PROGRESS`
- Active experiment campaigns: none (control WO; E0–E6 остаются `NOT_RUN`)
- START commit: см. git log ветки (pushed до substantive work)
- Next action: выбор минимального варианта фикса (package marker vs pytest-чек в workflow), локальная верификация (unittest discover 160→~200; WSL pytest tests/task_bus 40 passed с symlink), документирование обоснования в `docs/evidence/DIR1/`, события + handoff, PR (без merge)
- Blocking issue: none

## Scope (из директивы миссии — минимальный надёжный вариант)

1. DIR-1 (DIRECTOR_ACCEPTANCE_P14_R1, live-CI observation): `hosted-ci` Check 5/5 (`python3 -m unittest discover -s tests -t .`) не собирает `tests/task_bus` (нет `__init__.py`; Python 3.11+ не делает namespace-package discovery) — CI зелёный (160 tests) без task_bus-покрытия, «Start directory is not importable» при прямом discover в подкаталог.
2. Кандидат A (предпочтительный, минимум диффа): пустой `tests/task_bus/__init__.py` — `tests/task_bus/test_task_bus.py` уже чистый `unittest.TestCase` (pytest не используется), поэтому после package-маркера discovery собирает и исполняет все 40 тестов без изменения тестов и workflow. Не требует гейта на изменение `.github/workflows/hosted-ci.yml` (его изменение само по себе требует отдельного review/verify по NC-lint — DIRECTOR_ACCEPTANCE_P14_R1).
3. Кандидат B (отклоняется в этой ревизии): pytest-чек в hosted-ci.yml — изменение workflow требует отдельного гейта, pytest не гарантирован на runner (нужен pip install → сетевая зависимость и расширение supply-chain поверхности), ломает контракт Check 5/5 «validator + lint, stdlib only».
4. Бонус: на ubuntu-агенте symlink-негатив (`test_symlink_candidate_and_local_smoke_are_rejected`, skip только при `OSError` на `symlink_to`) исполняется позитивно — live-покрытие F-2 на Linux.
5. Локальная верификация: (a) Windows `python -m unittest discover -s tests -t .` — 160 → 200 (39 passed + 1 skipped symlink); (b) WSL `python3 -m pytest tests/task_bus -q` — 40 passed (symlink включён); (c) все 5 чеков hosted-ci локально.
6. Обоснование выбора варианта и результаты — `docs/evidence/DIR1/README.md`; DIRECTOR_ACCEPTANCE_P14_R1.md не редактируется (по директиве миссии).

## Вне scope (не трогать)

`tools/task_bus.py` и брокерные blob'ы, `project/state.json`, `project/infra-state.json`, `project/infra-plan.json`, science-файлы (`experiments/**`), `.github/workflows/**`, чужие `EX-*`, вердиктные документы (`docs/evidence/BUS-SMOKE-001/**`), history rewrite, ACCEPTED-статусы, P2 production activation.

## Документированные отклонения (для reviewer)

1. **`work_order_id: DIR-1`** — контрольный WO без задачи в `project/infra-plan.json` (тот же класс, что EX-CTRL-LINTSCHEMA-R1 `CTRL-LINTSCHEMA`); идентификатор self-consistent с `execution_id` `EX-DIR1-R1` по конвенции `EX-<wo>-R<N>` (дефис WO-номера опускается в execution_id); валидатор `work_cli` требует только совпадения `work_order_id` паспорта и событий.
2. **`checkpoint: INFRA1` при bus-происхождении finding'а** — DIR-1 зафиксирован в очереди BUS-SMOKE-001 (P2), но substance фикса — validation-покрытие hosted-ci (INFRA1 train), а не брокер/политики; схема паспортов допускает только `NL[0-8]|INFRA[0-7]`, bus-значения паттерном не предусмотрены.
3. **`docs/evidence/DIR1/**` в allowed_paths** — директива миссии требует отдельный README с обоснованием в `docs/evidence/DIR1/`; редактирование исходного вердикта `docs/evidence/BUS-SMOKE-001/DIRECTOR_ACCEPTANCE_P14_R1.md` запрещено.

Правило границ: без self-hosted runner'ов, secrets, GPU, paid compute; state-файлы и science не изменяются (Director gate); merge в `main` — Human Gate оркестратора после быстрого review.
