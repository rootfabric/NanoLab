# Fresh Review — NL5-001-C (EX-NL5-001-C-R1): clean release reproduction

- **Reviewer:** fresh independent REVIEWER (новая сессия; implementation/прогоны/анализ subject не выполнял, доступа к чату Implementation/Director не имел)
- **Дата review:** 2026-09-17
- **REVIEW_VERDICT: PASS**
- **Scientific conclusion (отдельно, по фиксации фактов):** classification facts воспроизведены независимо; интерпретация 11b INCONCLUSIVE остаётся открытой (out of scope этого review, не PASS и не MISMATCH)

## Verdict

**PASS.** Все заявленные результаты EX-NL5-001-C-R1 независимо перепроверены по raw-траекториям: 12/12 пер-репличных медиан воспроизведены в пределах frozen-конвенции округления отчётов (≤ 4.7e-10 deg при round-to-9-digits), все 4 классификации воспроизведены независимо (3 MATCH + 1 INCONCLUSIVE), frozen-протокол не менялся после старта, negative/inconclusive исход 11b сохранён честно, инварианты (74b, reference seeds, canonical state, allowed paths) соблюдены, artifact-manifest 112/112 sha256 подтверждён против живых raw-файлов. Findings — только minor observations, ни одно не влияет на classification facts.

## Exact subjects

- **Reviewed head (subject):** `work/nl5-001-c-clean-reproduction-r1` @ `b056db27a6cb9471f75fed33f0f7e062ecf6d3cc`
- **Live remote check:** `git fetch origin` → `origin/work/nl5-001-c-clean-reproduction-r1` = `b056db27a6cb9471f75fed33f0f7e062ecf6d3cc` — **совпадает с reviewed head**
- **Base:** `main` @ `6577f8bb5fcf5f97ad40fadfdbbc34e9f0c970fc` — подтверждён предок (`git merge-base --is-ancestor` → ok)
- **Commits on branch:** `5b2d440` (START, frozen protocol) → `ab3574b` (batch 1) → `ebaedcf` (correction event 0003) → `b056db2` (final)
- **Raw artifacts (вне Git):** `/home/rdpuser/nl5-001-c-env/run-EX-NL5-001-C-R1/` — живы, read-only использованы для независимого пересчёта
- **Rule:** `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` (`docs/release/REPRODUCTION_RULE_V0_1.md` + `scripts/release/reproduction_rule.py`)
- **PR:** отсутствует (создание возможно позже через токен) — review выполнен по ветке exact head

## Frozen-protocol audit

1. **WO-файл:** `docs/work/WO-NL5-001-C-R1.md` создан ровно один раз — в START-коммите `5b2d440` (2026-09-16 12:15Z, синхронно с event 0001 12:14:43Z, до запуска прогонов 12:45Z); `git log --follow` — единственная версия; SHA-256 содержимого идентичен во всех последующих коммитах ветки (`4e701a08…` на 5b2d440/ab3574b/ebaedcf/b056db2). Изменений протокола после старта **нет**.
2. **Rule/анализ-код:** `scripts/release/reproduction_rule.py`, `docs/release/REPRODUCTION_RULE_V0_1.md`, `scripts/e2/observables.py`, `scripts/hinge_family/oxdna_topology.py`, `scripts/hinge_family/canonical.py` — созданы до кампании (rule: 2026-09-14, WO-NL5-001-B-REPAIR; canonical rounding: 2026-09-11) и **bit-identical** на base и head (git blob SHA совпадает). Threshold tuning в истории ветки отсутствует.
3. **Seeds:** все 12 `input-build.json` в run-каталогах содержат ровно frozen fresh seeds из WO §Scope: 0b [170085,157480,561483], 11b [373439,592596,456410], 32b [399746,801667,659403], 53b [511532,979551,175554]; независимо подтверждено `seed =` в `input.in` каждого прогона; steps согласованы (0b/11b 200000, 32b/53b 150000). **PASS.**

## Independent recomputation

