# Provenance & Recovery — R1

**Revision:** `PROVENANCE-RECOVERY-R1`
**Work Order:** NL2-003 (EX-NL2-003-R1)
**Canonical owner:** `main`
**Machine-readable проекция:** [`config/infra/provenance-recovery.v1.json`](../../config/infra/provenance-recovery.v1.json)

Этот документ фиксирует контракт-плоскость провенанса и восстановления для вычислительных кампаний NanoLab. Он не вводит новых типов событий и не меняет схемы v1: все правила выражаются конвенциями поверх существующих контрактов (`EXPERIMENT_HARNESS_RU.md`, `config/control/harness/*.schema.v1.json`) и механическими проверками `scripts/harness/`. AiiDA/HPC-интеграция — отдельный будущий WO (§8).

## 1. Provenance-цепочка

Научный вывод допустим только тогда, когда каждое звено цепочки адресуемо и верифицируемо. Разрыв любого звена ограничивает claim рядом с выводом (`SCIENTIFIC_METHOD.md`, «условия запрета сильного вывода»).

```text
subject (freeze-коммит)
  └─ seeds (фактические, из логов engine)
       └─ inputs (байты из blob'ов subject, digest-верифицированы)
            └─ binaries (engine/tool: SHA-256 + размер + флаги сборки)
                 └─ runs (уникальный run_id, манифесты + события)
                      └─ analysis (observable/statistics, отдельная поверхность)
                           └─ evidence-map (review-unit кампании)
```

| Звено | Где фиксируется | Чем верифицируется |
|---|---|---|
| subject | `manifest.json.subject_sha` (40-hex freeze-коммит), события, артефакты | `experiment_cli validate`; freeze-коммит предшествует прогонам (git-хронология) |
| seeds | фактические значения из логов engine (`log.dat`), `resource_usage.seed` / `seed_policy` | попарная distinctness там, где требует протокол; коллизия → техническая классификация |
| inputs | `manifest.json.inputs[]` (sha256/size/blob-ref/modifications) | materialize из `git cat-file blob` + digest-проверка перед прогоном; «working copy не доверяется» (§6) |
| binaries | `manifest.json.model` / `environment` (binary_sha256, size, build flags, upstream commit) | SHA-256/размер/флаги перед каждым прогоном; пересборка = новые SHA-256 в новом subject |
| runs | `runs/<run-id>/` — массив-манифесты, события (терминал перед анализом), `artifacts.manifest.json` | `experiment_cli validate` (структура), `verify-digests` (sha256/size vs git-блобы), O1-линт storage_location |
| analysis | `ANALYSIS_COMPLETED` с научным исходом; статистика кампании | S003-правило: SUPPORTED только на analysis-поверхности с verification-surface (артефакты анализа существуют) |
| evidence-map | `experiments/evidence/<exp>/<campaign>/evidence-map.json` | `evidence-map.schema.v1.json` (campaign-конвенция, F-1/O3 sync) |

Правило неизменности: опубликованные run-поверхности не редактируются. Исправления — erratum/новым событием/новой ревизией (прецедент F1-ремонта NL2-001: superseded-манифесты byte-equal + пересчитанные канонические). Инструменты кампаний версионируются тем же механизмом: blob исторического subject сохраняется в git-истории; новая ревизия инструмента входит во freeze будущего subject (прецедент: emit_run-фикс NL2-003 в `e0_runner.py`).

## 2. Остановка (stop)

Техническая остановка/прерывание run фиксируется терминальным событием (`RUN_ABORTED`, `RUN_FAILED_TECHNICAL`, `RUN_BLOCKED_ENVIRONMENT`) с причиной, consumed resources и ссылками на частичные артефакты. Прерванный run остаётся в Git как есть — негативный/частичный результат долговечен (`AGENTS.md` hard rules). Run ID после остановки **никогда не переиспользуется** — ни для повтора, ни «дозапуска», ни ремонта.

Смена executor/машины/бинаря между попытками — новая попытка с новым run ID и recording'ом смещения в provenance (§1), а не «продолжение» старого.

## 3. Возобновление (resume)

Resume выполняется **новым run с новым run_id**. Связь с прерванным run фиксируется RESUMED-маркером — конвенция на существующем типе `RUN_CHECKPOINT` (схемы v1 не расширяются):

```text
runs/<new-run-id>/events/000N-run-checkpoint.json
  event_type: "RUN_CHECKPOINT"
  summary:    "RESUMED: <причина/фаза> (supersedes_run_id: <interrupted-run-id>, reuse: <что переиспользуется>)"
  resource_usage: {
    "resumed_marker": "RESUMED",
    "supersedes_run_id": "<interrupted-run-id>",
    "reuse_scope": "<inputs|binaries|none>",
    ...
  }
```

Требования:
- resume-точка — граница checkpoint'а (после preparation/equilibration/checkpoint-события), не произвольная середина фазы, если протокол не определяет иначе;
- `reuse_scope` переиспользуемых артефактов обязан ссылаться на дайджесты исходного run (reuse без digest+provenance запрещён);
- прерванный run обязан иметь терминальное событие ДО публикации resume-run (терминал не «задним числом», новые события не редактируются);
- механический контроль «RESUMED» на данный момент — конвенция review (grep-поверхность); автоматизация — будущий кандидат.

## 4. Дедупликация

