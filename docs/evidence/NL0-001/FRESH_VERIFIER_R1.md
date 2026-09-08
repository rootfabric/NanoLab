# NL0-001 — Fresh Independent Verifier R1

Исполнение: `EX-NL0-001-R1`. Роль: `VERIFIER` — независимая fresh-проверка; не Implementer и не Reviewer. PR: `rootfabric/NanoLab#11`.

Этот документ является **superseding fresh verification** для текущей сессии. Ветка `verify/nl0-001-reference-selection-r1` уже существовала до начала этой проверки на commit `5582ad765d7e43f50f48f3764ca054ad45ea2a77`; live ancestry подтверждает, что этот commit имеет прямым родителем exact candidate `f738bff77f2406552b4383c05989ffc6e56a3bd5` и до настоящего обновления ветка отличалась от candidate только этим verifier-report. Ветка не reset/force-push/delete; настоящий отчёт публикуется новым non-force commit.

```text
VERIFIED_HEAD        = f738bff77f2406552b4383c05989ffc6e56a3bd5
REVIEWED_HEAD        = f738bff77f2406552b4383c05989ffc6e56a3bd5
REVIEW_HEAD_MATCH    = YES
REVIEW_COMMIT        = e0303aa05bbcc3f6839c3af31d7a28ecbd66a932
CURRENT_MAIN         = f4d2979a1d2502d86c035f25e36961b4d5ac2764
EPOCH_DRIFT          = CONTINUE

VERDICT              = PASS

E1_HASH_CHECK        = PASS
E2_TREE_CHECK        = PASS
HARNESS_CLOSE_CHECK  = PASS
STATE_SAFETY_CHECK   = PASS

NEXT_ACTOR           = DIRECTOR
```

## Mandatory read

Live на exact candidate прочитаны `AGENTS.md`, `PROJECT_CONTROL.md`, `HARNESS_CONTROL.md`, `docs/work/WO-NL0-001.md`, `docs/research/REFERENCE_SELECTION.md`, `docs/research/INPUT_AVAILABILITY.md`, `docs/evidence/NL0-001/IMPLEMENTER_EVIDENCE.md`, execution package `docs/work/executions/EX-NL0-001-R1/`, `config/control/harness/review-policy.v1.json`, `config/control/harness/risk-policy.v1.json`, `scripts/harness/work_cli.py`. Fresh Reviewer evidence прочитан на exact `REVIEW_COMMIT=e0303aa05bbcc3f6839c3af31d7a28ecbd66a932`, а не с moving branch как источника истины.

## V1 — Candidate / Review binding

Финальный race-check перед публикацией:

```text
PR #11 state        = OPEN
PR_HEAD             = f738bff77f2406552b4383c05989ffc6e56a3bd5
REVIEWED_HEAD       = f738bff77f2406552b4383c05989ffc6e56a3bd5
REVIEW_COMMIT       = e0303aa05bbcc3f6839c3af31d7a28ecbd66a932
review branch HEAD  = e0303aa05bbcc3f6839c3af31d7a28ecbd66a932
```

`f738bff → e0303aa` имеет merge-base ровно `f738bff`; review-ветка на 3 commits впереди и меняет только:

```text
docs/evidence/NL0-001/FRESH_REVIEW_R1.md
docs/review/NL0-001_REVIEW_ASSIGNMENT.md
docs/review/NL0-001_REVIEW_STATUS.md
```

Durable report на `e0303aa` содержит `REVIEWED_HEAD=f738bff…`, `VERDICT=PASS`, `EPOCH_DRIFT=CONTINUE`, `NEXT_ACTOR=FRESH VERIFIER`.

```text
PR_HEAD == REVIEWED_HEAD → PASS
REVIEW_STALE              → FALSE
```

## V2 — E1 independently fetched evidence

Upstream: `lorenzo-rovigatti/oxDNA@00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`; live commit tree: `f03ce1de5c0f3a336cb00ad363686c4841600d10`.

Четыре exact upstream files получены на pinned SHA, их SHA-256 вычислены независимо от NanoLab evidence, после чего сравнены с `INPUT_AVAILABILITY.md`:

