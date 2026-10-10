# Work Order WO-NL5-V012-PACKAGING-PYC-REPAIR-R1 — Bounded packaging repair v0.1.2 (manifest pyc-artifact exclusion; science byte-identical)

Статус: **IN_PROGRESS** (execution `EX-NL5-V012-PACKAGING-PYC-REPAIR-R1`, ветка
`work/nl5-v012-packaging-pyc-repair-r1`, base `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad`
= canonical main HEAD / merge PR #52). Родительская линия: NL5 release
(NL5-001/NL5-002 release-contract line; прецедент bounded packaging repair —
v0.1.1 в `WO-NL5-002-C-R1`, PR #43). Дочерний факт-источник: находка
`EX-INFRA3-U2-OUTENEMY-READINESS-R1` (проверка release package на внешней
платформе U2, 2026-10-10). Track: work/release. Risk: **LOW-MEDIUM**. Claim
ceiling: **C0_SOFTWARE_ONLY**.

Дата открытия: 2026-10-10. Trigger: контракт R2 §6 gate U2 прямо допускает
«documented v0.1.1 pyc findings … либо bounded packaging v0.1.2 repair».
Находка механически воспроизведена и локализована на U2: свежий export пакета
v0.1.1 из git → `reproduce.py self-test` verify FAIL ровно на 7
`__pycache__/*.pyc`-записях манифеста (файлы не трекаются git и в дереве
отсутствуют; корень — `card_lint._package_files` включал CPython-артефакты,
сгенерированные на author-машине в момент сборки v0.1.1).

## 1. Проблема

`RELEASE_MANIFEST.json` v0.1.1 содержит 7 записей
`convention/nlbl_convention/__pycache__/*.cpython-310.pyc`. Это
platform/CPython-версионные артефакты: (а) их нет в git — `reproduce.py
verify` fail-closed (exit 3) на ЛЮБОЙ свежей копии пакета; (б) их наличие в
манифесте маскирует реальные повреждения пакета шумом; (в) внешняя сессия не
может отличить документированный finding от подмены без внепротокольного
знания.

## 2. Scope (allowed paths)

```text
docs/work/WO-NL5-V012-PACKAGING-PYC-REPAIR-R1.md
docs/work/executions/EX-NL5-V012-PACKAGING-PYC-REPAIR-R1/**
releases/nanolab-components-v0.1.2/**
scripts/release/card_lint.py
tests/test_release_contract.py              (регрессионный тест фильтра)
docs/work/WORK_QUEUE.md                     (одна surface-sync строка)
```

## 3. Вне scope (запрещено)

- Любые изменения научного содержания: convention/ (analyze_hinge.py,
  nlbl_convention/, arm-manifests, OBSERVABLE_CONVENTION), карточки, RIGHTS,
  схемы, протоколы — БАЙТ-ИДЕНТИЧНЫ v0.1.1.
- Изменение frozen package F2 (protocol/contract/seed record), FROZEN_R1
  history, HG-B записей, verdicts R/V, canonical статусов.
- Модификация или удаление releases/nanolab-components-v0.1.1 (superseded
  для дистрибуции, исторический artifact остаётся).
- Confirmatory scientific runs (0 научных запусков в этом WO).
- Merge в main (Human Gate); draft PR разрешён.

## 4. Change spec (packaging-only)

1. `scripts/release/card_lint.py`: `_package_files()` исключает каталоги
   `__pycache__` и файлы `*.pyc` (generated CPython artifacts never enter a
   release manifest) — единая точка для manifest_create и manifest_verify.
2. `releases/nanolab-components-v0.1.2/` = копия v0.1.1 с изменениями ТОЛЬКО:
   `VERSION` = 0.1.2; README.md (заголовок + changelog-строка 0.1.2);
   CITATION.cff version; reproduction/README.md (заголовок контракта +
   changelog-строка); RELEASE_MANIFEST.json — регенерирован инструментом
   `card_lint.manifest_create` (не вручную), без pyc, package_version 0.1.2.
3. Регрессионный тест: manifest_create/`_package_files` не включают
   `__pycache__/*.pyc`.

## 5. Validation plan

- `card_lint package` на v0.1.2 → ok (включая manifest_verify).
- Свежий export v0.1.2 из git (`git archive`) → `reproduce.py self-test` →
  verify ok=true, 0 errors — главное приёмочное правило (то, которое падало
  на v0.1.1).
- Байт-идентичность науки: все файлы v0.1.2 vs v0.1.1 идентичны кроме
  {VERSION, README.md, CITATION.cff, reproduction/README.md,
  RELEASE_MANIFEST.json}; convention/ идентична целиком.
- Полный unittest набор; `check-consistency`; `workflow_lint`.

## 6. Честные границы

Статусы не меняются; v0.1.1 остаётся историческим release; dispatch
научной кампании не затрагивается. F2 не изменяется: пакет v0.1.2 —
дистрибуционная поверхность U2-ноги, научные файлы байт-в-байт те же.
