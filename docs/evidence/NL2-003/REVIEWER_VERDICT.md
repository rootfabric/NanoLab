# NL2-003 — REVIEWER VERDICT (независимый review evidence-пакета EX-NL2-003-R1)

**Вердикт: `FIX_REQUIRED`** (исполнительная часть WO выполнена и независимо воспроизведена; пакет требует одного узкого ремонта — публикация заявляет механический контроль, отсутствующий в коде, см. F-1).

- **Subject:** ветка `work/nl2-003-provenance-recovery-r1` @ exact HEAD `757eb1e7889f79379a597b03099de7969f276fbf`; base `d121119add4533c77c40db287c292d0c8e542188` (ancestor подтверждён).
- **Рецензент:** независимый fresh-агент (REVIEWER), без доступа к контексту имплементёра; только Git-факты и собственные прогоны. Review-ветка `review/nl2-003-provenance-recovery-r1`, worktree `C:\NanoLab\review-nl2-003`.
- **Окружение:** Python 3.11.8, jsonschema 4.22.0; прогоны — disposable scratch; published-поверхности не изменялись. Полный журнал: [REVIEWER_VERIFICATION_LOG.md](REVIEWER_VERIFICATION_LOG.md).
- **Claim ceiling:** не затрагивается — `C0_SOFTWARE_ONLY`, campaign-level scientific_outcome = `NOT_EVALUATED`; настоящий вердикт не является accept'ом NL2-003 и не повышает claim.

## 1. Резюме по bounded scope

| # | Пункт | Результат |
|---|---|---|
| 1 | Scope diff `d121119..757eb1e` = allowed_paths; state/plan не тронуты | **PASS** — 20 файлов, 0 violations; SESSION_LOG строго append; научные поверхности нетронуты (единственное изменение в `experiments/evidence/**` — разрешённый `e0_runner.py`) |
| 2a | S003: негатив (gap-фикстура) + позитив (легитимная verify-цепочка) + регрессия легитимных кампаний | **PASS** — фикстура `s003_tech_with_sci_claim` → exit 3 с явной S003-ошибкой (на base была `ok:true`); scaffold terminal(null)→ANALYSIS_COMPLETED(SUPPORTED+артефакт) → exit 0; без/с битым `artifact_refs` → fail; E1-R1/R2 validate `ok=true`, 0 warnings; E0-R4 18/18 зелёные |
| 2b | verify-digests: E1-R1 16/16, E1-R2 15/15, E0-R4 56/56 → 0 mismatch; graceful fail на legacy | **PASS** — все три цели `ok=true`, exit 0; бонус R1/R2/R3 (55/55/59) 0 mismatch; legacy object-манифест (n007) и отсутствующий блоб (n006) — graceful errors, fail-closed; `--rev` работает |
| 2c | emit_run фикс: инвариант на фикс-версии; пре-фикс валится | **PASS** — HEAD: 0 stale digest'ов (включая `case_record.json`); пре-фикс blob d121119: stale ровно у `case_record.json` — F1-класс воспроизведён |
| 2d | Timestamp-правила: midnight → ERROR; whitelist точен | **PASS** — midnight (паспорт+событие, `Z`/`+00:00`) → exit 3; скан базы d121119: ровно один ≥3-хит = EX-NL2-002-R1 0002–0004 @ 11:37:54Z == whitelist; под другим `execution_id` exemption не действует; 1–2 совпадающих штампа легальны |
| 2e | evidence-map.schema: 3 published карты → 0 ошибок; старый checkpoint-вид не валиден | **PASS** — E1-R1/E0-R4/E1-R2 = 0/0/0 ошибок (Draft 2020-12 + FormatChecker); старый checkpoint-вид → 10 errors; старая схема против карт → 11/11/9 (F-3 о точности формулировки) |
| 3 | unittest 133/133; качество новых 31 | **PASS** — Ran 133, OK; 31 = 7+5+5+2+9+3; тесты проверяют реальные режимы отказа с привязкой к тексту ошибок, опубликованные фикстуры-регрессии, позитив/негатив на каждую дыру; «тестов на Integer» нет |
| 4 | Дока PROVENANCE_RECOVERY_R1: цепочка, stop/resume, readback vs hard rules | **PASS с замечанием** — run ID не переиспользуется (§2), RESUMED = конвенция на RUN_CHECKPOINT без расширения схем (§3), reuse только с digest+provenance (§5.2), readback из блобов (§5.1), дедупликация (§4) — согласовано с hard rules и machine-readable конфигом. Но §6/§7 содержат утверждение о несуществующем контроле (F-1) |
| 5 | События/паспорт/summary EX-NL2-003-R1 | **PASS** — passport+4 события: 0 schema-ошибок; терминал HANDOFF_COMPLETED последний; per-event timestamps попарно различны (13:04:53/13:30:32/13:31:14/13:32:40Z) и предшествуют публикующим коммитам; `subject_sha` 40-hex; `work_cli close` → ok:true |
| 6 | Не сломано ли принятое: полный чек-набор | **PASS** — consistency exit 0; lint 0; work_cli 14/14 EX OK; JSON unparseable ровно 2 pinned NEG (sha256 = CI-пинам); регрессия published runs: 62 green / 18 red — ровно документированная superseded E0-R2 (2 pre-existing stale campaign_id + O1 на сохранённых 55 stale `storage_location`); новых красных поверхностей нет |
| 7 | Self-acceptance | **PASS** — ACCEPTED только как исторические ссылки/дисклеймеры; NOT_EVALUATED; handoff → независимый REVIEWER → VERIFIER → Director; merge — Human Gate |

