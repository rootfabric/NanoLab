# EXTERNAL REPRODUCTION REPORT — nanolab-components 0.1.1 (WO-NL5-002-A-R2, Appendix B template)

Заполнен внешним исполнителем по `REPORT_TEMPLATE.md` (R1). Все пути артефактов —
относительно `/home/rdpuser/nl5-002-external-r2/workspace/`, если не указано иное.

## 1. Executor identity & independence statement

- **Что я собой представляю:** автономный AI-агент (модель GLM, harness DeepSeek),
  запущенный как delegated subagent «external reproduction executor».
  Работал без связи с авторской средой: единственные входы — копия пакета,
  файл протокола `EXECUTOR_PROTOCOL_R2.md` и шаблон отчёта.
- **Доступные входы (полный список):**
  1. `/home/rdpuser/nl5-002-external-r2/package/` — копия пакета (только чтение);
  2. `/home/rdpuser/nl5-002-external-r2/EXECUTOR_PROTOCOL_R2.md`;
  3. `/home/rdpuser/nl5-002-external-r2/REPORT_TEMPLATE.md`;
  4. публичный интернет через HTTP-прокси (GitHub codeload для движка и upstream-репозитория);
  5. системные инструменты хоста (bash, python 3.10, gcc/cmake/make, curl, git), используемые внутри workspace.
- **Недоступно/закрыто:** любые другие каталоги этого компьютера (в т.ч.
  возможные авторские репозитории/кэши); любые подсказки от авторов; GPU;
  платные сервисы; durable-кэш upstream-файлов (запрещён и не использовался).
- **Физический хост:** физический хост `outenemy` (Ubuntu 22.04, 2×Xeon E5-2698 v3).
  Совпадает ли он с авторской машиной — мне неизвестно; по published пину карточки
  авторская платформа — WSL2 Ubuntu 24.04 (gcc 13.3.0), т.е. **платформа отличается
  от авторской** (другая ОС/компилятор, см. §2). Пересечений с авторской средой
  не наблюдалось: на хосте нет каталогов/репозиториев NanoLab, доступных мне;
  все входы получены из пакета и публичного интернета.

## 2. Environment fingerprint

Полный вывод: `env/environment_fingerprint.txt`.

| пункт | значение |
|---|---|
| OS | Ubuntu 22.04.5 LTS (Jammy) |
| kernel | Linux outenemy 5.15.0-190-generic x86_64 |
| CPU | 2× Intel Xeon E5-2698 v3 @ 2.30GHz, 32 physical / 64 logical cores |
| RAM | 125 GiB total (~54 GiB available во время кампании) |
| disk | ~49 GiB free на /home |
| gcc/g++ | 11.4.0 (Ubuntu 11.4.0-1ubuntu1~22.04.3) |
| make | GNU Make 4.3 |
| cmake | 3.22.1 |
| python | 3.10.12 |
| git / curl | 2.34.1 / curl 7.81.0 |
| сеть | HTTP(S)-прокси `http://192.168.0.27:8888` (env http_proxy/https_proxy); localhost direct |
| campaign start (UTC) | 2026-09-19T02:30:08Z (запуск 12 реплик) |
| campaign end (UTC) | 2026-09-19T16:17:48Z (последняя реплика завершилась); анализ завершён 2026-09-19T16:22:33Z |

Отличия от авторского пина платформы (WSL2 Ubuntu 24.04, gcc 13.3.0, cmake 3.31.6):
другая ОС/ядро, старше компилятор и cmake. Сборка движка прошла на pristine
исходниках без правок (§4).

## 3. Package integrity

`python3 reproduction/reproduce.py verify` (полный вывод в `logs/verify.json`):

```json
{
  "mode": "verify",
  "ok": true,
  "files": 42,
  "errors": []
}
```

- exit code: 0.
- VERSION пакета: `0.1.1`; RELEASE_MANIFEST.json: `nanolab-components` `0.1.1`.
- **Предупреждение (косметическое):** `RIGHTS.json` содержит
  `"package_version": "0.1.0"` при VERSION/RELEASE_MANIFEST = 0.1.1 →
  Finding F1 (§13).
- `plan` (exit 0, полный вывод в `logs/plan.json`): 5 карточек; 0b/11b/32b/53b
  MEASURED, 74b NOT_MEASURED (KNOWN_GAP, значений не производил).

## 4. Engine build provenance

