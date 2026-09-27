# FRESH_RAW_REPLAY_VERIFY_R1 — независимый fresh Verifier отчёт по делегированному P1 raw replay (EX-NL5-002-E-R1)

```text
ВЕРДИКТ: VERIFIED
Сессия: verify/nl5-002-e-p1-raw-replay-r1 (fresh, без предшествующего контекста;
вердикт основан ТОЛЬКО на Git-фактах, committed-документах и собственном
независимом пересчёте на этой машине; implementer-скрипты/логи читались только
как cross-check, на веру не принимались).
Дата отчёта: 2026-09-27
Проверяемый объект: commit f9ff8cae5203b90f0698e81fdd64867c2e53aac2
  (event 0008 + replay tooling + logs), ветка origin/work/nl5-002-e-platform-sensitivity-r1
Bound TREE: 9fd58d2d82b00a1eac21a3227d789ab1fab78a7c
  (git rev-parse HEAD^{tree} в моём worktree — exact match с заданием)
Окружение: host DESKTOP-QNAGSTI (Windows) + WSL2 Ubuntu для сырого доступа;
raw data ~/nanolab-platform-sensitivity-r1/P1/runs (read-only для этой сессии).
Вся сверка — мой собственный код (python3, скретч вне репозитория), включая
собственное извлечение ожиданий из таблицы P1_RAW_REPLAY_COMMANDS_R1.md и из
run_output_digests_p1.json.
```

## 0. Резюме

1. Event-цепь 0001→0008 append-only: commit f9ff8ca добавляет ровно 6 новых
   файлов (все `A`), события 0001–0007 не изменены; 0008 валидный JSON,
   `event_type = CONTINUATION_CHECKPOINT`, нумерация без пропусков.
2. Независимый hash+size replay сырых P1 файлов: **60/60 sha256 OK и 60/60
   size OK** против ОБОИХ источников одновременно (digest JSON и таблица
   инструкции); source-vs-source (таблица ↔ digest JSON) — 0 расхождений.
3. Независимый median replay упакованным анализатором: **20/20 bit-exact**
   `replica_median_deg` против committed `evidence/p1/analysis/*.json` и
   **20/20 exact-decimal** против таблицы; `MEDIAN_MISMATCHES = 0`.
   Единственное структурное отличие regenerated-vs-committed — поле `seed`
   (см. раздел 5).
4. Протокол не мутирован: package 0.1.1, analyzer sha256, RELEASE_MANIFEST
   sha256, engine binary sha256, engine commit, окна 200000/150000, сиды —
   всё сошлось. NEW_PHYSICS_RUNS = 0, SCIENTIFIC_PROTOCOL_MUTATION = NONE.
5. Замороженный paired-результат не изменён (механическая сверка exact float):
   0b shift_v_deg = 0.6846952455000022, CI95 [-0.5502640344999961; 1.199043819],
   32b shift_v_deg = -1.207386400499999, CI95 [-2.090432681000003;
   2.1491488160000074], оба PLATFORM_INSENSITIVE; WO-level
   PLATFORM_INSENSITIVE. Границы NL5 не тронуты.

## 1. Identity bind и event append-only — PASS

- Worktree создан от exact `f9ff8cae5203b90f0698e81fdd64867c2e53aac2`;
  `git rev-parse HEAD^{tree}` = `9fd58d2d82b00a1eac21a3227d789ab1fab78a7c`
  (совпадает с заданием; иначе проверка была бы остановлена).
- `git diff 0c33ad8..f9ff8ca --stat`: ровно 6 файлов, все только добавление,
  `766 insertions(+)`, `M`=0, `D`=0:
  `events/0008-continuation-p1-raw-replay-verified.json`,
  `evidence/p1/logs/p1_raw_hash_replay_r1.log`,
  `evidence/p1/logs/p1_raw_median_replay_r1.log`,
  `p1_recovery/p1_raw_hash_replay_r1.sh`,
  `p1_recovery/p1_raw_median_replay_r1.sh`,
  `p1_recovery/p1_raw_replay_expectations_r1.json`.
