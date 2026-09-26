# FRESH_PAIRED_VERIFY_R1 — независимый fresh Verifier отчёт по EX-NL5-002-E-R1 (paired platform-sensitivity, механика исполнения)

```text
ВЕРДИКТ: VERIFIED
Уровень вердикта: committed-артефакты (полная цепь 8e6a1b2..c14759a) + P2 raw
(полная перезагрузка хэшей 60/60 + engine binary) + статистика (три независимые
реализации, bit-exact) + NC1–NC4. Единственный ОТКРЫТЫЙ сегмент — сырое
воспроизведение P1 raw→median на P1-машине: делегировано, см. раздел 7 и
P1_RAW_REPLAY_COMMANDS_R1.md. Это НЕ отменяет верификацию committed-цепочки.
Verifier: fresh session, без предшествующего контекста; механика проверена
собственными командами/кодом (скретч /tmp/verify_p1_*), reported results
НЕ принимались на веру.
Verified HEAD: c14759a3fb4c0fc4896cb1c223274cb6b6e3a847
  (branch work/nl5-002-e-platform-sensitivity-r1, working tree чистый на момент
  начала проверки; далее добавлены только 2 новых файла отчёта, ничего не
  модифицировано, push не выполнялся)
Дата отчёта: 2026-09-26 (host outenemy)
```

## 0. Резюме

1. Цепь коммитов от START (8e6a1b2) до HEAD (c14759a) линейная, append-only:
   111 файлов под `docs/work/executions/EX-NL5-002-E-R1/**` и
   `docs/evidence/NL5-002-E/**` — все только `A` (добавление), 0 модификаций,
   0 удалений, ни один файл не затронут дважды.
2. Все 4 замороженных протокольных блоба байт-идентичны своим introducing-коммитам.
3. Все пересчитанные хэши сошлись: 40/40 analysis JSON (метаданные тоже),
   60/60 сырых P2 файлов (sha256+size), engine binary sha256+size exact.
4. Паринг полный и однозначный: 10+10 пар, сиды = замороженному списку на обоих
   легах, steps 0b=200000/32b=150000, P1 final attempts 1:1 к слотам.
5. Статистика: `paired_analysis.py` = verbatim реализация
   `passport.statistics_frozen_pre_data`; отклонений НЕТ. Bit-exact
   воспроизведение: (а) повторный запуск самого `paired_analysis.py` на /tmp
   копии дерева — байт-идентичный JSON; (б) собственная третья реализация
   верификатора — bit-exact по всем числам; (в) twin tool
   `paired_stats_platsens.py` — `SELF_TEST: PASS`, на данных — exact match
   (через документированный адаптер, см. 5.3).
6. NC1–NC4: PASS (NC3 — PASS с документированной безвредной особенностью
   дискретного бутстрепа).
7. WO-вердикт PLATFORM_INSENSITIVE подтверждён по замороженному правилу
   решения (0b и 32b: CI95 содержит 0).

## 1. EXACT HEAD и append-only цепь — PASS

```bash
git rev-parse HEAD        # c14759a3fb4c0fc4896cb1c223274cb6b6e3a847
git status --porcelain    # пусто (до создания файлов отчёта)
git branch --show-current # work/nl5-002-e-platform-sensitivity-r1
git log --format='%h %p' 8e6a1b2..HEAD
```

- 8 коммитов, у каждого ровно один родитель; 1376575 → parent 8e6a1b2 (START).
  Линейность подтверждена.
- `git diff-tree --name-status -r <c> -- docs/work/executions/EX-NL5-002-E-R1 docs/evidence/NL5-002-E`
  для каждого коммита: суммарно **111 × `A`**, `M`=0, `D`=0.
- Контроль «файл затронут более одного раза»: пусто — переписываний истории
  файлов нет, цепь append-only.

## 2. Отсутствие мутации протокола — PASS

`git log --follow` по каждому пути: после introduction ни один коммит файл не
трогал. Сравнение blob-хэшей introduction → HEAD:

| файл | introduction | blob sha256 (git) | статус |
|---|---|---|---|
| `docs/work/WO-NL5-002-E-R1.md` | 4d6542f | `98719af3d2c4294dc25a51918a2b7f0c7fc1cb43` | IDENTICAL |
| `docs/evidence/NL5-002-E/PREREGISTRATION_FREEZE_R1.md` | 8d1eafd | `638ad73ffd87514c5d703fd66a2be926ec00d519` | IDENTICAL |
| `docs/work/executions/EX-NL5-002-E-R1/passport.json` | 8e6a1b2 | `ef29353edc12a960d1b045b92e56808f69210dcd` | IDENTICAL |
| `docs/work/executions/EX-NL5-002-E-R1/evidence/p2/passport_p2.json` | cabdb56 | `00c84fbaec4523270650431de49777e9c53f5845` | IDENTICAL |

## 3. Артефактные хэши — PASS

### 3(a) Committed analysis JSON (P1 20 + P2 20 = 40)

Собственный скрипт: sha256 пересчитан для каждого файла; имя файла ↔ embedded
`run_id` ↔ `variant` ↔ `window_steps` ↔ запись манифеста
(`run_output_digests_p1.json` / `run_output_digests_p2.json`): 40/40 OK, 0 ошибок.
P1: embedded `seed` в каждом analysis JSON равен сиду слота манифеста (20/20).
P2: embedded `seed` = `null` во всех 20 — упакованный анализатор вызван без
`--seed` (у `analyze_hinge.py` это опциональный аргумент, default None);
связка seed↔run_id для P2 держится на committed runmap +
`run_output_digests_p2.json` (значения = замороженному списку). Это задокументировано
заранее в `PAIRED_PROVENANCE.md` как принятый B-R2 прецедент — отклонением не
считаю. P1 final attempt ↔ analysis file stem: 20/20 exact.

### 3(b) P2 raw (workspace /home/rdpuser/nl5-002-e-p2/workspace)

Пересчитано 60/60 файлов (20 × traj.dat, energy.dat, last_conf.dat) по путям из
`run_output_digests_p2.json`: **sha256 и размер — 60/60 exact совпадение, 0 MISMATCH**.

### 3(c) Engine binary

`sha256sum workspace/engine/build/bin/oxDNA` =
`f590cc872c2989a0aee991517231b2a92db14f851757183c653b47e501f0b9b4` =
значение в `evidence/p2/logs/build_provenance.txt`; size = 3380728 B = заявленному.
Все 20 записей `runs[]` манифеста P2 ссылаются на этот же бинарник.

## 4. Корректность паринга — PASS

Собственный скрипт по обоим манифестам + обоим runmap:

- 10 полных пар на вариант (0b, 32b); отсутствующих слотов нет.
- Сиды: P1 manifest = P2 manifest = P1 runmap = P2 runmap (`seeds`) = замороженному
  списку для всех S001–S010 и обоих вариантов, включая
  S001=1259289227, S002=1358106528, S003=1524307444, S004=601855227,
  S005=274288237, S006=972234272, S007=1934775205, S008=1747973984,
  S009=880427736, S010=744386736.
- Steps: 0b=200000 и 32b=150000 на ОБОИХ легах (20/20 записей).
- P1 final attempts уникальны 1:1 к слотам (20 уникальных):
  оригиналы — 0B S001–S008 и 32B S007–S010; ретраи —
  `0B-S009-R21`, `0B-S010-R14`, `32B-S001-R14`, `32B-S002..S006-R13`.
  Совпадает с заданием и с `PAIRED_PROVENANCE.md`.

## 5. Статистическая реализация против паспорта — PASS (verbatim), отклонений нет

Посимвольная сверка `passport.json → statistics_frozen_pre_data` и
`evidence/paired/paired_analysis.py` (построчно):

| элемент паспорта | реализация | статус |
|---|---|---|
| raw MAD без 1.4826: `median(abs(x_i−median_x))` | `mad()` L42–44 | exact |
| `d_i = median(P2,seed) − median(P1,seed)`; `shift = median(d_i)` | L120–123 | exact |
| bootstrap `random.Random(902107)`, 10000 resamples, парные индексы с возвратом | L38–39, L132–137 (`randrange(n)` × n) | exact (эквивалентная формулировка: паспорт — «индексы», код — прямая выборка d_i; семантика идентична) |
| percentile CI95: `h=(B−1)p; floor/ceil; линейная интерполяция` | `percentile_linear()` L47–55 (`pos=(n−1)·q/100`, `lo=int(pos)`≡floor, `hi=lo+1`) — алгебраически то же; для B=10000, p∈{0.025,0.975}: h=249.975 / 9749.025 | exact |
| `within = median(MAD_P1, MAD_P2)` | L126 | exact |
| ratio degenerate: within==0&shift==0→0; within==0&|shift|>0→INF | L127–130 | exact |
| verdict: SENSITIVE = CI исключает 0 AND ratio≥1; INSENSITIVE = CI содержит 0 OR ratio<0.5; иначе INCONCLUSIVE | L140–146 (включённая нотация `lo<=0<=hi`) | exact |
| WO: both SENSITIVE→SENSITIVE; both INSENSITIVE→INSENSITIVE; else INCONCLUSIVE | L186–191 | exact |

