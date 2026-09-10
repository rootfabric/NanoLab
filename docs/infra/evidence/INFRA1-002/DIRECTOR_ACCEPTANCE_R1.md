# Director Acceptance — INFRA1-002 (Add PR validation gates)

Дата решения: 2026-09-09. Роль: DIRECTOR (главный агент INFRA-линии миссии; явная авторизация владельца на Director-приёмку и merge в `main` получена в сессии).

## Решение

```text
INFRA1-002 = ACCEPTED
checkpoint INFRA1 = ACCEPTED (стадия закрыта: safe hosted CI + PR validation gates)
frontier = INFRA2 (checkpoint INFRA2 = IN_PROGRESS)
next_work_order = INFRA2-001 (READY) — с обязательным предварительным условием (см. «Решения по findings»)
claim = C0_SOFTWARE_ONLY
VALIDATION_GATES_R1 (docs/infra/VALIDATION_GATES_R1.md + config/infra/validation-gates.v1.json) = ACCEPTED (был PROPOSED)
capabilities.hosted_ci = НЕ флипается этим merge — флип по post-merge live-условию (см. «Условия»)
```

## Основание

1. **Реализация**: `EX-INFRA1-002-R1` — механический negative-control линт workflow `scripts/harness/workflow_lint.py` (NC-1..NC-7 + fail-closed на unsupported формах `on:` и multi-doc/anchors/aliases, машинно-читаемая проекция `config/infra/validation-gates.v1.json`, revision `VALIDATION-GATES-R1`) + corrections-aware валидатор `scripts/harness/work_cli.py` (`REVIEW_CORRECTIONS`: только `REVIEWER/VERIFIER/DIRECTOR`, `ts >= terminal`, 40-hex `subject_sha` для всех новых событий при точном легаси-whitelist'е пары `(EX-NL1-002-R1, 0002-…)` со значением `9cc83e8` и provenance) + интеграция всех гейтов в `.github/workflows/hosted-ci.yml` (Check 3 diff-scoped на changed `EX-*`, новые Check 4 workflow-lint и Check 5 gate-tests) + тесты `tests/` (34 → 59, включая обязательные негативы всех закрытых обходов) + документ `docs/infra/VALIDATION_GATES_R1.md` (corrections policy, NC-эталон). Runners/secrets/GPU/paid compute — NONE; научный трек не затронут.
2. **Blocking-критерии приёмки — оба исполнены и независимо подтверждены**:
   - **(a) механический NC-тест** (наследованное условие MINOR-1 вердикта INFRA0-001): REVIEWER — 18/18 матричных исходов (фикстуры раунда 1 1:1) + 8 дополнительных проб (`RE_REVIEW_R1.md` §2); VERIFIER — собственная матрица 30/30, mismatch 0 (`VERIFIER_VERDICT.md` §2), включая позитивы «реальный hosted-ci.yml → exit 0» и блокировку самохостед-лейблов в обе стороны (`NC1_SELF_HOSTED_LABEL`, `NC1_DYNAMIC_RUNS_ON`, `NC1_RUNS_ON_MISSING`). Критерий «untrusted PR route не может выбрать self-hosted runner» воспроизведён независимо двумя сторонами.
   - **(b) corrections-aware `work_cli`** (первый пункт и блокирующий критерий из MINOR-2 вердикта INFRA1-001): REVIEWER — 10/10 `EX-*` validate сохранён, обе дыры R1 закрыты (corrections-ts < terminal; corrections от `IMPLEMENTER`; abbreviated/переиспользованный SHA) без регрессии обычного потока (`RE_REVIEW_R1.md` §3–§4); VERIFIER — 13/13 групп независимо, включая легитимный corrections-путь `REVIEWER` + `ts ≥ terminal` → OK (`VERIFIER_VERDICT.md` §3). Догфудинг: собственный corrections-хвост events `0005/0006` этого execution принимается repaired-валидатором.
3. **Независимые вердикты**: REVIEWER R1 `FIX_REQUIRED` (`1ca40b6`, MAJOR-1/MAJOR-2 — обходы линта, MINOR-1..3) → ремонт с `REPAIR_MAP_R1` (substantive ремонтного раунда `74e17c7`) → **RE_REVIEW_R1 PASS** (ветка `review/infra1-validation-gates-r1` @ `267cf4f`) и **VERIFIER PASS** (ветка `verify/infra1-validation-gates-r1` @ `c995f28`; полные чеки на `74e17c7`: JSON 111/111, check-consistency ok, 10/10 EX, lint 0 violations, 59/59 tests). Оба вердикта влиты в эту ветку merge-коммитами (`064fc8e`, `ed06d72`); blob-идентичность канонических копий подтверждена.
4. **Граница ролей соблюдена**: doc/config опубликованы в статусе `PROPOSED`, `ACCEPTED` имплементёром не выставлен, `capabilities.hosted_ci` не флипнут (`project/infra-state.json` blob `d9b0be08` = base по факту верификатора), state/science-файлы не тронуты — принятие и перевод статусов происходят только этим Director-решением через принятый merge.
5. **Base drift** (origin/main `a4533ab` = base `15a2c9b` + PR #27, science addendum NL1-002): INFRA-поверхность PR не пересекается (подтверждено верификатором, merge-base = base); свежий main влит в control-ветку merge-коммитом `0db562e` перед PR. На merge-HEAD ветки локально воспроизведены все 5 чеков: JSON 113/113, check-consistency ok, 10/10 EX, lint 0 violations, 59 tests OK.

## Решения по findings

| Finding | Решение Director'а |
|---|---|
| **MAJOR-1 / MAJOR-2 / MINOR-1** (REVIEWER R1: обходы линта — `on:` non-mapping, anchors/aliases, `secrets['X']`) | **ЗАКРЫТЫ РЕМОНТОМ R1**, подтверждены независимо: RE_REVIEW (фикстуры обходов 1:1 → закрыты, +8 доп. проб) и VERIFIER (30/30, включая свои эквивалентные формы). Повторных обходов ни одна сторона не нашла. |
| **MINOR-2 / MINOR-3** (REVIEWER R1: семантика corrections — timestamp против terminal, роль `REVIEW_CORRECTIONS`) | **ЗАКРЫТЫ РЕМОНТОМ R1** (ts ≥ terminal для новых событий при легаси-exempt 4 событий; роль `REVIEWER/VERIFIER/DIRECTOR`, IMPLEMENTER → hard error); независимо подтверждены обеими сторонами; легитимный corrections-путь сохранён, блокирующий критерий (b) исполнен. |
| **MINOR-4** (RE_REVIEW_R1; подтверждён верификатором V-1): таб-чек парсера — dead code (`indent = lstrip(" ")`, срез `[:indent]` не может содержать TAB); «tabs → fail closed» держится не для всех размещений | **ПРИНЯТО КАК ОБЯЗАТЕЛЬНЫЙ FOLLOW-UP.** Направление fail-safe (GitHub отвергает TAB-индентацию целиком — исполняемого файла нет, обход NC-1/NC-2 невозможен), поэтому приёмку INFRA1-002 не блокирует. Ремонт (отклонять TAB в ведущем whitespace сырой строки → `WorkflowParseError` + негативные тесты обоих размещений — под `on:` и под job-ключом) — **первый пункт пакетного контрольного WO и обязательное условие ДО старта `INFRA2-001`**: NC-1 — защитник label-namespace как раз при активации self-hosted runner'а. |
| **NOTE-5** (RE_REVIEW_R1; подтверждён верификатором V-2): `jobs:` в не-mapping форме (список/null) молча пропускает job-правила | **ПРИНЯТО КАК ОБЯЗАТЕЛЬНЫЙ FOLLOW-UP в тот же пакетный контрольный WO** («fail-closed на schema-невалидных формах» — вместе с MINOR-4; `on:` уже закрыт ремонтом MAJOR-1). Тот же fail-safe класс; до INFRA2-001. |
| **Schema-sync** (REVIEWER R1 NOTE-4; верификатор V-3; третий INFRA-прецедент подряд): `work-event.schema.v1.json` — enum без `REVIEW_CORRECTIONS`, `subject_sha` pattern против 4 легаси-событий `9cc83e8`; `execution-passport.schema.v1.json` — `checkpoint` `^NL[0-8]$` против `"INFRA1"` | **ПРИНЯТО КАК ОБЯЗАТЕЛЬНЫЙ FOLLOW-UP в тот же пакетный контрольный WO**: синхронизация control-схем с фактической семантикой (enum `REVIEW_CORRECTIONS`; 40-hex для новых событий при документированном легаси-whitelist'е; паспорт-паттерн `^(NL[0-8]|INFRA[0-7])$`). Живого конфликта нет (механической валидации events по JSON-схеме нет), но накапливать четвёртый прецедент нельзя. **До INFRA2-001.** |
| **Оговорка REPAIR_MAP-пути** (обе стороны: `docs/infra/evidence/INFRA1-002/` вне исходных allowed_paths паспорта) | **ПРИНЯТО, НАРУШЕНИЕМ НЕ СЧИТАЕТСЯ**: durably задокументировано имплементёром в event `0005-repair-completed`, размещение Repair Map в evidence-каталоге соответствует протоколу (AGENTS.md §10), история событий не переписывалась. |
| **Base drift миссии** (origin/main продвинулся к `a4533ab`) | **ПРИНЯТО К СВЕДЕНИЮ** (задокументирован имплементёром в event 0001 и доке §8.1); закрыт merge `0db562e` в этой control-ветке. |

**Сводка по пакетному контрольному WO**: MINOR-4 + NOTE-5 + schema-sync — единый bounded control WO («lint fail-closed hardening + schema sync»), **первый пункт control-очереди, обязательный и блокирующий для старта `INFRA2-001`**. `project/infra-state.json` переводит `INFRA2-001` в `READY` (планирование разрешено), но старт WO — только после merge этого контрольного WO.

## Условия, с которыми принято

- **`capabilities.hosted_ci` флипается по post-merge live-условию, а не этим merge.** Фиксация фактов: первый live SUCCESS-прогон наблюдался при INFRA1-001 (run `34350801109`, TR-PR PR #25; run `34351227262`, TR-PUSH-MAIN `6796531`); затем два RED-прогона — run `34352437448` (TR-PR `4143464`, PR #26) и run `34352589656` (TR-PUSH-MAIN `15a2c9b`) — оба упали на residual Check 3: corrections-unaware валидатор блокировал легитимные post-terminal events контрольного execution. Именно этот дефект устраняет настоящий WO (blocking-критерий (b)); его ремонт независимо подтверждён, а PR этого checkpoint'а сам является live-испытанием: TR-PR должен провести обновлённые гейты над merge-содержимым. **Решение: если TR-PUSH-MAIN прогон на merge-коммите этого checkpoint'а зелёный по всем 5 чекам — `hosted_ci` флипается в `true` отдельным follow-up control-решением (малый control commit/PR сразу после merge); если красный — `hosted_ci` остаётся `false`, причина фиксируется в отчёте миссии и SESSION_LOG.** На момент настоящего решения `hosted_ci = false`.
- Doc `VALIDATION_GATES_R1.md` и конфиг `validation-gates.v1.json` переводятся в статус `ACCEPTED` этим решением; изменение содержимого — только новой ревизией в отдельном bounded WO (включая обязательный пакетный контрольный WO выше).
- `TR-DISPATCH` остаётся `RESERVED_NOT_ACTIVE`; публичный PR-код не исполняется на self-hosted узлах (в репо их нет). Owner actions (`HOSTED_CI_R1.md` §6: repo default token read-only, branch protection с required check) остаются за владельцем.
- Научный трек не затронут: `project/state.json` без изменений (frontier NL2, `E1 = RUN`, `physics_runs = 4`); INFRA-merge не повышает scientific claim и не объявляет научную валидацию.

## Claim ceiling

`C0_SOFTWARE_ONLY` (подтверждён обоими независимыми вердиктами): результат — код линта/валидатора, тесты, CI-интеграция, machine-readable конфиг и документация; научных утверждений не содержит и не создаёт. Зелёные гейты — технический факт исполнения, не научный PASS. Настоящее решение не активирует INFRA2-исполнение: self-hosted runner остаётся несозданным, а старт `INFRA2-001` заблокирован до merge пакетного контрольного WO.

## Следующее действие

1. **Пакетный контрольный WO** «lint fail-closed hardening + schema sync» (MINOR-4, NOTE-5, schema-sync) — первый пункт control-очереди, до INFRA2-001.
2. После его merge — `INFRA2-001` «Bootstrap isolated self-hosted CPU runner» (READY; депенды INFRA1 закрыты). Владельцу — owner actions `HOSTED_CI_R1.md` §6 и решение по branch protection с новым набором чеков.
3. Post-merge: проверить `gh run` TR-PUSH-MAIN на merge-коммите; при зелёном результате — follow-up флип `capabilities.hosted_ci = true` (условие выше), при красном — фиксация причины с сохранением `false`.