Метод: собственный скрипт reviewer'а (пайплайн окно/гейты/медиана/классификация пере-реализован из текста WO, НЕ скопирован из `tools/analyze_all.py`), использующий только frozen-библиотеки `scripts/e2/observables.py` + `scripts/hinge_family/oxdna_topology.py` на reviewed head; frozen arm manifests из EX-NL3-002-*; окно `t<=150000`; гейты lbf≤0.1078 / pf_v2≥0.50 / disp≤20.0; детектор v2 mutual-nearest + PCA угол [0,180] (erratum R1 §2.5 подтверждён в `docs/research/E2_PROTO_R1.md:15`). Пересчитаны **все 12 реплик** (не только по одной на вариант).

Допуск сравнения: published-отчёты округляются до 9 знаков (`hinge_family.canonical.FLOAT_DIGITS=9`, frozen 2026-09-11), поэтому корректный критерий — |review − published| ≤ 5e-10 (половина шага округления).

| variant | replica | review (полная точность, deg) | published (deg) | Δ |
|---|---|---|---|---|
| 0b | **S001** | **66.15929643740789** | 66.159296437 | 4.08e-10 |
| 0b | S002 | 67.27986351398111 | 67.279863514 | 1.89e-11 |
| 0b | S003 | 65.35040283588306 | 65.350402836 | 1.17e-10 |
| 11b | **S001** | **75.51456235717909** | 75.514562357 | 1.79e-10 |
| 11b | S002 | 72.83429146446069 | 72.834291464 | 4.61e-10 |
| 11b | S003 | 75.63662546299110 | 75.636625463 | 8.90e-12 |
| 32b | **S001** | **78.93983867728963** | 78.939838677 | 2.90e-10 |
| 32b | S002 | 78.09656992889246 | 78.096569929 | 1.08e-10 |
| 32b | S003 | 73.05008535605432 | 73.050085356 | 5.43e-11 |
| 53b | **S001** | **133.10925557404374** | 133.109255574 | 4.37e-11 |
| 53b | S002 | 130.59224750137810 | 130.592247501 | 3.78e-10 |
| 53b | S003 | 132.57559044203413 | 132.575590442 | 3.41e-11 |

- **12/12 медиан**: max Δ = 4.61e-10 ≤ 5e-10 → воспроизведение в пределах frozen round-9 конвенции. **PASS.**
- **Frame-level (углублённо, 2 реплики 0B-S001 и 11B-S001, все 37 in-window кадров каждая):** angle_deg, pairs_fraction_v2, long_bond_fraction, displacement_max, valid-флаг — `round(mine,9) == published` во **всех 74 кадрах, 0 mismatches**.
- Счётчики кадров: frames_total 50 (0b/11b, шаги 4000..200000) / 37 (32b/53b, 4000..148000), in-window 37/37, valid 37/37 — воспроизведено у всех 12.
- Campaign statistics (median трёх медиан): 0b 66.15929643740789, 11b 75.51456235717909, 32b 78.09656992889246, 53b 132.57559044203413 — совпадают с published (66.159296437 / 75.514562357 / 78.096569929 / 132.575590442) в пределах round-9.
- Технические исходы: `exit_code.txt` EXIT:0 у 12/12; run-reports (live run dir) == published copy; wall-clock 35.8–50.7 ks (< 20h kill); energy-файлы завершены (последняя строка time 1000.0 = 200k шагов / 750.0 = 150k шагов); engine_stderr пуст.

## Classification check (4/4)

Классификация воспроизведена тремя независимыми путями: (а) моя собственная реализация правила из текста REPRODUCTION_RULE_V0_1.md, (б) вызов frozen `scripts/release/reproduction_rule.py::classify()`, (в) published classification-*.json — исходы совпадают во всех трёх для всех вариантов:

| variant | fresh medians (deg) | campaign stat (deg) | envelope (deg) | review outcome | frozen script | published |
|---|---|---|---|---|---|---|
| 0b | 66.159296437, 67.279863514, 65.350402836 | 66.159296437 | [65.095434789, 67.236579608] | MATCH | MATCH | MATCH |
| 11b | 75.514562357, 72.834291464, 75.636625463 | 75.514562357 | [72.165683993, 74.533109426] | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| 32b | 78.939838677, 78.096569929, 73.050085356 | 78.096569929 | [77.4927314, 79.877463339] | MATCH | MATCH | MATCH |
| 53b | 133.109255574, 130.592247501, 132.575590442 | 132.575590442 | [131.049227687, 135.285186059] | MATCH | MATCH | MATCH |

