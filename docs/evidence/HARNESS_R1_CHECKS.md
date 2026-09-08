# NanoLab Harness R1 — проверка control/experiment foundation

Тип: **HARNESS_BOOTSTRAP_CHECK**. Не является научным E0–E6 и не закрывает NL0.

## Subject

```text
BASE_MAIN 3714ae7d7dacb7ba90eedea4c1d6539c9d80225b
SUBJECT   253b44262001bf36779a2c4ea2cd5bff9bfbe5b2
TREE      94b46bfb76ab5a3eb63af5d5cfeaf877a2427bfd
BRANCH    control/nanolab-harness-r1
```

Evidence/report commit после этого subject может менять только документы проверки; machine logic должна оставаться идентичной subject.

## DWS baseline, использованный как источник архитектуры harness

Прочитан canonical `main` `rootfabric/distributed-world-simulator`:

```text
AGENTS.md                                      blob 4b7da93ec4943d645c0118705c45b0ad4178c8a9
HARNESS_CONTROL.md                             blob acdd59a08c4fd0122f0aa9fc61f4ce7bab9e7868
PROJECT_CONTROL.md                             blob 7c52110b66889b7acd369e608db75c239d0c97a9
docs/control/DEVELOPMENT_HARNESS_RU.md         blob 4b7a1a2b22d2fa7d1d7f7760d992deeae5c59ee6
docs/control/HARNESS_REVIEW_AND_EVIDENCE_RU.md blob b20325c37e6c0e14e887c801921c4f382733d9f9
docs/control/HARNESS_AUTONOMOUS_EXECUTION_RU.md blob ddb7e2fdc424e21658abff5548f236add4afecfa
CONTROL_DEVELOPMENT.ps1                       blob 8e5b16f309c2ed3d8bb2c19fcc0ff40ffbfb6e17
```

DWS-specific scheduler/Godot implementation не копировалась целиком. Перенесена модель control и создан компактный NanoLab runtime на Python standard library.

## Проверки remote state

- Branch создан от exact `main` `3714ae7d...`.
- GitHub compare перед финальным evidence показал `ahead`, `behind_by=0`.
- `project/plan.json` на subject содержит 9 стадий NL0–NL8, 18 tasks и E0–E6.
- `project/state.json`: `frontier=NL0`, `next_work_order=NL0-001`; E0–E6 = `NOT_RUN`.
- Harness scheduler сохранён с тем же `NL0 / NL0-001`; параллельная альтернативная roadmap не создана.
- Published `contracts.py`, `cli.py`, `experiment_cli.py`, `work_cli.py` прочитаны обратно из GitHub branch during review.

## Functional isolated smoke

Полный git clone candidate в execution container не состоялся из-за DNS: `Could not resolve host: github.com`. Поэтому exact full-checkout test честно не заявляется.

Для проверки логики опубликованные validator implementations были перенесены в изолированный `/tmp` и выполнены Python 3:

```text
python compileall                            PASS
Experiment close: valid ordered run         PASS
Experiment: REVIEW before final ANALYSIS    FAIL-CLOSED, exit 3
Work close: START + HANDOFF + summary        PASS
Work event after terminal HANDOFF            FAIL-CLOSED, exit 3
```

Наблюдаемые ошибки negative controls:

```text
REVIEW_COMPLETED cannot precede final ANALYSIS_COMPLETED
terminal/handoff event must be last
```

Ранее отдельный negative control подтвердил, что отсутствие `ANALYSIS_COMPLETED` блокирует experiment close, а отсутствие `summary.md` блокирует Work Order close.

## Что именно проверяет R1

- durable START/CONTINUATION/END contract для агентской работы;
- frozen experiment subject и уникальные run IDs;
- separate execution/scientific outcomes;
- порядок START → terminal execution → ANALYSIS → REVIEW;
- artifact provenance: SHA-256, size, producer run, subject, storage location;
- claim ladder C0–C5;
- risk routing LOW/MEDIUM/HIGH/CRITICAL;
- Human Gates для merge/main/history/foundation/CRITICAL/budget expansion;
- plan/state ↔ scheduler/checkpoint alignment.

## Ограничения

- Full exact clone/test не выполнен из-за DNS контейнера.
- JSON Schema meta-validation через сторонний `jsonschema` package не выполнялась; runtime намеренно не имеет внешней Python dependency.
- PowerShell wrappers не запускались в Windows в этой проверке.
- GitHub Actions/hosted runners не запускались.
- Научные движки, physics calculations и E0–E6 не запускались.

## Verdict

`HARNESS_R1_BOOTSTRAP = PASS_WITH_DECLARED_ENV_LIMITATION`.

Это означает, что control foundation готов быть каноническим правилом работы NanoLab. Это **не** утверждение о научной готовности проекта.
