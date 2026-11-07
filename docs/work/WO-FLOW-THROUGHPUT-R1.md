# WO-FLOW-THROUGHPUT-R1 — ускорение разработки без ослабления научных критериев

START: 2026-10-28T03:11:46.106Z. Owner request: внедрить предложенные по аудиту изменения harness и roadmap; продолжить прерванную операцию.

Base: `main@3b567ae33f247b182b2ae451d2cc4598a9e76019`, tree `560dc913a71a237d3c452a5a2e492e213b232911`.
Branch: `control/flow-throughput-r1`. Risk HIGH: control/risk/CI. Claim C0_SOFTWARE_ONLY.

Scope: readiness-aware routing и отдельные operational cards; writer новых work events; пакетная CI-валидация без удаления tests; impact-based review и reuse только при доказанной неизменности subject; актуальная roadmap, команды и source/integrator roles; resource correction addendum.

Scientific protocols, inputs, seeds, N, criteria, frozen F2 и исторические experiment events неизменны. U1 не назначается фиктивно, U2 не объявляется исправленным, R2 не активируется. Scientific runs=0, paid compute=0. Main не меняется без Human Gate и независимого review. Task Bus production и self-hosted PR execution не активируются.

Validation: focused negative/regression tests, полный unittest suite, consistency, все passports/events, workflow security lint. Budget: до 6 H0 CI jobs <=15 минут каждый и локальные C0 tests. Временный read-only H0 recovery exporter публичной Git-истории base удаляется до handoff; его artifact имеет TTL 1 день, secrets/config не экспортируются.

Outputs: code, tests, operational roadmap, planning corrections и один PR #95. Реализация не self-accepts; HIGH-политика для этого пакета не понижается им самим.