- **Commit pin (из карточек):** `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`.
- **Repo URL:** https://github.com/lorenzo-rovigatti/oxDNA
- **Где взят:** tarball по опубликованному в карточке URL
  `https://codeload.github.com/lorenzo-rovigatti/oxDNA/tar.gz/00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`
  (git-транспорт через прокси был нестабилен — карточка прямо разрешает tarball-путь).
  tarball sha256: `40a6dd36b93a1e126111fb9d9bbf2d4ac8fb392bb9e145d873cdd004ac9baa04`
  (размер 32 974 279 B; целостность gzip подтверждена).
- **Правки исходников:** НЕТ (build прошёл на pristine-исходниках; diff не требуется).
- **Команды сборки** (в `engine/build_provenance.txt`, логи `engine/build_cmake.log`, `engine/build_make.log`):

```text
cmake -DCUDA=OFF -DMPI=OFF -DDOUBLE=ON ../oxDNA-00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591
make -j 16
```

- CPU backend (CUDA/MPI OFF); **double precision** — явный флаг `-DDOUBLE=ON`
  (в pinned-коммите это и есть значение по умолчанию: `OPTION(DOUBLE ... ON)`).
- Warnings: 4 (все в bundled `src/extern/tinyexpr/tinyexpr.c`, -Warray-bounds; не
  влияют на физику); Errors: 0.
- Бинарник: `engine/build/bin/oxDNA`, sha256
  `11cba0abb13bec05a2057f12f22d0ea0714ceafcad41fb05d315888363c023b2`;
  движок self-report: `INFO: RELEASE: v3.7`.
- Время сборки: cmake 2026-09-19T02:11:17Z → бинарник 02:11:47Z (<1 мин, -j16).
- Smoke-проверки входного формата до реальных прогонов: 2 коротких прогона
  EXTERNAL-SMOKE-0B-01 (400 шагов) и EXTERNAL-SMOKE-0B-02 (4000 шагов), оба
  exit 0; подтверждено: backend CPU/double принимается, `print_energy_every=100`
  работает, счётчик шагов стартует с 0 (первый кадр траектории `t = 4000`,
  т.е. `restart_step_counter = 1` из upstream-конфига действует) — это критично
  для окна сравнения конвенции. Smoke-прогоны в кампанию не входят (не реплики).

## 5. Upstream inputs (download-on-run)

- Источник: https://github.com/gauravarya77/DNA-hinge-simulations, exact pinned
  commit `23fd1ff7731e9017bd776f49206dc42d70d9fe91`, получен tarball'ом
  (`https://codeload.github.com/gauravarya77/DNA-hinge-simulations/tar.gz/23fd1ff7731e9017bd776f49206dc42d70d9fe91`,
  sha256 `9b96c22e95ab401211324d49fe382033e75fefa2657b7b61674d4779722b58ae`,
  18 655 762 B, скачан 2026-09-19T02:28Z) в **disposable** каталог
  `upstream_disposable/` workspace.
- Обязательные гейты size + blob_sha1 (git blob SHA1 = sha1("blob <size>\\0"+content))
  против пинов `provenance/source-digests.json`; дополнительно сверён
  опубликованный sha256. Машиночитаемый результат: `logs/upstream_digest_gate.json`.

| файл (в карточке) | ожид. size | выч. size | size gate | ожид. blob_sha1 | выч. blob_sha1 | blob gate | sha256 сверка |
|---|---|---|---|---|---|---|---|
| MD_Hinges/0b.conf | 2294162 | 2294162 | PASS | 181373f0…6134da | 181373f0…6134da | PASS | == published (CONTENT_VERIFIED) |
| MD_Hinges/0b.top | 120204 | 120204 | PASS | 84edad43…e44b | 84edad43…e44b | PASS | == published (CONTENT_VERIFIED) |
| MD_Hinges/pro_CPU.in | 933 | 933 | PASS | 89d76310…a735 | 89d76310…a735 | PASS | == published (CONTENT_VERIFIED) |
| MD_Hinges/11b.conf | 2309610 | 2309610 | PASS | ce940256…4b50d | ce940256…4b50d | PASS | == published (COMPUTED_NOT_VERIFIED) |
| MD_Hinges/11b.top | 121176 | 121176 | PASS | c8d34a47…2f8688 | c8d34a47…2f8688 | PASS | == published (COMPUTED_NOT_VERIFIED) |
| MD_Hinges/32b.conf | 2345114 | 2345114 | PASS | 83dda807…0bdae | 83dda807…0bdae | PASS | == published (COMPUTED_NOT_VERIFIED) |
| MD_Hinges/32b.top | 123024 | 123024 | PASS | a0891d65…c6b | a0891d65…c6b | PASS | == published (COMPUTED_NOT_VERIFIED) |
| MD_Hinges/53b.conf | 2379246 | 2379246 | PASS | 74fb9738…b7d6a | 74fb9738…b7d6a | PASS | == published (COMPUTED_NOT_VERIFIED) |
| MD_Hinges/53b.top | 124872 | 124872 | PASS | 171fcb41…7f4fc9 | 171fcb41…7f4fc9 | PASS | == published (COMPUTED_NOT_VERIFIED) |

