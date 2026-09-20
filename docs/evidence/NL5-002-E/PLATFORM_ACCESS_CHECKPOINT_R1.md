# PLATFORM_ACCESS_CHECKPOINT_R1 — WO-NL5-002-E-R1 (PLATFORM-SENSITIVITY-R1)

Дата (UTC): 2026-09-20T12:46:38Z (`date -u` при записи). Роль: DIRECTOR (fresh session).
Тип: administrative checkpoint — environment accessibility re-verification. **Научные прогоны не выполнялись.**

## Fresh canonical state

```text
CANONICAL_MAIN (origin/main, после git fetch --all --prune) = d07e75e68c20599e4b942aefb20b4b3922985219
WO HEAD (freeze commit)                                     = 4d6542fda81084dced2578f3e008c8c8e0705a5a
WO TREE (git rev-parse 4d6542f^{tree})                      = 7651569ac8d0e93c0cc7614cb692945ad5bd0c98
PROTOCOL                                                    = FROZEN (PREREGISTRATION_FREEZE_R1)
canonical statuses (state.json)                             = NL5-002 WAITING_HUMAN; NL5 IN_PROGRESS;
                                                              external_reproductions = 0; frontier NL5;
                                                              NL6-001 PLANNED (LOCKED); E5 NOT_RUN
```

## Accessibility determination (fresh, эта сессия)

```text
CURRENT_HOST_IS_P1 = false
P1_ACCESSIBLE      = false
P2_ACCESSIBLE      = true

PLATFORM_EXECUTION = BLOCKED_ON_P1_AVAILABILITY  (re-confirmed; без изменений)
```

### P1 — author/reference environment (frozen definition: ENGINE_ENVIRONMENT_R1 §2)

Frozen: WSL2 Ubuntu 24.04.2, kernel `6.18.33.2-microsoft-standard-WSL2`, i9-13900H, gcc 13.3.0.

Недоступна из исполнительной среды; evidence:

```text
1. Текущий host = outenemy (см. P2 fingerprint ниже): kernel 5.15.0-190-generic,
   CPU Xeon E5-2698 v3, gcc 11.4.0, /proc/sys/fs/binfmt_misc/WSLInterop отсутствует
   → исполнительная среда НЕ является WSL2-хостом владельца ни в каком смысле.
2. ~/.ssh/config отсутствует; known_hosts содержит только github.com (+ hashed github-IPs) —
   нет SSH-маршрута/credentials к P1.
3. ENGINE_ENVIRONMENT_R1 §3: «Windows-сторона; WSL не имеет прямого интернета» —
   P1 исторически не имела даже прямого сетевого доступа; путь исполнения B-R1 шёл
   через локальный доступ владельца, не через сеть.
4. Документированного способа удалённого доступа к P1 в canonical main нет.
```

Вывод: замена P1 невозможна и ЗАПРЕЩЕНА (frozen WO §Platforms + PREREGISTRATION_FREEZE_R1
Dispatch decision: подмена P1 другой средой / P2-only paired run — запрещены как научно
нечестный pairing).

### P2 — external environment (frozen definition: платформа B-R2)

Fingerprint снят ДО любых прогонов этой кампании (2026-09-20T12:46Z, host outenemy):

```text
OS        : Ubuntu 22.04.5 LTS (jammy)           — совпадает с frozen определением (22.04.x)
kernel    : 5.15.0-190-generic #200-Ubuntu SMP Fri Aug 7 15:06:04 UTC 2026
CPU       : Intel(R) Xeon(R) CPU E5-2698 v3 @ 2.30GHz — совпадает (2 sockets × 16 cores × 2 threads = 64 logical)
compiler  : gcc/g++ (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0 — совпадает (11.4)
make      : GNU Make 4.3
cmake     : 3.22.1
python3   : 3.10.12
RAM       : 125 GiB total
WSL       : отсутствует (native Linux host)
```

Сравнение с frozen определением P2 (Ubuntu 22.04.x, gcc 11.4, Xeon E5-2698 v3, host
outenemy): **material mismatch отсутствует** → `PLATFORM_ENVIRONMENT_MISMATCH` не создаётся.
P2 остаётся готовой к paired dispatch при появлении P1.

### P3

Optional; владельцем не предоставлена — не блокирует (frozen WO).

## Decision (без изменений к freeze record)

```text
Прогоны кампании (любые, включая technical pilots этой кампании) НЕ запускаются.
Разрешено и выполнено в этой сессии: docs-status sync (header WO-NL5-002-E-R1),
настоящий fresh environment-access checkpoint, administrative preparation.
Resume condition: владелец открывает доступ к P1 (WSL2 author environment) →
paired dispatch строго по frozen WO (seeds/statistics/budget без изменений);
либо явная новая revision WO.
NL6-001 / E5: LOCKED (без изменений).
```

## Файлы этой административной сессии

```text
docs/work/WO-NL5-002-E-R1.md                     — только статусная строка (FROZEN + PASS refs +
                                                   BLOCKED_ON_P1_AVAILABILITY); научные разделы не менялись
docs/evidence/NL5-002-E/PLATFORM_ACCESS_CHECKPOINT_R1.md — этот файл
docs/work/SESSION_LOG.md                         — append-only запись сессии
```
