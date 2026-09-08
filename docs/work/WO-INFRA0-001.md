# Work Order INFRA0-001 — Compute trust and execution baseline

Статус: **READY after track activation merge**. Track: `INFRA`. Checkpoint: `INFRA0`.

Предлагаемая ветка: `infra/infra0-security-control-r1`.

## Цель

Подготовить исполняемый security/control baseline перед созданием GitHub workflows и self-hosted runner: определить trusted trigger routes, runner labels, permissions, execution budgets, artifact policy и негативные controls.

## Scope

Разрешено:

- `.github/workflows/` только для минимального validation prototype;
- `docs/infra/**`;
- `config/control/infra/**`;
- `project/infra-*.json`;
- tests/scripts, относящиеся только к infra policy validation.

Не разрешено:

- устанавливать/регистрировать runner на личном сервере в этом Work Order;
- запускать E1/E2 scientific campaign;
- добавлять repository secrets;
- менять scientific `project/state.json`;
- включать автоматический self-hosted execution для public PR.

## Required outputs

1. Machine-readable runner/dispatch policy.
2. Threat model validation matrix.
3. GitHub-hosted vs self-hosted routing contract.
4. Negative test: untrusted PR route не может выбрать self-hosted scientific label.
5. Exact next Work Order `INFRA1-001` или bounded repair.

## Acceptance

- public PR path и trusted scientific path технически различимы;
- self-hosted runner не является default PR executor;
- permissions/budget/artifact requirements заданы;
- никакой scientific claim не меняется;
- fresh Reviewer/Verifier проверяют control policy до перехода к INFRA1.
