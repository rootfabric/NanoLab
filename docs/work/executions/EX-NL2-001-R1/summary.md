# Execution Report EX-NL2-001-R1

## Identity
- Work Order: NL2-001 «Реализовать схемы, manifest и E0»
- Checkpoint: NL2
- Branch: `work/nl2-001-contracts-e0-r1`
- Base SHA: `15a2c9b1b5c095e24e2e1c24afd77feef5361102`
- Final HEAD: `24352f9dcc54e77472bdb8db827d2dc1fd0e1a1e` (subject кампании E0-R4: `ce477aad1e4a125c9e881fd9f6a741ec6d2fa876`)
- Risk / claim class: MEDIUM / C0_SOFTWARE_ONLY

## START
- Start commit: `609d4a3fb77a7125904ae17c6a215926dc3e9f8c` (WO + passport + event 0001, push до substantive work)
- Passport: [passport.json](passport.json) (+ [branch-passport.md](branch-passport.md))
- Initial scope: пререгистрация E0; контрактный формат evidence (NL1-002 R2); E0 — отрицательные/геометрические тесты, единицы, статусы

## CONTINUATION
| Event | HEAD (коротко) | Result/evidence | Next action |
|---|---|---|---|
| 0001-work-order-started | 15a2c9b (base) | scope, epoch drift (origin/main a4533ab, CONTINUE), маршрут | freeze кампании |
| 0002-continuation-checkpoint | 24352f9 | E0 за 4 попытки: R1 18×FAILED_TECHNICAL (emit repo-root), R2 17×FAILED_TECHNICAL (materialize пути + campaign_id), R3 erratum (неполные поддеревья фикстур; S003 KeyError), R4 исполнена: 17 SUPPORTED + S003 NOT_SUPPORTED (gap сохранён); все попытки в evidence | финальные валидации |
| 0003-validation-recorded | 24352f9 | experiment_cli 18/18 ok; work_cli EX ok (pre-terminal); check-consistency ok; jsonschema на всех контрактных JSON | terminal handoff |
| 0004-handoff-completed | 24352f9 | handoff независимому REVIEWER | review |

## END
- Implementation status: IMPLEMENTED (пререгистрация E0 + контрактный формат evidence + исполненный E0)
- Validation: `python -m harness.work_cli validate docs/work/executions/EX-NL2-001-R1` → ok=true; `close` (после терминального события, на терминальном коммите) → см. ниже; `python -m harness.experiment_cli validate` всех 18 run-каталогов E0-R4 → ok=true/0 warnings/exit 0; `python -m harness.cli check-consistency` → ok=true exit 0; jsonschema-валидация всех контрактных JSON кампании (Draft 2020-12 + FormatChecker) → чисто
- Experiment campaigns: E0-R4 — 18/18 COMPLETED; **17 SUPPORTED, S003 NOT_SUPPORTED** (preregistered gap-проба: technical RUN_COMPLETED с scientific_outcome=SUPPORTED принимается валидатором тихо → механическое разделение статусов отсутствует); campaign-level scientific_outcome = **NOT_EVALUATED**
- Review: не проводился (implementer не self-accept); next action — независимый REVIEWER
- Failed/inconclusive work: попытки E0-R1 (18× FAILED_TECHNICAL), E0-R2 (17× FAILED_TECHNICAL), E0-R3 (erratum: 8 случаев на неполных поверхностях) — ВСЕ сохранены в evidence с причинами; run ID не переиспользовались; ожидания не менялись с E0-PROTO-R1
- Remaining risks: (1) gap S003 — кандидат на validator hardening (NL2-003); (2) crash-валидаторы fail-closed, но некрасивы (exit 1); (3) одна инструментальная среда (Windows/Py3.11.8); (4) engine-coupled случаи E0 — после runtime
- Handoff event: `0004-handoff-completed`
- One next action: независимый REVIEWER — fresh-сессия, exact HEAD `24352f9`, evidence: `experiments/evidence/E0/E0-R4/**` + `docs/evidence/NL2-001/IMPLEMENTER_EVIDENCE.md` → `docs/evidence/NL2-001/REVIEWER_VERDICT.md`; merge — Human Gate

## Финальные команды валидации (терминальный коммит)
```text
PYTHONPATH=scripts python -m harness.work_cli validate docs/work/executions/EX-NL2-001-R1   -> ok=true, exit 0
PYTHONPATH=scripts python -m harness.work_cli close    docs/work/executions/EX-NL2-001-R1   -> ok=true, exit 0
PYTHONPATH=scripts python -m harness.cli check-consistency --root .                          -> ok=true, exit 0
```
(исполнены на рабочем дереве, байт-идентичном терминальному коммиту; самореферентный SHA текущего коммита в файлы не вносится — соглашение SESSION_LOG)
