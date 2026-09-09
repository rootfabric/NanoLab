# EX-INFRA0-001-R1 — Summary

```text
BASE_SHA = 57c1e63733ea3b10f991c0f9609c426dc75b17a5 (exact canonical main, live-verified)
HEAD     = см. binding ниже
TREE     = фиксируется terminal event 0004 и PR (candidate head)
```

## Binding (hardening: terminal event ↔ final handoff HEAD)

```text
START_COMMIT          = ff68c12e6a8b5a2e09d32796f462f5ee6ba885e6  (harness: start INFRA0-001 execution; pushed до substantive work)
IMPLEMENTATION_COMMIT = 870f52e309a85da1dd5fb95c0d67498f2f573898  (docs: define INFRA0 compute trust and execution baseline R1)
                        tree = aba753e218eba949270957dbcc9628060a53f6a3
SUBSTANTIVE_HEAD      = коммит, непосредственно предшествующий terminal event
                        (содержит все substantive артефакты включая этот summary);
                        exact SHA записан в 0004-handoff-completed.subject_sha
HANDOFF_COMMIT        = единственный коммит ПОСЛЕ terminal event; содержит только
                        0004-handoff-completed.json + статус passport/branch-passport;
                        substantive результат не меняет
```

## Параметры

```text
WORK_ORDER = INFRA0-001 (docs/work/WO-INFRA0-001.md, существует в main; создание не требовалось)
RISK       = MEDIUM (repository_automation / security control policy → Reviewer + Verifier)
CLAIM      = C0_SOFTWARE_ONLY (baseline не является научным claim)
```

## Результаты

```text
BASELINE    = EXECUTION-BASELINE-R1 PROPOSED (docs/infra/EXECUTION_BASELINE_R1.md)
  trust     = UNTRUSTED / TRUSTED_CONTROL / SCIENTIFIC_ARTIFACTS; граница по происхождению кода
              (canonical main + explicit protected dispatch), не по авторству PR
  routes    = TR-PR и TR-PUSH-MAIN → только GitHub-hosted (H0);
              TR-DISPATCH → protected self-hosted допустим только с exact subject_sha +
              work_order_id + resource budget (RESERVED_NOT_ACTIVE, fail closed);
              TR-SCHEDULE/TR-TAG deferred; TR-PRT (pull_request_target) и TR-WFRUN (workflow_run)
              = FORBIDDEN_R1
  runners   = H0 hosted (ubuntu-latest/ubuntu-24.04); C0 `nanolab-cpu`, G0 `nanolab-gpu`,
              H1 `nanolab-hpc-*` — зарезервированы, НЕ зарегистрированы; self-hosted labels
              запрещены в runs-on PR-маршрутов; self-hosted runner не носит hosted labels
  token     = repo default read-only (target), per-workflow минимальный permissions,
              PR route contents:read, fork PR без secrets, без долгоживущих credentials
  budgets   = RC0 ≤15 min / RC1 ≤60 min hosted; RC2 trusted CPU — budget обязателен в dispatch,
              числа — измерениями INFRA2/3; RC3 GPU forbidden до INFRA5; unbounded jobs
              запрещены; rerun не увеличивает бюджет; paid compute forbidden
  artifacts = provenance sha256/size_bytes/producer_run_id/subject_sha/storage_location;
              hosted CI артефакты не scientific evidence; raw вне Git — manifest в Git;
              rerun проверяет существующий manifest до вычисления
  negatives = NC-1..NC-7 (PR route не может выбрать self-hosted label; запрет untrusted→trusted
              транзита; dispatch без подотчётности отклоняется; токен PR route не пишет;
              fail closed без hosted; rerun не эскалирует бюджет; secrets не текут в fork PR)
              — механическая проверка NC-1/NC-2/NC-4/NC-7 = INFRA1-002, NC-3 = INFRA2-002
  threats   = матрица actor × vector × asset × control × residual risk (§9)
  запреты   = 11 явных non-goals этапа (без runner-установок, workflows, secrets, artifact store,
              GPU/scheduler/HPC, paid compute, physical, campaigns, изменения state-файлов,
              self-accept)
CONFIG      = config/infra/execution-baseline.v1.json (машинно-читаемая проекция, status PROPOSED;
              вход для механических проверок INFRA1-002 и dispatch-валидатора INFRA2-002)
```

## Validation

```text
python -m json.tool (passport, events 0001-0002, baseline config, infra-plan, infra-state) -> 6/6 OK
CONTROL_WORK.ps1 validate (pre-handoff)     -> ok=true, errors=[]
CONTROL_DEVELOPMENT.ps1 -CheckConsistency   -> ok=true, errors=[], warnings=[]
CONTROL_WORK.ps1 close (после terminal)     -> выполняется перед финальным push
```

## Отклонения и ограничения

- Паспорт использует `checkpoint: INFRA0`; паттерн `^NL[0-8]$` в execution-passport.schema.v1.json не покрывает INFRA-трек. Схема не менялась (вне allowed_paths); валидатор паттерн не проверяет. Расширение схемы — кандидат в отдельный control WO.
- Machine-readable конфиг размещён в `config/infra/` по явному указанию миссии (WO scope упоминал `config/control/infra/**`); путь задокументирован в passport allowed_paths.
- Negative test WO реализован документально (NC-1); механическая проверка — зависимость `INFRA1-002` по infra-plan, не этот WO.
- Baseline `PROPOSED`: capability не объявлена принятой; `project/infra-state.json` не изменён (Director gate); merge — Human Gate.

## Факты для аудита

```text
RUNNERS_REGISTERED        = NONE
WORKFLOWS_ADDED           = NONE (.github/workflows не тронут)
SECRETS_ADDED             = NONE
SCIENTIFIC_CAMPAIGNS_RUN  = NONE (E0–E6 NOT_RUN, physics_runs = 0)
PAID_COMPUTE              = NONE
project/infra-state.json  = не изменён Implementer'ом
project/state.json        = не изменён Implementer'ом
ACCEPTED                  = не выставлен (MEDIUM: Reviewer → Verifier; затем Director; merge — Human Gate)
```

## NEXT_ACTOR

```text
NEXT_ACTOR = REVIEWER, затем VERIFIER (MEDIUM routing по risk-policy).
Reviewer: инварианты границы полны? routes/guards согласованы с SECURITY_MODEL? запреты не дырявы?
Verifier: diff в allowed_paths, JSON по схемам/валиден, commands/SHA сходятся по exact HEAD,
          state-файлы не тронуты.
Director: checkpoint proposal INFRA0; merge PR — Human Gate; обновление infra-state.json — после merge.
```
