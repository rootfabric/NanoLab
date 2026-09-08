# NanoLab — Agent Router

Канонический репозиторий: `rootfabric/NanoLab`. Root `AGENTS.md` маршрутизирует работу; roadmap и scientific truth берутся из `main`.

## Mandatory read order

Перед изменением кода, запуском эксперимента, review или объявлением checkpoint читать:

```text
PROJECT_CONTROL.md
HARNESS_CONTROL.md
docs/control/DEVELOPMENT_HARNESS_RU.md
docs/control/HARNESS_REVIEW_AND_EVIDENCE_RU.md
docs/control/HARNESS_AUTONOMOUS_EXECUTION_RU.md
docs/control/EXPERIMENT_HARNESS_RU.md
docs/control/BRANCHING_AND_GIT_RU.md
project/state.json
project/plan.json
config/control/harness/project-goals.v1.json
config/control/harness/checkpoint-catalog.v1.json
```

Если задача относится к CI, runner, GPU, artifact storage, scheduler, AiiDA/HPC или другой вычислительной инфраструктуре, дополнительно читать:

```text
docs/infra/README.md
docs/infra/ROADMAP.md
docs/infra/SECURITY_MODEL.md
docs/infra/EXECUTION_BACKENDS.md
project/infra-plan.json
project/infra-state.json
```

Научный frontier и INFRA frontier независимы. INFRA не может самостоятельно закрывать `NL*` checkpoint или повышать scientific claim. Конкретный scientific Work Order объявляет зависимость от INFRA capability только явно.

Затем читать `docs/SCIENTIFIC_METHOD.md`, активный Work Order, паспорт эксперимента и ближайшие scoped инструкции.

## Hard rules

```text
MAIN DECLARES PROJECT STATE
BRANCHES REPORT EXECUTION FACTS
GIT IS DURABLE MEMORY; CHAT IS NOT
WORK ORDER IS THE EXECUTION UNIT
EXPERIMENT RUN IS THE SCIENTIFIC EXECUTION UNIT
COMMIT IS THE RECOVERY UNIT
EVIDENCE MAP IS THE REVIEW UNIT
IMPLEMENTER CANNOT SELF-ACCEPT
EXIT CODE 0 IS NOT A SCIENTIFIC PASS
SCIENTIFIC CLAIM MUST NOT EXCEED EVIDENCE
NEGATIVE / FAILED / INCONCLUSIVE RESULTS MUST BE PRESERVED
DO NOT CHANGE ACCEPTANCE CRITERIA AFTER SEEING RESULTS WITHOUT A NEW PROTOCOL REVISION
DO NOT REUSE A FAILED RUN ID
RAW ARTIFACT REUSE REQUIRES DIGEST + PROVENANCE
INFRASTRUCTURE PROVIDES CAPABILITY; IT DOES NOT DECLARE SCIENTIFIC TRUTH
PUBLIC PR CODE MUST NOT AUTOMATICALLY RUN ON TRUSTED SELF-HOSTED SCIENTIFIC NODES
```

## Work protocol

1. Проверить fresh `main`, соответствующий state (`project/state.json` или `project/infra-state.json`) и next Work Order.
2. Создать scoped branch от exact main; записать base SHA.
3. До substantive work создать durable START record и commit/push.
4. Выполнять только bounded scope и утверждённый resource budget.
5. После смыслового этапа/batch/blocker/handoff публиковать CONTINUATION checkpoint.
6. Для experiment campaign до запуска freeze protocol, code/model subject, inputs/digests, observables, statistics, exclusions, budget и stop conditions.
7. Каждый run получает уникальный ID; технический outcome и научный conclusion фиксируются отдельно.
8. Большие raw outputs не обязаны жить в Git, но manifest с SHA-256, размером и location обязателен.
9. MEDIUM+ получает Reviewer; HIGH scientific work — Reviewer + Verifier + Director. Implementer не self-accept.
10. `FIX_REQUIRED` исправляется с Repair Map и новым evidence, а не повторением того же действия.
11. Перед handoff оставить exact HEAD/TREE, commands, results, evidence paths, open risks и одно next action.
12. Merge в `main` остаётся Human Gate, если владелец явно не разрешил его в текущей mission.

## INFRA work protocol

INFRA — отдельный parallel capability train `INFRA0..INFRA7`. Каждая крупная стадия выполняется отдельной bounded веткой `infra/<checkpoint>-<slug>-rN` от свежего `main`; не поддерживать бесконечную long-lived infra branch.

До self-hosted execution сначала закрывается security/control baseline. Для публичного repository PR checks используют untrusted/ephemeral route; trusted self-hosted runner выбирается только explicit protected dispatch с exact subject и budget.

## Experiment Git checkpoints

Обязательные точки:

```text
START
  manifest + protocol + frozen subject + inputs

CONTINUATION
  phase/batch completed, blocker, repair, role handoff

END_EXECUTION
  completed/failed/aborted/blocked + artifact manifest

END_ANALYSIS
  observable/statistics + scientific outcome

REVIEW
  independent verdict + claim ceiling
```

Старые experiment events не редактировать; corrections/superseding — новым event.

## Resources and safety

Не запускать платные GPU/CI/внешние сервисы сверх budget. Не запускать физический wet-lab/hardware experiment по правилам вычислительного harness: такие работы `CRITICAL` и требуют отдельного human/domain gate. Не скрывать секреты и не изменять систему владельца глобальными установками без scope.

## Git authority

Внутри активного Work Order без нового запроса разрешены: scoped branch/worktree, stage, commit, non-force push, draft PR, evidence publication, review request. Не разрешены: direct push main, force-push/history rewrite, destructive remote deletion, foundation authority change.

## Language

Проектные документы и отчёты — русский. Code identifiers, schemas, event/status names и commit type — английский. Conventional Commits обязателен для обычных development commits.
