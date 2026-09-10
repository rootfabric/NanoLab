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

- JSON syntax: 710 tracked, ровно 2 unparseable = pinned NEG-фикстуры (sha256 = CI-пинам).
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
