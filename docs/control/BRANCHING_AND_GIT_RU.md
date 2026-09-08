# NanoLab — Branching и Git protocol

## Canonical branch

`main` — единственный canonical project state. Рабочая ветка создаётся от проверенного fresh `main`.

```text
work/nl1-002-reference-run-r1
experiment/e1-reference-reproduction-r1
repair/nl2-002-statistics-r1
control/harness-r1
docs/source-audit-r1
```

## Durable checkpoints

Минимум:

```text
START
  branch passport / Work Order / exact base

CONTINUATION
  после смыслового этапа, batch, blocker или handoff

END
  result/evidence/review status + next action
```

Для experiment campaign применяются дополнительные checkpoints `EXPERIMENT_HARNESS_RU.md`.

## Commits

Conventional Commits. Рекомендуемые scopes:

```text
harness:
control:
experiment(E1):
analysis(E1):
review(E1):
docs:
fix:
test:
```

Примеры:

```text
harness: start NL1-002 execution
experiment(E1): start reference campaign
experiment(E1): checkpoint replica batch 01
experiment(E1): record technical completion
analysis(E1): publish preregistered observable
review(E1): verify exact-head evidence
```

## PR

PR содержит Work Order/checkpoint, exact base/head, scope/diff, commands/tests, campaign IDs, evidence paths, failed/inconclusive outcomes, risk/claim class, review status, remaining risks и requested decision.

Merge в `main` — Human Gate до изменения policy.
