# EX-NL5-F02-U1-HOST-R1 — summary

**WO:** WO-NL5-F02-U1-HOST-R1 (Issue #83, программа NL5-CLOSE-R1 #81). **Роль:** HOST-PROVISIONING, реальная DSH-субагентская сессия `aa17776a-86cf-45c5-9921-d4fef9ac2c89` (identity-binding `59b59be`). **Класс:** C0_SOFTWARE_ONLY, SCIENTIFIC_RUNS = 0.

## Вердикт

```text
BLOCKED_OWNER_U1 — владелец не выделил native Ubuntu хост U1 (нет allocation record,
нет SSH host alias). AUTHOR_U1 = NOT_ASSIGNED; R2 = WAITING_HOST / NOT_ACTIVE.
Локальный кандидат помечен CANDIDATE_NOT_ALLOCATED; fingerprint не является frozen U1.
```

## Итог

- **Owner allocation 0/5 каналов:** `~/.ssh/config` ABSENT; env — нет; Git post-freeze — нет (`origin/main = BASE 3b567ae…` не двигался; policy/research остаются NOT_ASSIGNED/WAITING_HOST); F01 handoff (`c7c5be6`, read-only) подтверждает NOT_ASSIGNED; локальный хост = `outenemy` ∈ `forbidden_hostnames` (это U2, `EXTERNAL_U2_ONLY`) → **FORBIDDEN_AS_U1**.
- **Read-only fingerprint кандидата** (только читающие команды, 0 модификаций): Ubuntu 22.04.5 LTS, native kernel 5.15.0-190-generic (virt=none, systemd degraded), 2× Xeon E5-2698 v3 32C/64T, RAM 14Gi available из 125Gi, ext4 / 96% used (19Gi free), gcc 11.4.0 / cmake 3.22.1 / python 3.10.12; слушающих сервисов много (NET-1 fail). Даже без deny-list не прошёл бы HW-2/HW-3/HW-4/NET-1 → политика «U1 — отдельная машина» подтверждена фактами.
- **Eligibility checklist:** gates U1–U5 и NC-U1..U5 = `WAITING_HOST`; deny-list/роли (U2 ≠ U1); изоляция scientific executor от CI (включая public-PR правило); канонические пути `~/nanolab/…` + raw manifest; credential scope key-only, **секретов в evidence = 0**.
- **Evidence matrix:** блокирует R2 activation отсутствие allocation record + host alias; точный owner action list **A1–A6** (→ HG-A → R2 ACTIVE → только тогда F04) опубликован.
- **Расхождения Issue #83 ↔ репо:** вердикт точнее («BLOCKED_OWNER_U1», не просто BLOCKED_HOST); «verified fingerprint» возможен только на выделенном U1; «WO #65 chain» = `WO-NATIVE-UBUNTU-EXECUTOR-R1.md` + `U1_PROVISIONING_CHECKLIST_R1.md`.

## Границы

Модификаций хоста 0; apt/глобальных установок 0; physics/oxDNA 0; новых сетевых сканов 0; canonical state (`project/*.json`, frozen package) не менялся; U1 не имперсонировался; сам accept не объявлялся — максимум `HANDOFF_COMPLETED` с фактами.

## Валидация

`work_cli validate` ok; `check-consistency` ok; `workflow_lint` blocking=0; `json.tool` strict parse OK для всех новых JSON (финальные прогоны — в event 0003). Слияние в `main` — Human Gate (Director).

## Next action

Director: принять документальную передачу BLOCKED_OWNER_U1; эскалировать владельцу actions A1–A6 (HG-A chain). После реального выделения U1 — отдельный bounded WO на фактическом хосте (fingerprint → build → gates → NC → activation-check), затем F04. Научная авторизация этим WO не выдаётся.
