# Branch Passport — work/nl3-002-confirm-r1 (EX-NL3-002-R1)

- Base: `280104c07849ebbd60be686af292679a88f66b40` (main tip: freeze E2-PROTO-R1).
- Worktree: `C:\NanoLab\nl3-002-confirm`.
- Work Order: NL3-002 «Execute E2 component campaign» (issue #7); протокол кампании — `docs/research/E2_PROTO_R1.md` (FROZEN, единственный источник параметров).
- Scope: confirmatory-кампания E2-R1 на первом шарнире `0b` — 3 реплики E2-R1-C001/C002/C003, seeds 201004/202008/203012, steps = 200000, print_conf_interval = 4000 (50 кадров), print_energy_every = 100; digest-gated download-on-run (G1=B, без durable-кэша, удаление после execution); observables v2 (mutual) + integrity v1 + замороженный arm-manifest-0b.json; гейты §4 протокола; статистика §6 (median/IQR/q5–q95 + bootstrap CI 10000, seed 424242). Outcome = измеренные распределения; научные выводы не делаются; acceptance — Director после review.
- Runtime: WSL Ubuntu engine `/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA` (source commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, verified); Windows Python 3.11 для анализа/CLI; прогоны в `/home/yurig/nl3-002-confirm/runs/` (вне Git, манифесты SHA-256/size обязательны).
- Budget: ≤ 3.5 ч wall/реплика (прогноз ~2.9 ч), реплики параллельно, общий ≤ 4 ч + анализ ≤ 1 ч.
- Роль сессии: IMPLEMENTER (fresh-сессия). Reviewer/Director — отдельные сессии; merge в main — Human Gate; `project/state.json` не меняется.
