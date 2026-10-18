# EX-PREP-S17-R3 — Summary (handoff)

Work Order: `WO-PREP-S17-R3` — «DNA Driver–Follower Molecular Interface & Static Assembly».
Ветка: `work/prep-s17-r3-r1` (stacked на HEAD PR #59 `26c4cd51`; R2 **не слит** — merge = Human Gate).
Implementation HEAD: `49be26701596032bb0924f56a33dab536a5f9ffe` (tree `b72e567914b10de96063f7e4d35db86a3e6ec89c`).
Бюджет: сеть 48.3/256 MiB, scratch <200 MiB/2 GiB, scientific runs **0**.

## 1. Результат (executive)

1. **Молекулярный интерфейс driver–follower установлен и подтверждён на уровне
   последовательностей** (`SOURCE_CONFIRMED`): соединение = гибридизация **10 уникальных
   комплементарных ssDNA overhang-пар** (5 на arm, осевые оконечности arm).
   Все 20 connecting ODN восстановлены из pinned `Suppl. Dataset S1 V3.docx`
   (sha256 `dc3cc6c5…` = R1-пин) и машино-проверены: каждая пара — точный
   **20-nt reverse-complement match**, паросочетание строго уникально
   (второй кандидат ≤8 nt). 4 driver ODN несут по 3 LNA — согласуется с Methods.
2. **Реальная S17 D–F статическая сборка: `NOT_RECONSTRUCTED`** — follower-структура
   (topology/configuration/design) не опубликована ни в одном из проверенных источников
   (Nanobase 196, полные CD-перечисления Zenodo 8248808 из R2, sulcgroup/hinges — только
   угловые ряды, supplementary). Индексные якоря оверхэнгов в nNE.top — `UNKNOWN`
   (placeholder-последовательности). Receipt `S17_R3_ASSEMBLY_RECEIPT.json` фиксирует
   blocked inputs явно; связь не изобретается.
3. **Первые исполняемые контракты сборки созданы и протестированы**:
   `MechanicalComponentSpec v1` + `AssemblySpec v1` + минимальный детерминированный
   fail-closed двухкомпонентный сборщик (SOURCE_VERIFIED / CANDIDATE_DESIGN).
   Полный программный цикл доказан на синтетической паре (`ASSEMBLED_STATIC_ONLY` /
   `GEOMETRY_UNVERIFIED`, детерминированно, валидный oxDNA-вывод).
4. **Claim ceiling соблюдён**: `PINNED_IMPORT_VERIFIED` / `C0_SOFTWARE_ONLY`.
   Статическая сборка ≠ `ASSEMBLY_VALIDATED`, ≠ передача движения/функция/пригодность.
   `NL6 ACCEPTED` / `NL7 ACCEPTED` / `ASSEMBLY_VALIDATED` / `MODEL_REPRODUCED` —
   не объявляются.

## 2. Проверенные научные факты (SOURCE_CONFIRMED)

- Соединение — 10 overhang-пар; 2 пары 5'-оверхэнги (D-89, D-153), остальные 3';
  пары соответствуют Suppl. Fig. 5a (осевые оконечности arm, helices 0–17, «flip»).
- Driver = nNE: pins `nNE.top` `71eca286…`, `nNE.dat` `b0722a5b…` (CONTENT_VERIFIED).
- Follower-варианты F / F-soft-hinge / F-ss-hinge: 10 connecting ODN общие;
  структура не опубликована.
- Экспериментальные факты (как опубликовано, без моделей): сборка equimolar 30 °C 2 h;
  TEM yield D–F 60 % ± 20 %; медиана угла 64.73° → 51.66° под транскрипцией (P = 8×10⁻⁶⁴).

## 3. Системные артефакты

| Файл | Назначение |
|---|---|
| `docs/research/S17_R3_INTERFACE_AUDIT.md` | Аудит интерфейса: pin-таблица, F1–F10, 10 пар, UNKNOWN/негативы, ответы на миссию |
| `docs/research/S17_R3_COMPONENT_DRIVER.json` | Spec драйвера (nNE): pins, 10 портов (все `connection_capable=false`, basis UNKNOWN) |
| `docs/research/S17_R3_COMPONENT_FOLLOWER.json` | Spec follower: sequence-level только, структура честно UNKNOWN |
| `docs/research/S17_R3_ASSEMBLY_SPEC.json` | Assembly spec реальной пары (SOURCE_VERIFIED, recipe-pinned) |
| `docs/research/S17_R3_ASSEMBLY_RECEIPT.json` | Receipt: `NOT_RECONSTRUCTED`, детерминированный |
| `docs/research/S17_R3_SOURCE_GAPS.md` | Гэпы G1–G6 + порядок закрытия |
| `scripts/knowledge_pack/mechanical_component_spec.py` | Контракт MechanicalComponentSpec v1 |
| `scripts/knowledge_pack/assembly_spec.py` | AssemblySpec v1 + сборщик |
| `tests/test_s17_r3_component_spec.py` | 22 offline-теста контракта/рецепта |
| `tests/test_s17_r3_assembly.py` | 36 offline-тестов сборщика (позитив + 26 классов негативов) |
| `evidence/s17-r3-df-interface-recipe.json` | Машиночитаемый рецепт 10 пар (sha256 `5f485b0a…`) |
| `evidence/s17-r3-fetch-manifest.json` | 12 fetch-записей, 48.3 MiB, в бюджете |
| `evidence/s17-r3-synthetic-assembly-receipt.json` | Позитивный synthetic-прогон (durable evidence) |
| `evidence-map.json` | E1–E13: индекс evidence для review |

## 4. Валидация (exact HEAD `49be267`)

- `python3 -m unittest discover -s tests -t .` → **804 tests OK** (746 база + 58 R3).
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency` → **ok: true**.
- `PYTHONPATH=scripts python3 -m harness.workflow_lint` → **blocking: 0**.
- `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-S17-R3` → **ok: true**.

Инварианты: `project/state.json`, `project/plan.json` — байт-идентичны базе;
frozen NL5 evidence и R1/R2 surfaces не тронуты; WORK_QUEUE — append-only;
большие raw-файлы не вендорились; PR #59 не слит.

## 5. Открытые риски / ограничения

- Все индексные якоря интерфейса — `UNKNOWN` до появления design-файлов follower/nNE
  с connecting ODN (см. `S17_R3_SOURCE_GAPS.md`, G1–G4).
- Геометрия проверена только на синтетической паре; результат `GEOMETRY_UNVERIFIED`
  честно маркирует coarse-скан, не доказательство контакта.
- `BACKBONE_CONTINUATION` в v1 сознательно не исполняется (BLOCKED_SPEC) — только
  гибридизация.

## 6. Independent review — WAIT_EXTERNAL

Самопроверки в этой сессии — **не** независимая приёмка (IMPLEMENTER не self-accept).
Запрошено: **fresh Reviewer**, затем **exact-head Verifier** по draft PR
(`work/prep-s17-r3-r1` → `work/prep-s17-r2-r1`). После merge R2 — перенос только
собственных изменений R3 на свежий `main` с полной повторной валидацией.
One next action: independent fresh Reviewer на draft PR.
