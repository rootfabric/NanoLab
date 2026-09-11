# Summary — EX-DIR1-R1 (контрольный WO DIR-1: task_bus coverage в hosted-ci Check 5/5)

- Статус: **HANDOFF_READY** (implementer-фаза завершена; merge — Human Gate оркестратора)
- Ветка: `control/ci-taskbus-coverage-r1` от exact `main` `e26672c1a0e0344269ff0dc4d15374ec583c7192`
- Fix-субъект: `9f16e7ba5d216f4a3982b98177ad147e3bcfb712`
- Claim: `C0_SOFTWARE_ONLY` (не менялся); научный трек не затронут (E0–E6 `NOT_RUN`)

## Что сделано

1. **Фикс (кандидат A, минимальный)**: один новый пустой файл `tests/task_bus/__init__.py` — package-маркер, после которого существующий Check 5/5 (`python3 -m unittest discover -s tests -t .`) собирает и исполняет все 40 тестов брокера. Брокер (`tools/task_bus.py`, blob `a3d0556717f3320e885f4092f242bed53bf0584f`), тесты, workflow, state-файлы — не изменялись.
2. **Обоснование против кандидата B** (pytest-чек в hosted-ci.yml): `test_task_bus.py` — чистый `unittest.TestCase`, pytest не нужен; B требует гейта на изменение workflow (прямо отмечено в DIRECTOR_ACCEPTANCE_P14_R1), ставит CI в зависимость от установки pytest (сетевой шаг, supply-chain) и меняет контракт Check 5/5 «stdlib only». Полное сравнение — `docs/evidence/DIR1/README.md`.
3. **Локальная верификация (все 5 чеков hosted-ci parity)**:

| Прогон | Subject | Результат |
|---|---|---|
| `unittest discover` (Windows, Py 3.11.8) | `e26672c` (baseline) | 160 tests, OK — task_bus не собран |
| `unittest discover` (Windows, Py 3.11.8) | `9f16e7b` (fix) | **200 tests, OK (skipped=1** = symlink F-2, 39 passed + 1 skip — parity с регрессией Director'а**)** |
| `unittest discover` (нативный Linux-клон в WSL, Py 3.12.3) | `662e2ff` (baseline) | 160 tests, OK |
| `unittest discover` (нативный Linux-клон в WSL) | `9f16e7b` (fix) | **200 tests, OK — 0 skip** (symlink-тест позитивен; прямая CI-parity для ubuntu-агента) |
| `pytest tests/task_bus -q` (WSL, нативный клон) | `9f16e7b` (fix) | **40 passed** (symlink включён) |
| Checks 1–4 hosted-ci (JSON 739 файлов + pins; consistency; 18 EX-*; NC-lint) | рабочее дерево @ HEAD | все OK, 0 violations/failures |

Логи: `docs/evidence/DIR1/logs/{after-windows-discover-python3118,baseline-linux-662e2ff-discover,after-linux-native-9f16e7b}.txt`.

## Ожидаемый эффект после merge

- hosted-ci Check 5/5 на ubuntu-агенте: «Ran 200 tests, OK» без skip'ов — task_bus-покрытие (40 тестов) реально исполняется в live-CI на каждом PR/push.
- F-2 (REVIEWER_VERDICT §6): live-проверка symlink-отказа появляется на Linux (Windows-эквивалент остаётся опцией P2).
- DIR-1 снимается из очереди findings решением Director после контроля фактического зелёного CI на merge-коммите.

## Открытые пункты / границы

- Merge не выполнялся (Human Gate); после merge — контроль лога Check 5/5 (счёт 200).
- Вариант B (pytest в CI) не отклонён навсегда — отдельный workflow-гейт при необходимости.
- Windows-эквивалент symlink-негатива (junction/reparse) — очередь P2.
- `DIRECTOR_ACCEPTANCE_P14_R1.md` не редактировался (по директиве); настоящий doc + `docs/evidence/DIR1/README.md` — фиксация фактов для следующего Director-решения.

## Next action (один)

ORCHESTRATOR: быстрый control-review PR (`control/ci-taskbus-coverage-r1` @ `9f16e7b`, дифф = 1 пустой файл + docs/events) → merge (Human Gate) → контроль «Ran 200 tests» в CI-логе merge-коммита.
