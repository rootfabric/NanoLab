# NL0-001 — Fresh Independent Review R1

Исполнение: `EX-NL0-001-R1`. Роль: `REVIEWER` (fresh, независимая сессия, не Implementer).

```text
REVIEWED_HEAD = f738bff77f2406552b4383c05989ffc6e56a3bd5
EPOCH_DRIFT   = CONTINUE
VERDICT       = PASS
NEXT_ACTOR    = FRESH VERIFIER
```

Цель review — попытка опровергнуть выводы Implementer по Work Order `NL0-001` (выбор доступных эталонов E1/E2). Ниже — только независимо перепроверенные факты. Все live-проверки выполнены в день review через GitHub API/raw, PubMed/Europe PMC/Crossref/Semantic Scholar/Unpaywall и прямые загрузки pinned-файлов.

## 1. Exact-head freshness

PR #11 (`research: NL0-001 выбрать воспроизводимые E1/E2 эталоны`):

```text
PR head SHA (live API)   = f738bff77f2406552b4383c05989ffc6e56a3bd5
expected candidate HEAD  = f738bff77f2406552b4383c05989ffc6e56a3bd5
PR base SHA              = 9d8ea394c6c037b0560908689e2ce932bf0c511c
current main             = f4d2979a1d2502d86c035f25e36961b4d5ac2764
```

Совпадение точное. Review относится только к этому candidate HEAD. Ветка `review/nl0-001-reference-selection-r1` инициализирована от exact subject (`f738bff → 25c6d19 → f3990dc`) и пригодна; настоящий отчёт добавлен в неё.

## 2. Epoch drift

`9d8ea394 → f4d2979` (текущий `main`): 12 файлов, исключительно additive INFRA-линия — `docs/infra/*`, `docs/work/WO-INFRA0-001.md`, `project/infra-plan.json`, `project/infra-state.json`, `docs/evidence/INFRA_ROADMAP_R1_CHECKS.md` + роутинговые вставки в `AGENTS.md`/`PROJECT_CONTROL.md`/`README.md`/`docs/INDEX.md`.

Не затронуты: `docs/research/**`, `docs/research/SOURCES.md`, научная методология (`docs/control/*` не изменены), risk/review контракты (`config/control/harness/*` не изменены), критерии приёмки (`docs/work/WO-NL0-001.md` не изменён), `project/state.json` (не изменён; добавлен только отдельный `project/infra-state.json`). Новые hard rules только усиливают разделение INFRA/science и совместимы со scope NL0-001.

```text
EPOCH_DRIFT = CONTINUE
```

Refresh не требуется; выполнять его не стал.

## 3. E1 — независимая проверка DSDNA8

Upstream: `lorenzo-rovigatti/oxDNA@00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` (существует; лицензия репозитория на этом commit — GPL v3.0, подтверждено API).

Четыре файла скачаны независимо и пересчитаны побайтово:

| Файл | Существует | Размер | SHA-256 (live) | = INPUT_AVAILABILITY |
|---|---|---:|---|---|
| `test/DNA/DSDNA8/dsdna8.top` | да | 148 B | `f1aded90b5f6e1d9adab0e55925bba778477467be2957b4093d1264160c03fc4` | да |
| `test/DNA/DSDNA8/init.dat` | да | 4498 B | `0ff76d541728e0925f199970ff6296254fe6116d23e44fdf0d361d0f8891a9e0` | да |
| `test/DNA/DSDNA8/MD/quick_input` | да | 533 B | `8935c4bc623ca96d406429c3c5177901f12540ffe61bcd3299931f0689af74a2` | да |
| `test/DNA/DSDNA8/MD/quick_compare` | да | 51 B | `86a8b6ac50f382ba25e5aacbbef629cc5a1788f44e6c28d113509c8448e3ce27` | да |

Git blob SHA-1 всех четырёх файлов также совпадают с записанными. Несовпадений нет.

Содержание проверено построчно:

- `dsdna8.top`: заголовок `16 2` — 16 nucleotides, 2 strands; две комплементарные 8-nt цепочки. Заявление подтверждено.
- `quick_input`: `backend = CPU`, `steps = 1e6`, `thermostat = john`, `T = 20C`, `dt = 0.005`, `topology = ../dsdna8.top`, `conf_file = ../init.dat`. Заявленные параметры подтверждены дословно.
- `quick_compare`: `ColumnAverage::energy.dat::2::-1.37970256144::0.15` — заранее существующий upstream numerical oracle (среднее по колонке 2 energy-файла, tolerance 0.15). Прочитан верно: `REFERENCE_SELECTION.md` цитирует то же значение и ту же tolerance.
- Минимальность: в официальном `test/DNA` на pinned commit есть только `DSDNA8`, `SSDNA15`, `FORCE_FIELD`; DSDNA8 — минимальный **дуплексный** fixture с одним quick-oracle. SSDNA15 содержит на 1 nucleotide меньше, но это одноцепочечный poly-A гомополимер (не дуплекс). Выбор DSDNA8 как первого E1 обоснован и честно документирован (SSDNA15 оставлен fallback).
- Claim ceiling корректен: файлы явно ограничивают успешный quick regression уровнем `C1_COMPUTATIONAL_REPRODUCTION` и прямо отрицают C4 physical validation. Regression fixture не выдаётся за экспериментальную физическую валидацию.

## 4. E1 fallback

- `test/DNA/SSDNA15/MD`: существует; `ssdna15.top` = `15 1` (15 nt, 1 strand, poly-A), `quick_input` = CPU, `1e6` steps, `T = 300K`; `quick_compare` содержит **два** `ColumnAverage`-критерия. Описание Implementer точное.
- `examples/HAIRPIN`: существует; `initial.top` (`18 1`), `initial.conf`, `input`, `input_seq_dep`, `input_trap`, `hairpin_forces.dat`, `run.sh`, `DOCS/`. Основной `input`: `sim_type = VMMC`, `steps = 100000000` (1e8), `T = 334 K`. Утверждение «Selected input requests 100,000,000 VMMC steps at 334 K» подтверждено дословно.
- Сравнение сложности корректно: 1e6 CPU MD steps против 1e8 VMMC steps (×100) плюс более сложный пример. DSDNA8 действительно существенно проще первого HAIRPIN-сценария.

## 5. E2 — независимая проверка

Статья: Shi, Castro, Arya, *Conformational Dynamics of Mechanically Compliant DNA Nanostructures from Coarse-Grained Molecular Dynamics Simulations*, ACS Nano 2017, 11(5), 4617–4630, DOI `10.1021/acsnano.7b00242` (PubMed 28423273; авторы Ze Shi, Carlos E. Castro, Gaurav Arya — подтверждено Crossref/PubMed).

Репозиторий: `gauravarya77/DNA-hinge-simulations@23fd1ff7731e9017bd776f49206dc42d70d9fe91`.

- Pinned commit существует и является текущим HEAD `master` (последний push 2017-04-04), поэтому pinned tree = полное текущее состояние репозитория.
- Tree SHA commit = `b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9` — совпадает с записанным в `INPUT_AVAILABILITY.md`.
- Полный recursive tree (33 entry, не truncated) содержит ровно заявленное: `Design_Hinges/{0b,11b,32b,53b,74b}.json` (все 5 blob SHA-1 и размеры совпали с записанными: 173059/173145/173315/173481/173595 B), `MD_Hinges/{0b,11b,32b,53b,74b}.{top,conf}` (все 10 присутствуют), `MD_Hinges/pro_CPU.in` (blob `89d76310…` совпал) и `MD_Hinges/pro_GPU.in`, `Init_Hinges/` (`cadnano_interface.py`, `init_generator.py`, `ini_demo/…`).
- `MD_Hinges/0b.conf` = 2 294 162 B ≈ 2.29 MB — подтверждено; это реальные машинные входы, не metadata.
- `pro_CPU.in`: `backend = CPU`, `backend_precision = double`, `steps = 2e7`, `interaction_type = DNA2`, `salt_concentration = 0.5`, `T = 300K`, `thermostat = john`, `dt = 0.005`. `pro_GPU.in`: `backend = CUDA`, mixed precision, те же DNA2/0.5/300K/2e7. CPU/GPU inputs подтверждены.
- Pre-equilibrated structures: README `MD_Hinges` прямо описывает `.conf` как «structure and velocity data of an equilibrated hinge». Подтверждено.
- Связь статья ↔ репозиторий доказана независимо полным текстом статьи: «Additional supporting research data related to oxDNA simulations of the DNA hinges for this article may be accessed at https://github.com/gauravarya77/DNA-hinge-simulations» (Notes). Репозиторий действительно принадлежит публикации (владелец — соавтор Gaurav Arya) и содержит её входы.
- REPORTED-параметры статьи проверены по полному тексту: oxDNA2 («modeled using oxDNA2, an updated version of the oxDNA model»); average-base parametrization; 298 K и 500 mM Na⁺ («at a temperature of 298 K and a monovalent salt concentration of 500 mM Na+»); пять вариантов и длины spring-слоёв: «0 and 24 … 11 and 35 … 32 and 56 … 53 and 77 … 74 and 84 bases» — всё дословно совпадает с `REFERENCE_SELECTION.md`.