- Envelope-арифметика: published envelope == [min,max] карточных reference medians — 4/4; `card_reference` в classification-*.json deep-equals `reproduction.expected` карточек — 4/4; `reference_campaign_statistic_deg` == median(ref medians) — 4/4.
- **11b INCONCLUSIVE — корректный промежуточный исход:** stat 75.514562357 > ref_max 74.533109426 (вне envelope), НО S002 = 72.834291464 < ref_max → нет полной directional separation; S001/S003 > ref_min 72.165683993 → нет separation вниз. По frozen правилу — ровно INCONCLUSIVE: не подтянут к MATCH (stat вне envelope) и не объявлен MISMATCH (нет полного разделения). **Корректно.**
- 32b MATCH при одной реплике ниже envelope (73.05) — корректен по правилу: правило классифицирует по campaign statistic, S003-выброс не скрывался (опубликован во всех records).
- Bootstrap (10000/seed 424242) нигде не использован как tolerance (verify: `classification.*.card_reference.bootstrap_ci_role=DESCRIPTIVE_ONLY_NOT_A_REPRODUCTION_TOLERANCE`).

## Honesty check (INCONCLUSIVE preserved)

- 11b INCONCLUSIVE сохранён во всех durable-записях: classification-11b.json (outcome + reason), campaign-summary.json, event 0005, summary.md, event 0006 («открытый пункт для review, не PASS и не скрывается»). Нигде не интерпретирован как PASS и не заменён scientific interpretation'ом: события явно разделяют technical outcome (COMPLETED) и scientific interpretation (отложен к review/verifier/human gate).
- Ни один run не исключён (12/12 присутствуют во всех evidence, включая 32b S003 = 73.05 ниже envelope и оба «плохих» 11b-положения).
- Threshold tuning: отсутствует (см. Frozen-protocol audit; правило заморожено 2026-09-14 — до любых NL5-001-C данных, создано в B-REPAIR после Fresh Reviewer FIX_REQUIRED).
- Запуск дополнительных реплик для «дожима» 11b не предпринимался — ровно 12 заявленных прогонов (manifest + run dir).

## Invariants

- **74b не тронут:** card `74b.card.json` = NOT_MEASURED / KNOWN_GAP на head; `git diff base..head -- releases/ project/ docs/ROADMAP.md docs/research/ scripts/` — пуст. Никаких значений для 74b не создано (в manifest 112 файлов только 0b/11b/32b/53b).
- **Reference seeds не использованы:** 12 seeds input-build.json ∩ {201004, 202008, 203012} = ∅; в input.in тоже.
- **Canonical state не менялся:** `git diff --name-only 6577f8b..b056db2` не содержит project/state.json, project/plan.json, docs/ROADMAP.md, checkpoint catalog; branch history не переписывалась (remote == local head, обычные commits).
- **Allowed paths паспорта:** `allowed_paths = [docs/work/WO-NL5-001-C-R1.md, docs/work/executions/EX-NL5-001-C-R1/**]`; все 34 изменённых файла base..head — только добавления (8327 insertions, 0 deletions) ровно в этих двух путях. **PASS.**
- Events immutability: каждый event introduсирован одним коммитом и не редактировался; исправление факта — новым event 0003 (корректная процедура superseding).

## Infrastructure check

