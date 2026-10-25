# WO-NL5-F05-DISPATCH-PREP-R1 — frozen F2 dispatch readiness (C0 prep, БЕЗ authority A)

**Программа:** `NL5-CLOSE-R1` (#81). **Task issue:** [#86](https://github.com/rootfabric/NanoLab/issues/86) (`F05`, подготовительная C0-часть).
**Статус:** `DISPATCHED` (Director dispatch; launch после F01 handoff).
**Assigned ROLE:** `CONTROL IMPLEMENTER` — реальная отдельная субагентская сессия; далее fresh Reviewer + distinct Verifier; HUMAN protected writer — только для финальной authority A (вне этого WO).
**Dependencies:** F01 handoff (+F03 для полной C0-картины); **финальная authority A = BLOCKED до F04 R2 ACTIVE + отдельного Human launch approval.**

## Baseline

```text
BASE_SHA  = 3b567ae33f247b182b2ae451d2cc4598a9e76019
BRANCH    = work/nl5-f05-dispatch-prep-r1
FROZEN F2 = 60da9a846511265a8ac7564da088c3d74cb073f0 / TREE e565c8a6cee9e829fac14008ebc9c2ea1609931d
```

## Risk / claim / budget

```text
RISK_CLASS = MEDIUM; CLAIM = C0_SOFTWARE_ONLY
SCIENCE    = 0 scientific runs; offline validation + adversarial fail-closed preflight только
BUDGET     = CPU offline (существующие валидаторы scripts/nl5 read-only execution); wall <= 4h
```

## Goal

Подготовить исключительно корректный FROZEN_R2 dispatch lifecycle S→F→D/R/V→A: перепроверить ВСЕ freeze-предпосылки офлайн и задокументировать readiness + budget guard — **не создавая** authority A и не запуская науку.

## Required actions

1. Recheck HG-B canonical owner record (`docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json` = APPROVED) — blob SHA1 + canonical SHA256.
2. Exact F2 Git HEAD/TREE + protocol/contract/seed SHA256 (пересчитать самому, не доверять F01).
3. D2 freeze record + independently confirmed Reviewer(F2) PASS + Verifier(F2) VERIFIED — найти exact records и их HEAD.
4. Feasibility: N-grid PASS N=64 (primary 0b/32b; controls 11b/53b N=10) из frozen contract; collision-scan allowlist; **148 frozen seed identities + replacements** (12/12/2/2 pool) — пересчитать count из seed record скриптом-валидатором.
5. Budget guard: run budget 296+56≤352; 560h/platform; CPU-only; storage и pricing оценка — immutable budget ledger (документ).
6. Запустить существующий offline validator (`scripts/nl5/repro_v02_freeze_contract.py` и связанные) — PASS на F2; adversarial fail-closed preflight: неполная authority → должен ОТКЛОНЯТЬ (задокументировать негативные тесты как evidence).
7. Зафиксировать точный список условий до launch gate: F04 R2 ACTIVE + HG-A + отдельный owner scientific launch approval + budget authorization. **НЕ создавать** authority A schema v3 и launch plan execution — только readiness-документ со списком.

## Deliverables

```text
docs/work/executions/EX-NL5-F05-DISPATCH-PREP-R1/evidence/DISPATCH_READINESS_R1.{json,md}
passport.json + events + 1 append в WORK_QUEUE.md
budget ledger (в evidence dir), stop rules, attestations list
```

## Allowed paths

`docs/work/WO-NL5-F05-DISPATCH-PREP-R1.md`; `docs/work/executions/EX-NL5-F05-DISPATCH-PREP-R1/**`; `docs/work/WORK_QUEUE.md` (1 append). Чтение/исполнение (read-only run) `scripts/nl5/*` разрешено; модификация — запрещена.

## Forbidden

Создание authority A; научные запуски (даже dry-run scientific data); изменение F2/seeds/analyzer/criteria; canonical state; `accept risk` bypass; платные ресурсы; force-push/direct main; Task Bus P2. **Human approval на создание плана ≠ permission запускать 296 runs.**

## Review / stop / handoff

Fresh Reviewer + distinct Verifier обязательны (контрактная работа); NO_RUN до полного набора gates + explicit owner launch gate. Handoff → F06/F07 только после F04+authority A+launch approval.
