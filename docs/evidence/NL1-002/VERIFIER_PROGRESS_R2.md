# NL1-002 — Verifier Progress Log R2 (независимая верификация исполнением)

Verifier: fresh session R2. Branch: `verify/nl1-002-reference-run-r2` @ `ec7e3edc83a3434d96222a0a8a94b03f7fa10e23`.
Preambula: предыдущий verifier-вердикт R1 (`b405a7e`) аннулирован (role-mixing: написан той же сессией, что и reviewer-вердикт). Настоящая верификация не опирается на R1-вердикты.
Status log — дополняется коммитами по мере завершения проверок. Финальный вердикт: `VERIFIER_VERDICT_R2.md` (последним коммитом).

## Выполнено к этому коммиту

### 1. Exact subject — OK
- `ec7e3edc83a3434d96222a0a8a94b03f7fa10e23` резолвится в bare repo `C:\NanoLab\.git-store\repo.git` — OK.
- Base `71535d00a2e729349eea2337217a2c591ed9317d` резолвится; `merge-base --is-ancestor 71535d0 ec7e3ed` → exit 0 (subject строго потомок base) — OK.
- `ls-remote origin refs/heads/main` = `71535d00a2e729349eea2337217a2c591ed9317d` — base совпадает с remote main — OK.
- `ls-remote origin refs/heads/work/nl1-002-reference-run-r1` = `c44b2091d183be55e8accd47e845c0511c041083` — remote work-ветка УШЛА ВПЕРЁД subject: `ec7e3ed..c44b209` содержит только 4 вердикт-коммита R1 (`7b12012` reviewer, `b405a7e` аннулированный verifier, `d1da6b8`, `c44b209` merge). `git diff --stat ec7e3ed c44b209` = только `docs/evidence/NL1-002/REVIEWER_VERDICT.md` (+97) и `VERIFIER_VERDICT.md` (+66, аннулированный); work-content (experiments/, docs/ и пр.) между subject и remote tip — 0 изменений. `merge-base --is-ancestor ec7e3ed c44b209` → exit 0. Проверяемый subject содержится в remote-ветке бит-в-бит — OK.
- Worktree создан от exact `ec7e3ed`, чистый (`status` пуст).

### 2. Engine acquisition (pinned oxDNA) — OK
- Windows-сторона, scratch `C:\NanoLab\scratch\nl1-002-verify-r2\oxDNA` (свежий probe-repo, не переиспользован): `git init` + `remote add origin https://github.com/lorenzo-rovigatti/oxDNA` + `fetch --depth 1 origin 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` + `checkout --detach FETCH_HEAD` — OK.
- `git rev-parse HEAD` в probe-repo = `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` — точное совпадение с пином — OK.

### 3. Среда WSL — зафиксировано
- `Ubuntu 24.04.2 LTS` (WSL2), gcc 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1), 20 логических ядер — совпадает с `ENGINE_ENVIRONMENT_R1` §2 — OK.
- user-local cmake 3.31.6 в WSL ОТСУТСТВУЕТ (disposable scratch от NL1-001 вычищен) → повторное приобретение: `cmake-3.31.6-linux-x86_64.tar.gz`, пин SHA-256 `5a1133ff103c71eb5120e2cc3de922733e7d8a26a98ae716397e8676adb367bf`.
- **Сетевой инцидент №1:** первая загрузка tarball оборвалась (прокси, «response ended prematurely»): частичный файл 43 891 824 B, SHA-256 `fd7097a7ea7e33658830005405ea848e535c03d216f7f0e532097cdf9666dc22` ≠ пин — файл ЗАБРАКОВАН. Повтор через `curl.exe --retry 5`. Если повторный сбой — пересборка помечается BLOCKED по сети, верификация продолжается по независимым от сети проверкам.

