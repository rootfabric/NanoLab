# EX-NL4-003-R1 — сводка

Статус: **HANDOFF_READY** (IMPLEMENTER; MEDIUM → батчевый REVIEWER NL4 → Director: acceptance NL4 = MVP COMPLETE).
Claim ceiling: **C0_SOFTWARE_ONLY / MVP clean-run measured**.

## Что сделано

1. **MVP CLI** (`scripts/nl4/mvp.py`): вход `--goal user-goal.json` (target_angle / max_simulations / steps / revalidation_runs) → детерминированная scripted-стратегия `mvp-informed-greedy-r1` (published pooled-медианы параметрической серии зашиты как данные с ссылкой; ранжирование по |median − target|; frozen E2 seed-тройка; БЕЗ LLM) → реальные прогоны через `Controller + RealExecutorAdapter` (canonical-бюджет через ReplayExecutor, allowlist `nl4-allowlist-r1` не менялся) → best по score = |median − target| под гейтами E2_PROTO_R1 §4 → **re-validation** best свежим seed 206024 (вне frozen тройки, анти-bias NL4-002; исполняется через executor напрямую — seed не входит в enum allowlist, задокументировано) → финальный score по re-validation → отчёты `mvp-report.md` + canonical `mvp-report.json` (goal, runs+digests, распределение, gates, chosen+prior, revalidated score, confidence (кадры+bootstrap CI95), provenance, limitations, reproduction, **verdict FOUND/NOT_FOUND** — правило заморожено в коде до прогона).
2. **Тесты**: `tests/test_nl4_mvp.py` — 18 mock-тестов (детерминизм стратегии/отчёта/markdown, все verdict-ветки, goal-контракт, 74b-исключение, bootstrap-детерминизм). Полный suite — **310 OK (1 skip)**.
3. **Clean-room верификация (главный deliverable)**: свежий `git clone --branch work/nl4-003-mvp-r1` в `C:\NanoLab\mvp-cleanroom` (HEAD `9e4d720` = subject, status clean, пустые каталоги ранов); goal `{"target_angle": 90, "max_simulations": 3, "steps": 50000, "revalidation_runs": 1}`; прогон `scripts/nl4/mvp.py` целиком из clean-копии; артефакты не правились вручную, evidence опубликован as-is. Digest-гейт 3/3 PASS; раны в `/home/yurig/nl4-003-mvp/runs/<RUN_ID>/` (вне Git), манифесты SHA-256+size в evidence.

## Результаты (clean-room, measured)

| RUN_ID | Кандидат | median° | Валидность | score | wall, с |
|---|---|---|---|---|---|
| E3-MVP-C001 | 32b/201004/50000 | 78.32 | OK (12/12 кадров) | 11.677 | 2981.95 |
| E3-MVP-C002 | 11b/202008/50000 | 73.28 | OK (12/12) | 16.720 | 3143.63 |
| E3-MVP-C003 | 0b/203012/50000 | 67.31 | OK (12/12) | 22.691 | 2900.08 |
| **E3-MVP-REV001** | **32b/206024/50000 (reval)** | **75.60** | **OK (12/12)** | **14.402** | 2440.07 |

- Best = E3-MVP-C001 (32b; published prior 78.09°). Все раны exit 0, 0 STRUCTURALLY_INVALID, lbf ≤ 0.0562, pf_v2 ≥ 0.9813, disp ≤ 7.74.
- **Финальный заявляемый score = 14.402** (по re-validation, seed 206024; CI95 median [74.50, 76.73]).
- **Verdict: NOT_FOUND** — revalidated 14.402 ≥ published-best gap 11.908 (`|78.091845516 − 90|`). Нормальный исход по WO: гейты зелёные, но свежий seed не подтвердил превосходство над published-баром (согласуется с разбросом 32b@50k из EX-NL4-002-E3-REVAL-R1: 74.59/75.31/75.60 против прежних 77.04–80.17).
- Claim-формулировка: «ближайший найденный в пространстве {0b,11b,32b,53b} при бюджете 3×50000 шагов — 32b, revalidated score 14.402». Обещания изготовления/физической валидности — отсутствуют.

## Отклонения

1. `WSL_RUNS_ROOT` переопределён на `/home/yurig/nl4-003-mvp/runs` на уровне модуля в mvp.py (frozen-файлы toolchain не менялись).
2. Re-validation seed 206024 — вне frozen E2-тройки (по дизайну WO, анти-bias): исполняется через executor напрямую, не через кандидатное пространство allowlist.
3. Первый clean-room запуск упал с ModuleNotFoundError до любых ранов (sys.path при запуске скриптом) — фикс `9e4d720`, clean clone обновлён `git pull`, повторный прогон чистый; артефактов до фикса не создано.
4. 74b не предлагался: отсутствует в published-prior (NOT_MEASURED/BLOCKED) — сужение стратегии, не allowlist.

## Проверки

- unittest: 310 OK (1 skip). `work_cli validate` / `close` — ok. `harness.cli check-consistency` — ok. `state.json` не менялся.
- Временные исходники источника удалены (U4 = NO). Main не пушен.

## Next action

Батчевый REVIEWER NL4 (NL4-001/002/003 + MVP clean-run одним ревью) → Director: acceptance NL4 = **MVP COMPLETE** (merge — Human Gate).