(полнозначные хэши — в `logs/upstream_digest_gate.json`; pro_CPU.in один файл,
использован для всех вариантов). **Итог: 9/9 файлов (все варианты 0b/11b/32b/53b)
PASS по size+blob_sha1; sha256 совпал с опубликованным во всех 9 случаях.**
- **Durable-кэш: отсутствует.** Скачивание — одноразовое, в disposable каталог;
  по завершении исполнения upstream-файлы удаляются (REFERENCE_ONLY, G1 decision B).
- **frame0 oracle (обязательная самопроверка конвенции ДО прогонов)** — 4/4
  точных совпадений с `design.angle_frame0_deg` (выводы: `logs/frame0_*.json`,
  сводка `logs/frame0_oracle_summary.json`):

| вариант | oracle angle_deg | card design.angle_frame0_deg | exact match |
|---|---|---|---|
| 0b | 66.886745865 | 66.886745865 | YES |
| 11b | 74.357957026 | 74.357957026 | YES |
| 32b | 77.477102136 | 77.477102136 | YES |
| 53b | 132.949606811 | 132.949606811 | YES |

## 6. Frozen seeds

Заморожены ДО первого прогона (2026-09-19T02:08:21Z, файл `seeds_frozen.json`),
все целые положительные (валидны для движка), ни один не равен reference seeds
201004 / 202008 / 203012 (проверено программно при заморозке):

| вариант | seeds | проверка != reference |
|---|---|---|
| 0b | 410273, 520931, 638257 | OK |
| 11b | 741953, 852607, 963541 | OK |
| 32b | 174329, 285637, 396421 | OK |
| 53b | 507283, 618457, 729613 | OK |

## 7. Runs

Формат ID: `EXTERNAL-<variant>-<номер>`; повторные прогоны — под новыми
уникальными ID (переиспользование запрещено). Каждая реплика запускалась
полностью отвязанно (setsid + nohup, PID записан, stdout/stderr → файлы прогона),
по завершении фактический exit code записан в `exit_code.txt` каталога прогона.
Вход каждой реплики: upstream-файлы verbatim (копии, прошедшие гейты §5),
единственные изменения — overlay из protocol_pins карточки: seed, steps, пути
входов/выходов, print_energy_every=100 (см. `runs/<ID>/input`; sha256 входов —
в `runs/<ID>/run_meta.json`). Полная команда запуска каждой реплики:
`<workspace>/engine/build/bin/oxDNA input` в каталоге прогона (обёртка
`runs/<ID>/wrapper.sh`).

**Предыстория запусков (честно):**

- 2026-09-19T02:30:07–08Z: запущены все 12 реплик (ID без суффикса R).
- 2026-09-19T02:44:15Z: 6 реплик 32b/53b (EXTERNAL-32b-1..3, EXTERNAL-53b-1..3)
  остановлены исполнителем (SIGTERM; движок завершился чисто, exit 0, 0 кадров)
  из-за ошибочной первичной оценки темпа (см. §10 D1) и перезапущены под новыми
  ID с суффиксом `R` (2026-09-19T02:50:52–53Z, те же frozen seeds).
- 6 реплик 0b/11b продолжали работать без остановки с 02:30:07Z.

**Итоговые валидные реплики (12)** — все значения ниже наблюдаемые из файлов прогонов
(`exit_code.txt`/`exit_code_raw.txt`, `start_time.txt`/`end_time.txt`,
`analysis/completeness.txt`, sha256/size — `runs/<ID>/traj.dat`; полные дайджесты
всех выходов (traj.dat, energy.dat, last_conf.dat, log.dat, stdout.log,
stderr.log, run_meta.json каждой реплики) — в машинном файле
`run_output_digests.json`, 84 записи = 12 прогонов × 7 файлов):

