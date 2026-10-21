# EX-S17-STATIC-ASSEMBLY-HARDENING-R1 — summary

Work order: `WO-S17-STATIC-ASSEMBLY-HARDENING-R1` (issue [#66](https://github.com/rootfabric/NanoLab/issues/66), программа [#63](https://github.com/rootfabric/NanoLab/issues/63)).
Ветка: `work/s17-static-assembly-hardening-r1`, base = `0b9311c380a2d228be0bdb35701287a2b9e9339a` (tree `487335fbd4782825d6ab2d85674ad2ada7e4ff50`) — VERIFIED tip ремонта R3 (F01–F04 зелёные, independent Reviewer PASS).
Класс: `C0_SOFTWARE_ONLY`, 0 scientific runs, 0 network calls, 0 paid compute.

## 1. Точные HEAD/TREE

- **Тестируемый subject (exact tested head):** `e1c48f6cb1e81a3bb7ff7161c56ea3708604fbe6`, tree `724cb5ba7eb1b3c8db80d640d123977a5eb9e29e` — на нём выполнены полный unittest-прогон и оба harness-гейта.
- **Коммиты после него — docs-only evidence pack:** `966f2cc1267a20fba0c24dc84f19656c0ba10bfb` (events 0002–0003 + evidence-map) и текущий handoff-коммит (event 0004 + этот summary + строка WORK_QUEUE). Продукт-файлы после `e1c48f6` не менялись.
- START commit: `d9c3e0559532f4b8d2fcb4ae0f602c1a220ee1f0`; canonical main на момент старта: `513c4fa86470d939e9f9b7829e9c67c489c15a57`.

## 2. Что сделано (по deliverable)

1. **`scripts/knowledge_pack/assembly_cli.py`** — детерминированный OFFLINE CLI (argparse, stdlib + существующие импорты `knowledge_pack`/`hinge_family`):
   - `assemble`: входы = driver spec JSON + follower spec JSON + assembly spec JSON + опционально `--recipe` (обязан быть файлом, объявленным `interface_recipe_ref.path`, резолвится через `--recipe-base` — переиспользован `assembly_spec.assemble_artifacts(recipe_base=...)`); выход = `<assembly_id>.top` + `<assembly_id>.dat` + `receipt.json`, запись атомарная (temp + `os.replace`, очистка temp при отказе), sorted keys, фиксированный float-формат библиотеки, **никаких timestamps в байтах артефактов**.
   - `verify`: реверификация каталога по receipt — kind/status-проверки, sha256 cross-check обоих oxDNA-файлов, строгий reparse (`Topology.parse` + `check_chain_integrity`, `Configuration.parse`) с cross-check количеств; exit 0/1; одна строка статуса в stdout, без stdout-science.
   - Fail-closed границы: unknown args (argparse), отсутствующие/нечитаемые входы, oversized input JSON (>4 MiB), absolute/`..` outdir (out-of-tree), backslash, непустой существующий outdir, duplicate particle ids (один anchor-particle, привязанный двумя разными connection), `--recipe` при не-SOURCE_VERIFIED режиме, подмена recipe-файла, remote-only пины (offline: никогда не fetch), небезопасный `assembly_id`.
   - Exit codes: 0 = `ASSEMBLED_STATIC_ONLY` (3 артефакта) или честный `NOT_RECONSTRUCTED` (только receipt; **exit 0 — не научный PASS**), 1 = verify mismatch, 2 = отказ (BLOCKED_* receipt пишется как evidence; `.top`/`.dat` на failure-путях НИКОГДА не пишутся).
   - Claim-guard: статус вне `ASSEMBLY_STATUSES` или равный `ASSEMBLY_VALIDATED`/`MODEL_REPRODUCED` отказывается до записи.
2. **Пример CANDIDATE_DESIGN** `docs/examples/s17_static_assembly_example/` — синтетическая two-ODN пара (12 nt + точный 12-nt reverse-complement, одно non-covalent соединение, follower translation `[6,0,0]`), явно помечена CANDIDATE_DESIGN/HYPOTHESIS, НЕ реальные S17-последовательности; component+assembly specs, входные `.top`/`.dat`, README, закоммиченный `expected_receipt.json`; тест закрепляет байт-равенство receipt и byte-determinism двух прогонов.
3. **`tests/test_s17_static_assembly_cli.py`** — 31 тест: determinism (два прогона → идентичные sha256, устойчивость к PYTHONHASHSEED), verify-roundtrip, tampered artifact/receipt/unparseable/missing receipt, unknown arg, missing input, oversized input, absolute+traversal outdir, duplicate particle ids, recipe wrong bytes → `BLOCKED_INPUT`, подмена recipe, recipe при CANDIDATE_DESIGN, `NOT_RECONSTRUCTED` (structure-less follower + incapable ports) — чистый exit 0 с receipt-only каталогом, unsafe assembly_id, remote-pin offline-отказ, применение driver-трансформаций (library + CLI e2e), strictness рецепта.
4. **Minors независимого review ремонта R3** (в `scripts/knowledge_pack/assembly_spec.py`):
   - **(a) — выбран APPLY**: `_component_transform_params` делает pipeline role-симметричным; driver-side `unit_conversion`/`coordinate_transforms` применяются к driver-частицам (`assemble`/`assemble_artifacts`) и driver anchor-подсказкам (`_geometry_checks`); при отсутствии — identity (поведение 846 тестов не меняется). Альтернатива «REJECT loudly» отклонена (см. WO §Scope).
   - **(b)**: `_verify_interface_recipe` для `kind==SOURCE_VERIFIED` требует сегментные ключи и заявленный `overhang_segment` — пропуск cross-check больше невозможен (`BLOCKED_SOURCE`); `CANDIDATE_DESIGN` permissive; **`validate_component_spec` не менялся** (контракт PR #61: `[]` на валидной спеке).

## 3. Команды и результаты валидации (exact head `e1c48f6`)

| Команда | Результат |
| --- | --- |
| `python3 -m unittest discover -s tests -t .` | **Ran 877 tests — OK** (846 base + 31 новых; 4/4 falsifier зелёные) |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency` | `ok: true`, errors: [] |
| `PYTHONPATH=scripts python3 -m harness.workflow_lint` | `blocking: 0`, violations: 0 |
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-S17-STATIC-ASSEMBLY-HARDENING-R1` | `ok: true` (после evidence-pack коммитов) |
| CLI spot-probes | детерминизм 2 прогонов (идентичные sha256), verify roundtrip exit 0, tamper-детект exit 1×4, отказа-рецепты exit 2 |

## 4. Пример использования CLI

```bash
PYTHONPATH=scripts python3 -m knowledge_pack.assembly_cli assemble \
  --driver-spec docs/examples/s17_static_assembly_example/driver_component_spec.json \
  --follower-spec docs/examples/s17_static_assembly_example/follower_component_spec.json \
  --assembly-spec docs/examples/s17_static_assembly_example/assembly_spec.json \
  --input-root . \
  --outdir example-output/s17-static

PYTHONPATH=scripts python3 -m knowledge_pack.assembly_cli verify \
  --artifact-dir example-output/s17-static
```

## 5. Открытые риски

1. Ветка stacked на неслитой R3-цепочке (PR #59/#60/#68 не слиты) — порядок интеграции R2 → R3 → repair → эта ветка, либо rebase-only re-stack после их merge.
2. Правило duplicate particle ids — CLI-уровневая интерпретация класса из WO (один физический anchor-particle в двух разных connection); контракт библиотеки не менялся.
3. Реальная SOURCE_VERIFIED сборка остаётся заблокированной известной R3-REPAIR-ERRATUM-1 (21nt-окна follower против 20nt рецепта; вне scope этого WO).
4. `verify` не перепроверяет input-дайджесты receipt (входных файлов нет при verify); целостность держится на дайджестах собранных текстов + строгом reparse — задокументировано.

## 6. Инварианты

`project/state.json`, `project/plan.json`, `project/infra-state.json` не тронуты; frozen `docs/research/NANOLAB_REPRO*`, `releases/nl5*`, `experiments/**` не тронуты; пины `docs/research/S17_R3_*` не изменялись (read-only входы); falsifier-файл и R3-R2 фикстуры не модифицировались (новые тесты — только в новом файле); `mechanical_component_spec.py` и R1/R2 surfaces не тронуты; события append-only; без force-push. Claim ceiling `PINNED_IMPORT_VERIFIED` / `C0_SOFTWARE_ONLY`; честный `NOT_RECONSTRUCTED` реальной пары S17 сохранён.

## 7. Independent review — WAIT_EXTERNAL

Самопроверки и внутренние негативные пробы — не независимая приёмка. Одно next action: **fresh independent Reviewer** на tip ветки `work/s17-static-assembly-hardening-r1`, затем fresh exact-head Verifier, затем Human Gate (merge — решение владельца; PR открывает Director).
