# NL1-001 — Independent Reviewer Verdict R1

Роль: независимый REVIEWER (fresh session). Дата: 2026-09-09. Исполнение: `EX-NL1-001-R1`. Work Order: `NL1-001`.

## Verdict

**PASS**

Evidence-пакет NL1-001 соответствует критериям приёмки WO-NL1-001 и границам dispatch; запрет `E1-PROTO-R1` §7 на verbatim-прогон соблюдён; effective defaults подтверждены независимо по исходникам pinned oxDNA; все заявленные хэши воспроизведены байт-точно из Git-объектов; C0-дисциплина соблюдена, ACCEPTED/научный PASS нигде не объявлен. Findings уровня MINOR/NOTE (ниже) научную дисциплину не искажают и PASS не блокируют.

## Проверенное (команды и результаты)

Review выполнялся на ветке `review/nl1-001-env-pin-r1` от `39b34486b2cc156aab60add9f098885c15c51701` (HEAD `work/nl1-001-env-pin-smoke-r1`). Все байт-точные операции — через `git show`/`git cat-file` из копий object-store в WSL Ubuntu (bash redirect + sha256sum), минуя Windows working tree и PowerShell-пайплайны (`core.autocrlf=true` на машине ревьюера подтверждён).

### a) Scope и границы — OK

- `git merge-base --is-ancestor 57c1e63733ea3b10f991c0f9609c426dc75b17a5 HEAD` → exit 0: base — предок HEAD.
- `git diff --name-status 57c1e63 39b3448` → ровно 14 файлов: `docs/work/WO-NL1-001.md` (A), `docs/research/ENGINE_ENVIRONMENT_R1.md` (A), `docs/work/SESSION_LOG.md` (M, append), `docs/work/executions/EX-NL1-001-R1/**` (A), `docs/evidence/NL1-001/**` (A). Все — внутри `allowed_paths` passport.json.
- `project/state.json`, `project/plan.json`, policies, `E1-PROTO-R1`, схемы — в diff отсутствуют (границы WO соблюдены). Engine-исходники/бинари в репозиторий не вендорятся.
- Классы passport: `HIGH` / `C0_SOFTWARE_ONLY` — валидны по `config/control/harness/risk-policy.v1.json` (enum claim_classes; HIGH minimum_roles IMPLEMENTER/REVIEWER/VERIFIER/DIRECTOR совпадает с маршрутом WO) и `execution-passport.schema.v1.json`.
- Критерии приёмки WO (7/7): воспроизводимая установка (§2–§3 ENGINE_ENVIRONMENT_R1), fixture 4/4 (см. d), сборка pinned CPU с записанными version/flags/SHA-256 бинарей (§4), smoke go/no-go без scientific claims (§7), measured wall/RAM (§7, time.log), effective defaults §11.1–2 (§6, см. c), GPU-статус CPU-only по протоколу (§8).

### b) Запрет E1-PROTO-R1 §7 / quick_input_smoke — OK (с MINOR-1)

Независимо получен pinned oxDNA тем же способом, что у implementer: `git init` + `git fetch --depth 1 origin 00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` + checkout → `rev-parse HEAD` = `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`.

- `git show 39b3448:docs/evidence/NL1-001/smoke-run/quick_input_smoke | sha256sum` → `579cc93a9d0490b532867633cfcd49e50fba94d1ad7f1f140de1dd127e6148e0` — совпадает с пином IMPLEMENTER_EVIDENCE (414 B).
- `git show 00dc7fb9:test/DNA/DSDNA8/MD/quick_input` → SHA-256 `8935c4bc…af74a2` = пин §2.2 (533 B). Verbatim-прогона этого файла в пакете нет → §7 не нарушен.
- Функциональный diff smoke vs upstream — ровно два отклонения, как задекларировано: `steps = 1e6 → 1e4`, `print_conf_interval = 1e5 → 1e4`.
- Байт-уровень: файл дополнительно содержит **нефункциональные** отличия — удалены строки-комментарии/заголовки секций (`####  PROGRAM PARAMETERS  ####`, `#debug = 1`, `####    SIM PARAMETERS    ####`, `#pt = 0.1`, `####    INPUT / OUTPUT    ####`) и два концевых пробела (`T = 20C `, `print_energy_every = 1e3 `). Нефункциональность доказана по исходнику pinned-парсера: `src/Utilities/parse_input/parse_input.cpp:142–145` стирает всё от `#`; ключи/значения проходят `Utils::trim` (строки 288, 305–306). Эффективный набор параметров совпадает с задекларированным. → MINOR-1 (формулировка «единственные отклонения» точна только для effective parameters, не для байтов).
- Scientific claim из smoke не делается: в ENGINE_ENVIRONMENT_R1 §7 совпадение среднего колонки 2 с upstream-полосой явно помечено «не является scientific результатом»; `scientific_outcome = NOT_EVALUATED`.

