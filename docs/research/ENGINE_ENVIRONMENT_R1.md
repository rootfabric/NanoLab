# ENGINE_ENVIRONMENT_R1 — Канонический engine environment (результат NL1-001)

Статус: **IMPLEMENTED, REVIEW REQUIRED**. Исполнение: `EX-NL1-001-R1`. Work Order: `NL1-001` (issue #5). Дата: 2026-09-09.

Этот документ фиксирует первую каноническую среду исполнения NanoLab для oxDNA (`E1-PROTO-R1` §7, §11.1–2). Документ описывает среду и наблюдаемые effective defaults; научные прогоны E1 в NL1-001 не выполнялись.

## 1. Engine subject

```text
engine        = oxDNA (lorenzo-rovigatti/oxDNA)
pinned commit = 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591
release line  = v3.7 (строка RELEASE: v3.7 из лога фактического прогона)
rights        = GPL-3.0 (NL0-002); DOWNLOAD_ON_SETUP — engine не вендорится в NanoLab
acquisition   = git fetch --depth 1 origin <pinned-commit> в пустой репозиторий + checkout FETCH_HEAD
                (полный clone через прокси не уложился в таймаут; точечный fetch даёт тот же объект коммита)
```

Проверка субъекта: `git rev-parse HEAD` = `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`; заголовок лога прогона печатает `GIT COMMIT: 00dc7fb`.

## 2. Среда исполнения (первый канонический путь — Linux)

| Компонент | Значение |
|---|---|
| ОС | WSL2 Ubuntu 24.04.2 LTS (kernel `6.18.33.2-microsoft-standard-WSL2`) |
| CPU | 13th Gen Intel(R) Core(TM) i9-13900H, 20 логических ядер |
| RAM (WSL-аллокация) | 15 GiB |
| Компилятор | gcc/g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0 |
| Сборка | GNU Make 4.3 |
| CMake | 3.31.6, user-local tarball, **без глобальных установок и без sudo** |
| Python | 3.12.3 (в сборке не участвовал) |

Provenance CMake: `cmake-3.31.6-linux-x86_64.tar.gz`, SHA-256 `5a1133ff103c71eb5120e2cc3de922733e7d8a26a98ae716397e8676adb367bf`, совпадает с официальным checksum-файлом Kitware (`cmake-3.31.6-SHA-256.txt` из release v3.31.6).

Правило протокола (HARNESS_AUTONOMOUS_EXECUTION): среда = fallback executor №2 (локальная изолированная среда); WSL-дистрибутив владельца глобально не изменялся (cmake распакован в user-каталог, сборка в `~/nl1-001/`, fixture/артефакты в `C:\NanoLab\scratch\nl1-001\` — disposable scratch вне Git).

## 3. Команды сборки (воспроизводимая последовательность)

```bash
# 1. acquire pinned engine (Windows-сторона; WSL не имеет прямого интернета)
git init oxDNA && git -C oxDNA remote add origin https://github.com/lorenzo-rovigatti/oxDNA
git -C oxDNA fetch --depth 1 origin 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591
git -C oxDNA checkout --detach FETCH_HEAD

# 2. инструменты: user-local cmake (tarball см. §2), распаковка в tools/cmake

# 3. build (в WSL, native FS)
cp -r oxDNA ~/nl1-001/oxdna-src && mkdir -p ~/nl1-001/build-oxdna-cpu
cd ~/nl1-001/build-oxdna-cpu
<path-to>/tools/cmake/bin/cmake ../oxdna-src -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DMPI=OFF
make -j20     # BUILD_EXIT=0, wall ≈ 14 c на 20 ядрах
```

Эффективные опции сборки (CMakeCache): `CMAKE_BUILD_TYPE=Release` (→ `-O3 -DNDEBUG`), `DOUBLE=ON` (двойная точность), `CUDA=OFF`, `MPI=OFF`, `NATIVE_COMPILATION=ON` (`-march=native`), `JSON_ENABLED=ON`, `CMAKE_CXX_FLAGS` (доп.) пуст; в исходниках CMake добавляет `-D_FORCE_INLINES`.

## 4. Артефакты сборки (SHA-256)

```text
oxDNA         73b6cfb0e2d6a61f4fd946e7b4ec55e203f13c9bac5cbce9ee52f18ef08170b3  (3375976 B)
DNAnalysis    f5fc9da2e2aeed904b66bd136209244ef01a6f8e423d3be739aaa3e91305556b  (2957400 B)
confGenerator b4d420e173ebbed13236e40197f6baac005aa9b9cd7b6ed983baadeb2f801841  (2201664 B)
```

Бинари не коммитятся в NanoLab (scratch воспроизводим по командам §3); пересборка Verifier'ом возможна за ~15 c.

## 5. Правило байт-точного получения входов (критическое наблюдение)

Windows-checkout этого репозитория выполнялся с `core.autocrlf=true`: рабочие копии fixture-файлов получают CRLF, и их SHA-256 **не совпадают** с пинами (`E1-PROTO-R1` §2.2) — расхождение обнаружено при первой же проверке (4/4 mismatch на working tree) и устранено извлечением сырых blob'ов.

**Канонический способ** получения входов для любых прогонов — только сырые blob'ы pinned tree (line endings не искажаются):

```bash
git cat-file blob <blob-sha> > <file>   # в WSL/Linux; редирект bash байт-точный
sha256sum <file>                        # обязан совпасть с пином
```

Найденныеworking-tree-хэши CRLF-копий сохранены в IMPLEMENTER_EVIDENCE как негативный артефакт. Blob SHA-1 всех четырёх файлов в pinned tree совпали с пинами `E1-PROTO-R1` §2.2 (4/4), SHA-256 извлечённых сырых blob'ов — 4/4 MATCH, размеры 148/4498/533/51 B.

## 6. Effective defaults engine (закрытие UNKNOWN `E1-PROTO-R1` §11.1–2)

Источники: лог фактического прогона (OBSERVED) + исходники/документация pinned commit (OBSERVED-in-source). Значения с `#` вычислены по формулам исходников для параметров verbatim-входа.

| Параметр | Effective значение | Основание |
|---|---|---|
| interaction_type | `dna` (default; в `quick_input` не задан) | `input_options.md` §InteractionFactory: «Defaults to dna»; `InteractionFactory.cpp:45` (опция опциональна) |
| sequence-режим | average/sequence-НЕзависимый: `use_average_seq` default `true` (`DNAInteraction.cpp:14`, `_average(true)`); seq-файл НЕ загружается — в логе нет строки «Using ... sequence-dependent values» | исходники + лог |
| соль | NOT_APPLICABLE для default `dna` (oxDNA1): salt-опции относятся к `DNA2Interaction` (`input_options.md` §Interactions/DNA2Interaction.h); Debye-Hückel не активен | исходники + лог |
| thermostat | `john` = **alias BrownianThermostat** (`ThermostatFactory.cpp:25`); docs pinned commit list 'john' не содержат (stale) | исходники |
| thermostat pt | `pt = (2·T·nst·dt)/(T·nst·dt + 2·diff_coeff)` = **0.019929118**# при T=0.097717, nst=103, dt=0.005, diff_coeff=2.50 (`BrownianThermostat.cpp::init`) | формула исходников |
| thermostat pr (вращ.) | `pr = (2·T·nst·dt)/(T·nst·dt + 6·diff_coeff)` = **0.006687465**# | формула исходников |
| T | `20C` → **0.097717** внутр. ед. (лог: «Converting temperature ... (0.097717)») | лог OBSERVED |
| seed | случайный при каждом запуске (`#seed = 4982` закомментирован upstream; лог smoke: «seeding the RNG with -807631765»; значение smoke повторно НЕ используется) | лог OBSERVED |
| симуляция | MD (default: «Simulation type not specified, using MD»), backend CPU | лог OBSERVED |
| система | N=16, molecules=2 — совпадает с `dsdna8.top` «16 2» | лог OBSERVED |
| энергия в energy.dat | колонки: step(MD-time), U/N, K/N, (U+K)/N — `PotentialEnergy.cpp:24` `energy /= N`; колонка 2 = **потенциальная энергия на нуклеотид** — подтверждает ASSUMED `E1-PROTO-R1` §5.1 | исходники |

## 7. Upstream smoke (технический go/no-go, НЕ наука)

Run ID: `EX-NL1-001-SMOKE-001`. Вход: копия fixture (хэши перепроверены на месте, 2/2). Отклонения от `quick_input`: **функциональных ровно два** — `steps = 1e4` (вместо `1e6`) и `print_conf_interval = 1e4` (вместо `1e5`) — чтобы smoke не являлся protocol-прогоном E1 и дал по одной записи каждого вывода; кроме того, копия отличается байт-уровнево косметически (удалены строки-комментарии/заголовки секций, 3 пустые строки и 2 trailing-space; 414 B vs 533 B) — нефункционально, парсер pinned engine стирает `#`-комментарии и trim'ит ключи/значения (erratum по finding F-1/MINOR-1 независимых вердиктов). Прогон выполнялся **до** принятия NL1-001 в соответствии с запретом `E1-PROTO-R1` §7 именно на verbatim-прогоны; изменённый smoke-вход под запрет §7 не подпадает и научной интерпретации не подлежит.

```text
exit code        = 0
wall clock       = 0.13 s (/usr/bin/time -v); таймер engine: 0.100016 s, 0.0100 ms/step
max RSS          = 6424 KB
energy.dat       = 11 строк (steps/print_energy_every + стартовая), NaN/Inf: 0
trajectory.dat   = 1 конфигурация + last_conf.dat
engine verdict   = «END OF THE SIMULATION, everything went OK!»
```

Аргументы §4 `E1-PROTO-R1` (go/no-go): topology разбирается (16/2 из лога), engine стартует без ошибок, колонка 2 `energy.dat` конечна и по порядку величины совместима с upstream-оракулом (−1.29…−1.40 при полосе −1.3797±0.15 — **совпадение не является scientific результатом**).

Экстраполяция для планирования бюджета NL1-002 (planning input, не измеренный production-факт): 0.0100 ms/step × 1e6 ≈ **10–15 c на 1 ядро** на прогона; RAM ≈ 6–10 MB; 3 pilot + 1 T1 + запас ≪ 1 core-hour. Storage: сотни KB на прогон.

## 8. GPU-путь

`E1-PROTO-R1` §7: R1 = CPU only, GPU не используется. CUDA-сборка не выполнялась (`CUDA=OFF`), GPU-путь не измерялся — осознанно, не является блокером NL1 (acceptance каталога NL1 — один frozen non-AI CPU-путь с измеренными ресурсами). Измерение GPU-пути переносится в отдельный bounded WO при появлении потребности (E3+).

## 9. Ограничения и правила для NL1-002

1. Все входы E1 — только через `git cat-file blob` (§5); рабочие копии Windows-checkout для прогонов запрещены.
2. Verbatim-прогон `quick_input` (1e6 steps) разрешён только после ACCEPTED NL1-001 (`E1-PROTO-R1` §7).
3. Значения §6 (pt/pr, average-режим, отсутствие salt) — часть frozen subject кампании E1; любое их изменение = новая protocol revision.
4. NATIVE_COMPILATION=ON привязывает бинарь к CPU-архитектуре этой машины; перенос на другой executor требует пересборки по §3 и записи новых SHA-256.
5. Инструментальная цепочка (gcc 13.3.0, cmake 3.31.6) и версии ОС зафиксированы §2; смена = новая revision этого документа.
