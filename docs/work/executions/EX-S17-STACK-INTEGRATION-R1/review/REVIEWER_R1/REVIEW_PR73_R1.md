# [REVIEWER-73] Независимое review PR #73 (S17-R3/F01–F04/CLI) @ HEAD baac137 — VERDICT: PASS

**Reviewer:** REVIEWER-73 (независимая сессия; не Implementer/Author/Director этой ветки)
**Дата:** 2026-10-21 (UTC) · **Режим:** read-only review, offline C0; 0 scientific runs; 0 paid compute
**Checkout:** изолированный локальный клон ветки `integration/s17-r3-repair-assembly-cli-r1`; собственные write-артефакты — только `review-evidence/` и `/tmp`

## 0. Subject

| Параметр | Заявлено | Фактически (проверено `git`) | Совпадение |
| --- | --- | --- | --- |
| HEAD | `baac1378b3de604cdad99c546e1cf9d9b5b000b3` | `git rev-parse HEAD` → `baac1378b3de604cdad99c546e1cf9d9b5b000b3` | ✅ |
| TREE | `e63caed7c5922e83add2696abb6dc5c0fe8787b4` | `git write-tree` (чистое дерево) → `e63caed7c5922e83add2696abb6dc5c0fe8787b4` | ✅ |
| Base main | `fb3148b46a9638167168a46cb170902a4ad9e8d2` | `git merge-base baac137 fb3148b` → `fb3148b…` (ветка — прямой потомок base) | ✅ |
| Предок стека | `26c4cd5` | `git merge-base baac137 26c4cd5` → `26c4cd5…` (26c4cd5 — предок) | ✅ |

Состав vs base `fb3148b`: **74 добавленных файла + 1 модификация** (`docs/work/WORK_QUEUE.md`, +6 строк / −0 строк — append-only соблюдён). Никакие иные файлы `main` (включая `project/state.json`, `project/plan.json`, frozen NL5) не затронуты — проверено `git diff --name-status fb3148b..baac137`.

## 1. Обязательные команды

