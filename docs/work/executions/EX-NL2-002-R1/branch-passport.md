# Branch Passport

- Branch: `work/nl2-002-validate-e1-r1`
- Work Order: NL2-002 (Validate statistics and E1 — T2 confirmatory кампания)
- Checkpoint: NL2
- Base SHA: `0176098ed052ec29503ac5c353463be0cc8ea167`
- Created from canonical main: 2026-09-10T11:17Z (worktree C:\NanoLab\nl2-002; fetch: origin/main = base — epoch drift отсутствует)
- Risk class: HIGH
- Claim class: C1_COMPUTATIONAL_REPRODUCTION_CEILING (campaign-level scientific_outcome = NOT_EVALUATED; объявление статуса E1 — Director)
- Allowed paths: docs/work/WO-NL2-002.md; docs/work/executions/EX-NL2-002-R1/**; experiments/evidence/E1/E1-R2/**; docs/evidence/NL2-002/**; docs/work/SESSION_LOG.md (append)
- Current HEAD: `0176098ed052ec29503ac5c353463be0cc8ea167` (на момент создания паспорта)
- Status: IN_PROGRESS
- Active experiment campaigns: E1-R2 (T2 confirm: 3 реплики C001–C003, distinct seeds, frozen R_confirm = 3; campaign-level scientific_outcome = NOT_EVALUATED)
- Frozen protocol: E1-PROTO-R1 (§3 условия, §5.1 observable/критерий, §9 семантика, §10 stop) + E1-PROTO-R2 (§2 freeze R_confirm = 3, §3 правило confirmatory кампании) — БЕЗ изменений
- Environment: reuse зафиксированной сборки E1-R1 (бинарь ffc80b1a7abe2a06bea601ac7f730e26c0e5c09c33a9e8c7c5f7a96a4848579f, 3375976 B) с верификацией SHA-256/флагов; fallback — пересборка ENGINE_ENVIRONMENT_R1 §3
- Last durable event: 0001-work-order-started (создаётся этим START-коммитом)
- Next action: freeze-коммит кампании E1-R2 (campaign.md + protocol.json + analyze_energy.sh), затем campaign-START commit (manifests + started-events C001–C003), затем прогоны
- Blocking issue: нет
