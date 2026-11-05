# Backend R1 — handoff

Work Order: `WO-ATOMISTIC-PRODUCT-R1`, HIGH. Implementer — отдельная backend session; научная и product приёмка не выполнялась. Parent published source/protocol **599ba8d1f089d74dc5f67a33011cba020f6df57a**, TREE **d1e1359ba0e06230aeed0197f2b548f6e9b7f1d1**, exact tree равен локальному implementation commit `1346ebb4dcb07be9ff31f34737f86177233ab518`. Перед реальным расчётом checkout published HEAD был clean; manifest подтверждает `dirty_tracked_files: []`.

## Выполнено

- `scripts/atomistic/{api,budget,cli,worker,integration}.py`: строгий Cu-only config, фиксированный отдельный worker без shell, finite-state checks, BFGS и реальная Langevin MD, predeclared force derivative check, timeout/resource bounds, cancel, unique no-overwrite run IDs, сохранение ошибок, report и digest manifest.
- Persistent mission budget под общим git-common-dir: atomic flock reservation, одна активная задача, максимум 8 attempts / 1200 s / 2 GiB; CLI/UI/новый output_root используют один ledger. Failed/cancel attempts не исключаются. Crash reservation блокирует запуск до операторского аудита. Это профиль данного Work Order, не постоянное ограничение приложения.
- Пинованный isolated venv: `/workspace/scratch/48cb7a65c9c0/atomistic-venv`; `docs/atomistic/requirements.txt` содержит точные версии installed packages; при run core pins проверяются. Runtime model identity содержит SHA-256 модуля EMT и параметры Cu, сверенные с сохранённым до worker protocol.
- `docs/atomistic/{README,MODEL_CARD,PILOT_PROTOCOL_R1}.md` и `examples/atomistic/cu-demo.json`; материалы модели, ограничения, protocol до run и команды воспроизведения.

## Команды и результаты

`PYTHONPATH=scripts python3 -m unittest tests.test_atomistic_backend -v`: **11 PASS, 1 explicit real integration SKIP**; stdlib suite не импортирует ASE и не выполняет физических расчётов. Проверены неправильные единицы/NaN/Inf/bool/огромные числа/элементы/модели/oversize/unknown keys/duplicate JSON keys, unsafe paths, repeat run IDs, cancellation, worker-launch failure, digest tamper/traversal, missing successful artifacts, persistent mission count/serial guard. Первоначальная unit-test ошибка из-за глобального mock Popen, затронувшего git subject probe, устранена изоляцией test mock; никаких actual MD retries не выполнялось.

`PYTHONPATH=scripts python3 -m atomistic.cli validate --config examples/atomistic/cu-demo.json`: PASS, 32 атома.

После публикации protocol/source parent явно зарезервировал pilot1. Команда:

```bash
PYTHONPATH=scripts /workspace/scratch/48cb7a65c9c0/atomistic-venv/bin/python -m atomistic.integration --output-root examples/atomistic/runs --run-id cu-emt-demo-r1-001
```

**COMPLETED** за **0.655380319 s wall**, без повторов. Реальный ASE EMT: 32 Cu атома, BFGS converged за 10 шагов; potential energy 20.96948006 → 20.02719703 eV, final max force 0.032413 eV/Å. Далее 50 Langevin MD steps по 1 fs; 51 строка метрик, 11 кадров. Последняя kinetic T = 46.897077 K; это не равновесная оценка. Ошибка central-difference force = 7.71e-10 eV/Å при заранее заданном допуске 1e-4 eV/Å. Начальные/финальные координаты отличаются; все states конечны.

`PYTHONPATH=scripts python3 -m atomistic.cli verify examples/atomistic/runs/cu-emt-demo-r1-001`: PASS. Все output SHA-256/size опубликованы в [manifest](../../../../examples/atomistic/runs/cu-emt-demo-r1-001/manifest.json). Model module SHA-256: `b8384ffed58deb1182134a0e5088260b7118971488c35cdb6b29e51f6e604f9d`. Bytes результата с manifest: **66811**. Mission shared ledger после pilot содержит 1/8 attempts, 0.655380319/1200 s, 66811/2147483648 bytes. Этот snapshot отражает момент handoff; последующие UI/verifier runs учитываются parent отдельно в том же ledger.

## Ограничения и следующий шаг

Claim ceiling: **SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED**. Scientific outcome: **NOT_EVALUATED**. Derivative test использует тот же engine, не независимый material benchmark. Короткая MD не доказывает equilibrium, stability, accuracy, самосборку или наномашину. P0/E6 acceptance не закрыта; NL5/E5/R2 scientific launch не активируется. Контейнер не принимается как U1/U2.

Плотная BFGS-матрица может ограничить практический размер раньше hard cap4096; API гарантирует budget stop, а не производительность на cap. Mission ledger — guard согласованного локального профиля; изменение operator-selected nonGit root не выдаёт новую authority. Не выполнены material/timestep convergence validation и external physical reproduction.

**Один следующий шаг:** интегратору опубликовать evidence candidate, объединить с UI и передать неизменный subject отдельным Reviewer и Verifier; до acceptance это candidate.
