# DIRECTOR_ACCEPTANCE_R1 — WO-NL5-002-E-R1 (PLATFORM-SENSITIVITY-R1)

Дата (UTC): 2026-09-26 (authoritative `date -u` при записи). Роль: DIRECTOR record
по мандату миссии (Human Gate для этой миссии был pre-approved в dispatch-решении;
merge в main остаётся отдельным Human Gate).

## OUTCOME (единственное значение по §28)

```text
PLATFORM_INSENSITIVE
```

## Frozen decision chain (всё верифицировано fresh-ролями)

```text
preregistration  : WO-NL5-002-E-R1 @ 4d6542f (tree 7651569a), freeze + review 1f8c063 + verify bd25baf (до данных)
execution START  : 8e6a1b2 (passport frozen pre-data)
P1 leg           : eb8ccf0 - P1 complete 20/20 (tree c5a7c6e4)
P2 leg           : dispatched cabdb56, complete 5ef6c1c (tree cce8c0a0)
paired analysis  : 3941d27 - END_ANALYSIS (tree 9bc0275a)
FRESH REVIEWER   : PASS  @ c14759a (FRESH_PAIRED_REVIEW_R1.md; независимый bit-exact пересчёт,
                    P2 raw replay 20/20, findings F-1..F-6 нематериальны)
FRESH VERIFIER   : VERIFIED @ a2f1f57 (FRESH_PAIRED_VERIFY_R1.md; append-only chain,
                    отсутствие мутаций протокола, 60/60 P2 raw hash-совпадений,
                    парность 10+10, вербатим-аудит статистики, NC1-NC4 PASS,
                    тройное bit-exact воспроизведение)
```

## Verified numbers (per variant; тройное bit-exact совпадение)

```text
0b : shift_v = +0.6846952455000022 deg ; CI95 = [-0.5502640344999961, +1.199043819] (contains 0)
     MAD_P1 = 1.101103671500006 ; MAD_P2 = 1.4081993214999997 ; within_v = 1.2546514965000028
     ratio_v = 0.5457254444043144 ; verdict = PLATFORM_INSENSITIVE (branch: CI contains 0)

32b: shift_v = -1.207386400499999 deg ; CI95 = [-2.090432681000003, +2.1491488160000074] (contains 0)
     MAD_P1 = 1.299773310500001 ; MAD_P2 = 0.5319497240000004 ; within_v = 0.9158615172500006
     ratio_v = 1.3183067284291425 ; verdict = PLATFORM_INSENSITIVE (branch: CI contains 0;
     ratio >= 1 сам по себе недостаточен по frozen rule)

WO-level: 0b INSENSITIVE AND 32b INSENSITIVE -> PLATFORM_INSENSITIVE
```

## Заявленные отклонения исполнения (научный протокол не мутирован — проверено Verifier)

1. **Ранний P2 dispatch** (2026-09-21T21:25Z, Director override после P1 hard-kill deadline):
   задокументирован в DISPATCH_GATE.md / passport_p2 / event 0004; Reviewer F-1/F-2
   (расхождение времени 19:25/19:26Z vs 21:25Z в записях) — нематериально.
2. **P1 WSL-терминация 2026-09-20 ~21:28Z** (внешний CI-runner `wsl --shutdown`):
   recovery 2026-09-25..26 append-only retry-цепочками (-R1..-R21, 8 слотов,
   114 superseded-попыток сохранены перечислены в manifest); seeds/steps/engine/
   package/analyzer неизменны в каждой попытке; ни один exit=0 прогон не перезапускался;
   классификация только по exit-кодам и полноте артефактов (RECOVERY_INCIDENTS.md).
   Reviewer: канал для научной селекции отсутствует; paired-инференция не нарушена.
3. **P2 `seed:null` в analysis JSON** — принятый precedent B-R2 (анализатор не получает
   engine seed); привязка seed идёт через runmap + digest manifest (Verifier: PASS).

## OPEN ITEM (делегированная верификация)

```text
P1 raw replay на авторской машине (DESKTOP-QNAGSTI) — OPEN.
Подготовлен пакет: docs/evidence/NL5-002-E/P1_RAW_REPLAY_COMMANDS_R1.md
(точные команды packaged-analyzer для 20 финальных P1-прогонов + ожидаемые
sha256/size траекторий и ожидаемые replica_median_deg). P1-сессия может закрыть
пункт однократным выполнением; закрывающая запись — новым append-only event.
```

## Границы (§24, §29)

- Вердикт НЕ зависит от старого v0.1 envelope (MATCH/MISMATCH) — отдельный experiment.
- `NL5 != ACCEPTED` автоматически: `NL5-ACCEPTANCE-POLICY` остаётся отдельным решением.
- `external_reproductions = 0`.
- `NL6-001 = LOCKED` до отдельного canonical NL5 acceptance.
- Merge в `main` — Human Gate.
