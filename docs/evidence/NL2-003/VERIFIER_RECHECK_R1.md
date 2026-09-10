# NL2-003 — VERIFIER RECHECK R1 (аддендум: независимая верификация repair R1 исполнением)

**Вердикт по ремонту: `PASS`** — repair R1 закрывает `FIX_REQUIRED` ([REVIEWER_VERDICT](https://github.com/rootfabric/NanoLab/blob/review/nl2-003-provenance-recovery-r1/docs/evidence/NL2-003/REVIEWER_VERDICT.md) @ `b4e6758`) корректно и проверяемо: F-1 закрыт реализацией (путь (a)), errata F-2/F-3/F-4 подтверждены фактами, F-5 задокументирован. Научные исходы не затронуты; campaign-level `NOT_EVALUATED`; claim ceiling `C0_SOFTWARE_ONLY`. Путь к Director checkpoint открыт; merge — Human Gate.

- **Ремонтируемый subject:** `757eb1e7889f79379a597b03099de7969f276fbf` (проверенный reviewer'ом HEAD; base `d121119`).
- **Проверенный repaired HEAD:** `57b986dce7e5fd2ebe11a849eccda59309747157` (ветка `work/nl2-003-provenance-recovery-r1`; ремонтные коммиты `31997ac` — реализация, `57b986d` — repair-событие 0005 + SESSION_LOG).
- **Метод:** verification ≠ review — собственное воспроизведение на отдельном worktree `verify/nl2-003-provenance-recovery-r1`; все пробы — disposable scratch / read-only CLI; published-поверхности не изменялись. Окружение: Python 3.11.8, jsonschema 4.22.0, git 2.53.0.windows.1.

## 1. F-1 (MODERATE, причина FIX_REQUIRED) — закрыт реализацией, воспроизведено независимо

`scripts/harness/experiment_cli.py`: введён `MIDNIGHT_PLACEHOLDER` (тот же класс регулярок, что в `work_cli`: `T00:00:00(.0+)?(Z|z|+00:00)`) + error в `inspect_run` на каждый placeholder-штамп; правило «≥3 копий» не перенесено (как и заявлено). Мои собственные пробы (не через unittest):

| Проба | Результат |
|---|---|
| Базовая: валидный run-каталог (копия E0-R4-U001) с машинными штампами | `ok:true`, 0 ошибок |
| Все 3 события `2026-09-09T00:00:00Z` | **exit 3**, 3 ошибки «…is a midnight placeholder…» |
| Все 3 события `2026-09-09T00:00:00+00:00` (offset-форма) | **exit 3**, 3 midnight-ошибки |
| Published `E0-R4` (18 run-каталогов) | 18/18 `ok:true`, **0 midnight-упоминаний** |
| Published `E1-R2` (3 run-каталога) | 3/3 `ok:true`, 0 midnight-упоминаний |
| Gap-фикстура `E0-R1/fixtures/status/s003_tech_with_sci_claim/run` | **exit 3**: 2 midnight-ошибки (0001/0002) **+ S003-ошибка** разделения статусов — комбинация нарушений fail-closed |

Четыре поверхности заявления F-1 теперь соответствуют коду: `PROVENANCE_RECOVERY_R1.md` §6/§7 (дополнены честной пометкой, что контроль введён repair-коммитом R1 — первоначальная публикация декларировала его до реализации); `config/infra/provenance-recovery.v1.json` **не менялся** (0 строк в диффе) — его прежняя формулировка «rejected by work_cli/experiment_cli» стала истинной фактом реализации; `summary.md` обновлён. Стилистически: unittest-класс `ExperimentCliMidnightPlaceholderTests` (5 тестов) покрывает те же сценарии.

## 2. Errata — сверены с фактами

- **F-2 (MINOR) — подтверждено:** tracked `*.json`: base `d121119` = **707**, `757eb1e` = **713** (57b986d = 714: +1 repair-событие 0005). Мой собственный скан: unparseable **ровно 2** — pinned NEG-фикстуры `n001_empty_passport` (0 B, blob sha256 `e3b0c442…` = sha256 пустого файла) и `n002_truncated_json` (80 B, blob sha256 `1de18ae447d83f621e98f64ef928858e9c0b1456144f10b4870bfcea8a3c4a85`) — **совпадают с CI-пинами** `hosted-ci.yml`. Существенное утверждение неизменно; erratum корректен (события не редактировались — исправление в summary + событие 0005).
- **F-3 (MINOR) — подтверждено:** старая схема (blob `d121119:config/control/harness/evidence-map.schema.v1.json`) против опубликованных карт: **E1-R1 = 11, E0-R4 = 11, E1-R2 = 9 ошибок** (моя репродукция, Draft 2020-12 + FormatChecker); новая схема @ `57b986d` — **0/0/0**. Формулировка исправлена в `config/control/harness/README.md` и `description` схемы (правка description — текстовая, контракт `required`/`properties` не тронут — проверено по диффу).
- **F-4 (INFO) — подтверждено воспроизведением:** `verify-digests experiments/evidence/E0/E0-R1` (корень кампании) → **exit 3, ok=false**: 5 graceful errors на designed-negative фикстурах (n006/n007/s001/s002/s003), при этом **0 mismatches на 55 реальных записях** (18 runs + 5 fixture-каталогов просканированы). Оговорка добавлена в `scripts/harness/README.md` дословно соответствует поведению; для таких кампаний — сканировать `runs/` (проверено: `E0-R1/runs` → ok).
- **F-5 (INFO)** — задокументирован в branch-passport как вынужденное documented deviation (изменение существующего `tests/test_work_cli_corrections.py`); по диффу ремонта файл не трогался — отклонение относится к пре-ремонтному состоянию, зафиксировано корректно.

## 3. Полный чек-набор после ремонта — всё зелёное

| Чек | Результат |
|---|---|
| `python -m unittest discover -s tests -t .` | **Ran 138 tests — OK** (133 + 5 новых midnight) |
| `work_cli validate` по всем `docs/work/executions/EX-*` | **14/14 ok** (включая EX-NL2-003-R1 с новым 0005) |
| `experiment_cli verify-digests` | **E0-R1/runs 55, E0-R2/runs 55, E0-R3/runs 59, E0-R4 56** — 0 mismatch; бонус: E1-R1 16, E1-R2 15 — 0 mismatch, 0 errors |
| JSON-скан (собственный скрипт) | 714 tracked, unparseable ровно 2 pinned NEG (= CI-пинам) |
| `check-consistency` | ok, exit 0 |
| Регрессия published | E0-R4 18/18 ok, E1-R2 3/3 ok, 0 midnight; новых красных поверхностей нет |

## 4. Scope ремонтного диффа `757eb1e..57b986d` — чист

Ровно 10 файлов, все — ремонтные поверхности: `scripts/harness/experiment_cli.py` (+12: midnight), `tests/test_nl2_003_hardening.py` (+60: 5 тестов), `scripts/harness/README.md` (F-4 оговорка), `config/control/harness/README.md` + `evidence-map.schema.v1.json` (F-3 формулировки), `docs/research/PROVENANCE_RECOVERY_R1.md` (F-1 пометки SS6/SS7), `summary.md` (erratum F-2 + раздел Repair R1), `branch-passport.md` (F-5 deviation), `docs/work/SESSION_LOG.md` (строго append), **A** `events/0005-repair.json`. Вне поверхностей — 0 файлов; `project/**`, `config/infra/**`, `experiments/evidence/**` не тронуты.

## 5. Repair-событие 0005 — валидно, corrections-класс соблюдён

- `0005-repair.json` против `work-event.schema.v1.json` (Draft 2020-12 + FormatChecker): **0 ошибок**; `event_id` = имени файла; все 5 событий EX — 0 schema-ошибок.
- Позиция: **post-terminal corrections-class** — следует за терминальным `0004-handoff-completed` по прецеденту `EX-NL1-002-R1/0006-repair-completed` («corrections — новым event», старые события не редактировались); `work_cli validate` принимает (внутри 14/14). `timestamp_utc = 2026-09-10T14:07:01Z` — машинный (не placeholder; новый валидатор сам пропустил бы только такой).
- `subject_sha = d121119…` — **единообразен со всеми событиями EX** (0001–0004 несут тот же subject = `base_sha` паспорта); ремонтируемый subject `757eb1e` назван в summary/`evidence_refs` события. Конвенция EX соблюдена (отличается от прецедента NL2-001, где repair-событие ссылалось на ремонтируемый subject — здесь uniform-конвенция EX, не дефект).
- SESSION_LOG — строго append (+8 строк), история не переписывалась; run ID не переиспользованы; новых экспериментальных прогонов нет.

## 6. Self-acceptance

Нарушений нет: ACCEPTED не выставляется; приёмка NL2-003 — VERIFIER → Director; merge — Human Gate. Настоящий аддендум — верификация ремонта, не accept WO; campaign-level scientific_outcome остаётся `NOT_EVALUATED`.

## 7. Итог

| Finding REVIEWER | Статус после ремонта |
|---|---|
| F-1 (MODERATE) | **Закрыт реализацией** (путь (a): midnight в `experiment_cli` + 5 тестов; все 4 поверхности заявления согласованы с кодом) |
| F-2 (MINOR) | **Закрыт** erratum'ом (713 @ 757eb1e — верифицировано; 2 unparseable pinned NEG = CI-пинам) |
| F-3 (MINOR) | **Закрыт** (11/11/9 — верифицировано против blob d121119; формулировки исправлены) |
| F-4 (INFO) | **Закрыт** оговоркой в README; поведение воспроизведено |
| F-5 (INFO) | Принято: documented deviation в branch-passport |
| Замечание VERIFIER | Субъект-ссылка: `0005.subject_sha` = база EX (uniform с 0001–0004), ремонтируемый subject — в тексте события; не дефект, зафиксировано для прецедентной базы |

**Next action (одно):** Director checkpoint по NL2-003; merge в `main` — Human Gate.

*Recheck выполнен независимо (fresh-сессия, worktree `verify/nl2-003-provenance-recovery-r1` @ `57b986d`; пробы и скрипты — disposable scratch; published-поверхности не изменялись; старые события не редактировались).*
