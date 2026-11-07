# WO-ATOMISTIC-PRODUCT-R1

Дата: 2026-11-05. Owner request: обновить план согласно обсуждённой P0–P6 дорожной карте, реализовать ближайшую работу и вести Sol-субагентов.

Canonical base: `3b567ae33f247b182b2ae451d2cc4598a9e76019`. Integration dependency: FLOW-R1 `ddbc5cb68a5b720cbbaaadeba96f087d82d82732`, ещё не принят в main; используется как явно названная stacked dependency. Risk HIGH (roadmap, new physical adapter, execution scope). Historical NL acceptance and frozen NL5 inputs remain immutable.

## Результат

1. Согласованные roadmap, machine product plan и ограниченные задачи P0–P6. P0–P3 — ближайший продукт; P4–P6 — условные исследования.
2. Независимый review FLOW-R1, затем отдельная verification.
3. Первый малый атомистический путь: создание структуры одного материала → реальный расчёт → траектория/метрики → просмотр и сохранение. При отсутствии проверенного material benchmark явно отделить инженерную демонстрацию от принятого P0.
4. Проверяемая передача: команды, тесты, исходники, ограничения и один следующий шаг.

## Разрешённый scope и бюджет

Разрешены project plan/operations и product status (без изменения исторической научной приёмки), current roadmap/README/architecture/control routing, новый `scripts/atomistic/`, `examples/atomistic/`, `tests/test_atomistic*`, `docs/atomistic/`, scoped execution evidence. В составе проверки FLOW-R1 разрешён bounded repair подтверждённого finding FLOW-REV-01: `scripts/harness/review_impact.py` и `tests/test_flow_throughput.py`, без общего изменения review policy. Использовать существующий harness, не строить новый scheduler/task bus. Отдельные Sol sessions для implementation, review, verification; общий host не является независимым физическим исполнителем.

Текущий запрос владельца реализовать ближайший атомистический сценарий применяется к ограниченной инженерной проверке нового адаптера в disposable Linux container: один материал/одна явно названная модель, не более 4096 атомов, не более 2000 MD steps/run, не более 8 pilot runs, суммарно до 20 минут compute, до 2 GiB результатов; последовательное исполнение. Зависимости — только isolated venv; без платного compute, без вмешательства в U1/U2, системные службы и scientific runner. Фактические atomistic runs должны называться расчётами, а не маскироваться как mock. Claim ceiling — SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED; никакой NL5/NL6 или material acceptance. Confirmatory/material validation требует своего протокола и принятой среды.

Это узкое дополнение новой продуктовой линии к прежней U1/R2 policy для данной mission, не разрешение NL5/E5 dispatch и не признание текущего контейнера U1/U2. Будущие launch profiles задаются явно, наличие READY card само по себе ничего не запускает.

## Проверки и остановки

Сначала deterministic validation/negative tests: неверные единицы/NaN/unsupported material/oversize/unsafe paths; затем ограниченные реальные runs по сохранённому protocol/config. Stop при превышении budget, missing model rights/pin, non-finite forces/energies или failed integrity. Нельзя менять reference tolerance после оценки результата. Если material validation недоступна, P0 остаётся OPEN, а инженерный сценарий поставляется с этим ограничением.

Код/данные/inputs и влияние на authority проходят независимые Reviewer + Verifier на неизменном subject. Review-only actor не меняет product. До merge — candidate, не canonical acceptance. Никакой автоматической активации Task Bus P2.
