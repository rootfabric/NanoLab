# WO-NL5-001-A-R1 — Release contract: schema v0.1 + rights + reproduction interface

## Паспорт

- Work Order: `WO-NL5-001-A-R1` (`NL5-001-A`, planning decomposition из `docs/control/POST_MVP_DEVELOPMENT_ROUTE_R1.md`, Phase B / ближайшая очередь A..D).
- Base: `control/post-mvp-route-r1 @ e05793cc8ff03b3b332e5221038c2e843e7cd5f77` was planning intent; actual reviewed stacked base/head lineage is recorded by Git (`e05793cc8ff03b3b1af2d81b38e39d82cd7527d6` for PR #37 head).
- Historical implementation branch: `work/nl5-001-a-release-contract-r1`.
- Risk: MEDIUM; claim ceiling C0_SOFTWARE_ONLY.

## Цель

Заморозить release contract до сборки реальной component library:

1. component-card/release/rights schemas;
2. package layout/version/immutability rules;
3. rights/citation/manifest metadata;
4. reproduction interface;
5. owner-license options memo without selecting a license.

## Историческая граница A

A @ `9cbde33b854eeeb00abde84346c17fe3080bbe50` является **pre-amendment historical subject**. Fresh Reviewer обнаружил, что исходная digest policy безусловно требовала SHA-256 и тем самым завышала доказанность 11b/32b/53b/74b. Amendment R1.1 и последующий B-Repair R1 исправляют контракт интегрированно.

Поэтому A не принимается отдельно как финальный нормативный subject; финальный NL5-001 release contract проверяется в repaired integrated B. Это не стирает A evidence и не меняет историю.

## Allowed paths исторического A

`docs/release/**`, `schemas/**`, `scripts/release/**`, `examples/release/**`, `tests/test_release_contract.py`, A execution evidence.

## Forbidden

canonical state/plan/roadmap; physics runs; license choice by agent; main merge.

## Acceptance transfer

Актуальные acceptance rules superseded документом `docs/release/RELEASE_CONTRACT_V0_1.md` R1.2 и Fresh Re-review repaired B. Никакой код/научное evidence A задним числом не объявляется PASS.