Каждая заявленно закрытая дыра (S003, digest-vs-blob, emit_run, O1, O2/F3, F-1/O3) воспроизведена рецензентом негативом и позитивом самостоятельно; ни одно закрытие не принято на веру.

## 2. Findings

### F-1 (MODERATE — единственная причина FIX_REQUIRED): документация и конфиг заявляют механический контроль «midnight в experiment_cli», которого не существует в коде

Четыре опубликованные поверхности утверждают, что placeholder-проверка применяется к experiment-событиям в `experiment_cli`:

- `docs/research/PROVENANCE_RECOVERY_R1.md` §6: «Для experiment-событий применяется midnight-плейсхолд-проверка того же класса (`experiment_cli`)» (и далее: «правило «≥3 копий» туда сознательно не перенесено» — из чего следует, что midnight-правило перенесено);
- `docs/research/PROVENANCE_RECOVERY_R1.md` §7, таблица: «midnight/непарсируемый/копия-штампы | `work_cli validate` **(+ midnight в `experiment_cli`)**»;
- `config/infra/provenance-recovery.v1.json`, `readback.chronology`: «placeholder timestamps rejected by **work_cli/experiment_cli**»;
- `docs/work/executions/EX-NL2-003-R1/summary.md`: «midnight-правило **продублировано в `experiment_cli`**».

Факт: в `scripts/harness/experiment_cli.py` нет ни одной проверки timestamp (grep `timestamp|midnight` — 0 совпадений). Воспроизведено: полностью валидный run-каталог, все три события которого несут `timestamp_utc = 2026-09-09T00:00:00Z`, проходит `experiment_cli validate` с `ok:true`, 0 errors, 0 timestamp-ошибок (единственный механический слой для experiment-событий — `experiment-event.schema.v1.json` required + `format: date-time`, который midnight-passes по определению). WO-NL2-003 п.4 мандировал placeholder-правила только для `work_cli` — там всё реализовано и подтверждено; но канонический контракт-документ и machine-readable конфиг (продукт этого WO) декларируют enforcement, которого нет — тот самый класс «заявлено ≠ enforced» (S003: «структура без семантики не должна приниматься тихо»), ради которого существовал этот Work Order.

**Требуется (один ремонт-коммит, выбор одного пути):** (a) реализовать midnight-проверку в `experiment_cli` (проверка ~5 строк, повторяет `MIDNIGHT_PLACEHOLDER` из `work_cli`; правило «≥3 копий» туда не переносить — как и заявлено) + unittest позитив/негатив; либо (b) скорректировать четыре формулировки до фактического состояния («midnight-правило в R1 реализовано в work_cli; экспериментальные события пока гейтятся только схемой — автоматизация кандидат»). Путь (a) предпочтителен: правило уже объявлено контрактом, стоимость минимальна. Попутно в том же коммите — F-2/F-3.

