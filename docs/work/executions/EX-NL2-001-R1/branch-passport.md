# Branch Passport

- Branch: `work/nl2-001-contracts-e0-r1`
- Work Order: NL2-001 (Реализовать схемы, manifest и E0)
- Checkpoint: NL2
- Base SHA: `15a2c9b1b5c095e24e2e1c24afd77feef5361102`
- Created from canonical main: 2026-09-09T12:47Z (worktree C:\NanoLab\nl2-001; fetch показал origin/main = `a4533ab` — epoch drift PR #27, решение CONTINUE, см. WO §Epoch drift)
- Risk class: MEDIUM
- Claim class: C0_SOFTWARE_ONLY
- Allowed paths: docs/work/WO-NL2-001.md; docs/work/executions/EX-NL2-001-R1/**; docs/research/PREREGISTRATION_E0_R1.md; docs/experiments/E0_PIPELINE_VALIDATION.md; experiments/evidence/E0/E0-R1/**; docs/evidence/NL2-001/**; docs/work/SESSION_LOG.md
- Current HEAD: `15a2c9b1b5c095e24e2e1c24afd77feef5361102` (на момент создания паспорта)
- Status: IN_PROGRESS
- Active experiment campaigns: E0-R1 (пререгистрация → прогоны; campaign-level scientific_outcome = NOT_EVALUATED)
- Last durable event: 0001-work-order-started (создаётся этим START-коммитом)
- Next action: freeze-коммит кампании E0-R1 (пререгистрация + protocol.json + fixtures + tools), затем campaign-START commit (manifests + started-events), затем прогоны
- Blocking issue: нет

## Documented deviations (post-review repair, F6 @ `2c3b485`)

- `allowed_paths` паспорта дополнены (post-hoc): `docs/research/PREREGISTRATION_E0_R2/R3/R4.md` (superseding-пререгистрации, требовались §0.1 E0-PROTO-R1) и `experiments/evidence/E0/E0-R2|R3|R4/**` (evidence попыток-повторов по §8). Процедурное отклонение признано и задокументировано: docs/evidence/NL2-001/ERRATUM_F2_F5_R1.md (F6) + events/0001-repair-f1-f7.json.
