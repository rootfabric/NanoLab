# REVIEWER VERDICT — EX-DIR1-R1 (независимый REVIEWER, контроль фикса DIR-1)

**Work Order:** DIR-1 «unittest discover не собирает broker-suite `tests/task_bus` в hosted-ci Check 5/5»
**Execution:** `EX-DIR1-R1`, ветка `control/ci-taskbus-coverage-r1`
**Subject:** `ee3dca13a598687a92f1d03c597e587f2d8c7eef` (tip, records-only; фикс-субъект `9f16e7ba5d216f4a3982b98177ad147e3bcfb712`; base `e26672c1a0e0344269ff0dc4d15374ec583c7192` = canonical `main`)
**Review-ветка:** `review/ci-taskbus-coverage-r1` (worktree `C:\NanoLab\review-dir-1`, checkout exact subject `ee3dca1`)
**PR:** rootfabric/NanoLab#36 — OPEN, head `ee3dca1`, MERGEABLE; merge в `main` — Human Gate, **не выполнялся**
**Дата вердикта:** 2026-09-11 (раунд R1)
**Метод:** проверка исполнением (независимые пробы в чистом worktree); контекст имплементёра не использовался; self-acceptance исключён по роли

---

## Вердикт: **PASS**

Контрольный фикс выполнен минимально и точно: один пустой package-маркер `tests/task_bus/__init__.py` возвращает 40 broker-тестов в hosted-ci Check 5/5; брокер, workflow, policies и science-поверхности не тронуты; records полны и валидны; live-CI на PR зелёный с искомым счётом. Findings — только 2 NOTE, **не блокирующие** (см. ниже).

---

## 1. Минимальность диффа `e26672c..ee3dca1` — ✅

`diff --name-status` = **12 файлов, все `A`** (ни одного M/D):

- код: `tests/task_bus/__init__.py` — blob `e69de29` (канонический пустой, 0 байт); фикс-коммит `9f16e7b` добавляет ровно этот один файл (`diff --stat 662e2ff..9f16e7b` = 1 file, 0 insertions);
- records: `docs/evidence/DIR1/` (README + 3 лога), `docs/work/executions/EX-DIR1-R1/` (passport, branch-passport, events 0001–0004, summary).

Фильтр по `diff --name-only` вне `docs/` и `tests/task_bus/__init__.py` — **пусто**: `tools/`, `.github/workflows/`, policies, state-файлы не изменялись.

## 2. `unittest discover -s tests -t .` — счёт и реальное исполнение — ✅

| Проба (независимая) | Subject | Результат |
|---|---|---|
| discover, Windows, Python 3.11.8 | `ee3dca1` (= subject content) | **Ran 200 tests, OK (skipped=1)** |
| discover, Windows (temp worktree) | `e26672c` (baseline) | **Ran 160 tests, OK** — task_bus не собирался |
| discover `-s tests/task_bus`, verbose | `ee3dca1` | **Ran 40 tests, OK (skipped=1)**, ~45 c — git-integration тесты **исполняются**, не collected-only |

Прирост ровно +40; единственный skip — известный платформенный F-2 (unprivileged symlinks на Windows), 39 passed + 1 skip — parity с эталонной регрессией (`DIRECTOR_ACCEPTANCE_P14_R1`). Причина базовой линии воспроизведена: без `__init__.py` discovery не заходит в `tests/task_bus` ни на Windows, ни на Linux.

## 3. Брокер не изменён — ✅

`git rev-parse ee3dca1:tools/task_bus.py` = **`a3d0556717f3320e885f4092f242bed53bf0584f`** — совпадает с заявленным префиксом `a3d05567…` и с base `e26672c:tools/task_bus.py` (байт-в-байт идентичен).

## 4. Records `EX-DIR1-R1` — ✅

- `work_cli validate` → `ok: true`, `HANDOFF_READY`, `passport_sha256 f4bc96f16050fc90f9a3701ef04ea798df478913130191df5f61ceeaf4b8c6db`;
- `work_cli close` → `ok: true` (exit 0): терминальный `HANDOFF_COMPLETED` + `summary.md` на месте;
- события: `WORK_ORDER_STARTED → IMPLEMENTATION_COMMITTED → VALIDATION_RECORDED → HANDOFF_COMPLETED`; post-terminal corrections нет;
- паспорт: `base_sha` = `e26672c…`, `branch` = `control/ci-taskbus-coverage-r1`, `allowed_paths` = ровно фактически изменённые области; `claim_class C0_SOFTWARE_ONLY` не превышен;
- локальный прогон Check 3/5 parity: все каталоги `EX-*` репозитория валидны, 0 failures.

## 5. Live-CI на PR #36 — ✅

- run **34588996229** «RC0 hosted validation (H0)» (ubuntu-latest, hosted route): **conclusion SUCCESS**, завершён 2026-09-11T10:24:18Z;
- лог Check 5/5: `python3 -m unittest discover -s tests -t . -v` → **«Ran 200 tests in 7.769s» → «OK»** — 0 skip на Linux, как предсказано в records;
- Check 1/5: 742 tracked JSON OK (2 pinned negative-фикстуры digest-OK); Check 3/5: все `EX-*` VALIDATE, включая новый `EX-DIR1-R1`; Check 4/5: NC-lint violations = 0;
- `GITHUB_SHA` рана `627b5466…` — штатный merge-коммит PR-роута; `git merge-tree e26672c ee3dca1` → дерево `c37ae31a…` **== дерево `ee3dca1^{tree}`**: зелёный ран валидировал ровно содержимое subject.

---

## NOTE (не блокирующие)

1. **N-1:** счёт «200» держится на breadth-first discovery; при появлении новых test-подкаталогов каждому нужен свой `__init__.py`, иначе тесты снова выпадут молча. Кандидат на механизированный контроль (например, lint «test-dir without __init__.py») в будущей пакетной ревизии.
2. **N-2:** Windows-эквивалент symlink-негатива (junction/reparse) остаётся открытым пунктом P2 — вне scope данного WO, корректно отражён в records.

## Итог

**PASS.** Fix subject `9f16e7b` точен, минимален и проверен исполнением локально (160→200, 40 broker-тестов реально исполняются) и в live-CI («Ran 200 tests», SUCCESS). Merge в `main` — Human Gate оркестратора; данный review merge не выполнял.
