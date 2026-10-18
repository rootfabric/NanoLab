# U1_PROVISIONING_CHECKLIST_R1 — Проверяемые требования к выделению физической Ubuntu-машины U1 (AUTHOR_UBUNTU)

Статус пакета: **READY_FOR_HOST** — чек-лист полный и машинно проверяемый, но
машина U1 **не выделена** (канонический факт:
`docs/work/executions/EX-NL5-V02-FRESH-AUDIT-R1/evidence/u1-host-search-R1.json`,
`AUTHOR_U1 = NOT_ASSIGNED`). Все пункты имеют статус `HOST_NOT_ASSIGNED` до
фактического появления железа; ни один пункт не может получить PASS
декларацией — только выводом указанной команды на фактическом хосте.

Основания (канонические, все на `main`): `docs/research/ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md`
(§2–§5, §9), `docs/control/NATIVE_UBUNTU_EXECUTION_POLICY_R1.md`,
`docs/work/WO-NATIVE-UBUNTU-EXECUTOR-R1.md` (§3–§6),
`config/infra/r2-activation.v1.json` (`host_eligibility`, `forbidden_hostnames`),
`docs/infra/SECURITY_MODEL.md`, `docs/infra/U2_OUTENEMY_EXECUTOR_READINESS_R1.md`
(§7 — фактическая raw-ёмкость). Исполнение чек-листа на выделенном хосте —
runbook `docs/evidence/NL5-V02-FREEZE/DIRECTOR_FRESH_AUDIT_R1.md` §6
(`scripts/r2` fingerprint → build-engine → gates → NC → activation-check).

## 0. Главный инвариант: U1 ≠ U2 ≠ Windows/WSL2

| id | Требование | Проверка | Pass-условие | Статус |
|---|---|---|---|---|
| INV-1 | U1 — отдельная **физическая** машина, не совпадающая с U2 (outenemy) ни целиком, ни как VM/LXD-контейнер на ней | Сопоставление `hostname`, серийных номеров (`/etc/machine-id`, `dmidecode -s system-serial-number`) U1 и U2; владелец подтверждает физическую отдельность в allocation record | Оба идентификатора различны; hostname U1 отсутствует в `forbidden_hostnames` (`outenemy`); владелец письменно подтвердил выделение | HOST_NOT_ASSIGNED |
| INV-2 | U1 — native Ubuntu (native kernel, native ФС, native systemd); НЕ WSL, НЕ Docker Desktop VM, НЕ VirtualBox VM, НЕ bind mount `/mnt/c` | `PYTHONPATH=scripts python3 -m r2.cli check-host` на U1 | verdict = eligible (`virt=none`, без Microsoft-kernel маркера, native ext4/xfs/btrfs, systemd доступен) | HOST_NOT_ASSIGNED |
| INV-3 | U1 — author/dev/primary executor; outenemy сохраняет роль внешней независимой репродукции (U2, `EXTERNAL_U2_ONLY`) и **никогда** не предлагается как author executor | Политика `NATIVE_UBUNTU_EXECUTION_POLICY_R1.md` §2; deny-list в `config/infra/r2-activation.v1.json` | `r2.cli check-host` на outenemy остаётся NOT_ELIGIBLE (негативный контроль); ни один документ этого пакета не назначает outenemy автором | HOST_NOT_ASSIGNED |
| INV-4 | Windows/WSL2 не используется ни для U1, ни для новых scientific runs | `WINDOWS_ALLOWED_FOR_NEW_SCIENCE = NO` (owner decree 2026-09-27) | U1 не является Windows-хостом: `/proc/version` без Microsoft маркера; fallback-путь Windows в любом документе пакета отсутствует | HOST_NOT_ASSIGNED |

## 1. Hardware baseline (минимум для CPU-кампании 296+56 runs)

Фактическая ёмкость доказана на U2 (`U2_OUTENEMY_EXECUTOR_READINESS_R1.md` §7):
raw-проекция кампании ≈ 15 ГБ на ногу при пороге контроля 80%. Требования ниже —
нижняя граница, совместимая с этим объёмом и параллельной сборкой; точные
значения фиксируются фактическим fingerprint (§5), а не назначаются заранее.

