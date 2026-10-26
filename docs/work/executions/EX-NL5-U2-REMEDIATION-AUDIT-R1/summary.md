# EX-NL5-U2-REMEDIATION-AUDIT-R1 — Summary

**Роль:** `U2_RESOURCE_AUDITOR` (реальная отдельная DSH-сессия `7e172f80-927f-446e-af8c-4e5aeea2fd59`, физически на U2/outenemy)
**Task:** Issue #94 · **Программа:** NL5-CLOSE-R1 (#81) · **Origin:** F03 `1831585f` (immutable)
**BASE:** `3b567ae33f247b182b2ae451d2cc4598a9e76019` (= origin/main на момент fetch; epoch-check OK)
**Класс:** `C0_SOFTWARE_ONLY` · **Научных запусков:** 0 · **Мутаций:** 0

## Вердикт

```text
VERDICT_CLASS = REMEDIATION_REQUIRED
```

U2 не готов к внешней науке по 5 независимо измеренным провалам порогов. Исправление — только через owner-аппрув (APR-1..APR-8) и отдельную защищённую сессию `U2_INFRA_OPERATOR`.

## 5 главных измеренных фактов (2026-10-26T03:20–03:28Z)

1. **Диски:** `/` (nvme0n1p2, ext4) — 96% (free 18.33 GiB); `/mnt/gig` (nvme1n1, ext4 whole-disk) — 95% (free 49.12 GiB unpriv, reserved ~47.71 GiB для root); `/mnt/sda1` (ntfs-3g, spinning) — 92%. Все >80% guard. Inode-давления нет (max 13.3%).
2. **RAM:** MemAvailable **13.99 GiB** из 125.7 GiB (цель ≥32 GiB). Главный потребитель — Cisco `vpnagentd` с RSS **57.57 GiB** (45.7% MEM, leak-подозрение, error-спам ~1/мин).
3. **Swap:** `/swap.img` **99.995% FULL** (free 45 056 B). Активного своппинга нет (vmstat si 0–4), но запас нулевой.
4. **systemd degraded на обоих уровнях:** system — `clickhouse-server.service` (232/ADDRESS_FAMILIES, с boot 2026-08-26) + `vms-startup.service` (exit-code, тот же boot); user — `xdg-desktop-portal{,-gnome,-gtk}.service` (timeout/exit-1, с 2026-10-21). Linger=yes. NC-U1..U5 объявить нельзя.
5. **Raw-цель:** единственный raw-класс том `/mnt/gig` имеет 52.76 GB free (<64 GB = 2×32 GB) и 95% usage (>80%); до guard нужно освободить **97 413 734 400 B (90.73 GiB)**. Числовой минимум L-03 ≥30 GB — выполнен; fail именно по guard/2×.

Новые факты сверх Issue #94: `/robot-full-2026-09-24.img` 108.2 GiB root-only loop (attached, не смонтирован) на `/`; microk8s-кластер (20G, ~100 sandbox-маунтов); docker Images 26.74 GB (reclaimable 2.08 GB); ~630G на /mnt/gig permission-bounded (включая LIVE postgres pgdata); uptime 61d, load ~15.

## Рекомендация

- **PRIMARY (APR-1):** выделенный native ext4 SSD/NVMe **≥512 GB** → `mkfs.ext4` → `/mnt/nanolab-raw` (fstab UUID+nofail, chown rdpuser). После 32 GB raw: usage ≤6.3%, free ≥480 GB — все цели PASS структурно. Rollback: umount + fstab-строка.
- **RAM (APR-3):** рестарт/фикс `vpnagentd` (ожидаемо +~55 GiB → 32 GiB закрывается одним рычагом) или отдельно утверждённый envelope.
- **systemd (APR-4):** защищённое операторское окно: диагностика/ремедиа 5 failed units (или owner фиксирует их безвредность).
- **Swap (APR-5):** расширить `/swap.img` до 16–32 GB или зафиксировать envelope.
- **BRIDGE (APR-6, опция):** `tune2fs -m 1 /dev/nvme1n1` (+40.6 GiB unpriv, обратимо `-m 5`) — НЕ закрывает 80% guard.
- **Релокация verified-кэшей** квантифицирована как НЕДОСТАТОЧНАЯ: NanoLab disposable ~3–5 GB против требуемых 53.51 GB (`/`) и 97.41 GB (`/mnt/gig`).

## Ownership / Gates

- Никаких удалений raw/git-checkouts/Docker/логов-по-возрасту не предлагается; только provenance + owner signoff + rollback, per-item.
- После аппрува: отдельная `U2_INFRA_OPERATOR` сессия (строго allowlist, before/after receipts) → fresh Reviewer + distinct Verifier → re-run F03 L-01..L-12 → затем F07. U2 остаётся EXTERNAL ONLY; R2 NOT_ACTIVE; F07 HARD_BLOCKED; U1 NOT_ASSIGNED; F2 не тронут.

## BLOCKED / INCONCLUSIVE (6)

tune2fs-superblock (root; statvfs-компенсация), docker on-disk bytes (docker df компенсация), раскладка ~630G /mnt/gig (permission), robot-full img точный размер (loop19-bound), boot-journal текст failed units (ротирован; exit-коды сохранены), L-04 SHA не перепроверялся (F03 PASS_LIVE действует).

## Deliverables

- `evidence/U2_REMEDIATION_PLAN_R1.json` + `.md` (альтернативы A–D, APR-1..APR-8, stop/rollback, байт-точные числа)
- `evidence/raw/01..17` (все команды + выводы)
- `events/0001-started`, `0002-continuation`, `0003-handoff` (append-only, реальные UTC)
- `passport.json` (DISPATCHED → **REMEDIATION_REQUIRED**)
- `WORK_QUEUE.md` — одна append-only строка
