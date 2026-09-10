# NL2-001 — VERIFIER PROGRESS (verification-by-execution, раунд 2)

Независимый VERIFIER, fresh-сессия. Ветка: `verify/nl2-001-contracts-e0-r1`, субъект проверки: `work/nl2-001-contracts-e0-r1` @ `1d594f3cd6f7673307310f53393cb5680deb7696`. Метод — собственное воспроизведение (verification ≠ review); чек-лист поверхностей — §1–§5 [RE_REVIEW_R1.md](https://github.com/rootfabric/NanoLab/blob/review/nl2-001-contracts-e0-r1/docs/evidence/NL2-001/RE_REVIEW_R1.md). Промежуточный журнал; итог — `VERIFIER_VERDICT.md`.

## V1. Ancestry / scope — ВЫПОЛНЕНО

- `git merge-base --is-ancestor 15a2c9b 1d594f3` → exit 0: base `15a2c9b1b5c095e24e2e1c24afd77feef5361102` — предок проверяемого HEAD.
- `git diff --name-only 15a2c9b 1d594f3`: 815 файлов, 25689 insertions(+), 1 deletion(-); распределение: `experiments/evidence/**` 797, `docs/work/**` 9, `docs/evidence/NL2-001/**` 4, `docs/research/**` 4, `docs/experiments/E0_PIPELINE_VALIDATION.md` 1 — **все изменения только evidence-поверхности**, вне их — 0 файлов.
- Инструмент бит-в-бит base (tree-hash compare): `config` `592cddc2…`≡, `scripts` `2988ec85…`≡, `.github` `416af048…`≡, `project` `fecf726f…`≡ (base ↔ 1d594f3). `project/state.json`, `project/plan.json` не тронуты.
- Единственный не-add файл — статусная строка `docs/experiments/E0_PIPELINE_VALIDATION.md` (NOT_RUN → RUN), разрешено WO (allowed_paths, «только строка статуса»).

## V2. Контрольные прогоны E0 (собственное воспроизведение, ≥6 случаев) — ВЫПОЛНЕНО

Метод: замороженный инструмент `experiments/evidence/E0/E0-R1/tools/e0_runner.py` (бит-в-бит, см. V1) вызван на отдельном worktree `verify/nl2-001-contracts-e0-r1` @ `1d594f3`; прогоны — ТОЛЬКО в scratch (`C:\NanoLab\scratch\verify-nl2-001\`, published-поверхности не изменялись; worktree остаётся чистым). Subject E0-R4 `ce477aad1e4a125c9e881fd9f6a741ec6d2fa876`; протокол/дайджесты — `E0-R4/protocol.json` / `input_digests.json`; фикстуры материализованы runner'ом из git-блобов subject с дайджест-контролем (расхождений нет). Окружение: Python 3.11.8, jsonschema 4.22.0, git 2.53.0.windows.1 — совпадает с environment_binding протокола. Для U001 tier-2 пропущен (`--skip-tier2`: сетевой fetch — best-effort негейтящий по §11.4; в published R4 он NOT_OBTAINED).

| Кейс | Семья | Воспроизведено | Published case_record | Совпадение |
|---|---|---|---|---|
| E0-R4-U002 | UNIT | 4/4 вердикта REJECTED, вкл. подделку `0.0978` → REJECTED | то же (все REJECTED) | MATCH |
| E0-R4-N006 | NEG | битый provenance: exit 3, ok:false, errors непуст | exit 3, ok:false | MATCH |
| E0-R4-G001 | GEO | √2=1.4142135623730951 и 90° — оба query true (atol 1e-12) | то же | MATCH |
| E0-R4-S003 | STATUS | **exit 0, ok:true, separation_enforced=false → NOT_SUPPORTED (gap)** | NOT_SUPPORTED | MATCH |
| E0-R4-U001 | UNIT | T=20C→0.097717 ACCEPTED, delta=0, полоса 5e-7 | ACCEPTED (tier-1) | MATCH |
| E0-R4-POS001 | POS | 19/19 checks true (17 run-каталогов + EX + check-consistency) | 19/19 | MATCH |

Скрипт сверки (own script, `compare_case_records.py` в scratch): scientific_outcome + frozen expected + observed-ядро (exit_code/checks/verdicts/results) — **6/6 MATCH**; timestamps/durations сознательно не сравнивались (машинные). Исходы независимого воспроизведения совпали с published: **17 SUPPORTED + S003 NOT_SUPPORTED** подтверждается на выбранных 6 кейсах из 5 семей.

## V3. Digest-vs-blob всех 4 кампаний + superseded byte-equal — ВЫПОЛНЕНО

Собственный скрипт (`digest_vs_blob.py` в scratch; все байты читаются через `git cat-file blob 1d594f3:<path>` — published Git-содержимое, не autocrlf-конвертированную рабочую копию):

- Канонические `artifacts.manifest.json` @ `1d594f3`: **225/225 записей** (R1 55, R2 55, R3 59, R4 56) — sha256+size каждой записи равны фактическим блобам `artifacts/*` в Git: **0 mismatches**.
- `artifacts.manifest.v1-superseded.json` @ `1d594f3` vs канонический `artifacts.manifest.json` @ `2cee872`: **73/73 byte-equal** (blob-compare).
- Хирургичность ремонта: **73/73** — в каждом манифесте ровно одна изменённая запись (`case_record.json`), ровно поля sha256/size_bytes; имена/порядок/прочие поля неизменны.
- Замечание метода: первый вариант скрипта хэшировал рабочую копию и давал ложные 113 «mismatch» из-за autocrlf (CRLF в working tree); против блобов Git — 0. Зафиксировано как урок метода, не как дефект evidence.

## V4. Gap S003 — воспроизведён (валидатор молчит) — ВЫПОЛНЕНО

Двойная репродукция:

1. Через замороженный runner (кейс E0-R4-S003, см. V2): exit 0, `ok:true`, `separation_enforced=false` → научный исход NOT_SUPPORTED, совпадает с published.
2. Прямой CLI-проб, независимый от runner'а: фикстура `E0-R1/fixtures/status/s003_tech_with_sci_claim/run` материализована байт-в-байт из блобов `1d594f3` в scratch; `python -m harness.experiment_cli validate` → **`ok:true`, errors [], warnings [], exit 0** при событии `0002-run-completed` (`event_type=RUN_COMPLETED`, `scientific_outcome="SUPPORTED"`).

Контрактное ожидание пререгистрации (инструмент разделяет технический и научный статусы) не выполняется механически; gap сохранён и задокументирован как NOT_SUPPORTED — воспроизведён на `1d594f3` дословно.

## V5. Схемы и CLI — ВЫПОЛНЕНО

jsonschema (Draft 2020-12 + FormatChecker, схемы `config/control/harness/*.schema.v1.json` — бит-в-бит base; все payload — блобы `1d594f3`):

- **447 файлов, 0 ошибок**: все `manifest.json` (run-схема), все `events/*.json` всех run-каталогов 4 кампаний (event-схема), все `artifacts.manifest.json` + `.v1-superseded.json` (artifacts-схема), 4 campaign erratum-события (`subject_sha` каждого = subject своей кампании по run-манифестам), repair-событие `docs/evidence/NL2-001/events/0001-repair-f1-f7.json` (work-event-схема, `subject_sha=2cee872…`), события `EX-NL2-001-R1` 0001–0004 (work-event-схема).

CLI (замороженные валидаторы `scripts/harness/**` бит-в-бит base; PYTHONPATH=scripts):

- `experiment_cli validate` по run-каталогам: **E0-R1 18/18 ok**, **E0-R3 19/19 ok**, **E0-R4 18/18 ok** (все exit 0, `ok:true`, warnings пусты).
- **E0-R2: 18/18 fail** — ожидаемое задокументированное поведение; во всех 18 выходах присутствует текст `«0002-run-failed-technical.json: campaign_id differs from manifest»`, `«0003-analysis-completed.json: campaign_id differs from manifest»` (stale `campaign_id` зашит в событиях неудавшейся попытки; дефект emit-пути runner'а, задокументирован commit `f2fa411` и repair-документами; попытка superseded кампанией E0-R4). Не регресс ремонта.
- `work_cli validate docs/work/executions/EX-NL2-001-R1` → `ok:true`, exit 0, статус HANDOFF_READY.
- `cli check-consistency` → `ok:true`, exit 0 (state/plan консистентны).

## V6. Пререгистрация — ВЫПОЛНЕНО (скрипт `prereg_check.py`)

- Хронология git (author timestamps, monotone freeze → digests → campaign start) для всех четырёх попыток:
  R1 `5a151f7` 13:25:27Z → start `e3c940c` 13:26:01Z (дайджесты в самом freeze-коммите);
  R2 `e87202e` 13:34:22Z → `8355f84` 13:34:44Z; R3 `cc495fe`/`6c366e0` 13:40:40Z → `3dd0375` 13:40:49Z;
  R4 `f2e17bc`/`ce477aa` 13:52:47Z → `1688e71` 13:52:57Z. Ожидания заморожены ДО стартов; результаты — спустя десятки минут (R4-результаты `24352f9` 14:00:21Z).
- Ожидания не менялись R1→R4: все 18 кейсов protocol.json идентичны verbatim (модуль префикса run_id, кампания-само-ссылки в строках и документированный placeholder `frozen_at_utc` — erratum F3; в R1 — реальный машинный 13:18:32Z, в R2–R4 — круглые значения); `units_reference`, `geometry_tolerance`, `outcome_semantics` идентичны; литералы tolerances **5e-7 / 1e-12** присутствуют во всех ревизиях; `tools/units_check.py` (`ACCEPT_TOLERANCE=5e-7`) — frozen-поверхность E0-R1, не менялась.

## V7. Self-acceptance / E-статусы — ВЫПОЛНЕНО

- `ACCEPTED` в evidence-документах — только словарь механических вердиктов units-check (tier-1) и явное «ACCEPTED не выставляется»; campaign `claim.campaign_scientific_outcome = NOT_EVALUATED`, ceiling `C0_SOFTWARE_ONLY`; `failed_or_excluded_runs=[]`; per-run: 17× (COMPLETED, SUPPORTED) + 1× (COMPLETED, NOT_SUPPORTED) — совпадает с V2/V3.
- `next_action` evidence-map — независимый REVIEWER → VERIFIER → Director; merge — Human Gate.
- E1/E2 и `project/**` не тронуты (diff base..HEAD пуст по этим поверхностям); статус E0-дока — только execution fact (RUN), приёмка делегирована review.

## V8. Дополнительные пробы (полнота чек-листа §1–§5)

- Ремонт хирургичен: `git diff --name-status 2cee872 1d594f3` = **77 M** (73 `artifacts.manifest.json` + IMPLEMENTER_EVIDENCE, branch-passport, passport.json, evidence-map) + **80 A** (73 superseded + 4 campaign erratum-события + repair-событие + REPAIR_MAP + ERRATUM). Ни одного иного файла; `case_record.json`/события прогонов/summary/фикстуры/tools/protocol — не тронуты.
- F2 атрибуция подтверждена артефактами: R4-U001 `pinned_source_excerpt.txt` = `NOT_OBTAINED` (TimeoutExpired 300 c); R3-U001 = hit `src/Utilities/Utils.cpp:333` («Converting temperature from Celsius …»).
- F4 счётчики `failed_prior_attempts_preserved` соответствуют поверхностям (R1 18; R2 17+POS-артефакт; R3 19 каталогов).
- **O1** подтверждён: 55/55 записей R2-манифестов несут stale `storage_location` (`E0-R1/runs/E0-R2-…`) — сохранённый дефект попытки, дайджесты при этом корректны (V3).
- **O2** подтверждён: repair-событие `timestamp_utc=2026-09-09T18:25:00Z` — placeholder (коммит `5418f14` = 14:37:12Z).
- **O3** подтверждён: campaign-формат `evidence-map.json` — 11 ошибок против `evidence-map.schema.v1.json` (идентично до/после ремонта, пре-существующее).
- **Gap digest-vs-blob (F1-класс, кандидат NL2-003) воспроизведён пробой**: подмена байта `artifacts/stdout.txt` в scratch-копии E0-R4-U001 (sha256 `41b03f6d…` ≠ манифесту `b794d508…`) — `experiment_cli validate` отвечает `ok:true`, exit 0. Ни один валидатор не сверяет дайджесты с байтами (потому F1 и существовал во всех 73 каталогах) — мой digest-vs-blob (V3) потребовал собственного скрипта.
