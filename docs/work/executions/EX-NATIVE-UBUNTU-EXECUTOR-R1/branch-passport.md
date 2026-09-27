# Branch Passport — control/native-ubuntu-executor-r1

```text
execution_id = EX-NATIVE-UBUNTU-EXECUTOR-R1
work_order   = WO-NATIVE-UBUNTU-EXECUTOR-R1
base_sha     = d07e75e68c20599e4b942aefb20b4b3922985219 (origin/main, fresh 2026-09-27)
branch       = control/native-ubuntu-executor-r1
risk         = MEDIUM
claim        = C0_SOFTWARE_ONLY
kind         = control / infrastructure (NOT a scientific experiment)
```

## 1. Назначение

Создать contract и control-поверхности для native Ubuntu author/development/scientific
environment R2 (`U1 = AUTHOR_UBUNTU`) и вывести Windows/WSL2 из mandatory execution
path. Windows/WSL2 (DESKTOP-QNAGSTI, ENGINE_ENVIRONMENT_R1) остаётся историческим
фактом provenance; outenemy сохраняет роль внешней независимой репродукции/верификации.

## 2. Отклонения от схемы

- `checkpoint: "INFRA3"` не матчит `^NL[0-8]$` в `execution-passport.schema.v1.json`
  — тот же задокументированный класс, что EX-INFRA0-001-R1 / EX-INFRA1-001-R1 /
  EX-INFRA1-002-R1 (NOTE-1).

## 3. Честные границы этой R1 (на момент старта)

- Машина U1 НЕ выделена (owner подтверждение 2026-09-27). Все валидационные gates
  (environment fingerprint, engine build R2, frame0, smoke, harness, NC-U1..U5)
  НЕ выполняются и задокументированы как NEXT_ACTION. Никаких PASS по ним нет.
- `DEFAULT_AUTHOR_EXECUTOR = NATIVE_UBUNTU_R2` — PROPOSED, активируется только
  после фактической R2-валидации (см. policy doc).
- `WINDOWS_WSL_EXECUTOR = HISTORICAL_ONLY` для новых scientific runs — effective
  с закрытия P1_RAW_REPLAY по owner decree (mission 2026-09-27).
- `ENGINE_ENVIRONMENT_R1.md` НЕ изменяется (исторический provenance).

## 4. Allowed paths

См. `passport.json`. Всё вне списка — вне scope.