### 4. Схема-валидация (машинный контракт) — ПЕРВИЧНАЯ НАХОДКА
- Штатный валидатор репозитория `CONTROL_EXPERIMENT(.sh/.ps1) validate` → `scripts/harness/experiment_cli.py` на всех 4 run-каталогах (`E1-R1-S001/P001/P002/P003`) НЕ ПРОХОДИТ: `AttributeError: 'str' object has no attribute 'get'` (exit 1, traceback) — `artifacts.manifest.json` в пакете использует форму `{"artifacts": {имя: {...}}}` (объект), тогда как контракт CLI требует `{"artifacts": [ {sha256, size_bytes, producer_run_id, subject_sha, storage_location}, ...]}` (массив).
- Дополнительно по контракту `experiment_cli.py`: в `manifest.json` отсутствуют `subject_sha`, `claim_ceiling`, `model`, `observables`, `stop_conditions`; в каждом event отсутствуют `experiment_id`, `subject_sha`. Содержательно provenance-поля в пакете присутствуют (sha256/size/producer_run/producer_tool/storage), а frozen subject зафиксирован git-коммитами (`5c8774f`, `9cc83e8`) — расхождение формальное, но машинный контракт контроля ломается. Классификация — в финальном вердикте.

### 5. Документы пакета — прочитаны (основа для проверок)
- `IMPLEMENTER_EVIDENCE.md`, `campaign.md`, `protocol.json`, `evidence-map.json`, `analyze_energy.sh`, `PREREGISTRATION_E1_R1.md` (§2.2 пины, §5.1 критерий, §5.2 целостность, §6.4 пилот, §9 исходы), `PREREGISTRATION_E1_R2.md` (freeze R_confirm=3), `ENGINE_ENVIRONMENT_R1.md` (§2/§3/§5), `WO-NL1-002.md`, контрольные документы (`PROJECT_CONTROL.md`, `HARNESS_CONTROL.md`, `EXPERIMENT_HARNESS_RU.md`, `HARNESS_REVIEW_AND_EVIDENCE_RU.md`, `HARNESS_AUTONOMOUS_EXECUTION_RU.md`), `project/state.json`.

### 6. Дайджесты всех файлов деревьев evidence — OK (проверка D1)
- Метод: `git cat-file blob` (байты коммитов, byte-exact) → sha256sum в WSL; скрипт верификатора в disposable scratch (вне Git), ветка-ref `verify/nl1-002-reference-run-r2`.
- Деревья: `experiments/evidence/E1/E1-R1/**` = 44 файла, `docs/evidence/NL1-002/**` = 10 файлов — все SHA-256 посчитаны из сырых blob-байтов.
- Артефакты vs `artifacts.manifest.json` (по всем 4 прогонам): 16/16 sha256 MATCH, 16/16 size MATCH (log/energy/trajectory/last_conf × S001/P001–P003).
- Кросс-проверка: `events/0002-run-completed.json.artifacts_sha256` = `artifacts.manifest.json` sha256 по всем 16 позициям — MATCH; engine binary pin `ffc80b1a…` во всех manifest.json — MATCH.
- Манифест-дайджесты (пины): energy.dat S001 `ff26bad5…`, log.dat S001 `2c493f65…`, trajectory S001 `e51bc59d…`, last_conf S001 `f9af73bc…` — воспроизведены; полный список в scratch-отчёте верификатора.

### 7. Воспроизведение анализа (проверка D2) — OK до последнего знака
- Опубликованный `analyze_energy.sh` извлечён из blob (`747c5216589ab9270830a21eaf7f15d1aea742681360ac048f4392c2edfabd4d`) и исполнен в WSL на опубликованных `energy.dat` каждого прогона (байты из blob):
  - E1-R1-S001: rows=1001, avg_col2=**-1.39393635864**, delta=**-0.01423379720**, IN_BAND — совпало с зафиксированным 11/11 знаков;
  - E1-R1-P001: rows=1001, avg_col2=**-1.37730121179**, delta=**+0.00240134965**, IN_BAND — 11/11;
  - E1-R1-P002: rows=1001, avg_col2=**-1.39389370430**, delta=**-0.01419114286**, IN_BAND — 11/11;
  - E1-R1-P003: rows=1001, avg_col2=**-1.38687945155**, delta=**-0.00717689011**, IN_BAND — 11/11.
