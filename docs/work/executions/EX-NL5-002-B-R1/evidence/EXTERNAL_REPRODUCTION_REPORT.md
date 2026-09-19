# EXTERNAL_REPRODUCTION_REPORT — NanoLab component package `nanolab-components` v0.1.0 (DNA hinge family)

Заполнено внешним исполнителем по `REPORT_TEMPLATE.md` (Appendix B к WO-NL5-002-A-R1).
Все времена UTC. Рабочая область: `/home/rdpuser/nl5-002-external/workspace/`.
Кампания: 2026-09-18T13:57:34Z → 2026-09-19T01:05Z (~11.1 h wall; бюджет 48 h соблюдён).

## 1. Executor identity & independence statement

- Agent/session type: автономный программный агент (внешний reproduction executor),
  действующий строго по `EXECUTOR_PROTOCOL.md`; инструменты — shell/файлы/сеть.
- Доступно как вход:
  - каталог пакета `/home/rdpuser/nl5-002-external/package/` (только чтение; целостность
    подтверждена `reproduce.py verify`);
  - `EXECUTOR_PROTOCOL.md`, `REPORT_TEMPLATE.md`;
  - публичный интернет — только для ресурсов, прямо требуемых пакетом: upstream
    `gauravarya77/DNA-hinge-simulations` @ `23fd1ff7731e9017bd776f49206dc42d70d9fe91`
    (download-on-run, digest gates) и исходники движка oxDNA @ `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`;
  - системные инструменты (gcc/cmake/python3/git/curl; numpy/scipy из окружения).
- Недоступно/закрыто: всё прочее на машине (в т.ч. `/home/rdpuser/NanoLab`, другие проекты,
  кэши, истории); репозиторий NanoLab, на который пакет ссылается как на место хранения
  полных текстов `E2_PROTO_R1.md`, `E2_OBSERVABLES_R2.md`, `ENGINE_ENVIRONMENT_R1.md` и
  frozen arm-manifest'ов — не открывался (не входит в разрешённые входы). Это ограничение
  стало причиной главного PORTABILITY_FINDING (№1, см. §13).
- Физический хост: другой, чем авторская среда (авторы: WSL2 Ubuntu 24.04, gcc 13.3.0;
  исполнитель: Ubuntu 22.04.5 на голом железе, gcc 11.4.0 — см. §2). Пересечений с авторской
  средой нет, кроме копии пакета и публичных upstream-ресурсов.
- Подсказки от авторов не запрашивались и не получались. Решения в неоднозначных местах
  принимались исполнителем и зафиксированы как deviations/findings.

## 2. Environment fingerprint

- OS/kernel: Ubuntu 22.04.5 LTS (jammy); Linux 5.15.0-190-generic x86_64.
- CPU: 2× Intel Xeon E5-2698 v3 @ 2.30GHz (16C/32T каждый) = 64 vCPU; RAM 125 GiB; GPU не used.
- gcc/g++ 11.4.0; make 4.3; cmake 3.22.1; python 3.10.12; git 2.34.1; numpy 1.26.4; scipy есть.
- Сеть: через HTTP-прокси `http://192.168.0.27:8888`; github.com доступен, но git-транспорт
  больших pack'ов обрывается («early EOF») — движок получен tarball'ом точного коммита
  (см. §4, Deviation 2).
- Timestamps: старт кампании 2026-09-18T13:57:34Z; конец (отчёт завершён) 2026-09-19T01:05Z.
  Полный fingerprint: `workspace/env/environment_fingerprint.txt`.

## 3. Package integrity

`python3 reproduction/reproduce.py verify` (cwd = package/), полный вывод:

```json
{
  "mode": "verify",
  "ok": true,
  "files": 20,
  "errors": []
}
```

- exit code 0; сохранено: `workspace/logs/01_verify.txt`.
- `VERSION` = `0.1.0`; согласуется с `RELEASE_MANIFEST.json` и `CITATION.cff` (0.1.0). Предупреждений нет.
- `python3 reproduction/reproduce.py plan`: ok=true; 5 карточек (4 MEASURED + 74b NOT_MEASURED);
  engine pin/шаги/expected соответствуют карточкам (сверено вручную). Сохранено: `workspace/logs/02_plan.txt`.

## 4. Engine build provenance

