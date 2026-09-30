# NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1 — Proposal для owner (Human Gate B)

Статус: **PROPOSAL / WAITING_OWNER** (подготовлен WO-NL5-ACCEPTANCE-POLICY-R2;
canonical main `8205781def7179d6bdfa6eb7ab2a84d46776649c`; 2026-09-30).
Это полный proposal, не вопрос: ниже — принцип, альтернативы, последствия
approval'а, готовые артефакты и точная механика следующих шагов.

## 1. Открытое решение

`NL5-ACCEPTANCE-POLICY` (открыто владельцем 2026-09-20,
`docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md`): требует ли NL5 acceptance
(a) нового preregistered reproduction rule (например, distribution-based v0.2)
с успешным внешним воспроизведением под ним, или (b) иного owner-определённого
критерия.

## 2. Предлагаемый принцип (candidate)

```text
NL5 acceptance requires successful fresh external reproduction
under preregistered v0.2 distribution-based rule
```

Операционально:

1. Candidate protocol `NANOLAB_REPRO_V0_2_CANDIDATE_R1.md` (distribution-based
   equivalence, TOST margin δ=0.5 pooled SD, fresh paired seeds, N=10/ячейка,
   4 варианта, frozen vocabulary `REPRODUCED | REPRODUCED_WITH_DEVIATION |
   INCONCLUSIVE | FAILED_TECHNICAL | MISMATCH`) freeze'ится Director-записью
   после HG-B и проходит fresh scientific review + fresh verify ДО любых данных.
2. Author leg исполняется на AUTHOR_U1 (native Ubuntu R2) ТОЛЬКО после
   активации R2 (gates U1–U5 + NC-U1..U5 + review/verify + Human Gate) —
   отдельное execution `EX-NL5-REPRO-V0-2-U1-R1`.
3. External leg исполняется на U2 (outenemy) из release package / frozen WO —
   `EX-NL5-REPRO-V0-2-U2-R1`.
4. Независимые Scientific Reviewer + Verifier пересчитывают сырые данные и
   применяют frozen decision rule механически.
5. `NL5 = ACCEPTED`, `external_reproductions >= 1` объявляются ТОЛЬКО при
   frozen criterion выполнен + Review PASS + Verify VERIFIED + отдельный
   Human Gate (HG-C) на canonical merge. При MISMATCH/INCONCLUSIVE — NL5
   остаётся IN_PROGRESS, rule НЕ подгоняется, готовится следующий научно
   обоснованный branch.

## 3. Что HG-B approval РАЗРЕШАЕТ / НЕ разрешает

```text
APPROVES:
  - принцип §2 как рабочий критерий NL5 acceptance;
  - (опционально, отдельно) candidate protocol как basis для Director freeze
    — с любыми owner-поправками ДО freeze;
  - подготовку freeze-записи (protocol + seeds + analyzer pin) как следующий WO.

DOES NOT:
  - не активирует R2 (отдельная точка: gates + review/verify + HG-A);
  - не запускает scientific runs (нужны R2 ACTIVE + frozen protocol);
  - не меняет NL5-002 terminal MISMATCH, v0.1 envelope, PLATFORM_INSENSITIVE;
  - не открывает NL6-001 автоматически;
  - не разрешает платный compute (mission §49).
```

## 4. Альтернативы (если владелец отклоняет §2)

- **A. Иной критерий NL5 acceptance** — owner формулирует; candidate v0.2
  остаётся в истории как non-frozen proposal.
- **B. v0.2 с другими параметрами** (δ, N, variants, outcomes) — правки ДО
  freeze бесплатны для protocol integrity; после freeze — только новая revision.
- **C. Отложить NL5 acceptance** — решение остаётся открытым; научная вертикаль
  стоит на NL5 (NL6-001 LOCKED), infra-линия может продолжаться независимо.

## 4.1. Известный риск, видимый владельцу ДО HG-B (review refresh R-1/R-2)

Mandatory feasibility gate (§12 candidate R2), вычисленный на committed R1
данных (`evidence/repro-v0-2-feasibility-gate-R2.json`):

```text
0b : ratio 0.124 (subsample) / 0.207 (advisory √n) → FEASIBLE
32b: ratio 1.298 (subsample) / 0.907 (advisory √n) → FEASIBILITY-UNCERTAIN
     (независимый review, параметрика для реальных n=40: 0.76–0.81)
```

По букве протокола freeze-цепочка для 32b упрётся в честный INFEASIBLE→owner.
Варианты для владельца (решение owner, не имплементатора): (i) принять риск;
(ii) ревизия R3 — сузить primary set до 0b; (iii) ревизия R3 — расширить
budget. Пороги/статистика при этом не трогаются.

## 5. Почему это соответствует прежним owner-решениям

- Миссия 2026-09-20 (record DIRECTOR_DECISION_R1) прямо предлагала v0.2-class
  distribution rule как вариант (a).
- Frozen WO-NL5-002-E-R1 показал: paired platform shifts малы относительно
  внутриплатформенного разброса (PLATFORM_INSENSITIVE), т.е. строгие, но
  узкие точечные envelope'ы стабильно дают MISMATCH не из-за science, а из-за
  формы правила. v0.2 честно разделяет technical / numerical / distributional
  reproducibility.
- Protocol integrity: freeze ДО данных, fresh seeds (исторические seeds в
  exclusion list), margin a priori по конвенции (не под R1 values), история
  append-only.

## 6. Готовые артефакты (эта ветка)

```text
candidate protocol      = docs/research/NANOLAB_REPRO_V0_2_CANDIDATE_R1.md
                          (revision R2: paired-анализ, N=40 primaries, mechanical
                          decision rule, feasibility gate, 34-seed exclusion list;
                          НЕ FROZEN)
seed generation tool    = scripts/nl5/repro_v02_seeds.py (+ тесты; deterministic,
                          exclusion 34 документированных R1 seeds)
HG-B proposal           = docs/control/NL5_ACCEPTANCE_PRINCIPLE_HG_B_PROPOSAL_R1.md (этот файл)
WO                      = docs/work/WO-NL5-ACCEPTANCE-POLICY-R2.md
execution               = docs/work/executions/EX-NL5-ACCEPTANCE-POLICY-R2/
branch                  = control/nl5-acceptance-policy-r2 (review/verify отдельно)
review cycle            = fresh scientific review R1: FAIL f07fe39 (M-1/M-2/M-3) —
                          repair R1: candidate R2 (этот package); refresh review —
                          следующий шаг. FAIL-цикл ДО freeze — свидетельство работы
                          процесса pre-data integrity, а не дефект плана.
```

## 7. Точная механика после HG-B

```text
owner: HG-B APPROVED (принцип; опционально поправки)
  → агент: Director FREEZE record (protocol + seed record + analyzer pin +
    feasibility-gate evidence §12)
  → агент: fresh scientific Reviewer + fresh Verifier на FROZEN protocol
  → параллельно: R2 activation path (HG-A: выделить U1 → gates → activate)
  → после R2 ACTIVE + FROZEN: author leg (U1) → external leg (U2)
  → independent analysis → Review/Verify → HG-C (merge NL5 acceptance)
```

Ответ владельца достаточно выразить одной строкой:
`HG-B: APPROVED` / `HG-B: APPROVED WITH CHANGES: <список>` / `HG-B: <alternative>`.
