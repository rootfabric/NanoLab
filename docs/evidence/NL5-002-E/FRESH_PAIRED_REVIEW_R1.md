# FRESH_PAIRED_REVIEW_R1 — независимый fresh Scientific Review отчёт по EX-NL5-002-E-R1 (paired platform-sensitivity analysis)

```text
ВЕРДИКТ: PASS
WO-вердикт под обзором: PLATFORM_INSENSITIVE — ВОСПРОИЗВЕДЁН ТОЧНО (bit-exact)
Рецензент: fresh session, без предшествующего контекста; все числа пересчитаны
собственным кодом (см. /tmp/reviewer_p2/, скрипты task1/task2/task3 — собственная
реализация, operator-код НЕ запускался для production-чисел).
Reviewed HEAD: 3941d2751f338a9f08ef960706d1c17a454307fd
  (branch work/nl5-002-e-platform-sensitivity-r1, working tree чистый)
Дата отчёта: 2026-09-26 (host outenemy)
```

## 0. Резюме для Director / Verifier

1. **Полнота (20+20)**: 20 финальных P1 и 20 P2 packaged-анализов присутствуют в Git;
   все run_id/variant/window/steps/exit-code/frame-gates соответствуют пинам; паринг
   полный и однозначный (по 1 P1- и 1 P2-медиане на каждый variant × seed S001–S010).
   470/470 собственных проверок PASS, 0 FAIL.
2. **P2 raw replay (независимый)**: я запустил packaged-анализатор
   (nanolab-components 0.1.1, `convention/analyze_hinge.py`, без изменений) сам на всех
   20 сырых P2 прогонах из `/home/rdpuser/nl5-002-e-p2/workspace/runs/` — **20/20
   отчётов bit-exact совпали с committed P2 analysis JSON по ВСЕМ полям**, включая
   покадровые углы, гейты и `replica_median_deg`.
3. **Статистика (собственная реализация frozen-плана)**: shift, CI95, MAD, within,
   ratio, вердикты по вариантам и WO-вердикт — **все числа совпали с
   `evidence/paired/paired_platform_sensitivity.json` exact (bit-level)**.