| Path | Size | Independently computed SHA-256 | Match |
|---|---:|---|---|
| `test/DNA/DSDNA8/dsdna8.top` | 148 B | `f1aded90b5f6e1d9adab0e55925bba778477467be2957b4093d1264160c03fc4` | YES |
| `test/DNA/DSDNA8/init.dat` | 4498 B | `0ff76d541728e0925f199970ff6296254fe6116d23e44fdf0d361d0f8891a9e0` | YES |
| `test/DNA/DSDNA8/MD/quick_input` | 533 B | `8935c4bc623ca96d406429c3c5177901f12540ffe61bcd3299931f0689af74a2` | YES |
| `test/DNA/DSDNA8/MD/quick_compare` | 51 B | `86a8b6ac50f382ba25e5aacbbef629cc5a1788f44e6c28d113509c8448e3ce27` | YES |

Содержание upstream подтверждает:

```text
dsdna8.top       = header "16 2" → 16 nucleotides / 2 strands
quick_input       = backend CPU
                    steps 1e6
                    thermostat john
                    T = 20C
                    dt = 0.005
quick_compare     = ColumnAverage::energy.dat::2::-1.37970256144::0.15
```

E1 physics simulation в этом Work Order Verifier не запускал.

## V3 — E2 exact upstream tree

Upstream: `gauravarya77/DNA-hinge-simulations@23fd1ff7731e9017bd776f49206dc42d70d9fe91`.

Live commit tree:

```text
b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9
```

Recursive tree возвращён как `truncated=false` и содержит все требуемые machine inputs:

```text
Design_Hinges/
  0b.json
  11b.json
  32b.json
  53b.json
  74b.json

MD_Hinges/
  0b.top / 0b.conf
  11b.top / 11b.conf
  32b.top / 32b.conf
  53b.top / 53b.conf
  74b.top / 74b.conf
  pro_CPU.in
  pro_GPU.in

Init_Hinges/
  README.md
  cadnano_interface.py
  init_generator.py
  ini_demo/...
```

Пять design blob SHA-1 и sizes совпали с NanoLab evidence. `MD_Hinges/pro_CPU.in` blob = `89d76310ce726eaec9e7acb312bd7b0fc43fa735`; live content:

```text
backend = CPU
backend_precision = double
steps = 2e7
interaction_type = DNA2
salt_concentration = 0.5
T = 300K
```

Pinned `MD_Hinges/README.md` прямо описывает каждый `.conf` как input restart file, содержащий structure and velocity data of an equilibrated hinge. Следовательно, формулировка NanoLab `equilibrated/restart structures` поддержана upstream.

## V4 — Known discrepancies remain unresolved correctly

### 298 K article vs 300 K upstream input

Primary ACS article DOI `10.1021/acsnano.7b00242` проверена live в этой verifier-сессии. Methods сообщает `298 K` и `500 mM Na+`, а секция `Simulation Codes and Data` прямо связывает статью с `gauravarya77/DNA-hinge-simulations` и перечисляет caDNAno designs, scripts, input options, topology/configuration files. Pinned `pro_CPU.in` независимо показывает `T = 300K`.

Candidate не подменяет одно значение другим: расхождение явно сохранено и передано в `NL0-003`. Это корректно.

### E2 rights

Полный pinned recursive tree из 33 entries не содержит `LICENSE`, `COPYING` или `NOTICE`. Candidate не выводит право redistribution из public visibility: rights остаются `UNKNOWN`, решение передано в `NL0-002`. PR #11 содержит только docs/json evidence; upstream `.top/.conf/.in/.dat` в NanoLab не скопированы.

### S08

Для DOI `10.1021/acsnano.7b06470` primary ACS Supporting Information live перечисляет PDF с definitions/additional simulation results и пять MPG movies. Bounded inspection не устанавливает существование публичного machine-input pack. Accepted manuscript также благодарит Carlos Castro за предоставление original caDNAno files. Поэтому корректный статус остаётся:

```text
INPUT_PACK_NOT_LOCATED
```

а не `NO_DATA_EXISTS`.

## V5 — Harness execution package

На exact candidate существуют `passport.json`, `summary.md`, `branch-passport.md` и ровно пять event files:

```text
0001 WORK_ORDER_STARTED
0002 CONTINUATION_CHECKPOINT
0003 IMPLEMENTATION_COMMITTED
0004 VALIDATION_RECORDED
0005 HANDOFF_COMPLETED
```

Текущий `scripts/harness/work_cli.py` независимо прочитан. Его predicates воспроизведены против live execution package:

- exactly one `WORK_ORDER_STARTED` — PASS;
- START first — PASS;
- exactly one terminal/handoff — PASS;
- terminal/handoff last — PASS;
- `execution_id == EX-NL0-001-R1` во всех events — PASS;
- `work_order_id == NL0-001` во всех events — PASS;
- все `subject_sha` соответствуют `^[0-9a-f]{40}$` — PASS;
- event ids unique и lexically ordered — PASS;
- event types/actor roles допустимы — PASS;
- `summary.md` существует — PASS.

Эквивалент `close` даёт:

```text
ok = true
errors = []
status = HANDOFF_READY
has_terminal_handoff = true
has_summary = true
```

Прямой запуск `./CONTROL_WORK.sh close ...` / `python3 scripts/harness/work_cli.py close ...` в clean clone в этой verifier-сессии выполнить не удалось: container DNS не разрешал `github.com`, поэтому clone завершался `Could not resolve host: github.com`. Это explicit environment limitation; PASS здесь относится к независимому воспроизведению exact current predicates и live package, а не к заявлению о выполненном shell-wrapper.

Также зафиксирован non-blocking harness detail: terminal event `subject_sha=dd5cef3c8bd7212c64da4c80fedb5ca03169eac9`, а финальный PR HEAD = `f738bff…`; текущий `work_cli.py` не требует их равенства. Это не нарушает нынешние predicates, но является разумным будущим harness hardening.

## V6 — Scientific state safety

Live `project/state.json` на candidate и current `main` одинаков по scientific state:

```text
frontier          = NL0
next_work_order   = NL0-001
NL0-001           = READY
completed_tasks   = []
stage_status.NL0  = PLANNED
E0–E6             = NOT_RUN
physics_runs      = 0
```

Candidate не заявляет `NL0=COMPLETE`, `E1=PASS` или `E2=PASS`; Implementer evidence говорит `HANDOFF CANDIDATE; independent review required`; passport status = `HANDOFF_READY`. Self-accept отсутствует.

## V7 — Epoch drift

Live compare:

```text
9d8ea394c6c037b0560908689e2ce932bf0c511c
→
f4d2979a1d2502d86c035f25e36961b4d5ac2764
```

даёт 6 commits / 12 changed files. Изменения ограничены INFRA/control-routing: `docs/infra/**`, `docs/work/WO-INFRA0-001.md`, `project/infra-plan.json`, `project/infra-state.json`, `docs/evidence/INFRA_ROADMAP_R1_CHECKS.md`, плюс routing edits в `AGENTS.md`, `PROJECT_CONTROL.md`, `README.md`, `docs/INDEX.md`.

Не изменены `docs/research/**`, `docs/work/WO-NL0-001.md`, `config/control/harness/**`, `project/state.json` и scientific experiment contracts. Reviewer уже проверял тот же `CURRENT_MAIN=f4d2979…`; после Reviewer нового затрагивающего drift нет.

```text
EPOCH_DRIFT = CONTINUE
```

## FINDINGS

1. Exact subject binding подтверждён: PR HEAD всё ещё равен REVIEWED_HEAD; review не stale.
2. Все четыре E1 SHA-256 независимо пересчитаны и совпадают; topology/input/oracle совпадают побайтово по смысловым полям.
3. E2 pinned tree и machine-input package подтверждены; CPU input = CPU/double/2e7/DNA2/0.5/300K; `.conf` документированы upstream как equilibrated restart structures.
4. Научные неопределённости не замаскированы: 298 K vs 300 K остаётся NL0-003, redistribution rights UNKNOWN остаётся NL0-002, S08 остаётся `INPUT_PACK_NOT_LOCATED`.
5. Harness package удовлетворяет текущим `work_cli.py close` predicates; scientific state не повышен и Implementer не self-accepted.
6. Epoch drift остаётся `CONTINUE`.

## LIMITATIONS

1. Clean-clone shell execution `CONTROL_WORK close` недоступен в этой сессии из-за container DNS (`Could not resolve host: github.com`); текущие predicates воспроизведены независимо по live exact files и дали `ok=true`.
2. E1 physics simulation не запускался — это прямо исключено verifier scope данного Work Order.
3. Ветка `verify/nl0-001-reference-selection-r1` уже существовала на direct-child commit `5582ad765d7e43f50f48f3764ca054ad45ea2a77`; вместо destructive reset/force-push опубликован новый superseding non-force evidence commit. Ancestry от exact candidate сохранена.

## Verdict

```text
VERDICT = PASS
NEXT_ACTOR = DIRECTOR
```

Verifier не merge'ил PR #11, не изменял candidate files, не обновлял `project/state.json` и не закрывал NL0.