| run ID | variant | seed | steps | exit code (набл.) | wall time (набл.) | traj frames (набл.) | traj.dat sha256 / size |
|---|---|---|---|---|---|---|---|
| EXTERNAL-0b-1 | 0b | 410273 | 200000 | 0 | 13h44m16s (02:30:07→16:14:23Z) | 50 | `53dd853a486a9b44b2f9296b4b158cf2cdd44df4ca40388327f3ca5345c81e75` / 114 717 228 B |
| EXTERNAL-0b-2 | 0b | 520931 | 200000 | 0 | 13h38m30s (02:30:07→16:08:37Z) | 50 | `d3d265cc262ebe903f950dbdb494a04ac5f5b27f75a5635e96840a3bb30e187c` / 114 708 295 B |
| EXTERNAL-0b-3 | 0b | 638257 | 200000 | 0 | 13h44m34s (02:30:07→16:14:41Z) | 50 | `7b2399177266c4d1eccc5b6b98b84b9c9345213028d425cb9563b102bac3f015` / 114 710 272 B |
| EXTERNAL-11b-1 | 11b | 741953 | 200000 | 0 | 13h43m57s (02:30:07→16:14:04Z) | 50 | `f2b84aca380d60e882c0f7618d3889ce4d3ccdedb6313dc4a01efebd741f5c8d` / 115 484 703 B |
| EXTERNAL-11b-2 | 11b | 852607 | 200000 | 0 | 13h47m13s (02:30:07→16:17:20Z) | 50 | `0c6e4929a6e555b95a98110e786da42bea77e4d7d4a33d554fdd8bd8fae3c0db` / 115 490 280 B |
| EXTERNAL-11b-3 | 11b | 963541 | 200000 | 0 | 13h47m41s (02:30:07→16:17:48Z) | 50 | `b6cc82d48b3a52e6d5e4c36e5498c16efefac493f85bb2e2d720e091364c1b2b` / 115 484 762 B |
| EXTERNAL-32b-1R | 32b | 174329 | 150000 | 0 | 10h21m49s (02:50:52→13:12:41Z) | 37 | `d2a2f564ae0cdbe33e5cb21b6f4320e2cc108a936e8baa4fd20e7769a81179db` / 86 769 719 B |
| EXTERNAL-32b-2R | 32b | 285637 | 150000 | 0 | 10h25m25s (02:50:52→13:16:17Z) | 37 | `a301daba3b08484ee9610f4e331c3b3b2dc3c6c32a45c32bc61a53ad862cadd7` / 86 770 034 B |
| EXTERNAL-32b-3R | 32b | 396421 | 150000 | 0 | 10h20m23s (02:50:53→13:11:16Z) | 37 | `f69112a831654db62134a0b146e348e0fc8a54882db77651b2489559fd8f69b4` / 86 775 774 B |
| EXTERNAL-53b-1R | 53b | 507283 | 150000 | 0 | 9h49m45s (02:50:53→12:40:38Z) | 37 | `647a90d710decd509b09bf0c55bb055e16823c4a55850a3df3246d30121e3c3a` / 88 051 014 B |
| EXTERNAL-53b-2R | 53b | 618457 | 150000 | 0 | 9h48m58s (02:50:53→12:39:51Z) | 37 | `b9a7002b1cc1b4eba24516cc5d4be0b60ddd9f3013871f7c088df9897517386d` / 88 042 713 B |
| EXTERNAL-53b-3R | 53b | 729613 | 150000 | 0 | 9h45m42s (02:50:53→12:36:35Z) | 37 | `7b2fc416b33c196238278579c6265d2cc94f5e2f9583f1199b1ece8561b779c1` / 88 064 571 B |

Полнота траекторий: последний кадр каждой реплики совпадает с последним
запланированным шагом печати (`print_conf_interval = 4e3`): 0b/11b — последний
кадр t = 200000 (50 кадров), 32b/53b — последний кадр t = 148000 (37 кадров;
150000 не кратно 4000, поэтому последний запланированный печатью шаг — 148000).
Ни одна реплика не достигла 20-часового kill-лимита; бюджет кампании 48 ч
соблюдён (старт 02:30Z, конец 16:17Z того же дня). Хэши входов каждой реплики —
в `runs/<ID>/run_meta.json` (input/conf/top sha256).

**Неудачные/остановленные попытки (в кампанию не входят):**

| run ID | что произошло | exit code | примечание |
|---|---|---|---|
| EXTERNAL-32b-1..3, EXTERNAL-53b-1..3 | остановлены исполнителем на ~шаге 9000 (SIGTERM), 0 кадров | 0 (clean shutdown по сигналу) | перезапущены как -R; траектории неполные → отбракованы по completeness-правилу |
| EXTERNAL-SMOKE-0B-01 | smoke 400 шагов (валидация входа) | 0 | не реплика |
| EXTERNAL-SMOKE-0B-02 | smoke 4000 шагов (валидация времени первого кадра t=4000) | 0 | не реплика |

## 8. Analysis