4. **Recovery-целостность (P1)**: retry-политика append-only подтверждена на уровне
   committed-артефактов (114 superseded-попыток, цепочки без пропусков, сиды
   неизменны, все причины supersede в логах — внешние kill'ы mid-run без exit code).
   Канал отбора по научным значениям **отсутствует** (обоснование в §4). Ответ на
   обязательный вопрос event 0007: **ранний P2-dispatch и P1 retry-цепочки НЕ
   инвалидируют paired-инференс (НЕТ)** — с оговоркой о P1 raw-replay gap (§6).
5. **Материальных расхождений не найдено.** Список findings — все minor/cosmetic,
   вердикт не меняют (§5).

## 1. Проверка полноты и пинов (Task 1)

Собственный скрипт: `/tmp/reviewer_p2/task1_completeness.py` (470 OK / 0 FAIL).

| Блок | Проверка | Результат |
|---|---|---|
| Инвентарь | P1 analysis JSON = 20; P2 analysis JSON = 20 | PASS (20/20) |
| Файлы P1 | filename == run_id; variant ∈ {0b,32b}; window_steps 200000/150000; `engine_exit_code=0`; `frames_valid_in_window == frames_in_window == 50 (0b) / 37 (32b)`; `replica_median_deg` присутствует; `rule_id=NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`; frames[] длиной 50/37 | PASS 200/200 проверок |
| Файлы P2 | те же пины | PASS 200/200 проверок |
| Финальные попытки P1 | 0b: S001–S008 base, S009-R21, S010-R14; 32b: S001-R14, S002–S006-R13, S007–S010 base — совпадает с event 0006 и digest-манифестом | PASS |
| Паринг | для каждого variant × seed S001–S010 ровно одна P1- и одна P2-медиана; 10 пар на вариант | PASS (10+10) |
| Сиды | P1 runmap == P2 runmap == frozen WO-список (S001=1259289227 … S010=744386736); steps-пины 200000/150000 | PASS |
| P1 digest-манифест | expected==recorded==20; missing=[]; duplicate_check=true; все 20 финалов seed==frozen, steps==pin, exit=0, status=COMPLETE_EXIT_0, 10 артефактов sha256+size | PASS |
| P1 retry-цепочки | 8 слотов; суммарно 114 superseded-попыток (0B-S009:21, 0B-S010:14, 32B-S001:14, 32B-S002..S006:13); ID цепочек непрерывны (base, -R1..-R(k-1)); final_attempt_id == -Rk без пропусков | PASS |
| P2 digest-манифест vs raw | 20/20: run_meta.json, exit_code.txt (`EXIT_CODE: 0`), exit_code_raw.txt (`0`), input-файлы (`seed = <frozen>`, `steps = <pin>`), sha256(conf/top/input) — raw == manifest == meta | PASS 20/20 |
| Cross-platform input identity | sha256(0b.conf)=506c41fc…, sha256(0b.top)=cd046127…, sha256(32b.conf/top) идентичны у всех 10 P2 прогонов и == дайджестам, записанным P1-легом в своём манифесте | PASS |
| frame0 oracle (доп.) | мой собственный запуск `analyze_hinge.py frame0` на P2-raw входах: 0b=66.886745865, 32b=77.477102136 — совпало с P1-оракулами (evidence/logs/frame0_*.json) | PASS |
| completeness.txt | P1 (20 строк) и P2 (20 строк) побайтно сходятся с analysis JSON | PASS 40/40 |

## 2. Независимый P2 raw replay (Task 2)

Собственный драйвер `/tmp/reviewer_p2/task2_recompute.py`; анализатор запускался
из `workspace/package/convention/analyze_hinge.py` (nanolab-components 0.1.1)
с `--manifest convention/arm-manifest-<v>.json`, `--window` 200000 (0b) / 150000 (32b),
`--exit-code-file <run>/exit_code.txt`. Отчёты: `/tmp/reviewer_p2/reports_p2/`.

Результат: **20/20 отчётов совпали с committed `evidence/p2/analysis/*_analysis.json`
exact по всем скалярным полям И по каждому кадру** (angle_deg, gate-метрики, valid).
`replica_median_deg` — bit-exact во всех 20 случаях. Различий не найдено.

Дополнительно проверено: `replica_median_deg` == медиана валидных углов в окне по
кадрам отчёта (для 50-кадровых окон медиана считается как `a*0.5 + b*0.5` двух
средних значений — формула quantile-интерполяции анализатора; наивный
`statistics.median` даёт `(a+b)/2`, расхождение ≤ 5·10⁻¹³°, см. Finding F-4).

## 3. Независимая статистика по frozen-плану (Task 3)

Собственная реализация `/tmp/reviewer_p2/task3_stats.py` (operator-код не
импортировался и не запускался). Входы: committed P1-медианы (артефактный уровень —
raw P1 недоступны на этом хосте, §6) + мои raw-верифицированные P2-медианы.

### 3.1 Мои числа (primary-реализация: `random.Random(902107).randrange`, h=(B−1)p, lo/hi=floor/ceil, линейная интерполяция)

| Величина | 0b (200000 шагов, 50 кадров) | 32b (150000 шагов, 37 кадров) |
|---|---|---|
| d_i (диапазон, deg) | −4.5022 … +2.4537 | −3.5956 … +2.5677 |
| **shift_v** | **+0.6846952455000022°** | **−1.207386400499999°** |
| MAD(P1) raw | 1.101103671500006° | 1.299773310500001° |
| MAD(P2) raw | 1.4081993214999997° | 0.5319497240000004° |
| **within_v** = median(MAD1,MAD2) | **1.2546514965000028°** | **0.9158615172500006°** |
| **CI95 bootstrap** (B=10000) | **[−0.5502640344999961°, +1.199043819°]** | **[−2.090432681000003°, +2.1491488160000074°]** |
| CI содержит 0 | да | да |
| **ratio_v** = \|shift\|/within | **0.5457254444043144** | **1.3183067284291425** |
| Вердикт варианта | **PLATFORM_INSENSITIVE** (ветка CI∋0) | **PLATFORM_INSENSITIVE** (ветка CI∋0; ratio≥1 недостаточно по frozen-правилу) |

**WO-level вердикт: PLATFORM_INSENSITIVE** (оба варианта INSENSITIVE).

Сравнение с `paired_platform_sensitivity.json`: **bit-exact совпадение** всех 40+ чисел
(10×d_i × 2 варианта, shift, MAD×2, within, ratio, оба конца CI, флаги) и всех трёх
вердиктов. Таблица per-seed d_i (округлено до 4 знака; в JSON совпало exact):

```text
0b : +0.7125 +0.6996 −4.5022 −1.6206 +2.4537 +0.8601 +0.5201 +0.6698 +0.2162 +1.6856
32b: +2.5677 +2.2337 −1.3696 −2.4744 −1.7065 −1.9233 +2.1491 −3.5956 +0.7316 −1.0451
```

### 3.2 Robustness bootstrap-RNG (находка F-3)

Frozen-план фиксирует `random.Random(902107)`, B=10000, N=10 индексов с
возвращением из 0..9, но НЕ фиксирует конкретный stdlib-вызов. Я прогнал 4 идиомы:
`randrange(n)`, `randint(0,n−1)`, `choice(range(n))`, `choices(range(n),k=n)`.
**Все 4 дали bit-идентичные CI95 на обоих вариантах** (распределение бутстрап-медианы
дискретно; квантили 2.5%/97.5% попадают в одни и те же дискретные значения при всех
потоках). Вердикты не зависят от идиомы. Формула оператора
`a[lo]·(1−frac)+a[hi]·frac` алгебраически эквивалентна frozen-формуле
`a[lo]+(h−lo)(a[hi]−a[lo])`; на этих данных результаты bit-идентичны.

### 3.3 Соответствие `paired_analysis.py` frozen-плану (Task 3b)

Прочитан весь `evidence/paired/paired_analysis.py`. Соответствие plan'у:

- d_i, shift, raw MAD (без 1.4826), within, ratio с degenerate-правилом within=0 — **соответствует**;
- bootstrap: fresh `random.Random(902107)` на вариант, 10000 итераций, парные индексы
  с возвращением, статистика = медиана выбранных d_i — **соответствует**;
- percentile CI95 с линейной интерполяцией, правило `ci_contains_zero = lo ≤ 0 ≤ hi`,
  разбиение вердиктов SENSITIVE/INSENSITIVE/INCONCLUSIVE и WO-агрегация —
  **соответствует**; разбиение полное и непересекающееся;
- final-attempt loader (max `-R<N>`, иначе base) детерминирован и совпал с
  digest-манифестом; сиды паринга берутся из committed runmap'ов (в отчётах
  анализатора `seed: null` — задокументированный B-R2-прецедент) — **корректно**.

