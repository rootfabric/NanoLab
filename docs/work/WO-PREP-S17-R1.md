# WO-PREP-S17-R1 — PREP-S17: audited source pack for the published S17 leaf-spring DNA nanoengine

Статус: **IN_PROGRESS / PREPARATORY (NO CONFIRMATORY SCIENCE)**. Основание: миссия владельца 2026-10-14 («подготовить существующую опубликованную DNA-наномеханическую конструкцию для NanoLab») и маршрут [LITERATURE_TO_MECHANISM_ROUTE_R1](../../control/LITERATURE_TO_MECHANISM_ROUTE_R1.md) (PR #54, pending Human Gate merge — на этой ветке маршрут учитывается как **proposed**, не канонический).

## Scope

- Цель: превратить S17 (Centola et al., leaf-spring DNA-origami nanoengine, Nature Nanotechnology `10.1038/s41565-023-01516-x`; Nanobase structure 196; Zenodo `10.5281/zenodo.8248808`; `sulcgroup/hinges`) из библиографической ссылки в **проверенный реестр source inputs + прототип KnowledgePack v1 + минимальный reproducible import path** — реальный вход для будущего NL6-001/E5, но **не** сам E5.
- Base: `main @ 32d3c6840341ad3954d5001235a3cc35b8ca0e01`, tree `474249da8fee669c85aa763274e33a16d4293f40`.
- Risk: **MEDIUM** (новый tooling + внешние данные; без изменения научных границ); claim class: **C0_SOFTWARE_ONLY**; бюджет: metadata/minimal-file downloads (< 200 MB суммарно), локальный Python, **0 scientific runs**.
- Allowed: `docs/work/WO-PREP-S17-R1.md`, `docs/work/executions/EX-PREP-S17-R1/**`, `docs/research/S17_PREP_AUDIT_R1.md`, `docs/research/S17_KNOWLEDGEPACK.json`, `scripts/knowledge_pack/**`, `tests/test_knowledge_pack.py`, `docs/work/WORK_QUEUE.md` (только append новой строки WO при handoff).
- Forbidden: `project/state.json`, frozen NL5 packages/evidence и любые frozen artifacts, scientific protocols (NANOLAB_REPRO_V0_2_*), simulation/analysis runtime (`scripts/e2`, `scripts/nl4`, `scripts/nl5`, `scripts/r2`, `scripts/hinge_family`), запуск E5/campaign, status promotion (NL5/NL6/state), paid compute, direct main push/merge, durable кэш сырых trajectories вне evidence manifest.

## Non-goals (жёстко)

- Не запускать E5 / NL6-001 confirmatory science; не объявлять `MODEL_REPRODUCED`; не пересматривать `NL5-002=WAITING_HUMAN`, frozen v0.2 package, HG-B/HG-A границы.
- Не доказывать физические свойства (жёсткость пружины, частоту пульсаций) — только то, что подтверждается публикацией/исходниками, с полем `UNVERIFIED`/`UNKNOWN` для остального.
- Не создавать фиктивные связи между цепями; неподтверждённые интерфейсы/порты = `UNKNOWN`, не предположения.

## Required outputs

1. **Source registry (rights/provenance report)** `docs/research/S17_PREP_AUDIT_R1.md`: для каждого из 4 источников — canonical URL/DOI, exact version (article version / Zenodo record version + commit SHA / Nanobase structure revision), availability, форматы, размеры, SHA-256 скачанных минимальных файлов, права/лицензии, наличие topology/config/design/sim-conditions/analysis, UNKNOWN-список.
2. **KnowledgePack v1 prototype** `scripts/knowledge_pack/` — минимальный fail-closed validator (schema + checks), согласован с будущим контрактом из `docs/DATA_CONTRACTS.md` (не дублирует существующий provenance/manifest/harness код; не заменяет `component-card.v1`).
3. **Machine-readable pack** `docs/research/S17_KNOWLEDGEPACK.json` — экземпляр контракта для S17 (source_id, version, doi, rights, input manifest + sha256, scientific_model, engine, formats, observables, protocol references, missing_inputs, known_limitations, provenance).
4. **Import validation** (если topology-файл доступен и права позволяют): parse/validate topology, counts/integrity, детерминированный повторный импорт (тот же digest), negative tests на повреждённые входы. Результат = `IMPORT_VALIDATED` level максимум; **не** `MODEL_REPRODUCED`.
5. **Preliminary MechanicalComponentSpec sketch** в audit-документе: driver/follower элементы, anchors/ports — только подтверждённые или явно `UNKNOWN`; observables-кандидаты.
6. **План будущего HIGH scientific WO** NL6-001/E5 (черновая граница, не dispatch).
7. Полный цикл Harness: паспорт, START, CONTINUATION, summary, HANDOFF, evidence с SHA-256.

## Validation and review

- `python3 -m unittest discover -s tests -t .` (все тесты, включая новые `tests/test_knowledge_pack.py`).
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency`; `PYTHONPATH=scripts python3 -m harness.workflow_lint`; `work_cli validate` всех EX-* (включая новый).
- JSON parse всех новых machine-readable файлов; negative controls: повреждённый digest/manifest → validator FAIL.
- Fresh independent Reviewer + exact-head Verifier по control policy; merge = Human Gate.