### F-2 (MINOR): числовая неточность в validation-записи

Event 0003 и `summary.md` утверждают «710 tracked *.json». Фактически на `757eb1e` tracked JSON — **713** (base `d121119` = 707; branch добавил 6: `provenance-recovery.v1.json` + 5 файлов EX-NL2-003-R1). Существенное утверждение верно: unparseable ровно 2, оба — pinned NEG-фикстуры с sha256, совпадающими с CI-пинами (`e3b0c442…`, `1de18ae4…`). Гейт не затронут, но durable-запись содержит неверное число — исправить erratum'ом в ремонт-коммите.

### F-3 (MINOR): «11 идентичных ошибок на каждой кампанской карте» неточно

`config/control/harness/README.md` (секция sync) и наследуемая формулировка F-1/O3: против старой схемы (blob `d121119`) опубликованные карты дают **11 / 11 / 9** ошибок (E1-R1 / E0-R4 / E1-R2), т.е. число и состав не идентичны на каждой карте. Существенное утверждение подтверждено (все три карты старой схемой отвергаются, новой — валидны с 0 ошибок). Поправить формулировку при случае; не блокирует.

### F-4 (INFO, observation): `verify-digests` на корне кампании E0-R1 — exit 3 из-за фикстур

Скан поддерева кампании подбирает fixture-каталоги (n006/n007/s001/s002/s003) и даёт 5 graceful errors (exit 3) при 0 mismatch на всех реальных прогонах; `runs/`-поддерево — `ok=true`, 55/55. Заявление «E0-R1 55/55 — 0 mismatch» точное (entries/mismatches), поведение fail-closed корректно, но документированный сценарий «campaign-dir» не оговаривает, что negative-фикстуры под корнем делают полный прогон кампании красным. Рекомендация: оговорка в `scripts/harness/README.md` (или точечный прогон по `runs/`), без изменения кода.

### F-5 (INFO, observation): модификация существующего тест-файла против буквы WO

`tests/test_work_cli_corrections.py` — изменён (не создан), тогда как allowed_paths WO сформулирован «tests/** (новые unittest-файлы)» (паспорт допускает `tests/**` без ограничения). Изменение вынужденное: константный штамп генератора фикстур стал бы ошибкой нового валидатора; семантика проверяемых правил не изменилась (проверено по diff — только per-event штампы + комментарий); задокументировано в event 0003, но в branch-passport «Отклонения от allowed_paths: Нет» при букве WO-формулировки неточно. Принять к сведению; в ремонт не входит.

## 3. Self-acceptance

Нарушений нет (см. §1 п.7). Настоящий вердикт — единственный review-вердикт в пакете NL2-003; ACCEPTED/статус checkpoint не выставляется.

## 4. Итог

Исполнительная часть NL2-003 подтверждена независимо и полностью: все шесть накопленных дыр закрыты механически и воспроизводятся негативом/позитивом, регрессия чиста (62/18 документированных), документ provenance/recovery согласован с hard rules, поверхности EX-NL2-003-R1 валидны, 133/133 теста. Вердикт **`FIX_REQUIRED`** — исключительно из-за **F-1**: контрактная поверхность WO (дока §6/§7 + machine-readable конфиг + summary) заявляет midnight-контроль в `experiment_cli`, которого в коде нет. Научные исходы не затронуты; campaign-level `NOT_EVALUATED`.

**Next action (одно):** implementer — repair-коммит по F-1 (реализация midnight-проверки в `experiment_cli` с тестами, либо правка четырёх формулировок) + erratum F-2/F-3; после него независимый VERIFIER; merge — Human Gate.

*Review выполнен независимо (fresh-сессия, worktree `review/nl2-003-provenance-recovery-r1` @ `757eb1e`); прогоны и скрипты — disposable scratch; published-поверхности не изменялись; старые события не редактировались.*
