# NL0-003 — Director Checkpoint Proposal R1

Дата: 2026-09-08. Роль: `DIRECTOR` (routing checkpoint proposal, не ACCEPTED). Work Order: `NL0-003 — Preregister reference protocol`. Merge в `main` — **Human Gate**; настоящий документ предлагает владельцу решение, но не принимает его.

## Exact subjects

```text
BASE_MAIN                = 81e299f1924e50bcff1bc5c893bccd934ef2883d
START_COMMIT             = 9372b79e1406ffd2d0853bcd3c8f2232062f737c
SOURCE_CHECK_COMMIT      = 53379e4973158e38531e346461d625b421f93cdf
SUBSTANTIVE_HEAD         = 9404a422166cb07efd98443a5f208f078a4ab2c4
SUBSTANTIVE_TREE         = b8b1bd992f15f9093ea4338255858e94d0bc06ad
HANDOFF_COMMIT / PR_HEAD = 6e30aee73252c0cc88545cc675633448dd3aaee5 (только event 0005 + статусы)
PR                       = #21 (draft) work/nl0-003-preregister-reference-protocol-r1
FRESH_REVIEWER_R1        = 36c68e15f135c9b8141a9ce86283e4a2d50c612d (review/nl0-003-preregistration-r1)
FRESH_VERIFIER_R1        = ecc5dabf53eb1de4d17d2b2dc0392aa2249fa09c (verify/nl0-003-preregistration-r1)
EPOCH_DRIFT              = CONTINUE (origin/main == BASE_MAIN на момент proposal)
```

## Review history

```text
FRESH_REVIEWER_R1_VERDICT = PASS (0 BLOCKING, 2 MINOR)
FRESH_VERIFIER_R1_VERDICT = PASS (8/8 SHA-256+blob MATCH, verbatim MATCH, binding/scope/schema/controls OK,
                             числа без трассировки: не найдены)
```

Routing по risk-policy HIGH выполнен: независимый REVIEWER → независимый VERIFIER → Director proposal. Implementer ACCEPTED не выставлял; `state.json`/`plan.json` не менялись.

## Каноническое содержимое candidate

- `E1-PROTO-R1` (`docs/research/PREREGISTRATION_E1_R1.md`): PREREGISTERED, не выполнен. Subject: oxDNA DSDNA8/MD @ pinned `00dc7fb9…` (GPL-3.0, DOWNLOAD_ON_SETUP, 4/4 SHA-256 re-verified). Условия verbatim из `quick_input`; observable = ColumnAverage(energy.dat, col 2) против upstream-оракула `quick_compare` `-1.37970256144 ± 0.15`; T1 upstream-equivalent + T2 robustness; пилот(3) → freeze `R_confirm` в `E1-PROTO-R2`; семантика исходов зафиксирована до данных; UNKNOWN-реестр (engine defaults, семантика колонки 2, engine pin, measured budget) с процедурами закрытия.
- `E2-SETUP-R1` (`docs/research/E2_SETUP_R1.md`): постановка, кампания NOT_RUN. Первый шарнир `0b`; определения угла/целостности — только из спиненного SI (числа не выдуманы); decision rule 298 K vs 300 K: reproduction arm = авторские inputs verbatim (300 K), расхождение документируется в каждом отчёте; family = пять опубликованных вариантов; hard dependencies: права `DNA-hinge-simulations` (owner decision), методология E0/E1 (NL2), engine pin (NL1-001).
- Научные симуляции не запускались: `E0–E6 = NOT_RUN`, `physics_runs = 0`. Завершённый протокол — не выполненный E1.

## Findings и dispositions (не блокируют candidate)

| # | Источник | Finding |Disposition |
|---|---|---|---|
| 1 | Reviewer MINOR | §6.1 E1-PROTO-R1: тезис «seed-разброс встроен в смысл upstream-полосы» — интерпретация (ASSUMED), подана под REPORTED/OBSERVED-рубрикой; критерий T1 не затронут | Зафиксировать маркировку ASSUMED в `E1-PROTO-R2` (первая ревизия перед кампанией); candidate принимается как есть |
| 2 | Reviewer MINOR | `IMPLEMENTER_EVIDENCE.md` называет SUBSTANTIVE_HEAD = `34508669…`, авторитетный binding (event 0005, branch-passport, summary) = `9404a42…` — следствие самоссылочности evidence-коммита; противоречия по существу нет | Авторитетен terminal binding `9404a42…`; помечено для будущей docs-ревизии без изменения substantive |
| 3 | Verifier INFO | §3 E1-PROTO-R1 — нормализованная расшифровка без `#debug`/`#pt`; байт-точный эталон = upstream-файл по SHA-256 | Допустимо протоколом: расшифровка объявлена производной, эталон — pinned файл |

## Proposed state transition (применяется владельцем при merge, не ранее)

```text
NL0-003 = ACCEPTED
NL0     = ACCEPTED (checkpoint-catalog: references ✓ NL0-001; access/rights ✓ NL0-002;
          preregistered E1 scope + E2 постановка ✓ NL0-003 — durable)
frontier / next_work_order = NL1 / NL1-001 (pin environment and upstream smoke)
E0..E6  = NOT_RUN; physics_runs = 0 (не меняются)
```

Открытые owner decisions сохраняются без изменений: лицензия NanoLab; права `DNA-hinge-simulations` (или замена seed); policy private caching UNKNOWN-rights файлов; same-process `oxpy` оценка перед release architecture.

## Requested decision (Human Gate)

1. Разрешить merge PR #21 в `main` с guard `expected_head_sha = 6e30aee73252c0cc88545cc675633448dd3aaee5`.
2. Подтвердить proposed state transition выше (либо скорректировать).
3. Определить приоритет NL1-001 и судьбу E2 owner-запроса авторам.

До явного разрешения владельца merge не выполняется; `ACCEPTED` не выставляется.
