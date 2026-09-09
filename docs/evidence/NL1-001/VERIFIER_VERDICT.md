# NL1-001 — Независимый вердикт VERIFIER (R1)

**VERDICT: PASS** (1 finding severity MINOR; не блокирует)

- Верификатор: независимая fresh session, fresh clone, без доступа к контексту implementer'а.
- Дата верификации: 2026-09-09.
- Метод: только воспроизводимые команды (pwsh Windows git 2.53.0 + WSL2 Ubuntu 24.04.2, git 2.43.0) и факты из Git; байт-точные операции — `git show`/`git archive` через cmd/bash-редирект (PowerShell-пайплайны не использовались для хэширования).
- Вердикт не выставляет ACCEPTED и не является merge-решением: merge в `main` — Human Gate.

## Exact subject

| Факт | Значение | Проверка |
|---|---|---|
| Remote branch | `work/nl1-001-env-pin-smoke-r1` = `39b34486b2cc156aab60add9f098885c15c51701` | `git ls-remote https://github.com/rootfabric/NanoLab work/nl1-001-env-pin-smoke-r1` |
| Проверяемый HEAD | `39b34486b2cc156aab60add9f098885c15c51701` (совпадает с ls-remote) | fresh clone `C:\NanoLab\verify-nl1-001` → `git checkout 39b3448`, detached HEAD, без рабочей ветки |
| Base WO | `57c1e63733ea3b10f991c0f9609c426dc75b17a5` | `git merge-base --is-ancestor 57c1e63… 39b3448` → exit 0 (ancestor подтверждён); `57c1e63..39b3448` = 3 коммита: `dd4692d` (START) → `60db6b7` (substantive) → `39b3448` (только `events/0004-handoff-completed.json` — привязка terminal event к subject) |

## Проверки

### a) Diff scope — OK

Команда: `git diff --name-status 57c1e63733ea3b10f991c0f9609c426dc75b17a5 39b3448`.

Факт: 14 путей, все попадают в `allowed_paths` passport.json:

```text
A  docs/evidence/NL1-001/IMPLEMENTER_EVIDENCE.md
A  docs/evidence/NL1-001/smoke-run/{energy.dat, log.dat, quick_input_smoke, time.log}
A  docs/research/ENGINE_ENVIRONMENT_R1.md
M  docs/work/SESSION_LOG.md
A  docs/work/WO-NL1-001.md
A  docs/work/executions/EX-NL1-001-R1/{passport.json, summary.md, events/0001..0004}
```

Ограниченные поверхности не изменены: `git diff --name-only <base> <head> -- project/state.json project/plan.json config/ docs/research/E1-PROTO_R1.md` → пусто; blob-идентичность подтверждена `git ls-tree` на обоих коммитах: `project/state.json` = `16ddcc9d`, `project/plan.json` = `c3e854da`, `config/control/harness/scheduler-policy.v1.json` = `bbe3cf10`; E1-протокол (`docs/research/PREREGISTRATION_E1_R1.md`) = blob `e04c6882` в обоих коммитах (идентичен).

### b) Fixture-пины oxDNA — OK (4/4)

Команды: `git init C:\NanoLab\verify-nl1-001-oxdna` + `git remote add origin https://github.com/lorenzo-rovigatti/oxDNA` + `git fetch --depth 1 origin 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` → FETCH_EXIT=0; `git rev-parse FETCH_HEAD` = `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`.

Blob SHA-1 (`git ls-tree 00dc7fb9 -- <4 paths>`) против пинов PREREGISTRATION_E1_R1 §2.2:

| Файл | Пин blob SHA-1 | Факт | |
|---|---|---|---|
| test/DNA/DSDNA8/dsdna8.top | `1811af7ea4bea8a86519456cba608d1e6d44ed3b` | `1811af7e…` | MATCH |
| test/DNA/DSDNA8/init.dat | `856be1878ece7115a91f988b2cbd7ad650daf2db` | `856be187…` | MATCH |
| test/DNA/DSDNA8/MD/quick_input | `07eef592f070f9b8955f9001e0fd292de9862a4a` | `07eef592…` | MATCH |
| test/DNA/DSDNA8/MD/quick_compare | `74a088ec4ceb1bc01ab2e385e4700eb2d3907f40` | `74a088ec…` | MATCH |

