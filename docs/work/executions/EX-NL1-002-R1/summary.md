# EX-NL1-002-R1 — Summary (NL1-002: первый вертикальный E1 путь)

Статус: **IMPLEMENTED — HANDOFF to independent REVIEW + VERIFIER**. Campaign-level scientific_outcome: **NOT_EVALUATED** (acceptance E1 — NL2-002). Merge в `main` — Human Gate.

## Что сделано

1. **Frozen subject до запуска**: campaign.md + protocol.json + manifests + started-events запушены (`5c8774f`) до первого прогона; пропуск S001-event починен до старта прогона (`9cc83e8`).
2. **Preparation**: fixture из сырых blob'ов pinned commit, 4/4 SHA-256; engine пересобран по `ENGINE_ENVIRONMENT_R1` §3 (`ffc80b1a…579f`); импорт-проверки go/no-go.
3. **T1 production** `E1-R1-S001`: verbatim `quick_input` (1e6 steps, seed −200619630), COMPLETED, 13.13 s / 6304 KB → avg col2 **−1.39393635864**, |Δ| 0.014234 → **IN_BAND** (execution fact).
4. **PILOT** P001–P003: все COMPLETED, IN_BAND; между-репликационное SD **0.00832919790** (5.6% полосы).
5. **Freeze**: `E1-PROTO-R2` — **R_confirm = 3** (обоснование в документе; superseding только §6.4).
6. **Архив**: все артефакты 4 прогонов в Git с artifacts.manifest.json (SHA-256/size/producer); failed/excluded = 0.

## Результаты

- Вертикальный путь E1 end-to-end исполнен с измеренными ресурсами (acceptance-элемент NL1).
- T1-факт IN_BAND — **не** acceptance: критерий §9 (T1 + все T2) проверяет NL2-002 с R_confirm = 3.
- Научные claims отсутствуют; `E0–E6` в state.json не менялись этим WO.

## Evidence paths

```text
experiments/evidence/E1/E1-R1/**  (campaign, protocol, runs, evidence-map, analyze_energy.sh)
docs/research/PREREGISTRATION_E1_R2.md
docs/evidence/NL1-002/IMPLEMENTER_EVIDENCE.md
docs/work/executions/EX-NL1-002-R1/**
```

## Следующее действие (одно)

Независимый REVIEWER → `docs/evidence/NL1-002/REVIEWER_VERDICT.md`; затем VERIFIER (fresh checkout, перепроверка дайджестов/артефактов/повторяемость анализа) → `VERIFIER_VERDICT.md`; затем Director checkpoint и PR.