Отклонений от frozen-плана НЕ обнаружено. Замечания косметического уровня: (а)
недвусмысленность stdlib-вызова RNG устранена моей проверкой робастности (F-3);
(б) `data.get("window_steps") or data.get("window")` — fallback, на этих данных
неактивен; (в) эквивалентная форма интерполяции (см. 3.2).

## 4. Recovery-целостность P1 (Task 4)

Источники: `RECOVERY_INCIDENTS.md`, `ORCHESTRATION_DEVIATION_DISCLOSURE.md`,
`EARLY_P2_DISPATCH_DEVIATION.md`, events 0003–0007,
`evidence/p1/logs/recovery_scheduler.log` (241 строка) и `launch_log_full.txt`,
`run_output_digests_p1.json`.

**Что подтверждено на committed-артефактах:**

1. **Append-only, сиды неизменны**: 8 retry-цепочек непрерывны (base, -R1…-R(k−1)
   superseded; финал -Rk, без переиспользования ID); в digest-манифесте у каждого
   финала записан seed == frozen-сиду слота; P2-сид ы сырых input-файлов == тем же
   frozen-значениям (§1). Ни один финальный ID не дублируется (duplicate_check=true,
   missing=[]).
2. **Перечисление superseded-попыток полное**: ровно 114 попыток в 8 цепочках
   (21+14+14+13+13+13+13+13 = 114), совпадает с event 0006.
3. **Нет перезапуска exit=0 прогона (в пределах зафиксированного)**: все 114 записей
   `PREPARED … (supersedes …)` в recovery_scheduler.log содержат единственную форму
   причины: `technical: process killed mid-run (host/WSL restart), no exit code,
   truncated trajectory`. Ни одной записи supersede с завершённым (exit≠null)
   прогоном; ни одного вхождения научных величин (angle/median/verdict) в логи
   планировщика (grep — 0 совпадений). 0b S001–S008 (exit=0 wave-1) не имеют
   retry-цепочек вовсе.