**Средства:** исключительно упакованная конвенция пакета —
`package/convention/analyze_hinge.py` (детектор `v2 mutual-nearest (frozen,
packaged convention)`, угол в `[0,180]` deg через PCA axes, erratum R1 §2.5,
rule_id `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`), вызываемая драйвером
`workspace/analyze_all.sh` (лог: `logs/analyze_all.log`). Отступлений от
упакованной конвенции не было; собственных альтернативных расчётов не
производилось (кроме voided-реплик отбраковки — тоже средствами конвенции).

**Что выполнено** (все exit=0, наблюдаемые в `analysis/completeness.txt`):

- per-replica: 12 × `analyze_hinge.py run --trajectory runs/<ID>/traj.dat
  --energy runs/<ID>/energy.dat --topology runs/<ID>/<v>.top --manifest
  package/convention/arm-manifest-<v>.json --variant <v> --run-id <ID>
  --window <W> --exit-code-file runs/<ID>/exit_code.txt --report
  analysis/<ID>_analysis.json`, окно W: 200000 (0b) / 150000 (11b/32b/53b) —
  по protocol_pins карточек. Результаты: `analysis/<ID>_analysis.json` +
  копия stdout `analysis/<ID>_analysis_stdout.json` для всех 12 реплик;
  `analysis/<ID>_analysis_stderr.txt` — **все 12 файлов пустые (0 B)**;
- campaign: 4 × `analyze_hinge.py campaign --card
  package/families/dna_hinge/cards/<v>.card.json --variant <v> --run-jsons
  analysis/<...>_analysis.json` → `analysis/campaign_<v>.json` для
  0b/11b/32b/53b; `analysis/campaign_<v>_stderr.txt` — все 4 пустые (0 B).

**Как реализована конвенция угла:** элементы конвенции, доступные из пакета —
`convention/OBSERVABLE_CONVENTION_V0_1.md`, `convention/analyze_hinge.py`,
`convention/arm-manifest-<variant>.json` (×4), карточки вариантов
(`design.angle_frame0_deg`, envelope, pins). Все элементы оказались доступными;
`PORTABILITY_FINDING` по конвенции **нет** (подтверждено обязательной frame0
самопроверкой §5: 4/4 точных совпадений до прогонов).

**Frame-validity gates** (применены packaged-анализом, из published данных
пакета; значения из `<ID>_analysis.json`): `engine_exit_code = 0` (все 12);
`displacement_max_max = 20.0`; `long_bond_fraction_max = 0.1078`;
`pairs_fraction_v2_min = 0.5`; детектор `v2 mutual-nearest`. Итог по валидности:
`frames_valid_in_window = frames_in_window` и
`valid_frame_fraction_in_window = 1.0` во **всех 12** репликах — ни один кадр
не отбракован гейтами. Недоопределённым frame-validity не осталось; единственная
наблюдаемая неоднородность единиц времени (traj `t` = счётчик шагов, energy
`t` = шаг×dt) не входит в packaged-конвенцию и коснулась только
информационной строки watcher-скрипта — см. Finding F2 (§13).

**Per-replica результаты** (n валидных кадров в окне и median, значения
перенесены как записано в `analysis/<ID>_analysis.json`):

| run ID | window | n_valid_frames | median_deg |
|---|---|---|---|
| EXTERNAL-0b-1 | 200000 | 50 | 68.389781796 |
| EXTERNAL-0b-2 | 200000 | 50 | 69.600296613 |
| EXTERNAL-0b-3 | 200000 | 50 | 67.586275641 |
| EXTERNAL-11b-1 | 150000 | 37 | 72.255209867 |
| EXTERNAL-11b-2 | 150000 | 37 | 73.560609814 |
| EXTERNAL-11b-3 | 150000 | 37 | 75.35617795 |
| EXTERNAL-32b-1R | 150000 | 37 | 75.180138343 |
| EXTERNAL-32b-2R | 150000 | 37 | 74.713050721 |
| EXTERNAL-32b-3R | 150000 | 37 | 76.100697787 |
| EXTERNAL-53b-1R | 150000 | 37 | 132.41188514 |
| EXTERNAL-53b-2R | 150000 | 37 | 130.244172898 |
| EXTERNAL-53b-3R | 150000 | 37 | 136.169087714 |

**Campaign statistic** = median трёх per-replica medians — посчитан
packaged-анализом и записан в `analysis/campaign_<v>.json` (см. §9;
собственных пересчётов нет). Bootstrap CI95 (10000 resamples, seed 424242)
посчитан packaged-анализом внутри `<ID>_analysis.json`
(`angle_stats_valid_in_window.bootstrap`) и используется **только**
описательно (`DESCRIPTIVE_ONLY_NOT_A_REPRODUCTION_TOLERANCE`). Все числа
секций 8–9 — перенос наблюдаемых значений из artifacts, без интерпретаций.