SHA-256 сырых blob'ов (извлечение `git show <commit>:<path>` через cmd-редирект `cmd /c "… > tmp_<name>"`, затем `Get-FileHash`; PowerShell-переменные/пайплайны не использовались):

| Файл | Пин SHA-256 §2.2 | Факт SHA-256 | Size |
|---|---|---|---|
| dsdna8.top | `f1aded90b5f6e1d9adab0e55925bba778477467be2957b4093d1264160c03fc4` | идентичен | 148 B |
| init.dat | `0ff76d541728e0925f199970ff6296254fe6116d23e44fdf0d361d0f8891a9e0` | идентичен | 4498 B |
| quick_input | `8935c4bc623ca96d406429c3c5177901f12540ffe61bcd3299931f0689af74a2` | идентичен | 533 B |
| quick_compare | `86a8b6ac50f382ba25e5aacbbef629cc5a1788f44e6c28d113509c8448e3ce27` | идентичен | 51 B |

Независимое Linux-подтверждение: исходники, материализованные в WSL из object DB того же клона (`git archive 00dc7fb9 | tar -x`), дают те же 4/4 SHA-256 по `sha256sum`.

### c) Негативный контроль autocrlf-тезиса — OK (тезис подтверждён)

Команда: `git -C C:\NanoLab\verify-nl1-001-oxdna checkout 00dc7fb9… -- <4 paths>` при `core.autocrlf=true` (значение и global, и local), затем `Get-FileHash` рабочих копий.

Факт: ни один хэш НЕ совпал с пином; более того, все четыре в точности воспроизвели негативный артефакт из IMPLEMENTER_EVIDENCE («Негативный артефакт»):

| Файл | Хэш рабочей копии (CRLF) | Задокументированный негативный хэш | |
|---|---|---|---|
| dsdna8.top | `a9e8cb7ecc6aa23c5715c34cd8c471da20548fb206fc1a292cd75ee81f124bd2` | `a9e8cb7e…24bd2` | MATCH |
| init.dat | `354ccb3e6a0ae40836a905cef5509397d9736a7ff68c40c4d16d05c53fdce3a6` | `354ccb3e…3e3a6` | MATCH |
| quick_input | `e33136467af25bf66ed3af305a3dedc482866e6faa08e90539236aed8267b1e4` | `e3313646…67b1e4` | MATCH |
| quick_compare | `a65227cd3591c590b87ec27817d7309baec5dfbcae2041be6fe1d67e9b29761a` | `a65227cd…b29761a` | MATCH |

Байт-уровень: рабочая копия dsdna8.top = 165 B против 148 B blob'а; подсчёт пар 0x0D 0x0A → 17 CRLF (файл из 17 строк). Документированная ловушка (ENGINE_ENVIRONMENT_R1 §5, §9) воспроизведена и подтверждена.

### d) Сборка воспроизводима по ENGINE_ENVIRONMENT_R1 §3 — OK

Команды (WSL2 Ubuntu 24.04.2, gcc 13.3.0, 20 ядер): исходники pinned commit материализованы в `~/nl1-001/oxdna-src` (байт-точное извлечение, fixture-хэши 4/4 — см. b); cmake 3.31.6 переиспользован user-local из `/mnt/c/NanoLab/scratch/nl1-001/tools/cmake/bin/cmake` (существует, `cmake --version` = 3.31.6; разрешено условием верификации); затем по §3:

```bash
cd ~/nl1-001/build-oxdna-cpu
<mirror>/tools/cmake/bin/cmake ../oxdna-src -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DMPI=OFF   # CONFIGURE_EXIT=0
make -j20                                                                                      # BUILD_EXIT=0, wall 16.2 s
```

Факт: `CONFIGURE_EXIT=0`, `BUILD_EXIT=0`; `bin/oxDNA` создан (3375976 B). CMakeCache: `CMAKE_BUILD_TYPE=Release`, `CUDA=OFF`, `MPI=OFF`, `DOUBLE=ON`, `NATIVE_COMPILATION=ON`, `JSON_ENABLED=ON`, `CMAKE_CXX_FLAGS` пуст — соответствует §3.