| Команда | Exit code | Результат |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -t .` | 0 | **Ran 930 tests in 62.153s — OK** (0 failures) |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | 0 | `ok: true`, errors: [], warning: `git metadata unavailable` (окружение; head/tree при этом определены корректно) |
| `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | 0 | `violations: 0, blocking: 0` |
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-S17-STACK-INTEGRATION-R1` | 0 | `ok: true`, `HANDOFF_READY`, `has_post_terminal_corrections: true` (см. п. 4.8), errors: [] |

Дополнительно: `work_cli validate` для `EX-PREP-S17-R3-REPAIR-R1`, `EX-PREP-S17-R3-OVERHANG-ERRATUM-R1`, `EX-PREP-S17-R3`, `EX-S17-STATIC-ASSEMBLY-HARDENING-R1` — все `ok: true`, errors: [] (лог: `review-evidence/08_work_cli_all_dirs.txt`).

## 2. Таблица проверок (области 1–8)

| # | Область | Команда / метод | Exit | Наблюдение | Вывод |
| --- | --- | --- | --- | --- | --- |
| 1 | R3-контракты vs оригинальный WO | чтение `WO-PREP-S17-R3.md` (Required outputs 1–7) + сверка файлов | 0 | Все 7 обязательных outputs присутствуют: INTERFACE_AUDIT, COMPONENT_DRIVER/FOLLOWER, ASSEMBLY_SPEC/RECEIPT, 2 модуля контрактов, тесты, SOURCE_GAPS, execution-pack. Verdict реальной пары `NOT_RECONSTRUCTED`, claim ceiling `PINNED_IMPORT_VERIFIED` — как требует WO | ✅ соответствие |
| 2 | Целостность импорта 55 blob'ов | скрипт `git rev-parse <rev>:<path>` для всех 55 путей из `source-blob-map.json` против `7236461` (integration), HEAD и исходных tip'ов `ca6eabd`/`a4b4cf3`/`2cf8297`/`49be267` | 0 | На integration-коммите `7236461`: **55/55 blob'ов байт-идентичны** карте и исходным tip'ам. На HEAD: **53/55**; 2 пути (`S17_R3_COMPONENT_FOLLOWER.json`, `tests/test_s17_r3_assembly.py`) изменены позже — но именно erratum-коммитами `4f9583d`/`1bfafb9` со сквозным pinned-следом (см. п. 4.3) | ✅ (с minor M1) |
| 3 | 10 пар 20nt RC из Dataset S1 | собственный скрипт (извлечение портов из JSON + `reverse_complement`) | 0 | 10 driver + 10 follower портов; **10/10: driver и follower сегменты ровно 20 nt, follower == exact reverse-complement(driver)**, оба сегмента — подстроки собственных LNA-stripped ODN (`strip_lna` из библиотеки). Pin Dataset S1 `sha256 dc3cc6c5…3036c` (101900 B) согласован в 4 поверхностях: fetch-manifest, recipe `source_pins`, INTERFACE_AUDIT, erratum-тест. Erratum 21nt→20nt на 7 follower-портах **ИСПРАВЛЕНО** в рецептах/спеках (не открытый), RED CI #39523456603 (930 тестов / 7 FAIL) → GREEN CI #39524159028 (930 OK); RED-нога воспроизведена мной локально на `f15d6f4`: `Ran 4 tests … FAILED (failures=7)` | ✅ (исправлено, не молчаливо) |
| 4 | F01–F04 repair | чтение `WO-PREP-S17-R3-REPAIR-R1.md`; независимое RED-воспроизведение: /tmp-клон @ `2cf8297` + falsifiers из HEAD → `python3 -m unittest tests.test_s17_r3_fresh_review_falsifiers` | 0 | На faulty base `2cf8297` все 4 falsifier'а падают: **`FAILED (failures=4)`** (совпадает с заявленным CI 39124902081). На HEAD — проходят в составе 930 OK. F01: гейт `connection_capable=true` + конкретные integer-anchors + не-UNKNOWN статусы (только при assembly; честный NOT_RECONSTRUCTED сохранён). F02: `_verify_interface_recipe` реально читает байты с диска, сверяет SHA-256, безопасный путь, kind, per-connection binding, ambiguity → BLOCKED_SOURCE. F03: единый pipeline factor→rotation→translation для частиц И anchors, роль-симметричный. F04: проверка именно заявленных exposed overhang-сегментов (exact RC, 5'/3', LNA-strip, сегмент ⊂ своей ODN; отсутствие → BLOCKED_INFERRED_INTERFACE). Регрессии на каждый дефект + расширенная негативная матрица | ✅ fail-closed усилен, не ослаблен |
| 5 | Координатные трансформации | чтение `_rotation_matrix`, `_transform_point/particle`, `_component_transform_params`; проверка формулы | 0 | Матрица — корректный Rodrigues (right-handed, cI+(1−c)xxᵀ+s[x]ₓ); порядок строго **unit factor → rotation → translation**, применён одинаково к частицам, orientation-векторам и anchor-подсказкам; driver-side трансформации больше не игнорируются; фиксированный float-формат, детерминизм; F03-фальсификатор закрепляет 90°-кейс (24.005 vs buggy 29.005) | ✅ корректно |
| 6 | Recipe SHA/source binding | чтение `_verify_interface_recipe` + erratum-тест (tamper-regression) | 0 | Binding **реально исполняется кодом**: файл на диске, sha256 байтов, безопасный относительный путь, kind, обязательный join каждой hybridization-connection к записи рецепта (`recipe_pair_ref` либо `odn_name`), >1 совпадения → BLOCKED_SOURCE, обязательный cross-check сегментов обеих сторон. Pin рецепта `sha256 5f485b0a…61b6` подтверждён мной `sha256sum`; подмена 20nt→21nt → `BLOCKED_SOURCE` (тест + CI) | ✅ код, не декларация |
| 7 | UNKNOWN anchors | прямой разбор обоих `S17_R3_COMPONENT_*.json` + erratum-тест | 0 | Все 20 реальных портов: `anchor=(UNKNOWN, status=UNKNOWN)`, `orientation.status=UNKNOWN`, `connection_capable=false`; follower `topology/configuration=UNKNOWN`; receipt `NOT_RECONSTRUCTED`. Сборщик отказывает literal-UNKNOWN (F01). Ни один UNKNOWN не подменён вычисленным значением | ✅ честно |
| 8 | События 0003/0004 | `git show baac137` (полный diff), `git ls-tree 4db05c2`, чтение события 0005, summary | 0 | Подробно в п. 3. Вердикт: **допустимо с оговоркой** | ✅ / ⚠ minor M2 |

## 3. Append-only вердикт по событиям 0003/0004 (явный)

**Факты (проверено по Git-истории):**
1. События 0002–0004 `EX-S17-STACK-INTEGRATION-R1` были созданы в этом же PR коммитом `4db05c2` с идентичным `timestamp_utc = 2026-10-21T01:01:29.764Z`; hosted CI #39524871712 отклонил дубликаты.
2. Коммит `baac137` (HEAD, **новый non-force коммит**, не rewrite) изменил в событиях 0003/0004 **только поле `timestamp_utc`** (+1 мс / +2 мс). Остальные поля (actor, subject_sha, summary, refs) не тронуты; событие 0002 не менялось.
3. Старые blob'ы сохранены и адресуемы: `git ls-tree 4db05c2` даёт ровно заявленные `0002=00ba2a3c…`, `0003=10303b5b…`, `0004=f6e3bffc…` — история не переписана, force-push отсутствует.
4. Коррекция задокументирована **тремя** независимыми поверхностями: новое append-only событие `0005-continuation-timestamp-normalization.json` (с явным «REVIEWER MUST EXAMINE THIS EXCEPTION»), раздел в `summary.md`, commit message. Харнесс это же детектирует: `has_post_terminal_corrections: true`.

**Вердикт:** это **не** «правка старого события задним числом» в смысле blocker-критерия: редактировались события, созданные 4 минутами ранее **внутри этого же неслитого PR**, никогда не входившие в канонический `main`; история сохранена, коррекция раскрыта и помечена на review, научное содержание не затронуто. Такой случай подпадает под допустимую ветку «документированная коррекция новым событием» — **допустимо с оговоркой**. Оговорка (minor M2): формулировка «pre-acceptance documented exception» нигде не кодифицирована в control-документах; исключение обязано быть зафиксировано в policy (например, в `AGENTS.md`/`docs/control/`) отдельным решением владельца, иначе прецедент может тиражироваться.

## 4. Findings

### Blockers

**Не найдено.** Все 8 обязательных областей проверены независимо; расхождений «заявлено vs фактически», подмен статусов, fabricated anchors, ослабления fail-closed или научной инфляции не обнаружено.

### Minors

- **M1.** `EX-S17-STACK-INTEGRATION-R1/evidence/source-blob-map.json` декларирует 55 байт-идентичных blob'ов без аннотации, что на HEAD 2/55 путей (`S17_R3_COMPONENT_FOLLOWER.json` c44374a→3a09fab; `tests/test_s17_r3_assembly.py` 91729bb→074619e) суперсидены erratum-1. Расхождение полностью прослеживается (erratum-receipt явно пинует старый и новый blob SHA1, RED/Green CI зафиксированы), но самой карте нужна пометка `superseded_by_erratum-1`, чтобы карта была самодостаточной на exact HEAD.
- **M2.** Исключение append-only для 0003/0004 (п. 3) документировано в PR, но не кодифицировано в control-документах — требуется policy-решение владельца до того, как приём появится.
- **M3.** `check-consistency` выдаёт warning `git metadata unavailable` (окружение runner'а; head/tree при этом вычислены корректно). Стоит либо устранить причину, либо документировать warning как ожидаемый в offline-среде.
- **M4.** Паспорта `EX-PREP-S17-R3*`/`EX-S17-STATIC-ASSEMBLY-HARDENING-R1` несут `status: STARTED` при фактических HANDOFF_COMPLETED-журналах. Это сложившаяся конвенция репозитория (паспорт замораживается на старте, статус живёт в events/WORK_QUEUE — подтверждено на `EX-PREP-S17-R2` из `main`), но разнобуху с `HANDOFF_READY` у интеграционного паспорта стоит унифицировать.

### Claim ceiling

Подтверждён: реальная S17 follower-конструкция — **NOT_RECONSTRUCTED** (`S17_R3_ASSEMBLY_RECEIPT.json`; закреплено erratum-тестом `test_no_spurious_physical_port_or_science_claim`), follower topology/configuration — UNKNOWN, все статусы CLI — только `ASSEMBLED_STATIC_ONLY`/`NOT_RECONSTRUCTED`/`BLOCKED_*` + `GEOMETRY_UNVERIFIED`, `ASSEMBLY_VALIDATED`/`MODEL_REPRODUCED` запрещены маркер-гейтом CLI, `project/state.json` не изменён (проверено diff'ом vs base), 0 scientific runs. Никаких заявлений о собранной/функциональной конструкции нет. Пример CLI честно помечен `CANDIDATE_DESIGN/HYPOTHESIS` и синтетичен (мой прогон: assemble exit 0, `ASSEMBLED_STATIC_ONLY + GEOMETRY_UNVERIFIED`, verify ok, receipt sha256 `4504ebf7…` ≡ `expected_receipt.json`).

### Ограничения review

- Hosted CI прогоны (#39124902081, #39523456603, #39524159028, #39524871712) не переисполнялись мной (offline, C0); их RED/GREEN ноги независимо воспроизведены локально (п. 2, строки 3–4), что является более сильной проверкой, чем доверие к CI-логам.
- Pin Dataset S1 (sha256 `dc3cc6c5…`) не перепроверялся повторным скачиванием (offline-режим review); проверена внутренняя согласованность пина в 4 поверхностях и байт-пин рецепта, зависящего от этого источника.
- VERDICT относится к C0-кандидату на exact HEAD; это не научная приёмка и не замена обязательным остающимся гейтам: fresh integration exact-head Verifier (`integration_exact_verifier = WAIT_EXTERNAL`, честно задекларирован) и Human Gate на merge. Независимый Reviewer PASS здесь не повышает никаких статусов.

## 5. VERDICT

## **PASS**

Условия: blockers отсутствуют; minors M1–M4 не блокируют; merge в `main` по-прежнему требует свежего exact-head Verifier и Human Gate в соответствии с `WO-S17-STACK-INTEGRATION-R1.md` (п. 4 плана) — сам факт этого PASS их не заменяет и не отменяет.

**Evidence:** `review-evidence/00…09` в данном клоне (HEAD/TREE-чек, логи 4 обязательных команд, RC-проверка 10/10, RED-repro F01–F04 @2cf8297 и erratum @f15d6f4, прогон CLI-примера, validate всех 4 execution-диров).
