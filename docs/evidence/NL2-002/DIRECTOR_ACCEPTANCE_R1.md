# Director Acceptance — NL2-002 «Validate statistics and E1» + первое научное объявление статуса E1

Дата решения: 2026-09-10. Роль: DIRECTOR научной линии NL (fresh-сессия; контексты implementer/reviewer/verifier не переиспользовались — только Git-факты и вердиктные документы). Явная авторизация владельца на Director-приёмку и merge в main получена в миссии (Human Gate открыт). Это **первое объявление статуса эксперимента** в истории линии — применён максимальный уровень строгости по `docs/SCIENTIFIC_METHOD.md`.

## Решение

```text
NL2-002 = ACCEPTED                    # WO-уровень: статистическая инфраструктура и T2 исполнены и верифицированы
E1 = SUPPORTED                        # НАУЧНОЕ ОБЪЯВЛЕНИЕ по пререгистрации E1-PROTO-R1 §9 (см. ниже)
frontier = NL2                        # без изменений; stage NL2 = IN_PROGRESS (провананс/восстановление — NL2-003)
next_work_order = NL2-003 (READY)
experiment_status.E1 = RUN (в state.json)   # конвенция execution-facts; научный исход SUPPORTED объявлен вердиктными поверхностями (см. §Enum)
physics_runs = 4 → 7                  # S001 + P001–P003 + C001–C003, все published
Claim ceiling объявления: C1_COMPUTATIONAL_REPRODUCTION
```

## Объявление статуса E1: что утверждается и что не утверждается

**Пререгистрация**: критерий зафиксирован ДО данных — `E1-PROTO-R1` §9 (пререгистрация NL0-003, blob неизменен с base; проверено reviewer'ом и verifier'ом blob-идентичность): campaign-критерий выполнен ⟺ **T1 = PASS И все T2-реплики IN_BAND**; полоса/оракул из upstream `quick_compare` (`ColumnAverage::energy.dat::2::-1.37970256144::0.15`); superseding только `E1-PROTO-R2` §2 (freeze `R_confirm = 3` до confirmatory кампании), остальные пункты R1 унаследованы без изменений.

**Механический факт по данным**: критерий §9 на confirmatory set `E1-R1-S001 + E1-R2-C001..C003` (n = 4) ВЫПОЛНЕН — per-replica |Δ| = 0.0142 / 0.0125 / 0.0215 / 0.0232 ≤ 0.15 (4/4 IN_BAND), T1 = PASS (published execution fact NL1-002, cross-check воспроизведён), целостность §5.2 OK (1001 строка ×4, 10 конфигураций, NaN/Inf = 0), все значения опубликованы полностью, исключений/повторов/скрытых retries НЕТ.

**Подтверждён независимо трижды** (три разные fresh-сессии, три независимых пути):

1. **IMPLEMENTER** (кампания `E1-R2`, freeze `f34e62ca` до прогонов, reuse бит-в-бит сборки E1-R1 `ffc80b1a…`): 3/3 T2 COMPLETED с первого запуска, distinct seeds (факты `log.dat`), 15/15 digest-vs-blob.
2. **REVIEWER** (`9e26748`, PASS): воспроизведение avg col2 ×4 из published-блобов байт-в-бит инструментом + независимый Decimal-пересчёт mean/SD(n−1)/range — точное совпадение до 11 знака; freeze-хронология подтверждена git-датами (freeze 21:21:21 → campaign-START 21:23:45 → прогоны); 7/7 seeds попарно различны; критерий §9 MET подтверждён формально.
3. **VERIFIER** (`fe24e48`, PASS): fresh rebuild pinned oxDNA `00dc7fb9` по `ENGINE_ENVIRONMENT_R1` §3 (критерий размеров 3/3 байт-в-байт, флаги MATCH, SHA-256 бинаря свежей сборки ≠ implementer-ский — ожидаемо и подтверждает независимость) + **собственная confirmatory реплика C-VERIFY**: verbatim quick_input, новый seed 319832093 (9-й опубликованный seed, не входит в 7 кампании), exit 0, 1001 строка, avg col2 = **−1.39396936364**, |Δ| = 0.01426680220 → **IN_BAND**. Статистика confirmatory set: Decimal-пересчёт 3/3 MATCH.

**Объявляется (в пределах claim ceiling `C1_COMPUTATIONAL_REPRODUCTION`)**: *независимая вычислительная репродукция reference-пути (upstream-эталона `quick_compare`) на pinned среде подтверждена* — воспроизведение upstream-оракула в пререгистрированной полосе с preregistered статистической согласованностью повторов (distinct seeds), на зафиксированной среде, с полной публикацией данных и механически проверяемым критерием.

**НЕ объявляется** (по `SCIENTIFIC_METHOD` «Три независимых вопроса» успех уровня 1–2 не доказывает уровень 3):

