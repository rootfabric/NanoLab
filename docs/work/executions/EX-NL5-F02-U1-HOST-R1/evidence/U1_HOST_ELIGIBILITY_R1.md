# U1_HOST_ELIGIBILITY_R1 — готовность native Ubuntu хоста U1 (C0, read-only)

**Execution:** `EX-NL5-F02-U1-HOST-R1` · **WO:** `WO-NL5-F02-U1-HOST-R1` · **Issue:** #83 (программа NL5-CLOSE-R1 #81)
**Claim:** `C0_SOFTWARE_ONLY` · **SCIENTIFIC_RUNS = 0** · Дата: 2026-10-25

## Вердикт

```text
VERDICT            = BLOCKED_OWNER_U1
CANDIDATE MARKING  = CANDIDATE_NOT_ALLOCATED
AUTHOR_U1          = NOT_ASSIGNED        (канонический статус не менялся)
R2_STATUS          = WAITING_HOST / NOT_ACTIVE
BLOCKER CLASS      = OWNER_ALLOCATION_ABSENT
NEXT ACTOR         = owner (human): действия A1–A6, затем HG-A → F04
```

Владелец не выделил native Ubuntu хост U1 и не опубликовал SSH-доступ. По hard gate
WO ничего не имитируется: выдача U2/VM/WSL2 за U1 запрещена, R2 не активируется.

## 1. Проверка owner allocation (все каналы)

| id | Канал | Результат | Detail |
|---|---|---|---|
| OA-1 | `~/.ssh/config` (owner-алиас U1) | **ABSENT** | файла нет; в `~ssh` только личные ключи исполнителя (содержимое НЕ копировалось в evidence) |
| OA-2 | env исполнителя | **NOT_FOUND** | переменных вида U1/NANOLAB/AUTHOR_UBUNTU/HOST нет |
| OA-3 | Git-документы после freeze | **NOT_FOUND** | `origin/main = 3b567ae…` = BASE (не двигался); `ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §10 = WAITING_HOST; policy = NOT_ASSIGNED; `git log --all --grep U1` после freeze — только dispatch-записи этого WO (`edd7952`, `59b59be`) |
| OA-4 | F01 handoff (`origin/work/nl5-f01-frozen-audit-r1` @ `c7c5be6`, read-only) | **CONFIRMS_NOT_ASSIGNED** | F01 matrix: F02 READY(C0) / цель BLOCKED — машины нет; противоречий нет |
| OA-5 | Локальный кандидат (текущий хост) | **FORBIDDEN_AS_U1** | hostname = `outenemy` ∈ `forbidden_hostnames` (`config/infra/r2-activation.v1.json`); это U2, роль `EXTERNAL_U2_ONLY` |

**Итог: 0 из 5 каналов содержат allocation → `BLOCKED_OWNER_U1`** (ожидаемый честный исход).

## 2. Fingerprint локального кандидата — `CANDIDATE_NOT_ALLOCATED`

> ⚠️ Это **НЕ** frozen U1 fingerprint (§9 `ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU` не
> исполнялся). Хост `outenemy` = U2 и **запрещён** как U1 deny-list'ом. Сбор — только
> читающие команды; модификаций 0; apt/установок 0; physics 0; новых сетевых сканов 0.

```text
hostname      = outenemy                      machine-id = e06fe756a6ce49cabc9ebaf394fd6837
os            = Ubuntu 22.04.5 LTS (Jammy)    kernel = 5.15.0-190-generic x86_64 (native, без Microsoft-маркера)
virt          = none (systemd-detect-virt)    PID1 = systemd; is-system-running = degraded
cpu           = 2× Xeon E5-2698 v3, 32 ядра / 64 threads, 2 NUMA
ram           = 125Gi total / 14Gi available (swap 8/8 Gi used) — под конкурентной нагрузкой
fs            = ext4 (nvme0n1p2, /); 458G total / 19G avail (96% used); доп.: nvme1n1 ext4 /mnt/gig, sda1 ntfs /mnt/sda1
toolchain     = gcc/g++ 11.4.0, cmake 3.22.1, make 4.3, python 3.10.12, git 2.34.1
listeners     = sshd(22) + множество сторонних сервисов (80, 1883, 6379, 2222, 4000, …) — NET-1 не выполняется
egress        = https://github.com → 200
paths         = ~/src/NanoLab и ~/nanolab/{workspaces,raw,cache,tools} существуют
```

Даже без deny-list хост не прошёл бы HW-2 (14 < 32 GiB available), HW-3 (19 < 100 GiB
free), HW-4 (shared desktop/production: microk8s/lxd/wine snaps), NET-1. Это
подтверждает политику: **U1 — отдельная выделенная машина, не переиспользование U2**.

## 3. Eligibility checklist (policy basis)

**Gates (все `WAITING_HOST`):** U1 engine build · U2 package verify · U3 frame0
fixtures · U4 technical smoke · U5 harness — невыполнимы без выделенного U1 (build
на U2 зачёт не принимает: EN-4 требует собственную build-цепочку U1).

**Negative controls (все `WAITING_HOST`):** NC-U1 SSH/session close · NC-U2 agent
restart · NC-U3 runner service restart · NC-U4 CI cleanup вне raw · NC-U5 deliberate
kill → `FAILED_TECHNICAL`, run ID не переиспользуется.

**Deny-list / роли:** `forbidden_hostnames = [outenemy]`; outenemy =
`EXTERNAL_U2_ONLY` (никогда author/dev host); U1 = отдельная физическая Ubuntu,
не U2 и не VM/LXD на U2; Windows/WSL2 = HISTORICAL_ONLY, тихий fallback запрещён.

**Изоляция scientific executor от CI:** `nanolab-executor.service` /
`systemd-run --scope` отдельно от `github-actions-runner.service`; CI запрещены
`systemctl reboot|shutdown` и kill executor cgroup; job переживает SSH disconnect /
agent crash / CI restart (root cause NL5-002-E). Публичный PR-код — никогда на
доверенных self-hosted scientific узлах (только ephemeral GitHub-hosted runners;
self-hosted — explicit protected dispatch); runner (если позже) — non-root user,
disposable workspace, минимальный token — отдельный INFRA2 WO.

**Канонические пути:** `~/src/NanoLab`; `~/nanolab/workspaces/<execution-id>/`;
`~/nanolab/raw/<execution-id>/<attempt-id>/` (manifest: sha256, size, producer,
retention); `~/nanolab/cache/`; `~/nanolab/tools/`. Physics/raw — вне Git repo.

**Credential scope (без секретов):** SSH только key-based (`passwordauthentication
no`, `pubkeyauthentication yes`), доступ минимальному кругу; git
`core.autocrlf=false` / `core.safecrlf=true`; Python — pinned venv
`~/nanolab/venvs/r2` (global pip запрещён); ключи/токены не копируются в Git/логи —
в настоящем evidence секретов 0 (личный ключ исполнителя — не owner allocation).

**Hardware baseline (минимумы):** HW-1 ≥ 16 phys cores x86_64 (CPU-only); HW-2
≥ 32 GiB RAM available; HW-3 ≥ 100 GiB free под `~/nanolab/raw`; HW-4 выделенная
машина кампании.

## 4. Evidence matrix — что блокирует R2 activation (→ F04) и что делает owner

Блокирует: отсутствие allocation record (hostname/machine-id/serial + роль
AUTHOR_UBUNTU + подтверждение физической отдельности от U2) и SSH host alias →
fingerprint freeze, build, gates U1–U5, NC-U1..U5, fresh review/verify, HG-A — все
`WAITING_HOST`. F04 не стартует.

Точный список действий владельца (HG-A chain → F04):

```text
A1. Выделить/подтвердить отдельную физическую машину (HW-1..4; НИКОГДА outenemy,
    никогда VM/LXD на outenemy, не Windows).