Текстуальных/семантических отклонений НЕ обнаружено. Конвенция (у паспорта не
уточнена, у обеих реализаций одинакова): RNG пересоздаётся заново на каждый
вариант; CI-содержание нуля — включающее.

### 5.1 Committed числа (подтверждены тремя реализациями)

```text
0b : shift = +0.684695246 deg, CI95 = [-0.550264034, +1.199043819] (содержит 0),
     MAD_P1 = 1.101103672, MAD_P2 = 1.408199321, within = 1.254651497,
     ratio = 0.545725444 -> PLATFORM_INSENSITIVE (основание: CI содержит 0;
     ratio 0.5457 >= 0.5, ветка ratio<0.5 не задействована)
32b: shift = -1.207386400 deg, CI95 = [-2.090432681, +2.149148816] (содержит 0),
     MAD_P1 = 1.299773311, MAD_P2 = 0.531949724, within = 0.915861517,
     ratio = 1.318306728 -> PLATFORM_INSENSITIVE (CI содержит 0; правило
     SENSITIVE требует CI исключает 0 AND ratio>=1 — не выполнено)
WO : PLATFORM_INSENSITIVE
```

### 5.2 Три независимые воспроизведения

1. **Повторный запуск `paired_analysis.py`** (на /tmp-копии evidence-дерева,
   production не перезаписывался): созданный JSON **байт-идентичен** committed
   `paired_platform_sensitivity.json` (diff пустой).
2. **Собственная третья реализация верификатора** (независимый код, чтение
   committed analysis JSON, `statistics.median`, `random.Random(902107)`):
   bit-exact совпадение по shift, CI lo/hi, MAD_P1/P2, within, ratio, вердиктам
   обоих вариантов.
3. **Twin tool** `paired_tooling/paired_stats_platsens.py`:
   - `--self-test` → `SELF_TEST: PASS`, exit 0;
   - его собственная реализация ядра сверена с паспортом построчно — verbatim
     (raw MAD; `h=(B−1)p`, floor/ceil, интерполяция; degenerate ratio; вердикты; WO);
   - **прямой запуск на репо-директориях**: exit 1,
     `PAIRED_COMPLETENESS_GATE_FAIL variant=0b missing=['S009','S010']` — это
     ЗАРАНЕЕ ЗАДОКУМЕНТИРОВАННОЕ ограничение загрузчика (`run_id.split("-")[-1]`
     не парсит -R13/-R14/-R21; см. «Tooling note» в PAIRED_PROVENANCE.md).
     Механическое ограничение загрузчика, не статистики;
   - запуск на /tmp-адаптированных копиях (run_id без retry-суффикса, медианы
     не тронуты): **exact match всех 7 метрик × 2 вариантов + WO-вердикт**.
4. Дополнительно: per_seed-таблица committed paired JSON (80 строк) сверена с
   соответствующими committed analysis JSON (p1_run/p2_run/медианы/d_deg) —
   0 расхождений.

## 6. Негативные контролы NC1–NC4 (одноразовые копии в /tmp; production не менялся)

