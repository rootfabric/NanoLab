# NL2-001 — Независимый Reviewer Verdict (E0, contracts)

**Вердикт: `FIX_REQUIRED`** (научное/контрольное содержание подтверждено и независимо воспроизведено; пакет evidence требует erratum/исправлений до VERIFIER и Director — см. Findings).
**Review-unit:** `experiments/evidence/E0/E0-R4/**` + `docs/evidence/NL2-001/IMPLEMENTER_EVIDENCE.md` (линия попыток E0-R1..R4).
**Subject под review:** ветка `work/nl2-001-contracts-e0-r1`, exact HEAD `2cee872179bbcccff93c1b9458c6b25ea491a999`; base `15a2c9b1b5c095e24e2e1c24afd77feef5361102`.
**Роль:** независимый REVIEWER (fresh-сессия; контекст имплементёра не использовался — только Git-факты и собственные прогоны). Reviewer-ветка: `review/nl2-001-contracts-e0-r1`.
**Claim ceiling:** подтверждается `C0_SOFTWARE_ONLY`; campaign-level scientific_outcome E0 = `NOT_EVALUATED` (этот вердикт не является accept'ом E0 и не повышает claim).

## 1. Scope и метод проверки

Проверки исполнены независимо на собственном worktree `C:\NanoLab\review-nl2-001` (checkout `2cee872`). Инструментальная среда: Python 3.11.8, jsonschema 4.22.0, git 2.53.0.windows.1 — совпадает с environment_binding протокола.

1. `git diff 15a2c9b..2cee872`: 735 файлов, только поверхности `docs/evidence/NL2-001/**`, `docs/experiments/E0_PIPELINE_VALIDATION.md` (строка статуса), `docs/research/PREREGISTRATION_E0_R1..R4.md`, `docs/work/**`, `experiments/evidence/E0/**`. `project/*`, `config/**`, `scripts/**`, `experiments/evidence/E1|E2/**`, `PREREGISTRATION_E1_*` — 0 изменений (E1-прогоны не выполнялись).
2. Инструмент бит-в-бит: все 19 файлов `config/control/harness/*` + `scripts/harness/*` — git blob SHA идентичны base→HEAD (0 mismatch). Инструментальная заморозка подтверждена.
3. Хронология по коммитам: START `609d4a3` → freeze R1 `5a151f7` (23:25+10) → start R1 `e3c940c` → … → prereg R4 `f2e17bc` (13:52:47Z) → digests `ce477aa` → start R4 `1688e71` (13:52:57Z) → results `24352f9` (14:00:21Z). Машинные `finished_at_utc` в `case_record.json` R4: 13:53:01–13:59:59Z — между start- и results-коммитами. Пререгистрация предшествует прогонам.
4. Сверка ожиданий R1→R4: нормализованные JSON `cases` (замена `E0-R\d→E0-RX`, без `frozen_at_utc`) сравнены канонической сериализацией — **различий нет** (18/18 кейсов идентичны во всех четырёх протоколах; superseding-цепочка R2→R1, R3→R2, R4→R3 затрагивает только идентичность кампаний и ремонт runner'а, что подтверждено текстами `PREREGISTRATION_E0_R2/R3/R4.md` и полем `supersedes`).
5. Дайджесты: `input_digests.json` всех четырёх кампаний сверены с **сырыми git-блобами** `digest_rev` — 54/54 (R1), 57/57 (R2, R3, R4), 0 расхождений; drift после freeze — только документированный ремонт `e0_runner.py`/`e0_freeze.py` между попытками (для канонической R4: 0 drift digest_rev→HEAD; фикстуры E0-R1→HEAD байт-идентичны).
6. Артефакты ран-каталогов: sha256/size всех `stdout.txt`/`stderr.txt`/`validate_outputs.txt`/`pinned_source_excerpt.txt` сверены с блобами HEAD — совпадают; по `case_record.json` — систематическое расхождение, см. Finding F1.
7. Структурные контракты (мой машинный обход 73 run-каталогов R1–R4): `manifest.json`/события/`artifacts.manifest.json` валидны по v1-схемам (Draft 2020-12 + FormatChecker); `subject_sha` — 40-hex и равен subject кампании в манифесте, событиях и артефактах; `event_id` = имени файла; `experiment_id` присутствует; последнее событие — `ANALYSIS_COMPLETED`; `claim_ceiling=C0_SOFTWARE_ONLY` всюду; манифесты — контрактная форма `schema_version`+`artifacts[]` с обязательными полями. Нарушений нет.
8. Репродукция прогонов (мной, на published фикстурах, замороженными валидаторами HEAD):
   - Позитив: `experiment_cli validate` всех 18 run-каталогов E0-R4 → ok=true, warnings=[], exit 0 (18/18); `work_cli validate docs/work/executions/EX-NL2-001-R1` → ok=true exit 0; `cli check-consistency` → ok=true exit 0. Совпадает с POS001 (19/19 checks в `case_record`).
   - Негатив (8 кейсов): N003 `{}`→exit 3/ok:false; N004 filename≠event_id→exit 3; N006 битый provenance→exit 3; N007 legacy объектный манифест→crash exit 1, `ok:true` нет (fail-closed); N008 терминал не последним→exit 3; S001 анализ без outcome→exit 3; S002 `PASS`→exit 3. Всё воспроизводится.
   - UNIT: U001 → ACCEPTED, delta 0.0, полоса 5e-7 (reference 0.097717 — pinned NL1-001, не пере-выводился); U002 → все 4 кандидата REJECTED, включая near-miss 0.0978 (delta 8.3e-5 > 5e-7).
   - GEO: g001 → 1.4142135623731/90° (в пределах 1e-12); g002 → 0.0 и `ANGLE_UNDEFINED` (value null); g003 → 60°/120°. Совпадает с пререгистрацией.
   - **Gap S003 воспроизведён**: `experiment_cli validate` на `fixtures/status/s003_tech_with_sci_claim/run` → **exit 0, ok:true, 0 warnings** — технический `RUN_COMPLETED` с `scientific_outcome=SUPPORTED` принимается тихо. Gap существует; решение «не патчить посреди кампании» (инструмент заморожен, результат сохранён как NOT_SUPPORTED с candidate-fix NL2-003) корректно по §0/§10 протокола и hard rules.

## 2. Результаты по bounded scope

| # | Пункт | Результат |
|---|---|---|
| 1 | Scope = allowed_paths; state/plan/config/scripts не тронуты; инструмент бит-в-бит | Подтверждено (одно отклонение по 3 файлам пререгистраций — F6) |
| 2 | Пререгистрация до прогонов; tolerances не «под результат»; 17/1 против frozen ожиданий; superseding только идентичность | Подтверждено (метка времени `frozen_at_utc` R2–R4 дефектна — F3) |
| 3 | Отрицательные контроли честные (≥4 воспроизведено) | Подтверждено (воспроизведено 8 + UNIT/GEO + S003) |
| 4 | Gap S003 существует; «не патчить» корректно | Подтверждено |
| 5 | Дисциплина E0-R1..R3; run ID уникальны; ожидания не подгонялись | Подтверждено (77/77 run ID уникальны; причины FAILED_TECHNICAL правдоподобны и воспроизводятся по поверхностям R1/R2/R3: repo-root off-by-one → пустые emits; кампания-relative пути → «storage_location» с `E0-R1/…E0-R2-*`; KeyError `'exit_code'` в `E0-R3-S003/case_record.json`) |
| 6 | Контракты: манифесты-массивы, события 40-hex, terminal-last, jsonschema, CLI validate | Подтверждено (кроме F1 по дайджестам case_record) |
| 7 | Claim ceiling C0; никакого self-acceptance | Подтверждено (`NOT_EVALUATED`, ACCEPTED не выставлен, handoff → review) |

## 3. Findings

### F1 (MAJOR — блокирует переход к VERIFIER в текущем виде): дайджесты `case_record.json` в `artifacts.manifest.json` не соответствуют опубликованным байтам
Во **всех 73 run-каталогах всех четырёх кампаний** запись `case_record.json` в `artifacts.manifest.json` содержит sha256/size, соответствующие *предыдущей* версии файла: в Git лежит версия с финальным ключом `schema_validation["artifacts.manifest.json"]` (ровно **+35 байт** в каждом случае). Причина установлена из исходника `e0_runner.py::emit_run` (порядок строк 452–469): манифест артефактов сериализуется **до** финальной перезаписи `case_record.json`, добавляющей результат валидации самого манифеста. Проверено воспроизведением pre-image: удаление последнего ключа `schema_validation` + каноничная сериализация даёт записанный дайджест в **73/73** случаях; значения `schema_validation` всюду пусты (валидация чиста), научные исходы не затронуты. Тем не менее это нарушение provenance-контракта (`DIGEST + PROVENANCE`; манифест обязан описывать опубликованные байты), не задокументированное имплементёром; POS001 это не ловит, т.к. ни один валидатор не сверяет дайджесты артефактов с байтами — тот же класс «структура без семантики», что и S003.
**Требуется:** erratum + ремонт emit_run (финальная запись case_record до построения манифеста) + публикация скорректированных `artifacts.manifest.json` новым evidence-коммитом (не перезапись истории); рекомендация: добавить digest-vs-blob проверку в validator hardening (NL2-003).

### F2 (MODERATE): tier-2 результат R3 приписан R4-U001 в summary-поверхностях
`evidence-map.json` (run E0-R4-U001) и `IMPLEMENTER_EVIDENCE.md` утверждают: «конверсия найдена в pinned-исходниках `src/Utilities/Utils.cpp:333`». Фактически hit получен в попытке **R3** (`E0-R3-U001/artifacts/pinned_source_excerpt.txt`); собственный tier-2 артефакт R4 — `NOT_OBTAINED` (`TimeoutExpired` после 300 с, что разрешено §11.4 как негейтящая INCONCLUSIVE-заметка; tier-1 ACCEPTED от этого не зависит, исход U001 корректен). Атрибуция в верхнеуровневых документах неточна. **Требуется:** erratum в `evidence-map.json`/`IMPLEMENTER_EVIDENCE.md` (сослаться на R3-артефакт; для R4 указать NOT_OBTAINED).

### F3 (MINOR): `frozen_at_utc` в protocol.json R2/R3/R4 несовместимы с git-хронологией
Заявлены 14:25:00Z / 15:35:00Z / 17:05:00Z при prereg-коммитах 13:34:22Z / 13:40:40Z / 13:52:47Z и исполнении R4 в 13:53Z — значения выглядят placeholder'ами (round numbers). Хронология freeze→run подтверждается только цепочкой коммитов и машинными `finished_at_utc` в case_record (что я и использовал). Вопреки требованию машинных timestamps — дефект метаданных. **Требуется:** отметить в erratum; впредь — машинная генерация поля.

### F4 (MINOR): счётчики попыток в `evidence-map.json` неточны
`failed_prior_attempts_preserved`: E0-R2 указан как «runs: 18, RUN_FAILED_TECHNICAL» — фактически 17× FAILED_TECHNICAL + POS001 RUN_COMPLETED/NOT_SUPPORTED (артефакт отказа; корректно описан в `IMPLEMENTER_EVIDENCE.md` и commit-сообщении `f2fa411`); E0-R3 «runs: 18» — фактически 19 каталогов (включая авторизованный `E0-R3-S003-RETRY1`). **Требуется:** правка текста evidence-map.

### F5 (MINOR): «Final HEAD» в `EX-NL2-001-R1/summary.md` = `24352f9`, фактический терминальный HEAD ветки — `2cee872`
После `24352f9` добавлены evidence-map/IMPLEMENTER_EVIDENCE (`9c0f7ec`), EX-события 0002–0004 и summary (`edd0ddc`) и R3-поверхности (`2cee872`); события 0002–0004 несут `subject_sha=24352f9`. Поверхности ранов R4 после `24352f9` не менялись (проверено). **Требуется:** при финальном handoff указывать фактический HEAD; здесь достаточно erratum-заметки.

### F6 (MINOR, scope): `docs/research/PREREGISTRATION_E0_R2/R3/R4.md` формально вне allowed_paths паспорта
Паспорт разрешает только `PREREGISTRATION_E0_R1.md`; superseding-документы R2–R4 потребовались протоколом (§0.1 — новая версия пререгистрации) и появились в `docs/research/`, но расширение allowed_paths нигде не зафиксировано. Содержательно корректно, процедурно — отклонение. **Требуется:** зафиксировать в branch-passport/erratum как documented deviation.

### F7 (OBSERVATION): публикация поверхностей R3 и переименование R1-событий
(a) execution-поверхности R3 (0002/0003-события, artifacts) опубликованы только терминальным коммитом `2cee872`, хотя исполнены в 13:41–13:47Z (машинные timestamps) — отклонение от «commit is the recovery unit» для попытки R3; (b) `cf9365a` переименовал 18 уже опубликованных R1-событий (расширение `.json`) — формально правка опубликованных событий, задокументированная в коммите; содержание событий не менялось. На выводы не влияет; учтено на будущее.

## 4. Итог

Все 18 контрольных случаев канонической попытки E0-R4 независимо воспроизведены, включая сохранённый gap S003 (17 SUPPORTED + 1 NOT_SUPPORTED против frozen ожиданий E0-PROTO-R1, идентичность ожиданий по всей линии R1→R4 проверена машинно). Пререгистрация, заморозка инструмента (бит-в-бит), дисциплина четырёх попыток, уникальность run ID, контрактные формы и claim ceiling C0 подтверждены. Вердикт **FIX_REQUIRED** — исключительно из-за пакета доказательств: F1 (систематический digest-mismatch манифестов артефактов, не задокументирован) и F2 (неверная атрибуция tier-2 в summary-документах), плюс минорные F3–F6. Scientific conclusion не меняется: campaign-level `NOT_EVALUATED`; приёмка E0 остаётся за VERIFIER (после fix) и Director checkpoint; merge — Human Gate.

**Next action (одно):** implementer/repair — устранить F1/F2 (erratum + скорректированные `artifacts.manifest.json`/`evidence-map.json` новым коммитом), затем независимый VERIFIER.

*Reviewer-проверки: независимые прогоны на worktree `2cee872` (валидаторы/инструменты HEAD бит-в-бит base); скрипты и логи — disposable scratch, в evidence не включаются. Старые экспериментальные события этим review не изменялись.*
