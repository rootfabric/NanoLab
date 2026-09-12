# Director Acceptance R1 — NL3-002-PILOT (E2 pilot, calibration) — ACCEPTED

- Дата: 2026-09-12. Authority: владелец (миссия «делай следующий шаги» в контексте плана «Fresh Reviewer пилота → Director merge → E2-PROTO-R1»); Director-исполнение — координирующая сессия.
- Execution: `EX-NL3-002-PILOT-R1` @ exact HEAD `4d72ce0` (work/nl3-002-pilot-r1: eba4758 START → 82770d2 runs → 4d72ce0 records).
- Independent REVIEWER: **PASS** (10/10 проверок; F-1 LOW honest-error-entry, F-2 LOW reason-строка, F-3 INFO seed re-use в rate run) — `5d60f08`. Independence caveat зафиксирован (fresh-сессия, тот же физический хост).
- Coordination check (Director): ветка review получена с origin, дифф = ровно `REVIEWER_VERDICT.md`; WSL-дайджесты артефактов ранов сверены координатором независимо до review (`s001_traj.dat` `b8ca210a…`, `0b.top` `cd046127…`, `0b.conf` `506c41fc…` = пины/манифесты).

## Решение

**NL3-002-PILOT = ACCEPTED** как калибровочная фаза: campaign-level scientific_outcome = NOT_EVALUATED; E2 = NOT_RUN; claim ceiling C0_SOFTWARE_ONLY / non-confirmatory. Никакие числа пилота (lbf 0.054 frame 0, pairs 26–29, DRAFT-угол ~178.6°) не являются научными результатами — они кандидаты в `E2-PROTO-R1`.

## Принятые измеренные факты (вход в E2-PROTO-R1)

1. Per-step cost: ~0.052 s single / ~0.060 s (×3 parallel, contention 1.16×) на 8378 нуклеотидов; 2e7 steps ≈ 12 суток/реплику — full-length confirmatory локально нереалистичен без INFRA2.
2. Движок `00dc7fb9` совместим с авторским 2017-input (все раны exit 0).
3. v1 pairs-детекция неадекватна в масштабе (26–29 пар) → требуется `E2_OBSERVABLES_R2` (готовится в NL3-002-PROTO).
4. lbf ≈ 0.054 в frame 0 авторского конфига — baseline-факт против BOND_D_MAX = 1.0.
5. Findings F-1/F-2 LOW: приняты как процедуры для E2-PROTO (копировать все digest-gated входы в run-dir; точные reason-строки отклонений).

## Next action

Завершение NL3-002-PROTO (манифест рук + observables v2 + draft-tolerances) → Director freeze `E2-PROTO-R1` (включая решение владельца по длине/бюджету confirmatory) → confirmatory WO.
