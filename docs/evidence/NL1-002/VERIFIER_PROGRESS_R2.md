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

## Ещё НЕ выполнено (план)

- [ ] Пересборка oxDNA CPU по §3 в WSL (после восстановления cmake; критерий: BUILD_EXIT=0 + размеры/флаги).
- [ ] Собственный verify-smoke-прогон (НОВЫЙ run ID, 1e4 steps) + сравнение energy-полосы с NL1-001 smoke.
- [ ] SHA-256 всех файлов `experiments/evidence/E1/E1-R1/**` и `docs/evidence/NL1-002/**` по git-blob байтам vs манифесты.
- [ ] Воспроизведение `analyze_energy.sh` на опубликованных energy.dat S001/P001–P003 — до последнего знака.
- [ ] Пересчёт статистики повторов (SD 0.00832919790 и др.) своими командами.
- [ ] Проверка отсутствия ACCEPTED/self-acceptance в пакете (state.json/plan.json нетронуты vs base).
- [ ] `VERIFIER_VERDICT_R2.md` + push.