### c) Effective defaults против исходников pinned oxDNA — OK (всё подтверждено)

Проверено по blob'ам `00dc7fb9` (цитаты строк точны):

| Утверждение пакета | Факт в pinned-исходнике | Результат |
|---|---|---|
| `interaction_type` default `dna` | `src/Interactions/InteractionFactory.cpp:45`: `getInputString(&inp, "interaction_type", inter_type, 0)` с инициализацией `std::string inter_type("DNA")`; `input_options.md:388–391` «Defaults to dna» | ПОДТВЕРЖДЕНО |
| `use_average_seq` default true | `src/Interactions/DNAInteraction.cpp:14`: конструктор `_average(true)`; дополнительно `input_options.md` (DNAInteraction): «defaults to yes» | ПОДТВЕРЖДЕНО |
| `john` → BrownianThermostat alias | `src/Backends/Thermostats/ThermostatFactory.cpp:25`: `strncmp(thermostat_type,"john",…)→make_shared<BrownianThermostat>()`; `input_options.md:155` перечисляет `no|refresh|brownian|langevin|srd` без `john` — замечание «stale docs» корректно | ПОДТВЕРЖДЕНО |
| формула pt | `src/Backends/Thermostats/BrownianThermostat.cpp:45` (init): `pt=(2·T·nst·dt)/(T·nst·dt+2·diff_coeff)` | ПОДТВЕРЖДЕНО |
| формула pr | там же, строка 50: `pr=(2·T·nst·dt)/(T·nst·dt+2·3·diff_coeff)` | ПОДТВЕРЖДЕНО |
| колонка 2 = U/N | `src/Observables/PotentialEnergy.cpp:24`: `energy /= _config_info->N()` | ПОДТВЕРЖДЕНО |

Независимый пересчёт (T=0.097717, nst=103, dt=0.005, diff_coeff=2.50): x=T·nst·dt=0.050324255; **pt=0.019929118392815 → 0.019929118** (совпадает); **pr=0.00668746455522795 → 0.006687465** (совпадает). Дополнительно проверен нюанс исходника: код сначала пересчитывает `diff_coeff = T·nst·dt·(1/pt−1/2)` — результат совпадает с входным 2.50 (Δ=0), поэтому прямая формула pr корректна (NOTE-1). «Соль NOT_APPLICABLE для default dna»: секция `input_options.md` для DNAInteraction не содержит salt-опций (salt/salt_concentration — в RNAInteraction/DNA2Interaction) — подтверждено. Build-флаги §3 согласуются с `CMakeLists.txt` pinned-коммита: `-D_FORCE_INLINES` (строка 11), `DOUBLE` default ON (20), `NATIVE_COMPILATION` default ON → `-march=native` (23, 98–101).

### d) Логика autocrlf / негативный контроль — OK (полностью воспроизведено)

