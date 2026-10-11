# FRESH VERIFY — U2 OUTENEMY EXECUTOR READINESS R1 (PR #55, финальное состояние)

- `record_kind`: VERIFIER_VERDICT · `issuer_class`: INDEPENDENT_VERIFIER
- **verdict: VERIFIED** (0 блокирующих замечаний)
- **verified_head:** `ead9c256a5d1f26a2b9d43637b54a192d60da691`
- **verified_tree:** `76c9c63fac73cc1a39042549833a9b42ee2fce62`
- Ветка субъекта: `infra/u2-outenemy-executor-readiness-r1`; база: `main` @ `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad`
- Дата верификации: 2026-10-11T12:07:29Z · хост верификации: `outenemy` (закреплённая платформа U2)

## Метод

Свежий клон во временном каталоге (`/tmp/verify-u2-readiness-r1/clone`) из локального origin
(`/home/rdpuser/NanoLab/.git-store/repo.git`) со свежим `git fetch`; повторное использование
существующих worktree исключено. Все пины, родства, диффы, blob-SHA и машинные гейты
пересчитаны в этой сессии независимо. Ничего не ремонтировалось, ничего не мержилось,
форс-пушей нет, подтверждающей научной работы нет.

## Пины и происхождение (пересчитано)

| Величина | Ожидание | Пересчитано | Итог |
|---|---|---|---|
| HEAD ветки | `ead9c256…da691` | `ead9c256a5d1f26a2b9d43637b54a192d60da691` | ✓ |
| Дерево HEAD | `76c9c63f…ce62` | `76c9c63fac73cc1a39042549833a9b42ee2fce62` | ✓ |
| `main` | `8bf7e3a0…c4ad` | `8bf7e3a0dec5c3898cdc920f78d94d03b927c4ad` | ✓ |
| merge-base(main, HEAD) | = tip main | `8bf7e3a0…c4ad` | ✓ |
| Строгое происхождение от main | да | впереди на 8 коммитов, позади на 0; `main` — предок HEAD | ✓ |

## Цепочка сохранности (chain-of-custody)

1. **Независимый ревью — PASS.** Ветка `review/infra3-u2-outenemy-readiness-r1` @
   `d588e2aa43a84e58736de2c737ca5f67dc6074f6`; в
   `docs/evidence/INFRA3-U2-READINESS/FRESH_REVIEW_U2_READINESS_R1.json`:
   `verdict=PASS`, `blocking_findings=[]`, привязка `reviewed_head=9ded2bf7c230781111c9d90008502cbd8271aa45`,
   `reviewed_tree=520c0e9245a405c0acab163bcfa1897c68fabeb9`. Дерево `9ded2bf7` пересчитано —
   совпадает (`520c0e92…beb9`).
2. **Родство.** `9ded2bf7` — предок `ead9c25`; tip ревью-ветки `d588e2a` — предок `ead9c25`;
   интеграционный merge `8afe8ae` присутствует в `git log --merges` и приводит ровно два файла
   ревью-вердикта (`.md` + `.json`).
3. **m-1 узкий ремонт.** `5ce0a63` меняет ровно `scripts/r2/cli.py` +
   `tests/test_r2_activation_tooling.py`. Дифф по `cli.py` — только guard некорректного спека:
   оборачивание построения ledger/executor/spec в `try/except (KeyError, TypeError, ValueError)`
   с именованным отказом `BLOCKED_MALFORMED_SPEC` (exit 3) и валидация argv
   (`command` — список строк/чисел без bool). Семантика цепочки безопасности не тронута.
4. **Книжный коммит.** `git diff 8afe8ae..ead9c25 --stat`: ровно 2 файла —
   `docs/work/WORK_QUEUE.md` (+1/−1) и событие
   `EX-INFRA3-R2-TOOLING-REPAIR-R1/events/0004-continuation-fresh-review-pass-integrated.json` (+11).
   Пост-терминальные коррекции 0004 — легитимная книжная запись, машинно валидируются.
