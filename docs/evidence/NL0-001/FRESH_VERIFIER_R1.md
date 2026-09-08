# NL0-001 — Fresh Independent Verifier R1

Исполнение: `EX-NL0-001-R1`. Роль: `VERIFIER` (fresh, независимая сессия; не Implementer, не Reviewer). PR: `rootfabric/NanoLab#11`. Все SHA проверены live в день verification; выводы Reviewer не принимались на веру — все проверяемые факты перепроверены с нуля.

```text
VERIFIED_HEAD        = f738bff77f2406552b4383c05989ffc6e56a3bd5
REVIEWED_HEAD        = f738bff77f2406552b4383c05989ffc6e56a3bd5
REVIEW_HEAD_MATCH    = YES
REVIEW_COMMIT        = e0303aa05bbcc3f6839c3af31d7a28ecbd66a932
CURRENT_MAIN         = f4d2979a1d2502d86c035f25e36961b4d5ac2764
EPOCH_DRIFT          = CONTINUE

VERDICT              = PASS

E1_HASH_CHECK        = PASS
E2_TREE_CHECK        = PASS
HARNESS_CLOSE_CHECK  = PASS
STATE_SAFETY_CHECK   = PASS

NEXT_ACTOR           = DIRECTOR
```

Ветка настоящего отчёта `verify/nl0-001-reference-selection-r1` создана от exact candidate HEAD `f738bff`; файлы кандидата не изменены; PR не смержен; `project/state.json` не тронут; NL0 не закрыт.

## V1 — Candidate / Review binding

- PR #11 live (GitHub API): `state=open`, `head.sha = f738bff77f2406552b4383c05989ffc6e56a3bd5`, `base.sha = 9d8ea394c6c037b0560908689e2ce932bf0c511c`, 4 commits, 13 files. PR HEAD не менялся после Reviewer.
- `origin/work/nl0-001-reference-selection-r1` (fetch) = `f738bff` — совпадает с PR HEAD и REVIEWED_HEAD.
- `origin/review/nl0-001-reference-selection-r1` = `e0303aa` (= REVIEW_COMMIT); цепочка `f738bff → 25c6d19 → f3990dc → e0303aa` подтверждает инициализацию от exact subject.
- Durable PASS: `docs/evidence/NL0-001/FRESH_REVIEW_R1.md` добавлен именно в `e0303aa` и содержит `REVIEWED_HEAD = f738bff…`, `VERDICT = PASS`, `EPOCH_DRIFT = CONTINUE`. Diff review-ветки против кандидата — только 3 review-файла (assignment, status, verdict); candidate tree не тронут Reviewer.

```text
PR_HEAD == REVIEWED_HEAD → OK; REVIEW_STALE не применим.
```

## V2 — E1 independently fetched evidence (oxDNA)

Upstream `lorenzo-rovigatti/oxDNA@00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` существует (API); tree commit = `f03ce1de5c0f3a336cb00ad363686c4841600d10` — совпадает с записанным; license на commit = GPL-3.0 (API).

Четыре файла скачаны независимо (raw.githubusercontent на pinned SHA) и SHA-256 вычислены заново:

| Файл | Размер (live) | SHA-256 (live, независимый) | = INPUT_AVAILABILITY.md |
|---|---:|---|---|
| `test/DNA/DSDNA8/dsdna8.top` | 148 B | `f1aded90b5f6e1d9adab0e55925bba778477467be2957b4093d1264160c03fc4` | да |
| `test/DNA/DSDNA8/init.dat` | 4498 B | `0ff76d541728e0925f199970ff6296254fe6116d23e44fdf0d361d0f8891a9e0` | да |
| `test/DNA/DSDNA8/MD/quick_input` | 533 B | `8935c4bc623ca96d406429c3c5177901f12540ffe61bcd3299931f0689af74a2` | да |
| `test/DNA/DSDNA8/MD/quick_compare` | 51 B | `86a8b6ac50f382ba25e5aacbbef629cc5a1788f44e6c28d113509c8448e3ce27` | да |

Содержание проверено побайтово (файлы прочитаны целиком):

