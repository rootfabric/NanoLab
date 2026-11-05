# FLOW-R1: проверка mode/type обеих сторон исключения

Результат: устранён узкий defect независимого Reviewer; это candidate repair, не независимая приёмка.

Exact code subject HEAD: `ff35e283985f1eed1bacda9a3b3be191782e3700`; TREE: `9f54fc28c2c954c2e55ff706e6baac9fb8e280af`. Base: `0d8537cc368dc03ee39a543c835f72c40b651ae6`. Branch: `repair/flow-publication-mode-r1`. Последующая запись handoff меняет только собственные execution records.

`compare()` теперь требует `100644 blob` для head и любого существующего base entry исключаемого publication path. Отсутствующий base допускается для добавленного обычного report; прежние status/event/path ограничения сохранены. Executable или symlink на любой стороне перехода не получают publication-only equivalence.

## Проверки

- Red: `python3 -m unittest tests.test_flow_throughput.ReviewImpactTests.test_existing_report_mode_and_type_transitions_require_full_review -v` — exit 1 до fix; `100755 → 100644` ошибочно давал `PUBLICATION_ONLY_CANDIDATE`. Лог: `evidence/red.txt`.
- Green: `python3 -m unittest tests.test_flow_throughput -v` — 56 tests, OK; `evidence/green-flow.txt`.
- Full regression: `python3 -m unittest discover -s tests -t . -v` — 1028 tests, 31.951 s, OK; `evidence/green-all-tests.txt`.
- `PYTHONPATH=scripts python3 -m harness.batch_validate json --root .` — OK, 1523 JSON, 4 pinned non-JSON fixtures; `evidence/json-check.json`.
- `PYTHONPATH=scripts python3 -m harness.batch_validate executions --root .` — OK, 69 execution directories до terminal handoff; итоговый собственный record проверен после finish.
- `git diff --check` — OK.

Regression покрывает `100755 ↔ 100644`, symlink ↔ regular, а также сохраняет candidate для существующего обычного report update и ранее существовавший positive case нового report. Scientific runs/inputs/acceptance, trust policy и чужие reviewer records не менялись. Push/merge не выполнялись; публикация — Director. Полный CI интеграционного candidate остаётся обязанностью интегратора.

Оставшийся риск: независимый Reviewer ещё должен проверить repair на точном subject; HIGH verification исходного FLOW package остаётся отдельной ролью. Следующее действие: тот же независимый Reviewer выполняет recheck `ff35e283985f1eed1bacda9a3b3be191782e3700` и отдельно проверяет delta этого handoff.