A2. Native Ubuntu LTS + пользователь исполнителя + disk layout §3
    (~/src/NanoLab + ~/nanolab/{workspaces,raw,cache,tools}).
A3. SSH key-only доступ (SEC-1) + публикация host alias в канале владельца.
A4. Allocation record: hostname/machine-id/serial + роль AUTHOR_UBUNTU +
    физическая отдельность от U2.
A5. На U1: runbook DIRECTOR_FRESH_AUDIT_R1.md §6 — fingerprint → build-engine →
    gates U1–U5 → NC-U1..U5 → activation-check (отдельные bounded WO/execution).
A6. fresh review + fresh verify activation package → HG-A (Human Gate) →
    R2 ACTIVE → dispatch authority v3 → HUMAN_PROTECTED_WRITER → только тогда F04.
```

## 5. Расхождения Issue #83 ↔ репозиторий

- Issue допускает «U1 eligible or BLOCKED_HOST»; факты дают точнее: **BLOCKED_OWNER_U1**.
- «Verified host fingerprint» возможен только на выделенном U1; опубликован read-only
  fingerprint локального кандидата с маркировкой `CANDIDATE_NOT_ALLOCATED` /
  `FORBIDDEN_AS_U1`.
- «WO #65 chain» = `docs/work/WO-NATIVE-UBUNTU-EXECUTOR-R1.md` +
  `docs/infra/U1_PROVISIONING_CHECKLIST_R1.md` — ссылки сохранены.

Machine-mirror: `U1_HOST_ELIGIBILITY_R1.json` (те же факты, строгий JSON).
