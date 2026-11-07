# EX-ATOMISTIC-ROADMAP-R1 — передача roadmap candidate

Work Order: `WO-ATOMISTIC-PRODUCT-R1`. Base: `0d8537cc368dc03ee39a543c835f72c40b651ae6` (mission START поверх FLOW dependency, не новый canonical main). Product subject: `ca8ae3136231c6b69fb79331374d4ecd599b6bd0`, tree `af283945c46d54a1bbde114b6352540ef37ffc70`.

## Результат

Добавлены независимые machine P0–P6 product plan/state; P0–P3 ближайшие engineering, P4–P6 conditional research. README/roadmap/architecture/vision/control routing согласованы. Добавлены три C0 operations cards с consumer/demo/budget/stop; `drive` рекомендует ATOMISTIC-REFERENCE-PREP отдельно от WAITING_HUMAN NL5. CLI/UI команды заданы machine argv и в README. P1 engineering delivery не блокируется OPEN material reference; validated stage acceptance рассматривается отдельно. Все P остаются без acceptance. Adapter/app tasks IN_PROGRESS: actual execution evidence не принадлежит roadmap author и здесь не выдумано.

Engineering profile только этой mission: 1 материал/модель, disposable Linux/isolated venv, ≤4096 atoms, ≤2000 MD steps/run, ≤8 actual pilot runs/1200 секунд/2 GiB суммарно, sequential. Actual calculations названы расчётами; C0 cards не дают run authority. ASE EMT Cu — SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED. Никакого NL5/E5 dispatch, U1/U2 mutation, paid compute или future campaign authority.

## Проверки

- `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` — PASS, прежние 9 NL stages / 19 tasks / 7 experiments, NL5 scientific dispatch false.
- `PYTHONPATH=scripts python3 -m harness.batch_validate json --root .` — PASS, 1528 checked, 4 pinned non-JSON fixtures.
- `PYTHONPATH=scripts python3 -m unittest tests.test_flow_throughput -v` — PASS, 54 tests.
- `git diff --check` / staged check — PASS.
- Прямой comparison с base: project/state.json и прежние goals/catalog byte-for-byte; project/plan.json без нового additive product_track полностью равен base JSON; новые P DAG/task IDs/status/consumer/demo/budget/stop и C0 cards согласованы. `recommended_operational_task=ATOMISTIC-REFERENCE-PREP`, `dispatchable=false` для NL5.

Backend/UI/tests не редактировались; actual runs roadmap agent не выполнял. Неверный START checkpoint P0 был отвергнут writer без созданных файлов; существующий harness поддерживает только NL/INFRA checkpoint IDs, поэтому administrative roadmap passport помечен текущим NL5 с явным no scientific change. Это не dependency P0→NL5.

## Остаток и next action

Candidate, независимый HIGH review/verification и canonical merge ещё не выполнены. CLI/UI команды требуют интеграции соответствующих implementation commits. Возможный budget edge передан интегратору: CLI+UI и restart должны использовать один mission-wide cumulative ledger, а не сбрасываемые session counters. P0 material reference всё ещё OPEN; принятие EMT demo за material validation запрещено.

Следующее действие: интегратору включить roadmap subject с adapter/UI candidate; по их actual evidence обновить только product delivery/evidence status отдельным scoped commit и передать единый exact subject независимым Reviewer/Verifier. Push/merge не выполнялись по поручению интегратора.

## Дополнение по поручению интегратора после handoff

Scope явно расширен интегратором: `docs/experiments/E6_ATOMISTIC_ADAPTER.md`, `docs/experiments/README.md`, исторический `docs/control/POST_MVP_DEVELOPMENT_ROUTE_R1.md`. Убрана двусмысленность «E6 deferred/после NL5» для нового ACTIVE P0–P3 engineering приоритета; исторический E6 scientific NOT_RUN/NOT_ACCEPTED, P0 OPEN и старые machine NL acceptance/dependencies не изменены. Старый post-MVP route помечен историческим с pointer на current roadmap. Initial passport/events не переписывались. Architecture уже имеет узкий candidate capability label вместо глобального «интеграция не реализована».

## Factual status update после actual CLI/UI evidence

По фактическим данным интегратора и прочитанному CLI manifest: P1 delivery IMPLEMENTED_DEMO, adapter/app WAITING_REVIEW, material NOT_EVALUATED/P0 OPEN. CLI source `599ba8d1f089d74dc5f67a33011cba020f6df57a`: 32 Cu, 10 relaxation + 50 MD steps, 0.655380319 с, manifest/digests PASS. Browser demo repaired source `71bc62102cc36bf49b04d40d81d3070d87cccad6`: 32 Cu, 10 MD steps/6 frames, 0.655919 с, form/run/playback/rotate/zoom/ZIP digest PASS. Запуски выполнены другими mission исполнителями; roadmap agent новых runs не выполнял. Final independent recheck ещё pending; будущие screenshot/review/summary paths помечены pending publication destinations, не завершёнными verdicts. Product-state не объявляет перечисленные два результата полным mission ledger. Scientific state/frozen protocols не изменены.

## Final technical status по независимым отчётам

Reviewer PASS (3 findings closed) и отдельный Verifier PASS: exact source `71bc62102cc36bf49b04d40d81d3070d87cccad6`, tree `f86af90728797541594396ac0bef0964d9f8dd28`. Verifier: 1059 tests, один явный MD skip, дополнительный actual run 32 Cu/50 MD steps (~0.656 с), same-host/same-environment numeric match к pilot 1. Всего mission 3 actual runs/~1.967 с/<200 KB raw, active reservations=0; это не external reproduction. Reports интегратор публикует в `EX-ATOMISTIC-PRODUCT-R1/review/product-review-repair-report.md` и `product-verifier-report.md`.

P1 delivery IMPLEMENTED_DEMO / technical VERIFIED, canonical_acceptance=false; P0 OPEN/material NOT_EVALUATED. Adapter/app/FLOW cards WAITING_HUMAN actor HUMAN: merge PR #96 после docs-only publication delta review, без повторной реализации/review неизменного source. P0 reference-prep остаётся первой READY задачей. Старое scientific state и physics inputs не менялись.
