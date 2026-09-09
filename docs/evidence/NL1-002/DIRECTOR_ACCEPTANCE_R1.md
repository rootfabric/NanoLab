# Director Acceptance — NL1-002 (первый вертикальный E1 путь) и закрытие checkpoint NL1

Дата решения: 2026-09-09. Роль: DIRECTOR (главный агент миссии; явная авторизация владельца на merge запрашивается отдельно для этого PR).

## Решение

```text
NL1-002 = ACCEPTED
NL1 (checkpoint) = ACCEPTED   # catalog: "one frozen non-AI reference path executes end-to-end with measured resources" — выполнено
frontier = NL2; next_work_order = NL2-001 (READY)
experiment E1 = RUN (execution facts получены; scientific acceptance E1 = NL2-002, campaign ceiling C1)
```

## Основание

1. **Вертикальный путь end-to-end с измеренными ресурсами**: preparation (fixture 4/4 SHA-256 из сырых blob'ов pinned commit; пересборка engine по ENGINE_ENVIRONMENT_R1 §3, бинарь ffc80b1a…579f) → T1 production E1-R1-S001 (verbatim quick_input, seed −200619630, exit 0, 13.13 s / 6304 KB) → механический анализ §5.1 (avg col2 −1.39393635864, |Δ| 0.014234, факт IN_BAND) → архив (все артефакты в Git с artifacts.manifest.json).
2. **Frozen subject до запуска**: campaign/protocol/manifests/started-events запушены до первого прогона (5c8774f; S001-event добавлен до запуска — 9cc83e8, прозрачная коррекция).
3. **Пререгистрация соблюдена**: входы без модификаций; полоса/оракул не менялись; pilot (P001–P003, все COMPLETED IN_BAND) в evidence не засчитан; freeze R_confirm = 3 опубликован (E1-PROTO-R2, superseding только §6.4) ДО confirmatory кампании.
4. **Независимые вердикты**: REVIEWER PASS (SHA 7b12012bce4686b21ea8507a9fef39020c17e1f3 (ветка review/nl1-002-reference-run-r1, subject ec67752)) и VERIFIER PASS (SHA b405a7e0da5b04ad9d6b1ffe848ed3fd779764b6 (ветка verify/nl1-002-reference-run-r1, subject ec7e3ed — delta ec67752..ec7e3ed проверена верификатором)) на exact subject ec7e3edc83a3434d96222a0a8a94b03f7fa10e23.
5. **Дисциплина claims**: campaign-level scientific_outcome = NOT_EVALUATED; SUPPORTED не заявлялся; state experiment E1 = RUN (не ACCEPTED — приёмка E1 принадлежит NL2-002 по плану).

## Условия, с которыми принято

- Все 4 прогона выполнены на одной машине/сборке; независимость повторов для статистики — обязанность NL2-002 (R_confirm = 3, distinct seeds).
- SD пилота на n = 3 — грубая оценка; точные CI — NL2-002.
- E2 не затронут (REFERENCE_ONLY, owner decision в силе); ИИ-компоненты не использовались.

## Следующее действие

`NL2-001` (READY): реализовать схемы, manifest и E0. Затем NL2-002: T2 confirm (3 реплики по E1-PROTO-R2) + статистика + acceptance E1.
