# WO-NL5-001-B-REPAIR-R1 — Repair component library v0.1 after Fresh Reviewer

- Base: `work/nl5-001-b-library-assembly-r1 @ 628526594784ded8bb2067976cefbe53c4ac0e48`
- Branch: `repair/nl5-001-b-library-r1`
- Risk: MEDIUM
- Claim ceiling: C0_SOFTWARE_ONLY
- Source review: `review/nl5-001-b-r1` / `docs/evidence/NL5-001-B/FRESH_REVIEW_R1.md`
- Repair map: `review/nl5-001-b-r1` / `docs/evidence/NL5-001-B/REPAIR_MAP_R1.md`

## Scope

1. Freeze a valid independent-reproduction rule before NL5-001-C.
2. Make scientific/protocol pins evidence-derived rather than code literals.
3. Make the full release package deterministic, including `RELEASE_MANIFEST.json`.
4. Finish R1.1 digest-contract synchronization.
5. Remove stale references to nonexistent `POST_MVP_EXECUTION_PROGRAM_R1.md`.
6. Reject duplicate/unsafe manifest paths fail-closed.
7. Preserve 74b as `NOT_MEASURED`; no physics runs.

## Forbidden

- canonical state/plan/roadmap changes;
- oxDNA runs or new measurements;
- license choice on behalf of owner;
- merge/direct push to main.

## Revalidation

Full unit tests; package lint; full-package byte-identical builder check; manifest negative controls; evidence-vs-generated protocol-pin tests; reproduction-rule tests; consistency/work-close; fresh re-review.
