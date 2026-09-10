# Director Acceptance — NL2-003 «Integrate workflow provenance and recovery»

Дата решения: 2026-09-10. Роль: DIRECTOR научной линии NL (fresh-сессия; контексты implementer/reviewer/verifier не переиспользовались — только Git-факты и вердиктные документы). Явная авторизация владельца на Director-приёмку и merge в main получена в миссии (Human Gate открыт). Научных прогонов в этом Work Order не было — научные статусы экспериментов не затрагиваются; применяется потолок `C0_SOFTWARE_ONLY`.

## Решение

```text
NL2-003 = ACCEPTED                    # WO-уровень: provenance/recovery схема + validator hardening исполнены и верифицированы
campaign scientific_outcome = NOT_EVALUATED   # научных прогонов нет — уровень кампании этим WO не оценивался
stage NL2 = ACCEPTED                  # стадия закрыта: NL2-001, NL2-002, NL2-003 — все ACCEPTED (каталог: acceptance NL2 = «E0/E1 validation, statistics, provenance and recovery are accepted»)
frontier = NL3
next_work_order = NL3-001 (READY)
experiment_status: без изменений      # E0 = RUN, E1 = RUN — конвенция execution-facts сохранена; научное объявление E1 = SUPPORTED (NL2-002) не пересматривается
Claim ceiling: C0_SOFTWARE_ONLY
```

## Основание — вердиктная цепочка