- НЕ «наука верна» и НЕ «oxDNA физически валиден»: физическая валидность модели, применимость к короткому дуплексу — вне scope (`E1-PROTO-R1` §2.4, S02). Уровень 3 (соответствие модели реальному объекту) этим WO не затрагивался.
- НЕ утверждение о сборке/фолдинге/кинетике ДНК и о переносимости на другие среды/GPU.
- НЕ обобщение за пределы frozen subject: один observable (среднее колонки 2 `energy.dat` = потенциальная энергия на нуклеотид, OBSERVED-in-source), одна система (DSDNA8), одна конфигурация (`quick_input` verbatim), одна машина/сборка.
- Вычислительная репродукция ≠ независимая реализация анализа и ≠ физический эксперимент (`SCIENTIFIC_METHOD` «Независимая проверка»); C-VERIFY verifier'а — та же машина/архитектура, это ограничение зафиксировано самим verifier'ом.

## Основание — вердиктная цепочка

1. **Implementation**: `work/nl2-002-validate-e1-r1`, base `0176098` (без дрейфа), START `878e1ab`, freeze кампании `f34e62ca` (subject: campaign.md + protocol.json + analyze_energy.sh байт-в-бит из E1-R1, blob `77cfcc63`), campaign-START `42cb851` (push до первого прогона), handoff-HEAD `6cc7fde` (EX-NL2-002-R1, passport HANDOFF_READY). Поставлено: T2 confirm 3/3 COMPLETED (C001 −1.36722173127, C002 −1.35818087512, C003 −1.35653082817; seeds −1641386734 / 977680137 / −999572227), confirmatory-статистика по frozen правилам (mean −1.36896744830, SD(n−1) 0.01729656703 = 11.5% полосы; размах 0.03740553047), целостность §5.2, контрактная обвязка (манифесты-массивы, машинные события, терминал перед анализом), evidence-пакет `docs/evidence/NL2-002/IMPLEMENTER_EVIDENCE.md` + `experiments/evidence/E1/E1-R2/**`. Campaign-level scientific_outcome в публикациях исполнителя = NOT_EVALUATED; recommendation SUPPORTED корректно подчинён процедуре. Бюджет: 32.91 s wall ≈ 0.009 core-hour ≪ cap 1 core-hour.
2. **Independent REVIEWER = PASS** (`review/nl2-002-validate-e1-r1` @ `9e26748`): 6/6 bounded-проверок — scope (51 файл, все в allowed_paths; SESSION_LOG строго append; forbidden-поверхности blob-идентичны base), freeze-дисциплина (git-хронология; frozen-файлы не менялись после freeze; артефакты не менялись после END_EXECUTION; 7/7 seeds distinct), воспроизведение статистики (байт-в-бит + Decimal, формальное подтверждение §9 MET), протокольная чистота (verbatim-фингерпринты §3 в логах, эксперимент_cli 3/3 ok, jsonschema 15/15, digest-vs-blob 15/15), честность интерпретации (SD 11.5% vs пилот 5.6% явно опубликован; диагностика §4 не gate и не использовалась для подгонки; «подгонка под PASS» по данным Git не подтверждается), 5 findings — все LOW/INFO, ни один не блокирующий.
3. **Independent VERIFIER = PASS** (`verify/nl2-002-validate-e1-r1` @ `fe24e48`): scope/subject OK (13/13 forbidden-поверхностей IDENTICAL), независимый fresh rebuild + C-VERIFY IN_BAND (см. выше; первая попытка корректно классифицирована FAILED_TECHNICAL по ошибке верификатора, повтор новым запуском в новом каталоге — негатив сохранён в логе, техническое отделено от научного), статистика Decimal 3/3 MATCH, digest-vs-blob 15/15 на блобах Git, схемы/CLI OK (experiment_cli 3/3, work_cli ok=true HANDOFF, check-consistency ok), гигиена полномочий OK (self-acceptance нет; SUPPORTED только как recommendation).
4. **Роли независимы**: implementer, reviewer, verifier — три разные fresh-сессии (каждый вердикт фиксирует независимость; review PASS принимался verifier'ом только как контекст маршрута); ACCEPTED до настоящего решения в пакете отсутствовал; merge — Human Gate, разрешён владельцем в этой миссии.

## Enum `project/state.json` — решение по `experiment_status.E1` (комиссия)

Постановка: заменить ли `experiment_status.E1 = RUN → SUPPORTED`. Проверка допустимых значений:

- **Формальной JSON-схемы `state.json` в репозитории нет** (в `config/control/harness/*.schema.v1.json` state-схема отсутствует; машинный контроль — `scripts/harness/contracts.py::check_consistency`: только ID-наборы `experiment_status` vs `plan.json` + консистентность `scheduler-policy`, значения не проверяются).
- **Де-факто конвенция state.json**: значение `experiment_status` несёт только execution facts — `{NOT_RUN, RUN}` (установлено в NL2-001: «`E0 = RUN` — констатация исполненного execution fact…, а не объявление научного исхода»; `E1 = RUN` с NL1-002). Значение `SUPPORTED` в `experiment_status` ни разу не использовалось.
- **Формальный словарь научных исходов** `SCIENTIFIC_OUTCOMES = {SUPPORTED, NOT_SUPPORTED, INCONCLUSIVE, NOT_EVALUATED, INVALIDATED}` (`scripts/harness/experiment_cli.py`, `PROJECT_CONTROL.md` «Научный результат отделён от технического») — это словарь поля `scientific_outcome` campaign/анализ-событий, а не поля `experiment_status` в state.json.

**Решение**: `experiment_status.E1` остаётся `"RUN"` (фактическая конвенция execution-facts; тихая смена семантики трекаемого поля без schema/policy-ревизии нарушила бы дисциплину конвенций). Объявленный научный исход **E1 = SUPPORTED** фиксируется авторитетно в: настоящем record (durable acceptance record в main — по `PROJECT_CONTROL.md` именно он делает checkpoint принятым), статусной строке `docs/experiments/E1_REFERENCE_REPRODUCTION.md` (Director-owned поверхность, для implementer'а была forbidden именно поэтому), `scheduler-policy.v1.json` notes, `WORK_QUEUE.md`, `SESSION_LOG.md`. Полный словарь исходов останется доступным campaign-поверхностям: при будущих ревизиях harness (NL2-003 schema-sync-ревизия №2) можно формализовать отдельное поле научного исхода эксперимента в state-схеме — сейчас не делается (не менять схемы тем же коммитом, что объявляет статус).

## Checkpoint-ветка и интеграция

`control/nl2-002-director-checkpoint-r1` от handoff-HEAD `6cc7fde`; влиты merge-коммитами: `review/nl2-002-validate-e1-r1` @ `9e26748` и `verify/nl2-002-validate-e1-r1` @ `fe24e48` (конфликтов нет — множества файлов непересекаются). Слейт свежий canonical main `7b0c885` (дрейф base 0176098 → 7b0c885, 10 коммитов: PR #31 CTRL-LINTSCHEMA — MINOR-4 fail-closed TAB-чек, NOTE-5 non-mapping jobs, schema-sync enum/40-hex/паспорт-паттерн, снятие блокиратора INFRA2-001). Конфликт только `docs/work/SESSION_LOG.md` (два параллельных аппенда) — разрешён аддитивно, обе записи сохранены, хронология соблюдена (CTRL-LINTSCHEMA 21:06+10 → NL2-002 handoff 21:41+10); старые записи не редактировались. Старые события всех EX-* не тронуты.

## Ограничения, переносимые явно (из remaining_risks и вердиктов — видны рядом с выводом)

1. **SD confirmatory set вдвое выше пилотного**: 0.0173 (11.5% полосы, n = 4) vs 0.0083 (5.6%, пилот n = 3) — согласуется с малой выборкой, но подтверждает, что пилотная 5.6%-оценка была оптимистичной; на n = 4 без претензии на точный CI (§6.3 R1).
2. **Neff**: кадры траектории — НЕ независимые наблюдения; between-replicate SD — единственная gatинговая статистика. Диагностика §4 R2 (не gate): ac(1) 0.59–0.83, τ_int ≈ 10–60 prints, Neff ≈ 8–48 из 1001 строки на траекторию; независимый пересчёт reviewer'а (F-2) даёт для C003 τ_int ≈ 68, Neff ≈ 7.3 — «Neff ≥ 8» не гарантия. PyMBAR-level ESS/корреляционный анализ — открытая задача.
3. **Одна машина/сборка**: все 4 точки confirmatory set + C-VERIFY на одной campaign-машине (NATIVE_COMPILATION — бинарь привязан к CPU; перенос требует пересборки и записи новых SHA-256). Независимость повторов обеспечена distinct seeds (upstream-семантика), не машинами/бинарями.
4. **Seeds случайны при каждом прогоне** (upstream-семантика): точные значения невоспроизводимы; воспроизводима статистика повторов в полосе.
5. **CRLF-ловушка** (review F-3): дайджесты артефактов относятся к LF-блобам; Windows working-copy при `core.autocrlf=true` (например energy.dat 50050 B vs 49049 B) даст ложные mismatch — сверка только binary-safe `git cat-file blob`. Требование документируется в verifier-инструкциях (кандидат NL2-003).
6. **Runtime-акты не пере-наблюдаемы из Git** (review F-5): «SHA-256/флаги/CMakeCache бинаря верифицированы перед кампанией», «4/4 on-place SHA входов перед каждым прогоном» — документированное ограничение уровня доказательства; косвенная поддержка — машинные фингерпринты логов (verbatim §3) и полное воспроизведение всех чисел.
7. **Пакетные timestamps событий** (review F-1): `0001-started`/`0002-run-completed` несут время авторизации пакета, не момент каждого события; по-процессную хронологию устанавливает только Git-хронология коммитов.
8. Модельные ограничения (§2.4 R1): применимость oxDNA к короткому дуплексу; физическая валидность — вне scope.

## Findings — диспозиция

- **Review F-1 (LOW, timestamps)** — принять к сведению; машинное правило по-событийных timestamps — кандидат NL2-003 (emit_run/event-emission hardening).
- **Review F-2 (LOW, τ_int/Neff worst-case)** — принять; опубликовать уточнение не требуется (диагностика явно best-effort, не gate; границы «≈» и так не гарантия), но будущие публикации диагностик — с worst-case эстиматором. Кандидат NL2-003+ (статистическая диагностика).
- **Review F-3 (INFO, CRLF у verifier'ов)** — перенесено в ограничения №5; документирование в verifier-инструкциях — кандидат NL2-003.
- **Review F-4 / Verify F-1 (INFO/MINOR, campaign evidence-map вне v1-схемы)** — подтверждено verifier'ом на предшественниках (E1-R1, E0-R4 дают те же 11 ошибок): это расхождение схемы и устоявшейся конвенции, не дефект NL2-002. Кандидат: отдельная campaign-evidence-map схема — в schema-sync-ревизию №2 (NL2-003).
- **Review F-5 (INFO, эпистемическая граница Git-only)** — принято как ограничение №6.
- Превышений claim не обнаружено: `SUPPORTED` до настоящего решения в пакете присутствовал только как recommendation; campaign-level NOT_EVALUATED сохранён во всех научных поверхностях; `project/**`, `config/**`, `scripts/**`, протоколы E1, артефакты E1-R1 на work/review/verify-ветках не тронуты (подтверждено обоими вердиктами: blob/tree-идентичность).

## Изменения состояния проекта (этот checkpoint-коммит)

- `project/state.json`: NL2-002 = ACCEPTED; `completed_tasks` += NL2-002; `next_work_order` = NL2-003; `task_status.NL2-002` = ACCEPTED; `task_status.NL2-003` = READY; `execution.physics_runs` = 4 → 7 (published: S001, P001–P003, C001–C003); frontier NL2 и stage NL2 = IN_PROGRESS — без изменений; `experiment_status.E1` = RUN — без изменений (см. §Enum).
- `config/control/harness/scheduler-policy.v1.json`: next_work_order → NL2-003, notes обновлены (объявление E1 = SUPPORTED, ограничения, очередь NL2-003).
- `docs/experiments/E1_REFERENCE_REPRODUCTION.md`: статусная строка → SUPPORTED с полным обоснованием, claim ceiling и ограничениями (Director-owned поверхность).
- `docs/work/WORK_QUEUE.md`: строка NL2-002 → ACCEPTED/E1 = SUPPORTED; шапка — старт NL2-003 разрешён.
- `docs/work/SESSION_LOG.md`: настоящая запись (append; старые записи не редактировались).
- `docs/evidence/NL2-002/DIRECTOR_ACCEPTANCE_R1.md`: настоящий durable acceptance record.

## Условия, с которыми принято

- Объявление относится к frozen subject `f34e62ca` и опубликованным блобам; любое изменение протокола/полосы/статистики в будущем — новая protocol revision, а не редактирование.
- Одна инструментальная среда; внешняя (другая машина/ОС) репродукция — будущая работа (соотносится с NL5-002 external reproduction).
- Данные confirmatory set (n = 4) не заменяются C-VERIFY: C-VERIFY — дополнительная точка воспроизводимости за пределами исходной выборки, критерий §9 остаётся определённым на frozen set.
- Статус NL2-002 (WO) = ACCEPTED не делает принятым checkpoint NL2 целиком: по каталогу checkpoint он закрывается только после provenance/recovery (NL2-003).

## Следующее действие

`NL2-003` «Integrate workflow provenance and recovery» (READY, scheduler priority): подключение провенанса (AiiDA), хранение, остановка/resume, дедупликация, readback evidence + накопленные hardening-кандидаты: S003 (разделение технического/научного статусов), digest-vs-blob валидация, emit_run порядок записи, O1–O3 (NL2-001 observations), campaign evidence-map схема (F-4/F-1), по-событийные timestamps (F-1 review), CRLF-инструкции для verifier'ов (F-3), worst-case диагностические эстиматоры (F-2). Уже закрыто вне очереди: MINOR-4 (TAB-чек линта) и schema-sync enum — CTRL-LINTSCHEMA, PR #31.