- **Event 0002 (инцидент пересборки движка):** зафиксирован ДО использования данных — первичный запуск остановлен после замера скорости, clean rebuild (Release), бинарь байт-идентичен (sha256 45da6a50…), частичные траектории не использовались; финальный запуск 12 прогонов 12:45Z после пересборки. Проверено по фактам: `~/nl5-001-c-env/BUILD_PROVENANCE.md` существует (pinned commit 00dc7fb9, CPU/DOUBLE=ON/CUDA=OFF, gcc 11.4.0); текущий `oxdna-src/build/bin/oxDNA` sha256 = `45da6a5088b9b0b28636dbad11d1b87a478043641dc5610d7d85c0e4517a3e48` — совпадает с заявленным в event 0002.
- **Inputs:** download-on-run по pinned commit 23fd1ff7, size+blob_sha1 гейты против frozen пинов пакета — 12/12 PASS (`input-download-verification.json`; sha256 CONTENT_VERIFIED для пинов); `durable_cache=false`; в run dir нет кэша вне disposable директории.
- **input.in vs авторский pro_CPU.in:** diff ровно по frozen deviation list (seed, steps, имена выходных файлов, print_conf_interval 4e3→4000, print_energy_every 4e3→100, subject files); авторский файл в run dir байт-идентичен скачанному.
- **Artifact manifest:** все **112/112** записей (не выборочно) проверены sha256+size против живых raw-файлов — 0 mismatch, 0 missing.

## Independence caveat

Reviewer — fresh-сессия без доступа к чату implementation, реализовал пайплайн анализа самостоятельно. Ограничения независимости: (1) по условию frozen convention наблюдаемые считались через те же frozen-библиотеки `scripts/e2/observables.py` / `oxdna_topology.py` — их корректность принята как замороженная конвенция (hash-верифицирована base==head, создана до данных); (2) arm manifests взяты из опубликованных frozen evidence EX-NL3-002-*; (3) то, что raw-траектории действительно порождены pinned engine из записанных inputs, подтверждается только цепочкой записей (exit codes, digest gates, manifest sha256, energy-профили) — полная re-run репликация 12×(150–200k шагов) вне scope/budget review.

## Remaining risks

1. **Интерпретация 11b INCONCLUSIVE** остаётся открытой: stat вне envelope без directional separation при 3 reference репликах. Любые дополнительные реплики/изменения дизайна — только через новую protocol revision (post-hoc tuning запрещён).
2. **Байт-идентичность пересборки движка** (event 0002) подтверждена текущим sha256 бинаря и записью события; исходный (до-rebuild) бинарь не архивировался — полная независимая верификация невозможна post-hoc (accept: событие записано до использования данных).
3. **Raw-артефакты disposable** (вне Git): при удалении run dir останется только manifest; перепроверка станет невозможной. Митигировано digest-записями, но для будущих кампаний рассмотреть durable-хранение хотя бы agg-артефактов.
4. **Мелкие наблюдения (не влияют на классификацию, исправлять по усмотрению owner):**
   - `releases/.../cards/0b.card.json` в `reproduction.steps[4]` указывает окно «t <= 200000», тогда как WO §5 и остальные карточки — common window `t <= 150000` (E2_PROTO_R1 addendum: 0b confirmatory 200k, кросс-вариантное сравнение 150k). Текст карточки унаследован с base, веткой не менялся; кампания следовала frozen WO. Рекомендуется унификация формулировки в будущей ревизии пакета.
   - `passport.json.status = "RUNNING"` на финальном head при завершённой кампании (completion зафиксирован events/summary) — stale metadata.
   - Event 0001 `evidence_refs` ссылается на `docs/evidence/NL5-001-B/...`, отсутствующие в дереве этой ветки (записи живут на своих review-ветках) — ссылки не резолвятся в данном дереве.

## Verdict rationale

Заявленное = воспроизведённому: 12/12 пер-репличных медиан и 4/4 классификации независимо пересчитаны из raw-траекторий с максимальным расхождением 4.61e-10 deg (ровно frozen round-9 конвенция отчётов), frame-level сверка 74/74 кадров — 0 расхождений. Протокол заморожен до данных и не менялся; классификационное правило применено без tuning; промежуточный исход 11b сохранён как INCONCLUSIVE без подтягивания; инварианты (74b, seeds, canonical, allowed paths) соблюдены; манифест 112/112. Все findings — minor observations, не требующие блокировки. Fresh Verifier и Human Gate (merge) — следующие обязательные шаги по протоколу.

## REVIEW_VERDICT

**PASS**
