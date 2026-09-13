# Director Acceptance R1 — NL4-001 (bounded agent + controller + baselines) — ACCEPTED

- Дата: 2026-09-12. Authority: владелец (цепочка миссий «делай следующий шаги»/«продолжай»; frontier NL4 задан решением о закрытии NL3).
- Execution: `EX-NL4-001-R1` @ exact HEAD `4ef7b9c` (work/nl4-001-bounded-agent-r1: 6b8efff → 8009f16 → 4ef7b9c).
- Independent REVIEWER: **PASS** (`10d5cbe`, 10/10; ключевая проверка — безопасность allowlist собственными fail-closed пробами ревьюера). Independence caveat зафиксирован (fresh-сессия, тот же хост).
- Coordination checks: 287 тестов OK собственным прогоном координатора; validate ok (HANDOFF_READY); consistency ok; forbidden paths чисты; verdict-дифф = один файл.

## Принято

**NL4-001 = ACCEPTED** (C0_SOFTWARE_ONLY; инфраструктура NL4, zero physics): пакет `scripts/nl4/` — allowlist (4 действия, варианты {0b..74b}, steps {50k/100k/150k}, seed-тройка, бюджеты, forbidden-поля), контроллер (fail-closed цикл, канонический evidence), mock-ExecutorAdapter (детерминированный, готов к подмене реальным движком в NL4-002), baselines random/grid (детерминированные, budget accounting), bounded_agent (allowlist-валидация ДО исполнения + rejected log) + ScriptedBrain, scoring по frozen гейтам E2_PROTO_R1 §4. 45 новых тестов, полный набор 287 OK.

## Findings → действия

- F2 LOW (CANDIDATE_ALREADY_RUN для self-describing повторов): учесть в дизайне E3-пропозалов (NL4-002).
- F3 INFO: реальный ExecutorAdapter обязан давать консервативный wall-estimate (пилотные измерения: 0.049–0.066 s/step).
- F1/F4: cosmetic/procedure — к сведению.

## Next

**NL4-002 = READY** (E3: сравнение bounded LLM-агента vs random/grid baselines по равному бюджету; целевой угол и параметры кампании — решение владельца). Реальный ExecutorAdapter (oxDNA через WSL) — часть NL4-002.
