# Независимая механическая verification — WO-ATOMISTIC-PRODUCT-R1

Роль: отдельная verifier session; implementation не изменялась. Fresh local clone `git clone --no-hardlinks /workspace/scratch/48cb7a65c9c0/NanoLab /workspace/scratch/48cb7a65c9c0/NanoLab-product-verify`, detached checkout exact subject. Общий физический хост; это не external physical reproduction/U1/U2.

## Предварительный subject

HEAD `61790c05a738d43a9be276b08d7be00d0758ea04`, TREE `5414a12b970b40238eea0a702103df838af30df9`. Canonical base `3b567ae33f247b182b2ae451d2cc4598a9e76019`; stacked FLOW `ddbc5cb68a5b720cbbaaadeba96f087d82d82732`. Git history и name-status сохранены отдельно. Clone чист; candidate не изменялся.

## Все пять CI проверок на предварительном subject

| Проверка | Exact command | Результат |
|---|---|---|
| json | `PYTHONPATH=scripts python3 -m harness.batch_validate json --root .` | exit 0, 0.133 s |
| consistency | `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | exit 0, 0.062 s |
| executions | `PYTHONPATH=scripts python3 -m harness.batch_validate executions --root .` | exit 0, 0.070 s |
| workflow | `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | exit 0, 0.042 s |
| unittest | `python3 -m unittest discover -s tests -t . -v` | exit 0, 36.214 s |

JSON: 1551 tracked JSON и 4 pinned non-JSON fixtures. Execution integrity: 71 execution directory. Full suite: 1053 tests, OK (skipped=1), 35.795 s; skip — явно opt-in реальный MD, обычный full CI не запускает физику. Initial failures в моей CI-серии отсутствовали; прежние repair/red evidence не удалялись. Логи исходного subject сохраняются при исправлениях.

## История scientific state и frozen surfaces

`project/state.json` не byte-identical canonical3b567ae: stacked FLOW добавляет open_decisions и operational_queue. Все scientific fields (frontier, next_work_order, completed/active tasks, task/stage/experiment_status, execution/counters, tracking) совпадают с canonical base. В product delta `ddbc5cb..61790c0` state byte-identical. Поэтому утверждение «весь state не менялся от canonical» было бы неверным, а scientific acceptance/counters сохранены.

Не изменены `experiments/`, `data/`, `protocols/`, historical NL5 execution paths, frozen R1/R2 documents, goals/checkpoint catalog. Проверка выполнена по Git diff, детали в integrity.json.

## Проверка pilot1 без нового исполнения

`examples/atomistic/runs/cu-emt-demo-r1-001`: COMPLETED, NOT_EVALUATED. Все 10 записанных raw artifact digests/size сверены с exact HEAD Git blobs (не только рабочей копией). Все 6 adapter source module digest/size совпали и с current candidate, и с recorded source `599ba8d1f089d74dc5f67a33011cba020f6df57a`; recorded tree `d1e1359ba0e06230aeed0197f2b548f6e9b7f1d1` разрешается и совпадает. Source dirty list пуст. Backend verify_run прошёл. Это подтверждение целостности/software provenance; material accuracy не оценивалась.

## Статус

ПРЕДВАРИТЕЛЬНЫЙ, не final gate. Reviewer нашёл дефект ZIP export; UI default friction HTML validity исправляется отдельно. Для окончательного verdict нужны exact repaired subject, affected evidence и заключение независимого Reviewer. Единственный разрешённый verifier replication pilot ещё не запускался; ожидается после UI pilot, с общим mission ledger. Claim ceiling SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED; scientific outcome NOT_EVALUATED; P0 OPEN.

Все raw logs: `/workspace/scratch/48cb7a65c9c0/product-verifier-logs/`. Команды и exit codes — ci-results.json; integrity.json — digest/state evidence. Candidate, main и remote comments не изменялись.

## Repaired exact subject — verification completed, Reviewer gate pending

Final source HEAD `71bc62102cc36bf49b04d40d81d3070d87cccad6`, TREE `f86af90728797541594396ac0bef0964d9f8dd28`. Clean detached checkout; source not modified. Delta from baseline: three bounded repairs (ZIP byte integrity, global mission ID uniqueness across output roots, HTML friction step); associated regression tests/docs/work receipt.

| Проверка | Exact command | Результат |
|---|---|---|
| json | `PYTHONPATH=scripts python3 -m harness.batch_validate json --root .` | exit 0, 0.117 s |
| consistency | `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | exit 0, 0.063 s |
| executions | `PYTHONPATH=scripts python3 -m harness.batch_validate executions --root .` | exit 0, 0.067 s |
| workflow | `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | exit 0, 0.046 s |
| unittest | `python3 -m unittest discover -s tests -t . -v` | exit 0, 40.044 s |

