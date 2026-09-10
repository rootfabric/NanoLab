# NL2-002 — VERIFIER VERDICT (независимая свежая верификация)

**Вердикт: PASS**

- Роль: VERIFIER (fresh-сессия, независимо от IMPLEMENTER и REVIEWER; review PASS `9e26748` принимается только как контекст маршрута, не как основание настоящего вердикта).
- Subject: `work/nl2-002-validate-e1-r1` @ `6cc7fdef24d9d3275b5a5a8efab4dc806e7cf893`; base `0176098ed052ec29503ac5c353463be0cc8ea167` (ancestor подтверждён).
- Метод: воспроизведение исполнением — git-факты, собственная пересборка pinned oxDNA, собственный T2-прогон, Decimal-пересчёт статистики, digest-vs-blob через `git cat-file`, jsonschema + harness CLI. Сырые выводы: [VERIFIER_VERIFICATION_LOG.md](VERIFIER_VERIFICATION_LOG.md).

## 1. Scope/subject — OK

- Все 48 изменённых файлов в allowed_paths WO-NL2-002; вне scope — 0. `SESSION_LOG.md` — строго append (0 удалённых, 10 добавленных строк).
- Forbidden-поверхности blob-идентичны base (tree/blob SHA): state.json, plan.json, config/**, scripts/harness/**, протоколы E1-R1/R2, ENGINE_ENVIRONMENT_R1, E0-протокол, E1-R1/**, docs/evidence/NL1-002/**, NL2-001/**, docs/experiments/**, E0/** — 13/13 IDENTICAL.
- Freeze-коммит кампании `f34e62ca67f12f0cffbd1823d584afc09900db6a` = ровно campaign.md + protocol.json + analyze_energy.sh; commit-time freeze (21:21:21+10) < campaign-start `42cb851` (21:23:45+10); subject_sha всех run-поверхностей = freeze-коммит.

## 2. Независимый T2-прогон (C-VERIFY) — IN_BAND

Пересборка по ENGINE_ENVIRONMENT_R1 §3 на той же машине: свежий `git fetch` exact `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` (rev-parse HEAD совпал), cmake 3.31.6 (tarball SHA-256 = пин §2), `Release/CUDA=OFF/MPI=OFF`, make exit 0. **Критерий размеров §4: 3/3 байт-в-байт** (oxDNA 3375976 B, DNAnalysis 2957400 B, confGenerator 2201664 B); флаги CMakeCache MATCH (DOUBLE=ON, NATIVE=ON, JSON=ON, CMAKE_CXX_FLAGS пуст); SHA-256 бинаря свежей сборки `c8fc06b6…` ≠ implementer-ский `ffc80b1a…` — ожидаемо (COMPILED ON) и подтверждает независимость сборки.

Собственная confirmatory-реплика: verbatim quick_input (blob 8935c4bc…, 533 B, SHA on-place 4/4 перед прогоном), `/usr/bin/time -v`, **новый seed 319832093** (не входит в опубликованные 7: S001/P001–P003/C001–C003):

| Факт | Значение |
|---|---|
| Exit code | 0 («END OF THE SIMULATION, everything went OK!»), wall 11.11 s, RSS 6332 KB |
| Целостность §5.2 | 1001 строка, 10 конфигураций, NaN/Inf = 0, N=16/molecules=2, v3.7, GIT COMMIT 00dc7fb |
| avg col2 (analyze_energy.sh, байт-в-бит blob 77cfcc63) | **−1.39396936364** |
| Δ от оракула −1.37970256144 | −0.01426680220 → **IN_BAND** (|Δ| ≤ 0.15) |
| Независимый Decimal-пересчёт | mean −1.369…= −1.3939693636363… → IN_BAND (совпадает) |

Это **дополнительная 4-я T2-точка данных** (5-я с учётом S001), полученная полностью независимо: другой бинарь (свежая пересборка), другой seed, другой процесс. Результат консистентен с опубликованными 3/3 IN_BAND и не заменяет их. Отдельная точка не меняет механику §9 (критерий определён на frozen set S001+C001–C003) — она подтверждает воспроизводимость за пределами исходной выборки.

Техническая заметка: первая попытка C-VERIFY классифицирована FAILED_TECHNICAL по ошибке верификатора (layout: отсутствовал родительский `../init.dat`; engine завершился fail-closed с явной ошибкой, exit 1, данных нет, значение не использовалось). Повтор — новым запуском в новом каталоге; технический исход и научный вывод разделены, негатив сохранён в логе.

## 3. Статистика — MATCH

Decimal-пересчёт (prec 60, quantize 1e−11) по 4 published-точкам (S001+C001–C003): mean −1.36896744830, SD(n−1) 0.01729656703, размах 0.03740553047 — **3/3 MATCH** statistics.md/evidence-map.json. Per-replica значения воспроизведены из published blob'ов байт-в-бит инструментом: 4/4 дословно, 4/4 IN_BAND. Критерий §9 (T1 PASS И все T2 IN_BAND) — подтверждён механически на published-данных.

## 4. Дайджесты и seed — OK

- Digest-vs-blob: **15/15 MATCH** (5 артефактов × C001–C003, `git cat-file`, не working copy; SHA-256+size+producer_run_id+subject_sha). Порог ≥12 выполнен.
- analyze_energy.sh: blob E1-R2 == blob E1-R1 == `77cfcc63…` (SHA-256 747c5216… — пин); fixture-блобы pinned tree — 4/4 MATCH из свежего fetch.
- Seeds из log.dat blob'ов: C001/C002/C003 попарно различны (3/3) и отличны от S001/P001–P003 (пересечений нет).

## 5. Схемы и CLI — OK (с observation F-1)

- `experiment_cli validate`: 3/3 ok=true, 0 errors, 0 warnings; terminal execution + analysis присутствуют; порядок событий 0001 RUN_STARTED → 0002 RUN_COMPLETED (терминальный) → 0003 ANALYSIS_COMPLETED — terminal-last OK.
- `work_cli validate` EX-NL2-002-R1: ok=true, HANDOFF_COMPLETED терминальный, post-terminal corrections отсутствуют; `check-consistency` ok=true.
- jsonschema Draft 2020-12 + FormatChecker: 20/21 поверхностей OK (все run-манифесты, 9 run-событий, 3 artifacts.manifest, паспорт + 4 work-события).
- **F-1 (MINOR, вне WO, не блокирует):** campaign-level `evidence-map.json` не валиден против `config/control/harness/evidence-map.schema.v1.json` (11 ошибок). Классификация: campaign-maps принятых предшественников E1-R1 (NL1-002) и E0-R4 (NL2-001) дают идентичные ошибки — v1-схема описывает checkpoint-вид evidence map, а campaign-документы следуют устоявшейся конвенции. Расхождение схемы и конвенции стоит закрыть отдельной гигиенической задачей (не в этом WO).

## 6. Гигиена полномочий — OK

- Self-acceptance отсутствует: ни один документ ветки не выставляет ACCEPTED/статус E1; паспорт HANDOFF_READY; «ACCEPTED не выставляется» — явно.
- Campaign-level scientific_outcome = **NOT_EVALUATED** сохранён во всех публикациях (события, statistics.md, evidence-map, IMPLEMENTER_EVIDENCE).
- `SUPPORTED` присутствует только как recommendation_for_director; фактами публикуются исключительно execution facts (COMPLETED, wall/RSS, seeds) и preregistered band-facts (IN_BAND/OUT, механический MET по §9). Claim ceiling `C1_COMPUTATIONAL_REPRODUCTION` не превышен.
- Бюджет: 3 прогона × ~11 s ≈ 0.009 core-hour ≪ cap 1 core-hour; мой C-VERIFY добавил ~11 s (вне кампании, scratch).

## Ограничения верификации

- C-VERIFY выполнен на той же машине/архитектуре (NATIVE_COMPILATION) — независимость повторов в кампании обеспечивается distinct seed, не машинами; настоящий вердикт это ограничение не устраняет, но подтверждает устойчивость результата к пересборке и смене seed.
- C-VERIFY — одна точка; статистические выводы остаются на frozen set n=4.
- Scratch-артефакты C-VERIFY в Git не публикуются (правило disposable); их SHA-256/размеры зафиксированы в VERIFICATION_LOG для provenance.

## Итог

Evidence-пакет NL2-002 воспроизводится исполнением: scope чист, статистика сходится до последнего знака, дайджесты и seed-факты подтверждаются на уровне blob'ов, контрактные поверхности валидны, собственный независимый прогон верификатора IN_BAND. Опубликованные факты поддерживаются; вопрос приёмки E1 остаётся за Director (рекомендация SUPPORTED не превращена в факт — корректно).

**VERDICT: PASS** (0 FIX_REQUIRED; 1 observation F-1 MINOR — вне scope NL2-002).

Next action: Director checkpoint NL2-002 (объявление статуса E1 по evidence-пакету); merge — Human Gate.
