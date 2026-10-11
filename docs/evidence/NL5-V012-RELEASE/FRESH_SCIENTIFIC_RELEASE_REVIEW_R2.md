# FRESH SCIENTIFIC RELEASE REVIEW R2 — PR #56 (release v0.1.2 packaging)

- `record_kind`: FRESH_SCIENTIFIC_RELEASE_REVIEW (R2)
- `issuer_class`: INDEPENDENT_REVIEWER (fresh agent session, no prior context)
- Дата обзора: 2026-10-11 (`timestamp_utc` обзора: `2026-10-11T12:00:06Z`)
- Хост обзора: `outenemy` (закреплённая платформа U2) — допустимо для технического
  release-обзора; научные/подтверждающие работы НЕ запускались (только технические
  гейты).

## 0. Пины субъекта обзора (exact pins)

| Поле | Значение | Проверка |
|---|---|---|
| branch | `work/nl5-v012-packaging-pyc-repair-r1` | `git fetch origin --prune` из свежего клона |
| `reviewed_head` | `998878236a1f06995f837ba1dac583eee3a68f0e` | `git rev-parse origin/work/nl5-v012-packaging-pyc-repair-r1` |
| `reviewed_tree` | `c8fabd597a9adac87bbb5c9b39a695e202c65a62` | `git rev-parse 9988782^{tree}` — совпадает с заявленным |
| base / merge-base | `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad` (= `origin/main`) | `git merge-base origin/main 9988782` → `8bf7e3a…`; `git merge-base --is-ancestor` → main — строгий предок HEAD |
| Коммиты ветки | `d4d56a3` → `e7d5081` (R1) → `3b3de38` (handoff R1) → `e72dc4b` (R2 fix) → `9988782` (R2 record) | `git log --oneline 8bf7e3a..9988782` |

**Заявление о свежести:** обзор выполнен в полностью новом клоне
`/tmp/review-v012-r2/clone` (создан командой `git clone` из локального origin
`/home/rdpuser/NanoLab/.git-store/repo.git` в рамках этой сессии), с новым
`git fetch origin --prune`; существующие worktree/каталоги не использовались.
Все числа ниже пересчитаны самостоятельно (собственные скрипты/команды), а не
взяты из evidence-файлов ветки.

## 1. Сводка вердикта

**VERDICT: PASS** (claim ceiling: **packaging-only**; никаких научных утверждений
не проверялось и не принимается — все научные поверхности v0.1.2 байт-в-байт
идентичны v0.1.1, что само по себе не создаёт новых научных претензий).

Блокирующих находок (M-*) нет. Минорные находки: m-1 (см. §4).

## 2. Таблица проверки утверждений (claims 1–9)

