# DIR-1 — task_bus coverage в hosted-ci Check 5/5 (EX-DIR1-R1)

Контрольный фикс MEDIUM finding'а **DIR-1** из `docs/evidence/BUS-SMOKE-001/DIRECTOR_ACCEPTANCE_P14_R1.md` («Очередь accumulated findings»). Этот документ — обоснование решения и протокол локальной верификации. Исходный вердикт `DIRECTOR_ACCEPTANCE_P14_R1.md` сознательно **не редактируется** (по директиве миссии); корректировка очереди — дело следующего Director-решения.

- Ветка: `control/ci-taskbus-coverage-r1` (от exact `main` = `e26672c1a0e0344269ff0dc4d15374ec583c7192`, merge PR #35)
- Execution: `EX-DIR1-R1` (паспорт: `docs/work/executions/EX-DIR1-R1/passport.json`)
- Fix commit: `9f16e7ba5d216f4a3982b98177ad147e3bcfb712` — `fix(tests): add tests/task_bus package marker so unittest discover collects broker suite`
- Claim ceiling: `C0_SOFTWARE_ONLY` (не меняется; научный трек не затронут)

## Суть DIR-1

`hosted-ci` Check 5/5 (`python3 -m unittest discover -s tests -t .`) на merge-коммите PR #20 дал «Ran 160 tests» — ровно тот же счёт, что до merge: `tests/task_bus/` discovery не собирает. Причина: `tests/task_bus/` не является package (нет `__init__.py`); начиная с Python 3.11 unittest-discovery не заходит в namespace-пакеты, прямая попытка `discover -s tests/task_bus` даёт «Start directory is not importable». Итог: CI зелёный, но task_bus-покрытие (40 тестов брокера) в live-CI фактически отсутствует.

## Выбранный вариант: A — пустой `tests/task_bus/__init__.py` (единственный файл)

**Сравнение кандидатов:**

| | A: `tests/task_bus/__init__.py` (ВЫБРАН) | B: pytest-чек в hosted-ci.yml |
|---|---|---|
| Дифф | 1 пустой файл | изменение workflow (новый step или замена Check 5/5) |
| Запуск 40 task_bus-тестов в CI | да, существующим Check 5/5 | да, новым/изменённым чеком |
| Зависимости runner'а | никаких (stdlib unittest уже в Check 5/5) | pytest **не входит** в предустановку runner'а как контракт; нужен `pip install pytest` → сетевая зависимость, unpinned supply-chain поверхность (или pin+hash, отдельное сопровождение) |
| Контракт Check 5/5 | не меняется («validator + lint, stdlib only» — заголовок step'а) | меняется (stdlib-only контракт нарушается) |
| Гейт на изменение workflow | не требуется | **требуется**: DIRECTOR_ACCEPTANCE_P14_R1 прямо отмечает, что изменение `.github/workflows/hosted-ci.yml` — отдельный гейт с review/verify (NC-lint) |
| Бонус | symlink-негатив (F-2) исполняется позитивно на ubuntu | тот же бонус возможен, но ценой гейта |
| Риск регрессии | минимальный: маркер не меняет ни строки тестов и ни брокера | средний: новая CI-логика, установка пакетов, timeout/бюджет step'а |

**Почему A — минимальный и надёжный:**

1. `tests/task_bus/test_task_bus.py` — **чистый `unittest.TestCase`** (`import unittest`, `unittest.mock.patch`, `unittest.main`); pytest-специфики (fixtures, markers, `tmp_path`, `monkeypatch`) нет — проверено grep'ом по файлу. Следовательно, после появления package-маркера существующий `unittest discover` собирает и исполняет все 40 тестов без изменения тестов, брокера и workflow.
2. `tests/__init__.py` в main уже есть — добавлять его не требовалось (в директиве миссии кандидат A сформулирован как «tests/__init__.py + tests/task_bus/__init__.py»; первый уже существует с момента, когда Check 5/5 начал собирать tests/, поэтому фактический фикс — ровно один пустой файл).
3. Не трогается `.github/workflows/hosted-ci.yml` → не требуется отдельный workflow-гейт; NC-lint (Check 4/5) остаётся в неизменном контексте.
4. Не добавляется ни одной зависимости в CI — контракт «stdlib only» Check 5/5 сохранён; нет сетевых шагов и supply-chain поверхности.
5. Бонус (ожидание директивы подтвердилось): skip-условие symlink-теста — `OSError` на `path.symlink_to(...)`, на Linux unprivileged symlink разрешён → на ubuntu-агенте тест исполняется **позитивно** (broker возвращает `SMOKE_SYMLINK_DENIED`), т.е. F-2 закрывается live-покрытием на Linux. Проверено на нативном Linux-клоне (см. ниже): skip'а нет, тест проходит.

Вариант B не отклонён навсегда — pytest-чек может быть полезен позже (например, при переходе тестов на pytest-фичи), но это отдельный workflow-гейт по конвенции; в рамках DIR-1 он избыточен.

## Протокол локальной верификации

| # | Прогон | Платформа / subject | Результат | Лог |
|---|---|---|---|---|
| 1 | `python -m unittest discover -s tests -t .` (baseline, до фикса) | Windows, Python 3.11.8, worktree @ `e26672c` | **160 tests, OK** — task_bus не собран (parity с CI) | START-событие 0001 (command_refs) |
| 2 | `python -m unittest discover -s tests -t . -v` (после фикса) | Windows, Python 3.11.8, worktree @ `9f16e7b` | **200 tests, OK (skipped=1)** — +40 task_bus; skip = `test_symlink_candidate_and_local_smoke_are_rejected … 'Platform does not permit unprivileged symlinks'` (ожидаемо на Windows) | `logs/after-windows-discover-python3118.txt` |
| 3 | `python3 -m pytest tests/task_bus -q` (после фикса) | WSL Ubuntu 24.04, Python 3.12.3, worktree на /mnt/c @ `9f16e7b` | **40 passed** (symlink включён, skip'а нет) | транскрипт сессии + `logs/after-linux-native-9f16e7b.txt` (нативный прогон) |
| 4 | `python3 -m unittest discover -s tests -t .` (baseline Linux) | нативный Linux-клон в WSL @ `662e2ff` | **160 tests, OK** — базовая линия воспроизведена и на Linux | `logs/baseline-linux-662e2ff-discover.txt` |
| 5 | `python3 -m unittest discover -s tests -t .` + `python3 -m pytest tests/task_bus -q` (после фикса) | нативный Linux-клон в WSL, Python 3.12.3, git 2.43.0 @ `9f16e7b` | **discover: 200 tests, OK — 0 skip** (в т.ч. symlink-тест OK); **pytest: 40 passed** | `logs/after-linux-native-9f16e7b.txt` |

Прогон 5 — прямая CI-parity для ubuntu-агента: обычный checkout (не worktree, Linux-нативные пути) ⇒ ожидаемый итог Check 5/5 на hosted-ci: «Ran 200 tests, OK» без skip'ов (на CI-чекeате нет и артефакта «blobs not committed at HEAD yet», который skip'нулся в прогоне 2 WSL-worktree из-за Windows-путей gitdir worktree — на нативном клоне и на CI этот тест исполняется).

Примечание к прогону 2: единственный skip на Windows — известный F-2 (symlink-негатив); счёт 39 passed + 1 skipped совпадает с локальной регрессией Director'а на merge-коммите PR #20 (DIRECTOR_ACCEPTANCE_P14_R1, таблица «Каноническая регрессия»).

## Что изменилось (дифф фикс-коммита `9f16e7b`)

```text
tests/task_bus/__init__.py  (новый, пустой; package-маркер для unittest discovery)
```

Не изменялись: `tools/task_bus.py` (брокер), `.github/workflows/**`, `project/*.json` (state/plan), `experiments/**`, вердиктные документы, чужие `EX-*`.

## Ожидаемый эффект на hosted-ci (после merge)

- Check 5/5: «Ran 200 tests, OK» (было 160); 40 тестов брокера (`tools/task_bus.py`, blob `a3d0556717f3320e885f4092f242bed53bf0584f`) исполняются в live-CI на каждом PR/push.
- F-2 (REVIEWER_VERDICT §6): на ubuntu-агенте symlink-негатив исполняется позитивно — live-проверка отказа на symlink появляется на Linux; Windows-эквивалент (junction/reparse) остаётся опцией на будущее и не требуется для этого фикса.
- Остальные 4 чека hosted-ci — без изменений по содержанию (но проверены локально, см. событие 0003).

## Открытые пункты

- DIR-1 закрывается фактическим прогоном только после merge (зелёный Check 5/5 с «Ran 200 tests» на CI-логе) — merge/Human Gate вне этой ветки (оркестратор).
- Windows-эквивалент symlink-негатива (F-2, Windows-сторона) — по-прежнему в очереди P2.
- Вердикт `DIRECTOR_ACCEPTANCE_P14_R1.md` не редактировался; снятие DIR-1 из очереди — решением Director после зелёного CI.