- Целостность §5.2 на опубликованных файлах: 1001 строка energy.dat (4/4), 10 конфигураций trajectory (4/4), NaN/Inf = 0 (4/4), `END OF THE SIMULATION, everything went OK!` (4/4).
- Лог-факты каждого прогона: `RELEASE: v3.7`, `GIT COMMIT: 00dc7fb`, seed из лога = опубликованному (S001 −200619630; P001 −473348953; P002 −547126645; P003 −1610133928), `T … (0.097717)`, `N: 16, N molecules: 2` — все совпали.

### 8. Пересчёт статистики повторов (проверка D3) — OK бит-в-бит
- Независимый пересчёт (python3 statistics.stdev, не awk) по pilot_values из evidence-map: mean **-1.38602478921**, выборочное SD **0.00832919790**, размах **0.01659249251**, SD/полоса **0.0555** — все 4 значения совпали с `pilot_statistics` evidence-map и с `PREREGISTRATION_E1_R2` §1.
- Пересчёт delta_from_oracle для всех 4 прогонов (avg − (−1.37970256144)) — 4/4 до 11 знаков; band-классификация 4/4 IN_BAND при полосе ±0.15.
- Оракул верифицирован verbatim из upstream pinned tree: `git cat-file blob 00dc7fb9…:test/DNA/DSDNA8/MD/quick_compare` = `ColumnAverage::energy.dat::2::-1.37970256144::0.15`, SHA-256 `86a8b6ac50f382ba25e5aacbbef629cc5a1788f44e6c28d113509c8448e3ce27` = пин protocol.json — полоса/значение не подбирались NanoLab.

### 9. Схема-валидация и паспорт (проверка D4) — ОТКЛОНЕНИЯ ОТ МАШИННЫХ КОНТРАКТОВ
Валидаторы (`scripts/harness/*_cli.py`) бит-в-бит идентичны base `71535d0` (subject их не менял) — контракт действовал в этой форме во время исполнения.
- `CONTROL_WORK validate docs/work/executions/EX-NL1-002-R1` → **ok=false, exit 3**, 5 ошибок:
  1. `invalid subject_sha` в событиях `0002-campaign-runs-completed`, `0003-validation-recorded`, `0004-handoff-completed`, `0005-resource-evidence-committed` — указано `"9cc83e8"` (7 знаков), контракт требует 40 lowercase hex;
  2. `terminal/handoff event must be last` — после `0004-handoff-completed` (терминальный) опубликован `0005-resource-evidence-committed` (CONTINUATION_CHECKPOINT, post-handoff resource evidence, коммит `ec7e3ed`).
- `CONTROL_EXPERIMENT validate` на всех 4 run-каталогах — **падение (AttributeError, exit 1)**: `artifacts.manifest.json` использует объект `{"artifacts": {имя: …}}` вместо контрактного массива `[ {sha256, size_bytes, producer_run_id, subject_sha, storage_location} ]`; кроме того по контракту отсутствуют поля: в `manifest.json` — `subject_sha`, `claim_ceiling`, `model`, `observables`, `stop_conditions`; в каждом event — `experiment_id`, `subject_sha`.
- Прозаический контракт `EXPERIMENT_HARNESS_RU` (структура каталогов, типы событий, терминальные исходы, разделение technical/scientific) — СОБЛЮДЁН; содержательный provenance в пакете присутствует (см. §6: 16/16 артефактов с sha256/size/producer/storage). Отклонения — формально-контрактные, научную суть не затрагивают; классификация — в вердикте.
- Прочие структурные проверки: filenames = event_id (все), событие `RUN_STARTED` первое и единственное (4/4 прогонов), ровно один терминальный execution-event и `ANALYSIS_COMPLETED` после него (4/4), `scientific_outcome = NOT_EVALUATED` ∈ допустимых значений, лексический порядок event_id (4/4) — OK.