4. **Хронология согласована**: wave-1 завершена 2026-09-20 18:54–18:59Z (event 0003);
   WSL-терминации 2026-09-20 ~21:28Z и 2026-09-25 ~12:55Z; финалы retry-цепочек
   2026-09-25 21:44–22:40Z; 32b S007–S010 (никогда не запускавшиеся) запущены
   21:47–21:52Z, завершены 2026-09-26 00:16–00:23Z; P1-свидетельство закоммичено
   (eb8ccf0) 2026-09-26 01:20Z (event 0006); paired-анализ — после (event 0007,
   01:50Z). P2-лег: dispatch 2026-09-21 (ранний, Director override — раскрыто),
   завершение 2026-09-23, zero retries, zero superseded.

**Возможен ли отбор по научным значениям? Оценка: НЕТ (нет канала).**

- Решение о supersede принималось планировщиком по факту внешней смерти процесса
  (WSL `--shutdown` от параллельного CI-цикла), т.е. по событию, независимому от
  содержимого траектории; траектория при этом обрывалась и по протоколу никогда не
  анализировалась («no partial trajectories are ever analyzed»).
- Угол Хинга не вычислялся во время кампании вовсе (только packaged-анализатором
  пост-фактум; monitoring boundary = процесс/CPU/steps/stderr/exit-code). У
  планировщика не было входа, коррелированного с будущей медианой.
- Финал слота = первая попытка, дожившая до exit=0 (механическое правило «первый
  завершившийся»), а не выбор по значению. При фиксированном сиде/входах
  однопоточный CPU DOUBLE-движок детерминирован: любая завершившаяся попытка слота —
  детерминированная реплика той же реализации протокола, поэтому даже гипотетический
  «перебор до завершения» не создаёт сдвига распределения.
- Независимая индикация отсутствия селекции: прерванная P1-лега (114 попыток) и
  непрерывная P2-лега (0 retries) дают согласованные парные разности без
  систематики знака по «пересеянным» слотам: у 8 повторных P1-слотов d_i = +0.71,
  +0.70, −4.50, −1.62, +2.57, +2.23, −1.37, −2.47, −1.71, −1.92° (0b+32b) —
  разброс тот же, что и у неповторных слотов; против «подгонки» говорит и то, что
  итог отрицательный (H0 не отвергнут — селекция была бы выгодна лишь стороннику
  MISMATCH-нарратива, а её нет).
- Ответ на обязательный вопрос (event 0007): **ранний P2-dispatch + P1 retry-цепочки
  НЕ инвалидируют paired-инференс**: паринг определён frozen-сидами и идентичным
  протоколом, а не порядком запуска; P2-физика не могла наблюдать P1-результаты
  (P1-медианы не существовали до 2026-09-26, P2-анализ завершён 2026-09-23);
  статистический план применён только после появления обоих легов в Git.

## 5. Findings (все — minor/cosmetic; материальных нет)

| ID | Серьёзность | Находка | Влияние на вердикт |
|---|---|---|---|
| F-1 | minor (process, раскрыто) | Ранний P2-dispatch (2026-09-21) нарушил текст собственного dispatch-gate паспорта_p2 («P2 physics only AFTER durable P1 evidence commit»); Director override задокументирован (EXECUTION_ORCHESTRATION_DEVIATION=YES, SCIENTIFIC_PROTOCOL_MUTATION=NO) | нет: пины неизменны, паринг по сидам, статистика после обоих легов |
| F-2 | minor (bookkeeping) | Расхождение времён override/dispatch: passport_p2 `dispatched_at_utc=19:26Z`, `gate_resolution=19:25Z` vs event 0004 «decision at 21:25Z» и первый P2-прогон 21:27:22Z. Материальный факт (dispatch ДО P1-evidence) не оспаривается | нет |
| F-3 | minor (reproducibility) | Frozen-план не пинует конкретный stdlib-вызов бутстрап-RNG (randrange/randint/choice/choices). Проверено: на этих данных все 4 идиомы дают bit-идентичные CI и одинаковые вердикты; рекомендовано для будущих revision пиновать `random.Random.randrange` | нет |
| F-4 | cosmetic | `replica_median_deg` при чётном числе кадров = `a·0.5+b·0.5` (quantile-интерполяция анализатора), а не `statistics.median` → расхождения до 5·10⁻¹³° с наивным пересчётом в 5 из 10 файлов 0b (32b нечётный — точно). Конвенция ОДНА на обе платформы | нет |
| F-5 | cosmetic | В analysis JSON обеих легов `energy.rows=0`: `parse_energy` ждёт целочисленный первый столбец, а energy.dat 4-колоночный с float-первым полем. Дрейф энергии вёлся отдельно (P1: hinge_energy.dat, rows=2001, drift ≤ 0.0004; P2: completeness.txt last_energy_step_printed). Вне frozen-плана, симметрично на обеих легах | нет |
| F-6 | minor (verification gap) | См. §6: P1 raw-replay и exit-коды 114 superseded-попыток физически находятся только на авторской машине | нет для чисел; фиксируется как Verifier-phase условие |