- `git diff 0c33ad8..f9ff8ca` по каждому из событий 0001–0007 — пусто
  (проверено все 7 файлов по отдельности).
- События 0001–0008 существуют, валидный JSON, event_id идут строго 0001..0008
  без пропусков; 0008: `event_id = 0008-continuation-p1-raw-replay-verified`,
  `event_type = CONTINUATION_CHECKPOINT`, `execution_id = EX-NL5-002-E-R1`,
  в summary явно заявлены NEW_PHYSICS_RUNS = 0 и
  SCIENTIFIC_PROTOCOL_MUTATION = NONE.

## 2. Независимый hash+size replay — PASS (60/60 + 60/60)

Метод: мой собственный скрипт сам распарсил таблицу
`P1_RAW_REPLAY_COMMANDS_R1.md` (20 строк) и `run_output_digests_p1.json`
(20 записей `runs[]`, ключи `artifacts.trajectory.dat / hinge_energy.dat /
last_conf.dat`), затем посчитал sha256+size файлов
`runs/<FINAL>/trajectory.dat`, `runs/<FINAL>/hinge_energy.dat`,
`runs/<FINAL>/last_conf.dat` в WSL и сверил против ОБОИХ источников.

```text
HASH_OK: 60/60   SIZE_OK: 60/60
SOURCE_VS_SOURCE (таблица vs digest JSON, sha256+size x60): disagreements = 0
ALIAS-файлы traj.dat/energy.dat в 20 финальных dirs: ОТСУТСТВУЮТ
  (single-name layout; двойные хэши по секции 2 инструкции не требуются)
```

Построчный результат (3/3 файла на прогон):

```text
PLATSENS-P1-0B-S001      | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S002      | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S003      | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S004      | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S005      | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S006      | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S007      | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S008      | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S009-R21  | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-0B-S010-R14  | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S001-R14 | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S002-R13 | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S003-R13 | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S004-R13 | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S005-R13 | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S006-R13 | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S007     | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S008     | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S009     | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
PLATSENS-P1-32B-S010     | trajectory.dat H=OK S=OK | hinge_energy.dat H=OK S=OK | last_conf.dat H=OK S=OK
RESULT: HASH_REPLAY 60/60 PASS, SIZE_REPLAY 60/60 PASS
```

## 3. Независимый median replay (packaged analyzer) — PASS (20/20)

Пины перед запуском (пересчитано мной в WSL):

```text
package/convention/analyze_hinge.py sha256 = 300ecd58703c50aa9e24976ab92e9aac61f9d60e49f18e68a58b131861f3ae60 MATCH
package/RELEASE_MANIFEST.json      sha256 = 88c1f58061f15fde44225900f0577acbf2634d3f4a75fb96a2cedca24fd1bfef MATCH
package VERSION = 0.1.1
engine/build-oxdna-cpu/bin/oxDNA   sha256 = 363356b9789fab8e0dab314bd66f92dc0e3a7e2cb3810e24b031614cebb45058 MATCH (size 3375976 B)
```

Метод: упакованный анализатор запущен мной 20 раз по шаблону секции 2
инструкции (`--trajectory runs/<ID>/trajectory.dat --energy
runs/<ID>/hinge_energy.dat --topology runs/<ID>/<variant>.top --manifest
package/convention/arm-manifest-<variant>.json --variant <variant> --run-id
<ID> --window 200000|150000 --exit-code-file ... --report ...`), отчёты — в мой
отдельный каталог `analysis_verify_raw_replay_r1/` (никакой существующий
файл не перезаписан; движок не запускался). Сравнение: (а) bit-exact строковое
равенство токена `replica_median_deg` regenerated vs committed
`evidence/p1/analysis/<ID>_analysis.json`; (б) exact-decimal (Decimal)
против таблицы инструкции.

