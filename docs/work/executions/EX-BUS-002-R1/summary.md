# BUS-002 — Director discoverability

Status: **HANDOFF_READY**, not ACCEPTED.

Owner requirement: an agent assigned as the central/main agent must find the distributed-workflow instructions immediately and understand what to do without prior chat context.

## Result

Root `AGENTS.md` now has an early `Central agent / Director fast path` before the normal mandatory read order. It routes Director/distributed-roadmap assignments directly to root `DIRECTOR.md`.

`DIRECTOR.md` is a compact operational entry point containing:

- distinction between normal single Work Order and distributed Director mode;
- canonical state vs Task Bus execution state;
- exact recovery/read order;
- initial `status/history` commands;
- meanings of `CLAIM`, `CONTINUE`, `DISPATCH_OR_WAIT`, `RECLAIM`, `WAIT_RECLAIM`, `BLOCKED`, `BUDGET_EXHAUSTED` and terminal states;
- the Director execution loop;
- minimum handoff packet for a real subagent/session;
- prohibition on fake self-review, fake session IDs and background promises;
- repair, block, lease expiry, candidate drift and Human Gate behavior;
- exact current pilot branches/task/Issue/PR and the rule not to re-run `init/open`.

## Exact subjects

```text
BUS-002 base:
90eb244e27b538d0955852ec5f6b3e5caf2e5d13

START:
a57fd73d7d49a6ec79c13c2bb197fffade198060

entrypoint implementation:
77df4b2a7ba3b247f1d4c3c47af9c2bdda5c86ba
```

## Validation

Fresh Git reads of `AGENTS.md` and `DIRECTOR.md` succeeded. Compare `a57fd73d... -> 77df4b2a...` contains exactly:

```text
AGENTS.md                                           modified
DIRECTOR.md                                         added
docs/work/executions/EX-BUS-002-R1/events/0002-entrypoint-added.json added
```

No `project/state.json`, roadmap, infra state, Task Bus queue, implementation code or tests changed by the substantive BUS-002 commit.

## Important deployment boundary

The entry point is currently in draft PR #20 / branch `control/git-task-bus-r1`, not canonical `main`. Therefore:

- an agent explicitly testing the current pilot must use `control/git-task-bus-r1` and will see the new root route immediately;
- a generic agent starting only from current `main` will not see `DIRECTOR.md` until the PR passes the required review/live-pilot gate and the Human Gate permits merge.

This distinction is intentional; discoverability is implemented, but canonical activation has not been silently performed.

## Next action

Run the live independent BUS-SMOKE-001 cycle and independent review. When accepted and Human Gate authorizes merge, the `AGENTS.md -> DIRECTOR.md` route becomes the default canonical entry point for all future central agents.