5. **Инвариант цепочки безопасности.** `git diff 9ded2bf7..HEAD -- scripts/r2/fingerprint.py
   scripts/r2/engine_build.py scripts/r2/supervisor.py scripts/r2/executor.py` — **пуст**.
   Пост-ревью-набор коммитов исчерпывающ: `5ce0a63`, `8afe8ae`, `ead9c25` (+ сам вердикт ревьюера
   `d588e2a`, вошедший merge'ем). Ничего сверх этого.

## Результаты проверок

### 1. Целостность ревью-цепочки — PASS

См. chain-of-custody выше: вердикт PASS с корректной привязкой, оба пина ревью — предки
финального HEAD, пост-ревью-коммиты точно соответствуют заявленным, m-1-ремонт не выходит за
границу guard'а, файлы цепочки безопасности с ревью-HEAD (`9ded2bf7`) не менялись.

### 2. Машинные гейты на финальном HEAD — PASS

| Гейт | Результат |
|---|---|
| `python3 -m unittest discover -s tests -t .` | **Ran 631 tests — OK**, exit 0 (57.3 с) |
| `work_cli validate EX-INFRA3-R2-TOOLING-REPAIR-R1` | `ok: true`, exit 0; `has_post_terminal_corrections=true` (событие 0004 — ожидаемо и легитимно) |
| `work_cli validate EX-INFRA3-U2-OUTENEMY-READINESS-R1` | `ok: true`, exit 0 |
| `work_cli validate` по всем `docs/work/executions/EX-*` | **53 каталога, 0 отказов** |
| `harness.cli check-consistency --root .` | `ok: true`; инструмент сам пересчитал head/tree = пины верификации |
| `harness.workflow_lint --root .` | `ok: true`, violations=0, **blocking=0** |

### 3. Живые негативные контроли U2-диспетча на этом хосте — PASS

Хост `outenemy` — закреплённая U2-платформа, поэтому `NOT_ELIGIBLE` по U1 — канонический
корректный контроль (не «дефект», не «чинить»).

- `r2.cli check-host` → `NOT_ELIGIBLE`, **exit 2** (hostname forbidden as author host). ✓
- `r2.cli run --spec <tmp> --ledger <tmp>` → `BLOCKED_HOST`, **exit 2**, ledger не создан —
  U1-guard на финальном состоянии цел. ✓

### 4. Цепочка безопасности run-u2 в коде на HEAD — PASS

- `validate_u2_host` (fingerprint.py:186): нативный платформенный пол (Linux, `virtualization=none`,
  без WSL-маркера, нативная корневая ФС, systemd) + hostname закреплён политикой
  (case-insensitive, неизвестный хост — fail-closed) + хост обязан проваливать `validate_native_u1`
  (+ защитная проверка, что у закреплённого хоста причина отказа по U1 — именно hostname-политика). ✓
- Без `--dispatch-authority` → `BLOCKED_NO_DISPATCH_AUTHORITY`, **exit 3** — подтверждено кодом,
  юнит-тестом и живым контролем на этом хосте (outenemy проходит проверку U2-роли и упирается
  ровно в этот гейт; ledger не создаётся). ✓
- Не-fixture-план → `BLOCKED_LAUNCH_GATE_PROTECTED_WRITER`, exit 3 (код + тест). ✓
- Спек обязан содержать `"fixture": true` буквально → иначе `BLOCKED_NON_FIXTURE_SPEC`, exit 3. ✓
- Префикс `EX-NL5-REPRO-V0-2*` → `BLOCKED_FROZEN_CAMPAIGN_ID`, exit 3 (код + тест). ✓
- Ledger append-only: `AttemptLedger` открывает файл только в режиме `"a"`, повторный
  `attempt_id` → `AttemptReuseError` (юнит-тесты, вкл. случай после сбоя). ✓
- `scientific_outcome` всегда `NOT_EVALUATED`: константа в `contract.py`, дефолт `AttemptRecord`,
  жёстко прописан в записи executor'а и `exit.json`; пути переопределения нет. ✓
- Тесты существуют и проходят в составе 631 OK: класс `U2DispatchPathTest` — 9 тестов
  (end-to-end fixture dispatch, missing-authority, non-fixture-authority, invalid-authority,
  non-fixture spec, frozen campaign id, malformed spec (m-1), non-U2 host, CLI subprocess host guard). ✓

### 5. Замороженная наука и каноническое состояние vs main — PASS

Blob-SHA (`git ls-tree`/`git rev-parse`) идентичны на HEAD и `main`:

| Файл | Blob-SHA |
|---|---|
| `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` | `4835719622bae49a8e8b480536a482b4b222d408` |
| `…/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-freeze-contract-FROZEN_R2.json` | `d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b` |
| `…/EX-NL5-V02-DIRECTOR-FREEZE-R2/evidence/repro-v0-2-seed-record-FROZEN_R2.json` | `0164e0e3f5dda6dbf63174df3730b1bd921d2c76` |
| `project/state.json` | `b819755783119ecc56be50cab1bc736c09c85b24` |
| `project/infra-state.json` | `5056b8f539d51ddb0e3b6a3d33c931b91e29885d` |

Научных прогонов в диффе ветки: **0** (исполнений движка нет; файлов сырых данных
(`raw/data/results`, `*.npy/*.h5/*.csv/...`) в диффе нет). Всего изменённых файлов: 34 —
только docs, `scripts/r2/*`, `tests/`.

### 6. Покрытие scopes — PASS

`git diff --name-only 8bf7e3a..HEAD` (34 файла) полностью покрыт `allowed_paths` двух паспортов:
- `EX-INFRA3-R2-TOOLING-REPAIR-R1`: все `scripts/r2/*` (6 файлов) + `tests/test_r2_activation_tooling.py`;
- `EX-INFRA3-U2-OUTENEMY-READINESS-R1`: собственные docs-поверхности;
- общие поверхности (`docs/evidence/INFRA3-U2-READINESS/**`, `docs/work/WORK_QUEUE.md`,
  `docs/infra/U2_OUTENEMY_EXECUTOR_READINESS_R1.md`) объявлены в обоих паспортах.
- **Непокрытых файлов: нет.**

## Неблокирующие замечания

1. **m-2 (принято ревью, отложено по дизайну):** исполняемый argv fixture-команды берётся из
   спека оператора и не ограничен whitelist'ом; безопасность держится на пиннинге хоста +
   обязательной dispatch-authority + fixture-потолке + отказе по frozen-campaign-id +
   `NOT_EVALUATED`. Пиннинг ожидаемого argv/digest корректно отложен до WO замороженной кампании.
2. `run-u2` без обязательных CLI-путей (`--contract/--protocol/--seed-record/--repo-root`)
   падает на argparse с usage-ошибкой (exit 2) до именованных гейтов — fail-closed, дырой не является.

## Вердикт

**VERIFIED.** Финальное состояние PR #55 (`ead9c25…` / `76c9c63…`) соответствует заявленному:
цепочка «ревью PASS → m-1 узкий ремонт → интеграция → книжные коррекции» исчерпывающе
подтверждена, все машинные гейты зелёные, цепочка безопасности run-u2 цела (U1-guard не
ослаблен), замороженная наука и каноническое состояние не тронуты, научных прогонов 0,
scopes соблюдены. Блокирующих находок нет.