## 6. Атака проблемных мест

### A. 298 K vs 300 K

Расхождение реально: статья (Methods) — 298 K; оба авторских входа (`pro_CPU.in` и `pro_GPU.in`) — `T = 300K`. Salt (0.5 M = 500 mM) и модель (DNA2 = oxDNA2) совпадают; расходится только температура. Implementer зафиксировал расхождение явно и делегировал разрешение в NL0-003 («должно быть явно разрешено в NL0-003, а не замолчано») — это правильная передача: не молчаливый выбор одной температуры, а зарегистрированный конфликт для preregistration. Атака не удалась.

### B. License

Полный pinned tree (33 entry) не содержит `LICENSE`/`COPYING`/`NOTICE`; GitHub API для репозитория возвращает `license: None`; поскольку pinned commit = HEAD `master`, более поздней лицензии тоже нет. `INPUT_AVAILABILITY.md` корректно удерживает `REDISTRIBUTION_RIGHTS = UNKNOWN` и явно отделяет public accessibility от права копирования, делегируя решение NL0-002. Verdict Implementer не завышен — «public GitHub значит можно копировать» нигде не утверждается. Дополнительно для NL0-002: в репозитории есть медиафайл `MovieS1.mp4` — учитывать при аудите наряду с кодом/данными.

### C. S08 (`10.1021/acsnano.7b06470`)

Метаданные подтверждены (Sharma R, Schreck JS, Romano F, Louis AA, Doye JPK; ACS Nano 2017 Dec 26). Независимая проверка разумных поверхностей: полный текст статьи (зеркало) показывает, что Associated Content = SI PDF («precise definitions of all measured angles and extensions and additional simulation results») + 5 файлов Movies (MPG); GitHub-поиск по «jointed DNA nanostructures» — 0 репозиториев; Europe PMC — нет PMCID/полнотекстовых data-ссылок. Показательно: в благодарностях статьи caDNAno-файлы упомянуты как предоставленные Carlos Castro privately («supplying us with the original caDNAno files»), т.е. machine-readable pack не публиковался со статьёй. Формулировка `INPUT_PACK_NOT_LOCATED` (не `NO_DATA_EXISTS`) точна и правильно ограничена; UNKNOWN про непроверенные поверхности сохранён, recovery path (запрос авторам) записан. Атака не удалась.

### D. Leaf-spring benchmark

Centola et al. (`s41565-023-01516-x`) в PR подан только как «будущий rich benchmark», явно не вытесняющий первый E2, и не входит ни в одну зависимость E1/E2. `sulcgroup/hinges@7c8b04a` существует, README действительно описывает angle extraction/analysis; лицензии в root нет (подтверждено — правы, что отметили). Ошибочного включения в основной E2 нет. Замечание: размер Zenodo-записи (46.2 GB) из этого окружения непроверяем (Zenodo API 403) — не blocking, т.к. артефакт не является зависимостью.

## 7. Harness trail — `EX-NL0-001-R1`

