# NL2-001 — RE-REVIEW R1 (аддендум к REVIEWER_VERDICT: проверка ремонта F1–F7)

**Вердикт по ремонту: `PASS`** — findings F1–F6 из [REVIEWER_VERDICT.md](REVIEWER_VERDICT.md) (`FIX_REQUIRED`, @ `2c3b485`) закрыты корректно и проверяемо; F7 принят к сведению. Научные исходы и наука не изменены. Путь к VERIFIER открыт; merge — Human Gate. Claim ceiling по-прежнему `C0_SOFTWARE_ONLY`, campaign-level `NOT_EVALUATED`.

- **Ремонтируемый subject:** `2cee872179bbcccff93c1b9458c6b25ea491a999` (проверенный в R1 HEAD).
- **Проверенный repaired HEAD:** `1d594f3cd6f7673307310f53393cb5680deb7696` (ветка `work/nl2-001-contracts-e0-r1`, 10 ремонтных коммитов `0d9df16..1d594f3`).
- **Метод:** независимые blob- и digest-проверки против `2cee872`/`1d594f3`, schema-валидация, CLI-пробы на обоих состояниях (пре-ремонтное состояние взято из review-ветки @ `2c3b485`, чьё E0-содержимое байт-идентично `2cee872`).

## 1. F1 (MAJOR) — закрыт, подтверждено независимо

