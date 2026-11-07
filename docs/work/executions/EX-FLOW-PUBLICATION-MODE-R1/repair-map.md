# FLOW-R1: repair mode/type publication exclusions

Work Order: `WO-ATOMISTIC-PRODUCT-R1`. Exact base: `0d8537cc368dc03ee39a543c835f72c40b651ae6`; stacked mission base задан Director, canonical main этим не изменяется. Risk HIGH, claim `C0_SOFTWARE_ONLY`.

## Failure и причина

Независимый Reviewer обнаружил: report `summary.md` с mode `100755` в base и `100644` в head получает `PUBLICATION_ONLY_CANDIDATE` и `subject_equivalent=true`. `compare()` исключает путь из обоих subject digests, но проверяет mode/type только в head; executable base теряется из проверки.

## Scope и план

Owner/module: текущий Implementer, `scripts/harness/review_impact.py`, функция `compare()`. Входы: API `compare()` и CLI `harness.review_impact`. Sibling paths: явно исключённые summary/review/events, общая проверка mode/type. Разрешённые изменения: этот модуль, `tests/test_flow_throughput.py`, собственный execution directory. Reviewer report не изменяется.

1. Regression в существующем `ReviewImpactTests`: mode `100755 → 100644`, обратный переход и symlink ↔ regular; отрицательные результаты сохраняются.
2. Узкая проверка обоих существующих entries: каждый должен быть `100644 blob`; отсутствие base разрешено только для действительно нового обычного report. Удаление/неясное влияние остаётся full review.
3. Запуск focused regression, существующего FLOW suite, затем независимый recheck тем же Reviewer.

Scientific impact: отсутствует; scientific runs, acceptance, trust policy, main/remote и чужие evidence не изменяются. Только локальные commits; публикацию выполняет Director. Бюджет: обычные unit checks, без science/paid compute. Stop: выход за scope или дополнительный policy defect — handoff Director.

Следующее действие после реализации: независимый Reviewer проверяет точный commit и возвращает verdict; Implementer не принимает собственный repair.