Full suite: 1059 tests in 39.866 s, OK (skipped=1: explicit real MD). Final JSON and execution counts in raw JSON logs. Independent targeted command: `PYTHONPATH=scripts python3 /workspace/scratch/48cb7a65c9c0/product-verifier-logs/targeted-checks.py` (exit0), which verified:

- Existing actual pilot full ZIP contains 11 original files with byte equality; extracted `verify_run` PASS. No calculator execution used for ZIP check.
- Same failed run ID under a second output root is refused by mission ledger before a second worker launch: 1 mock worker, 1 ledger row, second attempt MISSION_BUDGET_BLOCKED. Temporary isolated ledger used; mission actual count unaffected.
- Default friction value aligns exactly to HTML min/step by decimal arithmetic. Actual browser confirmation belongs to UI session.

Initial RED evidence remains: baseline ZIP missing7files and digest/size mismatch3files; baseline cross-root run ID ledger2rows. Correction to early verifier probe: mock `subprocess.Popen` also counted `git` subprocess used by `_subject`, so raw baseline count4 was not a worker count; 2 ledger rows remain the valid admission evidence. Targeted final script initially repeated this instrumentation mistake and failed its own assertion, then was corrected by mocking `_subject` separately. Initial failure retained in `final/targeted-checks-initial-instrumentation-failure.log`. This correction changed verification instrumentation only, without candidate change or actual run.

### Единственный verifier actual replication

Exact command (exit0):

```bash
NANOLAB_ATOMISTIC_MISSION_ROOT=/workspace/scratch/48cb7a65c9c0/NanoLab/.git/nanolab-atomistic PYTHONPATH=scripts /workspace/scratch/48cb7a65c9c0/atomistic-venv/bin/python -m atomistic.integration --output-root /workspace/scratch/48cb7a65c9c0/verification-runs --run-id cu-emt-verifier-r1-001
```

Run started only after UI explicitly released its actual slot. 32 Cu atoms, pinned ASE3.26.0 EMT; same frozen50MD config/seed1729. COMPLETED, converged relaxation, derivative numerical control PASS, 51 metric rows, 11 frames, movement between start/end, all artifact SHA256/size verified. Exact run source HEAD/TREE equals repaired subject and dirty tracked list empty. Runtime resource metadata is separate from numerical outputs.

Worker wall 0.655634 s. Shared mission ledger snapshot: 3 consumed attempts, 1.966933 s charged, 172286 bytes charged; no active reservations. All within8/1200s/2GiB. No retries, no extra actual runs.

Same host, environment and seed: config, trajectory, numerical-control, relaxation and environment are byte-identical to pilot1. Metrics numerical values and series are exact; only `resource_usage` differs. Initial comparator asserted entire metrics byte equality and failed because CPU/RSS metadata naturally varies; preserved in `replication-initial-comparison-failure.log`, no rerun performed. This is local independent execution/software replication, not independent-host physical/material validation.

Pilot1 artifacts remain digest-valid in final Git blobs. api.py/budget.py changed from original producer599ba8d, so old pilot is attributed to its original source; current worker is unchanged. New actual run supplies exact repaired adapter-source provenance. Frozen scientific surfaces and project/state scientific fields rechecked on repaired HEAD: unchanged; entire state still byte-equal FLOW dependency. Details in `final/integrity.json`.

Scientific conclusion `NOT_EVALUATED`; claim ceiling `SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`. P0 material benchmark, model accuracy, timestep convergence/statistical uncertainty, U1/U2 and NL5/E5 acceptance remain unevaluated/open. Final independent Reviewer confirmation still pending when this section was written; mechanical PASS alone is not merge authorization.

## Итоговый verdict по source71bc621

VERIFIER PASS (software/engineering verification). Независимый Reviewer сообщил exact-head technical PASS для `71bc62102cc36bf49b04d40d81d3070d87cccad6` / TREE `f86af90728797541594396ac0bef0964d9f8dd28`; P-REV01/02/03 CLOSED. Его отдельный отчёт: `/workspace/scratch/48cb7a65c9c0/product-review-repair-report.md`. Reviewer не запускал MD и не изменял shared mission ledger. Все five CI gates, independent targeted repairs и единственный actual verifier pilot завершились PASS на exact repaired subject.

Остаётся LOW documentation correction `verify-run` → существующая CLI команда `verify`, передана интегратору. Она не меняет physics/product code; дальнейшие publication/status commits требуют delta review exact changed paths. Этот verdict не является merge/acceptance authority и не принимает P0/NL5/E5.

Next action: Director проверяет последующий publication-only delta и предъявляет единый candidate владельцу согласно действующему merge gate.