```text
MEDIAN_MATCHES: 20/20 (bit-exact vs committed JSON: 20/20; decimal-eq vs таблица: 20/20)
MEDIAN_MISMATCHES: 0
```

Построчный результат:

```text
PLATSENS-P1-0B-S001      | regen=67.070882863 committed=67.070882863 table=67.070882863 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S002      | regen=65.413594877 committed=65.413594877 table=65.413594877 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S003      | regen=68.744738874 committed=68.744738874 table=68.744738874 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S004      | regen=66.24673885  committed=66.24673885  table=66.246738850 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S005      | regen=63.825786126 committed=63.825786126 table=63.825786126 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S006      | regen=67.141783719 committed=67.141783719 table=67.141783719 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S007      | regen=66.922485192 committed=66.922485192 table=66.922485192 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S008      | regen=67.61580222  committed=67.61580222  table=67.615802220 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S009-R21  | regen=64.939909073 committed=64.939909073 table=64.939909073 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-0B-S010-R14  | regen=63.799736969 committed=63.799736969 table=63.799736969 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S001-R14 | regen=74.892180555 committed=74.892180555 table=74.892180555 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S002-R13 | regen=75.624640833 committed=75.624640833 table=75.624640833 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S003-R13 | regen=78.504573777 committed=78.504573777 table=78.504573777 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S004-R13 | regen=74.818110405 committed=74.818110405 table=74.818110405 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S005-R13 | regen=79.110521774 committed=79.110521774 table=79.110521774 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S006-R13 | regen=78.263485501 committed=78.263485501 table=78.263485501 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S007     | regen=74.398740326 committed=74.398740326 table=74.398740326 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S008     | regen=75.859814341 committed=75.859814341 table=75.859814341 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S009     | regen=76.227108343 committed=76.227108343 table=76.227108343 | bit_exact=True decimal_eq_table=True
PLATSENS-P1-32B-S010     | regen=77.417657026 committed=77.417657026 table=77.417657026 | bit_exact=True decimal_eq_table=True
RESULT: MEDIAN_REPLAY 20/20 PASS
```

## 4. Сводная таблица проверок 1–5

| # | проверка | результат | измеренные числа |
|---|---|---|---|
| 1 | Event append-only 0001..0008 | **PASS** | 6 новых файлов, все `A`; diff 0001–0007 пуст; 0008 = CONTINUATION_CHECKPOINT, JSON валиден, пропусков нет |
| 2 | Hash+size replay 60/60 | **PASS** | sha256 60/60 OK, size 60/60 OK против digest JSON И таблицы; таблица↔digest: 0 расхождений |
| 3 | Median replay 20/20 | **PASS** | bit-exact vs committed JSON 20/20; decimal-eq vs таблица 20/20; MEDIAN_MISMATCHES = 0; analyzer+manifest sha MATCH |
| 4 | Нет мутации протокола / нового physics | **PASS** | package 0.1.1; engine binary sha 363356b9… MATCH; engine commit 00dc7fb9…; сиды/варианты/окна digest↔таблица 20/20; 0008: NEW_PHYSICS_RUNS = 0, SCIENTIFIC_PROTOCOL_MUTATION = NONE — противоречий в evidence нет |
| 5 | Paired result и границы NL5 неизменны | **PASS** | 0b shift = 0.6846952455000022, CI95 [-0.5502640344999961; 1.199043819], INSENSITIVE; 32b shift = -1.207386400499999, CI95 [-2.090432681000003; 2.1491488160000074], INSENSITIVE; WO = PLATFORM_INSENSITIVE — все 7 значений exact-eq (float-равенство); NL5 = IN_PROGRESS, external_reproductions = 0, NL6-001 = LOCKED (см. 5.1) |

### 5.1 Границы NL5 (поверхности)

