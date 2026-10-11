# Work Order WO-INFRA3-R2-TOOLING-REPAIR-R1 — Bounded tooling repair R2-activation tooling (сопровождает WO-INFRA3-U2-OUTENEMY-READINESS-R1; 0 scientific runs)

Статус: **IN_PROGRESS** (execution `EX-INFRA3-R2-TOOLING-REPAIR-R1`, ветка
`infra/u2-outenemy-executor-readiness-r1` — ОБЩАЯ с родительским WO
`WO-INFRA3-U2-OUTENEMY-READINESS-R1`; base `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad`
= canonical main HEAD / merge PR #52; START checkpoint фиксирует фактический
состояние ветки на момент открытия, история ветки сохранена полностью,
append-only). Track: INFRA. Risk: **MEDIUM** (исполнительный tooling R2-ноги).
Claim ceiling: **C0_SOFTWARE_ONLY**. Дата открытия: 2026-10-11.

## 1. Проблема / задача

Исполнение `EX-INFRA3-U2-OUTENEMY-READINESS-R1` (старт 2026-10-10) выявило
дефекты R2-tooling и устранило их в этой же ветке (F-1/F-2/F-3: engine binary
path, реальная грамматика CMakeCache, `systemd-run --user` opt-in), однако
паспорт родительского WO объявлял allowed_paths только docs/evidence — правки
`scripts/r2/*` и `tests/*` остались вне его декларированного scope. По решению
владельца (mission «NL5 U2 Integration & Narrow Repair», шаг 1.2) это
расхождение закрывается НАСТОЯЩИМ самостоятельным bounded tooling-repair Work
Order: он даёт changes в `scripts/r2/*`, `tests/test_r2_activation_tooling.py`
и служебных docs явное WO-покрытие, сохраняя исходную историю ветки и START
checkpoint родительского исполнения (события 0001/0002 не редактируются;
расхождение документируется новым CONTINUATION-событием родителя).

## 2. Scope (allowed paths)

```text
scripts/r2/__init__.py
scripts/r2/cli.py
scripts/r2/engine_build.py
scripts/r2/executor.py
scripts/r2/fingerprint.py
scripts/r2/supervisor.py
tests/test_r2_activation_tooling.py
docs/work/WO-INFRA3-R2-TOOLING-REPAIR-R1.md
docs/work/executions/EX-INFRA3-R2-TOOLING-REPAIR-R1/**
docs/evidence/INFRA3-U2-READINESS/**
docs/work/WORK_QUEUE.md            (одна surface-sync строка tooling-repair WO
                                    + append-only обновление строки U2-readiness)
docs/infra/U2_OUTENEMY_EXECUTOR_READINESS_R1.md (только разделы tooling/U2-dispatch
                                    фактов; статусы НЕ меняются)
```

Правки F-1/F-2/F-3 (уже в истории ветки на START этого WO) покрываются этим
WO ретроспективно и явно; новые правки этого WO:

- **F-4** `resolve_engine_binary`: неоднозначные case-insensitive совпадения в
  `<build>/bin` (например `oxDNA` + `OXDNA`) → fail-closed отказ
  (FileNotFoundError), никогда произвольный выбор первого файла; +3 теста.
- **U2 executor path** (`r2.cli run-u2`): отдельный безопасный путь исполнения
  технических fixtures на закреплённой U2-платформе:
  1. собственная host-role проверка `validate_u2_host` (pinned U2 hostname
     case-insensitive/short-name, тот же native platform floor, host обязан
     ОСТАВАТЬСЯ не-U1-eligible; неизвестный hostname = fail-closed);
  2. ОБЯЗАТЕЛЬНАЯ dispatch authority: без `--dispatch-authority` →
     `BLOCKED_NO_DISPATCH_AUTHORITY` (exit 3); с ней — полная schema-v3
     валидация `nanolab_v02_dispatch_authority` (Git-bound lifecycle
     S → F → D/R/V → A) через `build_execution_plan`;
  3. launch gate: не-fixture план НИКОГДА не исполняется этой командой
     (`BLOCKED_LAUNCH_GATE_PROTECTED_WRITER` — machine_launch_authorized=false
     по конструкции; настоящий launch gate — внешний Human/Protected-Writer);
  4. fixture ceiling: исполняются ТОЛЬКО `synthetic_test_fixture_only`-планы;
     spec обязан объявлять `"fixture": true`; execution id замороженной
     кампании (`EX-NL5-REPRO-V0-2*`) — жёсткий отказ;
  5. ledger append-only, scientific_outcome = NOT_EVALUATED всегда.

## 3. Вне scope (запрещено)

- Ослабление U1 guard: `r2.cli run`/`build-engine`/`gate`/`nc-verify` продолжают
  требовать `validate_native_u1` без изменений (негативный контроль остаётся
  зелёным — на U2-платформе U1-путь обязан отказывать).
- Любые confirmatory scientific runs; запуск замороженных кампаний; изменение
  frozen package F2, frozen protocol/contract/seed record байтов.
- Изменение canonical статусов (`project/state.json`, `project/infra-state.json`),
  назначение AUTHOR_U1, объявление R2 ACTIVE.
- Реальное исполнение через systemd-transient launcher (argv остаётся
  unit-проверенным; проводка реального исполнения — предмет frozen WO кампании).
- Merge в main (остаётся Human Gate).

## 4. Required outputs (machine-checkable)

1. F-4 fix + тесты (ambiguous → fail-closed; единственное совпадение —
   резолвится).
2. `validate_u2_host` + `PINNED_U2_HOSTNAMES` + тесты (pinned eligible;
   неизвестный/would-be-U1/WSL — отказ; U1-инвариант не ослаблен).
3. `run-u2` CLI с полной safety chain + тесты: e2e fixture dispatch на
   синтетическом Git-репозитории (temp, disposable), missing/invalid authority
   отказ, frozen campaign id отказ, non-fixture план отказ на launch gate,
   non-U2 host отказ.
4. Родные (native, без инъекции fingerprint) машинные пробы на этой машине:
   e2e fixture run exit 0 + ledger запись; missing authority → exit 3;
   `r2.cli run` на outenemy → exit 2 BLOCKED_HOST (негативный контроль U1).
5. Полный unittest набор зелёный на этой машине; `work_cli validate` обоих
   executions ok; `check-consistency` ok; `workflow_lint` blocking=0.
6. Execution events START → CONTINUATION → HANDOFF + summary; evidence JSON
   с command/returncode/sha256.

## 5. Validation plan

- `python3 -m unittest discover -s tests -t .` → OK (0 failures).
- `PYTHONPATH=scripts python3 -m harness.work_cli validate
  docs/work/executions/EX-INFRA3-R2-TOOLING-REPAIR-R1` → ok.
- `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` → ok.
- `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` → blocking=0.

## 6. Честные границы

Этот WO НЕ активирует R2, НЕ назначает U1, НЕ запускает научную кампанию и НЕ
создаёт real dispatch authority. `run-u2` сегодня способен исполнить только
синтетические technical fixtures на outenemy; реальный U2-leg кампании остаётся
закрытым до R2 ACTIVE + валидной real dispatch authority + Human Protected
Writer Gate (план будет помечен launch gate HUMAN_PROTECTED_WRITER, machine
launch невозможен по конструкции — `BLOCKED_LAUNCH_GATE_PROTECTED_WRITER`).