SHA-256 пересобранных бинарей НЕ совпали с §4 (oxDNA `aa8e8192…` против задокументированного `73b6cfb0…`) — ожидаемо и не является критерием: бинарь содержит шаблон времени сборки (`strings bin/oxDNA` → `COMPILED ON: %s`, `v3.7`). Детерминизм подтверждён на уровне размеров: 3375976 / 2957400 / 2201664 B — в точности значения §4 для всех трёх бинарей. Соответствие флагов §3 — полное.

### e) Smoke-артефакты в Git — OK (4/4 хэша + содержимое)

Команды: `git show 39b3448:docs/evidence/NL1-001/smoke-run/<file>` через cmd-редирект, `Get-FileHash`.

| Файл | Заявлено (IMPLEMENTER_EVIDENCE) | Факт (blob из 39b3448) | |
|---|---|---|---|
| log.dat | `85267114c7e25314389906107fa4820ae7f5a0c015dfa3832bf3354a355145d7` | идентичен | MATCH |
| energy.dat | `ede2f7e2efcd14a0b1d6f5152bbacbb489ad229cd1f105cce9c8f01bd2e2bd00` | идентичен | MATCH |
| quick_input_smoke | `579cc93a9d0490b532867633cfcd49e50fba94d1ad7f1f140de1dd127e6148e0` | идентичен | MATCH |
| time.log | `b0638ed05f4435db2d4de1f94f9c73cd7a0df245ba918d2c1cd17ef82eb7a652` | идентичен | MATCH |

Содержимое:

- log.dat: `RELEASE: v3.7` (стр. 11), `GIT COMMIT: 00dc7fb` (стр. 12), `N: 16, N molecules: 2` (стр. 8), `seeding the RNG with -807631765` (стр. 1), `Converting temperature … (0.097717)` (стр. 5), `END OF THE SIMULATION, everything went OK!` (стр. 24) — все заявленные факты присутствуют.
- time.log: `Elapsed (wall clock) time … : 0:00.13`, `Maximum resident set size (kbytes): 6424`, `Exit status: 0` — совпадает с заявленными 0.13 s / 6424 KB.
- energy.dat: ровно 11 строк; `nan|inf` — 0 вхождений; значения колонки 2 в диапазоне −1.29…−1.40, совместимы с описанной в §7 полосой.
- Внутренняя арифметика согласована: steps 1e4 / print_energy_every 1e3 → 10 записей + стартовая = 11 строк energy.dat (наблюдается); User 0.08 + Sys 0.02 = 0.10 s ≈ заявленный engine-таймер 0.100016 s → 0.0100 ms/step.

### f) quick_input_smoke против upstream quick_input — PARTIAL (находка MINOR, см. F-1)

Команда: `diff` (bash, WSL) извлечённых сырых blob'ов `tmp_quick_input` (533 B) и `tmp_quick_input_smoke` (414 B).

Факт:

1. Два заявленных отклонения присутствуют в точности: `steps = 1e6` → `steps = 1e4`; `print_conf_interval = 1e5` → `print_conf_interval = 1e4`.
2. Но «остальное посимвольно» / «единственные отклонения» (ENGINE_ENVIRONMENT_R1 §7, event 0003) — неточно: smoke-копия дополнительно отличается косметикой — удалены 5 строк-комментариев/заголовков (`####  PROGRAM PARAMETERS  ####`, `#debug = 1`, `####    SIM PARAMETERS    ####`, `#pt = 0.1`, `####    INPUT / OUTPUT    ####`), 3 пустые строки-разделителя, 2 trailing-space (`T = 20C ` → `T = 20C`, `print_energy_every = 1e3 ` → `print_energy_every = 1e3`).
3. На уровне эффективных (парсеру видимых) параметров входы идентичны, кроме двух заявленных отклонений: все 20 параметрических строк совпадают по значению; комментарии/пустые строки/пробелы для oxDNA-парсера инертны. Соответствие подтверждено арифметикой прогона (см. e).

Оценка: на смысл claims не влияет — smoke и так не является verbatim-прогоном (запрет §7 соблюдён с запасом), научных claims нет (C0), точный smoke-вход опубликован в Git (воспроизводим байт-в-байт из артефакта). Находка — точность формулировок документации. Severity: MINOR, fix формулировкой в следующей ревизии/erratum, без переисполнения WO.

