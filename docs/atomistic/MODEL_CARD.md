# Model card — ASE_EMT_Cu / R1

Модель: Python `ase.calculators.emt.EMT(asap_cutoff=False)` из ASE **3.26.0**, только Cu. Параметры Cu поставляются в исходном коде ASE; отдельного импортированного EAM-файла нет. ASE распространяется по LGPL; установленный wheel содержит `ase-3.26.0.dist-info/licenses/LICENSE` (GNU Lesser General Public License v2.1). Фактические байты модуля EMT, значения параметров Cu, пакетные версии и источник адаптера сохраняются на каждый run. `requirements.txt` фиксирует установленный environment pilot на Python 3.12; wheel/source digests установленной модели дополняют version pin.

Primary sources:

- [ASE upstream source, tag 3.26.0](https://gitlab.com/ase/ase/-/blob/3.26.0/ase/calculators/emt.py).
- [ASE EMT documentation](https://docs.ase-lib.org/ase/calculators/emt.html).
- [ASE source documentation](https://docs.ase-lib.org/_modules/ase/calculators/emt.html).
- [ASE licensing and overview](https://docs.ase-lib.org/).

Документация ASE прямо представляет Python EMT как простую модель для demonstrations/tests и указывает Cu среди стандартных поддерживаемых металлов. Это основание выбора инженерного demonstrator, а не доказательство применимости к любым размерам, температурам, дефектам и поверхностям меди. Никакого статуса `SOURCE_VERIFIED` для внешнего material benchmark не присваивается.

Применение R1: небольшая FCC-частица с открытыми границами, чистая медь, ограниченные стартовые параметры; выполнение программного пути и проверка численной согласованности энергии/сил. Ограничение на lattice constant 3.4–3.8 Å и температуру 1–600 K — ограничение интерфейса, **не** валидированный диапазон точности модели.

Не выполнены: независимый lattice/cohesive-energy/elastic/surface benchmark, сравнение с DFT/экспериментом или вторым потенциалом, timestep convergence study, статистическая оценка равновесия, оценка uncertainty, внешнее воспроизведение на принятом U1/U2. Finite-difference контроль использует тот же calculator, поэтому проверяет внутреннюю производную, а не физическую точность. Короткая MD не доказывает долговременную устойчивость, самосборку или работоспособность наномашины.

Claim ceiling: `SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`. Scientific outcome: `NOT_EVALUATED`. P0/E6 acceptance остаётся OPEN и требует отдельного reviewed material-validation protocol и принятого исполнителя. R2/NL5/E5 не активируются этой поставкой.

## Подготовленный bulk reference R1

[Cu reference protocol](reference/cu-r1/PROTOCOL.md) и [source ledger](reference/cu-r1/sources.json) выделяют один первичный низкотемпературный bulk observable для будущего сопоставления: изотермический объёмный модуль. Это **подготовка**, без расчётов модели и без материальной приёмки. Calibration independence не установлена; совпадение fit-sensitive bulk quantity не считается независимой predictive validation. Открытые поверхности нынешнего непериодического UI-кластера и динамика требуют отдельных проверок. P0 остаётся OPEN, scientific outcome NOT_EVALUATED.
