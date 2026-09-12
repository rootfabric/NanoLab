# Director Acceptance R1 — NL3-002 (Execute E2 component campaign) — ACCEPTED

- Дата: 2026-09-12. Authority: владелец (миссия «реализуй саб агентами и проверь их результат» → «делай следующий шаги» → «продолжай», включая интерактивные решения: confirmatory «2e5 шагов × 3», параметрика «11b+32b+53b+74b × 3»).
- Claim ceiling серии: `C0_SOFTWARE_ONLY` / measured-only; trend-интерпретации — вне ceiling (прерогатива отдельного решения).

## Execution'ы и вердикты (все fresh-сессии; caveat «actor identity ≠ executor identity» в каждом вердикте)

| Execution | Верификация | Итог |
|---|---|---|
| EX-NL3-002-PROTO-R1 (`9b3e1c5`) | REVIEWER PASS `5669307` (11/11; манифест воспроизведён байт-в-байт) | манифест рук 0b + observables v2 + draft proposals |
| EX-NL3-002-R1 confirmatory (`c9ff9a1`) | REVIEWER PASS `18f7ef4` (10/10; пересчёт из raw: Δ ≤ 4.5e-10°) | `E2-R1` outcome = MEASURED |
| EX-NL3-002-PARAM-11B-R1 (`924cbef`) | BATCH REVIEWER PASS | MEASURED (12600 s, §5 budget interrupt, 46/50 кадров) |
| EX-NL3-002-PARAM-32B-R1 (`2aefafa`) | BATCH REVIEWER PASS | MEASURED (полные 150k) |
| EX-NL3-002-PARAM-53B-R1 (`0610f8a`) | BATCH REVIEWER PASS | MEASURED (полные 150k) |
| EX-NL3-002-PARAM-74B-R1 (`0274af4`) | BATCH REVIEWER PASS (honest BLOCKED) | NOT_MEASURED — детерминированный отказ arm-manifest-v1 (2/2), runs NOT_RUN, бюджет не израсходован |
| EX-NL3-002-SUMMARY-R1 (`24a21aa`) | BATCH REVIEWER PASS (пересчёт common-window до 1e-6) | таблица серии + карточка 0b |

Coordination checks Director'а: каждая verdict-ветка получена с origin и содержит ровно вердикт(ы); key numbers сверялись координатором независимо (WSL-дайджесты, тесты 242 OK, валидаторы) на каждом шаге.

## Замороженный результат E2 (measured-only)

- **0b (confirmatory, 200000 steps × 3 seeds, 150/150 валидных кадров)**: pooled median **65.98°**, IQR [64.94, 67.06], q5–q95 [63.00, 68.41], bootstrap CI95 **[65.67, 66.32]**; integrity: pf_v2 ≥ 0.981, lbf ≤ 0.0560 (baseline автора ~0.054), disp ≤ 8.40; energy drift ≤ 0.0099.
- **Параметрическое общее окно (t ≤ 150000, addendum §8)**: 0b **65.87°** [65.61, 66.12] · 11b **73.93°** [73.71, 74.12] · 32b **78.09°** [77.79, 78.67] · 53b **132.36°** [131.78, 132.99] · 74b NOT_MEASURED. Во всех измеренных вариантах 100% валидных кадров.
- Манифесты рук (до данных, байт-детерминизм): 0b 4006/3942 · 11b 4218/3722 · 32b 4814/3190 · 53b 4318/3638 · 74b — отказ деривации.
- Cost: 0.049–0.066 s/step; 150k ≈ 2.0–2.9 ч/реплику; 200k ≈ 3.1 ч кампаний ×3 параллельно.

## Honest gaps / ограничения (сохранены, не скрыты)

1. **74b NOT_MEASURED**: arm-manifest-v1 детерминированно не выделяет два доминирующих блока на frame 0 ни при одном пороге — путь решения (arm-manifest-v2 / другой референсный кадр) — только новая пререгистрированная ревизия.
2. Конвенция угла [0,180] first-principles (erratum R1 §2.5); соответствие SI статьи неизвестно (SI retrieval заблокирован publisher anti-bot; путь — `E2_OBS1_SI_DECISION_R1`).
3. Coarse-grained модель (oxDNA2), один движок/хост; интерпретация «что значит 66°/132° физически» — вне measured-claim'ов.
4. Процедурные: 11b wrapper-инциденты (раскрыты), F-2 параметризация REPO-пути — в следующий инструментальный WO.

## Решение

**NL3-002 = ACCEPTED** (полная серия в объёме «4 из 5 вариантов измерены + 1 честный NOT_MEASURED», распределения, статистика, все неудачи сохранены, карточка компонента 0b опубликована). `E2-R1` outcome = MEASURED (execution-facts: E2 = RUN; поддержка/интерпретация — вне ceiling). Веха NL3-002 закрывает измерительную часть стадии NL3; закрытие стадии NL3 (frontier → NL4) — отдельное решение владельца с учётом honest gap 74b.
