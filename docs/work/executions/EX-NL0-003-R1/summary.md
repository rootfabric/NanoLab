# EX-NL0-003-R1 — Summary

```text
BASE_SHA = 81e299f1924e50bcff1bc5c893bccd934ef2883d
HEAD     = см. binding ниже
TREE     = фиксируется terminal event 0005 и PR (candidate head)
```

## Binding (hardening: terminal event ↔ final handoff HEAD)

```text
START_COMMIT         = 9372b79e1406ffd2d0853bcd3c8f2232062f737c  (harness: start)
SOURCE_CHECK_COMMIT  = 53379e4973158e38531e346461d625b421f93cdf  (research: checkpoint source re-verification)
IMPLEMENTATION_COMMIT= 3450866925ce49fc81ee658806d3ec81b2e1bc81  (research: preregister E1 protocol R1 and E2 setup R1)
SUBSTANTIVE_HEAD     = коммит, непосредственно предшествующий terminal event
                       (содержит все substantive артефакты включая этот summary);
                       exact SHA записан в 0005-handoff-completed.subject_sha
HANDOFF_COMMIT       = единственный коммит ПОСЛЕ terminal event; содержит только
                       0005-handoff-completed.json + статус passport/branch-passport;
                       substantive результат не меняет
```

## Параметры

```text
WORK_ORDER = NL0-003 (docs/work/WO-NL0-003.md, из issue #4)
RISK       = HIGH (scientific_protocol / observable_definition / acceptThreshold → Reviewer+Verifier+Director)
CLAIM      = C0_SOFTWARE_ONLY (протокол не является научным claim; E1-кампания потолок C1)
```

## Результаты

```text
E1_PROTOCOL = E1-PROTO-R1 PREREGISTERED (docs/research/PREREGISTRATION_E1_R1.md)
  subject   = oxDNA DSDNA8/MD @ 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591, 4 файла SHA-256 verified (4/4 MATCH)
  условия   = verbatim quick_input (CPU, 1e6 steps, thermostat john, T 20C, dt 0.005, ...)
  observable= ColumnAverage(energy.dat, col 2) vs upstream oracle -1.37970256144 ± 0.15 (quick_compare verbatim)
  статистика= T1 upstream-equivalent + T2 robustness; R_confirm через pilot(3) → freeze в E1-PROTO-R2
  исходы    = SUPPORTED / NOT_SUPPORTED / FAILED_TECHNICAL / INCONCLUSIVE / BLOCKED_ENVIRONMENT зафиксированы
E2_SETUP    = E2-SETUP-R1 (docs/research/E2_SETUP_R1.md)
  first hinge = 0b (baseline), права UNKNOWN → REFERENCE_ONLY, hard deps: owner decision + NL2 + NL1-001
  298K-vs-300K= decision rule: reproduction arm = авторские inputs verbatim (300K); расхождение документируется
  family    = 0b/11b/32b/53b/74b только; angle/integrity определения — из спиненного SI, не из памяти
NOT_INVENTED= R_confirm, целевой угол E2, tolerances E2, engine version, measured budget, SI-геометрия
```

## Validation

```text
python -m json.tool (passport, events 0001-0003, state.json, plan.json) -> 6/6 OK
CONTROL_DEVELOPMENT.ps1 -CheckConsistency  -> ok=true, errors=[], warnings=[], exit 0
CONTROL_WORK.ps1 validate (pre-handoff)    -> ok=true, errors=[]
CONTROL_WORK.ps1 close (после terminal)    -> см. ниже / PR
```

## Ограничения

- Пререгистрация — документ, не evidence запуска: E1/E2 остались NOT_RUN, physics_runs = 0.
- UNKNOWN-реестр протокола принципиально не закрыт в NL0: engine pin — NL1-001, R_confirm — E1-PROTO-R2 после пилота, семантика колонки 2 — header первого прогона.
- E2 структурно заблокирован: rights (owner decision), SI pinning, compatibility audit 2017-scripts, методология E0/E1.
- transient raw.githubusercontent 404 в ходе проверки входов устранён повтором/переключением на contents API; итоговые SHA-256 верифицированы.

## Факты для аудита

```text
THIRD_PARTY_FILES_COPIED = NONE (загрузки во временный каталог ОС; в репозитории только refs/hashes/метаданные)
SIMULATIONS_RUN          = NONE (E0–E6 NOT_RUN, physics_runs = 0)
project/state.json       = не изменён Implementer'ом
ACCEPTED                 = не выставлен (HIGH: Reviewer → Verifier → Director; merge — Human Gate)
```

## NEXT_ACTOR

```text
NEXT_ACTOR = REVIEWER, затем VERIFIER (HIGH-risk routing по risk-policy).
Reviewer: критерии не подогнаны? REPORTED/ASSUMED/UNKNOWN разделены? пилот-процедуры корректны?
Verifier: exact subject/SHA-256/verbatim-цитаты/отсутствие выдуманных значений по exact HEAD.
Director: checkpoint proposal; merge PR — Human Gate (без явного разрешения владельца не выполняется).
```
