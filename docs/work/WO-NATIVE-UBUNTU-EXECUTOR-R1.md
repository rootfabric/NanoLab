# Work Order WO-NATIVE-UBUNTU-EXECUTOR-R1 — Native Ubuntu author/executor environment R2

Статус: **IN_PROGRESS** (execution `EX-NATIVE-UBUNTU-EXECUTOR-R1`, ветка
`control/native-ubuntu-executor-r1`, base `d07e75e68c20599e4b942aefb20b4b3922985219`).
Track: `INFRA` (встроен в существующее направление INFRA2 → INFRA3, без второго
параллельного инфраструктурного дизайна). Risk: **MEDIUM**. Claim ceiling:
**C0_SOFTWARE_ONLY**. Это **не научный эксперимент**: научных прогонов в этом WO нет;
первый научный WO на среде R2 остаётся отдельно preregistered HIGH.

Дата открытия: 2026-09-27. Trigger: системный отказ execution path кампании
NL5-002-E P1 (CI-цикл → `wsl --shutdown` → убийство physics-процессов → retry-шторм
до `-R21`, см. `RECOVERY_INCIDENTS.md`) и owner decree от 2026-09-27: после закрытия
`P1_RAW_REPLAY` новые scientific physics на Windows/WSL2 не запускаются.

## 1. Цель

Создать native Ubuntu author/development/scientific environment **R2**
(`U1 = AUTHOR_UBUNTU`) и вывести Windows/WSL2 из mandatory execution path:

```text
GitHub
   │
   ├── Native Ubuntu U1 — AUTHOR / DEV / PRIMARY EXECUTOR
   │      agents · Git checkout · harness · oxDNA build
   │      scientific runs · raw evidence
   │
   └── External Ubuntu U2 — EXTERNAL REPRO / VERIFY (outenemy)

Windows: optional UI / emergency historical evidence only
         NOT scientific executor · NOT required CI host
         NOT canonical raw-data host
```

## 2. Неизменяемые границы

- `docs/research/ENGINE_ENVIRONMENT_R1.md` (WSL2 Ubuntu 24.04.2, i9-13900H,
  gcc 13.3) — **исторический факт provenance, НЕ изменяется и не заменяется**.
- `NL5-002-E` научный результат (PLATFORM_INSENSITIVE, frozen R1) не пересчитывается
  и не переносится как oracle на R2. `PLATFORM_INSENSITIVE` — свойство конкретного
  frozen R1 исследования, а не требование побайтного совпадения платформ.
- Границы frontier не меняются этим WO: `NL5 = IN_PROGRESS`,
  `NL6-001 = LOCKED`, `external_reproductions = 0`; `NL5-ACCEPTANCE-POLICY`
  решается отдельно.
- Научная история и инфраструктурная миграция — два независимых integration
  stream; смешение в один commit/PR запрещено.

## 3. Требования к R2-машине (U1)

- **Native Linux**: native kernel, native ext4/xfs/btrfs, native process lifecycle,
  native systemd. ЗАПРЕЩЕНО как R2: WSL, Docker Desktop VM, VirtualBox VM,
  Windows bind mount `/mnt/c`.
- Версия Ubuntu фиксируется **по факту** fingerprint, не назначается заранее.
- Научные процессы живут вне agent session (`systemd-run --scope` / transient
  unit) и переживают SSH disconnect, agent crash, terminal close, CI restart.
- CI runner (`github-actions-runner.service`) и scientific job manager
  (`nanolab-executor.service` или scoped unit per campaign) — раздельные units;
  CI запрещены `systemctl reboot|shutdown`, kill executor cgroup.

## 4. Canonical paths и software policy

```text
~/src/NanoLab                          # Git checkout (author/dev)
~/nanolab/workspaces/<execution-id>/   # physics workspaces (вне Git repo)
~/nanolab/raw/<execution-id>/          # raw artifacts: manifest + sha256 + size
                                       # + producer + retention policy
~/nanolab/cache/                       # builds/downloads cache
~/nanolab/tools/                       # локальные инструменты (cmake и т.п.)
```

- Git: `core.autocrlf false`, `core.safecrlf true`; научные входы — через pinned
  blob/object/digest contract. CRLF-workaround больше не часть normal execution path.
- Python: pinned `.venv` (или repo-approved equivalent) с фиксацией exact версии,
  dependency lock, pip/uv версии, package hashes where applicable. Системный Python
  не является mutable environment по умолчанию.
- Toolchain: gcc/g++/cmake/make фиксируются **по факту** без автоматического
  `apt upgrade`. Другая GCC line относительно R1 допустима: это
  ENGINE_ENVIRONMENT_R2, а не имитация R1.
- Engine: fresh oxDNA build от pinned `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`
  (если отдельный future WO не меняет engine version): CPU, DOUBLE=ON, CUDA=OFF,
  MPI=OFF. Фиксируются: source SHA, compiler, cmake command, CMakeCache relevant
  pins, binary size, binary sha256, build log.
