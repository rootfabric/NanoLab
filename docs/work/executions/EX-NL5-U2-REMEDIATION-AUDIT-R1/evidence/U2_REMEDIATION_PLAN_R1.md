# U2_REMEDIATION_PLAN_R1 — измеренная диагностика + план восстановления U2 (outenemy)

**WO:** `WO-NL5-U2-REMEDIATION-AUDIT-R1` · **Task:** Issue #94 · **Программа:** NL5-CLOSE-R1 (#81)
**Класс claims:** `C0_SOFTWARE_ONLY` · **Научных запусков:** 0 · **Мутаций:** 0 (полностью read-only)
**Актор:** `U2_RESOURCE_AUDITOR` (DSH subagent `7e172f80-927f-446e-af8c-4e5aeea2fd59`), сессия физически на U2.
**Окно замеров:** 2026-10-26T03:20:44Z … 2026-10-26T03:28:25Z UTC. Origin-факты: F03 `1831585f` (immutable), BASE `3b567ae` (epoch-check OK).

## Вердикт

```text
VERDICT_CLASS = REMEDIATION_REQUIRED
```

Пять независимых MEASURED_FAIL по порогам, которые охраняет Issue #94:

| # | Метрика | Порог | Измерено | Вердикт |
|---|---------|-------|----------|---------|
| 1 | usage `/` (nvme0n1p2 ext4) | ≤80% | **96%** (free 18.33 GiB unpriv) | FAIL |
| 2 | usage `/mnt/gig` (nvme1n1 ext4 whole-disk) | ≤80% | **95%** (free 49.12 GiB unpriv) | FAIL |
| 3 | usage `/mnt/sda1` (ntfs-3g, spinning) | ≤80% (+ не raw-approved) | **92%** | FAIL |
| 4 | MemAvailable | ≥32 GiB | **13.99 GiB** | FAIL (deficit 18 GiB) |
| 5 | swap | headroom | **8589885440/8589930496 B = 99.995%** | FAIL (FULL) |
| 6 | systemd system+user | active | **degraded/degraded** (5 failed units) | FAIL |
| 7 | free ≥2× raw (2×32 GB) на native-ext4 raw FS | ≥64 GB | **52.76 GB** на /mnt/gig | FAIL (−11.25 GB) |

L-03-нюанс: числовой минимум ≥30 GB free на /mnt/gix **выполнен** (52.76 GB) — fail именно по 80%-guard и 2×-margin. Inode-давления нет нигде (макс. 13.3% на `/`): давление чисто байтовое.

## 1. Файловые системы (байт-точные)

| Mount | Device | FS | Total B | Used B | Free unpriv B | Reserved ~B | Use% | Inodes used |
|---|---|---|---|---|---|---|---|---|
| `/` | /dev/nvme0n1p2 | ext4 | 491 104 411 648 | 446 395 604 992 | 19 686 797 312 (18.33 GiB) | 25 022 009 344 (5.10%) | 96% | 4 058 560/30 531 584 (13.3%) |
| `/mnt/gig` | /dev/nvme1n1 (whole) | ext4 | 1 006 980 812 800 | 902 998 384 640 | 52 755 177 472 (49.12 GiB) | 51 227 250 688 (5.09%) | 95% | 148 801/62 513 152 (0.24%) |
| `/mnt/sda1` | /dev/sda1 | ntfs (fuseblk) | 1 000 202 039 296 | 917 158 621 184 | 83 043 418 112 (77.34 GiB) | 0 | 92% | n/a |

Reserved: `tune2fs -l` требует root (sudo -n недоступен) → вычислено через `os.statvfs` (f_bfree − f_bavail), совпадает с ext4 default 5%. NTFS **не утверждён** для canonical raw.

Ключевые находки сверх Issue #94:
- `/robot-full-2026-09-24.img` — root-only ext4 loop-образ **108.2 GiB** (loop19, attached, НЕ смонтирован) на `/`.
- microk8s-кластер: 20G в `/var/snap/microk8s`, ~100 sandbox-маунтов, kubelite жив.
- docker: Images 26.74 GB (reclaimable лишь 2.08 GB), Containers 4.43 GB, Volumes 6.63 GB (reclaimable ≈ 0).
- `/mnt/gig`: unpriv du видит 211G (Dayz 70G, SE2023 50G, «7 dayz» 50G, Ubunta Rust Server 28G…), **~630G permission-bounded** (clickhouse/, живой postgres pgdata/, filebrowser/) — INCONCLUSIVE для этой сессии. Том общий с шумными third-party тенантами — даже после очистки это не чистая raw-поверхность.
- `/home/rdpuser` = 256G: vm 109G, robot-aiten 26G, .qrl 19G, VirtualBox VMs 15G, .local 14G, .config 11G…
- NanoLab-атрибутика мала: `~/nanolab` = 162M (raw 12K, cache 162M), worktrees ~7.8G ⇒ **релокация disposable-кэшей NanoLab не решает проблему ёмкости** (нужно 53.51 GB на `/` и 97.41 GB на /mnt/gig до ≤80%).