- События 0001–0005 существуют, типы и порядок точно: `WORK_ORDER_STARTED → CONTINUATION_CHECKPOINT → IMPLEMENTATION_COMMITTED → VALIDATION_RECORDED → HANDOFF_COMPLETED`; timestamp монотонны (03:50:26 → 03:58:48 UTC); `subject_sha` каждого события образуют проверяемую цепь от base `9d8ea394` через START `3c946623`, checkpoint `73997369d7f83ef7d60585223c1128eef729204c` до research subject `dd5cef3c8bd7212c64da4c80fedb5ca03169eac9` с финальным HEAD `f738bff`, публикующим сами события; PR body документирует всю цепь явно.
- `passport.json` валиден (risk HIGH / claim C0 / allowed_paths покрывают все изменённые файлы); `summary.md`, `branch-passport.md` на месте.
- Воспроизведено независимо: `scripts/harness/work_cli.py close docs/work/executions/EX-NL0-001-R1` → `ok=true`, status `HANDOFF_READY` (команда не мутирует репозиторий).
- Self-accept отсутствует: статус `HANDOFF_READY`, verdict Implementer — «HANDOFF CANDIDATE; independent review required». `project/state.json` не переведён преждевременно: `NL0-001 = READY`, `completed_tasks = []`, `stage_status.NL0 = PLANNED`, `E0–E6 = NOT_RUN`, `physics_runs = 0`.

## 8. Scope review PR #11

13 файлов: 3 новых research/evidence документа, обновления `SOURCES.md`/`SESSION_LOG.md`, полный execution-пакет `EX-NL0-001-R1`. Все пути входят в `allowed_paths` паспорта; код, CI, INFRA, эксперименты не тронуты; `project/state.json` разрешён, но сознательно не изменён. Правки `SOURCES.md` ограничены статусом S08 + новыми S15/S16/S17 и лёгким редакторским сжатием S09–S14; исторический evidence-файл `docs/evidence/HARNESS_R1_CHECKS.md` сохранён. Scope creep не обнаружен.

## 9. Verdict

Попытки опровергнуть выводы Implementer исчерпаны: хеши, существование файлов, содержание inputs/oracle, связь статьи с репозиторием, границы REPORTED/OBSERVED/UNKNOWN, права, harness-trail и scope — всё подтвердилось без единого несовпадения.

```text
VERDICT = PASS
```

### REQUIRED_FIXES

Нет.

### RANK_UP_MOVES (не блокируют NL0-001)

1. **NL0-003:** зафиксировать, что 300 K стоит в обоих авторских входах (`pro_CPU.in` и `pro_GPU.in`), а 298 K — только в статье; preregister каноническую температуру и rationale, а также seed/thermostat/dt-политику (сейчас seed = 7777 задан авторским прагматиком, не протоколом статьи).
2. **NL0-003:** определить hinge-angle observable по определению угла из самой статьи `7b00242` (а не по S08-определениям) и preregister REPORTED equilibrium angles/FWHM из Figure 2c как reference до первого запуска.
3. **NL0-002:** включить в аудит медиафайл `MovieS1.mp4` и различие «ссылка на exact upstream objects» vs «копирование в NanoLab»; для oxDNA (GPLv3) оценить implications каждого режима использования.
4. **Harness (незначительно):** в будущих исполнениях делать `subject_sha` терминального события равным финальному HEAD ветки (сейчас связка `dd5cef3` + HEAD `f738bff` восстанавливается только через PR body).
5. Пере-верифицировать размер Zenodo `8248808` из окружения с доступом, когда leaf-spring benchmark станет актуален.

## Доказательства воспроизводимости review

Ключевые команды/поверхности: GitHub API (`pulls/11`, `git/trees?recursive=1`, `contents`, `license`), `raw.githubusercontent.com` на pinned SHA с локальным `sha256sum`, PubMed eutils/Europe PMC/Crossref/Semantic Scholar/Unpaywall, полный текст обеих статей через доступные зеркала, `scripts/harness/work_cli.py close` на candidate HEAD. Все живые ответы согласованы с `docs/research/INPUT_AVAILABILITY.md` и `docs/research/REFERENCE_SELECTION.md`.

## Next actor

`FRESH VERIFIER` (HIGH risk: Reviewer + Verifier + Director). Verifier должен проверить exact subject, hashes/manifests и harness-completeness независимо от настоящего отчёта. Merge PR #11 — Human Gate; настоящий review не авторизует merge и не закрывает NL0.
