# EX-PREP-S17-R3-REPAIR-R1 — summary

Work order: `WO-PREP-S17-R3-REPAIR-R1` (issue #62, parent PR #60 / EX-PREP-S17-R3).
Ветка: `work/prep-s17-r3-repair-r1`, base = faulty R3 head `2cf8297f10ab5ec98b8c8023ff76b39d92ef398b`.
Класс: `C0_SOFTWARE_ONLY`, 0 scientific runs, 0 network, 0 paid compute.

## 1. Что сделано

Исправлены четыре воспроизведённых independent adversarial review дефекта сборщика
(`scripts/knowledge_pack/assembly_spec.py`, единственный продукт-файл в ремонте):

- **R3-F01** — исполняемое соединение теперь требует порт с
  `connection_capable=true`, конкретными integer-якорями (не literal UNKNOWN, не
  bool, статус ≠ UNKNOWN) и orientation со статусом ≠ UNKNOWN
  (`_executable_port_violation`). Гейт стоит ПОСЛЕ структурного прохода, поэтому
  честный `NOT_RECONSTRUCTED` реальной пары S17 сохранён (закреплено тестом).
- **R3-F02** — `SOURCE_VERIFIED` проверяет рецепт фактически: безопасный
  относительный путь (без absolute/`..`/backslash), существование файла, SHA-256
  реальных байтов, UTF-8 JSON parse, kind рецепта, привязку каждого соединения к
  ровно одному элементу рецепта (явный `recipe_pair_ref` или join по pinned
  `chemistry.odn_name`), cross-check сегментов. Подделка digest/файла/пути
  никогда не собирает пару.
- **R3-F03** — единый transform-pipeline (unit factor → rotation → translation)
  для частицfollower И anchor-позиций (`_follower_transform_params`,
  `_transform_point`, `_transform_particle`); дублированный код в
  `assemble_artifacts` удалён; дигесты артефактов = дигестам receipt при поворотах.
- **R3-F04** — гибридизация привязана к заявленным exposed overhang-сегментам:
  оба сегмента заявлены (не UNKNOWN), ≥12 nt, точный reverse-complement матч
  пары, заявленные концы 5p/3p (same-end разрешён — pinned real S17 = 3p/3p),
  LNA-нотация `(LX)` срезается согласованно, сегмент обязан быть частью полной
  последовательности порта. Полный матч по ODN остался вторичной проверкой.
- Hardening: finite-проверки (translation, anchor_position, rotation, factor,
  band, threshold, assembly_box), bool-anchor reject, нечитаемый config с
  совпадающим digest → BLOCKED_INPUT.

`validate_component_spec` (mechanical_component_spec.py) сознательно НЕ менялся —
expectation PR #61 «валидатор компоненты проходит» сохранён; гейт живёт на
уровне исполняемой сборки.

## 2. RED → GREEN

- RED: falsifier-файл перенесён verbatim из review-only PR #61
  (`f0310f8e1f1ad691675363ca0528f3d7e3609104`), коммит `cd384dd`;
  на faulty base `2cf8297` все 4 теста падают — идентично hosted run
  [39124902081](https://github.com/rootfabric/NanoLab/actions/runs/39124902081)
  (808 tests / 4 FAILED).
- GREEN: коммит `82dddb0` (tree `5751fb36afd00e6c3ef9338b7212e48650918e61`) —
  все 4 falsifier-теста проходят без изменения ожиданий.

## 3. Валидация на exact head `82dddb0`

- `python3 -m unittest tests.test_s17_r3_fresh_review_falsifiers` → 4 tests OK.
- `python3 -m unittest discover -s tests -t .` → **846 tests OK**
  (804 базовых + 4 falsifier + 38 новых repair-тестов).
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency` → ok: true.
- `PYTHONPATH=scripts python3 -m harness.workflow_lint` → blocking: 0.
- `work_cli validate` EX-PREP-S17-R3-REPAIR-R1 и EX-PREP-S17-R3 → ok: true.

## 4. Долговременная находка (R3-REPAIR-ERRATUM-1)

Новая байт-уровневая верификация рецепта вскрыла ранее не замеченную
несогласованность в pinned R3 evidence: у 7 из 10 follower-портов
(`DFC-02..05,07,08,09`) `overhang_segment` — 21-nt окно, тогда как pinned рецепт
несёт точные 20-nt комплементы (`match_length_nt: 20`); driver-сторона
совпадает 10/10. Поведение fail-closed: такая пара отвергается; evidence-файлы
follower-спеки ВНЕ allowed paths ремонта и не менялись. Исправление (выравнивание
follower-окон до точных 20nt рецепта) — отдельный scoped change. На вердикт
`NOT_RECONSTRUCTED` не влияет (структурный отказ раньше).

## 5. Инварианты

`project/state.json`, `project/plan.json` не тронуты; frozen NL5 evidence не
тронуты; `mechanical_component_spec.py` и R1/R2 surfaces не тронуты; события
append-only; без force-push; PR #59/#60 не слиты. Claim ceiling
`PINNED_IMPORT_VERIFIED` / `C0_SOFTWARE_ONLY`; статическая сборка остаётся
`ASSEMBLED_STATIC_ONLY` + `GEOMETRY_UNVERIFIED`, никогда не
`ASSEMBLY_VALIDATED`.

## 6. Independent review — WAIT_EXTERNAL

Самопроверки — не независимая приёмка. Запрошено: **fresh Reviewer**, затем
**exact-head Verifier** на draft PR `work/prep-s17-r3-repair-r1` →
`work/prep-s17-r3-r1` (стек на PR #60, который стекается на PR #59; R2 не
каноничен). One next action: fresh independent Reviewer на repair-ветку.

## 7. Hosted CI evidence (append; 2026-10-18T14:29:09.658Z)

Workflow hostится только на PR→main, поэтому для точного repair-кода открыт
review-only evidence PR **#68** (`[DO NOT MERGE]`, head `review/prep-s17-r3-repair-ci-r1`
= tip PR #67, прецедент — закрытый PR #61). Результат: run
[39135996558](https://github.com/rootfabric/NanoLab/actions/runs/39135996558),
job `RC0 hosted validation (H0)` = **completed / success**, hosted
`unittest discover` = **846 tests OK**, включая все 4 adversarial falsifier'а
GREEN — hosted-парный контракт к failed run 39124902081 (4 FAILED на faulty
base). PR #68 будет закрыт без merge после записи evidence.
