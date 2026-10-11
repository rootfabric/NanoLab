# Summary — EX-INFRA3-R2-TOOLING-REPAIR-R1

WO: `WO-INFRA3-R2-TOOLING-REPAIR-R1` · ветка:
`infra/u2-outenemy-executor-readiness-r1` (общая с
`WO-INFRA3-U2-OUTENEMY-READINESS-R1`; история и START checkpoint родителя
сохранены, append-only) · base main `8bf7e3a` · implementation commit
`b87d61d1a101e8b85415a079288efa46384be201` · 0 scientific runs ·
claim ceiling C0_SOFTWARE_ONLY.

## Что сделано

1. **Scope-repair по решению владельца** (mission «NL5 U2 Integration &
   Narrow Repair», шаг 1.2): правки tooling F-1/F-2/F-3 в `scripts/r2/*`,
   `tests/*`, выполненные в родительской ветке 2026-10-10, получили явное
   bounded WO-покрытие настоящим execution — без ретро-редактирования
   родительского паспорта и его START события (расхождение документировано
   отдельным CONTINUATION-событием родителя).
2. **F-4**: `resolve_engine_binary` — неоднозначные case-insensitive
   совпадения в `<build>/bin` → fail-closed `FileNotFoundError` с перечнем
   совпадений (произвольный выбор первого файла исключён; provenance обязан
   связывать ровно один binary). +3 теста.
3. **U2 executor path `r2.cli run-u2`** — отдельный безопасный путь для
   будущего U2-dispatch:
   - host-role gate `validate_u2_host` (+`PINNED_U2_HOSTNAMES`): только
     закреплённая U2-платформа, тот же native platform floor, host обязан
     оставаться не-U1-eligible; неизвестный hostname → `BLOCKED_HOST_U2`
     (exit 2);
   - обязательная dispatch authority: без `--dispatch-authority` →
     `BLOCKED_NO_DISPATCH_AUTHORITY` (exit 3); с ней — полная schema-v3
     валидация `nanolab_v02_dispatch_authority` через
     `build_execution_plan` (Git-bound lifecycle S → F → D/R/V → A);
   - launch gate: не-fixture план никогда не исполняется
     (`BLOCKED_LAUNCH_GATE_PROTECTED_WRITER`, exit 3);
     `machine_launch_authorized` всегда false — Human/Protected-Writer gate
     CLI не подменяет;
   - fixture ceiling: только `synthetic_test_fixture_only`-планы; spec
     обязан объявлять `fixture:true`; execution id замороженной кампании
     (`EX-NL5-REPRO-V0-2*`) → жёсткий отказ;
   - ledger append-only; `scientific_outcome = NOT_EVALUATED` всегда.
   +8 тестов, включая e2e fixture dispatch на синтетическом временном
   Git-репозитории.
4. **U1 guard НЕ ослаблен**: `run`/`build-engine`/`gate`/`nc-verify`
   продолжают требовать `validate_native_u1`; родной негативный контроль на
   этой машине повторно подтверждён (`r2.cli run` на outenemy → exit 2
   BLOCKED_HOST).

## Валидация (host outenemy, 2026-10-11)

- `python3 -m unittest discover -s tests -t .` → **630 OK** (612 base + 18
  новых: F-4 ×3, `validate_u2_host` ×7, `run-u2` ×8).
- Нативная (без инъекции fingerprint) e2e проба `run-u2` на disposable
  fixtures → exit 0, RECORDED, COMPLETED / NOT_EVALUATED, ledger записан;
  негативные контролы: без authority → exit 3; `run` (U1) на outenemy →
  exit 2. Evidence:
  `evidence/tooling-repair-validation-R1.json`,
  `EX-INFRA3-U2-OUTENEMY-READINESS-R1/evidence/u2-dispatch-fixture-selftest-R1.json`.
- `work_cli validate` (этот execution) → ok; `check-consistency` → ok;
  `workflow_lint` → blocking=0 (см. handoff event / review request).

## Границы (не изменены)

R2 = WAITING_HOST / NOT_ACTIVE · AUTHOR_U1 = NOT_ASSIGNED · NL5 =
IN_PROGRESS · SCIENTIFIC_RUNS = 0 · F2/frozen artifacts не тронуты · real
dispatch authority НЕ создавался · merge = Human Gate (PR #55).

## Open risks / honest limits

- `run-u2` сегодня исполняет ТОЛЬКО синтетические technical fixtures;
  systemd-transient launcher остаётся argv-проверенным без проводки реального
  исполнения (предмет frozen WO кампании).
- Реальный U2-leg кампании закрыт до R2 ACTIVE + real dispatch authority v3 +
  Human Protected Writer Gate.

## Next action

Fresh independent Reviewer на exact branch HEAD/TREE → narrow repair при
находках → fresh independent Verifier на финальный exact HEAD/TREE
(mission шаг 1.7); merge остаётся Human Gate.
