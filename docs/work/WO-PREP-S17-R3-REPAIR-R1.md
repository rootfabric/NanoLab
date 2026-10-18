# WO-PREP-S17-R3-REPAIR-R1 — четыре RED→GREEN гейта сборщика

**Parent:** PR #60 (`WO-PREP-S17-R3`, faulty exact HEAD `2cf8297f10ab5ec98b8c8023ff76b39d92ef398b`), GitHub issue [#62](https://github.com/rootfabric/NanoLab/issues/62), программа работ [#63](https://github.com/rootfabric/NanoLab/issues/63).

**Класс исполнения:** scoped `C0_SOFTWARE_ONLY`, узкий repair, 0 scientific runs, 0 paid compute. Human Gate для merge не отменяется.

**Review evidence:** review-комментарий + Repair Map в PR #60, CI run [39124902081](https://github.com/rootfabric/NanoLab/actions/runs/39124902081) (808 тестов, 4 FAILED = F01–F04, исходные 804 OK), review-only PR #61 (закрыт, не слит; test-only head `f0310f8e1f1ad691675363ca0528f3d7e3609104`).

## Воспроизведённые дефекты (требуемые исправления)

- **R3-F01 — порт без подтверждённого соединения.** Сборщик принимает порт с
  `connection_capable=false` и UNKNOWN anchors/orientation и выдаёт
  `ASSEMBLED_STATIC_ONLY`. Требуется: соединение, исполняемое сборщиком,
  разрешено только при `connection_capable=true`, конкретных anchor-индексах
  (не literal UNKNOWN, статус не UNKNOWN) и orientation со статусом не UNKNOWN.
  Честный `NOT_RECONSTRUCTED` для реальной пары S17 (follower topology/config
  отсутствуют) обязан сохраниться.
- **R3-F02 — подмена рецепта.** `SOURCE_VERIFIED` принимает вымышленный SHA-256
  и несуществующий recipe-файл. Требуется: фактическая проверка байтов рецепта
  на диске, SHA-256, соответствия рецепта заявленным connections/портам и
  безопасности путей (относительный путь без обхода, никакой записи).
- **R3-F03 — неверная геометрия.** Поворот follower не применяется к anchor
  позициям при проверке расстояний (учитывается только translation+unit factor),
  из-за чего валидная повёрнутая геометрия даёт ложный `BLOCKED_GEOMETRY`.
  Требуется: единый pipeline преобразований (unit factor → rotation →
  translation) для частиц И anchor-позиций, тесты 90°/180° и совместности с
  unit conversion.
- **R3-F04 — неверная проверка гибридизации.** Комплементарность определяется
  по полной последовательности ODN, даже когда заявленные выступающие
  overhang-сегменты несовместимы. Требуется: проверка именно предназначенного
  интерфейса — точный reverse-complement матч заявленных overhang-сегментов,
  согласованность 5′/3′-концов, LNA-нотация через общий strip; сегмент обязан
  быть частью полной последовательности порта; отсутствие заявленного сегмента
  = `BLOCKED_INFERRED_INTERFACE` (fail-closed).

## Обязательные шаги

1. Портировать `tests/test_s17_r3_fresh_review_falsifiers.py` из review-only PR #61
   (head `f0310f8e1f1ad691675363ca0528f3d7e3609104`) в основную тестовую матрицу
   без изменения ожиданий.
2. Доказать **RED на exact faulty HEAD `2cf8297`** (все 4 falsifier-теста падают)
   и **GREEN на новом repair HEAD** (все проходят), сохранив полный прогон
   регрессии.
3. Расширить негативную матрицу: ошибочные anchor-индексы, повреждённые файлы,
   некорректная геометрия (NaN/Inf/нечисловые), несовместимые единицы, повторные
   идентификаторы, отсутствующие источники, недоказанные интерфейсы, опасные
   пути рецепта, подделанный дайджест рецепта, несоответствие рецепта
   connections, 5′/3′-polarity, LNA.
4. Сохранить: sequence-level 10-pair evidence S17, claim ceiling
   `PINNED_IMPORT_VERIFIED`, честный `NOT_RECONSTRUCTED` для реального follower,
   `GEOMETRY_UNVERIFIED` вместо безусловного PASS; никаких искусственных
   молекулярных связей и scientific runs.
5. Полные команды: `python3 -m unittest discover -s tests -t .`;
   `PYTHONPATH=scripts python3 -m harness.cli check-consistency`;
   `PYTHONPATH=scripts python3 -m harness.workflow_lint`;
   `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-S17-R3-REPAIR-R1`.
   Зафиксировать exact tested HEAD/TREE и вывод.
6. Опубликовать repair-ветку non-force push; HANDOFF с точным HEAD/TREE,
   результатами и next action (fresh Reviewer → exact-head Verifier → Human Gate).

## Разрешено/запрещено

Разрешено: scripts/knowledge_pack/assembly_spec.py; tests/test_s17_r3_assembly.py;
tests/test_s17_r3_fresh_review_falsifiers.py; docs/work/WO-PREP-S17-R3-REPAIR-R1.md;
docs/work/WORK_QUEUE.md (append-only); docs/work/executions/EX-PREP-S17-R3-REPAIR-R1/**;
docs/work/executions/EX-PREP-S17-R3/events/0006-*.json (append-only cross-ref).

Запрещено: scripts/knowledge_pack/mechanical_component_spec.py и остальные
R1/R2 surfaces (contract.py, import_validation.py, s17_*.py), project/state.json,
project/plan.json, frozen NL5 artifacts, history rewrite, direct main push,
merge PR #59/#60, научные запуски.
