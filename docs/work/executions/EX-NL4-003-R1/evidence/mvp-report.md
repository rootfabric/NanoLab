# MVP-отчёт NL4 (EX-NL4-003-R1)

Статус: measured-only clean-room прогон (claim C0_SOFTWARE_ONLY).

## Цель (goal)

- target_angle = 90°; max_simulations = 3; steps = 50000; revalidation_runs = 1
- Стратегия: mvp-informed-greedy-r1 (детерминированная, без LLM)
- Published-prior: docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/parametric-summary.json (pooled common-window t <= 150000 medians, valid frames only)

## Раны (кандидаты)

| RUN_ID | variant/seed/steps | median° | score | валидность | wall, с | digest |
|---|---|---|---|---|---|---|
| E3-MVP-C001 | 32b/201004/50000 | 78.32 | 11.677 | OK | 2981.95 | `1ae2273f99e1` |
| E3-MVP-C002 | 11b/202008/50000 | 73.28 | 16.720 | OK | 3143.63 | `83a7b4e40e42` |
| E3-MVP-C003 | 0b/203012/50000 | 67.31 | 22.691 | OK | 2900.08 | `82cd348ea0b1` |

## Распределение угла (валидные кадры, observables v2 mutual)

| RUN_ID | кадров (валид/всего) | min° | median° | max° | CI95 median |
|---|---|---|---|---|---|
| E3-MVP-C001 | 12/12 | 76.89 | 78.32 | 81.26 | [77.72, 80.06] |
| E3-MVP-C002 | 12/12 | 72.90 | 73.28 | 74.31 | [73.19, 73.84] |
| E3-MVP-C003 | 12/12 | 66.12 | 67.31 | 68.41 | [66.64, 67.74] |
| E3-MVP-REV001 | 12/12 | 73.85 | 75.60 | 77.50 | [74.50, 76.73] |

## Гейты

- E2_PROTO_R1 §4 (frozen): lbf ≤ 0.1078, pf_v2 ≥ 0.50, disp ≤ 20.0; статусы по ранам: {"E3-MVP-C001": "OK", "E3-MVP-C002": "OK", "E3-MVP-C003": "OK"}

## Выбранный кандидат

- best = E3-MVP-C001 (32b, seed 201004), candidate score = 11.677 (published prior для варианта: 78.092°)

## Re-validation и финальный score

- E3-MVP-REV001: 32b, свежий seed 206024; median = 75.60°, revalidated score = 14.402 (OK)
- Финальный заявляемый score = **14.402** (по re-validation; анти-bias правило NL4-002)

## Verdict

- **NOT_FOUND** (правило: FOUND iff best valid candidate exists AND revalidation passes frozen gates AND revalidated |median - target| < published-best gap; published-best gap = 11.908°); причины: REVALIDATED_SCORE_NOT_BELOW_PUBLISHED_BEST
- Формулировка: «ближайший найденный в пространстве 0b/11b/32b/53b при бюджете 3×50000 шагов, revalidated score 14.402»

## Provenance

- repo: `rootfabric/NanoLab`
- repo_commit: `9e4d7207b8997d38c00a8abbf2db205868c415d1`
- goal_file: `C:\NanoLab\mvp-goal.json`
- engine: `/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA`
- engine_source_commit: `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`
- allowlist_revision: `nl4-allowlist-r1`
- observables: `scripts/e2/observables.py v2 mutual-nearest (frozen)`
- arm_manifests: `frozen per-variant (EX-NL3-002 arm-manifest-v1)`
- runs_root: `/home/yurig/nl4-003-mvp/runs`
- revalidation_seed: `206024`
- input_digests: `{'E3-MVP-C001': '1ae2273f99e18b21c8fa3d524bc10d53bb6378ba36d193be5777f73557a0116c', 'E3-MVP-C002': '83a7b4e40e42b57766548020c6137f3004af6baa085a41294e15f8f0c3a37e33', 'E3-MVP-C003': '82cd348ea0b1446f8b94921f2d11c938401eb61abb5c34f72696b540c5d4dad5', 'E3-MVP-REV001': 'fd1794969a13f376bcbf41189efa54eab63e531de53fa8010020da9df60323fa'}`

## Ограничения (limitations)

- discrete candidate space: 4 published variants only (74b NOT_MEASURED — arm-manifest derivation BLOCKED)
- coarse-grained oxDNA model (DNA2), no claim of physical manufacturability
- angle convention R1: [0,180] deg PCA-axes unsigned; erratum E2_PROTO_R1 s.2.5 (no theta <-> 180-theta folding)
- budget: 3 candidates x 50000 steps + 1 revalidation run(s); no finer parameter search
- final claimed score is the re-validation score on ONE fresh seed (anti-bias rule NL4-002)

## Воспроизведение

- goal JSON: `{"target_angle": 90.0, "max_simulations": 3, "steps": 50000, "revalidation_runs": 1}`
- команда: `python scripts/nl4/mvp.py --goal <user-goal.json> --out-dir <evidence-dir> (from a fresh clone of commit 9e4d7207b8997d38c00a8abbf2db205868c415d1; proxy env required for digest-gated source download)`