## 9. Per-card classification

Все значения ниже перенесены **как записано** в `analysis/campaign_<v>.json`
(packaged rule `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`, rule
`package/reproduction/REPRODUCTION_RULE_V0_1.md`; классификация выполнялась
упакованным кодом, не исполнителем). Свежих пересчётов и интерпретаций нет.

| variant | campaign statistic (deg) | fresh replica medians (deg) | reference envelope (deg, из карточки) | classification | rule_id |
|---|---|---|---|---|---|
| 0b | 68.389781796 | 68.389781796, 69.600296613, 67.586275641 | [65.095434789, 67.236579608] | **MISMATCH** — "all fresh replica medians are directionally separated from the reference envelope" (все 3 выше ref_max; valid_replicas=3) | NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE |
| 11b | 73.560609814 | 72.255209867, 73.560609814, 75.35617795 | [72.165683993, 74.533109426] | **MATCH** — "fresh campaign replica-median statistic lies inside the preregistered empirical reference-replica envelope" (valid_replicas=3) | NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE |
| 32b | 75.180138343 | 75.180138343, 74.713050721, 76.100697787 | [77.4927314, 79.877463339] | **MISMATCH** — "all fresh replica medians are directionally separated from the reference envelope" (все 3 ниже ref_min; valid_replicas=3) | NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE |
| 53b | 132.41188514 | 132.41188514, 130.244172898, 136.169087714 | [131.049227687, 135.285186059] | **MATCH** — "fresh campaign replica-median statistic lies inside the preregistered empirical reference-replica envelope" (valid_replicas=3) | NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE |
| 74b | N/A — NOT_MEASURED/KNOWN_GAP, значения не производились | — | — | — | — |

Справочно (из `card_reference` тех же файлов): reference_campaign_statistic_deg
— 0b: 65.708669763; 11b: 74.218071238; 32b: 77.794798276; 53b: 132.343978104.
Примечание packaged-файлов: "bootstrap CI is descriptive only and never a
tolerance".

## 10. Deviations

Отступлений от научного содержания протокола (seeds, пороги, envelope,
анализ, окна, число шагов) нет. Зафиксированы следующие процессуальные
отклонения (факты; влияние на сравнимость указано для каждого):

- **D1 — смена launch-стратегии с остановкой и перезапуском 6 реплик.**
  Факт: все 12 реплик были запущены параллельно 2026-09-19T02:30:07–08Z;
  при 12-кратной параллельной konkуренции темп каждой упал примерно вдвое
  (~2.1 шаг/с, ETA 200k ≈ 26 ч > 20-часового kill-лимита протокола), поэтому
  2026-09-19T02:44:15–22Z исполнитель остановил 6 реплик 32b/53b
  (EXTERNAL-32b-1..3, EXTERNAL-53b-1..3; SIGTERM, движок завершился чисто,
  exit 0, 0 кадров) и перезапустил их 02:50:52–53Z под новыми уникальными ID
  с суффиксом `R` — с теми же frozen seeds и verbatim-входами, двумя волнами
  (0b/11b не прерывались ни разу). Зафиксировано в `logs/aborted_attempts.json`
  (6 записей, status `ABORTED_BY_EXECUTOR_AT_LAUNCH_STRATEGY_CHANGE`) и §7.
  Влияние на сравнимость: отсутствует для научных результатов — входы, seeds,
  число шагов и анализ идентичны остальным репликам; затронут только график
  (и список ID: в кампанию входят -R реплики). Отбраковка неполных траекторий
  выполнена по completeness-правилу (0 кадров ≠ последний запланированный шаг).