## 6. Ограничения (limitations)

1. **P1 raw-replay gap**: сырые P1 траектории лежат на авторской WSL2-машине
   (DESKTOP-QNAGSTI, вне этого хоста). P1-медианы проверены только на уровне
   committed-артефактов: внутренняя согласованность 20 analysis JSON ↔
   completeness.txt ↔ digest-манифест ↔ event 0006 ↔ пары сид/шаги. **Fresh
   Verifier-phase условие: replay всех 20 P1 финальных прогонов (и хотя бы выборки
   из 114 superseded-директорий — проверка «нет exit=0 среди superseded») на
   авторской машине.**
2. Заявление «ни один exit=0 прогон не перезапускался» подтверждено журналом
   планировщика и целостностью цепочек, но независимая проверка каждого из 114
   superseded-состояний (exit-коды/дайджесты не коммитились) возможна только на
   авторской машине (см. п.1).
3. P2-лег верифицирован максимально строго (raw replay 20/20 bit-exact + frame0
   oracle + sha256-цепочка), но моя проверка не может исключить гипотетическую
   подмену сырых данных НА ЭТОМ хосте ДО момента коммита digest-манифеста
   (2026-09-23); цепочка доверия = sha256 в Git-манифесте vs сырые файлы на диске —
   совпадает сегодня (проверено мной: conf/top/input, 20/20).
4. Бутстрап-CI — percentile-метод по frozen-плану; BCa/другие методы не применялись
   (вне плана). n=10 на ячейку — бюджет frozen WO; мощность ограничена дизайном.

## 7. Методы (воспроизводимость обзора)

- Task 1: `python3 /tmp/reviewer_p2/task1_completeness.py` — 470 проверок (пины,
  паринг, манифесты, sha256 raw-входов, цепочки retry). Результат: ALL PASS.
- Task 2: `python3 /tmp/reviewer_p2/task2_recompute.py` — 20 запусков packaged
  `analyze_hinge.py run` на сырых P2 прогонах; полное пополевое и покадровое
  сравнение с committed JSON. Результат: 20/20 EXACT. Отчёты: `/tmp/reviewer_p2/reports_p2/`.
- Task 3: `python3 /tmp/reviewer_p2/task3_stats.py` — собственная реализация
  frozen-плана (медианы, raw MAD, ratio-правило, bootstrap 4 идиомы, percentile
  h=(B−1)p с floor/ceil и линейной интерполяцией, вердикт-разбиение, WO-агрегация),
  exact-сравнение с `paired_platform_sensitivity.json`. Результат: ALL PASS (bit-exact).
  Сводка: `/tmp/reviewer_p2/task3_stats_summary.json`.
- Task 4: разбор RECOVERY_INCIDENTS.md, disclosure-документов, events 0003–0007,
  recovery_scheduler.log/launch_log_full.txt (все 114 supersede-причин), манифестов.
- Не изменён ни один файл репозитория, кроме настоящего отчёта; operator-код для
  production-чисел не выполнялся; протокольные файлы не тронуты; push не выполнялся.

## 8. Итог

```text
FRESH SCIENTIFIC REVIEW VERDICT: PASS
  - пары 10/10 + 10/10 подтверждены; P2 raw replay 20/20 bit-exact;
  - статистика frozen-плана воспроизведена bit-exact независимо;
  - WO-вердикт PLATFORM_INSENSITIVE подтверждён (0b: shift +0.6847°, CI95
    [−0.5503°, +1.1990°] ∋ 0, ratio 0.5457; 32b: shift −1.2074°, CI95
    [−2.0904°, +2.1491°] ∋ 0, ratio 1.3183; оба варианта INSENSITIVE);
  - отклонений от frozen-плана в paired_analysis.py не найдено;
  - ранний P2-dispatch и P1 retry-цепочки НЕ инвалидируют paired-инференс;
  - условия: Verifier-phase P1 raw-replay на авторской машине (§6.1) и
    независимый fresh Verifier + Director gate (Implementer не self-accept).
NL5 = IN_PROGRESS, external_reproductions = 0, NL6-001 = LOCKED — без изменений.
```
