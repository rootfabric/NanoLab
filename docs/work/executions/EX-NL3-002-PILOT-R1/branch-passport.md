# Branch Passport — work/nl3-002-pilot-r1 (EX-NL3-002-PILOT-R1)

- Base: `760901c8d8c66d6440693dd73b6e3f5cabd0a723` (local canonical main tip: Director acceptance NL3-002A, U-obs-1 decision, WO-NL3-002-PILOT).
- Worktree: `C:\NanoLab\nl3-002-pilot`.
- Work Order: `docs/work/WO-NL3-002-PILOT.md` (child of NL3-002), frontier NL3, E2 = NOT_RUN.
- Scope: bounded калибровочные (non-confirmatory) прогоны динамики первого шарнира `0b` — 3 реплики E2-PILOT-S001/S002/S003, seeds 101001/102002/103003; digest-gated download-on-run (G1=B, без durable-кэша); измерение per-step cost, stability smoke, integrity v1; научные исходы НЕ публикуются (NOT_EVALUATED).
- Runtime: WSL Ubuntu engine `/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA` (source commit 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591, verified); Windows Python 3.11 для анализа/CLI.
- Budget: ≤ 3 ч wall общий; steps ≤ ~25 мин/реплику engine wall, минимум 2000; 2e7 steps запрещены.
- Роль сессии: IMPLEMENTER (fresh-сессия). Reviewer/Director — отдельные сессии; merge в main — Human Gate.
