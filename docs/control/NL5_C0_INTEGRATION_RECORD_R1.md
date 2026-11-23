# NL5_C0_INTEGRATION_RECORD_R1 — один C0 candidate для верифицированных материалов NL5-CLOSE-R1

Director record (integrator function, `docs/control/FLOW_THROUGHPUT_R1.md` §6), 2026-11-23T14:33Z (UTC). Owner request в сессии 2026-11-24: «проверь состояние проекта; продолжи». Программа NL5-CLOSE-R1 (#81). Карта порядка: [NL5_C0_INTEGRATION_MAP_R1.md](NL5_C0_INTEGRATION_MAP_R1.md) (2026-10-26). Work Order: [WO-INTEGRATION-NL5-C0-R1](../work/WO-INTEGRATION-NL5-C0-R1.md); execution: `EX-INTEGRATION-NL5-C0-R1` (sequence-v1).

**Слияние в `main` остаётся Human Gate владельца.** Этот record и PR — одна merge-рекомендация на весь перечисленный scope; они не выдаёт launch/merge authority, не меняют NL5 acceptance, frozen F2, AUTHOR_U1, R2 или authority A. Scientific runs = 0, paid compute = 0.

## 1. Base и candidate

| | SHA | TREE |
|---|---|---|
| Fresh `main` (base) | `ddf8a25cdd95a1598338816f6a585ffdde1e0f2a` (PR #96 merge, 2026-11-07) | `80b4668d9d289f7696d06d39ed9d21d44c4f0acf` |
| Merge-only candidate `7096923` (7 no-ff merges) | `70969235169318db7af4aa019ce1304e40523fcc` | `0f6d13a72cf2f303b95ff2e6646f07b657de6da7` |
| Branch / PR | `integration/nl5-c0-r1` | https://github.com/rootfabric/NanoLab/pull/98 |

Финальный HEAD/TREE PR = commit, содержащий terminal event `EX-INTEGRATION-NL5-C0-R1/0003-handoff-completed.json` (события writer разрешают только существующий commit, поэтому terminal event физически не может содержать собственный SHA); hosted CI привязан к этому HEAD.

## 2. Выполненный порядок merge (пины карты проверены перед каждым merge, расхождений 0)

| # | Subject | Ветка | Exact subject SHA | Merge commit |
|---|---|---|---|---|
| 1 | F01 frozen audit (Director documentary acceptance) | `work/nl5-f01-frozen-audit-r1` | `c7c5be6edbcdb5a304705ff6d53863fa735d7d0c` | `2163b2c135cfb5d77609cfb3b57dedf1c6839d0a` |
| 2 | F02 U1 host eligibility (REVIEW PASS + VERIFIED на `c38ad68`; addendum `9b24f93` — Director control commit) | `work/nl5-f02-u1-host-r1` | `9b24f93092e917cb6064d5c7723e5b4d1f05d67d` | `2b6330d049e9593f3132fef78c73364c2d342fb5` |
| 3 | F03 U2 readiness (REVIEW PASS + VERIFIED, включая addendum 0004) | `work/nl5-f03-u2-readiness-r1` | `1831585fa70169c4e473acfe38e9603e45cfe22c` | `4bc91e85c036d7cd6c42af05b7d67b7da5fc3ca3` |
| 4 | F05 dispatch prep (REVIEW PASS + VERIFIED) | `work/nl5-f05-dispatch-prep-r1` | `4c9d8fd30300a2f48504d1b914693f0a66bb3555` | `30538ea28faf609880a9fe5aef4145b4fc42aa11` |
| 5 | Batch REVIEWER evidence (F02+F03+F05) | `review/nl5-c0-batch-f02-f03-f05-r1` | `906d55dffebb606570bb6ff6b3cd17778d314202` | `b3c1e19ca616d58c72fd45dea50ff531eb0117b6` |
| 6 | Batch VERIFIER evidence (F02+F03+F05) | `verify/nl5-c0-batch-f02-f03-f05-r1` | `9be1964b7860853931fa69d70c8f42a7f053b536` | `70c94325d1a5c6eae5dd941f45ee390f50e2f1f9` |
| 7 | Integration map (Director record) | `control/nl5-c0-integration-map-r1` | `8585c063a82971f9c9ce788bc1dfd173528631e5` | `70969235169318db7af4aa019ce1304e40523fcc` |

Все subjects основаны на `3b567ae33f247b182b2ae451d2cc4598a9e76019`; на дату integration их tips не двигались (карта: «новый коммит на subjects требует обновления пинов» — не потребовалось).

## 3. Целостность candidate (merge-only tree `0f6d13a7`)

- `git diff --stat origin/main 7096923`: **58 файлов, +4879 строк, 0 удалений, 0 изменений** существующих путей.
- Каждый из 58 добавленных путей **blob-идентичен** своему exact subject (`git rev-parse <subject>:<path>` == `HEAD:<path>`, 58/58): 6 execution directories (`EX-NL5-F01-FROZEN-AUDIT-R1`, `EX-NL5-F02-U1-HOST-R1`, `EX-NL5-F03-U2-READINESS-R1`, `EX-NL5-F05-DISPATCH-PREP-R1`, `EX-NL5-C0-BATCH-REVIEW-R1`, `EX-NL5-C0-BATCH-VERIFY-R1`: passports, events, evidence, dispatch proofs, summaries), 4 Work Orders (`WO-NL5-F01/F02/F03/F05`), `docs/control/NL5_C0_INTEGRATION_MAP_R1.md`.
- Исторические events/evidence subjects не редактировались; frozen F2 (`60da9a846511265a8ac7564da088c3d74cb073f0` / tree `e565c8a6cee9e829fac14008ebc9c2ea1609931d`), `project/state.json`, код, тесты и harness в diff отсутствуют.

## 4. Единственный конфликт — `docs/work/WORK_QUEUE.md` (6 из 7 merge)

Карта ожидала «механическую конкатенацию» append-строк. После карты в `main` принят FLOW-R1 (PR #95, merge `3b567ae..ddf8a25`), который **заменил общую таблицу** на `project/operations/*.json` и прямо запретил дописывать handoffs в общий файл («Это устраняет конфликты независимых веток на общей таблице»); предыдущая очередь сохранена побайтово в `docs/work/WORK_QUEUE_HISTORY_PRE_FLOW_R1.md` (копия `main@3b567ae`).

Разрешение: `WORK_QUEUE.md` в candidate **побайтово равен `main@ddf8a25`** (проверено `git diff HEAD origin/main -- docs/work/WORK_QUEUE.md` пуст после каждого merge). Шесть append-строк веток (F01, F02, F03, F05, review, verify) не переносятся в новую очередь; их факты сохранены: (а) в `summary.md` каждого из шести execution directories, включённых в candidate; (б) в историях subject-веток и в merge commits этого PR; (в) в operations cards `AUTHOR-U1.json` / `EXTERNAL-U2.json` / `RESOURCE-R1.json` (ссылки на F02/F03 evidence). Удаления строк в `main` не происходит. Это решение заменяет ожидание карты; карта как Director record 2026-10-26 не редактируется.

## 5. Проверки

Локально (Windows UI host, **не авторитетный gate**; authoritative = hosted CI H0 на PR, 5 checks):

| Gate | main@ddf8a25 | candidate | Комментарий |
|---|---|---|---|
| Check 1 JSON syntax | ok, 1591 | ok, **1624** | +33 JSON файлов subjects |
| Check 2 consistency | ok | ok | operations registry валиден |
| Check 3 executions | ok, 72 | ok, **78**, errors 0 | 6 NL5 C0 records валидны под FLOW-R1 harness (validator corrections-aware) |
| Check 4 workflow lint | 0 violations | 0 violations | |
| Check 5 unittest | Ran 1054; FAILED 49/27, skipped 3 | Ran 1054; FAILED 49/27, skipped 3 | **множество failing-методов идентично** (73 уникальных, все — Windows-окружение: symlink privilege WinError 1314, CRLF- digest, case-insensitive paths, `git commit` во временных fixture); **0 новых failures** |

Логи: `scratch/lead-2026-11-24/{main,integration}-unittest.log`, `*-failset.txt` (локальные, вне Git; hosted CI — канонический gate).

## 6. Зависимости и действующее разрешение

- F02 addendum (`9b24f93`) ссылается на handoff F01 `c7c5be6` — включён (#1). Batch review связывает F02 `c38ad68`(+addendum)/F03 `1831585`/F05 `4c9d8fd` — включены (#2–#4). Batch verify связывает review `906d55d` — включён (#5). Карта связывает все — включена (#7). Цепочка ссылок по exact tips остаётся валидной и после merge.
- Разрешение на подготовку candidate: карточка `INTEGRATION-R1` (READY, actor DIRECTOR) + FLOW-R1 §6 (интегратор «готовит совместимый C0 пакет… формирует одну merge-рекомендацию»; «не требовать нового Verifier только из-за отчётного SHA»). Subjects уже имеют независимые Reviewer/Verifier на exact HEAD/TREE (карта, §Верифицированные subjects); их содержимое не изменено (§3), поэтому новый полный review неизменных частей не требуется, интеграция получает полный интеграционный CI (FLOW-R1 §3).
- Не изменено и не разрешено: HG-A / R2 activation (AUTHOR_U1 = NOT_ASSIGNED), U2 remediation (#94), authority A (отдельный WO после F04), F04/F06/F07+ gates, scientific launch, budget, Task Bus P2.

## 7. Замечание о stale cards (вне этого PR)

В `main` карточки `FLOW-R1`, `ATOMISTIC-ADAPTER-PREP`, `ATOMISTIC-APP-PREP` всё ещё показывают `CANONICAL_MERGE_PENDING` для PR #96, хотя #96 смержен (`ddf8a25`). Исправление уже содержится в открытом PR #97 (`work/atomistic-reference-r1`); здесь не дублируется, чтобы не создавать конфликт между двумя открытыми PR. Порядок merge #97/#98 — на усмотрение владельца; второй по очереди получит интеграционный CI после merge main.

## 8. Claim ceiling и next action

C0_SOFTWARE_ONLY. VERIFIED/REVIEW PASS subjects не повышаются: merge этого PR не является научной приёмкой NL5, не активирует R2 и не авторизует запуски. Отрицательные результаты (BLOCKED_OWNER_U1, BLOCKED_NO_U2_ACCESS_FROM_SESSION, READY_WITH_OPEN_GATES, findings NF) сохранены в включённых records.

**Next action (одно):** владелец принимает merge-решение по PR #98 (один Human Gate на 7 subjects). После merge — `drive`/`operations` на fresh main и перевод карточки `INTEGRATION-R1` в `DONE` следующим C0 package; дальнейшие шаги NL5-CLOSE-R1 (F04 → authority A) по-прежнему ждут выделения AUTHOR_U1.
