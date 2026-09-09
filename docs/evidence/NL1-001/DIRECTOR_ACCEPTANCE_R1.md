# Director Acceptance — NL1-001 (pin environment and upstream smoke)

Дата решения: 2026-09-09. Роль: DIRECTOR (главный агент миссии «выполняй NL1», явная авторизация владельца на merge получена в сессии).

## Решение

```text
NL1-001 = ACCEPTED
frontier = NL1 (остаётся; closes по checkpoint-catalog только после NL1-002)
next_work_order = NL1-002 (READY)
claim = C0_SOFTWARE_ONLY (научных claims нет; E1-прогоны не начинались)
```

## Основание

1. **Реализация**: `EX-NL1-001-R1` — environment pin `ENGINE_ENVIRONMENT_R1` (oxDNA `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, WSL2 Ubuntu 24.04.2, gcc 13.3.0, cmake 3.31.6 user-local, CPU Release DOUBLE; сборка воспроизводима, SHA-256 бинарей и командные цепочки зафиксированы).
2. **Fixture**: 4/4 SHA-256 MATCH пинам `E1-PROTO-R1` §2.2 (сырые blob'ы; blob SHA-1 4/4); правило байт-точного извлечения задокументировано с негативным контролем (autocrlf-ловушка воспроизведена независимо reviewer'ом и verifier'ом).
3. **Smoke**: `EX-NL1-001-SMOKE-001` COMPLETED (exit 0, wall 0.13 s, RSS 6424 KB, NaN/Inf=0) — технический go/no-go §4, научной интерпретации не подлежит; verbatim-прогон §7 не выполнялся.
4. **Независимые вердикты**: REVIEWER **PASS** (`737b3eb`, MINOR-1..3, NOTE-1..2) и VERIFIER **PASS** (`ea486e2`, F-1 MINOR, F-2 OBSERVATION) на exact subject `39b3448`; findings MINOR-класса исправлены (`d81bf63`, erratum §7; passport status — `462050f`), корректирующая запись — event 0005.
5. **UNKNOWN `E1-PROTO-R1` §11.1–2 закрыты** (effective defaults + семантика колонки 2 OBSERVED-in-source), §11.3 подтверждён; бюджет-оценка NL1-002 опубликована как planning input.

## Условия, с которыми принято

- Все прогонные артефакты NL1-001 — C0; `E1` в state.json остаётся `NOT_RUN`.
- Правило для всех будущих прогонов: входы только через `git cat-file blob` (ENGINE_ENVIRONMENT_R1 §5, §9).
- NATIVE-сборка привязана к CPU campaign-машины; смена executor → пересборка + новые SHA-256.

## Следующее действие

`NL1-002` (READY): вертикальный E1 путь по `E1-PROTO-R1` — T1 verbatim + 3 PILOT + анализ + архив + freeze `R_confirm` в `E1-PROTO-R2`. Merge этого PR переводит `next_work_order` → `NL1-002` в canonical state.