1. **Implementation**: `work/nl2-003-provenance-recovery-r1`, base `d121119` (без дрейфа на момент старта), subject независимого review `757eb1e` (handoff-пакет EX-NL2-003-R1, passport HANDOFF_READY), repair tip `57b986d` (repair-коммит `31997ac` — реализация F-1, repair-событие `0005` + SESSION_LOG append). Поставлено: S003, digest-vs-blob (`experiment_cli verify-digests`), emit_run порядок (обязательный фикс REPAIR_MAP_F1_R1 §5.1), O1 stale `storage_location`, O2/F3 placeholder-timestamps в `work_cli`, F-1/O3 schema-sync `evidence-map.schema.v1.json`, контракт `docs/research/PROVENANCE_RECOVERY_R1.md` + machine-readable `config/infra/provenance-recovery.v1.json`. AiiDA вне scope по постановке WO (см. «Отложено»).
2. **Independent REVIEWER = FIX_REQUIRED** (`review/nl2-003-provenance-recovery-r1` @ `b4e6758`): bounded scope 20 файлов — 0 violations; все шесть накопленных дыр (S003, digest-vs-blob, emit_run, O1, O2/F3, F-1/O3) воспроизведены негативом/позитивом самостоятельно — «ни одно закрытие не принято на веру»; 133/133 теста; регрессия published 62 green / 18 red — ровно документированная superseded E0-R2; единственная причина FIX_REQUIRED — F-1 (MODERATE): четыре поверхности заявляют midnight-контроль в `experiment_cli`, отсутствующий в коде («заявлено ≠ enforced» — тот самый класс, ради которого существовал WO).
3. **Repair R1** (выбран путь (a) — реализация): `MIDNIGHT_PLACEHOLDER` + error в `experiment_cli` (тот же класс регулярок, что в `work_cli`; правило «≥3 копий» сознательно не перенесено — sub-second прогоны легитимны); +5 unittest (итого 138 OK); errata F-2/F-3/F-4 в одном ремонт-коммите; PROVENANCE_RECOVERY_R1 §6/§7 дополнены честной пометкой, что контроль введён repair-коммитом R1 (первоначальная публикация декларировала его до реализации); F-5 — documented deviation в branch-passport.
4. **Independent VERIFIER RECHECK R1 = PASS** (`verify/nl2-003-provenance-recovery-r1` @ `52dc8cf`): F-1 закрыт реализацией и воспроизведён собственными пробами verifier'а (midnight `Z`/`+00:00` → exit 3; published E0-R4 18/18 и E1-R2 3/3 — 0 midnight-упоминаний; s003-фикстура — комбинация midnight+S003 fail-closed); errata F-2 (713 tracked @ `757eb1e`, unparseable ровно 2 pinned NEG = CI-пинам), F-3 (11/11/9 против blob `d121119`; новая схема 0/0/0), F-4 (0 mismatch на 55 реальных записях E0-R1 при exit 3 на designed-negative фикстурах — оговорка в README соответствует поведению) — подтверждены фактами; полный чек-набор после ремонта зелёный: unittest **138/138**, `work_cli` **14/14** EX OK (включая repair-событие 0005 corrections-class), verify-digests E1-R1 16/16 + E1-R2 15/15 + E0-R4 56/56 (+ бонус E0-R1/R2/R3 55/55/59) — **0 mismatch**, JSON-скан 714 tracked / unparseable ровно 2 pinned NEG, `check-consistency` ok; scope ремонтного диффа `757eb1e..57b986d` чист — ровно 10 ремонтных поверхностей; repair-событие 0005 валидно (schema 0 ошибок, post-terminal corrections-class по прецеденту EX-NL1-002-R1, машинный timestamp).
5. **Роли независимы**: implementer, reviewer, verifier — три разные fresh-сессии; ACCEPTED до настоящего решения в пакете отсутствовал (review не accept'ил, verifier верифицировал ремонт, не повышая статус); merge — Human Gate, разрешён владельцем в этой миссии.

## Перечень закрытых дыр (все — механически, негатив+позитив, независимо воспроизведены)

| Дыра | Закрытие |
|---|---|
| **S003** (технический/научный статус) | `experiment_cli` reject'ит `SUPPORTED` вне `ANALYSIS_COMPLETED` с verification-поверхностью; gap-фикстура `s003_tech_with_sci_claim` → exit 3 с явной S003-ошибкой (на base — `ok:true`); легитимная verify-цепочка → ok |
| **digest-vs-blob** (CRLF-урок NL2-002 F-3) | новый режим `experiment_cli verify-digests` — сверка sha256/size с git-блобами; E1-R1 16/16, E1-R2 15/15, E0-R4 56/56 — 0 mismatch; legacy object-манифест (n007) и отсутствующий блоб (n006) — graceful fail-closed |
| **emit_run порядок** (обязательный фикс REPAIR_MAP_F1_R1 §5.1) | `e0_runner.py` пишет финальный `case_record.json` до манифеста + digest-инвариантность; пре-фикс blob `d121119` воспроизводит ровно F1-класс (stale ровно у `case_record.json`), HEAD — 0 stale |
| **O1** (stale `storage_location`) | in-Git пути проверяются на сегменты `campaign_id`/`run_id` манифеста; 55 stale-записей superseded E0-R2 именуются механически |
| **O2/F3** (placeholder-timestamps, `work_cli`) | midnight-placeholder и копия-штампы (≥3 события с одним значением) → **ошибки**; скан базы: ровно один ≥3-хит = whitelist `LEGACY_BATCH_TIMESTAMP` (EX-NL2-002-R1 0002–0004 @ 11:37:54Z); exemption не действует под другим `execution_id` |
| **F-1/O3** (evidence-map схема) | schema follow facts: синхронизирована с campaign-конвенцией трёх принятых карт → 0/0/0 ошибок; старая checkpoint-вид схема отвергает карты (11/11/9) |
| **F-1 review R1** (MODERATE, причина FIX_REQUIRED) | закрыт **реализацией** (путь (a)): midnight-проверка в `experiment_cli` + 5 тестов; все четыре поверхности заявления согласованы с кодом; «≥3 копий» в experiment_cli не переносится (заявлено и соблюдено) |
| **F-2 / F-3 / F-4** (MINOR/INFO review) | закрыты erratum'ами в repair-коммите; верифицированы verifier'ом против фактов (713; 11/11/9; campaign-root оговорка) |
| **F-5** (INFO) | принято: documented deviation в branch-passport (вынужденное изменение существующего тест-файла, семантика правил не менялась) |

## Отложено (явно, вне ACCEPT этого WO)

1. **AiiDA-интеграция** — будущий отдельный WO (зафиксировано постановкой NL2-003 «Не входит»): настоящий WO фиксирует схему провенанса и правила stop/resume/дедупликации/readback документарно (`PROVENANCE_RECOVERY_R1` + machine-readable конфиг); RESUMED — пока конвенция (grep-поверхность), механическая автоматизация — кандидат.
2. **Schema-sync-ревизия №2** (CTRL-класс): формализация repair-паспортов и repair-event конвенций — замечание verifier'а о субъект-ссылке repair-события (`0005.subject_sha` = база EX uniform с 0001–0004 vs прецедент NL2-001 со ссылкой на ремонтируемый subject) зафиксировано для прецедентной базы, не дефект; passports-паттерн — по прецеденту CTRL-LINTSCHEMA.
3. **O1–O3-замечания re-review**: остаточные наблюдения к качеству закрытия — O1-линт бессрочно именует 55 сохранённых stale `storage_location` superseded E0-R2 (постоянная документированная красная позиция регрессии 62 green / 18 red), F-4 campaign-root скан, F-5 — приняты к сведению; повторный взгляд при следующей harness-ревизии, не блокирует.

## Checkpoint-ветка и интеграция

`control/nl2-003-director-checkpoint-r1` от repair tip `57b986d`; влиты merge-коммитами: `review/nl2-003-provenance-recovery-r1` @ `b4e6758` (merge `def3fc8`) и `verify/nl2-003-provenance-recovery-r1` @ `52dc8cf` (merge `0726e6d`) — конфликтов нет (множества файлов вердиктных веток непересекаются: `REVIEWER_VERDICT.md` + `REVIEWER_VERIFICATION_LOG.md` vs `VERIFIER_RECHECK_R1.md`). Свежий `origin/main` слит: `d121119` уже является предком repair tip'а — дрейфа нет (merge «Already up to date», свежесть подтверждена fetch'ем). Старые события всех EX-* не тронуты.

