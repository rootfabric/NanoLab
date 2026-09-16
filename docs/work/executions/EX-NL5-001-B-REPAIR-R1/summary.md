# EX-NL5-001-B-REPAIR-R1 — Summary / Handoff

## Result

`IMPLEMENTED / REVIEW_REQUIRED` (MEDIUM risk; физика не запускалась, canonical не менялся, научные числа не менялись).

Substantive subjects: серия repair-коммитов `repair/nl5-001-b-library-r1`
(base `work/nl5-001-b-library-assembly-r1 @ 6285265`), финальный batch `54d8e03`
+ checkpoint `af894ee`; exact review head — итоговый HEAD ветки (см. 0003-handoff-completed).
CI: run `34842747606` на `cb63d0b` был 4/5 (падал только Check 5);
run `34851421528` на `af894ee` — **5/5 gates green**.

## Что сделано (поверх реализованного R1.1–R1.2 объёма)

**Package regression layer закрыт** — последний красный hosted-гейт Check 5
устранён тремя хирургическими фиксами (R8):

1. **F-R8.1 manifest sync**: `releases/nanolab-components-v0.1` пересобран
   детерминированным R1.2 builder-ом (`release.build_library_r12 build`). Все 5
   карточек value-идентичны reviewed subject (проверено per-key: только
   детерминированная ре-сериализация); wall-clock `RELEASE_MANIFEST.json`
   (`generated_at_utc`, `release.card_lint manifest create`) заменён на
   детерминированный манифест без timestamp (`generated_by release.build_library_r12
   deterministic-r1.2`); упакованный `REPRODUCTION_RULE_V0_1.md` стал байт-идентичным
   frozen rule doc (`NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`).

2. **F-R8.2 D2-warning**: rights-warning линтера теперь явно называет блокирующий
   owner-гейт **D2** («public release blocked until D2») — соответствует контракту
   (публичный release запрещён до owner D2) и устоявшейся терминологии
   D2-warning в evidence map A.

3. **F-R8.3 stale planning refs**: литерал несуществующего execution-program
   документа убран из `WO-NL5-001-B-REPAIR-R1` (переформулировка scope) и из
   `program_reference` паспортов EX-NL5-001-A-R1 / EX-NL5-001-B-R1 — с
   corrections-блоками по протоколу F-B5 (оригинал redacted-описанием, дословные
   байты восстанавливаются из git-истории). **Неизменяемое START-событие
   EX-NL5-001-A-R1 не редактировалось** (hard rule); `tests/test_release_planning_refs.py`
   получил единственное исключение exact path + sha256 pin (прецедент hosted-ci
   Check 1) — любой дрейф байтов = fail closed.

## Валидации (локально на exact HEAD + hosted CI)

```text
python3 -m unittest discover -s tests -t .   -> Ran 360 tests, OK (было 3 fail)
release.build_library_r12 check              -> ok, два независимых full build байт-идентичны
release.card_lint package releases/...v0.1   -> ok (единственный ожидаемый D2-warning)
check-consistency / workflow_lint            -> ok, 0 blocking
work_cli validate docs/work/executions/EX-*  -> все 36 каталогов ok
hosted-ci run 34851421528 @ af894ee          -> Check 1..5/5 все success
```

## Open risks / границы

- исторический A остаётся superseded integrated B-repair (без изменения его фактов);
- публикация пакета по-прежнему заблокирована: **D2 (решение владельца по лицензии)** + NL5-001-D;
- `74b` остаётся `NOT_MEASURED / KNOWN_GAP`; arm-manifest-v2 — будущий bounded WO;
- никаких новых oxDNA/physics runs в ремонте не выполнялось.

## Next action

REVIEWER (fresh, independent): review exact HEAD `repair/nl5-001-b-library-r1`
(после push — итоговый HEAD этого handoff) + PR #40 compatibility; затем Fresh
Verifier и Human Gate. **NL5-001-C не запускать** до полностью зелёного гейта,
re-review и verifier pass.