| # | Утверждение | Метод проверки (выполнен независимо) | Результат |
|---|---|---|---|
| 1 | R1-дефект: манифест v0.1.1 содержал 7 `__pycache__/*.pyc`, не трекаемых git; `reproduce.py verify` свежей копии v0.1.1 падает exit 3 ровно на них | `git show 8bf7e3a:…/RELEASE_MANIFEST.json \| grep pyc` → 7 записей `convention/nlbl_convention/__pycache__/*.cpython-310.pyc`; `git ls-tree -r 8bf7e3a \| grep -c pycache` → 0; `git archive 8bf7e3a` → чистый tmp → `reproduce.py verify` | **ПОДТВЕРЖДЕНО**: exit 3; ровно 7 ошибок «missing file: …/__pycache__/*.cpython-310.pyc», иных ошибок нет |
| 2 | R1-ремонт: фильтр в `card_lint._package_files`, единая точка для create+verify; v0.1.2 = копия v0.1.1; +3 регрессионных теста | Чтение diff `scripts/release/card_lint.py`; grep точек вызова; diff `tests/test_release_contract.py`; попарное сравнение деревьев (см. #5) | **ПОДТВЕРЖДЕНО**: условие `"__pycache__" not in p.parts and p.suffix != ".pyc"`; вызовы ровно в `manifest_create` (L210) и `manifest_verify` (L247); 3 теста `TestPackageFilesExcludesGeneratedArtifacts`; v0.1.2 — байтовая копия v0.1.1 с точечной дельтой |
| 3 | R2: RIGHTS.json v0.1.2 — устаревшие метаданные (диагноз), фикс 0.1.0→0.1.2 + регенерация манифеста; идемпотентность; ровно 1 изменённая запись | Поверхности версий всех трёх релизов (VERSION/RIGHTS/manifest) на HEAD и на base; `git rev-parse` деревьев v0.1/v0.1.1 base vs HEAD; регенерация `manifest create` в tmp-копии + `cmp` байтов; структурный diff манифестов 3b3de38 vs 9988782 | **ПОДТВЕРЖДЕНО**: v0.1.0 = 0.1.0/0.1.0/0.1.0 (согласована); v0.1.1 = 0.1.1/RIGHTS **0.1.0**/0.1.1 (устаревание внесено здесь, исторический релиз НЕ редактирован: tree-объекты v0.1 и v0.1.1 идентичны на base и HEAD); v0.1.2 = 0.1.2/0.1.2/0.1.2; регенерированные байты манифеста **байт-в-байт** равны закоммиченным (sha256 `56731402…`, 35 файлов; `manifest create` детерминирован, sort_keys-каноническая форма); vs R1-манифест изменена **ровно одна** запись: RIGHTS.json sha256 `5292781a…` → `a4650b97…` (size 1511 у обеих), top-level поля не менялись |
| 4 | Version-surface тесты: `TestReleaseVersionSurfacesConsistency`, 4 теста | `python3 -m unittest tests.test_release_contract.TestReleaseVersionSurfacesConsistency -v` | **ПОДТВЕРЖДЕНО**: 4 теста, все OK (v0.1.2 полное согласие; v0.1.0 историческая согласованность; v0.1.1 stale-pin immutable; manifest↔VERSION для каждого `releases/nanolab-components-*`) |
| 5 | Байтовая идентичность науки v0.1.1 ↔ v0.1.2 (36=36; 6 изменённых; 27 научных идентичны) | Собственный скрипт: os.walk обоих деревьев, sha256 по каждому файлу, excl `__pycache__`/`*.pyc`; сравнение множеств и дельт | **ПОДТВЕРЖДЕНО**: множества файлов идентичны (36 = 36); изменено ровно 6: `VERSION`, `README.md`, `CITATION.cff`, `reproduction/README.md`, `RELEASE_MANIFEST.json`, `RIGHTS.json`; 30 идентичны; научные поверхности (`families/`, `convention/`, `schema/`, `reports/`, `provenance/`) — 27 файлов, **0 изменённых** |
| 6 | Свежий экспорт: `git archive HEAD` → self-test exit 0; verify ok 35/0; plan ok 5 планов; RIGHTS = 0.1.2 в экспорте | `git archive --format=tar 9988782` → чистый tmp → `reproduce.py self-test`; чтение RIGHTS из экспорта | **ПОДТВЕРЖДЕНО**: exit 0; `verify.ok=true, files=35, errors=[]`; `plan.ok=true, plans=5`; `RIGHTS.package_version=0.1.2` в свежем экспорте |
| 7 | Гейты: package ok; manifest verify ok 35; unittest 612 OK; work_cli validate EX ok; check-consistency ok; workflow_lint blocking=0; 52/52 EX-* | Все команды выполнены в клоне на exact HEAD (полный список — §5) | **ПОДТВЕРЖДЕНО**: package ok (0 warnings, 5 карточек); manifest verify ok 35 файлов; **612 тестов OK** (56.2 c); work_cli EX-NL5-V012 ok (HANDOFF_COMPLETED, `has_post_terminal_corrections=true` — принимается); check-consistency ok (эхо-пин head/tree совпал); workflow_lint ok, blocking=0; **52 каталога EX-*, 0 сбоев** |
| 8 | Governance: терминал 0003 HANDOFF_COMPLETED до R2; 0004 = post-terminal CONTINUATION_CHECKPOINT позже терминала; старые события не редактированы; соответствие convention | Byte-compare блобов событий 0001–0003 vs `3b3de38`; timestamps; чтение `work_cli.py` (класс CORRECTIONS_EVENTS, правило «corrections не раньше терминала»); `work_cli validate` | **ПОДТВЕРЖДЕНО**: блобы 0001 (`72edd99b…`), 0002 (`14890395…`), 0003 (`29a3d54d…`) идентичны `3b3de38`; 0003 ts `2026-10-10T15:45:00Z` < 0004 ts `2026-10-11T13:06:00Z`; 0004 ∈ `CORRECTIONS_EVENTS={CONTINUATION_CHECKPOINT, REVIEW_CORRECTIONS}`, не-помеченные post-terminal события = hard error, правило «не раньше терминала» соблюдено; `work_cli validate` ok (`has_post_terminal_corrections=true`) |
| 9 | Границы: FROZEN_R2 артефакты не тронуты; state-файлы не менялись; 0 научных запусков в diff | Сравнение блобов base vs HEAD; `git diff --name-status` (50 файлов, полная классификация); скан diff на сырые данные/ресюи движка | **ПОДТВЕРЖДЕНО**: `NANOLAB_REPRO_V0_2_FROZEN_R2.md` (`48357196…`), `repro-v0-2-freeze-contract-FROZEN_R2.json` (`d6a9ccde…`), `repro-v0-2-seed-record-FROZEN_R2.json` (`0164e0e3…`) — блобы идентичны base/HEAD; `project/state.json` (`b8197557…`), `project/infra-state.json` (`5056b8f5…`) — не менялись; diff состоит только из: v0.1.2-пакета, docs/work (WO, WORK_QUEUE, EX-запись), `card_lint.py`, `test_release_contract.py`; сырых данных/артефактов движка нет; **научных запусков 0** |

