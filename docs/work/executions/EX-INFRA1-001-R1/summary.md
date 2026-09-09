# EX-INFRA1-001-R1 — Summary

```text
BASE_SHA = 7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de (exact canonical main, live-verified)
HEAD     = см. binding ниже
TREE     = фиксируется terminal event 0004 и PR (candidate head)
```

## Binding (hardening: terminal event ↔ final handoff HEAD)

```text
START_COMMIT          = a689711b0c7d55e3cff0e146a484a51862262e75  (harness: start INFRA1-001 hosted CI execution; pushed до substantive work)
IMPLEMENTATION_COMMITS:
  ed2d5961cb24cda692e8a5f722a73caf8db80573  ci(infra1): add hosted RC0 harness validation workflow (H0 only)
  0ab044b87e3e296942da3307f1b1c5ed0c34f5f1  docs(infra): document HOSTED_CI_R1 route mapping and machine config
                        tree = a10573f73a4e409d68b9b82b5fd15efbcbede3ff  (substantive implementation tree)
SUBSTANTIVE_HEAD      = 0ab044b87e3e296942da3307f1b1c5ed0c34f5f1 — коммит, непосредственно предшествующий
                        terminal event-коммиту (содержит все substantive артефакты:
                        workflow + config + doc; events 0002/0003 ссылаются на него);
                        exact SHA записан в 0004-handoff-completed.subject_sha
HANDOFF_COMMIT        = единственный коммит ПОСЛЕ terminal event; содержит только
                        0004-handoff-completed.json + summary.md + статус passport/branch-passport;
                        substantive результат не меняет
```

## Параметры

```text
WORK_ORDER = INFRA1-001 «Add hosted harness CI» (файл docs/work/WO-INFRA1-001.md в main отсутствует;
             scope: миссия Implementer'а + project/infra-plan.json + EXECUTION-BASELINE-R1 §13.3;
             авторство WO — Director authority, см. отклонения)
RISK       = MEDIUM (первый исполняемый CI surface, repository automation → Reviewer + Verifier)
CLAIM      = C0_SOFTWARE_ONLY (зелёный CI — технический факт, не научный PASS)
```

## Результаты

```text
WORKFLOW    = .github/workflows/hosted-ci.yml (единственный workflow этапа, HOSTED-CI-R1)
  routes    = TR-PR (pull_request -> main, fork и in-repo равноправны) и TR-PUSH-MAIN (push -> main);
              TR-PRT pull_request_target / TR-WFRUN workflow_run / schedule / tag-release физически
              отсутствуют (FORBIDDEN_R1 или deferred)
  runner    = runs-on exclusively ubuntu-latest (класс H0); ни одного self-hosted или
              nanolab-* label (NC-1); нет fallback на другой исполнитель (NC-5 fail closed)
  token     = явный permissions: contents: read, write-объявлений нет (NC-4); секреты не
              используются (NC-7); checkout persist-credentials: false
  budget    = timeout-minutes: 15 = RC0_HOSTED_VALIDATION; concurrency cancel-in-progress —
              rerun наследует бюджет, не суммирует (NC-6); RC1_HOSTED_EXTENDED объявлен, не используется
  actions   = actions/checkout@93cb6efe18208431cddfb8368fd83d5badbf9bfd (v5.0.1),
              actions/upload-artifact@330a01c490aca151604b8cf639adc76d48f6c5d4 (v5.0.0) —
              pin по full commit SHA (lightweight-теги верифицированы git ls-remote)
  checks    = 1/3 json.tool по всем tracked *.json (58/58 OK на ветке);
              2/3 harness.cli check-consistency (plan/state/goals/catalog/scheduler, stdlib-only);
              3/3 harness.work_cli validate для ИЗМЕНЁННЫХ EX-* каталогов (diff vs merge-base;
              сплошной validate невозможен — см. находки)
  artifacts = только при падении; retention 7 дней; manifest nanolab.hosted_ci_debug_manifest.v1
              с полями sha256/size_bytes/producer_run_id/subject_sha/storage_location;
              scientific_evidence: false; секреты в логи/артефакты не выводятся
CONFIG      = config/infra/hosted-ci.v1.json (машинно-читаемая проекция HOSTED-CI-R1, PROPOSED;
              вход для линтеров INFRA1-002)
DOC         = docs/infra/HOSTED_CI_R1.md (включённое/исключенное, маппинг на baseline §3–§9,
              NC-мэппинг, owner actions, находки, free tier)
```

