# WO-NL5-F02-U1-HOST-R1 — U1 native Ubuntu: выделение, fingerprint, host security (C0)

**Программа:** `NL5-CLOSE-R1` (#81). **Task issue:** [#83](https://github.com/rootfabric/NanoLab/issues/83) (`F02`).
**Статус:** `DISPATCHED` (Director dispatch; launch после F01 handoff).
**Assigned ROLE:** `HOST-PROVISIONING / INFRA implementer` — реальная отдельная субагентская сессия.
**Dependencies:** F01 (EX-NL5-F01-FROZEN-AUDIT-R1 handoff) + **owner-provided host/SSH** (WO #65 chain).

## Baseline

```text
BASE_SHA  = 3b567ae33f247b182b2ae451d2cc4598a9e76019
BRANCH    = work/nl5-f02-u1-host-r1
FROZEN F2 = 60da9a846511265a8ac7564da088c3d74cb073f0 (read-only reference)
```

## Risk / claim / budget

```text
RISK_CLASS = MEDIUM (control documentation; host fingerprint only)
CLAIM      = C0_SOFTWARE_ONLY; SCIENCE_RUNS = 0 (жёстко)
BUDGET     = offline read-only host inspection; wall <= 3h; no apt upgrade, no global installs
```

## Goal

Обеспечить документированную готовность физически отдельной от U2 (outenemy) native Ubuntu author-машины U1 по `ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU` / `NATIVE_UBUNTU_EXECUTION_POLICY_R1` — БЕЗ выдачи VM/WSL2/outenemy за U1.

## Hard gate (из Issue #83)

Если владелец не выделил хост/SSH-доступ на момент исполнения — опубликовать `BLOCKED_OWNER_U1` с точным списком того, что должно предоставить владелец. Ничего не имитировать. Текущий канон: `AUTHOR_U1=NOT_ASSIGNED`.

## Required actions

1. Проверить наличие owner allocation: SSH-алиасы (`~/.ssh/config`), env, документы Git (после freeze — нет новых). Если нет → `BLOCKED_OWNER_U1` (это честный ожидаемый исход) + собрать остальную C0-часть.
2. C0-часть: для локального кандидата (текущий host) собрать read-only fingerprint: hostname/OS (`/etc/os-release`)/kernel (`uname -a`)/native FS/systemd/CPU/RAM/топология/drive — ЗАПРЕЩАЮЩИЕ команды (apt, установки, модификации) запрещены.
3. Пометить fingerprint как `CANDIDATE_NOT_ALLOCATED` — не объявлять U1 назначенным.
4. Составить eligibility checklist по policy §gates (U1-U5 предварительный), deny-list (U2=outenemy ≠ U1), изоляция scientific executor от CI, пути raw (`~/nanolab/workspaces/raw`), credential scope БЕЗ секретов в Git/логах.
5. Evidence matrix: что блокирует R2 activation (→F04) и что должен решить владелец (HG-A).

## Deliverables

```text
docs/work/executions/EX-NL5-F02-U1-HOST-R1/evidence/U1_HOST_ELIGIBILITY_R1.json (+ .md)
passport.json + events (START/CONTINUATION/HANDOFF) по схеме харнесса
docs/work/WORK_QUEUE.md — одна append-only запись
```

## Allowed paths

`docs/work/WO-NL5-F02-U1-HOST-R1.md`; `docs/work/executions/EX-NL5-F02-U1-HOST-R1/**`; `docs/work/WORK_QUEUE.md` (1 append).

## Forbidden

Изменения канонических state-файлов; frozen package; scripts/tests; научные запуски; apt/глобальные установки; секреты в Git; impersonation U1; force-push/direct main; production Task Bus P2. Fingerprint/SSH сами по себе НЕ означают R2 ACTIVE.

## Review / stop

Fresh INFRA Reviewer + distinct Verifier на exact evidence при добавлении контрактов; Director принимает документальную передачу. STOP при любом требовании записи вне allowed paths или попытке «назначить» хост без owner allocation.

## Handoff

`BLOCKED_OWNER_U1` → owner action (выделение U1) → только тогда F04. Никакой auto-активации.