- **D2 — потеря сессии исполнителя и административный перезапуск watcher'а.**
  Факт: прежняя executor-сессия завершилась во время ожидания; watcher
  `wait_and_analyze.sh` умер вместе с ней. По логу
  `logs/wait_and_analyze_progress.txt` виден gap: непрерывные 5-минутные
  строки `pending=12` до 2026-09-19T05:48:17Z, затем отсутствие записей,
  затем `2026-09-19T14:03:44Z pending=6` — перезапущенный экземпляр.
  Перезапуск (2026-09-19T14:03:46Z) выполнила сторонняя orchestration
  **административно, без изменения скрипта** (в workspace остался исходный
  `wait_and_analyze.sh`; пустой nohup-лог перезапуска —
  `logs/watcher_recovery_nohup.log`). Watcher только опрашивает наличие
  `exit_code.txt` и по готовности запускает упакованный анализ; научного
  содержания он не касается. Сами движковые прогоны не пострадали: все
  реплики были запущены отвязанно (setsid + nohup), продолжали работать и
  завершились с наблюдаемыми exit code (§7). Анализ выполнен один раз,
  упакованными средствами, все exit=0 (§8). Влияние на сравнимость:
  отсутствует (пауза watcher'а не влияет на прогоны и не прерывает их).
- **D3 — отсутствие предупреждений подтверждено наблюдением.** Все 12
  `runs/<ID>/stderr.log` валидных реплик — 0 B; все 12
  `analysis/<ID>_analysis_stderr.txt` и все 4 `analysis/campaign_<v>_stderr.txt`
  — 0 B; в `runs/<ID>/stdout.log` нет строк WARNING/ERROR. Открытых
  warnings, требующих отражения как отклонения, не наблюдалось.

Иных отступлений от шагов карточек и протокола не зафиксировано. Повторных
запусков после D1 не было: каждая -R реплика завершилась с первого перезапуска.

## 11. Artifact manifest

Манифест — машинный файл **`artifact_manifest.json`** (workspace root): JSON-массив
записей `{path, sha256, size, producer}`; пути относительно
`/home/rdpuser/nl5-002-external-r2/workspace/`. Пересчитан генератором
`build_manifest.py` **после финализации этого отчёта**, поэтому включает
финальный `EXTERNAL_REPRODUCTION_REPORT.md`, а также:

- `analysis/` — полные результаты анализа: `completeness.txt`, 12 ×
  `<ID>_analysis.json` + `<ID>_analysis_stdout.json` + `<ID>_analysis_stderr.txt`,
  4 × `campaign_<v>.json` + `campaign_<v>_stderr.txt` (producer — packaged
  `convention/analyze_hinge.py` run/campaign; stderr/stdout-копии — драйвер);
- `logs/` наблюдения завершения: `wait_and_analyze_progress.txt`,
  `analyze_all.log`, `watcher_recovery_nohup.log`, плюс прежние логи запусков
  (`launch_12_runs.txt`, `launch_wave2_runs.txt`, `aborted_attempts.json`,
  `campaign_start_utc.txt`, `frame0_*`, `upstream_digest_gate.json`, `verify.json`,
  `plan.json`);
- `run_output_digests.json` — sha256/size всех выходов 12 валидных прогонов
  (traj.dat, energy.dat, last_conf.dat, log.dat, stdout.log, stderr.log,
  run_meta.json ×12 = 84 записи, каждая с path/sha256/size/run_id/producer);
- обновлённые скрипты инфраструктуры: `analyze_all.sh`, `launch_run.sh`,
  `wait_and_analyze.sh`, `wait_wave2.sh`, `build_manifest.py`,
  `seeds_frozen.json`, `env/environment_fingerprint.txt`, build provenance
  движка, прогоны в `runs/` (trajectories, energy, last_conf, exit codes,
  run_meta, input, wrapper, stdout/stderr), upstream-логи disposable-каталога.

Свойства манифеста: каждая запись содержит непустые `path`, `sha256`, `size`,
`producer`; файл `artifact_manifest.json` **не хэширует сам себя**
(самоссылка невозможна), это единственный сохранённый артефакт вне
собственного списка. Исключены из манифеста по построению: disposable-исходники
upstream (удалены после исполнения, см. §5), исходное дерево движка и
промежуточные объекты сборки (фиксируется только бинарник и provenance-логи),
transient download-логи (`logs/*download*`, `logs/git_fetch_nohup.log`,
`logs/download_http11_nohup.log`).

## 12. WO-level verdict self-assessment (non-binding)

**`MISMATCH`** (non-binding self-assessment; классификации карточек —
non-binding к физическому статусу в силу published правила).

Обоснование строго по frozen mapping `package/reproduction/REPRODUCTION_RULE_V0_1.md`
(rule_id `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`) на основании §9 и §10:

- technical execution завершён: 12/12 реплик с наблюдаемым exit code 0,
  полными траекториями (последний кадр = последний запланированный шаг
  печати), без FAILED_TECHNICAL, digest abort или budget abort;
- frozen integrity/analysis применены: входы прошли size+blob_sha1 гейты 9/9
  (§5), frame0 oracle 4/4 (§5), анализ — исключительно packaged-конвенцией
  (§8), все analyze/campaign exit=0;
- валидных fresh replica medians ровно по 3 на каждую MEASURED карточку
  (valid_replicas=3 во всех 4 campaign JSON, valid_frame_fraction=1.0);
- итог по карточкам: 2/4 **MATCH** (11b: 73.560609814 внутри
  [72.165683993, 74.533109426]; 53b: 132.41188514 внутри
  [131.049227687, 135.285186059]) и 2/4 **MISMATCH** (0b: 68.389781796 и все
  3 реплики выше ref_max 67.236579608; 32b: 75.180138343 и все 3 реплики ниже
  ref_min 77.4927314) — в обоих MISMATCH-случаях полное согласованное
  directional separation, т.е. по правилу это MISMATCH, а не INCONCLUSIVE;
- отклонения §10 (D1 launch strategy, D2 watcher restart) — процессуальные,
  научное содержание (входы, seeds, шаги, анализ) не затронули, поэтому по
  правилу («технический сбой… не превращается в scientific mismatch») они не
  являются основанием ни для FAILED_TECHNICAL, ни для смягчения исхода;
- WO-уровень: кампания не может считаться REPRODUCED при наличии двух
  карточек с per-card MISMATCH по frozen правилу; INCONCLUSIVE исключён
  (валидных реплик достаточно и separation согласован во всех репликах).
  По published формулировке это «operational reproduction mismatch, не
  автоматический физический NOT_SUPPORTED за пределами claim ceiling».

## 13. Findings

Нумерованный список findings (наблюдаемые исполнителем; portability /
документация / интерфейс пакета / окружение, включая friction, не повлиявший
на результат):

- **F1 (документация пакета, косметика):** `RIGHTS.json` содержит
  `"package_version": "0.1.0"` при `VERSION` = 0.1.1 и
  `RELEASE_MANIFEST.json` = nanolab-components 0.1.1. `reproduce.py verify`
  при этом проходит (ok=true, 42 files, 0 errors) — рассинхронизация не
  блокирует, но метаданные прав в пакете противоречат версии релиза.
  Выявлено при целостности пакета (§3).
- **F2 (friction watcher-инфраструктуры, на конвенцию не влияет):
  информационная строка `completeness.txt` "last_step" некалибрована.**
  `analyze_all.sh` вычисляет `last_step = t_traj / 0.005`, но в pinned oxDNA
  `traj.dat` печатает `t` как счётчик шагов (последний кадр 0b: t = 200000;
  32b/53b: t = 148000), а `energy.dat` — как шаг×dt (1000.0000 / 750.0000),
  поэтому эхо-строка показывает 40000000/29600000 вместо шагов 200000/148000.
  Значение нигде не используется как гейт: полнота и окно считаются
  packaged `analyze_hinge.py` (frames_in_window / frames_valid_in_window /
  engine_exit_code в `<ID>_analysis.json` — авторитетный источник), и обе
  единицы согласованно подтверждают полную траекторию. Расхождение единиц
  времени traj/energy в пакете нигде явно не документировано — потенциальный
  источник ошибок у стороннего пользователя (у нас — только косметика в логе).
- **F3 (окружение, friction без влияния):** git-транспорт через прокси был
  нестабилен при скачивании pinned-исходников движка; использован
  разрешённый карточкой tarball-путь (codeload) с проверкой sha256 (§4).
  На сборку/воспроизводимость не повлияло (pristine-исходники, 0 правок).
- **F4 (наблюдение, не дефект):** при `print_conf_interval = 4e3` (verbatim
  из upstream) и steps = 150000 последний кадр печатается на шаге 148000, а
  не 150000; packaged-конвенция корректно включает все кадры в окно
  t ≤ 150000 (frames_in_window = 37 = frames_total). Отмечено, чтобы
  исключить ложную тревогу по «неполной» траектории при чтении логов.

Других portability/документационных проблем пакета не наблюдалось; конвенция
угла самодостаточна (frame0 oracle 4/4), классификационное правило
воспроизводимо из packaged-кода.

---

## Self-check (финализация, административная)

Self-check финализатора (административная проверка, не научное содержание):
все 13 секций шаблона заполнены, 0 плейсхолдеров; все числа секций 7–9 —
наблюдаемые значения из файлов прогонов и packaged-анализа (`*_analysis.json`,
`campaign_<v>.json`, `completeness.txt`), без пересчётов; `artifact_manifest.json`
пересчитан после финализации этого отчёта (включает финальную версию отчёта и
`run_output_digests.json`); `run_output_digests.json` покрывает все 12 валидных
прогонов (84 записи). Никаких scientific changes: seeds, пороги, envelope,
окна, анализ и классификации взяты из frozen protocol и packaged-артефактов
без изменений.