| id | Требование | Проверка | Pass-условие | Статус |
|---|---|---|---|---|
| HW-1 | CPU x86_64, ≥ 16 физических ядер (CPU-only oxDNA, без CUDA) | `lscpu \| grep -E '^CPU\(s\)|Model name'` | ≥ 16; модель записана в fingerprint | HOST_NOT_ASSIGNED |
| HW-2 | RAM ≥ 32 GiB свободно под scientific jobs (без конкуренции с CI) | `free -h` | available ≥ 32 Gi | HOST_NOT_ASSIGNED |
| HW-3 | Диск под `~/nanolab/raw` ≥ 100 GiB нативной ФС (raw ≈ 15 ГБ/нога × запас на replacement + workspace + cache + сборки) | `df -h ~/nanolab/raw` | ≥ 100 GiB free на ext4/xfs/btrfs; порог оповещения 80% зафиксирован | HOST_NOT_ASSIGNED |
| HW-4 | Отдельная физическая машина, выделенная кампании (не общий desktop, не машина с посторонними production-нагрузками) | Владелец указывает назначение хоста в allocation record | Роль AUTHOR_UBUNTU закреплена за хостом | HOST_NOT_ASSIGNED |

## 2. OS и версии (пин по факту, не назначение заранее)

| id | Требование | Проверка | Pass-условие | Статус |
|---|---|---|---|---|
| OS-1 | Ubuntu LTS, native install (версия фиксируется fingerprint'ом; друга GCC line относительно R1 допустима) | `cat /etc/os-release`; `uname -a` | Ubuntu LTS; `VERSION_*` записаны; kernel без «Microsoft» | HOST_NOT_ASSIGNED |
| OS-2 | Toolchain для сборки: `gcc`, `g++`, `cmake`, `make`, `git`, `python3` | `gcc --version; g++ --version; cmake --version; make --version; git --version; python3 --version` | Все присутствуют; версии записаны в fingerprint; автоматический `apt upgrade` отключён | HOST_NOT_ASSIGNED |
| OS-3 | Python для harness: pinned venv `~/nanolab/venvs/r2` (exact версия, dependency lock, pip/uv версии); системный Python не mutable environment | `~/nanolab/venvs/r2/bin/python3 --version`; `pip freeze` в lock | venv создан, версии зафиксированы в activation report | HOST_NOT_ASSIGNED |
| OS-4 | Git policy: `core.autocrlf=false`, `core.safecrlf=true` | `git config --global core.autocrlf; git config --global core.safecrlf` | `false` / `true` | HOST_NOT_ASSIGNED |

## 3. Disk layout (канонические пути R2)

| id | Требование | Проверка | Pass-условие | Статус |
|---|---|---|---|---|
| DS-1 | `~/src/NanoLab` — Git checkout на native ФС (НЕ `/mnt/c`, НЕ network mount) | `findmnt -T ~/src/NanoLab -no FSTYPE` | ext4/xfs/btrfs | HOST_NOT_ASSIGNED |
| DS-2 | Созданы `~/nanolab/workspaces/`, `~/nanolab/raw/`, `~/nanolab/cache/`, `~/nanolab/tools/`; physics/raw НЕ внутри Git repo | `ls -d ~/nanolab/{workspaces,raw,cache,tools}` | Каталоги существуют; путь вне `~/src/NanoLab` | HOST_NOT_ASSIGNED |
| DS-3 | Raw-манифест каждого execution: `~/nanolab/raw/<execution-id>/<attempt-id>/` + manifest (path, sha256, size, producer, retention) | Контракт `config/infra/r2-activation.v1.json` (`raw_evidence`); полевой контроль — при первом реальном run | Схема путей соответствует контракту | HOST_NOT_ASSIGNED |

## 4. Сетевая изоляция

| id | Требование | Проверка | Pass-условие | Статус |
|---|---|---|---|---|
| NET-1 | U1 не публикует сервисов в LAN; входящие соединения — только SSH с ключом | `ss -tlnp` на U1 | Слушаются только sshd (и локальные unix-сокеты) | HOST_NOT_ASSIGNED |
| NET-2 | Исходящий доступ ограничен необходимым: github.com (git/clone), PyPI — только в pinned venv при setup | `curl -sSf https://github.com -o /dev/null -w '%{http_code}'` и firewall rules владельца | git-доступ работает; прочие исходящие — по явному решению владельца | HOST_NOT_ASSIGNED |
| NET-3 | U1 и U2 могут обмениваться только через GitHub (evidence/releases), не через взаимные mounts/копирование workspace | Проверка владельцем; protocol §5: workspace U2 НЕ копируется из author | Отсутствие cross-host mounts; независимая build-цепочка на каждой ноге | HOST_NOT_ASSIGNED |

## 5. Процедура заморозки environment fingerprint (точные команды)

Выполняется на U1 сразу после выделения, вывод append-only в
`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §10 + activation report
(`ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` §9; runbook `DIRECTOR_FRESH_AUDIT_R1.md` §6, шаг 1):

```bash
hostname; uname -a; cat /etc/os-release; lscpu; free -h
gcc --version; g++ --version; cmake --version; make --version
python3 --version; git --version
systemd-detect-virt          # ожидание: none
findmnt -T ~/src/NanoLab -no FSTYPE   # ожидание: ext4|xfs|btrfs
systemctl is-system-running  # ожидание: running|degraded
git config --global core.autocrlf; git config --global core.safecrlf
PYTHONPATH=scripts python3 -m r2.cli fingerprint --out ~/nanolab/u1-fingerprint.json
PYTHONPATH=scripts python3 -m r2.cli check-host   # ожидание: eligible
```

| id | Требование | Pass-условие | Статус |
|---|---|---|---|
| FP-1 | Fingerprint записан до любого build/run, статус `ENGINE_ENVIRONMENT_R2_NATIVE_UBUNTU.md` переведён в FROZEN только по факту §9 | Файл `~/nanolab/u1-fingerprint.json` существует; digest включён в activation report | HOST_NOT_ASSIGNED |
| FP-2 | `check-host` возвращает eligible; при ineligible активация останавливается без silent fallback | exit 0 / eligible | HOST_NOT_ASSIGNED |

## 6. oxDNA build provenance (gate U1)

| id | Требование | Проверка/команда | Pass-условие | Статус |
|---|---|---|---|---|
| EN-1 | Source pin: oxDNA `lorenzo-rovigatti/oxDNA` commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` (смена версии — только отдельный future WO) | `git -C <oxdna-src> rev-parse HEAD` | = `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` | HOST_NOT_ASSIGNED |
| EN-2 | Flags: CPU, `CMAKE_BUILD_TYPE=Release`, `DOUBLE=ON`, `CUDA=OFF`, `MPI=OFF` | `PYTHONPATH=scripts python3 -m r2.cli build-engine --src <src> --build-dir <dir> --jobs <n>` | Provenance-запись (source SHA, compiler, cmake argv, CMakeCache pins, binary size, binary sha256, build log) создана tooling'ом | HOST_NOT_ASSIGNED |
| EN-3 | Migration gate = same source commit + same intended flags + clean build + engine smoke + frame0 oracle + protocol fixtures; побайтное равенство с WSL-сборкой НЕ требуется | Gates U1+U3+U4 в runbook §6 | Все соответствующие gates PASS на evidence | HOST_NOT_ASSIGNED |
| EN-4 | У U1 своя build-цепочка; binary не копируется с U2/WSL | `sha256sum <build>/bin/oxDNA` | Digest записан из собственной сборки U1 | HOST_NOT_ASSIGNED |

## 7. Зависимости (полный список для setup)

```text
build-essential (gcc, g++, make), cmake >= 3.16, git, python3 >= 3.10,
python3-venv/pip или uv, openssh-server, systemd (native), rsync (опционально,
backup raw после завершения run)
oxDNA dependencies per upstream (BOOST и пр.) — фиксируются фактической
сборкой; научные входы — только через pinned blob/object/digest contract
```

| id | Pass-условие | Статус |
|---|---|---|
| DEP-1 | Все пакеты установлены из штатного apt без сторонних PPA либо зафиксированы в build log | HOST_NOT_ASSIGNED |
| DEP-2 | Python-зависимости harness в pinned venv с lock/hash | HOST_NOT_ASSIGNED |

## 8. SSH / CI изоляция

| id | Требование | Проверка | Pass-условие | Статус |
|---|---|---|---|---|
| SEC-1 | SSH: только key-based auth; доступ — минимальному кругу исполнителей | `sshd -T \| grep -E 'passwordauthentication\|pubkeyauthentication'` | `passwordauthentication no`, `pubkeyauthentication yes` | HOST_NOT_ASSIGNED |
| SEC-2 | **Публичный PR-код никогда не запускается на доверенных self-hosted scientific узлах** (включая U1): `pull_request` jobs — только GitHub-hosted ephemeral runners; self-hosted — только explicit protected dispatch с exact subject и budget | `docs/infra/SECURITY_MODEL.md` hard rules 1–3; workflow review при подключении runner'а | На U1 нет self-hosted runner, слушающего публичные PR events | HOST_NOT_ASSIGNED |
| SEC-3 | Runner (если будет подключен позже, INFRA2-001) — отдельный non-root user, без root, без интерактивных секретов, disposable workspace; `GITHUB_TOKEN` минимальных permissions | SECURITY_MODEL isolation target | Изоляция подтверждена отдельным INFRA2 WO (не этим пакетом) | HOST_NOT_ASSIGNED |
| SEC-4 | Долгоживущие credentials не передаются simulation-процессам | SECURITY_MODEL rule 6 | Отсутствие секретов в executor environment | HOST_NOT_ASSIGNED |

## 9. systemd survival / сессии (root cause NL5-002-E исключается конструктивно)

| id | Требование | Проверка | Pass-условие | Статус |
|---|---|---|---|---|
| SYS-1 | Scientific jobs запускаются вне agent session: `systemd-run --scope` / transient unit (`nanolab-executor.service` или scoped unit per campaign); переживают SSH disconnect, agent crash, terminal close, CI restart | NC-U1, NC-U2 (runbook §6, шаг 4) | Job продолжает работать после закрытия сессии/рестарта агента | HOST_NOT_ASSIGNED |
| SYS-2 | Для user-manager пути (если root недоступен): `loginctl enable-linger <user>`; механика `systemd-run --user` проверена | `loginctl show-user <user> -p Linger` | `Linger=yes`; проверка механики зафиксирована (прецедент: U2, `u2-systemd-mechanics-R1.json`) | HOST_NOT_ASSIGNED |
| SYS-3 | CI runner и scientific executor — раздельные units; CI ЗАПРЕЩЕНЫ `systemctl reboot|shutdown`, kill executor cgroup | NC-U3, NC-U4 | Restart GitHub runner service не убивает scientific job; CI cleanup не трогает raw workspace | HOST_NOT_ASSIGNED |
| SYS-4 | Deliberate kill → supervisor фиксирует `FAILED_TECHNICAL`; run/attempt ID не переиспользуется (append-only ledger, attempt `<run_base>-R<n>`) | NC-U5 | Ledger демонстрирует новый attempt id после kill | HOST_NOT_ASSIGNED |

## 10. Процедура доказательства U1 ≠ U2 ≠ Windows/WSL2 (сводная)

1. Записать `hostname`, `cat /etc/machine-id`, `dmidecode -s system-serial-number`
   U1 и (отдельной сессией) U2 — все три идентификатора различны.
2. `hostname` U1 не входит в `forbidden_hostnames` (`outenemy`);
   `hostname` U2 входит — это её каноническая роль.
3. `r2.cli check-host` на U1 → eligible; `r2.cli check-host` на U2 →
   NOT_ELIGIBLE (негативный контроль корректен).
4. `/proc/version` U1 не содержит Microsoft; `findmnt` — native ФС; ИТОГ:
   three-way distinctness (U1 физическая Ubuntu ≠ U2 физическая Ubuntu ≠
   любой Windows/WSL2 хост) зафиксирована в activation report.

Все четыре шага на текущий момент невыполнимы по отсутствию U1 — статус
единого пакета: **HOST_NOT_ASSIGNED**.

## 11. Точный список человеческих действий для активации U1

```text
A1. Выделить/приобрести отдельную физическую машину, удовлетворяющую §1 (или
    подтвердить существующую), НИКОГДА не outenemy и не VM/LXD на outenemy.
A2. Установить native Ubuntu LTS (§2), создать пользователя исполнителя,
    настроить disk layout §3 (~/src/NanoLab + ~/nanolab/*).
A3. Обеспечить SSH-доступ по ключу для executor-сессии (§8 SEC-1) и
    опубликовать параметры доступа (host alias) в канале владельца.
A4. Зафиксировать allocation record: hostname/machine-id/serial + роль
    AUTHOR_UBUNTU + физическая отдельность от U2 (§10, шаг 1–2).
A5. После A1–A4: исполнить runbook DIRECTOR_FRESH_AUDIT_R1.md §6 на U1
    (fingerprint → build-engine → gates U1–U5 → NC-U1..U5 → activation-check)
    — это отдельные bounded WO/execution, не этот пакет.
A6. Дальнейшая цепочка — по политике: fresh review + fresh verify activation
    package → HG-A (Human Gate) → R2 ACTIVE → dispatch authority v3 →
    HUMAN_PROTECTED_WRITER launch gate.
```

До A1–A6: R2 = WAITING_HOST / NOT_ACTIVE; NEW_SCIENCE = HARD_BLOCKED; тихий
fallback на Windows/WSL2 запрещён.
