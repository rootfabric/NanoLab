# EX-NL4-002-E3-REVAL-R1 — сводка

Статус: **HANDOFF_READY** (IMPLEMENTER; MEDIUM → Director далее по WO-NL4-002).
Claim ceiling: **C0_SOFTWARE_ONLY / anti-selection-bias re-validation measured, no physics-interpretation**.

## Миссия

Winner re-validation кампании E3 (anti-selection-bias шаг WO-NL4-002 §Winner-критерий, авторизация Director: свежие seeds вне allowlist-тройки, verification-шаг). Победитель по `docs/evidence/NL4-002/BATCH_REVIEWER_VERDICT.md`: кандидат **32b / seed 203012** (E3-LLM-R003, observed median 80.168°, claimed score **9.832**). Предупреждение о регрессии к среднему зафиксировано заранее: аннулирование claimed score при выходе re-validation за пределы — ожидаемое поведение anti-bias гейта, не провал кампании.

## Что сделано

1. **2 re-validation рана** (32b, 50000 шагов, параллельно, RealExecutorAdapter напрямую: digest-gated download 32b.top/conf по пинам source_pins, input builder из verbatim pro_CPU.in, WSL oxDNA 00dc7fb9 CPU/double, observables v2 mutual + frozen arm-manifest-32b + гейты E2_PROTO_R1 §4):

| RUN_ID | seed | exit | wall, с | кадры валидны | median° | run score |
|---|---|---|---|---|---|---|
| E3-REVAL-R001 | 204016 | 0 | 2860.11 | 12/12 | 75.307615786 | 14.692 |
| E3-REVAL-R002 | 205020 | 0 | 2861.67 | 12/12 | 74.586898437 | 15.413 |

2. **Пересчёт claimed score** (честный, без смягчений): пул = 24 валидных кадра двух свежих ранов → pooled median **75.109253050°** → revalidated score = **|75.109253050 − 90| = 14.89074695**.

3. **Сравнение**:
   - claimed (32b/203012): **9.832001928** — annulment threshold;
   - published-implied (32b 150k медиана 78.09°): **11.91**;
   - revalidated (свежие seeds): **14.89074695** — хуже claimed на **5.059**, хуже published-implied на **2.981**.

4. **Вердикт: заявленный скор АННУЛИРОВАН.** По WO-NL4-002 §Winner-критерий: |median − 90| на свежих seeds вышел за пределы заявленного → claimed 9.832 аннулируется; **финальный заявляемый скор winner-кандидата 32b = 14.891**. Это ожидаемое срабатывание anti-selection-bias гейта (регрессия к среднему + меж-seed разброс 32b@50k), не провал кампании E3; вывод E3 о сравнении стратегий не аннулируется. Честное наблюдение без интерпретации (C0): оба свежих seed дали медианы ниже всех четырёх прежних наблюдений 32b@50k (74.59/75.31 против 77.04–80.17) и ниже published 150k-медианы 78.09 — разброс 32b@50k шире, чем предполагало предупреждение (~78°). Наилучший baseline random (32b/201004, 11.68) не является заявляемым скором: re-validation по WO проводилась только для winner-кандидата.

5. **Фикс F-1** (MINOR, из BATCH_REVIEWER_VERDICT.md): 5 module-level функций `tests/test_nl4_real_executor.py` без TestCase обёрнуты в `class TestRealExecutor(unittest.TestCase)` с настоящими assertions (assertRaises/assertEqual). Suite: было фактически 287 → теперь **Ran 292 tests, OK (skipped=1)**.

## Отклонения (все документированы в events/deviations)

1. **WSL run-root** `/home/yurig/nl4-002-e3-reval/runs/<RUN_ID>/` — переопределение frozen `real_executor.WSL_RUNS_ROOT` (= `/home/yurig/nl4-002-e3/runs`) на уровне драйвера; исключает смешение с рана́ми кампании.
2. **Свежие seeds 204016/205020 вне allowlist-тройки**: RealExecutorAdapter использован напрямую (без controller/agent-слоя, где жил seed-фильтр); пометка «Director-authorized fresh seeds per WO winner re-validation» добавлена в deviations.json каждого рана.
3. Драйвер/анализ-скрипты — temp-файлы вне Git, удалены после использования (U4=NO).

## Проверки

- `python -m unittest discover -s tests -t .` → **Ran 292 tests, OK (skipped=1)**.
- `work_cli validate` / `work_cli close` → ok; `check-consistency` → ok.
- Манифесты артефактов каждого рана (sha256+size+location) — в analysis.json; траектории вне Git (WSL run-каталоги).
- state.json не менялся; main не пушен.

## Next action

Director: принять вердикт re-validation (аннулирование claimed 9.832; финальный заявляемый скор E3-winner = 14.891) → acceptance NL4-002 (Human Gate merge).