## Ограничения, переносимые явно

1. **Провананс документарен**: цепочка subject→seeds→inputs→binaries→runs→analysis→evidence-map и правила stop/resume/дедупликации/readback зафиксированы контрактом и валидаторами, но не исполняются runtime-системой (AiiDA и автоматизация RESUMED — отложены, см. выше).
2. **Grandfather-механизмы**: whitelist `LEGACY_BATCH_TIMESTAMP` и сохранённые superseded-записи E0-R2 — постоянные исключения, которые линт именует явно; не тишина, а tracked-исключения (любое новое попадание → ошибка).
3. **«Заявлено ≠ enforced»-урок F-1**: публикация NL2-003 R1 декларировала midnight-контроль до реализации — закрыто реализацией с честной пометкой в доке; дисциплина «контрактная поверхность следует коду» усилена 5 тестами.
4. Научные поверхности не затронуты: `experiments/evidence/**` в диффе NL2-003 — только разрешённый `e0_runner.py` (обязательный фикс порядка); `project/**` до настоящего checkpoint-коммита не тронуты (подтверждено обоими вердиктами).

## Изменения состояния проекта (этот checkpoint-коммит)

- `project/state.json`: NL2-003 = ACCEPTED; `completed_tasks` += NL2-003; `stage_status.NL2` = ACCEPTED (стадия закрыта: NL2-001/002/003 все ACCEPTED); `stage_status.NL3` = IN_PROGRESS; `frontier` = NL3; `next_work_order` = NL3-001; `task_status.NL3-001` = READY; `experiment_status` — **без изменений** (E0 = RUN, E1 = RUN — конвенция execution-facts; SUPPORTED-объявление E1 остаётся в вердиктных поверхностях NL2-002); `execution.physics_runs` = 7 — без изменений (научных прогонов не было).
- `config/control/harness/scheduler-policy.v1.json`: `current_checkpoint` → NL3, `next_work_order` → NL3-001, notes обновлены.
- `docs/work/WORK_QUEUE.md`: строка NL2-003 → ACCEPTED; шапка — стадия NL2 закрыта, разрешён старт NL3-001.
- `docs/work/SESSION_LOG.md`: настоящая запись (append; старые записи не редактировались).
- `docs/evidence/NL2-003/DIRECTOR_ACCEPTANCE_R1.md`: настоящий durable acceptance record.

## Условия, с которыми принято

- ACCEPT относится к repair tip `57b986d` и вердиктной цепочке `757eb1e` → `b4e6758` (FIX_REQUIRED) → repair R1 → `52dc8cf` (RECHECK PASS); любое изменение заявленных контролей в будущем — новая ревизия поверхностей, а не редактирование.
- WO-уровень ACCEPT не объявляет научных исходов: campaign-level `NOT_EVALUATED`, потолок `C0_SOFTWARE_ONLY`; статусы E0/E1 и `physics_runs` не менялись.
- Отложенные пункты (AiiDA, schema-sync №2, O1–O3 re-review) не являются частью принятого объёма и требуют собственных bounded WO/ревизий.
- Закрытие стадии NL2 не закрывает научные вопросы E0/E1: по каталогу checkpoint NL2 принята как «validation, statistics, provenance and recovery accepted» — инфраструктурный уровень; научные объявления живут в вердиктных поверхностях NL2-001/NL2-002 и не пересматриваются этим решением.

## Следующее действие

`NL3-001` «Register hinge design family» (READY, scheduler priority; depends_on NL2-003 — выполнено): зарегистрировать семейство шарниров (выбор NL0-001 — Shi–Castro–Arya hinge family; постановка `E2-SETUP-R1` готова в NL0-003), проверенная параметризация и экспорт, исходный компонент воспроизведён. Накопленные кандидаты для последующих ревизий: AiiDA-интеграция, schema-sync-ревизия №2 (repair-паспорта, CTRL-класс), автоматизация RESUMED-конвенции, O1–O3-замечания re-review.
