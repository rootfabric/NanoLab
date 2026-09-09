# EX-NL1-001-R1 — Summary (NL1-001: pin environment and upstream smoke)

Статус: **IMPLEMENTED — HANDOFF to independent REVIEW + VERIFIER**. Merge в `main` — Human Gate.

## Что сделано

1. **Среда зафиксирована** ([ENGINE_ENVIRONMENT_R1](../../research/ENGINE_ENVIRONMENT_R1.md)): WSL2 Ubuntu 24.04.2 + gcc 13.3.0 + user-local cmake 3.31.6 (SHA-256 сверен с Kitware); oxDNA собран из pinned upstream commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` (CPU, Release, DOUBLE=ON, CUDA/MPI=OFF); SHA-256 бинарей записаны; commands полностью воспроизводимы.
2. **Fixture верифицирован**: 4/4 SHA-256 MATCH против пинов `E1-PROTO-R1` §2.2 (blob SHA-1 4/4); обнаружено и задокументировано правило байт-точного извлечения (autocrlf-ловушка Windows working tree → только `git cat-file blob`).
3. **Upstream smoke go/no-go** (`EX-NL1-001-SMOKE-001`, сокращённый вход, НЕ E1): COMPLETED, exit 0, wall 0.13 s, RSS 6424 KB, NaN/Inf нет, «everything went OK».
4. **UNKNOWN `E1-PROTO-R1` §11.1–2 закрыты**: interaction_type=dna default (average, без seq-файла), john=BrownianThermostat-alias (pt=0.019929118, pr=0.006687465 по формулам исходников), T=0.097717, salt NOT_APPLICABLE, seed случайный; семантика колонки 2 energy.dat (U/N) подтверждена исходником (§11.3).
5. **Бюджет для NL1-002** (planning input): ~10–15 c/прогон на 1 ядре, ~6–10 MB RAM → кампания T1+3 pilot ≪ 1 core-hour.

## Результаты

- execution_outcome smoke: `COMPLETED` (exit 0). scientific_outcome: `NOT_EVALUATED` (C0 — smoke вне научного сравнения).
- Verbatim `quick_input` (1e6 steps) **не запускался** — запрет `E1-PROTO-R1` §7 соблюдён; E1 стартует только в NL1-002 после ACCEPTED NL1-001.

## Evidence paths

```text
docs/research/ENGINE_ENVIRONMENT_R1.md
docs/evidence/NL1-001/IMPLEMENTER_EVIDENCE.md
docs/evidence/NL1-001/smoke-run/{log.dat, energy.dat, quick_input_smoke, time.log}
docs/work/executions/EX-NL1-001-R1/** (passport, events 0001–0004)
```

## Open risks

См. IMPLEMENTER_EVIDENCE §«Оставшиеся риски» (march=native привязка; неэфемерность WSL; stale docs john-алиаса; прокси-маршрут fetch).

## Следующее действие (одно)

Независимый REVIEWER: верифицировать evidence-пакет против exact HEAD и выставить вердикт в `docs/evidence/NL1-001/REVIEWER_VERDICT.md`; затем независимый VERIFIER (fresh checkout, перепроверка хэшей/команд) с вердиктом в `VERIFIER_VERDICT.md`; затем Director checkpoint и PR (merge — Human Gate).