- **Migration gate** = same source commit + same intended build flags + clean build
  + expected engine smoke + frame0 oracle + protocol fixtures. НЕ `binary SHA ==
  WSL binary`.

## 5. Raw evidence policy

- Raw artifacts локально на Ubuntu: `~/nanolab/raw/<execution-id>/` (или отдельный
  volume); каждый execution имеет manifest (sha256, size, producer, retention).
- Git хранит только compact evidence.
- Backups: после завершения run — `raw local + digest + optional secondary storage
  copy`; не копировать mutable trajectory во время расчёта без необходимости.

## 6. Валидационные gates (до объявления R2 canonical)

Выполняются на фактически выделенной U1 и публикуются append-only:

```text
U1  engine build (CPU/DOUBLE=ON/CUDA=OFF/MPI=OFF, clean)        PASS | WAITING_HOST
U2  package verify (nanolab-components, известные documented
    v0.1.1 pyc findings допустимы; либо bounded v0.1.2 repair)  PASS | WAITING_HOST
U3  frame0 oracle: 0b exact; 11b exact; 32b exact; 53b exact;
    74b NOT_MEASURED (если gap не ремонтировался)               PASS | WAITING_HOST
U4  short technical oxDNA smoke: exit=0, finite outputs,
    expected frames/files (НЕ scientific claim)                 PASS | WAITING_HOST
U5  harness: unit tests, check-consistency, workflow lint,
    work_cli validation                                         PASS | WAITING_HOST
NC-U1  SSH/session close → scientific test job продолжает работать    WAITING_HOST
NC-U2  agent process restart → job продолжает работать                WAITING_HOST
NC-U3  GitHub runner service restart → job продолжает работать        WAITING_HOST
NC-U4  CI workspace cleanup → raw workspace вне его и не удаляется    WAITING_HOST
NC-U5  deliberate kill scientific process → supervisor фиксирует
       FAILED_TECHNICAL и не переиспользует run ID                    WAITING_HOST
```

Статусы в этой R1 — честные: машина U1 не выделена, все gates = `WAITING_HOST`.
Никакой gate не помечается PASS без фактического исполнения.

## 7. Execution policy (fixируется документом NATIVE_UBUNTU_EXECUTION_POLICY_R1)

```text
WINDOWS_WSL_EXECUTOR        = HISTORICAL_ONLY        # effective с 2026-09-27 (owner decree)
WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO                 # исключение: explicit bounded
                                                     # environment comparison WO
DEFAULT_AUTHOR_EXECUTOR     = NATIVE_UBUNTU_R2       # PROPOSED → ACTIVE только после
                                                     # всех gates §6 + review/verify
```

## 8. Scope

Разрешено (allowed_paths паспорта): WO-документ, execution-каталог
`EX-NATIVE-UBUNTU-EXECUTOR-R1/**`, `docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md`,
`docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md`, поверхностные обновления
`AGENTS.md`, `docs/work/AGENT_START.md`,
`docs/control/HARNESS_AUTONOMOUS_EXECUTION_RU.md`,
`config/control/harness/scheduler-policy.v1.json`, `docs/ROADMAP.md`,
`docs/work/WORK_QUEUE.md`, `docs/infra/ROADMAP.md`, `project/infra-plan.json`.

Не разрешено: регистрация self-hosted runner (отдельный INFRA2-001), secrets,
платные сервисы, scientific runs, изменения `project/state.json` /
`project/infra-state.json` (Director gate), изменения scientific history и
существующих execution-каталогов, изменения `ENGINE_ENVIRONMENT_R1.md`.

## 9. Required outputs

1. `docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` (контракт + статус
   WAITING_HOST + процедура заморозки fingerprint по факту).
2. `docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md` (execution policy §7).
3. Поверхностные обновления (§8) с conditional-формулировками.
4. INFRA3-увязка в `docs/infra/ROADMAP.md` и `project/infra-plan.json`
   (задача среды R2 внутри существующего checkpoint INFRA3).
5. Events + summary + handoff с exact HEAD/TREE и NEXT_ACTION = выделение U1.

## 10. Acceptance (этого WO) и acceptance (миграции)

- Acceptance этого WO: документы опубликованы, policy зафиксирована, honest
  статусы, fresh Reviewer + fresh Verifier на exact HEAD, затем Human Gate merge.
- Acceptance МИГРАЦИИ (отдельная точка, требует машину U1): все gates §6 PASS +
  process-survival + raw evidence manifest test + «CI cannot kill scientific
  executor» + review/verify. Только после этого `DEFAULT_AUTHOR_EXECUTOR =
  NATIVE_UBUNTU_R2` становится ACTIVE, а `WINDOWS_WSL_EXECUTOR` теряет любые
  научные функции кроме historical evidence.
