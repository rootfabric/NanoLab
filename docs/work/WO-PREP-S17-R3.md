# WO-PREP-S17-R3 — DNA Driver–Follower Molecular Interface & Static Assembly (0 scientific runs)

Статус: **HANDOFF_COMPLETED** (2026-10-18; реализация `49be26701596032bb0924f56a33dab536a5f9ffe`; verdict реальной пары `NOT_RECONSTRUCTED` при `SOURCE_CONFIRMED` интерфейсе на уровне последовательностей; 804 tests OK; independent review — **WAIT_EXTERNAL**: fresh Reviewer + exact-head Verifier по draft PR; merge = Human Gate). START 2026-10-18. Родитель: `WO-PREP-S17-R2` (PR #59, **OPEN — ещё не слит**; execution R2 завершено `HANDOFF_COMPLETED`, independent Reviewer PASS_WITH_NOTES и Verifier VERIFIED опубликованы в PR #59, merge = Human Gate). Маршрут: [LITERATURE_TO_MECHANISM_ROUTE_R1](../control/LITERATURE_TO_MECHANISM_ROUTE_R1.md) — этот WO впервые реализует первые исполняемые контракты `MechanicalComponentSpec v1` и `AssemblySpec v1` (требования в [DATA_CONTRACTS.md](../DATA_CONTRACTS.md)).

## Base rule (согласно mission)

- PR #59 (R2-ветка `work/prep-s17-r2-r1`) **не слит** на момент fresh fetch 2026-10-18T01:01Z (`origin/main = 513c4fa86470d939e9f9b7829e9c67c489c15a57`, без изменений).
- Разрешена временная **stacked-ветка R3 от exact HEAD PR #59** `26c4cd51151167634815c531b9c49dcc54ba6243` (tree `110193d5360c4e2714eed102b0addf94ca13575d`), draft PR против `work/prep-s17-r2-r1`.
- **Зафиксировано: R2 ещё не каноничен.** После merge R2 собственные изменения R3 переносятся на свежий `main`, полная проверка повторяется, и только тогда R3 PR открывается/перенаправляется в `main`.
- Merge PR #59 НЕ выполняется (Human Gate). История R2 не изменяется, force-push запрещён.

## Scope

- Цель: для пары driver (S17 leaf-spring DNA nanoengine) — passive follower:
  (A) targeted source-аудит молекулярного интерфейса driver–follower по доступным источникам (статья CC BY 4.0, supplementary, Nanobase 196, Zenodo 8248808, `sulcgroup/hinges` REFERENCE_ONLY, source registry R1/R2);
  (B) минимальный machine-readable контракт `MechanicalComponentSpec v1` со строгой валидацией (fail-closed) + component specs для driver и follower;
  (C) `AssemblySpec v1` + минимальный детерминированный fail-closed сборщик **двух** DNA-компонентов (режимы `SOURCE_VERIFIED` / `CANDIDATE_DESIGN`);
  (D) offline-тесты и полная матрица negative controls;
  (E) артефакты/evidence/handoff.
- Verdict для настоящей S17 D–F пары: только `SOURCE_VERIFIED_STATIC_ASSEMBLY` либо `NOT_RECONSTRUCTED`. Если follower-структура отсутствует в источниках — follower spec с явным `UNKNOWN`, assembly остаётся `NOT_RECONSTRUCTED`; программная часть при этом реализуется и тестируется на синтетических компонентах (`CANDIDATE_DESIGN`).
- Risk: **MEDIUM**, claim class: **C0_SOFTWARE_ONLY**, 0 scientific runs, 0 paid compute.
- Claim ceiling: **`PINNED_IMPORT_VERIFIED` / `C0_SOFTWARE_ONLY`**. Статическая сборка `ASSEMBLED_STATIC_ONLY` никогда не является `ASSEMBLY_VALIDATED`, доказательством передачи движения, работоспособности или лабораторной изготовимости.
- Бюджет: ≤ 256 MiB сетевой передачи (bounded fetch; никаких полных 3–21 GB архивов), scratch ≤ 2 GiB.

## Allowed paths

`docs/work/WO-PREP-S17-R3.md`, `docs/work/WORK_QUEUE.md` (только append), `docs/work/executions/EX-PREP-S17-R3/**`, `docs/research/S17_R3_*.md`, `docs/research/S17_R3_*.json`, `scripts/knowledge_pack/mechanical_component_spec.py`, `scripts/knowledge_pack/assembly_spec.py`, `scripts/knowledge_pack/s17_*.py`, `tests/test_s17_r3_*.py`.

## Forbidden (без исключений)

`project/state.json`, `project/plan.json`, NL5 freeze/thresholds и frozen artifacts, `scripts/nl5/**`, `scripts/r2/**`, `scripts/e2/**`, `scripts/nl4/**`, `scripts/hinge_family/**` и `scripts/knowledge_pack/{contract,import_validation,s17_*}.py` (переиспользование импортом разрешено, изменение запрещено — R1/R2 surface freeze), канонические статусы NL5/NL6, oxDNA MD/relaxation/pull-release/E5, любые новые научные прогоны, вендоринг сырых файлов (в т.ч. исходники `sulcgroup/hinges` — REFERENCE_ONLY, без лицензии), прямое изменение истории R2, direct main push, force-push, merge PR #59, self-review/self-acceptance, claim inflation.

## Non-goals (жёстко)

- Не путать внутренние bridge-ODN механизма с соединением driver–follower без прямого доказательства (R2: bridge-ODN интерфейс UNKNOWN; linked.top ≡ nNE.top).
- Не выдавать `CANDIDATE_DESIGN` за опубликованную конструкцию; не подменять отсутствие данных фиктивной молекулярной связью.
- Не запускать NL6-001/E5; не активировать U1/R2; не использовать U2 как научный author executor.
- ДНК-гибридизация ≠ произвольная ковалентная связь: разделять backbone topology edits, комплементарность последовательностей и геометрическую подготовку контакта.
- Не объявлять порт пригодным к физическому соединению только потому, что существует валидный числовой индекс.
- Геометрическая проверка упрощённая: если алгоритм не может исключить стерический конфликт — честный `GEOMETRY_UNVERIFIED`, не ложный PASS.

## Required outputs

1. `docs/research/S17_R3_INTERFACE_AUDIT.md` — targeted interface audit: для каждого вывода source URL/DOI + версия/SHA-256 материала + точное местоположение (figure/table/section/file) + индексы и пространство индексации + статус `SOURCE_CONFIRMED` / `INFERRED_CANDIDATE` / `UNKNOWN`; список вопросов авторам (текст, НЕ отправляется).
2. `docs/research/S17_R3_COMPONENT_DRIVER.json`, `docs/research/S17_R3_COMPONENT_FOLLOWER.json` — валидные `MechanicalComponentSpec v1` (driver — от pinned NE/nNE; follower — честный partial spec с UNKNOWN, если структура не восстановлена).
3. `docs/research/S17_R3_ASSEMBLY_SPEC.json` + `docs/research/S17_R3_ASSEMBLY_RECEIPT.json` — assembly spec + детерминированный manifest с SHA-256; для оригинальной D–F пары — `NOT_RECONSTRUCTED`/`BLOCKED_SOURCE` receipt (machine-readable), для синтетической пары — полный программный прогон `CANDIDATE_DESIGN`.
4. `scripts/knowledge_pack/mechanical_component_spec.py`, `scripts/knowledge_pack/assembly_spec.py` — контракты + сборщик (fail-closed, детерминированные, offline); переиспользуют существующие `KnowledgePack`/`ComponentCard` контрактные поверхности (`contract.py`), без второго реестра provenance.
5. `tests/test_s17_r3_*.py` — позитивные кейсы + полная матрица negative controls (несовпадающие SHA, несовместимые порты, неверные/неоднозначные индексы, переиспользование strand/particle IDs, нарушение backbone connectivity, полярность/ориентация, неизвестная последовательность, несовместимая комплементарность, единицы, отсутствие координат, геометрические конфликты, отсутствие follower, недоказанный connection recipe, несовместимые версии, права, повреждение входов). Все offline.
6. `docs/research/S17_R3_SOURCE_GAPS.md` — точные гэпы источников + вопросы авторам + следующие действия.
7. `docs/work/executions/EX-PREP-S17-R3/**` — паспорт, append-only events, evidence pack + evidence-map, summary; WORK_QUEUE append.

## Validation

```bash
python3 -m unittest discover -s tests -t .
PYTHONPATH=scripts python3 -m harness.cli check-consistency
PYTHONPATH=scripts python3 -m harness.workflow_lint
PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-S17-R3
```

Плюс: регрессии S17-R1/R2 зелёные; повторный прогон сборщика даёт байт-идентичный SHA-256; все negative controls fail детерминированно; `project/state.json` и `project/plan.json` byte-identical; frozen NL5 evidence не изменён; 0 scientific runs; никаких больших raw-файлов.

## Review and handoff

Draft PR против `work/prep-s17-r2-r1` (R2 ещё не каноничен; после merge R2 — rebase собственных изменений R3 на свежий `main`, полная повторная проверка, PR в `main`). Handoff: отдельный fresh Reviewer, затем exact-head Verifier; они не являются частью этой сессии — до их фактического подключения фиксируется `WAIT_EXTERNAL`, self-PASS запрещён.