- Pin (карточки): oxDNA @ `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`; «CPU build, double precision»; модель DNA2.
- Repo: `https://github.com/lorenzo-rovigatti/oxDNA` (пакет называет движок «oxDNA» без URL;
  указанный коммит существует в каноническом публичном репозитории oxDNA).
- Получение: `git clone` и `git fetch --depth=1` через прокси обрываются → tarball точного
  коммита `https://codeload.github.com/lorenzo-rovigatti/oxDNA/tar.gz/00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`
  (curl `--http1.1`), 32 974 279 bytes,
  sha256 `40a6dd36b93a1e126111fb9d9bbf2d4ac8fb392bb9e145d873cdd004ac9baa04`
  (контент = дерево пиннутого коммита).
- Сборка: `cmake ../oxdna-src -DCMAKE_BUILD_TYPE=Release -DDOUBLE=ON -DCUDA=OFF -DMPI=OFF -DDebug=OFF -DNATIVE_COMPILATION=OFF -DJSON_ENABLED=OFF -DLEGACY_CODE=OFF`
  → CPU, double (CMakeLists: `OPTION(DOUBLE "Set the numerical precision to double" ON)`);
  линковка без CUDA/MPI подтверждена (ldd: только libstdc++/libm/libgcc/libc).
- Патч (единственное изменение исходников движка, физика не затронута):
  `src/Utilities/parse_input/parse_input.h` + `#include <string>` — коммит не собирается
  GCC 11.4 («field 'key' has incomplete type 'std::string'»). Diff: `workspace/build/engine_patch.diff`.
- Параллельная сборка `-DNATIVE_COMPILATION=ON` сделана только для замера скорости
  (3.97 vs 4.17 steps/s) — в кампании НЕ использовалась.
- Warnings: только `-Warray-bounds` в 3rd-party `src/extern/tinyexpr/tinyexpr.c`; полный лог
  `workspace/build/oxdna_build.log` (0 ошибок после патча).
- Время сборки: 14:29:18Z → ~14:31Z (~2 мин, make -j16). Бинарник: `workspace/build/oxdna-build/bin/oxDNA`
  (лог движка: `INFO: RELEASE: v3.7`; CPU backend; double).

## 5. Upstream inputs (download-on-run)

Скрипт `workspace/downloads/dl_verify.py`; disposable-каталог `workspace/downloads/disposable-20260918T143146Z/`
(скачивание 2026-09-18T14:31–14:32Z). Обязательные гейты size + blob_sha1 (git blob hash,
пересчитан локально); sha256 — информационно, в паре с sha256_status.

| файл | size (ожид/факт) | blob_sha1 | sha256 | verdict | ts |
|---|---|---|---|---|---|
| MD_Hinges/0b.conf | 2294162 / 2294162 | PASS | match (CONTENT_VERIFIED) | PASS | 14:31:33Z |
| MD_Hinges/0b.top | 120204 / 120204 | PASS | match (CONTENT_VERIFIED) | PASS | 14:31:36Z |
| MD_Hinges/11b.conf | 2309610 / 2309610 | PASS | match (COMPUTED_NOT_VERIFIED) | PASS | 14:31:44Z |
| MD_Hinges/11b.top | 121176 / 121176 | PASS | match (COMPUTED_NOT_VERIFIED) | PASS | 14:31:46Z |
| MD_Hinges/32b.conf | 2345114 / 2345114 | PASS | match (COMPUTED_NOT_VERIFIED) | PASS | 14:31:53Z |
| MD_Hinges/32b.top | 123024 / 123024 | PASS | match (COMPUTED_NOT_VERIFIED) | PASS | 14:31:55Z |
| MD_Hinges/53b.conf | 2379246 / 2379246 | PASS | match (COMPUTED_NOT_VERIFIED) | PASS | 14:32:01Z |
| MD_Hinges/53b.top | 124872 / 124872 | PASS | match (COMPUTED_NOT_VERIFIED) | PASS | 14:32:03Z |
| MD_Hinges/pro_CPU.in | 933 / 933 | PASS | match (CONTENT_VERIFIED) | PASS | 14:32:06Z |