- Позитивный контроль: `git show 00dc7fb9:test/DNA/DSDNA8/dsdna8.top` (bash redirect, WSL) → SHA-256 **`f1aded90b5f6e1d9adab0e55925bba778477467be2957b4093d1264160c03fc4`** = пин §2.2, 148 B. Байт-точность пути cat-file/blob подтверждена.
- `git ls-tree 00dc7fb9` — blob SHA-1 всех 4 fixture-файлов = пины `E1-PROTO-R1` §2.2: dsdna8.top `1811af7e…ed3b`, init.dat `856be187…af2db`, MD/quick_input `07eef592…2a4a`, MD/quick_compare `74a088ec…7f40` (4/4).
- SHA-256 извлечённых blob'ов 4/4 MATCH пинам: `f1aded90…` (148 B), `0ff76d54…1a9e0` (4498 B), `8935c4bc…f74a2` (533 B), `86a8b6ac…e3ce27` (51 B).
- Негативный контроль (независимое воспроизведение находки implementer'а): Windows working-tree копия `dsdna8.top` того же pinned-коммита (autocrlf=true) → SHA-256 **`a9e8cb7ecc6aa23c5715c34cd8c471da20548fb206fc1a292cd75ee81f124bd2`**, 165 B — в точности негативный артефакт `a9e8cb7e…24bd2`, записанный в IMPLEMENTER_EVIDENCE. Логика «working tree искажён → канонический путь только blob» доказана независимо.

### e) Консистентность событий, passport, артефактов — OK (с MINOR-2, MINOR-3)

- Events 0001–0004 и passport.json валидны как JSON и **SCHEMA_OK** против machine-контрактов `config/control/harness/work-event.schema.v1.json` и `execution-passport.schema.v1.json` (jsonschema Draft202012, 0 ошибок).
- Нумерация 0001–0004 без пропусков; timestamps монотонны: 07:02:00Z → 07:45:00Z → 08:05:00Z → 08:20:00Z.
- subject_sha согласованы с реальными коммитами ветки: 0001=`57c1e63` (base), 0002/0003=`dd4692d62850ffe897ada99a920b3b4d2e81caa8` (START-коммит, существует), 0004=`60db6b7cae8d7995fde53f7be9a9e78ab9ca7f70` (evidence-коммит, существует).
- Smoke-артефакты согласованы с evidence map: log.dat — `RELEASE: v3.7`, `GIT COMMIT: 00dc7fb`, `N: 16, N molecules: 2`, seeding `-807631765`, T→`0.097717`, «END OF THE SIMULATION, everything went OK!»; time.log — Elapsed `0:00.13`, Max RSS `6424 KB`, Exit status 0; energy.dat — 11 строк, NaN/Inf=0 (grep по energy.dat), среднее колонки 2 = −1.360180 (вне научной интерпретации). SHA-256 всех 4 артефактов из Git-blob'ов совпали с пинами IMPLEMENTER_EVIDENCE (log.dat `85267114…`, energy.dat `ede2f7e2…`, quick_input_smoke `579cc93a…`, time.log `b0638ed0…`).
- Хронология коммитов соответствует событиям: dd4692d (START) → 60db6b7 (evidence+events 0002–0004) → 39b3448 (handoff/summary).

### f) Отсутствие self-acceptance / научных claims — OK

Grep по всем новым файлам: упоминания `ACCEPTED`/`SUPPORTED` встречаются только как запреты/условия («не выставлять ACCEPTED», «разрешён только после ACCEPTED NL1-001», «Претензий на ACCEPTED от implementer'а нет»); `scientific_outcome = NOT_EVALUATED`; summary — «IMPLEMENTED — HANDOFF to independent REVIEW + VERIFIER». Checklist в IMPLEMENTER_EVIDENCE явно помечен «самопроверка implementer'а, не acceptance». Self-acceptance и научные claims отсутствуют.

## Findings

- **MINOR-1** — `quick_input_smoke` отличается от upstream `quick_input` не только двумя задекларированными значениями, но и на байтовом уровне (удалены строки-комментарии/заголовки секций и концевые пробелы; 414 B vs 533 B). Отличия нефункциональны для pinned-парсера (см. b), эффективный набор параметров совпадает с задекларированным, §7 не нарушен. Рекомендация: в будущих документах формулировать «два функциональных отклонения; остальные текстовые отличия (комментарии/пробелы) игнорируются парсером» или публиковать минимальный diff.
- **MINOR-2** — В blob `docs/work/SESSION_LOG.md` @ `39b3448` в записи NL1-001 находятся управляющие байты: `0x00` перед `0dc7fb9a…` (пин движка потерял ведущий `0`) и `0x1b` перед `nergy /= N`. Гигиена durable memory; канонические значения присутствуют и корректны в ENGINE_ENVIRONMENT_R1 и IMPLEMENTER_EVIDENCE, поэтому recovery не страдает. Исправление — отдельным commit исправляющей роли (ревьюер ограничен своим scope).
- **MINOR-3** — `passport.json.status` остался `IN_PROGRESS` при завершённом HANDOFF_COMPLETED (значение валидно по схеме, но не отражает терминальное состояние; `IMPLEMENTED`/`HANDOFF_READY` не выставлены). Синхронизация статуса — в том же последующем коммите.
- **NOTE-1** — В `BrownianThermostat.cpp::init` pr вычисляется после внутреннего пересчёта `diff_coeff` из pt; численно результат идентичен прямой формуле (Δ=0), расхождения нет — для протокола достаточно зафиксированной формулы §6.
- **NOTE-2** — Все хэши пакета ревьюером проверены из Git-blob'ов (байт-точно), включая 4/4 fixture SHA-256, 4/4 blob SHA-1 и 4/4 smoke-артефакта; воспроизводимость acquisition-пути (init+fetch --depth 1) подтверждена независимо. Фактическое re-execution сборки §3 и smoke — предмет независимого VERIFIER, не этого review.

## Claim ceiling

`C0_SOFTWARE_ONLY` (подтверждён): environment pin + технический smoke. Никаких научных утверждений пакет не содержит и не претендует на повышение claim. Для будущей кампании E1 ceiling остаётся `C1_COMPUTATIONAL_REPRODUCTION` (E1-PROTO-R1 §1).

## Next action (одно)

Независимый VERIFIER: fresh checkout `39b34486b2cc156aab60add9f098885c15c51701`, повторить команды ENGINE_ENVIRONMENT_R1 §3 (сборка pinned oxDNA), сверить SHA-256 бинарей §4 и артефактов smoke с пинами IMPLEMENTER_EVIDENCE, выставить вердикт в `docs/evidence/NL1-001/VERIFIER_VERDICT.md`; затем Director checkpoint и PR (merge в `main` — Human Gate). MINOR-1..3 учесть исправляющим коммитом до/вместе с checkpoint.