- `dsdna8.top`: заголовок `16 2` — 16 nucleotides / 2 strands (две комплементарные 8-nt цепочки). Подтверждено.
- `quick_input`: `backend = CPU`, `steps = 1e6`, `thermostat = john`, `T = 20C`, `dt = 0.005`, `topology = ../dsdna8.top`, `conf_file = ../init.dat`. Подтверждено дословно.
- `quick_compare`: ровно одна строка `ColumnAverage::energy.dat::2::-1.37970256144::0.15`. Подтверждено дословно; `REFERENCE_SELECTION.md` цитирует oracle без искажений.

E1 physics simulation Verifier-ом не запускался (вне scope WO).

## V3 — E2 exact upstream tree (DNA-hinge-simulations)

Upstream `gauravarya77/DNA-hinge-simulations@23fd1ff7731e9017bd776f49206dc42d70d9fe91` существует; commit tree SHA = `b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9` — совпадает с записанным pinned tree. Pinned commit = HEAD `master` (pushed_at 2017-04-04 = дате commit), т.е. более поздних изменений нет.

Полный recursive tree (API, `truncated=false`, 33 entries) содержит ровно заявленное:

- `Design_Hinges/{0b,11b,32b,53b,74b}.json` — все 5; blob SHA-1 `0ed4075c…`, `7f193697…`, `6adb55af…`, `3ffdb753…`, `776725c1…` и размеры 173059/173145/173315/173481/173595 B совпали с записанными всеми пятью.
- `MD_Hinges/{0b,11b,32b,53b,74b}.top` и `.conf` — все 10 пар; `0b.conf` = 2 294 162 B (≈2.29 MB, как записано).
- `MD_Hinges/pro_CPU.in` (blob `89d76310ce726eaec9e7acb312bd7b0fc43fa735` — совпал) и `pro_GPU.in`.
- `Init_Hinges/` с `cadnano_interface.py`, `init_generator.py`, `ini_demo/…`.

`pro_CPU.in` прочитан целиком; параметры подтверждены дословно:

```text
backend = CPU
backend_precision = double
steps = 2e7
interaction_type = DNA2
salt_concentration = 0.5
T = 300K
```

`pro_GPU.in` проверен дополнительно: `backend = CUDA`, `backend_precision = mixed`, те же DNA2/0.5/`T = 300K`/2e7 — оба авторских входа используют 300 K.

`MD_Hinges/README.md` (pinned SHA) дословно описывает каждый `.conf` как «Input restart file (containing structure and velocity data of an equilibrated hinge)» — заявление о equilibrated/restart structures подтверждено первоисточником.

## V4 — Known discrepancies remain correctly unresolved

1. **298 K (статья) vs 300 K (upstream input):** upstream-сторона проверена независимо и побайтово — оба авторских входа (`pro_CPU.in`, `pro_GPU.in`) задают `T = 300K`. Candidate НЕ «исправил» расхождение: `REFERENCE_SELECTION.md` фиксирует его явно и передаёт явное разрешение в NL0-003; ни одна температура не выбрана молча. Статья-сторона (298 K в Methods) из этого окружения неперечитываема (ACS full text paywalled/bot-blocked; Europe PMC `pmcid=None`, Unpaywall `is_oa=false`) — принимается по full-text-цитате Reviewer и вторичным свидетельствам; для вердикта NL0-001 некритично, т.к. Work Order требует именно зарегистрировать и делегировать конфликт, что сделано.
2. **LICENSE:** полный pinned tree (33 entries) не содержит `LICENSE`/`COPYING`/`NOTICE`; GitHub API `license = None`. Candidate не назначил лицензию и не заявил право копирования: права зафиксированы как UNKNOWN, решение делегировано в NL0-002; upstream data в NanoLab не копировались (в diff кандидата входят только 13 docs/json файлов, ни одного `.top/.conf/.in/.dat`).
3. **S08 (`10.1021/acsnano.7b06470`):** статус записан как `INPUT_PACK_NOT_LOCATED`, не `NO_DATA_EXISTS`; UNKNOWN про непроверенные поверхности и recovery path (запрос авторам) сохранены. Независимый bounded check согласуется: GitHub repo-search «jointed DNA nanostructures» → 0 результатов; Europe PMC — нет PMCID/full-text data-ссылок; статья не OA.

## V5 — Harness execution package

