# Branch passport — work/nl4-002-e3-reval-r1

- Execution: `EX-NL4-002-E3-REVAL-R1` (IMPLEMENTER, fresh session)
- Work Order: `NL4-002` — winner re-validation (E3 anti-selection-bias step, verification)
- Base SHA: `e3f7e5c` (merge review/nl4-002-e3-r1: batch REVIEWER PASS) — exact `main` HEAD at start
- Worktree: `C:\NanoLab\nl4-002-e3-reval`
- Authorization: WO-NL4-002 §Winner-критерий (re-validation seeds 204016/205020 вне allowlist-тройки, Director, пост-кампания, verification-шаг) + `docs/evidence/NL4-002/BATCH_REVIEWER_VERDICT.md` (winner 32b/203012, claimed 9.832, PASS)
- Scope: 2 прогона 32b (seeds 204016/205020, 50000 шагов) через `RealExecutorAdapter` (digest-gated входы, WSL oxDNA 00dc7fb9, frozen observables v2 + arm-manifest-32b + гейты E2_PROTO_R1 §4); честный пересчёт финального claimed score; фикс F-1 (orphaned tests). state.json не меняется; main не пушится.
- Run root (WSL): `/home/yurig/nl4-002-e3-reval/runs/<RUN_ID>/` — переопределён на уровне драйвера (frozen `real_executor.WSL_RUNS_ROOT` = `/home/yurig/nl4-002-e3/runs`; отклонение документируется в deviations/events: свежий root исключает смешение с рана́ми кампании).
