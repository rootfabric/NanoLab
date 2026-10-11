# FRESH INDEPENDENT VERIFICATION R2 — PR #56 (release v0.1.2 packaging)

- `record_kind`: FRESH_VERIFY (R2)
- `issuer_class`: INDEPENDENT_VERIFIER (новая агентская сессия, без предшествующего контекста)
- Дата верификации: 2026-10-11 (`timestamp_utc`: `2026-10-11T12:11:01Z`)
- Хост верификации: `outenemy` (закреплённая платформа U2) — допустимо для технической
  верификации; научные/подтверждающие работы НЕ запускались, выполнены только
  технические гейты.
- Ремонт/мерж/force-push не выполнялись; платные сервисы не использовались.

## 0. Заявление о свежести

Верификация выполнена в полностью новом клоне `/tmp/verify-v012-r2/clone`,
созданном в этой сессии командой `git clone` из локального origin
`/home/rdpuser/NanoLab/.git-store/repo.git`, с обновлением
`git fetch origin 'refs/heads/*:refs/remotes/origin/*'`. Существующие
worktree/каталоги не использовались; все числа ниже пересчитаны самостоятельно
(собственный скрипт `cmp_releases.py`, собственные команды git/python), а не
взяты из evidence-файлов ветки или отчёта ревьюера.

## 1. Пины субъекта верификации (exact pins) — ПОДТВЕРЖДЕНЫ

| Поле | Пересчитанное значение | Метод |
|---|---|---|
| branch | `work/nl5-v012-packaging-pyc-repair-r1` | `git ls-remote origin` |
| `verified_head` | `998878236a1f06995f837ba1dac583eee3a68f0e` | `git rev-parse origin/work/nl5-v012-packaging-pyc-repair-r1` == заявленному пину |
| `verified_tree` | `c8fabd597a9adac87bbb5c9b39a695e202c65a62` | `git rev-parse 9988782^{tree}` == заявленному пину |
| base (main) | `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad` | `git rev-parse origin/main` |
| merge-base | `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad` (== main) | `git merge-base subject origin/main` |
| Строгое происхождение | main — строгий предок HEAD; HEAD не предок main | `git merge-base --is-ancestor` (оба направления) |
| Коммиты ветки | `d4d56a3` → `e7d5081` (R1 fix) → `3b3de38` (handoff R1) → `e72dc4b` (R2 fix RIGHTS) → `9988782` (R2 record) | `git log --oneline 8bf7e3a..9988782` |

## 2. Review-chain — ПОДТВЕРЖДЕНА

- Ветка ревью: `review/nl5-v012-packaging-r2`, tip = `0c9dcf17bcc7ee1268295dd83f6efcc3be285e53`.
- Родитель review-коммита — ровно `9988782` (`git cat-file commit`): review-ветка
  строго происходит от субъекта HEAD.
- HEAD НЕ опережает отревьюированный субъект: tip рабочей ветки на origin
  (`refs/heads/work/nl5-v012-packaging-pyc-repair-r1` = `9988782`) совпадает с
  `reviewed_head` — post-review коммитов на ветке нет.
- `docs/evidence/NL5-V012-RELEASE/FRESH_SCIENTIFIC_RELEASE_REVIEW_R2.json`:
  `record_kind=REVIEWER_VERDICT`, `issuer_class=INDEPENDENT_REVIEWER`,
  `verdict=PASS`, `reviewed_head=9988782…`, `reviewed_tree=c8fabd5…` — все
  значения совпадают с моими пересчитанными пинами. MD-файл ревью согласуется.

## 3. Результаты независимых проверок (1–6)

### Проверка 1 — байтовое сравнение v0.1.1 vs v0.1.2 — PASS

Собственный скрипт (sha256 по каждому файлу, исключая `__pycache__`/`*.pyc`),
плюс контрольный `diff -r -x __pycache__ -x '*.pyc'`:

- файловых наборов: **36 = 36**, наборы идентичны (0 только-в-v0.1.1, 0 только-в-v0.1.2);
- изменённых поверхностей — ровно **6**: `CITATION.cff`, `README.md`,
  `RELEASE_MANIFEST.json`, `RIGHTS.json`, `VERSION`, `reproduction/README.md`;
- идентичных поверхностей: 30; из них **научных 27/27 байт-идентичны**
  (`families/`, `convention/`, `schema/`, `reports/`, `provenance/`),
  научных изменённых: **0**.

### Проверка 2 — версионные поверхности — PASS

- **v0.1.2**: `VERSION` = `0.1.2`; `RIGHTS.json.package_version` = `0.1.2`;
  `RELEASE_MANIFEST.json.package_version` = `0.1.2` — консистентно (3×0.1.2).
- **Исторический v0.1.0** (каталог `releases/nanolab-components-v0.1`):
  `VERSION`/`RIGHTS`/`MANIFEST` = `0.1.0` ×3 — полностью консистентен.
- **Исторический v0.1.1**: `VERSION` = `0.1.1`, `MANIFEST` = `0.1.1`,
  `RIGHTS` = `0.1.0` (известный исторический дефект метаданных, задиагностирован
  в evidence R2; v0.1.2 его унаследовал и починил — см. коммит `e72dc4b`).
  **Неизменяемость v0.1.1**: `git ls-tree -r` каталога v0.1.1 идентичен на main
  (`8bf7e3a`) и на HEAD (`9988782`) — sha256 вывода ls-tree совпадает
  (`9549f2403b52ec983dae5a86e46a97c509d2dc7020ff94f3242ee0026dbacca6` в обоих
  случаях); `git diff` по каталогу пуст. Дополнительно каталог v0.1 (v0.1.0)
  тоже идентичен на main и HEAD (`9375b2e2…`). Иммутабельные релизы не тронуты.