## Validation

```text
JSON (json.tool): passport, events 0001-0003, hosted-ci.v1.json, все tracked *.json -> 58/58 OK
harness check-consistency (WSL Ubuntu 24.04, python3 3.12.3)  -> ok=true, errors=[], warnings=[]
work_cli validate EX-INFRA1-001-R1 (pre-handoff)             -> ok=true, errors=[]
YAML structural gate (triggers/permissions/runs-on/pins/PC)  -> OK
diff вне allowed_paths                                        -> пусто (6 files, +491 на 0ab044b)
hosted live run                                               -> невозможен до merge (workflow
                                                                 активируется первым PR/push в main);
                                                                 первый прогон — evidence для reviewer
```

## Находки и отклонения

- **work_cli terminal-last vs review-corrections**: `EX-INFRA0-001-R1` и `EX-NL1-001-R1` в canonical main несут пост-терминальные `CONTINUATION_CHECKPOINT` (review corrections), которые текущее правило terminal-last валидатора помечает ошибкой → Check 3 сделан diff-scoped; policy-решение (corrections-aware валидатор или формализация идиома) — `INFRA1-002`. Подробно: HOSTED_CI_R1.md §7.1.
- **WO-файл отсутствует**: `docs/work/WO-INFRA1-001.md` не существует в main; создание — Director authority, вне allowed_paths; исполнение по миссии + infra-plan + baseline §13.3.
- **tests/task_bus на main нет**: pytest-чеки живут в невлитой ветке `control/git-task-bus-r1`; включение в CI — кандидат в INFRA1-002 после влития.
- **Repository settings вне git**: repo default GITHUB_TOKEN read-only и branch protection — owner actions (HOSTED_CI_R1.md §6); каждый workflow независимо несёт явный `permissions:`.
- **Checkpoint `INFRA1` vs схема**: паттерн `^NL[0-8]$` не покрывает INFRA-трек (тот же класс отклонения, что EX-INFRA0-001-R1); валидатор паттерн не проверяет; схема не менялась.

## Факты для аудита

```text
RUNNERS_REGISTERED        = NONE (никаких self-hosted runner'ов)
WORKFLOWS_ADDED           = 1 (.github/workflows/hosted-ci.yml; hosted-only, H0, RC0)
SECRETS_ADDED             = NONE (секреты не используются ни одним шагом)
GPU / PAID_COMPUTE        = NONE (public repo → free tier; paid_compute_authorized = false)
SCIENTIFIC_CAMPAIGNS_RUN  = NONE (E0–E6 NOT_RUN, physics_runs = 0)
project/infra-state.json  = не изменён Implementer'ом (Director gate)
project/state.json        = не изменён Implementer'ом
ACCEPTED                  = не выставлен (MEDIUM: Reviewer → Verifier; затем Director; merge — Human Gate)
STATUS                    = HOSTED-CI-R1 PROPOSED; capability hosted_ci в infra-state не флипается здесь
```

## NEXT_ACTOR

```text
NEXT_ACTOR = REVIEWER, затем VERIFIER (MEDIUM routing по risk-policy).
Reviewer: маршрутная поверхность полна и не дырява (нет TR-PRT/TR-WFRUN/fallback)? NC-инварианты
          соблюдены конструктивно? выбор чеков корректен для untrusted hosted? находка §7.1
          (work_cli vs review-corrections) — корректная интерпретация?
Verifier: diff в allowed_paths, JSON/YAML валидны, pins = реальные commit SHA, commands/SHA
          сходятся по exact HEAD 0ab044b, state-файлы не тронуты.
Director: checkpoint proposal INFRA1-001; merge PR — Human Gate (первый live hosted-прогон
          произойдёт на PR — проверить лог как evidence); обновление project/infra-state.json
          (frontier/task_status/capabilities.hosted_ci) — только после принятого merge.
```
