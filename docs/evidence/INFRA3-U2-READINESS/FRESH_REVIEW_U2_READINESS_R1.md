# FRESH_REVIEW_U2_READINESS_R1 — Независимый fresh-review ветки `infra/u2-outenemy-executor-readiness-r1` (PR #55)

- `record_kind`: REVIEWER_VERDICT (machine-readable двойник: `FRESH_REVIEW_U2_READINESS_R1.json`)
- `issuer_class`: INDEPENDENT_REVIEWER (свежая агентная сессия без предыдущего контекста)
- Дата обзора: 2026-10-11
- Вердикт: **PASS** (0 блокирующих находок M-*; 2 малых находки m-1, m-2 — не блокируют)

## 0. Пины объекта обзора и метод

| Пин | Значение | Проверка |
|---|---|---|
| reviewed_head | `9ded2bf7c230781111c9d90008502cbd8271aa45` | `git rev-parse origin/infra/u2-outenemy-executor-readiness-r1` после свежего `git fetch origin` = заявленный HEAD; локальный checkout этого SHA |
| reviewed_tree | `520c0e9245a405c0acab163bcfa1897c68fabeb9` | `git rev-parse 'HEAD^{tree}'` = заявленному дереву |
| base | `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad` (main, merge PR #52) | `git rev-parse origin/main` = заявленному base |
| merge-base(base, HEAD) | `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad` | `git merge-base` = сам base; `git merge-base --is-ancestor` = base — строгий предок HEAD; `base..HEAD` = 4 коммита (`db816c8` → `79671bc` → `b87d61d` → `9ded2bf`) |

Метод: **свежий temp-dir клон** `/tmp/review-u2-readiness-r1/clone` (создан заново из
origin `/home/rdpuser/NanoLab/.git-store/repo.git`, существующие worktree не
использовались), свежий `git fetch origin` перед всеми проверками. Все тесты и
гейты исполнены в этом чистом клоне; хост исполнения — `outenemy` (по условию
задачи это и есть закреплённая U2-платформа, поэтому `r2.cli check-host` =
NOT_ELIGIBLE здесь — канонический негативный контроль, а не дефект).

## 1. Сводная таблица проверки заявлений (claims 1–8)

| # | Заявление | Метод проверки | Результат |
|---|---|---|---|
| 1 | WO `WO-INFRA3-U2-OUTENEMY-READINESS-R1` / `EX-INFRA3-U2-OUTENEMY-READINESS-R1`: техническая готовность U2 (pinned provenance, smoke, release-пакет v0.1.1 с ровно 7 pyc-findings, systemd user-manager, storage), 0 scientific runs | Чтение WO/passport/events 0001–0004/summary; парсинг всех 8 evidence-JSON; перекрёстные проверки док ↔ evidence ↔ WORK_QUEUE; пересчёт заявленных sha256; live `check-host` из клона | **ПОДТВЕРЖДЕНО.** Все evidence-JSON парсятся; двоичный sha256 `6effd00a…5126b78` (size 3 380 728) и `source_tree_sha256 b1742ce9…22a911c` согласованы в `u2-engine-build-result-R1.json`, `u2-engine-build-provenance-R1.json`, `u2-engine-smoke-R1.json`, доке §2 и строке WORK_QUEUE; pin `00dc7fb9…` = verified=True; pins CMake Release/ON/OFF/OFF verified; smoke exit 0, 4 кадра, «END OF THE SIMULATION…» (явно помечен НЕ научным утверждением); release self-test: ровно 7 ошибок, все 7 — `convention/nlbl_convention/__pycache__/*.pyc`, 0 non-pyc (documented finding); systemd: user-manager RC 0 + active, system manager RC 1, Linger=yes; storage-каталоги `~/nanolab/{workspaces,raw,cache,tools}` существуют на хосте, проекция ~15 GB задокументирована (док §7); claim_class C0_SOFTWARE_ONLY, scientific runs = 0 во всех событиях |
| 2a | Расхождение scope (docs-only паспорт родителя против изменённых `scripts/r2/*`, `tests/test_r2_activation_tooling.py`) закрыто отдельным tooling-WO | Сравнение `allowed_paths` паспорта `EX-INFRA3-R2-TOOLING-REPAIR-R1` и §2 WO-дока с фактическим `git diff --name-only 8bf7e3a..HEAD` | **ПОДТВЕРЖДЕНО.** Паспорт tooling-WO явно включает все 7 изменённых code/test-путей (`scripts/r2/__init__.py`, `cli.py`, `engine_build.py`, `executor.py`, `fingerprint.py`, `supervisor.py`, `tests/test_r2_activation_tooling.py`); объединение паспортов двух WO покрывает все 31 изменённый файл ветки |
| 2b | Родительская история и START checkpoint НЕ переписаны | `git log --follow` на события 0001/0002; `git diff 79671bc..HEAD` на события 0001/0002 + passport.json; сравнение blob-SHA | **ПОДТВЕРЖДЕНО.** `--follow`: 0001 создан только в `db816c8`, 0002 — только в `79671bc`; blob-SHA при `79671bc` и при HEAD идентичны: 0001 = `7b3001a7…`, 0002 = `97c7fa3a…`, passport = `ee47dac…`; diff пуст |
| 2c | Расхождение задокументировано новым родительским CONTINUATION-событием | Чтение `events/0003-continuation-scope-repair-and-u2-dispatch-check.json` | **ПОДТВЕРЖДЕНО.** Event 0003 (CONTINUATION_CHECKPOINT, append-only) явно фиксирует: правки F-1/F-2/F-3 были вне docs-only allowed_paths, расхождение закрыто отдельным WO на той же ветке, паспорт НЕ ретро-редактировался, 0001/0002 не тронуты |
| 3 | F-4: `resolve_engine_binary` fail-closed на неоднозначных case-insensitive совпадениях в `<build>/bin` | Чтение `scripts/r2/engine_build.py:102-137`; тесты | **ПОДТВЕРЖДЕНО.** >1 совпадения по нижнему регистру → `raise FileNotFoundError` с перечнем совпадений (строки 125–130), произвольный выбор исключён; точное имя резолвится детерминированно; тест `test_ambiguous_case_insensitive_bin_matches_are_refused` (+2 смежных) зелёные |
| 4a | `validate_u2_host`: pinned hostname (case-insensitive + short-name), тот же native floor, host НЕ проходит `validate_native_u1`, неизвестный hostname — fail-closed | Чтение `scripts/r2/fingerprint.py:186-259`, `scripts/r2/__init__.py` (`PINNED_U2_HOSTNAMES=("outenemy",)`); тесты `U2HostValidationTest` (7 тестов) | **ПОДТВЕРЖДЕНО.** Тот же native floor (Linux/virt=none/не-WSL/native fs/systemd); hostname обязан совпасть с pinned (full/case-insensitive/short-name), иначе отказ; отдельная причина отказа, если хост прошёл бы U1-валидацию (роли не пересекаются); защитная проверка «pinned-хост, отваливший U1 по неожиданной причине» |
| 4b | Обязательный `--dispatch-authority`: нет → `BLOCKED_NO_DISPATCH_AUTHORITY` exit 3; есть → полная schema-v3 валидация через `build_execution_plan` (Git-bound) | Чтение `scripts/r2/cli.py:105-204`; `scripts/nl5/repro_v02_freeze_contract.py:531,2086,2347+` (файл не менялся веткой); тесты | **ПОДТВЕРЖДЕНО.** Пустой authority → `BLOCKED_NO_DISPATCH_AUTHORITY`, exit 3 (cli.py:170-180); исключение валидации → `BLOCKED_DISPATCH_AUTHORITY`, exit 3; `_DISPATCH_AUTHORITY_SCHEMA_VERSION = 3`, Git-bound lifecycle (реальный F-коммит + Director FREEZE + HG-B + review + verify + R2 ACTIVE); live-проба из evidence: exit 3, ledger не создан |
| 4c | Не-fixture план никогда не исполняется: `BLOCKED_LAUNCH_GATE_PROTECTED_WRITER` exit 3; `machine_launch_authorized` остаётся false; launch gate HUMAN_PROTECTED_WRITER не подменяется | cli.py:193-204; nl5 contract:2330/2416 (`machine_launch_authorized: False`, `launch_gate=_LAUNCH_GATE_HUMAN`); grep по `scripts/r2` | **ПОДТВЕРЖДЕНО.** План без `synthetic_test_fixture_only` → отказ exit 3; в `scripts/r2` нет ни одного присваивания `machine_launch_authorized=True` (значение только читается из плана, где оно конструктивно False); тест `test_non_fixture_authority_never_executes_launch_gate_holds` зелёный |
| 4d | Fixture ceiling: `fixture:true` в spec; `EX-NL5-REPRO-V0-2*` — жёсткий отказ | cli.py:102 (`FROZEN_CAMPAIGN_EXECUTION_ID_PREFIXES=("EX-NL5-REPRO-V0-2",)`), cli.py:151-169; тесты | **ПОДТВЕРЖДЕНО.** `spec_json.get("fixture") is not True` → `BLOCKED_NON_FIXTURE_SPEC` exit 3; префикс замороженной кампании → `BLOCKED_FROZEN_CAMPAIGN_ID` exit 3 «что бы ни говорила authority»; тесты `test_non_fixture_spec_is_refused`, `test_frozen_campaign_execution_id_is_refused_even_with_valid_authority` зелёные |
| 4e | Ledger append-only; `scientific_outcome` всегда NOT_EVALUATED | `scripts/r2/contract.py:115-155` (append-only, повтор attempt_id → `AttemptReuseError`); `scripts/r2/executor.py:197,223` | **ПОДТВЕРЖДЕНО.** Append — единственная мутация; e2e-проба: attempt T001, `scientific_outcome: NOT_EVALUATED` |
| 5 | U1 guard не ослаблен | `git diff 8bf7e3a..HEAD -- scripts/r2/cli.py`, `-- scripts/r2/fingerprint.py`; live-пробы | **ПОДТВЕРЖДЕНО.** `cmd_run`/`cmd_build_engine`/`cmd_gate`/`cmd_nc_verify` не изменены и по-прежнему первыми вызывают `require_u1_or_exit`/`validate_native_u1`; в fingerprint.py дифф чисто аддитивный (1 изменённая строка — импорт), `validate_native_u1` байт-в-байт прежний; дефолт launcher для `run` остался `"systemd"` (system manager), `systemd-user` — только opt-in и единственный недирект-вариант для `run-u2`; нового обходного пути нет: единственный исполняющий путь вне U1 — `run-u2` за собственным U2-гейтом; live-негативный контроль из клона: `check-host` на outenemy → NOT_ELIGIBLE, exit 2; в evidence повторён `r2.cli run` → exit 2 BLOCKED_HOST |
| 6 | FROZEN_R2 артефакты и canonical state не тронуты | `git rev-parse <commit>:"<path>"` для base и HEAD | **ПОДТВЕРЖДЕНО.** Blob-SHA идентичны base↔HEAD: протокол `4835719622…`, contract `d6a9ccde4d…`, seed record `0164e0e3f5…`; `project/state.json` `b819755783…` и `project/infra-state.json` `5056b8f539…` идентичны; под `project/`, `docs/research/`, `docs/control/` изменений нет вообще |
| 7 | Полный набор тестов и гейтов | Свежий клон, этот хост | **ПОДТВЕРЖДЕНО.** `python3 -m unittest discover -s tests -t .` → **Ran 630 tests — OK** (59.9 s, exit 0); `work_cli validate` обоих executions → ok:true, exit 0; `check-consistency` → ok:true (head/tree совпадают с пинами обзора); `workflow_lint` → ok:true, blocking=0; `work_cli validate` по ВСЕМ `docs/work/executions/EX-*` → **53 каталога, 0 неудач** |
| 8 | Внутренняя согласованность evidence (хост-факты до ветки не перепроверяются) | Парсинг JSON; пересчёт sha256; кросс-ссылки док↔WO↔WORK_QUEUE↔evidence | **ПОДТВЕРЖДЕНО.** Все 15 evidence-JSON (обоих executions) парсятся; заявленные в `tooling-repair-validation-R1.json` sha256 шести `scripts/r2/*.py` пересчитаны точно (совпадают и на `b87d61d`, и в worktree; заявленный `subject_tree 646592ec…` = `b87d61d^{tree}`); арифметика тестов сходится (612 + 18 = 630, док §6/§11); event subject_sha согласованы (`8bf7e3a` для 0001/0002, `b87d61d` для 0003/0004) |

## 2. Находки

### Блокирующие (M-*)

Отсутствуют.

### Малые (m-*, не блокируют PASS)

- **m-1** (`scripts/r2/cli.py:210,212,215,216`) — в `cmd_run_u2` после прохождения
  всех гейтов ключи спецификации `run_base`/`command`/`raw_root`/`workspace`
  читаются прямым индексированием `spec_json[...]`: синтетически некорректная
  spec (при валидной authority) вызывает неструктурированный `KeyError`
  (traceback, exit 1) вместо именованного структурированного отказа. По
  безопасности это fail-closed (исполнение не начинается), но диагностически
  грубее остальных отказов цепочки. Рекомендация: валидировать схему spec
  явно, в стиле остальных BLOCKED-ответов.
- **m-2** (`scripts/r2/cli.py:208-218`) — fixture ceiling декларативен: сам
  исполняемый `command` берётся из operator-spec и не ограничен white-listом
  fixture-команд; защитные свойства держатся на пиннинге хоста + обязательной
  authority + fixture-флагах + неизменном `scientific_outcome=NOT_EVALUATED`
  (что и заявлено). Граница честно задокументирована в WO §6 («Честные
  границы») и доке §11; научного повышения полномочий нет. Рекомендация на
  будущее: при подготовке frozen WO кампании зафиксировать в плане
  ожидаемый argv/дайджест fixture-команды.

## 3. Честные границы обзора

- Обзор выполнен в свежем temp-dir клоне при свежем fetch; пины HEAD/tree/base
  установлены независимо (см. §0).
- Аппаратные/хост-факты, предшествующие ветке (сборка ~67 s, smoke, systemd-механика,
  fingerprint-значения), по условию задачи НЕ перепроверяются — проверена
  внутренняя согласованность записей, включая пересчёт всех заявленных
  sha256-дайджестов файлов и кросс-ссылки между документами, событиями,
  WORK_QUEUE и evidence.
- Никаких научных/подтверждающих запусков не выполнялось: только технические
  гейты и юнит-тесты (в т.ч. `run-u2`-тесты на синтетических temp-фикстурах);
  `scientific_runs = 0`.
- Live-проверка с этого хоста: `r2.cli check-host` → NOT_ELIGIBLE, exit 2 —
  канонический негативный контроль (машина = закреплённая U2-платформа, никогда
  не U1); это ожидаемый корректный результат, а не дефект.

## 4. Вердикт

**PASS.** Все восемь групп заявлений подтверждены независимо в свежем клоне;
блокирующих находок нет; U1 guard не ослаблен; родительская история исполнения
не переписана; замороженные научные артефакты байт-в-байт не тронуты; полный
тестовый набор (630) и все гейты зелёные. Малые находки m-1/m-2 —
рекомендации по качеству диагностики и будущей фиксации fixture-команды,
исправление не требуется для слияния (слияние остаётся Human Gate).
