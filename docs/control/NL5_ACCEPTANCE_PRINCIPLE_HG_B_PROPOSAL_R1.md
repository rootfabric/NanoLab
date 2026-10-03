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
   equivalence, TOST margin δ=0.5 pooled SD, fresh paired seeds (R3:
   primaries 0b/32b = 64 paired replicas/platform, controls 11b/53b = 10
   paired replicas/platform; выбрано declared N-grid search'ом с headroom
   0.80 на committed R1 planning-данных ДО каких-либо confirmatory data),
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

## 4.1. Feasibility: resolved by declared N-grid search (candidate R3)

Предыдущий пункт риска (candidate R2: 32b ratio 1.298 при N=40 →
FEASIBILITY-UNCERTAIN) устранён конструкторски, без изменения δ/статистики:
candidate R3 зафиксировал declared N-grid search ДО вычислений (grid
{40, 48, 64, 80, 96, 128}, headroom ratio ≤ 0.80 по обеим primaries) и
механически выбрал **SELECTED_N = 64** (0b 0.071 / 32b 0.736; полный grid
в evidence `repro-v0-2-n-grid-R3.json`). Mandatory feasibility gate теперь
PASS по построению; путь «owner accepts risk → execute despite failed gate»
в R3 явно ЗАПРЕЩЁН (gate FAIL ⇒ BLOCKED; разрешение — только новая
preregistered revision, сама проходящая gate). Budget обновлён
machine-consistently: 296 confirmatory + 60 replacement = max 356 runs,
wall ≤ 560 ч/платформа.

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
                          (revision R3: paired-анализ, N=64 primaries/10 controls
                          по declared grid, mechanical decision rule + consistency gate,
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

## 8. Addendum R4 — owner decision delta (pre-freeze hardening, 2026-10-03)

Append-only addendum к этому proposal (текст §1–§7 выше не изменяется).
Focused audit R4 (2026-10-03, `docs/evidence/NL5-V02-PREFREEZE-HARDENING-R4/`)
воспроизвёл F1–F4 на exact R3 subject; hardening R4 реализован в
`EX-NL5-V02-PREFREEZE-HARDENING-R4` (ветка `work/nl5-v02-prefreeze-hardening-r4`).
Ниже — ЕДИНСТВЕННЫЕ численные delta кандидата (pre-data; confirmatory data
нет; это НЕ тихая смена science criteria — явная часть owner decision package
вместе с принципом §2):

```text
параметр                | R3          | R4 (предлагается)     | основание
N_min (primary ячейка)  | 51          | 52 = ceil(0.80·64)    | 51/64 = 79.6875% НЕ удовлетворяет literal «не менее 80%»
N_min (control)         | 8           | 8 = ceil(0.80·10)     | без изменения (8/10 = 80% ≥ 80%)
replacement budget      | ≤59 → 60    | 56 = Σ 2·floor(0.20·N)| 60/296 = 20.27% НАРУШАЕТ literal «не более 20%»; per-cell 12/12/2/2 пар: 18.75%/18.75%/20%/20%
max_runs                | 356         | 352                   | 296 + 56; ужесточение, не расширение
wall hours/platform     | 560         | 560                   | без изменения
N, δ=0.5, варианты, grid, paired scheme | — | без изменений    | не трогались
```

Целочисленная политика зафиксирована одной именованной схемой
`ceil-nmin-floor-replacement-pairs-v1` (machine-enforced в
`scripts/nl5/repro_v02_freeze_contract.py`; machine block в candidate doc).
Словесные смягчения R4 (не численные): feasibility-прохождение = planning-факт
на committed данных, не гарантия исхода; CI медианного парного сдвига
проверяет эквивалентность медианного сдвига, НЕ все свойства распределений;
старый terminal MISMATCH NL5-002 не «объясняется» формой v0.2.

Для владельца: HG-B approval по §2 теперь неявно покрывает таблицу выше;
`HG-B: APPROVED WITH CHANGES: <список>` остаётся доступным для отклонения
любой строки. До HG-B кандидат остаётся **PRE-DATA / NOT FROZEN**;
`freeze`/`dispatch` машинно запрещены без PASS полного contract gate.
