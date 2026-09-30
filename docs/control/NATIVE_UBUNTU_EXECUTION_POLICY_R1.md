# NATIVE_UBUNTU_EXECUTION_POLICY_R1 — Executor policy после R1-линии

Статус: **PARTIALLY_EFFECTIVE** (см. §1). Execution: `EX-NATIVE-UBUNTU-EXECUTOR-R1`.
Work Order: `WO-NATIVE-UBUNTU-EXECUTOR-R1`. Дата: 2026-09-27.

## 1. Статус политик

```text
WINDOWS_WSL_EXECUTOR            = HISTORICAL_ONLY   [EFFECTIVE 2026-09-27]
WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO                [EFFECTIVE 2026-09-27]
DEFAULT_AUTHOR_EXECUTOR         = NATIVE_UBUNTU_R2  [PROPOSED → ACTIVE после gates]
```

Канонический статус на момент integration rebuild (2026-09-30, ветка
`integration/native-ubuntu-executor-r1` от science-integrated main `3e220f6`;
append-only уточнение, не переписывает решение 2026-09-27):

```text
NATIVE_UBUNTU_POLICY            = MERGED            [этот integration branch; канонично на main после Human Gate миграции]
AUTHOR_U1                       = NOT_ASSIGNED
R2_STATUS                       = WAITING_HOST / NOT_ACTIVE
R2_ACTIVATED                    = NO
NEW_SCIENCE                     = HARD_BLOCKED (без R2; silent fallback на Windows = FORBIDDEN)
OUTENEMY_ROLE                   = EXTERNAL_U2_ONLY  [не author/dev host]
```

- `WINDOWS_WSL_EXECUTOR = HISTORICAL_ONLY` и `WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO`
  — **effective немедленно** по owner decree (mission 2026-09-27): после закрытия
  `P1_RAW_REPLAY` новые scientific physics на Windows/WSL2 не запускаются.
  Единственное исключение — explicit bounded environment comparison WO.
- `DEFAULT_AUTHOR_EXECUTOR = NATIVE_UBUNTU_R2` — PROPOSED. Активация ТОЛЬКО после:
  (а) выделения U1 native Ubuntu; (б) frozen fingerprint
  (`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §9); (в) всех validation gates U1–U5;
  (г) всех negative controls NC-U1..U5; (д) fresh Reviewer + fresh Verifier;
  (е) Human Gate. До этого момента научные execution-запросы не имеют canonical
  executor и ожидают U1 (никакой тихий fallback на Windows запрещён).

## 2. Архитектура после активации

```text
                 GitHub
                    │
        ┌───────────┴───────────┐
        │                       │
Native Ubuntu U1            Ubuntu U2 (outenemy)
AUTHOR / DEV                EXTERNAL
PRIMARY EXECUTOR            REPRO / VERIFY
        │                       │
        └──────── evidence ─────┘

Windows:
UI / emergency historical evidence only
NOT scientific executor · NOT required CI host · NOT canonical raw-data host
```

outenemy НЕ становится author/dev host — он сохраняет независимую внешнюю роль.
U1 — отдельная машина, не совпадающая с U2.

## 3. Разделение процессов (после активации R2)

```text
nanolab-executor.service / systemd-run --scope   ← scientific jobs
github-actions-runner.service                    ← CI, отдельно

CI ЗАПРЕЩЕНО: systemctl reboot · systemctl shutdown · kill executor cgroup
Scientific job переживает: SSH disconnect · agent crash · terminal close · CI restart
Deliberate kill → supervisor: FAILED_TECHNICAL, run ID не переиспользуется
```

Root cause, который исключается конструктивно: цикл «CI job → `wsl --shutdown` →
physics killed → retry storm» (NL5-002-E P1, RECOVERY_INCIDENTS.md). Scientific
executor и CI runner не владеют жизненным циклом друг друга.

## 4. Surface rules для локальных агентов

- Новые local agents ищут Ubuntu host (U1) первым; Windows fallback не является
  canonical executor ни для build, ни для scientific runs, ни для raw data.
- Запуск agent session на U1: `ssh <u1-host>`, `cd ~/src/NanoLab`,
  `git fetch --all --prune` — без цепочки Windows → PowerShell → WSL.
- До активации R2: Windows используется только для чтения historical evidence,
  harness/documentation work (C0) и координации; никаких новых scientific runs.

## 5. Научные границы (не меняются этой политикой)

- `PLATFORM_INSENSITIVE` (WO-NL5-002-E-R1) — свойство frozen R1 исследования;
  НЕ означает «все платформы дают одинаковые trajectories».
- Старые scientific numbers НЕ становятся oracle для R2. Сравнение платформ —
  только explicit bounded comparison WO (Ubuntu U1 vs U2/outenemy).
- Будущие scientific WO после активации R2 получают
  `execution_environment = ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU` и остаются
  отдельно preregistered (HIGH — по классу научной задачи).
- `NL5 = IN_PROGRESS`, `NL6-001 = LOCKED`, `external_reproductions = 0` —
  миграция сама по себе их не меняет; `NL5-ACCEPTANCE-POLICY` решается отдельно.