- Итог: 12/12 PASS (`overall_digest_gate=PASS`), все sha256 также совпали — файлы со статусом
  COMPUTED_NOT_VERIFIED фактически подтверждены повторным независимым скачиванием.
  JSON: `workspace/downloads/upstream_digest_gates.json`.
- 74b-входы не скачивались: карточка NOT_MEASURED, прогоны/значения не производились.
- Durable-кэш отсутствует: после кампании (00:52Z) все 9 upstream-файлов удалены из
  disposable-каталога; перед удалением неизменность подтверждена повторным пересчётом
  всех digest'ов (`downloads/post_campaign_input_reverification.json`, all_unchanged=true);
  удаление зафиксировано (`downloads/disposable_dir_deletion_record.json`).

## 6. Frozen seeds

Зафиксированы ДО первого запуска движка: 2026-09-18T14:01:32Z; файл
`workspace/analysis/frozen_seeds.json`
(sha256 `457bf4fadb177a97136aeea2b4d4cb8a6c44489d293a836bcf53dbcf8314906d`).

| вариант | seeds (R1/R2/R3) | проверка |
|---|---|---|
| 0b | 510101 / 520202 / 530303 | ≠ reference (201004, 202008, 203012) ✓ |
| 11b | 510101 / 520202 / 530303 | ✓ |
| 32b | 510101 / 520202 / 530303 | ✓ |
| 53b | 510101 / 520202 / 530303 | ✓ |

Дизайн зеркалит reference-кампанию (одни и те же 3 seed на все варианты). Все значения —
целые, валидные для движка, не равные reference.

## 7. Runs

Команда каждой реплики (cwd = каталог прогона; full command):

```
timeout 72000 /home/rdpuser/nl5-002-external/workspace/build/oxdna-build/bin/oxDNA input.in
```

Конфиг реплики = upstream `pro_CPU.in` VERBATIM с минимальным overlay (`runs/launcher.py`):
`seed` (fresh), `steps` (по protocol_pins карточки), `topology`/`conf_file` (digest-верифицированные
файлы варианта), `trajectory_file`/`energy_file`/`log_file` (per-run пути), `print_energy_every=100`
(pin protocol_pins.options; в авторском файле 4e3). Остальное byte-identical (thermostat=john,
newtonian_steps=103, diff_coeff=2.5, interaction_type=DNA2, salt_concentration=0.5, T=300K,
dt=0.005, verlet_skin=0.05, rcut=2.0, print_conf_interval=4e3, debug=1, refresh_vel=1,
restart_step_counter=1, …). Полный overlay виден в `runs/<ID>/input.in`.

Диагностические прогоны (не входят в 12; ID не переиспользовались):

| run ID | seed/steps | exit | wall | назначение/исход |
|---|---|---|---|---|
| EXTERNAL-0b-SMOKE1 | 510101 / 4000 | killed SIGTERM (таймаут 600 s исполнителя) | ~600 s | smoke: конфиг принят, RNG seeded 510101, energy/last_conf пишутся; ~2500 шагов (~4.2 steps/s) |
| EXTERNAL-0b-SMOKE2 | 510101 / 4000 | 124 (timeout 150 s) | 150 s | замер скорости native-сборки (3.97 steps/s) |
| EXTERNAL-0b-DET-D1/D2 (2000) | 777777 / 2000 | 0 / 0 | ~7.5 min каждый | первая проверка детерминизма — траектории ПУСТЫ (2000 < print_conf_interval 4000), сравнение вакуумное; помечено в логе |
| EXTERNAL-0b-DET-D1/D2 (8000) | 777777 / 8000 | 0 / 0 | ~30 min каждый | детерминизм: 2 кадра, траектории byte-identical, sha256 `6d1aeb51321264e17b0e6e0f7c0725636d411b37659114c70ef6f81cab2af1e0` — PASS |

