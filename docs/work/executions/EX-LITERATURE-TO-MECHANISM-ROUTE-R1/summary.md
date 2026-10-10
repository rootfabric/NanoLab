# EX-LITERATURE-TO-MECHANISM-ROUTE-R1 — Implementation handoff

## Identity / scope

- Base: `main @ 8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad`; exact tree on START `0eba7b901ab9991cca6b9439df227d71a90a82df`.
- Working branch: `docs/literature-to-mechanism-roadmap-r1`.
- **Implementation subject:** `22681d5e29e745170fa51a5d93bf96463bb68729` / tree `22a53b7838c27b27130270ad2cc69f23f36bff23` (handoff evidence subsequently added; final PR head is different).
- Result: **DOCUMENTATION IMPLEMENTED / REVIEW REQUIRED**; risk MEDIUM, claim ceiling C0_SOFTWARE_ONLY.
- New scientific runs: **0**; U1 activation: **not performed**; human scientific gate: **not bypassed**.

## Changed surfaces

- `docs/ROADMAP.md` — depth-first route `NL5-002 → NL6-001/E5 → NL7-001 assembly → NL8-001`, `NL6-002/E3-R2` parallel non-gating.
- `project/plan.json` + `config/control/harness/checkpoint-catalog.v1.json` — future dependencies and stage acceptance aligned without adding/removing task IDs.
- `docs/work/WORK_QUEUE.md` — planned tasks, source-pack preparation and current hold clearly separated.
- `docs/control/LITERATURE_TO_MECHANISM_ROUTE_R1.md` — complete source shortlist and design/assembly/test/validation plan.
- `docs/research/SOURCES.md` — S17 activation candidate clarified, S18–S21 registered as references (NOT_INTEGRATED).
- `docs/ARCHITECTURE.md` / `docs/DATA_CONTRACTS.md` — planned KnowledgePack, component ports, assembly compiler, test rigs and reduced-model boundaries.
- Work Order / passport / event / summary / evidence map for durable recovery.

## Static validation (GitHub connector)

- `main` at audit still = base `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad` (no main drift).
- Git compare after implementation commit: **ahead 3 / behind 0** (handoff commit adds one ahead).
- `project/state.json` Git blob byte-identical to base: frozen frontier `NL5`, task `NL5-002=WAITING_HUMAN`, `external_reproductions=0`.
- Plan JSON parse PASS; 9 stages, **19 existing tasks**, same IDs as base, references and dependencies valid; `NL6-001` depends on `NL5-002`; `NL7-001` and non-gating `NL6-002` both depend on `NL6-001`.
- Checkpoint catalog JSON parse PASS; NL6 E5 gate and NL7 mechanism assembly acceptance aligned.
- No stale requirement `NL7-001` after `NL6-002` in edited roadmap/work queue.
- S17 already existed as reference; S18–S21 are candidates, no source pack imported, license/reuse details open.
- **Not executed:** repository Python test suite, local `CONTROL_DEVELOPMENT --check-consistency`, independent scientific/model execution, external source rights audit. GitHub CI may run separately on PR.

## Explicit limits

1. NL5 scientific acceptance still open; original frozen MISMATCH and v0.2 FROZEN_R2 unaltered.
2. New scientific runs blocked until proper accepted NL5 and native Ubuntu U1/R2 activation.
3. Proposal is a roadmap, not a working assembly compiler or proof of nanomachine function/fabrication.
4. Rights for third-party code, exact topology packages and raw datasets are not assumed.
5. `docs/control/POST_MVP_DEVELOPMENT_ROUTE_R1.md` retained unchanged as historical prior routing.

## One next action

`Fresh independent Reviewer → Verifier (exact PR HEAD) → Director/Human Gate merge; after merge open PREP-S17 as separate bounded reference/input/rights audit WO (without scientific runs).`