Идентичная frozen поверхность не исполняется повторно: если существует опубликованный run с теми же звеньями (subject_sha, protocol_revision, input digests, binary, seed), evidence-map кампании ссылается на существующий run (прецедент: `E1-R1-S001` в confirmatory set `E1-R2` — `counts_toward_evidence: true` + cross-check, повтор не выполнялся).

Таблица решений:

| Ситуация | Действие |
|---|---|
| Все звенья идентичны (включая seed) | Ссылка на существующий run; нового прогона нет |
| Отличие только в seed (протокол требует независимости) | Новый run ID, новый прогон |
| Отличие в inputs/binaries/protocol | Новый run ID + новый subject/протокол-ревизия (superseding) |
| Технический сбой | Новый run ID, причина в терминале; `--retry-of` только с новым id (прецедент `E0-R3-S003-RETRY1`) |

## 5. Readback-требования (чтение опубликованных данных)

1. **Читать из git-блобов, не из рабочей копии** (`git cat-file blob <rev>:<path>`): autocrlf на Windows даёт ложные digest-mismatch (урок F-3, VERIFIER NL2-002; повторение — в VERIFIER NL2-001 §3).
2. Каждое использование raw-артефакта вне исходного run-каталога — по `sha256`/`size_bytes` из `artifacts.manifest.json` (hard rule: `RAW ARTIFACT REUSE REQUIRES DIGEST + PROVENANCE`).
3. Механическая проверка: `PYTHONPATH=scripts python3 -m harness.experiment_cli verify-digests <campaign-or-run-dir> [--rev HEAD]` — сверяет каждую запись манифеста с блобом; exit 0 только при 0 mismatch (пригодно как CI-чек). Прогон R1: E1-R1 16/16, E1-R2 15/15, E0-R4 56/56, E0-R1 55/55, E0-R3 59/59, E0-R2 55/55 — 0 mismatch.
4. Хронология авторитетно восстанавливается по commit-датам + машинным `timestamp_utc`; placeholder-штампы (O2/F3-класс) отвергаются валидатором (§7).

## 6. Timestamps: машинные штампы обязательны

Каждое событие несёт собственный машинный `timestamp_utc` (ISO-8601, UTC). Отклонения, обнаруженные в NL2-001/NL2-002 (F3: round-number `frozen_at_utc`; O2: placeholder в repair-событии; F-1 NL2-002: batch-штампы трёх событий), объединены в класс «placeholder timestamps» и закрыты в `work_cli` (NL2-003):

- midnight-placeholder `T00:00:00Z` — ошибка (однозначный маркер подстановки даты вместо времени);
- непарсируемый/отсутствующий штамп — ошибка (хронологическая сверка review без него невозможна);
- константный copy-штамп на ≥3 событиях одного execution — ошибка; прецедент EX-NL2-002-R1 (0002–0004, один штамп batch-записи) grandfathered точным whitelist'ом `(execution_id, event_id)` — опубликованные события неизменяемы, новые обязаны штамповаться по-событийно;
- 1–2 совпадающих штампа допустимы (легитимные sub-second последовательности, прецедент E0-R4: терминал и анализ в одну секунду); «одинаковые минуты» вне scope.

**Почему ошибка, а не предупреждение.** (1) F3/O2 показали: placeholder-штампы реально возникают и вводят восстановление хронологии в заблуждение — reviewer вынужден опускаться до commit-дат, то есть контракт поля не работает. (2) Опубликованный позитив-контроль POS001 использует сигнатуру «ok:true, **0 warnings**» — предупреждения в этой системе воспринимаются как шум, который гейтится ничем. (3) Стоимость исправления минимальна (перештамповать при создании события), а цена молчаливого пропуска — подрыв единственного независимого от памяти агента источника хронологии. Fail-closed — конвенция всех валидаторов harness'а (урок S003: «структура без семантики» не должна приниматься тихо).

Для experiment-событий применяется midnight-плейсхолд-проверка того же класса (`experiment_cli`); правило «≥3 копий» туда сознательно не перенесено: у быстрых прогонов терминал/анализ легитимно совпадают до секунды, а 3-событийные run'ы дали бы ложные срабатывания.

## 7. Сводка механических контролей (после NL2-003)

| Контроль | Инструмент | Класс дыры |
|---|---|---|
| `verify-digests` (sha256/size vs git-блобы) | `experiment_cli verify-digests` | F1/digest-vs-blob |
| SUPPORTED только на analysis-поверхности с verification-surface | `experiment_cli validate` | S003 |
| storage_location содержит сегменты campaign_id/run_id | `experiment_cli validate` | O1 |
| midnight/непарсируемый/копия-штампы | `work_cli validate` (+ midnight в `experiment_cli`) | O2/F3 |
| 40-hex subject_sha новых событий | `work_cli validate` (MINOR-2, подтверждён) | legacy-сокращения |
| campaign evidence-map схема | `evidence-map.schema.v1.json` | F-1/O3 |
| emit_run: манифест после финализации case_record | `e0_runner.py` + unittest | F1-корень |

## 8. Вне scope (будущие WO)

- AiiDA/HPC: перенос цепочки §1 на workflow-engine с автоматическим provenance-graph — отдельный bounded WO после INFRA2-линии; настоящий документ объявляет контракт-плоскость, которой такой движок должен удовлетворять (run ID не переиспользуется, RESUMED-конвенция, digest+provenance на reuse, readback из блобов).
- Автоматический RESUMED-чек в `experiment_cli`, graceful crash-пути валидаторов (N001/N002/N007), engine-coupled E0-кейсы, per-event штампы задним числом для batch-прецедентов (запрещено — события неизменяемы).
