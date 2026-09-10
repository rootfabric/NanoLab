# EX-NL2-003-R1 — Summary (NL2-003: provenance/recovery + validator hardening)

**Ветка:** `work/nl2-003-provenance-recovery-r1` (worktree `C:\NanoLab\nl2-003`)
**Base:** `d121119add4533c77c40db287c292d0c8e542188` (canonical main, PR #32; NL2-002 ACCEPTED, next NL2-003 READY)
**Final HEAD:** см. терминальное событие 0004 и handoff-коммит (записывается фактический HEAD ветки)
**Risk / claim:** MEDIUM / C0_SOFTWARE_ONLY; campaign-level scientific_outcome = `NOT_EVALUATED`; научных прогонов не было; state.json/plan.json не менялись (Director gate).

## Сделано (bounded scope WO-NL2-003, всё с unittest позитив/негатив)

| ID дыры | Суть закрытия | Тест-контроль |
|---|---|---|
| **S003** | `experiment_cli`: `SUPPORTED` — научное заключение; отвергается на любом не-analysis событии (в т.ч. техническом терминале); на `ANALYSIS_COMPLETED` требует verification-поверхности (непустой `artifact_refs` → существующий файл). Fail-closed. | негатив: синтетический gap + опубликованная фикстура `s003_tech_with_sci_claim` → exit 3 с S003-ошибкой; позитив: terminal(null) → ANALYSIS_COMPLETED(SUPPORTED + evidence) → ok; регрессия: E0-R4 18/18 ok |
| **digest-vs-blob** | Новый режим `experiment_cli verify-digests <run|campaign> [--rev HEAD]`: sha256/size каждой записи манифеста vs git-блобы (`git cat-file`, не working copy — CRLF-урок); graceful fail-closed на legacy-формах; CI-пригоден (exit 0 ⇔ 0 mismatch) | unittest: 0-mismatch / tamper / missing blob / no manifests; canonical smoke E1-R1+E1-R2+E0-R4 |
| **emit_run (корень F1)** | `e0_runner.py::emit_run`: финальный `case_record.json` пишется ДО сериализации манифеста; запись патчится финальными байтами; digest-инвариантность schema-валидации утверждается runtime-проверкой (REPAIR_MAP_F1_R1 §5.1 — обязательный фикс) | unittest: манифест описывает опубликованные байты (0 stale) на синтетическом scaffold; на пре-фикс коде тест валится (воспроизведение F1-класса) |
| **O1** | `experiment_cli`: `storage_location` in-Git формата обязан содержать сегменты `campaign_id`/`run_id` манифеста | негатив: точная историческая форма stale-записи E0-R2 → ошибка; позитив/внешняя схема → ok; E0-R4+E1 — 0 O1 |
| **O2/F3 (timestamps)** | `work_cli`: midnight-placeholder `T00:00:00Z`, отсутствующий/непарсируемый `timestamp_utc`, константный copy-штамп на ≥3 событиях → **ошибки**; легаси batch EX-NL2-002-R1 0002–0004 grandfathered точным whitelist'ом (Director F-1 «пакетные timestamps»); 1–2 совпадающих штампа легальны (sub-second прецедент E0-R4); midnight-правило продублировано в `experiment_cli` | unittest: 8 кейсов (placeholder/passport/unparseable/missing/const-copy×3/×2-ok/legacy-ok/no-exemption) |
| **40-hex subject_sha** | Enforcement подтверждён прогоном (MINOR-2 whitelist не регрессировал): work_cli 14/14 EX OK; тесты `SubjectShaLegacyScopeTests` зелёные | существующие + новые тесты |
| **F-1/O3 (схема)** | `evidence-map.schema.v1.json` синхронизирован с де-факто campaign-конвенцией (schema follow facts — карты приняты, формат устоялся); ядро identity/provenance строго, аналитические секции открыты | jsonschema: E1-R1/E0-R4/E1-R2 → 0 ошибок каждая; stdlib-тесты ядра схемы |
| **Provenance/recovery** | `docs/research/PROVENANCE_RECOVERY_R1.md` (цепочка subject→seeds→inputs→binaries→runs→analysis→evidence-map; stop/resume: run ID не переиспользуется, RESUMED-маркер на `RUN_CHECKPOINT` нового run; дедупликация идентичной поверхности; readback из блобов) + machine-readable `config/infra/provenance-recovery.v1.json` | публикуется как контракт; механические контроли §7 документа |

Дополнительно обновлены: `scripts/harness/README.md` (verify-digests + новые правила), `config/control/harness/README.md` (секция evidence-map sync), `docs/control/EXPERIMENT_HARNESS_RU.md` (S003 enforcement + правило манифестов + ссылка на provenance-док).

## Результаты чеков (subject ce0f7de + events-коммит)

- JSON syntax: 710 tracked на момент прогона; erratum F-2 (Repair R1): на subject `757eb1e` — **713**; неизменно: ровно 2 unparseable = pinned NEG-фикстуры (sha256 = CI-пинам).
- `check-consistency`: ok, exit 0. `workflow_lint`: 0 violations.
- `work_cli validate`: 14/14 EX OK.
- `unittest discover`: **133 OK** (102 pre-existing + 31 новый).
- `verify-digests`: E1-R1 16/16, E1-R2 15/15, E0-R4 56/56 — **0 mismatch** (бонус: E0-R1/E0-R3/E0-R2 — 55/59/55, 0 mismatch).
- evidence-map schema: 3/3 → 0 ошибок.
- Регрессия published runs: 62 green; red ровно 18 — документированная superseded-попытка E0-R2 (2 pre-existing stale-campaign_id + 3 новых O1-ошибки на сохранённом дефекте; новых красных поверхностей нет).

## Границы исполнения

- AiiDA-интеграция НЕ выполнялась — зафиксирована как будущий bounded WO (PROVENANCE_RECOVERY_R1 §8).
- Опубликованные evidence-поверхности не редактировались; единственное изменение в `experiments/evidence/**` — `E0/E0-R1/tools/e0_runner.py` (обязательный фикс REPAIR_MAP §5.1; исторические subject'ы сохраняют старый блоб в git-истории).
- Graceful crash-пути (N001/N002/N007), engine-coupled E0-кейсы, F-2 эстиматоры — вне scope (WO «Не входит»).

## Open risks

- Правило «константный copy-штамп ≥3 событий» может требовать per-event штампования при batch-записи событий будущих handoff'ов (стоимость минимальна; легаси не тронуто).
- `verify-digests` читает HEAD по умолчанию — для исторических сверок указывать `--rev <subject>`; больших внешних (вне Git) артефактов пока не покрывает (схема storage_location остаётся строкой).
- RESUMED-конвенция пока grep-поверхность review, не автоматический чек.

## Next action (одно)

Независимый REVIEWER (fresh-сессия): проверить evidence-пакет EX-NL2-003-R1 на exact HEAD — каждая закрытая дыра с позитив/негатив-тестом, все чеки §«Результаты», отсутствие новых красных поверхностей → `docs/evidence/NL2-003/REVIEWER_VERDICT.md`; затем VERIFIER; merge — Human Gate.

---

## Repair R1 (2026-09-10) — по REVIEWER_VERDICT `FIX_REQUIRED` @ `b4e6758` (review/nl2-003-provenance-recovery-r1)

**F-1 (MODERATE, единственная причина вердикта) — закрыт путём (a), реализация:** `experiment_cli` теперь отвергает midnight-placeholder `timestamp_utc` в experiment-событиях (тот же `MIDNIGHT_PLACEHOLDER`-паттерн, что в `work_cli`; правило «≥3 копий» сознательно не перенесено — sub-second прогоны легитимны). Исполнительная формулировка R1 («продублировано в experiment_cli») объявляла контроль до его реализации — тот самый класс «заявлено ≠ enforced»; теперь заявленное и реализованное совпадают. Тесты: валидный run с тремя `T00:00:00Z`-событиями → exit 3 (3 midnight-ошибки); легитимные машинные штампы → ok; offset-форма `+00:00` → ошибка; published-фикстура s003 дополнительно флагует midnight; published E0-R4/E1-R2 — 0 midnight-ошибок (регрессия).

**Erratum F-2 (MINOR):** записи 0002/0003 и прежний текст настоящего summary утверждали «JSON 710 tracked». Фактически на subject `757eb1e` — **713** (base `d121119` = 707; ветка добавила 6: `provenance-recovery.v1.json` + 5 JSON-файлов EX-NL2-003-R1). Число 710 было истинным в момент измерения (до публикации событий 0002–0004), но в durable-записи устарело. Существенное утверждение верно и не меняется: unparseable ровно 2, оба — pinned NEG-фикстуры (sha256 = CI-пинам). События неизменяемы — исправление фиксируется настоящим erratum и repair-событием 0005.

**Erratum F-3 (MINOR):** формулировка «11 идентичных ошибок на каждой кампанской карте» (config/control/harness/README.md + описание схемы) неточна: старая схема против опубликованных карт даёт **11 / 11 / 9** ошибок (E1-R1 / E0-R4 / E1-R2). Исправлено в обоих документах; существенное утверждение (все три карты старой схемой отвергаются, новой — 0 ошибок) подтверждено.

**Erratum F-4 (INFO):** `scripts/harness/README.md` дополнен оговоркой: скан корня кампании, содержащей designed-negative фикстуры (E0-R1), даёт graceful errors и exit 3 при 0 mismatch на всех реальных прогонах — для таких кампаний сканировать поддерево `runs/`. Код не менялся (поведение fail-closed корректно).

**F-5 (INFO) — задокументированное вынужденное отклонение:** изменение существующего `tests/test_work_cli_corrections.py` против буквы WO («новые unittest-файлы») зафиксировано в branch-passport как documented deviation (вынужденное: константный штамп генератора фикстур стал бы ошибкой нового валидатора; семантика проверяемых правил не менялась — подтверждено REVIEWER'ом).

**Результаты после ремонта:** unittest **138 OK** (133 + 5 новых midnight-тестов); S003-фикстура → exit 3 (S003 + midnight по событиям); все 5 чеков зелёные (JSON 713 tracked на 757eb1e, unparseable ровно 2 pinned NEG; consistency ok; work_cli 14/14 EX; lint 0); verify-digests: E1-R1 16/16, E1-R2 15/15, E0-R4 56/56, E0-R1/runs 55/55 — 0 mismatch. Научные исходы не затронуты; campaign-level `NOT_EVALUATED`; приёмка NL2-003 остаётся за VERIFIER и Director.

**Next action (обновлённый):** независимый VERIFIER: подтвердить repair R1 на exact HEAD (F-1 реализация + тесты, errata F-2/F-3/F-4, F-5 documented deviation, полный чек-набор) ; merge — Human Gate.
