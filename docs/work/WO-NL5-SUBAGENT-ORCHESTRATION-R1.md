# WO-NL5-SUBAGENT-ORCHESTRATION-R1 — C0 план распределённого исполнения NL5

Статус: **STARTED / PLAN_PREPARATION_ONLY**. Parent: [Issue #81](https://github.com/rootfabric/NanoLab/issues/81). Subagent tasks: [#82](https://github.com/rootfabric/NanoLab/issues/82)–[#93](https://github.com/rootfabric/NanoLab/issues/93).
BASE = `3b567ae33f247b182b2ae451d2cc4598a9e76019` / TREE `560dc913a71a237d3c452a5a2e492e213b232911`.
Branch: `plan/nl5-subagent-orchestration-r1`, Execution: `EX-NL5-SUBAGENT-ORCHESTRATION-R1`.
Risk: **MEDIUM** (control documentation); scientific claim: **C0_SOFTWARE_ONLY**; scientific runs: **0**.

## Цель
Подготовить прочитываемый новым Director подробный исполняемый DAG NL5 с настоящими субагентскими ролями и неизменяемыми научными воротами FROZEN_R2. Создать маршрут task issues → role prompts → role-separated evidence → owner Human Gate. Само выполнение U1/R2/научных вычислений **НЕ входит** в этот WO.

## Scope — allowed only
- `docs/work/WO-NL5-SUBAGENT-ORCHESTRATION-R1.md`
- `docs/control/NL5_SUBAGENT_EXECUTION_PLAN_R1.md`
- `docs/control/NL5_SUBAGENT_TASK_GRAPH_R1.json`
- `docs/work/prompts/NL5_DIRECTOR_SUBAGENT_R1.md`
- `docs/work/executions/EX-NL5-SUBAGENT-ORCHESTRATION-R1/**`
- `docs/work/WORK_QUEUE.md` (только append-only новая запись)

## Forbidden
`project/state.json`, `project/plan.json`, `project/infra-state.json`, `project/infra-plan.json`, `docs/evidence/NL5-V02-FREEZE/**`, `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md`, frozen seed/contract, accepted scientific data, `scripts/nl5/**`, `scripts/r2/**`, paid compute, U1/U2 activation, MD/oxDNA runs, self-review, force-push, direct main write or actual scientific dispatch.

## Preconditions & invariants
- Canonical `NL5=IN_PROGRESS`; original NL5-002 terminal MISMATCH preserved.
- F2 `60da9a846511265a8ac7564da088c3d74cb073f0`, tree `e565c8a6cee9e829fac14008ebc9c2ea1609931d` frozen immutably.
- R2 `WAITING_HOST/NOT_ACTIVE`; U1 absent by latest evidence. Never convert this planning task into `R2=ACTIVE`.
- BUS-001 production workflow unavailable until own independent gates; no simulated queue/lease/subagent identities.

## Required outputs
1. Human-readable NL5 subagent plan: every stage/role/dependency, immutable frozen budget and stop conditions, gate owner, evidence and honest failure outcomes.
2. Machine-readable proposed task DAG with `NOT_STARTED` statuses and child Issue IDs, no fabricated job/session IDs.
3. Director role prompt with actual launching/checkpoint logic, handoff and `WAIT_EXTERNAL` fallback.
4. Passport/events/evidence/summary + append-only queue proposal; draft PR only, not canonical state change.

## Validation and review
- JSON parser strict, DAG dependencies refer to known task IDs and ordering is acyclic, job budget 296+56=352, max wall 560h/platform and 0 science.
- `python3 -m unittest discover -s tests -t .` existing suite; `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .`, `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .`, `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-SUBAGENT-ORCHESTRATION-R1`.
- Hosted CI exact HEAD; fresh independent Reviewer + separate Verifier. Merge remains Human Gate; user requested the plan, **not** activation or science.

## One next action
Publish plan/docs and hand off to fresh Reviewer of orchestration; after human adoption Director reads the plan, starts C0 F01 in a *different actual session*, and waits for U1 owner allocation.
