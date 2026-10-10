# WO-LITERATURE-TO-MECHANISM-ROUTE-R1 — Literature-to-mechanism roadmap R1

Статус: **DOCUMENTATION IMPLEMENTATION / REVIEW REQUIRED**. Основание: поручение владельца скорректировать roadmap после анализа публикаций о наномеханике. Это проектная корректировка (не запуск NL6 или пересмотр NL5).

## Scope

- Миссия: дополнить depth-first DNA nanomechanics путь переходом от воспроизведения отдельного компонента к сборке и проверке новых механизмов.
- Base: `main @ 8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad`, tree `0eba7b901ab9991cca6b9439df227d71a90a82df`.
- Risk: **MEDIUM (control planning changes)**; claim class: **C0_SOFTWARE_ONLY**; бюджет: документация + проверки JSON, **0 scientific runs**.
- Allowed: `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md`, `docs/research/SOURCES.md`, `docs/work/WORK_QUEUE.md`, `project/plan.json`, `config/control/harness/checkpoint-catalog.v1.json`, `docs/control/LITERATURE_TO_MECHANISM_ROUTE_R1.md`, данный Work Order и `docs/work/executions/EX-LITERATURE-TO-MECHANISM-ROUTE-R1/**`.
- Forbidden: `project/state.json`, immutable/frozen NL5 packages and evidence, scientific protocols, simulation/analysis code, status promotion, new science, paid compute, direct main push/merge.

## Required outputs

1. Источники: разделить bibliographic reference, executable pack и verified reproduction; приоритет S17 / springs, затем проверка compositional coupling, programmable arrays, candidate design generators.
2. Конструктор: ports/anchors, topology/mapping, assembly compiler, load/actuation, reduced model and evidence boundaries.
3. Roadmap + machine-readable plan/checkpoint reconciliation: `NL7-001` следует непосредственно за `NL6-001` (после NL5 acceptance), `NL6-002` остаётся отдельным post-E5 benchmark, не доказывающим ценность ИИ автоматически.
4. Проверяемые acceptance gates, типы риска/прав/моделей, параллельные preparation tasks; staged implementation.
5. No change of existing NL5 scientific or host activation gates.

## Validation and review

- JSON parse, normalized plan/catalog dependencies, old accepted stages preserved.
- Coverage audit: links, capability mappings, explicit non-claims and human gates.
- Fresh review + verification of exact PR head per control policy; merge only by Human Gate.
