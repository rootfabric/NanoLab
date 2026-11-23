# WO-NL5-F01-FROZEN-AUDIT-R1 — независимый аудит NL5 FROZEN_R2 и графа задач (C0)

**Программа:** `NL5-CLOSE-R1` ([Issue #81](https://github.com/rootfabric/NanoLab/issues/81)).
**Task issue:** [#82](https://github.com/rootfabric/NanoLab/issues/82) (`F01`).
**Статус:** `DISPATCHED` (Director dispatch 2026-10-25).
**Assigned ROLE:** `IMPLEMENTER-AUDITOR` — реальная отдельная субагентская сессия (read-only control), не Director.

## Baseline (exact)

```text
BASE_BRANCH = work/nl5-f01-frozen-audit-r1 (от main)
BASE_SHA    = 3b567ae33f247b182b2ae451d2cc4598a9e76019
BASE_TREE   = 560dc913a71a237d3c452a5a2e492e213b232911
WORKTREE    = /home/rdpuser/NanoLab/nl5-f01-audit
FROZEN F2   = 60da9a846511265a8ac7564da088c3d74cb073f0
F2_TREE     = e565c8a6cee9e829fac14008ebc9c2ea1609931d
```

Director independently re-confirmed before dispatch: F2 commit is ancestor of `main`; canonical SHA-256 of frozen protocol/contract/seed-record blobs match `docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R2.json` exactly (`2658ee3e…`, `7e647654…`, `8e844bff…`); `HG-B=APPROVED`; `AUTHOR_U1=NOT_ASSIGNED`; `R2=WAITING_HOST/NOT_ACTIVE`; `NL5-002=WAITING_HUMAN` with preserved terminal `MISMATCH/NOT ACCEPTED`; `external_reproductions=0`. Auditor MUST independently recompute all of these and not trust this preamble.

## Risk / claim / budget

```text
RISK_CLASS   = MEDIUM (control documentation only)
CLAIM_CLASS  = C0_SOFTWARE_ONLY
SCIENCE_RUNS = 0 (hard zero; no oxDNA/MD, no physics, no paid compute)
WALL_BUDGET  = ≤ 4 hours single session
IDENTITY     = real DSH subagent session id issued by Director launcher;
               fabricated session/job ids are FORBIDDEN
```

## Goal

Установить точный текущий канон NL5: состояние `NL5`, `HG-B`, `F2`/`F2_TREE`, `D2`, Reviewer(F2), Verifier(F2), старый terminal `NL5-002 MISMATCH`, risk/claim/gates. Сверить состояние `main` с существующими WO/PR/branches и исключить повторную реализацию уже закрытых задач. Составить evidence matrix `READY/BLOCKED/STALE` для F02/F03/F05 и карту зависимостей с true blockers.

## Required actions (no self-accept)

1. Fresh `git fetch origin`; подтвердить, что `origin/main` всё ещё `3b567ae…` или зафиксировать новый HEAD как epoch change.
2. Пересчитать `GIT_BLOB_SHA1` + `CANONICAL_BLOB_SHA256` (checkout bytes) для: frozen protocol `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md`, freeze contract, seed record (пути в `DIRECTOR_FREEZE_R2.json`), на exact F2 commit.
3. Проверить ancestry/authority: F2 и `DIRECTOR_FREEZE_R2` record — предки `main`; `HG_B_OWNER_DECISION_R1 = APPROVED`; FRESH_SCIENTIFIC_REVIEW_R2 + verifier records для F2 присутствуют и не переписаны.
4. Проверить feasibility grid N=64 (primary 0b/32b; controls 11b/53b N=10; 296 primary runs + ≤56 replacements ≤352; ≤560h/platform; CPU-only) — прочитать из frozen contract/seed record, НЕ изобретать значения.
5. Подтвердить freeze gate PASS и `DISPATCH_BLOCKED` (machine_launch_authorized=false) на F2 evidence.
6. Подтвердить текущие `AUTHOR_U1=NOT_ASSIGNED`, `R2=WAITING_HOST/NOT_ACTIVE` (по `docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md` и свежим evidence, не по старым аудитам), `science_runs` с момента freeze = 0.
7. Подтвердить old `NL5-002` terminal MISMATCH сохранён (append-only), `NL5=IN_PROGRESS`, `NL5-001=ACCEPTED`.
8. Проанализировать реальные subagent capabilities среды (реальный launcher = DSH subagent tool, отдельные сессии с durable id) и безопасно профилировать identity/permission ограничения (в т.ч. недоступность issue-comment API) — без имитации сессий.
9. Проверить открытые branches/PR на дублирование уже сделанной работы.

## Deliverables

```text
docs/work/executions/EX-NL5-F01-FROZEN-AUDIT-R1/evidence/NL5_F01_IMMUTABLE_AUDIT_R1.md
docs/work/executions/EX-NL5-F01-FROZEN-AUDIT_R1.json  (зеркало json: см. фактический путь ниже)
docs/work/executions/EX-NL5-F01-FROZEN-AUDIT-R1/evidence/NL5_F01_IMMUTABLE_AUDIT_R1.json
passport.json + events 0001 START / 000N CONTINUATION / final HANDOFF_COMPLETED
```

Json содержит: hashes + команды их получения, evidence matrix `READY/BLOCKED/STALE` по F02/F03/F05, карту зависимостей с true blockers, список разрешённых C0 запусков и отдельный launch-gate. Все выводы прежних Reviewer/Verifier не переписывать.

## Allowed paths

```text
docs/work/WO-NL5-F01-FROZEN-AUDIT-R1.md            (только статусы/append-only пометки)
docs/work/executions/EX-NL5-F01-FROZEN-AUDIT-R1/**
docs/work/WORK_QUEUE.md                             (одна append-only запись)
```

## Forbidden

`project/state.json`, `project/plan.json`, `project/infra-state.json`, `project/infra-plan.json`, `docs/evidence/NL5-V02-FREEZE/**` (read-only), `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` (read-only), frozen seed/contract, `scripts/**`, `tests/**`, любые scientific runs, U1/U2 изменения, платные ресурсы, force-push, direct main push, самостоятельный PASS/ACCEPT, запуск production Git Task Bus P2.

## Validation

```bash
PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-F01-FROZEN-AUDIT-R1
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
python3 -m json.tool <каждый новый json>  # strict parse
```

Review: новый код/контракты не добавляются → по Issue #82 достаточно документальной передачи Director без научной приёмки; любые вскрытые противоречия → `BLOCKED`/`FIX_REQUIRED` с Repair Map.

## Stop conditions

FROZEN_R2 hash mismatch; F2 не ancestor main; HG-B/Reviewer/Verifier records повреждены; попытка записи в forbidden path; недоступность данных для вердикта → честный `INCONCLUSIVE`/`BLOCKED` в evidence. Никогда: `READY` для F06/F07 из этого WO — science launch gates не в юрисдикции F01.

## Handoff / next actor

HANDOFF_COMPLETED на branch → Director integration → разрешено начало C0 F02/F03 и подготовительной части F05 (Issue #83/#84/#86) отдельными сессиями.
