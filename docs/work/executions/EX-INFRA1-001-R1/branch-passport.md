# Branch Passport — EX-INFRA1-001-R1

- Branch: `infra/infra1-hosted-ci-r1`
- Work Order: `INFRA1-001` (файл `docs/work/WO-INFRA1-001.md` в canonical `main` **отсутствует**; scope определён миссией Implementer'а + `project/infra-plan.json` задача `INFRA1-001 «Add hosted harness CI»` + `docs/infra/EXECUTION_BASELINE_R1.md` §13.3; см. «Документированные отклонения»)
- Checkpoint: `INFRA1` (см. примечание о схеме ниже)
- Base SHA: `7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de` (exact canonical `main`, live-verified: `origin/main` = local `main` = base до старта; дерево чистое)
- Created from canonical main: yes
- Risk class: `MEDIUM` (repository automation / CI security surface — первый исполняемый workflow; no scientific claim → Implementer + Reviewer + Verifier по risk-policy)
- Claim class: `C0_SOFTWARE_ONLY`
- Allowed paths: see `passport.json` (`.github/workflows/**`, `docs/infra/HOSTED_CI_R1.md`, `config/infra/hosted-ci.v1.json`, `docs/work/executions/EX-INFRA1-001-R1/**`)
- Status: `STARTED`
- Active experiment campaigns: none (инфраструктурный Work Order; E0–E6 остаются `NOT_RUN`)
- START commit: фиксируется после commit/push до substantive work
- Next action: реализовать hosted RC0 workflow (H0 only, pinned actions, минимальные permissions) + HOSTED_CI_R1.md + hosted-ci.v1.json
- Blocking issue: none

## Документированные отклонения (для reviewer)

1. **Checkpoint `INFRA1` vs schema pattern.** `config/control/harness/execution-passport.schema.v1.json` задаёт `checkpoint: ^NL[0-8]$` — паттерн написан только для научного трека и не покрывает INFRA (тот же class отклонения, что в EX-INFRA0-001-R1). Паспорт записывает `INFRA1` (семантически верно, соответствует `project/infra-state.json.frontier`); практический валидатор `scripts/harness/work_cli.py` паттерн checkpoint не проверяет. Схема не менялась (вне allowed_paths).
2. **WO-файл отсутствует.** `docs/work/WO-INFRA1-001.md` не существует в `main` (перечень docs/work проверен). Авторство WO — Director authority; создание WO-файла не входит в allowed_paths. Исполнение ведётся по тексту миссии (bounded: только untrusted hosted route H0; без self-hosted runners, secrets, GPU, paid compute), контрактам `EXECUTION-BASELINE-R1` §4–§8 и задаче `INFRA1-001` из `project/infra-plan.json`.
3. **Repository settings вне Git.** Baseline §5.1 требует repo default `GITHUB_TOKEN` permissions = read-only «фиксируется настройкой репозитория при INFRA1-001». Настройка репозитория GitHub — владелец/admin UI, не git-коммит; в скоуп Implementer'а через git недоступна. Зафиксировано как owner action в HOSTED_CI_R1.md и summary (каждый workflow в этом WO независимо несёт явный `permissions: contents: read`).

Правило границ: только untrusted hosted route; никаких self-hosted runner'ов, secrets, GPU, paid compute; `project/infra-state.json` и `project/state.json` не изменяются (Director gate).
