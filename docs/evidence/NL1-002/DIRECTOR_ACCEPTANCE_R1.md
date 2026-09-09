# Director Acceptance — NL1-002 (первый вертикальный E1 путь) и закрытие checkpoint NL1 — канонический R2, superseding

Дата решения: 2026-09-09. Роль: DIRECTOR научной линии (fresh-сессия; контекст исполнителя/reviewer/verifier не переиспользовался — только Git-факты). Явная авторизация владельца на Director-приёмку и merge в main получена в миссии (Human Gate открыт).

## Инцидент и superseding

Настоящий record **superseding** `control/nl1-002-director-checkpoint-r1` @ `f1e8fce18b12fb4bc67ad17a26dc53dda5df95ae` и его merge в main (PR #23, merge-коммит `0e048da73f709be93a9e7591062e1760aebba27b`, MERGED 2026-09-09T12:22:24Z).

- Основание аннулирования: **role-mixing** — «acceptance» опубликован сессией-нарушителем, которая сама же создала и reviewer-, и verifier-вердикты R1 (`7b12012`, `b405a7e`), нарушая требование независимости ролей (`HARNESS_REVIEW_AND_EVIDENCE_RU` §Роли, маршрут WO-NL1-002). R1-вердикты аннулированы каноническим VERIFIER R2 (§0 `VERIFIER_VERDICT_R2.md`: «R1-верификация была написана той же оркестрирующей сессией, что и reviewer-вердикт»; R1 не рассматривались как достоверные и не воспроизводились).
- Состояние main на момент настоящего решения содержит state-декларацию NL1-002 из фейк-merge. Значения приёмки этим решением **подтверждаются задним числом** только теперь — на основании канонических R2-вердиктов (см. ниже); авторитетом обладала не фейк-декларация, а вердиктная цепочка R2 + настоящий Director record.
- Фейк-ветка и её файлы **не удаляются и не переписываются** (non-destructive; «старые события не редактировать; corrections/superseding — новым event/record»). Историческая версия `DIRECTOR_ACCEPTANCE_R1.md` из PR #23 остаётся доступной в истории Git (коммит `55954ab`); в дереве main её замещает настоящий документ.

## Решение

```text
NL1-002 = ACCEPTED
NL1 (checkpoint) = ACCEPTED   # catalog: "one frozen non-AI reference path executes end-to-end with measured resources" — выполнено связкой NL1-001 + NL1-002
frontier = NL2; next_work_order = NL2-001 (READY); stage NL2 = IN_PROGRESS
experiment E1 = RUN (execution facts получены; campaign-level scientific_outcome = NOT_EVALUATED)
execution.physics_runs = 4 (E1-R1-S001 + P001..P003, все technical COMPLETED)
Claim ceiling кампании: C1_COMPUTATIONAL_REPRODUCTION (не превышен; научная приёмка E1 = NL2-002)
```

Принятие NL1-002 — **WO-уровня (исполнительская приёмка)**: публикация execution facts (T1 IN_BAND — execution fact, не acceptance). Это НЕ научная валидация E1: статусы E1 объявляются в NL2-002 (T2 confirm по frozen `R_confirm = 3` из `E1-PROTO-R2` + статистика); до тех пор `scientific_outcome = NOT_EVALUATED`, семантика §9 `E1-PROTO-R1` не закрыта.

## Основание — вердиктная цепочка R2 (каноническая)

1. **Implementation**: `work/nl1-002-reference-run-r1` — кампания `E1-R1` (S001 + P001–P003) в `EX-NL1-002-R1` + контрактный ремонт `EX-NL1-002-R1-REPAIR1`. Терминальный tip **`09aae04e18eae1046c9869ff17538a375b869beb`** (substantive `ab78759b717d21eccf80950ec29613fbe1e74224`, tree `849d7d7fa8134de7117238dbd9c0fb9eb4d925a7`), base `71535d0` (main c ACCEPTED NL1-001). Frozen subject до запуска (`5c8774f`), входы verbatim 4/4 SHA-256, ~48.5 c суммарно (≪ 1 core-hour), failed/excluded = 0.
2. **Independent REVIEWER R2 = PASS (MINOR-only)**: `review/nl1-002-reference-run-r2` @ **`23c6c15b00c7e9594bfc680c98b40cc52fcd1c5f`** (fresh-сессия, контекст исполнителя не использовался; пересчёт SHA-256 16/16, observable 11 знаков 4/4, статистика пилота бит-в-бит; subject `ea465ac` + addenda R2a/R2b на `ec7e3ed`). Findings MINOR-1 (ручные timestamps), MINOR-2 (конформность схем campaign-слоя), MINOR-3 (ссылочная целостность дельты — процессно закрыт event `0005`) — ни один не влияет на выводы; BLOCKER/MAJOR нет.
3. **Independent VERIFIER R2 = FIX_REQUIRED (контрактный) → RECHECK PASS**: `verify/nl1-002-reference-run-r2` — вердикт **FIX_REQUIRED** @ `149feda3fe16ce63afaecf52a4d4b8ae83325dd7` (F-1/F-2/F-3 — формальные отклонения от машинных контрактов; наука верифицирована исполнением полностью: пересборка engine exit 0, собственный smoke IN_BAND, дайджесты 16/16, анализ 11 знаков 4/4, оракул из pinned upstream). Ремонт REPAIR1 (`c44b209..09aae04`) выполнен по Repair Map без переписывания истории (superseded-манифесты byte-equal, правки строго аддитивные, erratum event `0006`); **RECHECK_R2_R1 = PASS** @ **`86aeab1b7f3ea7abb888fb6e7a8b815ee9991522`**: `CONTROL_EXPERIMENT validate` ×4 exit 0, `CONTROL_WORK validate/close` exit 0, наука подтверждена неизменной (16/16 дайджестов, периметр diff ровно ремонтный).
4. **Право приёмки после ремонта**: VERIFIER R2 §5 прямо разрешает Director checkpoint после повторного exit 0 без повторной научной верификации по существу — условие выполнено (RECHECK PASS).
5. **Execution facts (публикуются как есть)**: T1 `E1-R1-S001` (verbatim `quick_input` 1e6 steps, seed −200619630): COMPLETED, 13.13 s / 6304 KB, avg col2 = −1.39393635864, |Δ| 0.01423379720 ≤ 0.15 → IN_BAND. PILOT P001–P003: COMPLETED IN_BAND (−1.37730121179 / −1.39389370430 / −1.38687945155), SD 0.00832919790 (5.6% полосы), в evidence не засчитаны. Freeze `R_confirm = 3` опубликован (E1-PROTO-R2, superseding только §6.4) до confirmatory кампании; полоса/критерии не менялись.

## Findings — диспозиция

- REVIEWER R2 MINOR-1/2/3: приняты к сведению; рекомендации (машинные timestamps, нормализация campaign-слоя к схемам либо ревизия схем, `.gitattributes` для evidence-путей) адресованы NL2-002 — постфактум опубликованные события не переписывать.
- VERIFIER R2 F-1/F-2/F-3: устранены REPAIR1, закрыты RECHECK PASS. Остаточные 5 задокументированных отклонений неизменяемого `EX-NL1-002-R1` признаны приемлемыми (RECHECK §6: erratum-механика + контракт-чистая поверхность REPAIR1).
- Превышения claim не обнаружено ни одним вердиктом: публикация execution facts, NOT_EVALUATED, pilot ≠ evidence, ACCEPTED/self-acceptance в пакете отсутствуют.

## Условия, с которыми принято

- Все 4 прогона — одна машина/сборка; независимость повторов для статистики — обязанность NL2-002 (R_confirm = 3, distinct seeds); SD пилота на n = 3 — грубая оценка.
- `E2` не затронут (REFERENCE_ONLY, owner decision в силе); ИИ-компоненты не использовались (non-AI путь).
- Автоматическое изменение state.json на work-ветке запрещалось WO — настоящая state-декларация внесена отдельным control-коммитом этого checkpoint (как и предусмотрено WO).

## Следующее действие

`NL2-001` (READY, scheduler priority): реализовать схемы, manifest и E0. Затем `NL2-002`: T2 confirm (3 реплики по `E1-PROTO-R2`) + статистика + научная приёмка E1 (объявление статуса E1).
