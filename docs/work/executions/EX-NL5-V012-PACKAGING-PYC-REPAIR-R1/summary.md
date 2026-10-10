# EX-NL5-V012-PACKAGING-PYC-REPAIR-R1 — Summary

Статус: **READY_FOR_REVIEW** (0 scientific runs; packaging-only v0.1.2).

## Что сделано

1. **Дефект** (машинно воспроизведён на U2-платформе outenemy в
   `EX-INFRA3-U2-OUTENEMY-READINESS-R1`): `RELEASE_MANIFEST.json` пакета
   `nanolab-components-v0.1.1` содержал 7 записей
   `convention/nlbl_convention/__pycache__/*.cpython-310.pyc` —
   сгенерированные CPython-артефакты author-машины, не трекаемые git и
   отсутствующие в дереве. `reproduce.py verify` на любой свежей копии
   завершался fail-closed (exit 3) ровно на этих 7 записях (0 иных ошибок).
2. **Ремонт** (в пределах допущения контракта
   `ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §6 gate U2 — «bounded packaging
   v0.1.2 repair»):
   - `scripts/release/card_lint.py::_package_files` — исключены каталоги
     `__pycache__` и файлы `*.pyc` (единая точка для manifest create/verify);
   - `releases/nanolab-components-v0.1.2/` — копия v0.1.1; изменены ТОЛЬКО
     `VERSION` (0.1.2), `README.md`, `CITATION.cff`, `reproduction/README.md`
     и `RELEASE_MANIFEST.json` (регенерирован `card_lint.manifest_create`;
     35 файлов; 0 pyc-записей);
   - 3 регрессионных теста в `tests/test_release_contract.py`.
3. **Наука не тронута**: diff v0.1.2 vs v0.1.1 = ровно 5 разрешённых
   packaging-поверхностей; convention/, карточки, RIGHTS, схемы,
   протоколы — байт-в-байт идентичны
   (`evidence/v012-vs-v011-byte-diff-R1.txt`). F2/frozen artifacts не
   затронуты.

## Валидация (все на этой машине)

```text
fresh git-archive export → reproduce.py self-test  = verify ok, 0 errors,
                                                     plan ok, exit 0
                                                     (v0.1.1 на том же тесте = FAIL/7 pyc)
card_lint package (v0.1.2)                         = ok, version 0.1.2
check-consistency                                  = ok (exit 0)
workflow_lint                                      = blocking 0
unittest (полный набор)                            = 608 OK (605 base + 3 new)
```

## Evidence

- `evidence/v012-fresh-export-selftest-R1.json` — приёмочный self-test
  свежего export.
- `evidence/v012-vs-v011-byte-diff-R1.txt` — полное diff-доказательство
  byte-identity науки.
- `evidence/v012-card-lint-package-R1.json` — lint-отчёт пакета v0.1.2.

## Границы

Статусы не менялись; `releases/nanolab-components-v0.1.1` остаётся immutable
historical release; confirmatory runs = 0; merge = Human Gate.

## Next action

Fresh independent review + exact-head verify ветки
`work/nl5-v012-packaging-pyc-repair-r1`, затем Human Gate.