Основные 12 реплик — фактическое состояние (см. Deviation 1): **все 12 были терминированы
окружением исполнителя** ~2026-09-19T00:15–00:30Z (≈9.5 h wall каждая; заявленный протоколом
hard kill 20 h НЕ наступил; движковые процессы исчезли, wrapper'ы не дописали exit_code).
Ни один прогон не дошёл до заявленных steps; наблюдаемого exit code нет. Последние состояния
зафиксированы по артефактам (последний `t =` в trajectory.dat; последний step в energy.dat; mtime):

| run ID | variant | seed | steps (заявл.) | факт. последний шаг (energy) | последний кадр t | кадров | wall (start→kill) | траектория (sha256/size) |
|---|---|---|---|---|---|---|---|---|
| EXTERNAL-0b-R1 | 0b | 510101 | 200000 | 131100 | 128000 | 32 | 14:48:49Z→00:16:09Z (9.46h) | 8ea08af6be66e772… / 73 406 125 B |
| EXTERNAL-0b-R2 | 0b | 520202 | 200000 | 131300 | 128000 | 32 | 14:48:49Z→00:15:19Z (9.44h) | 42e5c51e47ae5d41… / 73 415 861 B |
| EXTERNAL-0b-R3 | 0b | 530303 | 200000 | 130600 | 128000 | 32 | 14:48:49Z→00:18:17Z (9.49h) | 2b6316f6ce9008d7… / 73 398 372 B |
| EXTERNAL-11b-R1 | 11b | 510101 | 200000 | 132000 | 132000 | 33 | 14:48:49Z→00:30:10Z (9.69h) | 5cad392168c97734… / 76 219 580 B |
| EXTERNAL-11b-R2 | 11b | 520202 | 200000 | 132800 | 132000 | 33 | 14:48:49Z→00:26:30Z (9.63h) | 0e5012acc24c8499… / 76 220 172 B |
| EXTERNAL-11b-R3 | 11b | 530303 | 200000 | 130900 | 128000 | 32 | 14:48:50Z→00:17:01Z (9.47h) | cf3abda0220e30a3… / 73 908 541 B |
| EXTERNAL-32b-R1 | 32b | 510101 | 150000 | 129900 | 128000 | 32 | 14:48:50Z→00:21:26Z (9.54h) | dc107ebea8663e16… / 75 043 626 B |
| EXTERNAL-32b-R2 | 32b | 520202 | 150000 | 129500 | 128000 | 32 | 14:48:50Z→00:23:14Z (9.57h) | 0fd4e0c293b0af0c… / 75 042 089 B |
| EXTERNAL-32b-R3 | 32b | 530303 | 150000 | 129300 | 128000 | 32 | 14:48:50Z→00:24:27Z (9.59h) | c6b14b7be88d875b… / 75 043 562 B |
| EXTERNAL-53b-R1 | 53b | 510101 | 150000 | 138800 | 136000 | 34 | 14:48:50Z→00:18:17Z (9.49h) | 97df8463d218224d… / 80 925 697 B |
| EXTERNAL-53b-R2 | 53b | 520202 | 150000 | 136600 | 136000 | 34 | 14:49:14Z→00:27:36Z (9.64h) | 222f4279276d5b86… / 80 899 941 B |
| EXTERNAL-53b-R3 | 53b | 530303 | 150000 | 138700 | 136000 | 34 | 14:50:22Z→00:18:43Z (9.47h) | 005a5b69733e95c7… / 80 913 632 B |

Примечания:
- «кадров» — полных кадров в trajectory.dat (кадр каждые 4000 шагов с t=4000); последний
  кадр каждого прогона полон (парсинг без ошибок, §8.2).
- Прогноз завершения при наблюдаемой скорости ~3.3–3.6 steps/s: 150k-прогоны ~02:00Z,
  200k ~06:30Z; фактическая остановка — на 85–92% / 64–66% пути.
- Полные digest'ы всех выходных файлов: `workspace/artifacts/run_output_digests.json`.
- `analysis/TESTPARTIAL_analysis.json` — валидация анализатора на частичной копии
  траектории 0b-R1 (4 кадра); в отчётные таблицы не входит.

## 8. Analysis

### 8.1 Конвенция угла: что было доступно из пакета и чего не хватило

Опубликованное в пакете описание наблюдаемого (карточки/family/reports):
«[0,180] deg, PCA axes, erratum R1 §2.5; detector v2 mutual-nearest + PCA hinge angle,
frozen arm manifest». Ссылки ведут на артефакты, НЕ входящие в пакет:
`docs/research/E2_OBSERVABLES_R2.md`, `docs/research/E2_PROTO_R1.md` (гейты §4, статистика §6),
erratum R1 §2.5, frozen arm-manifest'ы (`arm-manifest-0b.json` и т.п.), скрипт
`scripts/release/reproduction_rule.py`. Протокол внешнего воспроизведения прямо запрещает
читать репозиторий NanoLab. => обязательные элементы конвенции (точное членство нуклеотидов
в плечах, точные константы детектора, правило ориентации осей из erratum) в пакете отсутствуют.

PORTABILITY_FINDING (главный): воссоздать frozen-конвенцию 1-в-1 из пакета невозможно.
Что попробовано (полный лог: `workspace/analysis/convention_reconstruction_log.md`,
12 семейств методов): калибровка детектора пар (взаимно-ближайшие; window; antiparallel a1);
дуплекс-сегменты; коаксиальное слияние в спирали; пороговые сетки параллельности на уровне
спиралей и нуклеотидов (по a3 и по оси спирали a1×a3); спектральная бисекция контактного
графа; 2-линейные смеси (EM); принудительные по размеру назначения; биссекторные плоскости;
исключения области вершины; полилинии; tip-направления. Валидационные оракулы пакета:
(а) published размеры плеч и coverage — не воспроизводятся ни одним правилом (например,
32b: карточка 4814/3190, тогда как любая пространственная бисекция даёт ~4248/3928);
(б) `design.angle_frame0_deg` — лучшие результаты по семействам (deg):

| метод (frame 0) | 0b (66.8867) | 11b (74.3580) | 32b (77.4771) | 53b (132.9496) |
|---|---|---|---|---|
| C1: спектральные плечи + PCA-оси, наружу, [0,180] | 63.6229 | 65.0022 | 63.7227 | 114.8802 |
| C2: вершина-исключение R=8 + размер-forced + PCA | 67.2960 | 75.1564 | 79.5881 | 119.0540 |
| tip-направления (вершина→дистальный дециль) | 66.18 | 69.72 | 71.20 | 118.59 |

Ошибки (±0.4–2° у 0b/11b/32b в лучших семействах, −14…−18° у 53b) превышают ширину
reference-конвертов (0b 2.14°, 11b 2.37°, 32b 2.38°, 53b 4.24°); ни одно единое правило не
закрывает все 4 варианта одновременно. Значения для карточек НЕ выдумывались;
contract-классификация по этой причине не выполнялась (§9); все числа ниже —
`BEST_EFFORT_NOT_CONTRACT`.

### 8.2 Frame-validity gates

Пороги опубликованы в карточках (`integrity.details`); определения метрик — в недоступном
E2_PROTO_R1 §4; реализованы реконструкции:
- `pairs_fraction_v2 ≥ 0.50`: v2-детектор (COM window [0.9,1.4), mutual-nearest, antiparallel
  a1, cross-strand) воспроизводит published счётчики пар: у меня 0b t=4000..16000 →
  3283/3281/3317/3301 против reference_pairs_v2_count 3292–3301; доля = pairs(frame)/pairs(first).
- `displacement ≤ 20.0`: max |r(t) − r(0)| по нуклеотидам; максимум по кадрам.
- `long_bond_fraction ≤ 0.1078`: реконструкция — доля backbone-связей длиннее 1.0
  (FENE-предел r0+DR0=0.75+0.25); воспроизводит published baseline (ниже).
- `energy |drift| total`: |E_tot(t) − E_tot(0)| из energy_file (print_energy_every=100).

Фактические значения по усечённым окнам (все кадры валидны, 392/392; NaN/truncated кадров нет):

| вариант | min pairs_fraction | max displacement | max long_bond (proxy) | max energy drift | valid |
|---|---|---|---|---|---|
| 0b | 0.9933 | 8.044 | 0.05607 | 0.005543 | 96/96 |
| 11b | 0.9836 | 8.732 | 0.05718 | 0.006891 | 98/98 |
| 32b | 0.9867 | 12.975 | 0.05822 | 0.011325 | 96/96 |
| 53b | 0.9914 | 15.673 | 0.05853 | 0.007367 | 102/102 |

Сопоставление с published baseline 0b (reference): displacement_max_max 7.43–8.40 (у меня 8.04);
long_bond max 0.0555–0.0560 (у меня 0.0561); energy drift 0.0046–0.0099 (у меня 0.0055);
pairs_fraction min 0.9818 (у меня 0.9933). Реконструкции воспроизводят published масштабы,
но их определения остаются недоопределёнными в пакете (PORTABILITY_FINDING №2).

### 8.3 Per-replica результаты — BEST_EFFORT_NOT_CONTRACT

Окно: заявленное протоколом t ≤ 150000; фактически доступно из-за терминирования только
t ≤ 128000 (0b, 32b; 32 of 37 in-window кадров), t ≤ 132000 (11b-R1/R2, 33; R3 — 128000, 32),
t ≤ 136000 (53b, 34). Медианы по валидным кадрам доступного окна; surrogate-манифесты плеч
заморожены на frame 0 (детерминированное построение, повторяемо).

Конвенция C1 (спектральные плечи + PCA-оси, наружу, [0,180]):

| вариант | per-replica median (R1/R2/R3), deg | campaign statistic | frame-0 offset vs card | calibrated stat (диагностика) |
|---|---|---|---|---|
| 0b | 62.713 / 63.760 / 61.885 | 62.713 | −3.264 | 65.977 |
| 11b | 64.224 / 65.242 / 65.841 | 65.242 | −9.356 | 74.598 |
| 32b | 64.085 / 64.230 / 64.673 | 64.230 | −13.754 | 77.984 |
| 53b | 117.044 / 113.052 / 114.508 | 114.508 | −18.069 | 132.577 |

Конвенция C2 (вершина-исключение R=8, размеры по карточке, PCA-оси):

| вариант | per-replica median (R1/R2/R3), deg | campaign statistic | frame-0 offset vs card | calibrated stat (диагностика) |
|---|---|---|---|---|
| 0b | 66.128 / 67.436 / 64.840 | 66.128 | +0.409 | 65.719 |
| 11b | 74.793 / 76.176 / 76.403 | 76.176 | +0.798 | 75.377 |
| 32b | 77.718 / 79.323 / 79.112 | 79.112 | +2.111 | 77.001 |
| 53b | 121.552 / 118.244 / 120.005 | 120.005 | −13.896 | 133.900 |

Bootstrap (10000 resamples, seed 424242, numpy PCG64, median) — descriptive only; per-replica
и pooled CI95 сохранены в `workspace/analysis/campaign_summary.json` (реализация — исполнителя;
авторский `confirm_analysis.py` в пакет не включён).

Ключевое наблюдение: разные surrogate-конвенции/калибровки дают разные исходы относительно
envelope (0b: C1-calibrated 65.98 и C2 66.13 — внутри; 11b: C1-calibrated 74.60 чуть выше
[72.17, 74.53]; 32b: C2 79.11 внутри, C2-calibrated 77.00 ниже; 53b: обе calibrated внутри,
без калибровки — ниже). Чувствительность к выбору конвенции — прямое следствие отсутствия
frozen-определения; эти числа НЕ являются претензией на MATCH/MISMATCH.

## 9. Per-card classification

| variant | campaign statistic (BEST_EFFORT, C1/C2) | envelope (из карточки) | classification | примечание |
|---|---|---|---|---|
| 0b | 62.713 / 66.128 (окно усечено до 128000) | [65.095434789, 67.236579608] | **INCONCLUSIVE** | frozen-конвенция нереализуема из пакета (PORTABILITY_FINDING №1); прогоны терминированы окружением на ~131k/200000 шагов |
| 11b | 65.242 / 76.176 (окно усечено до 128–132000) | [72.165683993, 74.533109426] | **INCONCLUSIVE** | то же; усечение на ~131–133k/200000 |
| 32b | 64.230 / 79.112 (окно усечено до 128000) | [77.4927314, 79.877463339] | **INCONCLUSIVE** | то же; усечение на ~129–130k/150000 |
| 53b | 114.508 / 120.005 (окно усечено до 136000) | [131.049227687, 135.285186059] | **INCONCLUSIVE** | то же; усечение на ~137–139k/150000 |
| 74b | N/A — NOT_MEASURED/KNOWN_GAP, значения не производились | — | — | подтверждено: ни прогонов, ни значений; входы 74b не скачивались |

Обоснование по frozen-правилу `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`: MATCH требует
«frozen integrity/analysis применены» — frozen observable-конвенция неприменима из пакета;
кроме того, техническое выполнение неполно (реплики терминированы до заявленных шагов,
окно t ≤ 150000 не достигнуто). Каждая из двух причин независимо достаточна для
INCONCLUSIVE; technical failure зафиксирован отдельно и не трактуется как научный mismatch.

## 10. Deviations

1. **Терминирование прогонов окружением (главное)**: все 12 реплик остановлены средой
   исполнителя ~2026-09-19T00:15–00:30Z на ~128000–138800 шагах (64–66% пути для 200k-вариантов,
   85–92% для 150k); ~9.5 h wall (предел протокола 20 h не наступил). Stop-правила протокола
   (digest gate fail; >1 invalid output на вариант) не срабатывали; exit code прогонов не
   наблюдаем; новых прогонов не запускалось (оркестрационное решение в рамках 48-часового
   бюджета). Влияние: окно анализа усечено (32–34 кадра из 37), кампания технически не
   завершена — отражено в §7–§9 и в вердикте.
2. Движок получен tarball'ом точного коммита (git-транспорт через прокси обрывается).
3. Однострочный include-патч `parse_input.h` (сборка GCC 11); физика не изменена.
4. Основная сборка `NATIVE_COMPILATION=OFF`; native-сборка — только замер скорости, не использовалась.
5. Run-overlay против verbatim `pro_CPU.in`: seed, steps, пути входов/выходов,
   `print_energy_every=100` (pin карточки; в авторском файле 4e3).
6. Два smoke-прогона и детерминизм-прогоны (уникальные ID, вне 12 реплик; детерминизм PASS;
   первая 2000-шаговая попытка вакуумная — пустые траектории — и помечена в логе).
7. 53b-R2/R3 запущены detached (setsid) из-за лимита фоновых задач исполнителя (10);
   до терминирования работали наравне с остальными.
8. Disposable-каталог upstream-входов удалён после кампании (durable-cache FORBIDDEN),
   после фиксации неизменности digest'ов.
9. Анализ TESTPARTIAL (4 кадра, валидация пайплайна) — вне отчётных таблиц.
10. Детекторы/гейты/углы — реконструкции (§8.1–8.2, findings №1–2): неизбежное следствие
    неполноты пакета, а не молчаливая подмена; все такие числа помечены BEST_EFFORT_NOT_CONTRACT.

Иных отклонений нет: пороги/envelope не менялись, значения для NOT_MEASURED-карточки не
производились, package/ не изменялся и не открывался на запись.

## 11. Artifact manifest

Полный машиночитаемый манифест: `workspace/artifacts/artifact_manifest.json`
({path, sha256, size, producer} для каждого файла workspace: отчёт, логи, fingerprint,
build-артефакты и патч, download-гейты, frozen_seeds.json, per-run manifests/конфиги/
траектории/energy/last_conf/логи, все analysis-скрипты и JSON, включая campaign_summary.json
и per-run `*_analysis.json`). Сводные digest'ы выходов прогонов:
`workspace/artifacts/run_output_digests.json`. Манифест детерминированно пересчитывается
`workspace/analysis/artifact_manifest.py`.

## 12. WO-level verdict self-assessment (non-binding)

**INCONCLUSIVE.**

Обоснование по опубликованным правилам:
- Техническая цепочка до движка воспроизводится полностью: package verify PASS (20 файлов,
  0 ошибок); движок собран из точного pinned commit (CPU/double; однострочный задокументированный
  include-патч); 12/12 upstream digest gates PASS (size + blob_sha1 обязательны; sha256 тоже
  совпали); fresh seeds заморожены до запусков; исполнение движка детерминировано на машине
  исполнителя (byte-identical повторы). Пороги/envelope/пакет не изменялись.
- Научное сравнение невозможно по двум независимым причинам:
  (1) frozen observable-конвенция (arm manifests + E2_OBSERVABLES_R2 + erratum R1 §2.5)
  не опубликована в пакете и не восстановлена 12 семействами реконструкций с приемлемой
  точностью (ошибки против published frame-0 oracle превышают ширину envelope; для 53b — до ~14°);
  (2) все 12 реплик терминированы окружением до завершения (окно t ≤ 150000 не достигнуто).
- По REPRODUCTION_RULE_V0_1: технический сбой фиксируется отдельно и не превращается в
  scientific mismatch; оснований для MISMATCH нет; MATCH недостижим. Итог — INCONCLUSIVE.
  (FAILED_TECHNICAL не выбран как WO-уровень, поскольку первичный блокер — неполнота пакета
  относительно наблюдаемого, а не только исполнение; терминирование задокументировано как
  Deviation 1 и вторая независимая причина INCONCLUSIVE по карточкам.)

## 13. Findings

1. **[PORTABILITY, blocking]** Frozen arm-manifest'ы, `E2_OBSERVABLES_R2.md`, erratum R1 §2.5
   и код детектора не включены в пакет (ссылки на внешний репозиторий NanoLab). Угол
   («[0,180] deg, PCA axes, erratum R1 §2.5; detector v2 …; frozen arm manifest») не
   реализуем из пакета 1-в-1: 12 семейств реконструкций не закрывают одновременно published
   размеры плеч и angle_frame0_deg (§8.1, `analysis/convention_reconstruction_log.md`).
   Card-level сравнение невозможно без публикации манифестов/определений.
2. **[PORTABILITY, moderate]** Определения frame-validity метрик (long_bond_fraction,
   pairs_fraction_v2, displacement, energy drift) — в недоступном E2_PROTO_R1 §4; в карточках
   только пороги. Реконструкции воспроизводят published baseline (v2 pair counts 3281–3317 vs
   3292–3301; long-bond 0.0546–0.0585 vs ~0.0555–0.0560; displacement 8.04 vs 7.43–8.40 @0b),
   но определения пришлось реверс-инжинирить.
3. **[PORTABILITY, minor]** Engine pin `00dc7fb…` не собирается GCC 11+ (нет `#include <string>`
   в parse_input.h) — нужен однострочный патч (авторская среда gcc 13.3 с этим не сталкивалась).
4. **[PORTABILITY, minor]** Авторский `pro_CPU.in` жёстко ссылается на `74b.top`/`74b.conf`:
   для каждого варианта нужен per-variant overlay путей; в карточках не документировано.
5. **[DOC/CONSISTENCY]** Карточки пинят `print_energy_every=100`, авторский конфиг содержит
   4e3: overlay подразумевается, но не указан явно как diff.
6. **[DOC]** 11b: protocol_pins.steps=200000, но reference-прогон остановлен на ~184000
   (SIGTERM budget interrupt, зафиксирован в parametric-summary). Пин описывает запрос,
   а не факт; внешняя реплика обязана выполнить полные 200000.
7. **[PORTABILITY, info]** Published размеры плеч (например, 32b 4814/3190) не соответствуют
   никакой пространственной бисекции спаренного множества (~4248/3928): алгоритм
   arm-manifest-v1 не выводим из пакета; сообщение об ошибке 74b раскрывает только сетку
   порогов (ключи вида 0.85) и таблицы размеров блоков.
8. **[FRICTION]** git clone/fetch через прокси окружения обрывается (early EOF) — движок
   получен tarball'ом точного коммита codeload (--http1.1); контент идентичен дереву коммита.
9. **[FRICTION]** Лимит фоновых задач исполнителя (10): 2 реплики запущены detached;
   на результат не повлияло.
10. **[EXECUTION/ENV]** Все 12 реплик терминированы средой ~9.5 h wall (128–138.8k шагов из
    150k/200k; заявленный протоколом kill 20 h не наступал; stop-правила не срабатывали).
    Зафиксировано как независимая причина INCONCLUSIVE по карточкам.
11. **[POSITIVE]** Воспроизводимость движка на машине исполнителя: два независимых повтора
    (seed 777777, 8000 шагов) — byte-identical траектории (sha256 `6d1aeb51…`).
12. **[DOC, minor]** `protocols/README.md` отсылает за полными протоколами в репозиторий
    NanoLab, который по правилам внешнего воспроизведения не является входом — пакет в
    текущем виде не self-contained для независимой репликации наблюдаемого (корень finding 1).

---
Машинные артефакты: `workspace/analysis/campaign_summary.json` (per-replica/bootstrap/
классификации), `workspace/analysis/manifest_<variant>.json` (surrogate-манифесты),
`workspace/analysis/<run>_analysis.json` (per-frame ряды),
`workspace/downloads/upstream_digest_gates.json`, `workspace/artifacts/run_output_digests.json`,
`workspace/artifacts/artifact_manifest.json`.