| Проверка (моя, независимо) | Результат |
|---|---|
| `artifacts.manifest.v1-superseded.json` @ `1d594f3` byte-equal каноническому `artifacts.manifest.json` @ `2cee872` | **73/73** (blob-compare, 0 отличий) |
| Канонические манифесты @ `1d594f3`: sha256/size **всех** записей vs фактические байты в Git | **225/225, 0 mismatch** (R1 55, R2 55, R3 59, R4 56) — совпадает с заявленным |
| Хирургичность: в каждом манифесте изменена ровно одна запись (`case_record.json`, только sha256/size); имя/порядок/прочие поля — без изменений | **73/73** |
| `case_record.json` байты `2cee872`→`1d594f3` | изменённых **0** (научное содержимое нетронуто) |
| Schema-valid манифестов (73 канонических + 73 superseded, `artifact-manifest.schema.v1.json`) | 0 ошибок |
| 4 campaign erratum-события (`E0-R*/events/0001-erratum-f1-manifest-digests.json`) vs `experiment-event.schema.v1.json` | 0 ошибок; `subject_sha` = subject своей кампании; timestamps машинные (14:29:13Z/14:29:35Z/14:32:01Z — согласуются с commit-временами) |
| Repair-событие `docs/evidence/NL2-001/events/0001-repair-f1-f7.json` vs `work-event.schema.v1.json` | 0 ошибок; `event_type=REPAIR_COMPLETED`; `subject_sha=2cee872` (корректно: subject ремонта) |
| [REPAIR_MAP_F1_R1](https://github.com/rootfabric/NanoLab/blob/work/nl2-001-contracts-e0-r1/docs/evidence/NL2-001/REPAIR_MAP_F1_R1.md) | корректен: root cause (порядок записи в `emit_run`), pre-image 73/73 +35 B, метод, гарантии — совпадают с моими собственными проверками R1-верdict'а; CLI-заявления (R1 18/18, R3+R4 37/37, R2 — сохранённое отклонение) воспроизведены |

CLI после ремонта (моя репродукция на `1d594f3`): `experiment_cli validate` — E0-R1 **18/18 ok**, E0-R3 **19/19 ok**, E0-R4 **18/18 ok** (0 warnings); `work_cli validate EX-NL2-001-R1` ok=true exit 0; `check-consistency` ok exit 0. Заявленное «225/225, 0 mismatch» подтверждено моим независимым digest-vs-blob прогоном.

**Замечания, не блокирующие (сохранённые дефекты неудавшейся попытки, задокументированные ремонтом):**
- **O1:** 55 записей R2-манифестов несут `storage_location` на несуществующие пути `E0-R1/runs/E0-R2-*` (stale campaign-id дефект попытки R2). Дайджесты при этом корректны (проверено резолюцией по реальному пути); REPAIR_MAP §3.2 («прочие поля — без изменений»), §5.3 и R2-erratum-событие фиксируют сохранение дефекта как есть. Принято для superseded-попытки; кандидат на очистку вместе с NL2-003 hardening.
- **O2:** `timestamp_utc = 18:25:00Z` в repair-событии — placeholder-значение (commit `5418f14` = 14:37:12Z; campaign-erratum-события при этом имеют точные машинные timestamps). Рецидив F3-класса в одном поле; хронология авторитетно устанавливается цепочкой коммитов. Отметка на будущее — только машинная генерация.
- **O3:** campaign-формат `evidence-map.json` не соответствует `evidence-map.schema.v1.json` (11 ошибок схемы — **идентично до и после ремонта**, пре-существующее несоответствие формата «campaign evidence-map» vs harness-схема; заявленные в протоколе jsonschema-проверки покрывали только run/event/artifacts-схемы и были честными). Кандидат NL2-003 на выравнивание формата.

## 2. F2 / F3–F5 — закрыты, документы согласованы с фактами

- [ERRATUM_F2_F5_R1.md](https://github.com/rootfabric/NanoLab/blob/work/nl2-001-contracts-e0-r1/docs/evidence/NL2-001/ERRATUM_F2_F5_R1.md) сверён с артефактами: R4-U001 tier-2 = `NOT_OBTAINED` (TimeoutExpired 300 с, разрешено §11.4, негейтящее); hit `src/Utilities/Utils.cpp:333` — артефакт `E0-R3-U001`; tier-1 ACCEPTED не зависит — атрибуция теперь верна в `evidence-map.json` (run-entry U001) и `IMPLEMENTER_EVIDENCE.md` (диффы проверены).
- F3 (frozen_at placeholder'ы R2–R4) и F5 («Final HEAD» summary) описаны точно; `summary.md` не переписывался (corrections — новым документом) — соответствует правилу «старые события не редактировать».
- F4: счётчики в `evidence-map.json` исправлены (R2: «17× RUN_FAILED_TECHNICAL + POS001 RUN_COMPLETED/NOT_SUPPORTED»; R3: 19 каталогов с RETRY1) — совпадает с фактическими поверхностями.

## 3. F6 — закрыт

`passport.json`: `allowed_paths` дополнены `docs/research/PREREGISTRATION_E0_R2/R3/R4.md` и `experiments/evidence/E0/E0-R2|R3|R4/**`; отклонение зафиксировано в `branch-passport.md` (раздел «Documented deviations») и в repair-событии. Процедурное отклонение теперь задокументировано.

## 4. E0-R2 CLI 18× fail — задокументированный дефект попытки, НЕ регресс ремонта

Моя репродукция на **обоих** состояниях: пре-ремонт (`2cee872`-содержимое) — **0/18 ok**; пост-ремонт (`1d594f3`) — **0/18 ok**; текст ошибки идентичен: `«0002-run-failed-technical.json: campaign_id differs from manifest»`, `«0003-analysis-completed.json: campaign_id differs from manifest»` — events неудавшейся попытки R2 несут зашитый `campaign_id=E0-R1` (дефект emit-пути runner'а, задокументирован ещё в commit `f2fa411`). Ремонт эти файлы не менял (diff-проверено: в R2 изменён только `artifacts.manifest.json` + добавлены superseded-копия и campaign-erratum-событие). Попытка R2 superseded кампанией E0-R4. Не регресс.

## 5. Исходы/наука не изменены

`git diff --name-status 2cee872..1d594f3`: **только** evidence-обвязка — M: `artifacts.manifest.json` (73), `evidence-map.json`, `IMPLEMENTER_EVIDENCE.md`, `passport.json`, `branch-passport.md`; A: `*.v1-superseded.json` (73), 4 campaign erratum-события, repair-событие, `REPAIR_MAP_F1_R1.md`, `ERRATUM_F2_F5_R1.md`. Не тронуты: `case_record.json`/`stdout`/`stderr`/`summary.md`/`manifest.json`/события 0001–0003 всех 73 run-каталогов (blob-compare: 0 изменений), фикстуры, tools, `protocol.json`, `campaign.md`, `input_digests.json`, пререгистрации, `config/**`/`scripts/**`/`project/**` (инструмент по-прежнему бит-в-бит base). Новых прогонов нет; run ID не переиспользовались; научный итог неизменен: **17 SUPPORTED + S003 NOT_SUPPORTED (gap сохранён), campaign-level NOT_EVALUATED**.

## 6. Итог

| Finding R1-вердикта | Статус после ремонта |
|---|---|
| F1 (MAJOR) | **Закрыт** (73 манифеста исправлены, superseded byte-equal, 225/225 дайджестов, события schema-valid, REPAIR_MAP точен) |
| F2 (MODERATE) | **Закрыт** (атрибуция tier-2 исправлена в обоих документах) |
| F3/F4/F5 (MINOR) | **Закрыты** (erratum-документ; счётчики исправлены; summary не переписывался) |
| F6 (MINOR, scope) | **Закрыт** (allowed_paths расширены, отклонение задокументировано) |
| F7 (OBSERVATION) | Принят к сведению без правок — корректно |
| Новые замечания re-review | O1 (stale storage_location R2 — сохранён и задокументирован), O2 (placeholder-timestamp в repair-событии), O3 (формат campaign evidence-map vs схема) — не блокирующие, кандидаты NL2-003 |

**Next action (одно):** независимый VERIFIER — проверить repair-поверхности на exact HEAD `1d594f3` (по чек-листу §1–§5 настоящего аддендума), затем Director checkpoint; merge — Human Gate.

*Re-review выполнено независимо (fresh-проверки на отдельном worktree; скрипты — disposable scratch). Ре-ветка ревьюера: `review/nl2-001-contracts-e0-r1`. Старые события не редактировались; вердикт R1 (`REVIEWER_VERDICT.md`) сохранён без изменений.*
