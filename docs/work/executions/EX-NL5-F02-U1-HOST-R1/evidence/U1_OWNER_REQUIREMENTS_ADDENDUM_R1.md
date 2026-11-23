# U1 OWNER REQUIREMENTS ADDENDUM R1 (Director, append-only, post-handoff)

Источник: прямая директива владельца (2026-10-25/26, канал миссии NL5-CLOSE-R1).
Статус выделения НЕ меняется: **AUTHOR_U1=NOT_ASSIGNED**. Это фиксация ФОРМАЛЬНОЙ
спецификации для action A1 (owner allocation) — не выделение и не разрешение.

## Минимальная спецификация машины U1 (от владельца)

```text
ARCH        = x86-64, физические ядра >= 16
RAM         = доступно >= 32 GiB (MemAvailable)
DISK        = свободно >= 100 GiB (native FS под raw evidence)
OS          = native Ubuntu LTS (не VM на U2, не WSL2, не Windows)
ISOLATION   = физически отдельная машина, hostname НЕ outenemy (U2), U2 != U1
ACCESS      = SSH key-only, публикация host alias владельцем
```

## Канонические пути на U1 (из policy/WO-NATIVE-UBUNTU-EXECUTOR-R1)

```text
~/src/NanoLab                  # checkout
~/nanolab/{workspaces,raw,cache,tools}
```

После фактического выделения владельцем (hostname + machine-id + роль AUTHOR_UBUNTU
+ подтверждение физической отдельности) Director диспатчит F04 (R2 activation:
gates U1-U5 + NC-U1..U5 + fresh Reviewer + distinct Verifier + HG-A).

## Request for U1 != permission to use outenemy as author (Issue #94)

