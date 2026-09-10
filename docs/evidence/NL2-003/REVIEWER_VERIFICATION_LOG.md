# NL2-003 — REVIEWER VERIFICATION LOG (независимое воспроизведение)

**Рецензент:** независимый fresh-агент (REVIEWER), без доступа к контексту имплементёра.
**Worktree:** `C:\NanoLab\review-nl2-003` (checkout `757eb1e7889f79379a597b03099de7969f276fbf`, ветка `review/nl2-003-provenance-recovery-r1`).
**Окружение:** Python 3.11.8, jsonschema 4.22.0, Windows/PowerShell (совпадает с environment_binding предшествующих вердиктов). Прогоны — disposable scratch `C:\NanoLab\scratch\review-nl2-003\`; published-поверхности не изменялись (git status чист).

## 1. Scope

- `git diff --name-only d121119..757eb1e` = **20 файлов**, все внутри allowed_paths паспорта EX-NL2-003-R1; violations = **0**. `project/state.json`, `project/plan.json` отсутствуют в диффе.
- `docs/work/SESSION_LOG.md` — единственный hunk, только добавление 10 строк в конец (append).
- Коммит-цепочка: `0ef0e97` START → `3d72712` hardening → `4d9832d` schema sync → `ce0f7de` provenance docs → `4a7635b` records → `757eb1e` terminal. Diff `4a7635b..757eb1e` = ровно 3 файла (event 0004 + паспорт-статус + SESSION_LOG) — соответствует заявлению события 0004.

## 2. S003 (технический/научный статус)

- **Негатив (опубликованная фикстура):** `python -m harness.experiment_cli validate experiments/evidence/E0/E0-R1/fixtures/status/s003_tech_with_sci_claim/run` → **exit 3**, `ok:false`, ошибка `0002-run-completed.json: S003: … must not be carried by a RUN_COMPLETED event`. (На base d121119 тот же вызов давал `ok:true`, exit 0 — REVIEWER NL2-001 §1.8; контраст подтверждает закрытие дыры.)
- **Позитив (легитимная verify-цепочка, собственный scaffold):** RUN_STARTED → RUN_COMPLETED (`scientific_outcome: null`) → ANALYSIS_COMPLETED (`SUPPORTED`, `artifact_refs=["artifacts/analysis.json"]`, файл существует) → `ok:true`, CLI **exit 0**.
- **Дополнительные негативы:** SUPPORTED на ANALYSIS_COMPLETED без `artifact_refs` → fail; с несуществующим артефактом → fail; SUPPORTED на RUN_CHECKPOINT → fail.
- **Регрессия легитимных кампаний:** `validate` E1-R1-S001, E1-R2-C001/C002/C003 → `ok=true`, **0 warnings**, exit 0. Все 18 run-каталогов E0-R4 — зелёные (см. §7).

## 3. verify-digests (digest-vs-blob)

| Цель | ok | runs | entries | mismatches | errors |
|---|---|---|---|---|---|
| E1/E1-R1 | true | 4 | **16** | 0 | 0 |
| E1/E1-R2 | true | 3 | **15** | 0 | 0 |
| E0/E0-R4 | true | 18 | **56** | 0 | 0 |
| E0/E0-R3 | true | 19 | 59 | 0 | 0 |
| E0/E0-R2 | true | 18 | 55 | 0 | 0 |
| E0/E0-R1**`/runs`** | true | 18 | 55 | 0 | 0 |

- `--rev d121119add…` на E1-R2 → ok=true, 15/15 (флаг ревизии работает).
- **Graceful fail:** legacy object-манифест фикстуры n007 → error `artifact entry must be an object (array contract)` (не crash, скан продолжается); отсутствующий блоб (n006) → graceful error; ok=false.
- Observation F-4: скан **корня** E0-R1 (поддерево) подбирает fixture-каталоги (n006/n007/s001/s002/s003) → 5 errors, exit 3 при 0 mismatch на реальных прогонах; `runs/`-поддерево чистое.

## 4. emit_run порядок (REPAIR_MAP_F1_R1 §5.1)

- **Фиксированный код (HEAD):** синтетический scaffold через `emit_run` → sha256/size **каждой** записи `artifacts.manifest.json` = фактические байты; **0 stale** (инвариант держится).
- **Пре-фикс код (blob d121119, размещён в scratch той же глубины):** тот же сценарий → **stale ровно у `case_record.json`** — F1-класс воспроизведён: «на пре-фикс версии тест валится» подтверждено.

## 5. Timestamp-правила (work_cli)

- **Скан базы d121119** (все `docs/work/executions/EX-*/events/*.json` через `git show`): ровно **один** hit «≥3 событий с одним штампом»: `EX-NL2-002-R1`, `2026-09-10T11:37:54Z`, события 0002–0004 — **в точности whitelist** (`LEGACY_BATCH_TIMESTAMP_EVENTS`).
- **Whitelist точен:** неизменённая копия EX-NL2-002-R1 → `ok:true`; та же выборка штампов под другим `execution_id` → `ok:false` с `constant copy timestamp` (exemption не переносится).
- **Midnight-placeholder → ERROR (exit 3):** паспорт `started_at_utc` и `timestamp_utc` события; формы `Z` и `+00:00` обе ловятся (`^\d{4}-\d{2}-\d{2}T00:00:00(\.0+)?(?:Z|z|\+00:00)$`).
- Опубликованный `EX-NL2-002-R1` валиден (входит в 14/14, §7).
- **F-1 (см. вердикт):** в `experiment_cli` проверок timestamp НЕТ (grep `timestamp|midnight` — 0 совпадений); полностью валидный run с тремя midnight-штампами проходит `validate` с `ok:true`, 0 ошибок — вопреки формулировкам в PROVENANCE_RECOVERY_R1 §6/§7, `provenance-recovery.v1.json` (`readback.chronology`) и `summary.md`.

## 6. evidence-map.schema.v1.json (F-1/O3)

- Новая схема (Draft 2020-12 + FormatChecker) против трёх published карт: **E1-R1 = 0, E0-R4 = 0, E1-R2 = 0 ошибок**.
- Старый checkpoint-вид (минимальный документ старой формы) против новой схемы → **10 errors** (`kind`, `campaign_id`, `experiment_id`, `execution_id`, … required) — осознанно не валиден.
- Старая схема (blob d121119) против опубликованных карт: **11 / 11 / 9** ошибок (E1-R1 / E0-R4 / E1-R2) — несовместимость подтверждена; формулировка README «11 идентичных ошибок на каждой» неточна для E1-R2 (finding F-3).

## 7. Полный чек-набор

- **unittest:** `python -m unittest discover -s tests -t .` → **Ran 133 tests … OK** (2.5s). Новых тестов **31**: S003 7, O1 5, verify-digests 5, emit_run 2, timestamps 9, evidence-map 3 — соответствуют заявлению.
- **JSON:** tracked `*.json` = **713** (заявлено 710; base d121119 = 707 + 6 новых — finding F-2); unparseable ровно **2** — pinned NEG-фикстуры `n001_empty_passport` (sha256 `e3b0c442…`, 0 байт) и `n002_truncated_json` (sha256 `1de18ae4…`, 80 байт).
- **check-consistency:** exit 0. **workflow_lint:** 0 violations, exit 0.
- **work_cli validate:** **14/14 EX OK** (13 pre-existing + EX-NL2-003-R1).
- **work_cli close EX-NL2-003-R1:** `ok:true`, HANDOFF_READY (не мутирует; git status чист после прогона).
- **Регрессия published runs** (80 run-каталогов E0-R1..R4, E1-R1/R2): **62 green / 18 red**; red — ровно superseded E0-R2, в каждом 2 pre-existing `campaign_id differs` + O1-ошибки на сохранённых 55 stale `storage_location` (17×3 + POS001×4 = 55) — новых красных поверхностей нет.

## 8. Поверхности EX-NL2-003-R1

- `passport.json` + 4 события против `execution-passport.schema.v1.json` / `work-event.schema.v1.json` (Draft 2020-12 + FormatChecker): **0 ошибок**.
- `subject_sha` всех событий = base `d121119…` (40-hex); первое событие WORK_ORDER_STARTED, терминал HANDOFF_COMPLETED последний.
- Per-event timestamps: 13:04:53Z / 13:30:32Z / 13:31:14Z / 13:32:40Z — попарно различны; каждое предшествует своему публикующему коммиту (13:07:10Z / 13:32:58Z / 13:34:34Z +10).

## 9. Self-acceptance

- «ACCEPTED» в пакете — только исторические ссылки (NL2-002 ACCEPTED решением Director) и дисклеймеры («ACCEPTED не выставляется»); паспорт HANDOFF_READY; next action — независимый REVIEWER. Нарушений нет.
