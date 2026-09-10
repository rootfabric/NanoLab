# Director Acceptance — CTRL-LINTSCHEMA «lint fail-closed hardening + schema sync»

Дата решения: 2026-09-10. Роль: DIRECTOR (главный агент INFRA-линии миссии; явная авторизация владельца на Director-приёмку и merge в `main` получена в сессии).

**Статус WO:** контрольный, пакетный (назначен Director-решением INFRA1-002 блокиратором INFRA2-001); **capability-пунктом не является** — capability-флаги этой приёмкой не меняются.

## Решение

```text
WO CTRL-LINTSCHEMA / EX-CTRL-LINTSCHEMA-R1 = ACCEPTED (контрольный WO)
Блокиратор старта INFRA2-001 (из DIRECTOR_ACCEPTANCE_R1 INFRA1-002) = СНЯТ
INFRA2-001 = READY (старт разрешён; предварительные условия старта — см. «Следующее действие»)
VALIDATION_GATES_R1 (doc + config) = остаётся ACCEPTED; содержимое актуализировано данным WO в его границах
capabilities = БЕЗ ИЗМЕНЕНИЙ (hosted_ci = true — флип уже исполнен PR #29 по post-merge live-evidence;
             self_hosted_cpu = false — до фактического создания защищённого runner'а в INFRA2-001)
claim = C0_SOFTWARE_ONLY
```

## Основание

