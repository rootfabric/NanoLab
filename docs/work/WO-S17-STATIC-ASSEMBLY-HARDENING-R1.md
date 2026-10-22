# WO-S17-STATIC-ASSEMBLY-HARDENING-R1 — детерминированный OFFLINE CLI сборки + Evidence Receipt

**Parent:** PREP-S17 line (`WO-PREP-S17-R3-REPAIR-R1`, verified head `0b9311c380a2d228be0bdb35701287a2b9e9339a`), GitHub issue [#66](https://github.com/rootfabric/NanoLab/issues/66), программа работ [#63](https://github.com/rootfabric/NanoLab/issues/63).

**Класс исполнения:** scoped `C0_SOFTWARE_ONLY`, 0 scientific runs, 0 network calls, 0 paid compute. Merge в `main` — Human Gate (Director открывает PR; IMPLEMENTER PR не открывает).

**База:** worktree `/home/rdpuser/NanoLab/s17-assembly-hardening`, ветка `work/s17-static-assembly-hardening-r1`, base_sha = `0b9311c380a2d228be0bdb35701287a2b9e9339a` (tree `487335fbd4782825d6ab2d85674ad2ada7e4ff50`) — VERIFIED tip ремонта R3 (F01–F04 зелёные, 846 tests OK, independent Reviewer PASS).

## Цель

Минимальный детерминированный OFFLINE путь «MechanicalComponentSpec + AssemblySpec → экспорт oxDNA topology/config + Evidence Receipt» через CLI на stdlib: подкоманды `assemble` и `verify`, fail-closed границы, байт-в-байт воспроизводимые артефакты (без timestamps в байтах артефактов), честный claim ceiling (`ASSEMBLED_STATIC_ONLY` / `NOT_RECONSTRUCTED` / `BLOCKED_*` из `assembly_spec.ASSEMBLY_STATUSES`, note `GEOMETRY_UNVERIFIED`, никогда `ASSEMBLY_VALIDATED`).

## Scope (bounded deliverables)

1. `scripts/knowledge_pack/assembly_cli.py` — новый offline CLI (argparse, stdlib + существующие импорты `knowledge_pack`/`hinge_family`):
   - `assemble`: входы = driver spec JSON + follower spec JSON + assembly spec JSON + опционально `--recipe` (+ `--recipe-base`), выходной `--outdir`; запись `topology` + `dat config` + `receipt.json` атомарно (temp + rename, очистка при отказе); recipe резолвится относительно `--recipe-base` (переиспользование `assembly_spec.assemble(recipe_base=...)`).
   - `verify`: реверификация каталога артефактов по receipt (sha256 cross-check + строгий reparse oxDNA-текста через `hinge_family`-парсеры), exit 0/1, без stdout-science.
   - Fail-closed границы: неизвестные аргументы, отсутствующие файлы, oversized input JSON (> 4 MiB), absolute/`..` out-of-tree `--outdir`, duplicate particle ids (один particle-index порта, привязанный двумя разными connection), recipe при mode CANDIDATE_DESIGN (противоречивый вход) — каждый отказ = чистый exit code + stderr, никаких частичных артефактов.
   - Exit codes: 0 = детерминированно исполнено (в т.ч. честный `NOT_RECONSTRUCTED` с receipt; exit 0 НЕ научный PASS), 2 = отказ/граница (в т.ч. `BLOCKED_*` receipt), 1 = verify mismatch.
2. `docs/examples/s17_static_assembly_example/` — пример-CANDIDATE_DESIGN (маленькая синтетическая two-ODN пара, в файлах явно помечена CANDIDATE_DESIGN/HYPOTHESIS; НЕ реальные последовательности S17): driver+follower component specs + assembly spec + входные .top/.dat + expected receipt; end-to-end тест CLI с byte-determinism (два прогона → идентичные sha256).
3. `tests/test_s17_static_assembly_cli.py` — матрица: happy-path determinism, verify-roundtrip, tampered artifact/receipt, recipe-with-wrong-bytes (BLOCKED_INPUT), out-of-tree outdir, oversized input, missing input, duplicate particle ids, NOT_RECONSTRUCTED path, отсутствие .top/.dat на всех failure-путях.
4. Свёрнутые minors независимого review ремонта R3 (обе правки в `scripts/knowledge_pack/assembly_spec.py`):
   - **(a) driver-side unit_conversion/coordinate_transforms** — ВЫБРАНО: **APPLY** (предпочтительный вариант). Тот же shared transform-pipeline (`_component_transform_params`, unit factor → rotation → translation) применяется к driver-частицам и driver anchor-подсказкам, когда driver-трансформация заявлена; при отсутствии — identity (поведение 846 существующих тестов не меняется). Альтернатива «REJECT loudly» не выбрана: она сужает контракт без необходимости, а symmetric-apply устраняет причину (молчаливое игнорирование) и сохраняет валидатор без изменений.
   - **(b) SOURCE_VERIFIED strictness** — в `_verify_interface_recipe` recipe-entry без ключей `driver_segment`/`follower_segment` или порт без заявленного `overhang_segment` больше НЕ пропускают segment cross-check молча: для `kind==SOURCE_VERIFIED` это `BLOCKED_SOURCE` (fail-closed). `CANDIDATE_DESIGN` остаётся permissive (рецепт не проверяется). `validate_component_spec` НЕ меняется (контракт PR #61: `[]` на валидной спеке).

## Разрешено/запрещено

Разрешено: `scripts/knowledge_pack/assembly_cli.py` (новый); `scripts/knowledge_pack/assembly_spec.py` (только minors (a)/(b)); `tests/test_s17_static_assembly_cli.py` (новый); `docs/examples/s17_static_assembly_example/**` (новое); `docs/work/WO-S17-STATIC-ASSEMBLY-HARDENING-R1.md`; `docs/work/WORK_QUEUE.md` (append-only); `docs/work/executions/EX-S17-STATIC-ASSEMBLY-HARDENING-R1/**`.

Запрещено: `project/state.json`, `project/plan.json`, `project/infra-state.json`; frozen `docs/research/NANOLAB_REPRO*`; `releases/nl5*`; `experiments/**`; пины `docs/research/S17_R3_*` (read-only входы); falsifier-файл и R3-R2 тест-фикстуры (только ADDING new tests, без модификации существующих); `scripts/knowledge_pack/mechanical_component_spec.py` и прочие R1/R2 surfaces; `scripts/harness/**`; history rewrite; force-push; direct main push; научные запуски; сетевые вызовы.

## Бюджет

Local Python only; 0 network fetches; 0 scientific runs; 0 paid compute; полный unittest-прогон + 3 harness-гейта. Ограничение размера входных JSON: 4 MiB (fail-closed).

## Инварианты и claim ceiling

`PINNED_IMPORT_VERIFIED` / `C0_SOFTWARE_ONLY`. Статусы вывода CLI — только из `assembly_spec.ASSEMBLY_STATUSES`; геометрия — `GEOMETRY_UNVERIFIED`/`NOT_PERFORMED`/`GEOMETRIC_CONFLICT`; `ASSEMBLY_VALIDATED` и `MODEL_REPRODUCED` никогда не пишутся (в т.ч. guard-скан байтов receipt). Timestamps — только в evidence (события), НЕ в байтах артефактов. Честный `NOT_RECONSTRUCTED` реальной пары S17 сохраняется. Артефакты — детерминированные файловые операции, никогда не доказательство гибридизации/функции.

## Валидационный гейт перед handoff

`python3 -m unittest discover -s tests -t .` (все зелёные; отчёт точного числа — ожидается 846 + новые); `PYTHONPATH=scripts python3 -m harness.cli check-consistency` → ok; `PYTHONPATH=scripts python3 -m harness.workflow_lint` → blocking 0; `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-S17-STATIC-ASSEMBLY-HARDENING-R1` → ok. Push всех коммитов non-force.