### 10. Отсутствие ACCEPTED/self-acceptance (проверка D5) — OK
- `git diff 71535d0..ec7e3ed -- project/state.json project/plan.json config/ docs/control/ scripts/` — ПУСТО (state/plan/policies/контроль не тронуты веткой; `NL1-002` в state.json остаётся `READY`).
- `docs/evidence/NL1-002/` на subject: только `IMPLEMENTER_EVIDENCE.md` + `run-resources/**` — вердикт-файлов REVIEWER/VERIFIER/DIRECTOR и acceptance-record НЕТ.
- Паспорт `EX-NL1-002-R1/passport.json`: `status: IN_PROGRESS`, accept-статусов нет; события handoff маршрутизируют REVIEWER → VERIFIER → Director, merge = Human Gate.
- Паспорт `E1_REFERENCE_REPRODUCTION.md`: статус `RUN`, campaign scientific_outcome `NOT_EVALUATED`; слово ACCEPTED в пакете встречается только как ссылка на внешний уже принятый main-факт NL1-001 (environment state) — само-acceptance NL1-002 отсутствует.
- IMPLEMENTER самопроверка явно помечена «самопроверка implementer'а, не acceptance» — допустимо.

### 11. Пересборка engine §3 (проверка D6) — OK (BUILD_EXIT=0, размеры/флаги 1:1)
- См. `verify-r2/ENGINE_REBUILD_AND_SMOKE_R2.md`: fetch exact `00dc7fb9` (rev-parse HEAD совпал), cmake 3.31.6 re-acquired SHA MATCH пину, CMAKE_EXIT=0, BUILD_EXIT=0; размеры бинарей 3375976/2957400/2201664 B — 1:1 с §4 и campaign-пином; флаги Release/-O3/-DNDEBUG/DOUBLE=ON/CUDA=OFF/MPI=OFF/NATIVE=ON/JSON=ON/`-D_FORCE_INLINES`, `GIT_COMMIT="00dc7fb"` — 1:1. SHA бинаря `a4810960…` ≠ campaign `ffc80b1a…` — ожидаемо (встроенный BUILD_TIME), критерий protocol.json соблюдён.

### 12. Независимый smoke-прогон (проверка D7) — OK, полоса совместима
- Run ID `EX-VERIFY-NL1-002-R2-SMOKE-001` (новый, не переиспользован): на собственной пересборке, вход = raw blobs (fixture 2/2 SHA MATCH пинам + опубликованный `quick_input_smoke` 414 B, steps=1e4/print_conf_interval=1e4 подтверждены).
- RUN_EXIT=0; wall 0.14 s; RSS 6620 KB; «END OF THE SIMULATION, everything went OK!»; 11 строк energy.dat; NaN/Inf=0; 1 конфигурация; RELEASE v3.7; GIT COMMIT 00dc7fb; N=16/molecules=2; seed −588845438.
- avg_col2 (тот же `analyze_energy.sh`) = **−1.36689954545** → IN_BAND; NL1-001 опубликованный smoke = **−1.36018000000** → IN_BAND; расхождение 0.0067 ≪ полоса 0.15 — energy-полоса СОВМЕСТИМА (compatibility-факт, не scientific claim).
- Артефакты verify-прогона опубликованы в `verify-r2/smoke-run/EX-VERIFY-NL1-002-R2-SMOKE-001/`.

### 13. Ресурсы прогонов (проверка D8) — OK
- Опубликованные `docs/evidence/NL1-002/run-resources/<run>/time.log` сверены с заявленным: S001 13.13 s/6304 KB, P001 11.08/6328, P002 11.74/6700, P003 12.56/6520 — все значения = IMPLEMENTER_EVIDENCE/evidence-map. Бюджет ~48.5 c ≪ 1 core-hour.

## Итог проверок

Все запланированные проверки выполнены (D1–D8, §1–§13). Исполнительная/научная суть пакета воспроизведена полностью; зафиксированы формальные отклонения от машинных контрактов (§4, §9). Итоговый вердикт — `VERIFIER_VERDICT_R2.md` (следующий коммит).