- `evidence/paired/paired_platform_sensitivity.json → nl5_nl6_status`:
  `NL5 = IN_PROGRESS`, `NL6-001 = LOCKED`, `external_reproductions = 0`
  (встроено в сам paired-артефакт) — exact match.
- `project/state.json`: `stage_status.NL5 = IN_PROGRESS`;
  `execution.external_reproductions = 0`; `task_status.NL6-001 = PLANNED` —
  каноническая запись «PLANNED (LOCKED до отдельного NL5 acceptance)»
  (`DIRECTOR_DECISION_R1.md`, `DIRECTOR_ACCEPTANCE_R1.md`,
  `SESSION_LOG.md`), т.е. LOCKED-семантика подтверждена; противоречия нет.
- `git diff 0c33ad8..f9ff8ca` не трогает ни `project/state.json`, ни paired
  JSON, ни какие-либо surfaces — границы не сдвинуты этим коммитом.

## 5. Нотационные наблюдения (раскрытие, не отклонения)

1. **Trailing-zero padding в таблице**: у S004 и S008 табличное значение
   дополнено девятым десятичным знаком нулём, а в JSON/анализаторе он
   отсутствует: S004 таблица `66.246738850` ↔ JSON/regen `66.24673885`;
   S008 таблица `67.615802220` ↔ JSON/regen `67.61580222`. Числа равны точно
   (Decimal-сравнение True в обоих случаях); это чисто нотационный артефакт
   заполнения таблицы, ничего не округлялось и не переписывалось. Остальные
   18 значений совпадают посимвольно.
2. **Поле seed в analyzer-отчётах**: регенерированные отчёты содержат
   `seed: null` (шаблон команды секции 2 не передаёт `--seed`), committed
   копии во всех 20 файлах несут точный frozen seed (int, совпадающий с
   таблицей и digest JSON: 20/20). Полный структурный leaf-diff
   regenerated-vs-committed у меня: ровно одно отличие на прогон — `seed`;
   все остальные поля идентичны. Это задокументированный прецедент (event
   0004, `PAIRED_PROVENANCE.md`, disclosure в event 0008) — связи
   seed↔run_id держится на committed runmap/digest, научных следствий нет.
3. **Имена файлов на диске**: в 20 финальных run-dirs существуют только
   канонические `trajectory.dat` / `hinge_energy.dat` (алиасы `traj.dat` /
   `energy.dat` из шаблона секции 2 отсутствуют как отдельные файлы —
   single-name layout, предусмотренный инструкцией). Анализатор вызван на
   канонические имена; то же раскрыто в event 0008.
4. **exit-code файл**: форматирование выполнено по правилу инструкции
   (`0` → `EXIT_CODE: 0`), но форматированная копия записана в МОЙ каталог
   `analysis_verify_raw_replay_r1/exit_code_formatted/`, а не в `runs/`
   (каталог прогонов для этой сессии строго read-only).
5. **Гигиена сессии**: ни один существующий файл под
   `~/nanolab-platform-sensitivity-r1/P1/runs/` и в workspace не изменён; в
   WSL workspace создан единственный новый каталог
   `analysis_verify_raw_replay_r1/`; oxDNA не запускался (никакого physics,
   retries, новых сидов); скретч-скрипты верификатора лежат вне репозитория
   и вне workspace; в Git-worktree изменён/добавлен только этот файл отчёта.

## 6. Итог

Делегированный шаг P1 raw replay закрыт и независимо подтверждён: сырые
файлы на P1-машине байт-в-байт соответствуют обоим committed-источникам
(60/60 хэшей и 60/60 размеров), перегенерация упакованным анализатором
воспроизводит все 20 committed `replica_median_deg` bit-exact, протокольные
пины не тронуты, нового physics нет, замороженный paired-результат и границы
NL5 (NL5 = IN_PROGRESS, external_reproductions = 0, NL6-001 = LOCKED)
неизменны.

**VERDICT: VERIFIED**
