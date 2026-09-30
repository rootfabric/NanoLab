# DIRECTOR_ACCEPTANCE_R2 — Addendum к Director Acceptance R1 (EX-NL5-002-E-R1)

Статус: **ADDENDUM (append-only)**. Не изменяет и не переписывает
`DIRECTOR_ACCEPTANCE_R1.md`. Дата: 2026-09-27. Автор: Director (mission 2026-09-27).

```text
PLATFORM-SENSITIVITY-R1 = FULLY VERIFIED
WO OUTCOME              = PLATFORM_INSENSITIVE (unchanged, frozen)
P1 RAW GAP              = CLOSED
```

## 1. Что закрывает этот addendum

Единственный открытый пункт `DIRECTOR_ACCEPTANCE_R1.md` — delegated P1 raw replay.
Он исполнен делегированным оператором на P1-машине (DESKTOP-QNAGSTI, WSL2) строго
по авторитетной инструкции fresh Verifier
`docs/evidence/NL5-002-E/P1_RAW_REPLAY_COMMANDS_R1.md` и опубликован событием
`0008-continuation-p1-raw-replay-verified.json` на
`work/nl5-002-e-platform-sensitivity-r1`:

```text
P1_RAW_REPLAY_HEAD = f9ff8cae5203b90f0698e81fdd64867c2e53aac2
P1_RAW_REPLAY_TREE = 9fd58d2d82b00a1eac21a3227d789ab1fab78a7c
```

## 2. Результаты raw replay (из event 0008)

```text
P1_RAW_HASH_REPLAY    = 60/60 PASS   (20 финалов x trajectory/hinge_energy/last_conf;
                                     двойная сверка: run_output_digests_p1.json И
                                     таблица инструкции — источники AGREE)
P1_RAW_SIZE_REPLAY    = 60/60 PASS
P1_RAW_ANALYSIS_REPLAY = 20/20 PASS  (packaged analyzer nanolab-components 0.1.1
                                     convention/analyze_hinge.py sha256 300ecd58…;
                                     regen==committed bit-exact по
                                     replica_median_deg на всех 20)
MEDIAN_MISMATCHES     = 0
NEW_PHYSICS_RUNS      = 0
SCIENTIFIC_PROTOCOL_MUTATION = NONE
```

Задокументированные нотационные наблюдения (не mismatches):
- 2 значения (S004, S008) в таблице инструкции записаны с trailing-zero паддингом
  до 9 знаков (66.246738850 / 67.615802220) против JSON-сериализации
  (66.24673885 / 67.61580222) — числа равны точно; оба представления опубликованы.
- Единственное структурное отличие regen-отчётов от committed-копий — поле seed
  (packaged analyzer пишет seed:null; в committed-копиях seed инжектирован
  evidence-драйвером кампании — документированный прецедент event 0004 /
  PAIRED_PROVENANCE.md).

## 3. Независимая верификация

```text
verify session = verify/nl5-002-e-p1-raw-replay-r1 (fresh, без контекста имплементёра)
verifier bind  = exact P1_RAW_REPLAY_HEAD/TREE выше (matched exactly)
verifier record = docs/evidence/NL5-002-E/FRESH_RAW_REPLAY_VERIFY_R1.md
verifier head  = 9e6200a9cf0a265305308acecba157601a419c46
verifier tree  = a32301376795d49289d3465c3a440a6b7e058d11
verdict        = VERIFIED (все 5 проверок PASS, независимо: append-only event 0008;
                 hash 60/60 + size 60/60 против обоих источников собственной
                 рекомпутацией; median 20/20 bit-exact packaged-анализатором;
                 нет protocol mutation / новых physics; paired result unchanged
                 exact float equality; NL5/NL6 границы не тронуты)
```

## 4. Неподвижность научного результата (механическая сверка, не пересчёт)

Committed `evidence/paired/paired_platform_sensitivity.json` содержит ровно:

```text
0b : shift = +0.6846952455000022 ; CI95 = [-0.5502640344999961, +1.199043819]
     -> PLATFORM_INSENSITIVE
32b: shift = -1.207386400499999 ; CI95 = [-2.090432681000003, +2.1491488160000074]
     -> PLATFORM_INSENSITIVE
WO = PLATFORM_INSENSITIVE
```

Scientific result не изменён; statistics/протокол не мутировали; новые runs/retries/
seeds отсутствуют; raw trajectories остаются вне Git (WSL2 FS), append-only.

## 5. Границы

- NL5 = IN_PROGRESS; NL6-001 = LOCKED; external_reproductions = 0 — без изменений
  (решается отдельно NL5-ACCEPTANCE-POLICY).
- С этого момента — execution policy owner decree: новые scientific physics на
  Windows/WSL2 НЕ запускаются (см. параллельную инфраструктурную линию
  WO-NATIVE-UBUNTU-EXECUTOR-R1: native Ubuntu R2, outenemy = external repro,
  Windows = historical only).
