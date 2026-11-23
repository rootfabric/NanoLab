# U2_LIVE_HOST_OBSERVATION_R1 — Append-only addendum: live read-only наблюдение U2-хоста (post-handoff)

- `record_kind`: U2_LIVE_HOST_OBSERVATION_ADDENDUM (machine-двойник: `U2_LIVE_HOST_OBSERVATION_R1.json`)
- Дата снимка: **2026-10-25T17:33:42Z** · сессия DSH `ce662f0f-4b0d-4388-b3e0-96e018fecf94` · actor `nl5-f03-u2-preflight-r1`
- Основание: DIRECTOR ADDENDUM для F03 — F02 (`work/nl5-f02-u1-host-r1` @ `c38ad687d87bfa0c33d69bfee4fe40020d34ba45`) независимо установил и Director лично подтвердил: hostname ЭТОЙ среды = `outenemy`, текущая сессия исполняется **прямо на U2-машине**.
- **Append-only**: ни одно прежнее событие/evidence не редактировалось; event 0001 (BLK-1) и handoff 0003 остаются историей. Настоящий addendum уточняет **классификацию доступа**, не класс вердикта. C0_SOFTWARE_ONLY · **scientific_runs = 0** · изменений состояния хоста — 0 · запусков тулинга — 0.

## 1. Observation топологии среды (environment topology observation)

```text
FACT       = Director-оркестрация (DSH) и её ролевые субагентские сессии
             (включая эту U2-сессию и параллельную F02) физически исполняются
             НА U2-машине (hostname outenemy).
ИНВАРИАНТ  = независимость научных ног (author vs external reproduction)
             определяется процессами/креденшелами/хостами ИСПОЛНЕНИЯ НАУКИ,
             а не местом запуска Director-чата.
СЛЕДСТВИЕ  = это НЕ делает сессию author-сессией: 0 scientific runs, 0 авторских
             артефактов; outenemy остаётся EXTERNAL_U2_ONLY (запрещён как author).
             ROLE ACTOR IDENTITY IS NOT PROOF OF INDEPENDENT EXECUTOR IDENTITY.
РОЛЬ       = U2 как научный оператор по-прежнему требует owner-координации и
             отдельной защищённой сессии; эта сессия — C0 read-only/documentary.
```

## 2. Исправление классификации доступа

Формулировка `BLOCKED_NO_U2_ACCESS_FROM_SESSION` (event 0001) была честной **на момент записи**: SSH-маршрута/креденшалов к отдельному U2-логину не было (`~/.ssh/config` отсутствует, `outenemy` — 0 вхождений в `~/.ssh/known_hosts`). Topology-факт (F02 + Director) показывает: сессия уже находилась **на** U2-хосте, поэтому read-only наблюдение стало возможным и выполнено. Теперь BLOCKED относится только к: (а) operator-активностям с изменением состояния/исполнением (репетиции L-02/L-06…L-10, сервисные операции) — требуют owner-координации и защищённой сессии; (б) U2 как научному оператору. Ничего не симулировано: все числа §3 собраны этой сессией read-only командами.

## 3. Live read-only снимок (независимый, эта сессия)

| Категория | Факт (2026-10-25T17:33:42Z) | Сверка |
|---|---|---|
| Identity | hostname `outenemy`, machine-id `e06fe756a6ce49cabc9ebaf394fd6837`, rdpuser uid 1001 | = F02 и = записи 2026-10-11 |
| OS/kernel/virt | Ubuntu 22.04.5 LTS; 5.15.0-190-generic; `systemd-detect-virt`=none | дрейфа НЕТ vs `u2-fingerprint-R1.json` |
| CPU | 64 × Xeon E5-2698 v3, 2 сокета, 2 NUMA | совпадает |
| RAM | total 125Gi, **available 14Gi** (used 109Gi); HW-порог «available ≥ 32Gi» НЕ выполнен | = F02 |
| Swap | **8.0Gi/8.0Gi — FULL** | = F02 |
| Диски | `/` ext4 458G, avail **19G, 96%**; `/mnt/gig` ext4 938G, avail 50G, **95%**; `/mnt/sda1` ntfs 932G, avail 78G, **92%** | порог контроля 80% **ПРЕВЫШЕН на всех томах** |
| Inodes `/` | 14% used | давления нет, давление байтовое |
| `~/nanolab/{workspaces,raw,cache,tools}` | существуют, owner uid 1001, mode 775 | = записи |
| Текущий след | raw 12K, cache 162M, workspaces 832K | проекция ~15 GB/ногу ещё не расходована |
| **Engine binary** | `~/nanolab/cache/oxdna-build-r2-u2/bin/oxDNA` sha256 `6effd00a…5126b78`, size 3 380 728, provenance присутствует | **EXACT MATCH** к `u2-engine-build-result-R1.json` — дрейфа с 2026-10-11 нет (L-04 live PASS) |
| systemd | **system = degraded (exit 1), user = degraded (exit 1)** | **ДРЕЙФ**: 2026-10-11 записан user manager active (RC 0). NC-гейты выживаемости job из degraded-состояния объявлять нельзя — нужна диагностика failed units оператором |
| NTP | service active, clock synchronized | L-11 live PASS |
| Сеть | 1264 listening-записей (TCP+UDP), 44 TCP-листенера на широких адресах | подтверждает наблюдение F02 о сторонних сервисах |
| Egress | github.com достижим (git fetch этой сессии; HTTP 200 у F02) | подтверждено |

