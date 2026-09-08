# NL0-002 — Implementer Evidence (EX-NL0-002-R1)

Роль: IMPLEMENTER. Статус: `HANDOFF_READY`, не ACCEPTED. Scientific claim: отсутствует (`C0_SOFTWARE_ONLY`). Симуляции не запускались; сторонние научные файлы не копировались.

## Exact subjects

```text
BASE_SHA            = 95b1319600bcc64572d84c0456acb927802ab806
START_COMMIT        = 6a35586642bc9162e5b6f02ab4071a4332a30b45 (harness: start NL0-002 rights audit)
CORE_RIGHTS_COMMIT  = 57fea0628df0126ace877c81bdd60b8ad476536f3 (research: checkpoint NL0-002 core rights audit)
```

Live state на старте: `main` = `95b1319`, `project/state.json`: frontier NL0, NL0-001 ACCEPTED, NL0-002 READY, next_work_order NL0-002, E0..E6 NOT_RUN, physics_runs 0 — совпало с ожидаемым.

## Что проверено и чем (команды/источники)

| Проверка | Метод | Результат |
|---|---|---|
| E1 license | GitHub API `GET /repos/lorenzo-rovigatti/oxDNA/license?ref=00dc7fb...` | `LICENSE`, GPL-3.0, blob `94a9ed024d3859793618152ea559a168bbcbb5e2`, полный текст GPLv3 |
| E1 scope | root LICENSE единственный; README pinned commit прочитан | fixtures/test покрыты root license; citation: JOSS 4693 / JCC 23763 / NAR gkab324 |
| E2 license | GitHub API git/trees + contents по всем каталогам pinned commit `23fd1ff...` + repo metadata | LICENSE/COPYING/NOTICE отсутствуют во всём tree; license detection пустая; pushed_at 2017-04-04 |
| E2 READMEs | root + Design_Hinges + Init_Hinges + MD_Hinges прочитаны полностью | только описания файлов; правовых statements нет |
| Зависимости | GitHub API `/license` для sulcgroup/oxdna-viewer, UC-Davis-molecular-computing/scadnano, choderalab/pymbar, aiidateam/aiida-core, aiidateam/aiida-shell, facebook/Ax, pytorch/botorch | GPL-3.0 (oxdna-viewer); MIT (все остальные); aiida-core текст — MIT (NOASSERTION у GitHub из-за формулировки copyright) |
| NANOBASE | попытка прямого доступа nanobase.org | недоступен из сетевого контура исполнения; использована публикация S10 (copyright deposited structures у авторов) |
| S08 | bounded re-check без расширения поиска | `INPUT_PACK_NOT_LOCATED` сохранён; SI/movies — ACS copyright, cite-only |

## Результаты

```text
E1_RIGHTS                = CLEAR (GPL-3.0, DOWNLOAD_ON_SETUP)
E2_RIGHTS                = UNKNOWN → REQUIRES_OWNER_DECISION (REFERENCE_ONLY + user-side download)
S08_RIGHTS               = RESTRICTED
NANOBASE_RIGHTS          = UNKNOWN per-record
MVP_DEPENDENCY_MATRIX    = DEPENDENCY_LICENSE_MATRIX.md (9 CLEAR, 1 RESTRICTED, 3 UNKNOWN)
NANOLAB_LICENSE_OPTIONS  = Apache-2.0 / MIT / GPL-3.0-or-later; docs: CC BY 4.0 / CC BY-SA 4.0 (решение владельца)
```

## Изменённые поверхности

```text
docs/work/WO-NL0-002.md                                   (создан из issue #3)
docs/research/DEPENDENCY_LICENSE_MATRIX.md                (создан)
docs/research/RIGHTS_AND_REDISTRIBUTION_AUDIT.md          (создан)
docs/evidence/NL0-002/IMPLEMENTER_EVIDENCE.md             (этот файл)
LICENSE_POLICY.md, docs/research/SOURCES.md,
docs/research/TOOL_LANDSCAPE.md, docs/work/SESSION_LOG.md (обновления NL0-002)
docs/work/executions/EX-NL0-002-R1/**                     (passport, events, summary)
```

`project/state.json` / `project/plan.json` не изменялись (нет self-acceptance).

## Incident (environment)

Внешняя реструктуризация workspace заменила одиночный checkout на клоны `main/`+`nl0-002/` между START-push и первым research-коммитом; два несоммиченных research-файла выпали из working tree и восстановлены дословно из сессионного содержимого в клоне `nl0-002`. Remote branch, START и все push-коммиты не пострадали. Зафиксировано в event 0002. Это environment failure, не NL0-002 result.

## Validation

```text
python -m json.tool project/state.json  -> OK
python -m json.tool project/plan.json   -> OK
./CONTROL_DEVELOPMENT.sh --check-consistency / CONTROL_DEVELOPMENT.ps1 -> см. summary.md (выполнено, результат зафиксирован)
./CONTROL_WORK.ps1 validate docs/work/executions/EX-NL0-002-R1 -> OK
./CONTROL_WORK.ps1 close    docs/work/executions/EX-NL0-002-R1 -> OK
```

## Открытые риски / ограничения

- Аудит — не юридическое заключение; интерпретации GPLv3-совместимости для будущих bundling-решений требуют owner/legal review.
- NANOBASE не проверен напрямую (сетевая недоступность).
- Runtime-пин версий PyPI-пакетов и сборки oxDNA — NL1-001.
- E2 derivative designs — отдельный вопрос до NL3-001.

## Next

`NEXT_ACTOR = VERIFIER` (LOW risk: docs/metadata). Поднятие risk не требуется: неоднозначные права не решались агентом, а переданы как OWNER_DECISION; Reviewer желателен перед merge по усмотрению владельца, т.к. появились правовые интерпретации (GPL copyleft/bundling) — Verifier обязан проверить факты матрицы по exact HEAD.