`docs/work/executions/EX-NL0-001-R1/`: `passport.json` (risk `HIGH`, claim `C0_SOFTWARE_ONLY`, base `9d8ea394…`, allowed_paths покрывают все 13 изменённых файлов), `summary.md`, `branch-passport.md`, события 0001–0005 ровно в порядке `WORK_ORDER_STARTED → CONTINUATION_CHECKPOINT → IMPLEMENTATION_COMMITTED → VALIDATION_RECORDED → HANDOFF_COMPLETED`; все `subject_sha` — 40 hex, `execution_id`/`work_order_id` консистентны с паспортом.

Реально выполнено на candidate worktree (`f738bff`):

```bash
python3 scripts/harness/work_cli.py close docs/work/executions/EX-NL0-001-R1
# → ok=true, errors=[], status=HANDOFF_READY, exit 0
```

Predicates `work_cli.py` проверены и кодом, и исполнением: ровно один START, START первый, ровно один terminal/handoff, terminal последний, `summary.md` существует.

## V6 — Scientific state safety

`project/state.json` не изменён кандидатом (diff base→candidate пуст) и на текущем `main`: `NL0-001 = READY`, `completed_tasks = []`, `stage_status.NL0 = PLANNED`, `E0–E6 = NOT_RUN`, `physics_runs = 0`. Нигде не заявлено `NL0 = COMPLETE`, `E1 = PASS` или `E2 = PASS`. Implementer verdict — `HANDOFF CANDIDATE; independent review required`; статус ветки — `HANDOFF_READY`. Self-accept отсутствует; merge не выполнялся.

## V7 — Epoch drift

`9d8ea394… → f4d2979…` (текущий `main`): 12 файлов, все — additive INFRA-линия (`docs/infra/*`, `docs/work/WO-INFRA0-001.md`, `project/infra-plan.json`, `project/infra-state.json`, `docs/evidence/INFRA_ROADMAP_R1_CHECKS.md`) плюс роутинговые вставки в `AGENTS.md`/`PROJECT_CONTROL.md`/`README.md`/`docs/INDEX.md`. Не затронуты `docs/research/**`, `docs/work/WO-NL0-001.md`, `config/control/harness/*`, `project/state.json`, научная методология. Вставки только усиливают разделение INFRA/science. Tip `main` (2026-09-08T04:38:50Z) предшествует review-коммиту (06:24:27Z): после Reviewer новых затрагивающих изменений нет.

```text
EPOCH_DRIFT = CONTINUE
```

## FINDINGS

1. Все проверяемые заявления кандидата подтвердились независимо; ни одного несовпадения хешей, размеров, параметров или структуры tree не обнаружено.
2. Binding точный: review относится к текущему PR HEAD; durable PASS на review-ветке корректен.
3. Claim ceiling не завышен: DSDNA8 ограничен `C1_COMPUTATIONAL_REPRODUCTION`, C4 прямо отрицается.
4. Отрицательные результаты (S08 pack not located; E2 LICENSE unknown) сохранены и корректно делегированы (NL0-002/NL0-003) без самовольного «исправления» научных данных.
5. Harness-trail полон и воспроизводим; `close` даёт `ok=true`.

## LIMITATIONS

1. ACS full text обеих статей (`7b00242`, `7b06470`) из этого окружения недоступен (paywall/bot-block); статья-сторона 298 K и перечисление SI S08 приняты по full-text-цитате Fresh Reviewer + вторичным поверхностям (Crossref/PubMed/SEMANTIC SCHOLAR metadata, GitHub search 0, Europe PMC no-PMCID). Upstream-сторона 300 K проверена побайтово.
2. Размер Zenodo record `8248808` (46.2 GB) не перепроверялся — не является зависимостью NL0-001.
3. E1 physics simulation не запускался Verifier-ом (по условиям Work Order).
4. Предикаты `work_cli.py` исполнялись в worktree на exact `f738bff`; локальная среда доступна, поэтому limitation «локальная среда недоступна» не применяется.

## Next actor

`DIRECTOR` (HIGH: Implementer + Reviewer PASS + Verifier PASS). Решение о merge PR #11 и закрытии только `NL0-001` — Human Gate; настоящий verification не авторизует merge и не закрывает NL0.
