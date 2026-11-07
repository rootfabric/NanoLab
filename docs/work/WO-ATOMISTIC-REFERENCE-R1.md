# WO-ATOMISTIC-REFERENCE-R1

Owner request: «Реализуй следующий пункт», после выполненного merge PR #96.
Canonical base: `ddf8a25cdd95a1598338816f6a585ffdde1e0f2a`.
Task: AP-P0-REFERENCE / ATOMISTIC-REFERENCE-PREP. Risk HIGH (reference/protocol/units/rights), execution C0_SOFTWARE_ONLY. Checkpoint NL6 используется лишь совместимым legacy work-passport; product stage P0 независим от NL6 acceptance.

## Цель и полезный результат

Подготовить проверяемый эталон для одного материала Cu и существующей ASE 3.26.0 EMT(asap_cutoff=False): доступные primary sources, численные reference values с условиями/единицами/ограничениями, pinned model/source/rights, draft protocol с tolerances и convergence plan до будущего расчёта. Машинная проверка пакета и негативные tests защищают от использования неполных/несогласованных входов. Consumer — material reviewer и следующий исполнитель benchmark. P0 остаётся OPEN до actual validation и независимой приёмки.

## Scope

Разрешены docs/atomistic/reference/cu-r1/**, docs/atomistic/MODEL_CARD.md, docs/atomistic/README.md, docs/ROADMAP.md, scripts/atomistic/reference.py, tests/test_atomistic_reference.py, project/product-plan.json, project/product-state.json, project/operations/ATOMISTIC-*.json, project/operations/FLOW-R1.json, данный Work Order и docs/work/executions/EX-ATOMISTIC-REFERENCE-R1/**. Отразить уже состоявшийся merge #96 в устаревших operational status; не подменять им material acceptance.

Запрещены изменения historic project/state.json/plan.json, NL counters, frozen NL5, runtime calculator/web/worker, запуск новых calculator/MD/science, paid compute, U1/U2 mutations, authority expansion, direct main push/force. Ранее разрешённый engineering pilot не переиспользуется как разрешение material validation.

## План и бюджет

1. Не более двух содержательных source passes без нового факта, один материал/модель. Пиновать реальные байты там, где права допускают; для внешних copyrighted источников — locator/digest/проверенная фактическая выписка, без полного текста.
2. Сформировать ограниченный reference scenario, observables/units/conditions, source uncertainty отдельно от engineering tolerance, convergence и fail/inconclusive rules. Не выдавать bulk consistency за nanosurface/finite-temperature validation.
3. Реализовать offline validation reference package, без расчётов энергии/сил; synthetic fixtures лишь для software tests.
4. Sol implementer, отдельные Sol Reviewer и Verifier; затем hosted CI и reviewable PR. WIP ≤3. Максимум два ремонта одной причины, затем пересмотр scope.

Physics runs = 0; локальные структурные/арифметические tests разрешены. Missing source/rights/applicability → явный BLOCKED_SOURCE и одна resume condition; не выдумывать эталон. Source choice и tolerances должны предшествовать любому будущему результату. Подготовка не означает freeze/launch approval.

## Завершение

Точные subject/pins/evidence, все найденные ограничения, независимые verdicts и один следующий шаг. Для actual material validation отдельно требуются frozen protocol/code/environment и существующие approved executor/launch gates; этот WO их не отменяет. Merge main — отдельное scoped решение владельца.