## 2. RAM / swap

- Mem: 135 021 649 920 B total; available **15 026 679 808 B = 13.99 GiB** (target 32 GiB, дефицит ~18 GiB).
- Swap `/swap.img`: **99.995% full** (free 45 056 B). Давления в момент замера нет (vmstat si 0–4, so 0), но запаса ноль: любой новый потребитель → мгновенный swap-out/OOM-риск.
- Топ: **cisco `vpnagentd` RSS 60 370 156 KiB = 57.57 GiB (45.7% MEM**, подозрение на утечку, с 13 сентября, error-спам в journal каждую минуту); VBoxHeadless SE2023 15.66 GiB; VirtualBoxVM ubuntu-proxy 7.84 GiB; Jitsi 3.36 GiB; GitLab-стек ~5 GiB; kubelite 1.03 GiB; DSH web 1.0 GiB.
- Хост мультитенантный: microk8s, GitLab, Jitsi, ClickHouse, живой postgres, 3× actions-runner, 2 VM, VPN, xrdp — структурный, не транзиентный спрос.
- Рычаги: фикс/рестарт vpnagentd → **+~55 GiB** (один этот рычаг закрывает 32 GiB цель); suspend VM на время science-run → +15.7/+7.8 GiB (owner choice).

## 3. systemd: кто и почему degraded

**system: `degraded`** — 2 failed units:
1. `clickhouse-server.service` — failed с **2026-08-26** (текущий boot, uptime 61d), `status=232/ADDRESS_FAMILIES` (не смог bind address family на старте). Unit enabled, сторонний сервис. Точный текст ошибки **ротирован** из journal → INCONCLUSIVE detail.
2. `vms-startup.service` — failed с **2026-08-26**, exit-code при старте (custom unit «Start multiple VirtualBox VMs»; сами VM при этом запущены отдельно). Journal ротирован → INCONCLUSIVE detail.

**user: `degraded`** — 3 failed units: `xdg-desktop-portal.service` (timeout, SIGTERM), `xdg-desktop-portal-gnome.service` (exit 1/FAILURE), `xdg-desktop-portal-gtk.service` (exit 1/FAILURE) — все с **2026-10-21** (desktop-portal-стек xrdp-сессии). Linger=yes.

Пока менеджеры degraded — NC job-survival gates (NC-U1..U5) объявить нельзя (L-05 → подтверждено с атрибуцией). Рестарты/resets-failed **не выполнялись** (запрещены). Текущий err-поток journal доминирован `acvpnagent` CERTSTORE_ERROR_NULL_POINTER ~1/мин.

## 4. Альтернативы восстановления (сравнительная таблица)

| Критерий | **A. Выделенный native ext4 диск под raw** (РЕКОМЕНДОВАН) | B. Owner-reclamation ≥97.41 GB на /mnt/gig | C. Реclamation на `/` + релокация verified-кэшей | D. Bridge: tune2fs -m 1 на /mnt/gig |
|---|---|---|---|---|
| Эффект | raw-том: usage ~0%→≤6%, free ≥480 GiB ⇒ **все цели PASS структурно** | usage ≤80% PASS, 2× PASS (если ≥97.41 GB) | на `/` нужно ≥53.51 GB — только owner-активы; кэши дают лишь ~3–5 GB | 2× PASS (+40.6 GiB unpriv), **usage guard остаётся FAIL (95%)** |
| Оценка ГБ | ≥512 GB SSD/NVMe (min viable ~200 GB) | ≥97.41 GB (90.73 GiB) | ≥53.51 GB на `/` (owner-активы) + 3–5 GB кэши | +40.6 GiB unpriv free |
| Риски | Низкие: не трогает существующие данные; одна fstab-строка (UUID+nofail) | ВЫСОКИЕ: third-party и **живой postgres pgdata**, clickhouse root-owned | Средне-высокие на owner-активах; низкие на кэшах (rebuildable) | Средне: меньше root-headroom на 95%-полном томе с живыми БД |
| Rollback | umount + удалить fstab-строку; нулевая data-зависимость | только backup-first per-item | кэши: rebuild по provenance; активы: archive-then-delete | `tune2fs -m 5` (точный обратный) |
| Стоимость владения | железо + 1–2h оператор; 0 recurring | высокий owner-review per-item; том снова заполнится | owner-review; hygiene дёшев | минуты; 0 |
| Owner-аппрув | железо + окно оператора + маунт-план | per-item signoff + provenance + backup | каждый item отдельно | явный (root-мутация) |
| Вердикт | **PRIMARY** | FALLBACK, не рекомендован | HYGIENE-трек для кэшей; активы — по signoff | BRIDGE, только если диск A задерживается |