| NC | манипуляция | ожидание | результат | вердикт |
|---|---|---|---|---|
| NC1 | в копии P1 analysis: `replica_median_deg` у `PLATSENS-P1-0B-S001` +5.0 deg; перезапуск twin tool | shift/CI 0b изменятся; 32b не изменится | 0b: shift `+0.684695246 → +0.594910868` (Δ = −0.089784378), CI `[-0.550264034, +1.199043819] → [-2.035616625, +1.192596645]`, MAD_P1 изменён; 32b: bit-идентичен production (локализация) | PASS |
| NC2 | обмен входов (variant_stats(P2, P1)) | shift меняет знак точно на обоих вариантах | 0b: `+0.684695246 → −0.684695246`; 32b: `−1.207386400 → +1.207386400`; остаток `+0.000e+00` (бит точный); CI зеркальны; вердикты остаются INSENSITIVE (CI по-прежнему содержит 0) | PASS |
| NC3 | disposable-копия twin tool с `RNG_SEED = 902108`; production файл не тронут | CI отличается от production | CI совпал с production до 9 знаков на ОБОИХ вариантах — безвредная особенность данных: распределение бутстреп-медиан дискретно, оба квантиля лежат в сериях одинаковых значений длиной 72–275 (0b: run 72/96; 32b: run 89/275), сдвиг счётчиков от +1 к сиду не меняет floor/ceil-позиции. Зависимость от RNG НЕ отсутствует: seed 1 и 99999 двигают CI 0b (`1.199043819→1.192596645`; `[-0.475415283, 1.192596645]`), seed 42 двигает CI 32b lo (`−2.090432681→−1.923319146`). Хардкодинга нет; production файл пинит 902107 (строка 28), `git status`/`git diff` по нему чистые | PASS (с нюансом, документирован выше) |
| NC4 | из копий удалена пара 0b S003 (P1+P2 analysis) | exit != 0, `PAIRED_COMPLETENESS_GATE_FAIL` | `PAIRED_COMPLETENESS_GATE_FAIL variant=0b missing=['S003']`, exit 1 | PASS |

Все NC выполнены на `/tmp/verify_p1_scratch/nc/*`; в репозитории единственные
изменения — два новых файла отчёта (см. раздел 8).

## 7. Делегированный P1 raw replay — ОТКРЫТО

Сырые P1 артефакты доступны только на P1-машине (`~/nanolab-platform-sensitivity-r1/P1/runs`,
WSL2; в Git не публико́вались). Уровень P1, проверенный здесь: committed analysis
JSON ↔ манифест ↔ паринг ↔ статистика (разделы 3–5). Непроверенной остаётся
связь raw→median.

Создан **`docs/evidence/NL5-002-E/P1_RAW_REPLAY_COMMANDS_R1.md`** —
делегированный replay-пак: точные команды packaged-анализатора (по
`p1_recovery/analyze_all_p1.sh`, с обработкой exit-code файла), пины
(пакет 0.1.1 + release manifest sha, engine commit/binary, окна 200000/150000),
таблица всех 20 финальных прогонов с ожидаемыми sha256+size
(trajectory/energy/last_conf) из `run_output_digests_p1.json` и ожидаемыми
`replica_median_deg` из committed P1 analysis JSON (например, 0B S001:
traj `07b2a08c…`, energy `d5a719ab…`, last_conf `78a1cd7d…`, median
67.070882863; 0B S009-R21: median 64.939909073; 32B S001-R14: median
74.892180555), критерии закрытия. Статус: **OPEN — DELEGATED RAW REPLAY**.

## 8. Целостность процесса проверки

- Reviewer-отчёт `docs/evidence/NL5-002-E/FRESH_PAIRED_REVIEW_R1.md`:
  единственный коммит в истории — c14759a (REVIEW), после — не модифицирован
  (`git log` = 1 запись, porcelain чистый). PASS.
- Изменения в репозитории от этой сессии: ТОЛЬКО создание
  `docs/evidence/NL5-002-E/FRESH_PAIRED_VERIFY_R1.md` (этот файл) и
  `docs/evidence/NL5-002-E/P1_RAW_REPLAY_COMMANDS_R1.md`. Ни один существующий
  файл не изменён; эксперименты — в /tmp; push не выполнялся.

## 9. Итог

**VERIFIED** на уровне: committed-цепь (append-only, без мутации протокола),
все пересчитанные хэши (40 analysis + 60 P2 raw + engine binary), полный и
однозначный паринг, verbatim-статистика с тройным bit-exact воспроизведением,
NC1–NC4 PASS. WO-вердикт PLATFORM_INSENSITIVE следует из замороженного правила
решения и подтверждён. Открытый делегированный сегмент (P1 raw→median на
авторской машине) не подрывает ни одно из подтверждённых здесь утверждений;
его закрытие оформляется по `P1_RAW_REPLAY_COMMANDS_R1.md`.
