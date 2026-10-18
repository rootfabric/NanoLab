# INFRA3_NL5_READINESS_REPORT_R1 — Компактный отчёт готовности: U1 + frozen NL5 v0.2 кампания

Дата: 2026-10-18. WO: `WO-INFRA3-NL5-READINESS-R1` (issue #65, программа #63).
Execution: `EX-INFRA3-NL5-READINESS-R1`, ветка `infra/infra3-nl5-readiness-r1`,
base `513c4fa86470d939e9f9b7829e9c67c489c15a57`. Claim ceiling:
**C0_SOFTWARE_ONLY**. DRY-RUN ONLY: 0 scientific runs за весь этот WO.

## 1. Декларация HOST_NOT_ASSIGNED

```text
AUTHOR_U1            = NOT_ASSIGNED   (отдельная физическая Ubuntu-машина U1
                                       НЕ ВЫДЕЛЕНА; каноническое evidence:
                                       docs/work/executions/EX-NL5-V02-FRESH-AUDIT-R1/
                                       evidence/u1-host-search-R1.json)
R2_STATUS            = WAITING_HOST / NOT_ACTIVE
R2_ACTIVATED         = NO
NEW_SCIENCE          = HARD_BLOCKED (silent fallback на Windows запрещён)
OUTENEMY_ROLE        = EXTERNAL_U2_ONLY (никогда author executor)
EXPECTED_OUTCOME_CLASS = READY_FOR_HOST (пакет готовности полон; железа нет)
```

## 2. Состояние готовности по gates (честное, без PASS)

| Gate | Суть | Проверка (команда/артефакт) | Статус |
|---|---|---|---|
| U1 | engine build (pin `00dc7fb9…`, CPU/Release/DOUBLE=ON/CUDA=OFF/MPI=OFF, provenance) | `r2.cli build-engine` + provenance record | **HOST_NOT_ASSIGNED** |
| U2 | package verify (nanolab-components; v0.1.2 repair из PR #56) | `reproduce.py verify` на fresh export | **HOST_NOT_ASSIGNED** |
| U3 | frame0 oracle: 0b/11b/32b/53b exact; 74b NOT_MEASURED | `r2.cli gate --gate U3` + fixtures | **HOST_NOT_ASSIGNED** |
| U4 | технический oxDNA smoke (exit=0, finite outputs) — НЕ scientific claim | runbook smoke step | **HOST_NOT_ASSIGNED** |
| U5 | harness: unittest + check-consistency + workflow lint + work_cli | 4 команды на U1 | **HOST_NOT_ASSIGNED** |
| NC-U1 | SSH/session close → job живёт | `r2.cli nc-plan/nc-verify NC-U1` | **HOST_NOT_ASSIGNED** |
| NC-U2 | agent restart → job живёт | `nc-plan/nc-verify NC-U2` | **HOST_NOT_ASSIGNED** |
| NC-U3 | GitHub runner restart → job живёт | `nc-plan/nc-verify NC-U3` | **HOST_NOT_ASSIGNED** |
| NC-U4 | CI cleanup → raw workspace не тронут | `nc-plan/nc-verify NC-U4` | **HOST_NOT_ASSIGNED** |
| NC-U5 | deliberate kill → FAILED_TECHNICAL, id не переиспользуется | `nc-plan/nc-verify NC-U5` | **HOST_NOT_ASSIGNED** |

Machine-checkable определения gates — `docs/infra/NL5_V02_DRYRUN_MANIFEST_R1.json`
(поля `gates` / `negative_controls`); требования к хосту —
`docs/infra/U1_PROVISIONING_CHECKLIST_R1.md`.

## 3. Frozen-кампания NL5 v0.2 — что подтверждено из канонических источников

Числа сверены с frozen-протоколом на этом base (не взяты из mission-текста):

```text
протокол      docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md
              sha256 2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d
              F2 = 60da9a846511265a8ac7564da088c3d74cb073f0
              tree e565c8a6cee9e829fac14008ebc9c2ea1609931d
контракт      .../EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/
              repro-v0-2-freeze-contract-FROZEN_R2.json (sha256 7e647654…)
seed record   .../repro-v0-2-seed-record-FROZEN_R2.json (sha256 8e844bff…)
варианты      0b=64, 32b=64 (primary); 11b=10, 53b=10 (controls); 74b запрещён
подтвердительные расчёты = 296 = 2·(64+64+10+10)   (обе ноги U1+U2)
replacement cap = 56 runs;  MAX = 352;  wall ≤ 560 ч/платформу
N_min пары    primary 52, control 8; δ=0.5; B=10000; SELECTED_N=64 (grid 0.80)
```

Dispatch кампании: **BLOCKED** — chain S→F→D есть, но R (fresh Reviewer(F)),
V (fresh Verifier(F)), A (dispatch authority v3), R2 ACTIVE и Human launch
gate отсутствуют; `machine_launch_authorized = false`.

## 4. Reconciliation merged vs review-verified (git history, base 513c4fa)

Всё, что ниже — **merged в canonical main** (проверено `git log`/`git show` +
`git merge-base --is-ancestor` на этом base):

| PR | Merge | Что канонически на main |
|---|---|---|
| #45/#46 | `3e220f6` / `8205781` | Executor policy: `NATIVE_UBUNTU_EXECUTION_POLICY_R1.md`, `ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md`, `WO-NATIVE-UBUNTU-EXECUTOR-R1.md` |
| #47 | `87298b3` | R2 activation tooling: `scripts/r2/*`, `config/infra/r2-activation.v1.json`, `tests/test_r2_activation_tooling.py`, `WO-INFRA3-R2-ACTIVATION-R1.md` (+ execution с repair R1) |
| #52 | `8bf7e3a` | Frozen NL5 v0.2 FROZEN_R2 пакет (protocol + contract + seed record + Director FREEZE R2) |
| #53 | `4c77290` | Fresh audit + U1 blocker evidence (`u1-host-search-R1.json`: AUTHOR_U1 = NOT_ASSIGNED) |
| #55 | `0665558` | U2 readiness (`U2_OUTENEMY_EXECUTOR_READINESS_R1.md`), tooling repairs F-1..F-4, `run-u2` path; fresh review PASS `d588e2a` интегрирован (`8afe8ae`) |
| #56 | `32d3c68` | nanolab-components v0.1.2 packaging repair |
| #54/#57 | `37c22ad` / `513c4fa` | docs roadmap + PREP-S17 (base этой ветки) |

**Canonical на main (сводно):** frozen F2 пакет + activation tooling + U2-плечо
готово технически + AUTHOR_U1 = NOT_ASSIGNED. **Никакой «review-verified, но не
merged» infra-факт не остался вне main**: все infra-ветки линии
(`integration/infra3-native-ubuntu-r2-activation-r1`,
`infra/infra3-native-ubuntu-r2-activation-r1`,
`infra/u2-outenemy-executor-readiness-r1`, `control/native-ubuntu-executor-r1`,
`integration/native-ubuntu-executor-r1`) — предки `main` на этом base.
Чего НЕТ нигде (и что не выдается за факт): U1, PASS любого gate, R2 ACTIVE,
Reviewer(F)/Verifier(F)/authority(A), научные запуски v0.2 (SCIENTIFIC_RUNS = 0).

## 5. Точные человеческие действия для активации U1

Полный проверяемый чек-лист: `docs/infra/U1_PROVISIONING_CHECKLIST_R1.md` §11.
Минимальный след владельца:

1. **A1** Выделить/приобрести отдельную физическую машину (≥16 ядер CPU,
   ≥32 GiB RAM, ≥100 GiB нативного диска) — НИКОГДА outenemy, НИКАКИХ VM/LXD
   на outenemy (это разрушило бы независимость author/external).
2. **A2** Установить native Ubuntu LTS; создать пользователя исполнителя;
   настроить `~/src/NanoLab` + `~/nanolab/{workspaces,raw,cache,tools}`.
3. **A3** Обеспечить SSH-доступ по ключу (password auth off) и передать
   host alias исполнителю.
4. **A4** Зафиксировать allocation record (hostname/machine-id/serial + роль
   AUTHOR_UBUNTU + физическая отдельность от U2).
5. **A5** На выделенной U1 исполнить механический runbook
   (`DIRECTOR_FRESH_AUDIT_R1.md` §6): fingerprint → `build-engine` → gates
   U1–U5 → NC-U1..U5 → `activation-check` — отдельными bounded WO.
6. **A6** Дальнейшая цепочка по политике: fresh review + fresh verify →
   HG-A (Human Gate) → R2 ACTIVE → dispatch authority v3 →
   HUMAN_PROTECTED_WRITER launch decision → только тогда legs
   `EX-NL5-REPRO-V0-2-U1-R1` / `EX-NL5-REPRO-V0-2-U2-R1`.

## 6. Что остаётся ЗАПРЕЩЁННЫМ до Human Gate / выделения U1

- Любые scientific runs (включая первый confirmatory расчёт v0.2); запуск
  oxDNA на любом хосте; научное исполнение gates/NC.
- Новые scientific runs на Windows/WSL2 (owner decree 2026-09-27); тихий
  fallback на Windows вместо ожидания U1.
- Использование outenemy как author/dev-хоста или «U1-заменителя»
  (EXTERNAL_U2_ONLY).
- Регистрация self-hosted runners, secrets, платный compute.
- Изменение frozen NL5 v0.2 acceptance criteria / protocol files (только
  новая ревизия v0.3+ через новый WO и новый freeze).
- Изменение `project/state.json`, `project/infra-state.json`, `project/plan.json`,
  статусов `NL5`/`NL6-001` этим пакетом (INFRA не двигает научные границы).
- Прямой push в `main`; merge = Human Gate.

## 7. Валидация этого пакета (факты на момент handoff)

См. `docs/work/executions/EX-INFRA3-NL5-READINESS-R1/summary.md` — exact
HEAD/TREE и полные выводы: unittest discover (включая
`tests/test_infra3_nl5_readiness.py`), `check-consistency`, `workflow_lint`,
`work_cli validate EX-INFRA3-NL5-READINESS-R1`.
