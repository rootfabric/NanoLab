# Атомистический адаптер R1: Cu / ASE EMT

Реальный ограниченный расчёт одного материала: непериодический FCC-кластер меди → BFGS-релаксация → короткая Langevin MD → JSON-траектория, метрики, отчёт и SHA-256 manifest. `SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`, scientific outcome `NOT_EVALUATED`. Это инженерная демонстрация; E6, P0 и исторические научные checkpoints остаются без приёмки.

## Запуск

Из корня репозитория, Python 3.12 / Linux:

```bash
python3 -m venv .venv-atomistic
.venv-atomistic/bin/python -m pip install -r docs/atomistic/requirements.txt
PYTHONPATH=scripts python3 -m atomistic.cli validate --config examples/atomistic/cu-demo.json
PYTHONPATH=scripts .venv-atomistic/bin/python -m atomistic.cli run --config examples/atomistic/cu-demo.json --output-root /tmp/nanolab-atomistic --run-id cu-demo-001
PYTHONPATH=scripts python3 -m atomistic.cli verify /tmp/nanolab-atomistic/cu-demo-001
```

Run ID нельзя повторять, в том числе после ошибки. Перед первым расчётом в данной mission требуется зарезервировать pilot budget у интегратора и опубликовать frozen protocol/code/config checkpoint. Work Order разрешает максимум 8 pilots, суммарно 20 минут compute и 2 GiB результатов. API ведёт небольшой persistent ledger с atomic reservation под `flock`: `<git-common-dir>/nanolab-atomistic/WO-ATOMISTIC-PRODUCT-R1.json`. Все worktrees, CLI и UI используют одну квоту; смена output_root и перезапуск сервера её не сбрасывают. Failed/cancelled attempts учитываются. В ledger сначала резервируются полный timeout и output cap, после завершения записывается фактический расход. Только одна активная reservation разрешена. После аварии родительского процесса незавершённая reservation остаётся блокирующей: требуется аудит остановки worker и append-only correction оператором, автоматического reset/retry нет.

Это guard бюджета конкретного pilot Work Order, не постоянное ограничение лицензии приложения. Для установки вне Git оператор должен установить один фиксированный абсолютный `NANOLAB_ATOMISTIC_MISSION_ROOT` для CLI/UI; его смена не означает новой grant. Новый accepted execution profile потребует отдельной scope/budget revision. CLI не выдаёт launch authority. Существующие scientific launch gates не изменены.

Встроенный профиль: только Cu / `ASE_EMT_Cu`, 1–4096 атомов (FCC conventional cell содержит 4 атома), до 500 шагов релаксации и 2000 MD steps; до 201 сохранённого кадра. Предоставленный pilot — 32 атома, до 100 relaxation steps, 50 MD steps, 50 fs. Полный расчёт ограничен 120 s wall time, worker — 120 s CPU, 2 GiB address space, 256 MiB output, одним численным потоком. Превышение лимита, нечисловое состояние, отсутствие сходимости релаксации или cancellation сохраняются как `FAILED_TECHNICAL`. Верхние caps обеспечивают ограниченность, но не обещают возможность рассчитать 4096 атомов за этот бюджет: плотная BFGS-матрица может упереться в память.

## Контракт

`atomistic.api.validate_config(config)` работает на stdlib. Неизвестные поля, неоднозначные единицы, boolean вместо чисел, NaN/Inf, неподдерживаемые материал/модель и превышения caps отвергаются до worker. `read_config(path)` дополнительно отвергает повторяющиеся JSON keys и файл >64 KiB.

`run(config, output_root, run_id, *, timeout_seconds=120, cancel_event=None)` запускает фиксированный subprocess текущего Python без shell и возвращает `{run_id, run_dir, status, trajectory, metrics, manifest}`. Для реального расчёта текущий Python должен принадлежать изолированному venv. API требует Linux resource limits; произвольные команды, модели и пути к потенциалам отсутствуют. `cancel_event` — совместимый `threading.Event`. Исключения: `ValidationError` до запуска, `RunError` при неуспешном исполнении. Worker log и partial outputs остаются в уникальном каталоге.

| Файл | Содержимое |
|---|---|
| `protocol.json` | сохранён до subprocess: config, subject/digests, model source, observables, numerical tolerance, budget, stop rules |
| `config.json` | строгий нормализованный config `atomistic-config-v1` |
| `environment.json` | версии всех installed distributions, Python/platform, SHA-256 исходника EMT, Cu parameters, limits |
| `trajectory.json` | `atomistic-trajectory-v1`, material/model/atom_count/symbols/cell_angstrom/pbc, `frames` |
| `metrics.json` | `atomistic-metrics-v1`, relaxation, MD parameters, `series` каждого MD step, `final`, numerical control и resource usage |
| `numerical-control.json` | заранее заданная finite-difference проверка силы той же модели |
| `relaxation.json`, `relaxation.log` | сходимость, energies, max force и шаги BFGS |
| `worker.log`, `report.md` | журнал процесса и читаемый отчёт |
| `manifest.json` | статус, actual wall time, exit code, failure class, source/code identity, pins и SHA-256/size всех прочих файлов |

Кадр: `{step, time_fs, positions_angstrom:[[x,y,z],...], potential_energy_ev, kinetic_energy_ev, total_energy_ev, temperature_k}`. Step 0 — релаксированная структура после задания скоростей; затем interval и финальный шаг. Энергии — полные eV, время — fs с начала MD, координаты — Å. `cell_angstrom` содержит bounding simulation cell с вакуумом; `pbc` всегда false. Температура — ASE kinetic definition с 3N степенями свободы, не равновесная оценка. Langevin фиксирует центр масс; стартовые скорости Maxwell–Boltzmann, затем удаление импульса центра масс с сохранением стартовой температуры.

## Проверки

Обычный suite не требует ASE и не выполняет MD:

```bash
PYTHONPATH=scripts python3 -m unittest tests.test_atomistic_backend -v
```

Выделенная integration-команда **реально считает** один pilot и требует отдельной регистрации его budget:

```bash
PYTHONPATH=scripts .venv-atomistic/bin/python -m atomistic.integration --output-root /tmp/nanolab-atomistic --run-id integration-cu-001
```

Она проверяет сходимость, уменьшение potential energy при релаксации, finite-difference контроль, число шагов/кадров, движение атомов и digest readback. Optional unittest запускается только при `NANOLAB_REAL_ATOMISTIC_TEST=1`, с обязательным `NANOLAB_ATOMISTIC_OUTPUT_ROOT` и новым `NANOLAB_ATOMISTIC_RUN_ID`; он тоже расходует один pilot. Побитовое совпадение между платформами не заявляется.

См. [MODEL_CARD.md](MODEL_CARD.md) и [PILOT_PROTOCOL_R1.md](PILOT_PROTOCOL_R1.md).
