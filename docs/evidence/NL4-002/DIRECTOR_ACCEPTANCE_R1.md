# Director Acceptance R1 — NL4-002 (E3: измерение вклада ИИ) — ACCEPTED

- Дата: 2026-09-12. Authority: владелец (решения: target = 90°, бюджет = 5 прогонов × 50k на агента; цепочка миссий «продолжай»).
- Executions: `EX-NL4-002-E3-MECH-R1` (random+grid arms + RealExecutorAdapter, `f24460a`), `EX-NL4-002-E3-LLM-R1` (LLM arm, `9eb20c7`), `EX-NL4-002-E3-REVAL-R1` (winner re-validation, `db4608e`).
- Independent REVIEWER: batch **PASS** (`3fbc323`, 10 проверок; сравнение признано **VALID** — изоляционный инцидент LLM не повлиял: решения зафиксированы до утечки и побайтово соответствуют preregistered стратегии, выводимой из опубликованных E2-чисел). Independence caveat в вердиктах.
- Coordination checks: reval 292 теста OK (вкл. F-1 фикс), validate ok, consistency ok.

## Замороженный результат E3 (measured-only)

1. **Все три стратегии сошлись на 32b** как кандидате, ближайшем к target 90°: random (score 11.68), grid (16.23), LLM (claimed 9.83).
2. **Anti-selection-bias гейт сработал**: winner re-validation (свежие seeds 204016/205020) дала pooled median 75.109° → revalidated score **14.891**; claimed 9.832 **АННУЛИРОВАН** (WO §winner-критерий). Регрессия к среднему подтверждена (свежие seeds ниже всех прежних наблюдений 32b@50k).
3. **Честный вывод E3 (вне trend-интерпретаций)**: при данном бюджете (5×50k) и дискретном пространстве (4 измеримых варианта) **статистически значимого преимущества LLM-агента перед random не выявлено**: revalidated 14.89 (LLM best-of) против random best-of 11.68 — оба best-of-числа оптимистичны; семейственный типичный скор 32b по 6 наблюдениям seeds ≈ 12.4–13.4. Знание published-данных позволило LLM сразу номинировать верный вариант (структурное преимущество приоритизации), но best-of-seed «выигрыш» не подтвердился.
4. Инфраструктура: RealExecutorAdapter работает end-to-end (11 ранов реального движка за кампанию, 0 крэшей, 0 invalid кадров), стоимостная модель 0.049–0.066 s/step подтверждена.

## Findings → действия

- F-1 (MINOR) исправлен в reval (292 теста); F-4 PROCESS (arm-сводки в SESSION_LOG до закрытия всех arm'ов) — правило на будущие сравнительные кампании (изоляционный инцидент E3 стал возможен только из-за этого — в E3 решении признан VALID, но повторение недопустимо).
- 291-vs-287 расхождение подсчёта — объяснено (мёртвые тесты), закрыто F-1 фикс.

## Решение

**NL4-002 = ACCEPTED** (E3 исполнен по пререгистрации, winner re-validation проведена, все неудачи/аннуляции сохранены; outcome = honest negative-on-AI-advantage + validated pipeline). state: task_status NL4-002 = ACCEPTED; next = **NL4-003** (пользовательский MVP) = READY.
