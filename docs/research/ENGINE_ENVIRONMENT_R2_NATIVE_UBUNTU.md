# ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU — Каноническая среда исполнения R2 (native Ubuntu)

Статус: **WAITING_HOST** (контракт заморожен; машина U1 = AUTHOR_UBUNTU не выделена
на момент ревизии R1, 2026-09-27). Execution: `EX-NATIVE-UBUNTU-EXECUTOR-R1`.
Work Order: `WO-NATIVE-UBUNTU-EXECUTOR-R1`. Risk MEDIUM, claim C0_SOFTWARE_ONLY.

> Этот документ фиксирует **требования и процедуру** канонической среды R2 и будет
> дополнен фактическим fingerprint после выделения машины. Он НЕ заменяет и не
> изменяет `ENGINE_ENVIRONMENT_R1.md` (WSL2 Ubuntu 24.04.2, i9-13900H, gcc 13.3) —
> тот остаётся историческим фактом provenance всех экспериментов R1-линии.

## 1. Engine subject (неизменяемый)

```text
engine        = oxDNA (lorenzo-rovigatti/oxDNA)
pinned commit = 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591
rights        = GPL-3.0 (NL0-002); DOWNLOAD_ON_SETUP
note          = смена engine version допустима только отдельным future WO
```

## 2. Требования к host (U1 = AUTHOR_UBUNTU)

```text
ОБЯЗАТЕЛЬНО:
  native Linux kernel            (НЕ WSL, НЕ Hyper-V/VirtualBox/Docker Desktop VM)
  native filesystem              ext4 / xfs / btrfs (НЕ /mnt/c bind mount)
  native process lifecycle       + native systemd
  systemd-run --scope / transient unit доступен для scientific jobs

ЗАПРЕЩЕНО КАК R2:
  WSL · Docker Desktop VM · VirtualBox VM · Windows bind mount /mnt/c
```

Назначение U1: AUTHOR / DEV / PRIMARY EXECUTOR. outenemy сохраняет роль внешней
независимой репродукции/верификации (U2) и НЕ используется как основной
author/dev host — иначе схема `author environment` / `external reproduction
environment` теряет независимость.

## 3. Canonical paths

```text
~/src/NanoLab
~/nanolab/workspaces/<execution-id>/
~/nanolab/raw/<execution-id>/
~/nanolab/cache/
~/nanolab/tools/
```

Physics workspaces и raw artifacts НЕ хранятся внутри Git repo.

## 4. Software policy (фиксация по факту, без auto-upgrade)

```bash
git config --global core.autocrlf false
git config --global core.safecrlf true

hostname; uname -a; cat /etc/os-release; lscpu; free -h
gcc --version; g++ --version; cmake --version; make --version
python3 --version; git --version
```

- Python: pinned `.venv` (или repo-approved equivalent): exact Python version,
  dependency lock, pip/uv version, package hashes where applicable.
- gcc/g++/cmake/make: фиксируются фактически; другая GCC line относительно R1
  допустима (это R2, а не имитация R1). Автоматический `apt upgrade` запрещён.
- Научные входы всегда через pinned blob/object/digest contract; CRLF-workaround
  не является частью normal execution path.

## 5. Fresh oxDNA build R2

```text
build flags: CPU · DOUBLE=ON · CUDA=OFF · MPI=OFF
фиксировать:  source SHA (00dc7fb9…), compiler, cmake command,
              CMakeCache relevant pins, binary size, binary sha256, build log
```

Migration gate: `same source commit + same intended build flags + clean build +
expected engine smoke + frame0 oracle + protocol fixtures`. Побайтное равенство
binary с WSL-сборкой НЕ требуется и не проверяется.

## 6. Validation gates (все статусы сейчас WAITING_HOST)

```text
U1  engine build PASS            → [ ] WAITING_HOST
U2  package verify PASS (nanolab-components; documented v0.1.1 pyc findings
    допустимы; либо bounded packaging v0.1.2 repair)  → [ ] WAITING_HOST
U3  frame0: 0b exact; 11b exact; 32b exact; 53b exact;
    74b NOT_MEASURED (если gap не ремонтировался)      → [ ] WAITING_HOST
U4  short technical oxDNA smoke (exit=0, finite outputs,
    expected frames/files; НЕ scientific claim)        → [ ] WAITING_HOST
U5  harness: unit tests · check-consistency · workflow lint ·
    work_cli validation                                → [ ] WAITING_HOST
```

## 7. Process-survival negative controls (все WAITING_HOST)

```text
NC-U1  SSH/session close  → scientific test job продолжает работать   [ ] WAITING_HOST
NC-U2  agent process restart    → job продолжает работать             [ ] WAITING_HOST
NC-U3  GitHub runner service restart → job продолжает работать        [ ] WAITING_HOST
NC-U4  CI cleanup попытка      → raw workspace вне CI и не удаляется  [ ] WAITING_HOST
NC-U5  deliberate kill process → supervisor фиксирует FAILED_TECHNICAL,
       run ID не переиспользуется                                     [ ] WAITING_HOST
```

## 8. Raw evidence manifest test

Каждый execution на U1 обязан производить `~/nanolab/raw/<execution-id>/` с
manifest (sha256, size, producer, retention policy). Git хранит только compact
evidence. Backup после завершения run: raw local + digest + optional secondary
copy; без копирования mutable trajectory во время расчёта.

## 9. Процедура заморозки fingerprint (по факту выделения U1)

1. Выполнить §4 (команды fingerprint) и записать вывод в этот документ (раздел 10).
2. Выполнить build §5, приложить cmake command + CMakeCache pins + build log +
   binary sha256/size.
3. Прогнать gates §6 и NC §7, публикуя сырые outputs append-only.
4. Перевести статус документа в FROZEN; только после этого
   `DEFAULT_AUTHOR_EXECUTOR = NATIVE_UBUNTU_R2` становится ACTIVE (см.
   `docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md`).
5. Первый научный WO на R2 — отдельно preregistered HIGH с
   `execution_environment = ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU`.

## 10. Фактический fingerprint (заполняется по факту)

```text
WAITING_HOST — машина U1 не выделена (owner подтверждение 2026-09-27).
```