## 4. Обновление статуса чек-листа L-01…L-12

| # | Статус | Комментарий |
|---|---|---|
| L-01 | **PARTIAL_PASS_LIVE** | identity/OS/kernel/virt/CPU перепроверены live, совпадение; полный прогон r2.cli fingerprint — за операторской сессией |
| L-02 | OPEN (operator session) | негативные контроли тулинга вне read-only scope |
| L-03 | **MEASURED_FAIL_ON_THRESHOLD** | замер live: требуемые ~30 ГБ (2×15 ГБ) номинально есть на `/mnt/gig` (50G) и `/mnt/sda1` (78G), но порог 80% превышен на ВСЕХ томах (96/95/92%) + swap full + 14Gi RAM available → **очистка/remediation или explicit owner accept-risk ОБЯЗАТЕЛЬНЫ до F07**; raw-том выбирать native ext4 (`/mnt/gig`), не ntfs |
| L-04 | **PASS_LIVE** | дайджест бинарника совпал байт-в-байт |
| L-05 | **DRIFT → operator diagnosis required** | оба менеджера degraded; Linger-рекомпонентовка и NC-проверки выживаемости — в защищённой сессии |
| L-06…L-08, L-10 | OPEN | тулинг/пакет/pilot — вне read-only scope этой сессии |
| L-09 | PARTIAL_EVIDENCE | egress подтверждён live; маршрут oxDNA `00dc7fb9` и канал возврата evidence — не доказаны |
| L-11 | **PASS_LIVE** | NTP активен |
| L-12 | OPEN (owner) | attestation независимости — owner action; с учётом топологии: наука должна исполняться в процессах/креденшалах, разделённых с оркестрацией |

## 5. Вердикт после addendum

```text
READINESS                = READY_FOR_DISPATCH_PREP  (класс не изменился; ограничения обновлены и частично ИЗМЕРЕНЫ)
LIVE U2 LEG              = read-only наблюдение ВЫПОЛНЕНО на хосте (17:33:42Z);
                           operator-проверки остаются BLOCKED_PENDING_OWNER_COORDINATION
НАУЧНАЯ АВТОРИЗАЦИЯ      = ОТСУТСТВУЕТ; R2 = WAITING_HOST / NOT_ACTIVE; AUTHOR_U1 = NOT_ASSIGNED
НОВЫЕ МАТЕРИАЛЬНЫЕ РИСКИ = диски >92% (порог 80% пробит) + swap full + systemd degraded
                           (оба менеджера) + 14Gi RAM available + широкая сторонняя
                           listening-поверхность  →  вход F05/F07 с этими фактами
```

## 6. Честные границы

- Наблюдение read-only; Linger/failed-units/NC-механика не дергались; тулинг не запускался (в т.ч. потому что дисковое давление делает любые сборки/репетиции рискованными без remediation).
- Совпадение дайджеста бинарника доказывает неизменность **файла**, не работоспособность окружения (см. degraded).
- Запись не является U1-fingerprint (host EXTERNAL_U2_ONLY, forbidden как author — консистентно с F02) и не активирует R2.
- Merge в main — Human Gate (Director); следующим потребителем фактов — F05 authority planning.
