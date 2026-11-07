# CU-EMT-DEMO-R1 — protocol до первого pilot

Work Order: `WO-ATOMISTIC-PRODUCT-R1`. Claim: `SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`; scientific outcome `NOT_EVALUATED`. Исследовательский вопрос не заявлен: цель — проверить выполнение реальной малой атомистической инженерной цепочки.

Input: `examples/atomistic/cu-demo.json`; 32 Cu атома, 2×2×2 conventional FCC cells, lattice constant 3.61 Å, непериодические границы, vacuum 8 Å. Model: pinned ASE 3.26.0 EMT, `asap_cutoff=False`; Cu параметры и source SHA-256 фиксирует environment artifact. Исходный source/config subject должен быть закоммичен и опубликован интегратором до run. Runtime `protocol.json` сохраняется до старта worker и содержит exact HEAD/TREE и source/config digests. Runtime protocol не заменяет этот preregistration checkpoint.

Подготовка: central finite difference одной силы при смещении первого атома на +0.03 Å вдоль x; derivative step 1e-5 Å, абсолютный допуск 1e-4 eV/Å. Затем восстановление исходных координат и BFGS: max step 0.1 Å, до 100 iterations, fmax 0.05 eV/Å. Нефинитное состояние или провал derivative check — остановка. Отсутствие convergence — failed technical; MD не стартует.

MD: Maxwell–Boltzmann velocities при 100 K, seed 1729, removal of center-of-mass momentum с сохранением температуры; Langevin fixcm=True, timestep 1 fs, friction 0.01 fs⁻¹, 50 steps. Записываются energy/temperature каждого шага; позиции step0 и каждые 5 steps, включая final: 51 строка метрик и 11 кадров.

До результата установлены mechanical integration критерии: finite states, BFGS converged, final relaxation potential energy <= initial potential energy, derivative error <=1e-4 eV/Å, 32 атома, 51 строка метрик, 11 кадров, final step50, движение координат между step0 и step50, корректные SHA-256/size. Это SOFTWARE PASS criteria и не scientific PASS. Термостатированная полная энергия не обязана сохраняться. Никаких statistical confidence или equilibrium claims.

Budget первого pilot: максимум 120 s wall / 120 s CPU, 2 GiB worker address space, 256 MiB outputs, один поток. Mission максимум 8 реальных pilots, 20 min суммарного compute, 2 GiB результатов; последовательное исполнение и ledger интегратора обязательны. Дополнительный запуск — только новый ID, новый ledger reservation, без скрытых повторов. Ошибки, timeout и negative outcomes сохраняются; никаких исключений после просмотра результата. Стоп при missing pin/rights, nonfinite state, digest failure, budget/cancel.

Executor: disposable Linux container данной owner-authorized mission; не U1/U2. Система, paid compute и NL5/E5 scientific dispatch не затрагиваются. Сравнение независимых materials/engines и confirmatory protocol — отдельная работа.
