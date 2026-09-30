# branch-passport — control/nl5-acceptance-policy-r2

```text
execution_id = EX-NL5-ACCEPTANCE-POLICY-R2
work_order   = WO-NL5-ACCEPTANCE-POLICY-R2 (open owner decision NL5-ACCEPTANCE-POLICY)
base         = 8205781def7179d6bdfa6eb7ab2a84d46776649c (origin/main, fresh fetch 2026-09-30)
risk / claim = HIGH / C0_SOFTWARE_ONLY (acceptance-policy PROPOSAL; protocol НЕ freeze'ится;
               никаких scientific runs и данных)
host         = outenemy (C0 control-work среда; scientific executor'ом не является)
```

## 1. Scope

Candidate-пакет для HG-B: HG-B proposal (принцип NL5 acceptance), candidate
protocol NANOLAB_REPRO_V0_2 (PRE-DATA, NOT FROZEN), deterministic
seed-generation tooling + тесты, sync WORK_QUEUE (NL5-002 строка). Полный
scope — `docs/work/WO-NL5-ACCEPTANCE-POLICY-R2.md` §2/§5.

## 2. Границы и честные статусы

- Никакой freeze: candidate помечен `CANDIDATE / PRE-DATA / NOT FROZEN`;
  freeze chain (HG-B → Director freeze → fresh review/verify frozen) — вне
  этого WO.
- Scientific facts не меняются: NL5-002 terminal MISMATCH / NOT accepted,
  v0.1 envelope immutable, PLATFORM_INSENSITIVE — факт frozen R1 study,
  external_reproductions = 0, NL6-001 LOCKED.
- Никаких simulations/physics; никакой платной инфраструктуры;
  `project/state.json` не изменяется (owner decision остаётся открытым —
  его закрывает владелец, не этот WO).
- Seed-tool детерминирован и привязан к protocol anchor; исторические seeds
  R1 — в frozen exclusion list (тестами).
