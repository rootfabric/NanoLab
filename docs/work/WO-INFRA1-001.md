# Work Order INFRA1-001 — Safe GitHub-hosted CI

Статус: **BACKFILL** — опубликован задним числом при Director-checkpoint R1 (NOTE-2 вердикта REVIEWER `0f1c348`, finding 2 вердикта VERIFIER `22394cc`). Авторство WO — Director authority; исполнение велось до публикации файла по миссии владельца, `project/infra-plan.json` (задача `INFRA1-001 «Add hosted harness CI»`, depends_on ACCEPTED `INFRA0-001`) и `EXECUTION-BASELINE-R1` §13.3. Track: `INFRA`. Checkpoint: `INFRA1`.

Фактическая ветка исполнения: `infra/infra1-hosted-ci-r1` (substantive HEAD `0ab044b`, handoff-tip `ff8d86a`).

## Цель

Добавить первый исполняемый GitHub-hosted workflow репозитория, обслуживающий untrusted/canonical маршруты строго по контрактам `EXECUTION-BASELINE-R1` §3–§9: TR-PR и TR-PUSH-MAIN, только hosted runner-класс H0, минимальные read-only permissions, pinned actions, ограниченный бюджет RC0, failure-only артефакты с provenance.

## Scope

Разрешено:

- `.github/workflows/hosted-ci.yml` — единственный hosted workflow этапа;
- `config/infra/hosted-ci.v1.json` — машинно-читаемая проекция;
- `docs/infra/HOSTED_CI_R1.md` — документация маршрутов, чеков, owner actions;
- `docs/work/executions/EX-INFRA1-001-R1/**` — паспорт, события, summary.

Не разрешено:

- регистрация self-hosted runner'ов и любые labels, кроме стандартных hosted;
- repository secrets и любое использование `secrets.*` в шагах;
- запрещённые маршруты baseline §4: `pull_request_target` (TR-PRT), `workflow_run` (TR-WFRUN), `schedule`, tag/release-триггеры, `workflow_dispatch` (RESERVED_NOT_ACTIVE);
- write-permissions (contents/pull-requests/releases/events) на hosted route;
- изменение `project/state.json` и `project/infra-state.json` (Director gate);
- scientific campaigns, paid compute, fallback на другой исполнитель при недоступности hosted (NC-5).

## Required outputs

1. Hosted workflow `hosted-ci.yml`: чеки JSON-syntax всех tracked `*.json`, `harness.cli check-consistency`, diff-scoped `harness.work_cli validate` изменённых EX-* каталогов.
2. Machine-readable проекция `config/infra/hosted-ci.v1.json` (вход для линтеров INFRA1-002).
3. Документация `docs/infra/HOSTED_CI_R1.md` с owner actions (repo default token read-only, branch protection — вне git).
4. Exact next Work Order `INFRA1-002` «Add PR validation gates».

## Acceptance

- public/untrusted PR path и canonical push-main path обслуживаются только hosted H0; forbidden-маршруты физически отсутствуют;
- permissions read-only (`contents: read`), секретов нет, actions запинены по full commit SHA;
- бюджет ≤ 15 минут, concurrency cancel-in-progress, артефакты только при падении;
- никакой научный claim не меняется; `capabilities.hosted_ci` не флипается имплементёром (Director gate);
- fresh Reviewer и Verifier PASS на exact substantive HEAD; merge — Human Gate; первый live-прогон workflow — evidence.