**Запрещённые варианты (не предлагаются):** удаление raw-артефактов, git-checkouts, Docker images/volumes, логов «по возрасту» — только provenance + owner signoff + rollback в отдельной операторской сессии. NTFS не предлагается для canonical raw.

## 5. Рекомендация (количественно)

1. **Вариант A**: выделенный NVMe/SSD ≥512 GB (min ~200 GB), `mkfs.ext4`, маунт `/mnt/nanolab-raw` (fstab UUID+nofail), chown rdpuser. После записи 32 GB raw: usage ≤6.3% ≤80% ✓, free ≥480 GB ≥64 GB ✓, L-03 ✓. Рекомендованный объём 512 GB–1 TB (запас на несколько кампаний + манифесты + репликация).
2. **RAM-трек**: owner-рестарт/фикс `vpnagentd` (ожидаемо +~55 GiB → 32 GiB цель достигается одним рычагом) либо отдельно утверждённый capacity envelope; опционально suspend VM на время пилота.
3. **systemd-трек**: защищённая сессия `U2_INFRA_OPERATOR` диагностирует/чинит или owner объявляет безвредными 5 failed units (см. §3), затем NC gates.
4. **Swap**: расширить `/swap.img` до 16–32 GB или зафиксировать envelope «8G swap + ≥32 GiB MemAvailable после фикса vpnagentd».
5. Опционально bridge D (tune2fs -m 1, обратимо -m 5) и hygiene APR-7 — каждый пункт отдельно, никогда автоматически.

## 6. Что требует owner-аппрува (APR-1…APR-8)

См. `U2_REMEDIATION_PLAN_R1.json` → `owner_approval_requests`: железо/маунт (APR-1), per-item reclamation (APR-2), рестарт vpnagentd или envelope (APR-3), операторское окно на systemd (APR-4), swap (APR-5), tune2fs-bridge (APR-6), hygiene per-item (APR-7), governance-подтверждение external-only + последовательность «оператор → fresh Reviewer + distinct Verifier → re-run F03 L-01..L-12 → только затем F07» (APR-8).

## 7. Stop / rollback условия

- Любое искушение мутации вне allowlist → STOP, BLOCKED-evidence. Epoch-change на main → STOP, re-baseline. Wall > 3h → STOP, handoff. Owner отклоняет APR-1…APR-5 целиком → переклассификация в `BLOCKED_OWNER` **новым** append-only event.
- Rollback по каждому варианту — в JSON (`rollback_conditions`); A и D обратимы без потери данных.

## 8. BLOCKED / INCONCLUSIVE

1. `tune2fs -l` точные superblock-параметры — root недоступен; компенсация: statvfs-оценка 5.10%/5.09% (совпадает с default).
2. Точные байты `/var/lib/docker` — permission; компенсация: `docker system df`.
3. Распределение ~630G на /mnt/gig (clickhouse/pgdata/filebrowser) — permission-bounded INCONCLUSIVE.
4. Точный размер/содержимое `/robot-full-2026-09-24.img` — root-only; компенсация: loop19 = 116 223 467 520 B, attached-but-unmounted.
5. Причины загрузочных отказов (clickhouse 232/ADDRESS_FAMILIES, vms-startup) — journal ротирован; exit-коды зафиксированы.
6. L-04 (SHA движка) в этой сессии не перепроверялся (вне C0-скоупа); действует PASS_LIVE F03 от 2026-10-25; дрейф не заявляется.

## 9. Расхождения Issue #94 ↔ факты

Цифры Issue #94 подтверждены байт-в-байт (округления df учтены). Дополнено: атрибуция 5 failed units; новые факты — vpnagentd-утечка (45.7% MEM), microk8s, docker-инвентарь, robot-full-образ, uptime 61d, Linger=yes. Нюанс: минимум ≥30 GB на /mnt/gig выполнен — L-03 fail именно по 80%-guard/2×-margin.
