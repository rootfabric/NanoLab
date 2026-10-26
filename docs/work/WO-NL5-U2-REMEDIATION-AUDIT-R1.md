# WO-NL5-U2-REMEDIATION-AUDIT-R1 — U2 resource diagnostics + remediation plan (C0, READ-ONLY)

**Программа:** `NL5-CLOSE-R1` (#81). **Task issue:** [#94](https://github.com/rootfabric/NanoLab/issues/94).
**Статус:** `DISPATCHED` (Director dispatch 2026-10-25). **Assigned ROLE:** `U2_RESOURCE_AUDITOR` — реальная отдельная субагентская сессия.
**Происхождение:** F03 #84, evidence `work/nl5-f03-u2-readiness-r1 @ 1831585fa70169c4e473acfe38e9603e45cfe22c` (L-03 MEASURED_FAIL_ON_THRESHOLD, L-05 DRIFT). Это НОВЫЙ отдельный C0 WO — не ретро-правка VERIFIED subject F03.

## Baseline

```text
BASE_SHA  = 3b567ae33f247b182b2ae451d2cc4598a9e76019 (fresh main; epoch-check обязателен)
BRANCH    = work/nl5-u2-remediation-audit-r1
WORKTREE  = /home/rdpuser/NanoLab/nl5-u2-remediation-audit
```

## Risk / claim / budget

```text
RISK_CLASS = MEDIUM; CLAIM = C0_SOFTWARE_ONLY; SCIENCE_RUNS = 0 (жёстко)
BUDGET     = read-only host inspection + bounded du; wall <= 3h
```

## Разрешено (read-only диагностика)

df -h/df -B1/df -i/lsblk -f/findmnt для `/`, `/mnt/gig`, `/mnt/sda1`, текущих raw/workspace mountpoints; reserved-blocks и inode headroom; **bounded** `du -x -h -d 1` только на авторизованных путях (никаких неконтролируемых full-disk сканов на нагруженной ноде); free -h/swapon --show/топ RAM-потребителей (без секретов); `systemctl --failed` и `systemctl --user --failed`, loginctl show-user (linger), bounded journalctl-выдержки.

## Запрещено (жёстко)

Любые мутации: удаление файлов, swapoff, restart сервисов, package upgrades, mounts, перемещение данных, `docker system prune`, изменение существующих научных/чужих нагрузок. Никакой науки. Никаких секретов в evidence.

## Требуемый результат

1. Независимые замеры (с командами и выводами) — утилизация/inodes/reserved по каждому FS; кандидаты роста (bounded du).
2. Memory/swap: давление, топ-потребители, MemAvailable vs требуемый preflight headroom.
3. systemd: точный список degraded/failed units (system + user), причина (bounded journal-выдержки), без рестартов.
4. Альтернативы восстановления (без исполнения): выделенный native ext4 диск/raw mount vs owner-approved релокация верифицируемых disposable-кэшей vs планированное освобождение ёмкости. **Никогда** не предлагать удаление raw-артефактов/git-checkouts/Docker images+volumes/логов «по возрасту»; нужна provenance + owner signoff + rollback. NTFS не утверждён для canonical raw.
5. Количественная цель на выбранном native-ext4 raw FS: usage ≤80%, free ≥2× прогнозируемых raw-потребностей (F05 §7: ≥32 GB/platform с запасом) и подтверждение минимума операторской L-03 ≥30 GB free; RAM: рекомендация ≥32 GiB MemAvailable до protected pilot — или отдельно утверждённый capacity envelope.
6. Точный план: оценки/риски/rollback/stop-условия/точные пути+байты, варианты для owner. Классификация строго: `REMEDIATION_REQUIRED` | `READY_AFTER_APPROVED_REMEDIATION` | `BLOCKED_OWNER`. **Никакого PASS по факту осмотра.**

## Deliverables (allowed paths)

```text
docs/work/executions/EX-NL5-U2-REMEDIATION-AUDIT-R1/evidence/U2_REMEDIATION_PLAN_R1.{json,md}
passport.json + events (START→CONTINUATION→HANDOFF) + summary.md
docs/work/WORK_QUEUE.md (одна append-only запись)
```

Corrections после терминала — только новым append-only event/evidence (прецедент F03-NF-1 учтён: **никаких** правок существующих событий).

## Gates (из Issue #94)

NO accept-risk здесь; NO science (F07=HARD_BLOCKED, R2=WAITING_HOST/NOT_ACTIVE, U1=NOT_ASSIGNED); freeze F2 неизменен; request U1 ≠ разрешение использовать outenemy как author. После owner-аппрува плана — **отдельная** сессия `U2_INFRA_OPERATOR` применяет строго allowlisted изменения; затем fresh Reviewer + distinct Verifier и повтор F03 L-01..L-12 в protected operator-сессии до F07.

## Валидация

work_cli validate EX-NL5-U2-REMEDIATION-AUDIT-R1; check-consistency; workflow_lint; json.tool всех новых JSON.
