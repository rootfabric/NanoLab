# WO-NL5-F03-U2-READINESS-R1 — U2 external reproducibility + raw manifests (C0)

**Программа:** `NL5-CLOSE-R1` (#81). **Task issue:** [#84](https://github.com/rootfabric/NanoLab/issues/84) (`F03`).
**Статус:** `DISPATCHED` (Director dispatch; launch после F01 handoff; параллельно с F02).
**Assigned ROLE:** `EXTERNAL-PREFLIGHT IMPLEMENTER (U2)` — реальная отдельная субагентская сессия, НЕ author U1-сессия.
**Dependencies:** F01 handoff; существующие U2 receipts (PR #55 chain, `docs/evidence/INFRA3-U2-READINESS/`).

## Baseline

```text
BASE_SHA  = 3b567ae33f247b182b2ae451d2cc4598a9e76019
BRANCH    = work/nl5-f03-u2-readiness-r1
FROZEN F2 = 60da9a846511265a8ac7564da088c3d74cb073f0 (read-only reference)
```

## Risk / claim / budget

```text
RISK_CLASS = MEDIUM; CLAIM = C0_SOFTWARE_ONLY; SCIENCE_RUNS = 0
BUDGET     = offline Git/evidence analysis + software/synthetic dry-run checks; wall <= 3h
```

## Goal

Проверить готовность внешнего исполнителя U2 (outenemy) к приёму frozen release package: независимость от U1, exact pins release-package, права, дисковые лимиты, raw artifact ingress/egress, воспроизводимый сценарий БЕЗ научных вычислений.

## Required actions

1. Прочитать существующие U2 receipts/evidence (`docs/evidence/INFRA3-U2-READINESS/FRESH_REVIEW_U2_READINESS_R1.*`, PR #55 chain, `infra/u2-outenemy-executor-readiness-r1` branch) и зафиксировать их актуальность (STALE check по датам/HEAD).
2. Из этой сессии нет SSH-доступа к outenemy — live-проверки host identity/fingerprint НЕВОЗМОЖНЫ: честно зафиксировать `BLOCKED_NO_U2_ACCESS_FROM_SESSION` для live-части. Ничего не имитировать.
3. C0-часть (выполнима offline): проверить состав frozen release package (F2) для доставки на U2 — manifest inputs/digests; проверить шаблон raw-manifest (hash+size+producer+HEAD+storage+retention); схему unique job IDs; safe path/permissions требования; изоляцию от author-результатов (нет доступа к промежуточным U1 данным).
4. Составить `U2_READINESS_R1.json/md`: platform independence matrix, inventory storage/evidence capacity (по evidence), budgets, точный список live-проверок, которые владелец/оператор U2 должен выполнить, вердикт `BLOCKED_*` или `READY_FOR_DISPATCH_PREP` с явными ограничениями.

## Deliverables

`docs/work/executions/EX-NL5-F03-U2-READINESS-R1/evidence/U2_READINESS_R1.{json,md}` + passport + events + 1 append в WORK_QUEUE.md.

## Allowed paths

`docs/work/WO-NL5-F03-U2-READINESS-R1.md`; `docs/work/executions/EX-NL5-F03-U2-READINESS-R1/**`; `docs/work/WORK_QUEUE.md` (1 append).

## Forbidden

oxDNA/scientific runs; новые классификации данных; изменение frozen package; canonical state; scripts/tests (модификация); U1-подмена; секреты; force-push/direct main; Task Bus P2. **U2-ready ≠ R2_ACTIVE ≠ scientific authorization.**

## Review / stop / handoff

Fresh Reviewer + distinct Verifier при добавлении контрактов; STOP при имитации U2-доступа. Handoff → F05 authority planning; live U2 checks → перед F07 при общих разрешениях.
