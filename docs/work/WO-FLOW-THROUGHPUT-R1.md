# WO-FLOW-THROUGHPUT-R1 — ускорение разработки без ослабления научных критериев

START: 2026-10-28T03:11:46.106Z. Owner request: внедрить предложенные по аудиту изменения harness и roadmap; продолжить прерванную операцию.

Base: `main@3b567ae33f247b182b2ae451d2cc4598a9e76019`, tree `560dc913a71a237d3c452a5a2e492e213b232911`.
Branch: `control/flow-throughput-r1`. Risk: HIGH (control/CI policy), claim: C0_SOFTWARE_ONLY. Implementer не является независимым Reviewer/Verifier.

## Scope
Readiness-aware drive и operational task records; генерация валидных work events; пакетная CI-валидация без удаления тестов; impact-based review policy и перенос evidence при доказанной неизменности subject; актуальная навигация/roadmap с параллельными NL6/NL7 PREP; исправления ресурсной арифметики отдельным addendum без редактирования исторических evidence.

## Границы
Научные протоколы, inputs, seeds, N, критерии приёмки, frozen F2 и исторические experiment events неизменны. U1 не назначается фиктивно, U2 не объявляется исправленным, R2 не активируется. Scientific runs=0. Paid compute=0. Main не меняется без Human Gate и независимого review. Никакой автоматической активации Task Bus P2, self-hosted PR execution или глобальной настройки узлов.

## Validation / outputs
Focused regression/negative tests, полный существующий unittest suite, consistency, все execution passports/events, workflow security lint; exact HEAD/TREE, evidence и один PR. Для runtime recovery разрешён временный H0 read-only export публичной Git-истории exact base в debug artifact (1 день); exporter удаляется из final diff. Budget: до 6 H0 CI jobs по <=15 минут, локальные C0 tests; при исчерпании остановить повторные запуски и опубликовать результат.

## Next
Получить exact checkout, реализовать пакет, прогнать проверки и передать независимому Reviewer. Научный frontier NL5 и external_reproductions=0 не повышаются этой работой.
