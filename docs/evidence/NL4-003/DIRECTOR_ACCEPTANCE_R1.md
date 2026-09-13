# Director Acceptance R1 — NL4-003 (user-facing MVP, clean-room) + NL4 stage acceptance = MVP COMPLETE

- Дата: 2026-09-12. Authority: владелец (цепочка миссий «делай следующий шаги»/«продолжай» + интерактивные решения: NL3 closure, E3 target/бюджет, параметрика, NL4-003 dispatch).
- Execution: `EX-NL4-003-R1` @ exact HEAD `a907bf2` (work/nl4-003-mvp-r1).
- Independent BATCH REVIEWER NL4: **PASS** (`980442a`, 10/10; независимый пересчёт MVP-чисел до 1e-6; рекомендация «NL4 acceptance = MVP COMPLETE готов»). Independence caveat в вердикте.
- Coordination checks: 310 тестов OK, validate ok, consistency ok, forbidden paths чисты.

## NL4-003 = ACCEPTED

Clean-room MVP-прогон исполнен честно: fresh clone (`9e4d720`) → **unattended полный конвейер** (goal → informed-greedy план → digest-gated загрузки → 3 параллельных реальных oxDNA-рана → Controller replay → best → revalidation свежим seed 206024 → отчёт as-is). Все 4 рана exit 0, 48/48 кадров валидны, гейты зелёные, бюджет соблюдён.

**Verdict = NOT_FOUND** (revalidated 14.402 ≥ published-best gap 11.908) — **нормальный исход, поддержанный MVP**: честная формулировка «ближайший найденный в {0b,11b,32b,53b} при бюджете 3×50000 шагов — 32b, revalidated score 14.402», без обещаний физической валидности.

## Стадия NL4 = **MVP COMPLETE** (акцептанс)

| Компонент MVP | Статус |
|---|---|
| Controller + bounded agent (allowlist, бюджеты, fail-closed) | ✅ NL4-001 |
| Baselines random/grid + RealExecutorAdapter (oxDNA/WSL, digest-gated) | ✅ NL4-001/002 (18+4 рана реального движка, 0 крэшей) |
| E3 benchmark (равный бюджет, изоляция arm'ов, anti-bias re-validation) | ✅ NL4-002 (честный negative-on-advantage) |
| User-facing CLI + clean-room отчёт (provenance/limitations/reproduction; NOT_FOUND поддержан) | ✅ NL4-003 |

**Честные итоги NL4 (measured-only)**: (1) конвейер «цель → эксперименты → подтверждение → отчёт» воспроизводится clean-room; (2) все заявляемые скоры = revalidated (anti-bias гейты сработали дважды: 9.83→14.89, best-of→14.40); (3) значимое преимущество LLM перед random не выявлено при данном бюджете/пространстве — структурная приоритизация по published-знаниям зафиксирована; (4) 74b остаётся honest gap (arm-manifest-v2 — отдельный WO).

## Findings → действия

- F-B1 (input_digests — двусмысленное имя): schema-ревизия отчёта — будущий WO.
- F-B2/B3: к сведению.

## Следующая стадия

`frontier = NL5`, `next = NL5-001` (библиотека компонентов + release-пакет; внешний доступ). Открытые пункты: 74b arm-manifest-v2; LICENSE-решение владельца; E3-уроки (обогащение пространства параметров, enrichment 50k→длиннее для финальных заявок, LLM-агент на более богатых пространствах).
