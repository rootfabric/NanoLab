# Work Order WO-NL5-V02-FRESH-AUDIT-R1 — Director fresh audit NL5 v0.2 FROZEN_R2 + R2 activation readiness (WAITING_HOST honest record)

Статус: **IN_PROGRESS** (execution `EX-NL5-V02-FRESH-AUDIT-R1`, ветка
`control/nl5-v02-fresh-audit-r1`, base `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad`
= canonical main HEAD / merge PR #52). Родительская линия: NL5 / WO-NL5-V02-DIRECTOR-FREEZE-R2
(исполнен, FROZEN_R2 ready) + INFRA3-003 (R2 = WAITING_HOST / NOT_ACTIVE).
Track: control/NL5. Risk: **MEDIUM**. Claim ceiling: **C0_SOFTWARE_ONLY**.

Дата открытия: 2026-10-10. Trigger: central-agent mission «NL5 FINAL CLOSURE»
(§2 «точка старта», §4 Этап A, §11 правила автономности): fresh fetch + fresh
audit фактического состояния; попытка реальной активации R2; при отсутствии U1 —
максимально полный activation package, точное препятствие и честный WAITING_HOST.

## 1. Проблема / задача

Перед любым научным dispatch нужно механически подтвердить на свежем fetch:

1. Цепочка authority `S → F → D / R / V` для FROZEN_R2 на exact Git objects
   (HG-B APPROVED → F2 = 60da9a8/e565c8a → Director FREEZE R2 = a2f7304 →
   fresh Reviewer PASS → fresh Verifier VERIFIED) с сверкой SHA-256 трёх
   frozen artifacts.
2. Машинные гейты: mandatory freeze contract gate (с pinned-scan re-run) и
   mandatory feasibility gate (§10.1 N-grid) на актуальных planning inputs.
3. Доступность вычислительной среды: есть ли реальный U1 (native Ubuntu,
   физически ≠ U2/outenemy) для gates U1–U5 / NC-U1..U5 → HG-A → R2 ACTIVE.
4. Если U1 отсутствует — задокументировать точное препятствие и подготовить
   activation package так, чтобы активация после выделения U1 была механической.

## 2. Scope (allowed paths)

```text
docs/work/WO-NL5-V02-FRESH-AUDIT-R1.md
docs/work/executions/EX-NL5-V02-FRESH-AUDIT-R1/**
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FRESH_AUDIT_R1.md
docs/evidence/NL5-V02-FREEZE/DIRECTOR_FRESH_AUDIT_R1.json
docs/work/WORK_QUEUE.md            (одна surface-sync строка audit WO)
```

## 3. Вне scope (запрещено)

- Любые confirmatory scientific runs (campaign legs EX-NL5-REPRO-V0-2-U1-R1 /
  EX-NL5-REPRO-V0-2-U2-R1 остаются закрыты до полного authority chain).
- Изменение frozen package F2, FROZEN_R1 history, HG-B записи, verdicts R/V.
- Изменение `project/state.json` / canonical статусов (R2 остаётся
  `WAITING_HOST / NOT_ACTIVE`; статусные переходы = только Human Gate).
- Назначение AUTHOR_U1; объявление R2 ACTIVE; любые фиктивные host/fingerprint.
- Merge в main (остаётся Human Gate); draft PR разрешён.

## 4. Required outputs

1. Evidence: frozen gate PASS report (с re-run pinned collision scan),
   feasibility N-grid fresh reproduction, outenemy audit-fingerprint +
   check-host BLOCKED record, U1 host search inventory.
2. `DIRECTOR_FRESH_AUDIT_R1.{md,json}` — durable Director record: verified
   chain, gate results, exact blocker, activation runbook (§6 record).
3. Execution events START → CONTINUATION → HANDOFF + summary; work_cli valid.
4. Honest boundaries: НИ ОДИН статус канонического state не меняется этим WO.

## 5. Validation plan

- `work_cli validate docs/work/executions/EX-NL5-V02-FRESH-AUDIT-R1` → ok.
- `check-consistency` ok; `workflow_lint` blocking=0.
- Digest-сверка трёх frozen artifacts против Director FREEZE R2 record.

## 6. Честные границы

Этот WO ничего не активирует. При положительном audit результат — «chain
S→F→D/R/V подтверждён свежим fetch; единственный hard blocker научного dispatch
= отсутствие U1; активация механически готова». При любом расхождении — честный
FAIL-факт и stop, без подгонки.
