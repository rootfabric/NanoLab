# Branch Passport — EX-INFRA0-001-R1

- Branch: `infra/infra0-execution-baseline-r1`
- Work Order: `INFRA0-001` (docs/work/WO-INFRA0-001.md, существует в main с INFRA roadmap bd5f0d2)
- Checkpoint: `INFRA0` (см. примечание о схеме ниже)
- Base SHA: `57c1e63733ea3b10f991c0f9609c426dc75b17a5` (exact canonical main, verified live: `origin/main` = HEAD до старта)
- Created from canonical main: yes
- Risk class: `MEDIUM` (repository_automation / security control policy; no scientific claim → Implementer + Reviewer + Verifier по risk-policy)
- Claim class: `C0_SOFTWARE_ONLY`
- Allowed paths: see `passport.json` (`docs/infra/EXECUTION_BASELINE_R1.md`, `config/infra/execution-baseline.v1.json`, `docs/work/executions/EX-INFRA0-001-R1/**`)
- Status: `HANDOFF_READY`
- Active experiment campaigns: none (документальный Work Order; E0–E6 остаются `NOT_RUN`)
- START commit: `ff68c12e6a8b5a2e09d32796f462f5ee6ba885e6` (pushed до substantive work)
- Implementation commit: `870f52e309a85da1dd5fb95c0d67498f2f573898` (tree `aba753e218eba949270957dbcc9628060a53f6a3`)
- Last durable event: `0004-handoff-completed`
- Next action: независимый REVIEWER, затем VERIFIER (MEDIUM routing); затем Director checkpoint proposal; merge — Human Gate; обновление `project/infra-state.json` — только Director gate
- Blocking issue: none

## Документированные отклонения (для reviewer)

1. **Checkpoint `INFRA0` vs schema pattern.** `config/control/harness/execution-passport.schema.v1.json` задаёт `checkpoint: ^NL[0-8]$` — паттерн написан только для научного трека и не покрывает INFRA. Паспорт записывает `INFRA0` (семантически верно, соответствует `project/infra-state.json.frontier`); практический валидатор `scripts/harness/work_cli.py` паттерн checkpoint не проверяет. Схема не менялась (вне allowed_paths); расширение паттерна на INFRA-трек — кандидат в будущий control WO.
2. **Размещение machine-readable конфига.** WO scope разрешает `config/control/infra/**`, миссия владельца явно требует `config/infra/execution-baseline.v1.json` — использован путь миссии как более общий namespace для infra-конфигов; файл единственный, дублирования нет.
3. **Negative test как документ.** Required output WO «negative test: untrusted PR route не может выбрать self-hosted scientific label» зафиксирован как negative control `NC-1` с mechanical_validation = `INFRA1-002` (задача «Add PR validation gates» в infra-plan). Механических тестов в этом документальном WO нет — workflows не создавались.

Правило границ: ни один runner, workflow, secret, artifact store в рамках этого WO не создавались; `project/infra-state.json` и `project/state.json` не изменялись.