## 3. Дополнительно проверено

- Отрицательный контроль fail-closed сохранён: список файлов для verify берётся
  из манифеста, фактический — из `_package_files`; `.pyc`, внесённый в манифест,
  породит «manifest lists missing file» (послабления fail-closed нет).
- `WORK_QUEUE.md` — только append-only запись о WO/R2-обновлении; `summary.md`
  — R1-снимок + append-only R2-дополнение (см. m-1).
- `check-consistency` эхо-пины (`head=9988782…`, `tree=c8fabd59…`) совпали с пинами обзора.

## 4. Находки

### M-* (блокирующие)
Отсутствуют.

### m-* (минорные, не блокируют)
- **m-1** — `EX-NL5-V012-PACKAGING-PYC-REPAIR-R1/summary.md`, раздел «Что сделано»
  п.3 (R1-снимок) всё ещё утверждает «RIGHTS … байт-в-байт идентичны» и «5
  packaging-поверхностей». Это осознанный append-only формат: в том же файле ниже
  есть «ОБНОВЛЕНИЕ R2», явно исправляющее утверждение (6 поверхностей, RIGHTS
  0.1.0→0.1.2), и WORK_QUEUE/event 0004 согласованы. Расхождения машинных
  артефактов нет; рекомендация — при следующих правках summary не копировать
  R1-формулировки без ссылки на R2-дополнение.

## 5. Реестр выполненных гейтов (точные команды, exit-коды)

| Команда (cwd = клон на 9988782) | Результат |
|---|---|
| `python3 releases/nanolab-components-v0.1.1/reproduction/reproduce.py verify` (на `git archive 8bf7e3a`) | exit 3; 7 ошибок pycache (ожидаемо, claim 1) |
| `PYTHONPATH=scripts python3 -m release.card_lint package releases/nanolab-components-v0.1.2` | exit 0, ok, 0 warnings |
| `PYTHONPATH=scripts python3 -m release.card_lint manifest verify releases/nanolab-components-v0.1.2` | exit 0, ok, 35 файлов |
| `PYTHONPATH=scripts python3 -m release.card_lint manifest create <tmp-копия>` + `cmp` | exit 0; байты идентичны закоммиченному манифесту |
| `python3 -m unittest tests.test_release_contract.TestReleaseVersionSurfacesConsistency -v` | 4 теста OK |
| `python3 -m unittest discover -s tests -t .` | **612 тестов OK**, exit 0 (~56 c) |
| `PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-V012-PACKAGING-PYC-REPAIR-R1` | exit 0, ok, HANDOFF_COMPLETED |
| `PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .` | exit 0, ok, 0 errors / 0 warnings |
| `PYTHONPATH=scripts python3 -m harness.workflow_lint --root .` | exit 0, ok, blocking=0 |
| `work_cli validate docs/work/executions/EX-*` (цикл по всем) | 52 каталога, **0 сбоев** |
| `python3 releases/nanolab-components-v0.1.2/reproduction/reproduce.py self-test` (на `git archive 9988782`) | exit 0; verify 35/0; plan 5/5 |

## 6. Вердикт и потолок претензий

**VERDICT: PASS.** Все девять групп утверждений воспроизведены независимо в
свежем клоне; расхождений с заявленными пинами/хешами не обнаружено; блокирующих
находок нет.

**Claim ceiling:** данный вердикт распространяется **исключительно на
упаковку релиза v0.1.2** (корректность манифеста, метаданных версий, байтовую
идентичность научных поверхностей относительно v0.1.1, целостность governance-
записи). Он **не** подтверждает и не усиливает никаких научных утверждений
пакета (значения огибающих, классификации воспроизведения и т.п. наследуют свой
прежний статус и остаются вне потолка настоящего обзора). Научные запуски в ходе
обзора: **0**. Слияние = Human Gate (владелец репозитория), что данным обзором
не исполняется.

Подписи пинов обзора: `reviewed_head = 998878236a1f06995f837ba1dac583eee3a68f0e`,
`reviewed_tree = c8fabd597a9adac87bbb5c9b39a695e202c65a62`. Машинный дубликат —
`FRESH_SCIENTIFIC_RELEASE_REVIEW_R2.json` рядом с этим файлом.
