# NL0-003 — Implementer Evidence (EX-NL0-003-R1)

Роль: IMPLEMENTER. Статус: `HANDOFF_READY`, не ACCEPTED. Scientific claim: отсутствует (`C0_SOFTWARE_ONLY`); будущая кампания E1 ограничена потолком `C1_COMPUTATIONAL_REPRODUCTION`, кампания E2 — отдельной пререгистрацией. Симуляции не запускались: `E1 = NOT_RUN`, `E2 = NOT_RUN`, `physics_runs = 0`.

## Exact subjects

```text
BASE_SHA            = 81e299f1924e50bcff1bc5c893bccd934ef2883d (canonical main, origin совпал)
START_COMMIT        = 9372b79e1406ffd2d0853bcd3c8f2232062f737c (harness: start NL0-003 execution)
SOURCE_CHECK_COMMIT = 53379e4973158e38531e346461d625b421f93cdf (research: checkpoint source re-verification)
SUBSTANTIVE_HEAD    = 3450866925ce49fc81ee658806d3ec81b2e1bc81 (research: preregister E1 protocol R1 and E2 setup R1; tree a18762b9bc577a92eb10b923801b974f42fd4273)
```

Live state на старте: `main` = `81e299f`, `project/state.json`: frontier NL0, NL0-001 ACCEPTED, NL0-002 ACCEPTED, NL0-003 READY, next_work_order NL0-003, E0..E6 NOT_RUN, physics_runs 0 — совпало с ожидаемым.

## Что проверено и чем (команды/источники)

| Проверка | Метод | Результат |
|---|---|---|
| Входы E1 (4 файла) | повторный download на pinned commit `00dc7fb9…` + SHA-256; tree-listing GitHub API | **4/4 SHA-256 MATCH** против пинов `INPUT_AVAILABILITY.md`; blob SHA-1 совпали (`1811af7e`, `856be187`, `07eef592`, `74a088ec`); один transient raw-404, устранён повтором/переключением на contents API |
| Условия E1 | дословное чтение `quick_input` (533 B) | CPU, 1e6 steps, newtonian_steps 103, diff_coeff 2.50, thermostat john, T 20C, dt 0.005, verlet_skin 0.05, print_energy_every 1e3, print_conf_interval 1e5, external_forces 0; `#seed` и `#pt` закомментированы upstream |
| Критерий E1 | дословное чтение `quick_compare` (51 B) | `ColumnAverage::energy.dat::2::-1.37970256144::0.15` — перенесён в протокол без изменений |
| Топология | чтение `dsdna8.top` (148 B) | `16 2`; цепь 1 ACGTACGT, цепь 2 ACGTACGT (порядок строк файла) |
| E2 условия | только принятые факты NL0-001/NL0-002 (blob `89d76310…`, tree `b2d6cebc…`) | `pro_CPU.in`: DNA2, salt 0.5, T 300K, CPU/double, 2e7 steps; статья: 298 K, 500 mM; файлы E2 НЕ скачивались (RIGHTS UNKNOWN → REFERENCE_ONLY) |
| Rights | без новых проверок | унаследованы от принятого NL0-002: E1 CLEAR/GPL-3.0/DOWNLOAD_ON_SETUP; E2 UNKNOWN/REFERENCE_ONLY |
| Issue #4 | `GET /repos/rootfabric/NanoLab/issues/4` | WO восстановлен дословно, acceptance criteria не расширены |

## Результаты

```text
E1_PROTOCOL   = E1-PROTO-R1 PREREGISTERED (docs/research/PREREGISTRATION_E1_R1.md):
                subject+SHA-256, verbatim conditions, механическое определение observable,
                upstream-критерий (не подгоняется), T1 upstream-equivalent + T2 robustness,
                пилот-процедура и freeze для R_confirm, семантика исходов, UNKNOWN-реестр.
E2_SETUP      = E2-SETUP-R1 (docs/research/E2_SETUP_R1.md): первый шарнир 0b, требования к
                определению угла/целостности (числа — не назначены), decision rule 298K-vs-300K
                (reproduction arm = авторские inputs verbatim), family = 5 опубликованных
                вариантов, скелет статистики, hard dependencies (rights/owner, NL2, NL1-001).
NOT_INVENTED  = R_confirm, целевой угол E2, tolerances E2, engine version, measured budget,
                SI-определение угла — всё помечено UNKNOWN с процедурами закрытия.
```

## Изменённые поверхности

```text
docs/work/WO-NL0-003.md                                    (создан из issue #4)
docs/research/PREREGISTRATION_E1_R1.md                     (создан)
docs/research/E2_SETUP_R1.md                               (создан)
docs/research/SOURCES.md                                   (S15/S16: ссылки на протокол и постановку)
docs/evidence/NL0-003/IMPLEMENTER_EVIDENCE.md              (этот файл)
docs/work/SESSION_LOG.md                                   (запись EX-NL0-003-R1)
docs/work/executions/EX-NL0-003-R1/**                      (passport, branch-passport, events, summary)
```

`project/state.json` / `project/plan.json` не изменялись (нет self-acceptance). Сторонние scientific файлы в репозиторий не копировались (E1 — только SHA-256/метаданные; загрузки шли во временный каталог ОС). Policies/схемы не менялись.

## Validation

```text
python -m json.tool passport.json / events 0001-0003 / state.json / plan.json -> OK (6/6)
CONTROL_DEVELOPMENT.ps1 -CheckConsistency  -> ok=true, exit 0, head 34508669
CONTROL_WORK.ps1 validate (pre-handoff)    -> ok=true, errors [], terminal/summary отсутствовали (ожидаемо)
CONTROL_WORK.ps1 close                     -> выполняется после terminal event; результат в summary.md
```

## Открытые риски / ограничения

- Протокол E1 намеренно держит UNKNOWN: effective `interaction_type`/salt/thermostat-delta (defaults pinned engine), семантика колонки 2 `energy.dat`, `R_confirm` (пилот → `E1-PROTO-R2`), engine pin (NL1-001), measured budget (первый прогон).
- E2 заблокирован структурно до: решения владельца по правам `DNA-hinge-simulations`, получения/pinning SI, compatibility audit авторских скриптов 2017, принятой методологии E0/E1.
- Пререгистрация — документы: она не создаёт scientific evidence и не приближает E1/E2 статусы к RUN.

## Next

`NEXT_ACTOR = VERIFIER` после независимого REVIEWER (HIGH-risk routing: scientific_protocol/observable_definition/acceptance_threshold → Reviewer + Verifier + Director). Reviewer проверяет, что критерии не подогнаны и REPORTED/ASSUMED/UNKNOWN разделены; Verifier проверяет exact subject, SHA-256, verbatim-цитаты и отсутствие выдуманных значений. Merge — Human Gate.
