# E6 — Атомистическая специализация и связь с P0–P3

Научный статус E6: **NOT_RUN / NOT_ACCEPTED**; material validation P0: **OPEN**. Приоритет engineering route: **ACTIVE**, P0–P3 по owner-directed [ATOMISTIC-PRODUCT-R1](../work/WO-ATOMISTIC-PRODUCT-R1.md), см. [текущую roadmap](../ROADMAP.md) и [machine product plan](../../project/product-plan.json).

Прежний общий dispatch «DEFERRED, после NL5» заменён для нового atomistic engineering продукта: adapter/app/эталонная подготовка идут независимо от DNA NL5. Историческая запись E6/NL6 в старом scientific plan сохраняется без переноса acceptance; actual engineering pilots не отмечают E6 RUN и не закрывают P0. Future scientific/material validation требует отдельного frozen protocol/model validation и принятой среды.

Первый engineering preset — ASE_EMT_Cu, fcc Cu 2×2×2 (32 atoms), actual relaxation/короткая MD с trajectory/metrics/manifest. Ceiling: SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED, не validated EAM. Только mission WO разрешает disposable Linux validation: ≤4096 atoms, ≤2000 MD steps/run, ≤8 actual pilot runs/20 минут/2 GiB суммарно, sequential, isolated venv; stop при missing pin/rights, non-finite/integrity/budget failure. Карточки C0 и этот исследовательский паспорт сами по себе запуск не разрешают. Кандидаты дальнейших моделей: [ASE S14 и OpenKIM S12](../research/SOURCES.md).

## Вопрос

Можно ли провести независимый атомистический опыт через то же ядро целей, протоколов, исполнения и evidence, не создавая второй NanoLab?

## Выбор задачи

Один материал и один тип объекта: небольшая наночастица либо поверхность. Выбрать наблюдение с доступным эталоном и подходящую модель. Этот первый опыт проверяет расширяемость и физическую применимость, не обязан открыть новый материал.

## Программа

ModelCard с областью применимости → контрольные свойства/проверки реализации → импорт структуры → расчёт → анализ → воспроизведение → общий отчёт. Если выбранная модель обучалась только на bulk-структурах, её пригодность для поверхности должна проверяться отдельно.

## Научная приёмка E6 и material validation

Адаптер соблюдает общие контракты и сохраняет специфические для физики поля. Есть контрольный результат и ограничения; ошибки правильно классифицируются. Не сравнивать абсолютные энергии разных моделей без согласования определений.

Квантовый cross-check добавляется, только если он отвечает конкретному вопросу. DFT не является безусловной истиной. Связь атомистического модуля с ДНК не выполняется автоматически: совместная мультифизика требует отдельного контракта и проверки.

Следующее развитие этого направления может вести к 2D-интерфейсам, наноэлектронике и виртуальным измерениям. Ни одно из них не входит в E6 по умолчанию.
