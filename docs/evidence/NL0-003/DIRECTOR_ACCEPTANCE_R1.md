# NL0-003 — Director Acceptance R1

Дата: 2026-09-08. Роль: `DIRECTOR`. Work Order: `NL0-003 — Preregister reference protocol`.

## Exact subjects

```text
BASE_MAIN                  = 81e299f1924e50bcff1bc5c893bccd934ef2883d
START_COMMIT               = 9372b79e1406ffd2d0853bcd3c8f2232062f737c
SOURCE_CHECK_COMMIT        = 53379e4973158e38531e346461d625b421f93cdf
SUBSTANTIVE_HEAD           = 9404a422166cb07efd98443a5f208f078a4ab2c4
SUBSTANTIVE_TREE           = b8b1bd992f15f9093ea4338255858e94d0bc06ad
PR_HEAD                    = 6e30aee73252c0cc88545cc675633448dd3aaee5
FRESH_REVIEWER_R1_EVIDENCE = 36c68e15f135c9b8141a9ce86283e4a2d50c612d (review/nl0-003-preregistration-r1)
FRESH_REVIEWER_R1_VERDICT  = PASS (0 BLOCKING / 2 MINOR)
FRESH_VERIFIER_R1_EVIDENCE = ecc5dabf53eb1de4d17d2b2dc0392aa2249fa09c (verify/nl0-003-preregistration-r1)
FRESH_VERIFIER_R1_VERDICT  = PASS
CHECKPOINT_PROPOSAL        = ebafd1e42b5b60b78d7c6484b1942cadea248b97 (control/nl0-003-director-checkpoint-r1)
MERGE_COMMIT               = 678be065067e41b14a11a71269b6fbf1c46581e1
```

Human merge gate был явно разрешён владельцем в сессии («хорошо публикуй») перед merge. PR #21 объединён GraphQL-мутацией с race-guard `expectedHeadOid = 6e30aee7…`; `origin/main` оставался на `BASE_MAIN` вплоть до merge — race между verification и merge не допущен.

## Review history preserved

Fresh Reviewer R1 (PASS, 0 blocking): критерии E1 зафиксированы до кампании (verbatim upstream-оракул, не выбор NanoLab); пилот-дисциплина `R_confirm` корректна (PILOT ≠ доказательство, freeze до confirmatory, без уменьшения после старта); семантика исходов различена, пути тихого ретрая нет; 298 K vs 300 K решён научным decision rule без замалчивания; число повторов/целевой угол/точность не выдуманы; нигде не заявлено, что E1/E2 выполнены.

MINOR findings сохранены с dispositions (не блокируют candidate):

1. §6.1 `PREREGISTRATION_E1_R1.md`: тезис «seed-разброс встроен в смысл upstream-полосы» — интерпретация (ASSUMED), подана под REPORTED/OBSERVED-рубрикой; критерий T1 не затронут → маркировка ASSUMED переносится в `E1-PROTO-R2` (первая ревизия перед кампанией).
2. `IMPLEMENTER_EVIDENCE.md` называет SUBSTANTIVE_HEAD = `34508669…`, авторитетный binding (event 0005, branch-passport, summary) = `9404a42…` — следствие самоссылочности evidence-коммита, противоречия по существу нет → авторитетен terminal binding.

Fresh Verifier R1 (PASS): 4/4 SHA-256 и 4/4 git blob upstream входов совпали независимо; verbatim-цитаты `quick_input`/`quick_compare` подтверждены; binding `9404a42…`/tree `b8b1bd99…` подтверждён; diff внутри allowed_paths; `state.json`/`plan.json`/policies не тронуты; JSON соответствует схемам; контролы exit 0; числа без трассировки не найдены. INFO: §3 — нормализованная расшифровка при байт-точном эталоне (SHA-256) — допустимо протоколом.

## Director decision

```text
RISK_CLASS       = HIGH
CLAIM_CLASS      = C0_SOFTWARE_ONLY
REVIEWER_R1      = PASS
VERIFIER_R1      = PASS
EPOCH_DRIFT      = CONTINUE
DIRECTOR_VERDICT = ACCEPTED
```

## Канонически принятые результаты

### E1

```text
E1_PROTOCOL = E1-PROTO-R1 PREREGISTERED (docs/research/PREREGISTRATION_E1_R1.md)
subject     = oxDNA DSDNA8/MD @ 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (GPL-3.0, DOWNLOAD_ON_SETUP)
conditions  = verbatim quick_input; observable = ColumnAverage(energy.dat, col 2)
criterion   = upstream quick_compare: -1.37970256144 ± 0.15 (существует до кампании, не подгоняется)
statistics  = T1 upstream-equivalent + T2 robustness; R_confirm через pilot(3) -> freeze в E1-PROTO-R2
outcomes    = SUPPORTED / NOT_SUPPORTED / FAILED_TECHNICAL / INCONCLUSIVE / BLOCKED_ENVIRONMENT зафиксированы
claim ceiling будущей кампании = C1_COMPUTATIONAL_REPRODUCTION
```

Запуск E1 — NL1-002 (первый вертикальный путь) и NL2-002 (научная приёмка). Engine pin — NL1-001; measured budget — первый прогон.

### E2

```text
E2_SETUP   = E2-SETUP-R1 (docs/research/E2_SETUP_R1.md), кампания NOT_RUN
first hinge= 0b (baseline)
angle      = определение ТОЛЬКО из спиненного SI перед E2-PROTO; reconstruct ≠ original
298K-vs-300K = decision rule: reproduction arm = авторские inputs verbatim (300K); расхождение
             документируется в каждом отчёте; paper-fidelity arm (298K) — отдельная preregistered revision
family     = только пять опубликованных вариантов 0b/11b/32b/53b/74b
hard deps  = права DNA-hinge-simulations (owner decision), методология E0/E1 (NL2), engine pin (NL1-001)
```

### Simulations

```text
E0..E6 = NOT_RUN; physics_runs = 0; ai_campaigns = 0
```

Завершённый протокол — не выполненный E1: пререгистрация не создаёт scientific evidence.

## State transition

Каноническое состояние после этого acceptance record:

```text
frontier        = NL1
NL0             = ACCEPTED
NL1             = IN_PROGRESS
NL0-001/002/003 = ACCEPTED
NL1-001         = READY
next_work_order = NL1-001 (pin environment and upstream smoke)
E0..E6          = NOT_RUN
physics_runs    = 0
```

`NL0` закрыт по checkpoint-catalog: references ✓ (NL0-001), access/rights ✓ (NL0-002), preregistered E1 scope + E2 постановка ✓ (NL0-003) — всё durable в `main`.

## Open owner decisions preserved

1. Выбрать лицензию NanoLab для code/docs/data.
2. Получить явную лицензию/permission для `DNA-hinge-simulations` (контакт авторов) либо заменить E2 seed до NL3.
3. Определить policy durable private caching для UNKNOWN-rights files.
4. Перед release architecture отдельно оценить same-process `oxpy` integration.

Обновление: расхождение 298 K vs 300 K более не open decision — закрыто decision rule'ом E2-SETUP-R1 §5; E1 tolerances пререгистрированы. Остаются: E2 tolerances/пороги целостности и целевой интервал угла (E2-PROTO после пилота), спиннинг SI, engine/build versions и measured budget (NL1-001 и первые прогоны).

## Final

```text
NL0-003 = ACCEPTED
NL0     = ACCEPTED
NEXT    = NL1-001
```