### Проверка 3 — детерминизм манифеста — PASS

- Во временной копии v0.1.2 (`cp -a` в `/tmp/verify-v012-r2/pkg-copy`) выполнено
  `PYTHONPATH=<clone>/scripts python3 -m release.card_lint manifest create`:
  `ok=true`, 35 файлов, exit 0.
- Регенерированный `RELEASE_MANIFEST.json` **байт-в-байт** равен закоммиченному:
  sha256 обоих `567314026bd1b2157cddd9b3831a5990cdad0862b0a15c0f22004c6c9e0f122b`
  (`cmp` — без различий).
- `manifest verify` на закоммиченном пакете: `ok=true`, **35 файлов, 0 ошибок**, exit 0.
- В закоммиченном манифесте v0.1.2 **0** записей `__pycache__`/`*.pyc`
  (у v0.1.1 исторически их было 7 — R1-дефект; в v0.1.2 исправлено).

### Проверка 4 — self-test свежего экспорта — PASS

- `git archive --format=tar 9988782…` → чистая распаковка в пустой tmp.
- `RIGHTS.json.package_version` в экспорте = **0.1.2**.
- `python3 releases/nanolab-components-v0.1.2/reproduction/reproduce.py self-test`:
  **exit 0**; `verify` ok: **35 файлов, 0 ошибок**; `plan` ok: **5 планов**
  (4 MEASURED + 1 NOT_MEASURED/KNOWN_GAP); общий `ok: true`.

### Проверка 5 — гейты в свежем клоне — PASS

| Гейт | Команда | Результат |
|---|---|---|
| Полный unittest-набор | `python3 -m unittest discover -s tests -t .` | **Ran 612 tests — OK**, exit 0 (≈56 c) |
| work_cli: subject EX | `… work_cli validate docs/work/executions/EX-NL5-V012-PACKAGING-PYC-REPAIR-R1` | ok; `HANDOFF_COMPLETED`; события `WORK_ORDER_STARTED → CONTINUATION_CHECKPOINT → HANDOFF_COMPLETED → CONTINUATION_CHECKPOINT`; correction-событие **0004 после терминала 0003** присутствует и легитимно (append-only, класс corrections принимается валидатором) |
| work_cli: все EX-* | цикл по `docs/work/executions/EX-*` | **52 каталога, 0 провалов** |
| check-consistency | `… harness.cli check-consistency --root .` | ok; 0 ошибок, 0 предупреждений; эхо head `9988782…` / tree `c8fabd5…` |
| workflow_lint | `… harness.workflow_lint --root .` | ok; workflows=1, **blocking=0** |
| card_lint package | `… release.card_lint package releases/nanolab-components-v0.1.2` | ok; 5 карт (4 MEASURED, 74b NOT_MEASURED); warnings=0, exit 0 |

### Проверка 6 — границы — PASS

- **Замороженные артефакты** (blob SHA по `git rev-parse`, HEAD == main):
  - `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` = `4835719622bae49a8e8b480536a482b4b222d408` — SAME;
  - `EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-freeze-contract-FROZEN_R2.json` = `d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b` — SAME;
  - `EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-seed-record-FROZEN_R2.json` = `0164e0e3f5dda6dbf63174df3730b1bd921d2c76` — SAME.
- **Файлы состояния**: `project/state.json` = `b8197557…` и
  `project/infra-state.json` = `5056b8f5…` — идентичны main.
- **Диф ветки** (`main..HEAD`): только `docs/work` (WO, WORK_QUEUE, запись
  EX-NL5-V012-PACKAGING-PYC-REPAIR-R1 с 4 событиями и evidence), новая копия
  пакета `releases/nanolab-components-v0.1.2`, `scripts/release/card_lint.py`,
  `tests/test_release_contract.py`. Расширения — только текстовые
  (`.py/.json/.md/.txt/.cff` + extensionless `VERSION`); путей с raw-данными /
  выводами движка нет. **Научных запусков в дифе: 0** (упоминания `oxdna` в дифе —
  текст внутри легитимных упаковочных файлов, байт-идентичных v0.1.1).
- **R1-дефект остаётся исправленным**: в `scripts/release/card_lint.py`
  `_package_files` (L173–189) — единая точка (choke point): фильтр
  `p.name != RELEASE_MANIFEST.json and "__pycache__" not in p.parts and p.suffix != ".pyc"`;
  используется и в `manifest_create` (L222), и в `manifest_verify` (L259).
  Проверено вживую: подсаженный в копию пакета `__pycache__/x.cpython-310.pyc`
  не меняет verify (ok, 35 файлов) и не попадает в регенерированный манифест
  (байт-идентичен закоммиченному); контрольная порча трекаемого файла →
  verify fail-closed (exit 3, 2 ошибки).

## 4. Вердикт верификатора

**VERDICT: VERIFIED**

Все проверки 1–6 пройдены на пересчитанных данных; review-chain подтверждена
(review PASS привязан ровно к субъекту HEAD, post-review коммитов нет); научный
дрифт отсутствует (27/27 научных поверхностей байт-идентичны v0.1.1);
манифест детерминирован; иммутабельные релизы v0.1/v0.1.1 не тронуты; границы
соблюдены; все гейты зелёные; научных запусков 0.

Замечание (не блокирующее): минорная находка ревью m-1 (секция R1 в `summary.md`
EX-записи словесно устарела относительно R2-дополнения в том же файле)
воспроизводится и остаётся некритичной — машинные артефакты консистентны.

Мерж — Human Gate (не выполнялся данным верификатором).