1. **Реализация**: `EX-CTRL-LINTSCHEMA-R1` — branch `control/lint-schema-sync-r1`, substantive subject `7a631d6` (tip `1d1a792` — records-only), base `51a479c` = canonical `main`. Поставлено ровно в границах пакета, назначенного INFRA1-002:
   - **MINOR-4 → fail-closed по-настоящему**: TAB в ведущем whitespace сырой строки → `WORKFLOW_UNPARSEABLE`; dead code (срез `stripped_comment[:indent]` из ведущих пробелов, не мог содержать TAB) устранён; обход, воспроизведённый ревьюером на base (top-level TAB-ключ → silent pass, exit 0), на subject блокируется (8/8 TAB-проб → ожидаемый FAIL; TAB внутри скаляра-значения корректно остаётся OK).
   - **NOTE-5 → fail-closed формы `jobs:`**: не-mapping формы (null/sequence/scalar, включая benign-содержимое) → `WORKFLOW_JOBS_UNSUPPORTED_FORM`/`WORKFLOW_JOBS_BLOCK_MISSING`; job-правила NC-1/NC-6/pinning больше не обходятся никакой формой `jobs:`; пустой `runs-on: []` → `NC1_RUNS_ON_MISSING`.
   - **Schema-sync** (третий→закрытый прецедент «схема отстаёт от фактов»): `work-event.schema.v1.json` — enum `event_type` == `ALLOWED_EVENTS` валидатора (12 типов, вкл. `REVIEW_CORRECTIONS`), `subject_sha` = 40-hex; `execution-passport.schema.v1.json` — `checkpoint` = `^(NL[0-8]|INFRA[0-7])$`, `base_sha` = 40-hex; легаси-расхождение floor/ceiling (4 события `9cc83e8`) задокументировано в `config/control/harness/README.md` точно (пары, provenance, иерархия «схема — потолок / валидатор — floor», запрет переиспользования); `config/infra/validation-gates.v1.json` синхронизирован с кодом.
   - **Тесты**: 59 → 102 (обязательные негативы TAB обоих размещений, форм `jobs:`, fail-closed parser'а); документация `docs/infra/VALIDATION_GATES_R1.md` и `config/control/harness/README.md` обновлены.
2. **Независимый вердикт**: REVIEWER R1 — **PASS** (`review/ctrl-lintschema-r1` @ `acbdff1`, FRESH REVIEWER, без доступа к контексту имплементёра). Собственная матрица ревьюера: 44 негатива + 7 позитивов — все ожидаемые исходы, включая независимое воспроизведение dead code на base-бинарнике и блокировку на subject. Самохостед-лейблы/secrets/платный compute — NONE; научный трек не затронут. Вердикт влит в эту ветку merge-коммитом `ccbfba2`.
3. **Локальная репродукция всех 5 чеков hosted-ci**: на промежуточном merge-HEAD `ccbfba2` (subject + verdict) — JSON 115/115, check-consistency ok, work events 11/11 `EX-*`, lint 0 violations, unittest 102 OK; **на финальном merge-HEAD `71b2f8e` (после sync свежего `main`, Check 1 — с учётом нового пина NEG-фикстур из `90bb4c1`)** — Check 1: 685 tracked JSON, ровно 2 pinned NEG-фикстуры sha256-совпадают, 0 failures; Check 2: `ok=true`, 0 errors/warnings; Check 3: **12/12** `EX-*` OK (добавился `EX-NL2-001-R1` из дрейфа); Check 4: 1 workflow, **0 violations**; Check 5: **Ran 102, OK**. Live-подтверждение — TR-PR/TR-PUSH-MAIN прогоны этого PR (см. SESSION_LOG).
4. **Границы ролей соблюдены**: имплементёром не выставлено ни `ACCEPTED`, ни terminal-статусов приёмки; на subject паспорт `IN_PROGRESS` при единственном START-событии (schema-валидно, входит в 11/11); state-файлы не тронуты (подтверждено blob-сравнением scope-дельты: 10 файлов ревью — все в `allowed_paths` паспорта, `project/`, `experiments/`, чужие `EX-*` — пусто).
5. **Периметр checkpoint-ветки (осознанный, по миссии)**: ветка `control/ctrl-lintschema-director-checkpoint-r1` = subject `7a631d6` + review-вердикт; **implementation-records** (`1d1a792`: events 0002–0004, `summary.md`, terminal-статус паспорта — только records самого execution, 0 строк кода) остаются на ветке `control/lint-schema-sync-r1` и этим merge в `main` не переносятся. На substance-приёмку не влияет (ревью выполнено на exact subject `7a631d6`; все проверки на merge-HEAD зелёные); при необходимости переноса records — отдельная records-only ревизия, не этот PR.
6. **Base drift**: на момент dispatch отсутствовал (origin/main = `51a479c` = base, merge-base подтверждён); в ходе подготовки checkpoint-ветки origin/main продвинулся к `0176098` (PR #30 — science-track checkpoint NL2-001 + CI-фикс `90bb4c1` пина двух NEG-фикстур в Check 1). Свежий `main` влит merge-коммитом `71b2f8e` (конфликт только `docs/work/SESSION_LOG.md` — два аппенда, разрешён аддитивно); дрейф science-поверхности (E0 evidence, `project/state.json`, `WORK_QUEUE.md`, Check 1 workflow) INFRA-поверхность этого PR не пересекает; все 5 чеков перепроверены на финальном merge-HEAD (п. 3).

## Решения по findings

| Finding | Решение Director'а |
|---|---|
| **F1 MINOR** (пре-существующий): паспорта repair-исполнений `EX-NL0-002-R1-REPAIR1`/`EX-NL1-002-R1-REPAIR1` несут `repair_of`/`verdict_repaired` вне passport-схемы (`additionalProperties: false`) — schema-невалидны при отсутствии механической валидации паспортов; список известных расхождений README неполон в части паспортов | **ПРИНЯТО, НЕ БЛОКИРУЕТ (поля и данные — пре-существующие, данным WO не вводились).** → **Пакетная schema-sync-ревизия №2**: добавить `repair_of`/`verdict_repaired` в passport-схему (опциональные, `type: string`, `minLength`) — либо симметрично 7-hex-кейсу зафиксировать в README как осознанное расхождение floor/ceiling; список известных расхождений README дополнить частью паспортов. Вместе с накопившимися прецедентами (см. ниже). |
| **F2 MINOR**: `VALIDATION_GATES_R1.md` §5 упоминает негатив «TAB в теле `run: \|`», но выделенного теста этого размещения в `tests/test_infra_workflow_lint.py` нет (правило кейс фактически покрывает — независимая проба ревьюера → `WORKFLOW_UNPARSEABLE`) | **ПРИНЯТО, НЕ БЛОКИРУЕТ (рассинхрон документ↔список тестов; правило работает).** → **Та же пакетная ревизия №2**: добавить тест размещения «TAB в теле `run: \|`» либо уточнить формулировку списка тестов в документе. |
| **N2 NOTE** (класс «`checkpoint: CTRL*`»): фактически не встречается (паспорт WO несёт валидный `INFRA1`); при будущем control-`CTRL*` паттерн паспорта снова отстанет от фактов | **ПРИНЯТО К СВЕДЕНИЮ, ПРОФИЛАКТИЧЕСКИ.** → **Та же пакетная ревизия №2**: рассмотреть добавление `CTRL[0-9]*` в паттерн `checkpoint` отдельной sync-ревизией (прецедент процесса — sync отдельным control WO + README-документирование — создан и пригоден), не точечным редактированием принятой ревизии. |

**Сводка по schema-sync-ревизии №2** (единая будущая пакетная control-ревизия схем/тестов, не блокирует INFRA2): F1 (repair-поля в passport-схеме + полнота README) + F2 (тест/формулировка `run: |`) + N2 (проактивно `CTRL*`) + накопленные прецеденты floor/ceiling (4 легаси-события `9cc83e8` — уже задокументированы; новые фиксировать по тому же процессу: sync отдельным bounded control WO, README-документирование, без редактирования принятых ревизий) + **очередь из control-decision NL2-001 от 2026-09-09**: независимое ревью CI-дельты `90bb4c1` (пин NEG-фикстур в Check 1) с переносом NEG-allowlist в `config/infra/validation-gates.v1.json` с линт-контролем. Назначение ревизии — отдельное Director-решение при накоплении критической массы или первом реальном конфликте; до тех пор вести список прецедентов/очередь в README/WORK_QUEUE.

## Условия, с которыми принято

- Настоящее решение — приёмка **контрольного WO**, а не capability: `capabilities.*` в `project/infra-state.json` не меняются (`hosted_ci = true` уже зафиксирован PR #29; `self_hosted_cpu = false` до фактической поставки INFRA2-001).
- `project/infra-state.json` **не изменяется** (минимальное изменение state): контрольный WO `CTRL-LINTSCHEMA` в state не числится; `INFRA2-001` уже `READY`. Снятие блокиратора фиксируется этим документом и SESSION_LOG.
- Содержимое принятых `VALIDATION_GATES_R1.md`/`validation-gates.v1.json` меняется только новой ревизией в отдельном bounded control WO (включая будущую sync-ревизию №2 выше).
- Научный трек не затронут: `project/state.json` без изменений (frontier NL2); INFRA/control-merge не повышает scientific claim и не объявляет научную валидацию. Публичный PR-код не исполняется на self-hosted узлах (их ещё нет).

## Claim ceiling

`C0_SOFTWARE_ONLY`: результат — код линта, schema/config/doc sync, негативные тесты и их документация; научных утверждений не содержит и не создаёт. Зелёные гейты и матрицы проб — технические факты исполнения, не научный PASS. Настоящее решение не активирует self-hosted исполнение: runner не создан, `TR-DISPATCH` остаётся `RESERVED_NOT_ACTIVE`.

## Следующее действие

1. **`INFRA2-001` «Bootstrap isolated self-hosted CPU runner» — блокиратор снят, READY, старт разрешён** (депенды INFRA1-001/INFRA1-002 + контрольный пакет закрыты).
2. **Перед стартом — owner actions `docs/infra/HOSTED_CI_R1.md` §6 требуют владельца**: repo default token read-only, branch protection с required checks (новый набор из 5 чеков) — вне полномочий Director-линии; исполнение WO начинается после подтверждения владельцем.
3. При старте `INFRA2-001` сохранять инварианты: публичный PR-код не исполняется на trusted self-hosted узлах; активация runner'а — explicit protected dispatch с exact subject и budget (baseline §4/§6).