### g) События, статусы, согласованность — OK

- 4 JSON (`events/0001…0004`) парсятся `ConvertFrom-Json` без ошибок; `event_id` = `0001-work-order-started` … `0004-handoff-completed` (сквозная нумерация 0001–0004); `timestamp_utc` монотонны: 07:02 < 07:45 < 08:05 < 08:20 (passport started_at 07:00 ≤ первой).
- `actor_role` всех событий = IMPLEMENTER; слово «ACCEPTED» в текстах NL1-001 отсутствует как вердикт implementer'а: в ENGINE_ENVIRONMENT_R1 (стр. 120) и summary.md (стр. 16) «ACCEPTED NL1-001» — только будущее условие запрета §7; IMPLEMENTER_EVIDENCE (стр. 88) прямо заявляет «Претензий на ACCEPTED от implementer'а нет»; чекбоксы приёмки в WO-NL1-001.md не отмечены. Исторические «ACCEPTED» относятся к NL0-001/002/003 (Director, ранее).
- `subject_sha` событий согласованы с историей: 0001 = base `57c1e63`, 0002/0003 = START `dd4692d`, 0004 = `60db6b7`; финальный коммит `39b3448` содержит только обновление event 0004 (привязка terminal event) — паттерн соответствует практике NL0.
- Числа согласованы по всем документам: wall 0.13 s (summary, event 0003, IMPLEMENTER_EVIDENCE, §7 = time.log `0:00.13`); RSS 6424 KB (те же = time.log); 11 строк energy.dat (те же = файл); seed −807631765 (event 0003 = log.dat стр. 1); T 0.097717 (§6/§7/события = log.dat); N=16/molecules=2 (§6 = log.dat = dsdna8.top); RELEASE v3.7 + GIT COMMIT 00dc7fb (документы = log.dat = пересобранный бинарь).

## Findings

| ID | Severity | Содержание | Влияние | Рекомендация |
|---|---|---|---|---|
| F-1 | MINOR | Формулировка «единственные отклонения: steps, print_conf_interval» (ENGINE_ENVIRONMENT_R1 §7, event 0003) неточна байт-точне: smoke-копия дополнительно отличается удалением 5 строк-комментариев/заголовков, 3 пустых строк и 2 trailing-space. Эффективные параметры — идентичны кроме двух заявленных. | Нет влияния на соответствие §7 (smoke non-verbatim), на C0-статус и на воспроизводимость (точный вход опубликован). | Erratum/правка формулировки в следующей ревизии документа («единственные отклонения эффективных параметров; косметические отличия — см. diff артефакта»). Переисполнение NL1-001 не требуется. |
| F-2 | OBSERVATION | Независимая пересборка даёт иные SHA-256 бинарей при идентичных размерах (3375976 B) и флагах; причина — время сборки в бинаре (`COMPILED ON: %s`). Задокументировано в условии верификации как ожидаемое; §4 не позиционирует hash как критерий. | Нет. | Опционально: добавить в §4 явную пометку «hash воспроизводим до sizes/flags, не до bytes». |

## Заключение

Exact subject `work/nl1-001-env-pin-smoke-r1` @ `39b34486b2cc156aab60add9f098885c15c51701` проверен независимо и полностью: scope в границах passport, fixture-пины 4/4 (blob SHA-1 и SHA-256), autocrlf-тезис подтверждён байт-уровнем и точным воспроизведением негативных хэшей, сборка по §3 воспроизводима (CONFIGURE_EXIT=0, BUILD_EXIT=0, флаги совпадают), smoke-артефакты 4/4 по SHA-256 и по содержимому, события корректны, научных claims и self-acceptance нет.

**VERDICT: PASS** — evidence-пакет NL1-001 sufficient для передачи на Director checkpoint. Human Gate merge в `main` остаётся за владельцем. Следующий этап по маршруту WO — NL1-002 (E1-кампания) только после ACCEPTED NL1-001.

---

*Verifier: independent fresh session. Проверки выполнены на fresh clone `C:\NanoLab\verify-nl1-001` (detached HEAD 39b3448), WSL2 Ubuntu 24.04.2 / Windows git 2.53.0. Этот вердикт коммитится в ветку `verify/nl1-001-env-pin-r1` от 39b3448; других файлов не касается.*
