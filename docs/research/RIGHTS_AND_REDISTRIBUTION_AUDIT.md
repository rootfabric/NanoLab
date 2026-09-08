# NL0-002 — Аудит прав и перераспределения исходных данных

Исполнение: `EX-NL0-002-R1`. Статус: IMPLEMENTER RECOMMENDATION / REVIEW REQUIRED. Никакие сторонние научные файлы не копировались в NanoLab; никакие симуляции не запускались.

Правило чтения: `UNKNOWN` не является разрешением. «Public GitHub», «есть DOI», «open source» сами по себе не дают права копировать, модифицировать или включать в release.

## 1. E1 — oxDNA upstream DSDNA8 fixtures

Субъект: `lorenzo-rovigatti/oxDNA` @ `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`.

### Независимо установленные факты (GitHub API, live-проверка в этом исполнении)

- Корневой файл `LICENSE` на pinned commit существует: Git blob `94a9ed024d3859793618152ea559a168bbcbb5e2`, GitHub классифицирует как `GPL-3.0`, содержание — полный текст GNU GPL v3.0 (29 June 2007). Совпадает с наблюдением NL0-001.
- Единственный `LICENSE` в корне; отдельных лицензий для `test/`, `examples/` или `docs/` в pinned tree не обнаружено → лицензия репозитория по умолчанию покрывает и test fixtures, включая выбранный DSDNA8-пакет.
- README pinned commit требует цитирование: Poppleton et al., JOSS 8, 4693 (2023), DOI 10.21105/joss.04693 (код); Rovigatti et al., J. Comput. Chem. 36, 1 (2015), DOI 10.1002/jcc.23763 (CUDA); Poppleton et al., NAR e72 (2020), DOI 10.1093/nar/gkab324 (analysis tools).
- Внутри дерева поставляются сторонние библиотеки (TinyExpr++, nlohmann/json, pybind11, fast_double_parser, zstdpp); авторы заявляют совместимость с их лицензиями. Для NanoLab это фон, не наша обязанность.

### Анализ

- GPLv3 — strong copyleft: распространение fixtures вместе с производными/связанными в единое произведение обязывает распространять соответствующий источник под GPLv3-совместимыми условиями. Если NanoLab выберет пермиссивную лицензию собственного кода, вендоринг GPLv3-файлов внутрь репозитория создаст смешанное произведение и конфликт с Option A/B (см. матрицу).
- Цитирование: обязанность научная/академическая (README), не юридическая блокировка; фиксируется в NOTICE/citation policy.
- Файлы крошечные (4 файла, ~5.2 КБ суммарно), но вопрос не в размере, а в правовом режиме.

### Рекомендация

```text
E1_ACCESS_MODE = DOWNLOAD_ON_SETUP
```

Причина: лицензия известна и разрешает копирование/модификацию/распространение под GPLv3, но NanoLab ещё не выбрал собственную лицензию. До решения владельца безопасный режим — хранить в NanoLab только метаданные (upstream repo, exact commit, exact paths, SHA-256 — уже сохранены в INPUT_AVAILABILITY.md) и загружать файлы в setup/runtime напрямую из upstream по pinned commit с верификацией SHA-256. Вендоринг (`VENDOR_ALLOWED`) возможен позже, если владелец выберет GPL-3.0-совместимую лицензию NanoLab или согласится держать fixtures как изолированный GPLv3-submodule/подкаталог с NOTICE; при Option A/B (Apache/MIT) вендоринг в основное дерево `VENDOR_NOT_RECOMMENDED`.

```text
E1_RIGHTS = CLEAR (GPL-3.0; redistribution allowed under GPLv3 terms; attribution/citation required)
```

Влияние на NL1: setup-скрипт NL1-001 должен скачивать 4 файла по exact commit и сверять SHA-256; это уже соответствует сохранённым identities.

## 2. E2 — DNA-hinge-simulations (Shi–Castro–Arya)

Субъект: `gauravarya77/DNA-hinge-simulations` @ `23fd1ff7731e9017bd776f49206dc42d70d9fe91` (tree `b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9`).

### Независимо установленные факты (GitHub API, live-проверка)

- Полный корневой tree pinned commit: только `Design_Hinges/`, `Init_Hinges/`, `MD_Hinges/`, `MovieS1.mp4`, `README.md`. Ни одного `LICENSE`, `COPYING`, `NOTICE` нет ни в корне, ни в подкаталогах.
- GitHub repo metadata: поле license пустое (нет детекции). Репозиторий не обновлялся с 2017-04-04 — рассчитывать на «появится позже» нельзя.
- Все README (root + 3 подкаталога) прочитаны полностью: только описание файлов, никаких licensing/rights statements.
- Подтверждено содержимое: 5 caDNAno `.json` (173–174 КБ), `cadnano_interface.py` (56 КБ), `init_generator.py`, `ini_demo/`, 5 пар `.top/.conf` (`.conf` ≈ 2.3 МБ каждый), `pro_CPU.in`, `pro_GPU.in`, `MovieS1.mp4`.
- Статья DOI 10.1021/acsnano.7b00242 связана с репозиторием; сама статья — ACS copyright, её условия не переносятся на repository files и наоборот.

### Анализ

- Нет лицензии → по умолчанию all rights reserved у авторов. GitHub ToS позволяют view/fork внутри GitHub, но не дают NanoLab права перераспространять, модифицировать и публиковать эти файлы или включать их в свой release.
- Отдельно: `MovieS1.mp4` — media, статья — publisher copyright; никогда не переносить в NanoLab.
- Скрипты (`cadnano_interface.py` — модифицированный конвертер; происхождение исходного caDNAno-кода отдельно не установлено) — code без лицензии, тоже UNKNOWN.

### Статусы

```text
can fetch (user-side download from author repo by exact commit) = YES (public access confirmed)
can cite/reference (bibliographic, DOI + repo + commit)           = YES
can redistribute                                                  = NO (not established)
can modify / derive                                               = NO (not established)
can include in NanoLab release                                    = NO (not established)
can mirror publicly                                               = NO (not established)
can cache privately for local execution                           = GREY (private ephemeral use for a
                                                                    lawful scientific purpose is a
                                                                    defensible reading, but is NOT a
                                                                    redistribution right; treat as
                                                                    owner-decision before any durable cache)
REDISTRIBUTION_RIGHTS = UNKNOWN
```

### Рекомендация

```text
E2_ACCESS_MODE = REFERENCE_ONLY + download from author repository by exact commit (user-side)
```

NanoLab хранит только repo/commit/tree refs и уже записанные blob identities; runtime/setup скачивает файлы напрямую из авторского репозитория пользователем, локально, без re-publication. Любое копирование в NanoLab-репозиторий, публичный mirror, CDN-кэш или release-asset — только после явного разрешения авторов (issue/email к владельцу репозитория) или решения владельца NanoLab.

```text
E2_RIGHTS = UNKNOWN → REQUIRES_OWNER_DECISION (contact authors; no license in pinned tree)
```

Влияние на NL1/NL3: (a) NL1 setup должен уметь скачивать E2-пакет по pinned commit с верификацией по записанным blob SHA-1; (b) публичный «скачай benchmark одной командой» для E2 обещать нельзя до разрешения; (c) любые производные design-файлы NanoLab, построенные поверх caDNAno-дизайнов авторов, — отдельный правовой вопрос (derivative work), решить до NL3-001.

## 3. S08 — Sharma et al. 10.1021/acsnano.7b06470

Роль: scientific reference, не executable seed. Bounded проверка NL0-001 подтверждается без расширения поиска:

- Article access: publisher page публична; SI (PDF с definitions/results) и movies перечислены публично.
- Movies/SI — ACS copyright: ссылаться/цитировать можно, копировать/перераспространять — нет.
- Machine-readable input pack: `INPUT_PACK_NOT_LOCATED` (не `NO_DATA_EXISTS`); bounded поиск в этом исполнении не расширялся — сохранена прежняя формулировка.
- Citation obligation: стандартная академическая (DOI) при научном использовании.

```text
S08_RIGHTS = RESTRICTED (article/SI/movies under publisher copyright; reference & cite only)
```

## 4. NANOBASE

- Прямая проверка nanobase.org из этого окружения не выполнена (сайт недоступен из сетевого контура исполнения). Публикация NANOBASE (PMC8728195, S10) фиксирует: copyright на deposited structures остаётся у авторов соответствующих публикаций.
- Ключевое различие сохраняется: лицензия/условия сайта базы ≠ лицензия софта базы ≠ права на конкретный uploaded structure ≠ copyright статьи-источника. Ни один deposited design нельзя считать перераспространяемым без проверки конкретной записи.
- Режим по умолчанию для любых будущих кандидатов: `REFERENCE_ONLY` + проверка прав конкретной записи до копирования.

```text
NANOBASE_RIGHTS = UNKNOWN per-structure (REQUIRES per-record check; site license ≠ structure rights)
```

## 5. Leaf-spring benchmark (S17, будущий)

`sulcgroup/hinges` — LICENSE в root не наблюдался в NL0-001 inspection; права остаются UNKNOWN до активации этого benchmark. Zenodo-архивы требуют отдельной проверки лицензии записи при активации. За пределами текущего MVP-scope; в матрицу зависимостей не входит.

## 6. Сводка режимов доступа

| Субъект | Access mode | Redistribution | Статус |
|---|---|---|---|
| E1 DSDNA8 fixtures | DOWNLOAD_ON_SETUP | allowed under GPLv3 | CLEAR |
| E2 hinge pack | REFERENCE_ONLY + user-side download | not established | UNKNOWN → OWNER_DECISION |
| S08 article/SI/movies | REFERENCE_ONLY | no (publisher copyright) | RESTRICTED |
| NANOBASE structures | REFERENCE_ONLY per record | per-record unknown | UNKNOWN |
| S17 hinges repo/zenodo | deferred | unknown | UNKNOWN (deferred) |

## 7. Решения, которые должен принять владелец NanoLab

1. Контактовать авторов `DNA-hinge-simulations` с запросом явной лицензии (или письменного разрешения) на использование/redistribution hinge-пакета; альтернатива — replace E2 seed на открытый источник в NL3.
2. Выбрать лицензию NanoLab (см. OPTIONS в `DEPENDENCY_LICENSE_MATRIX.md` §3): этот выбор определяет, допустим ли вендоринг GPLv3-fixtures в основном дереве.
3. Решить политику private caching сторонних UNKNOWN-файлов (allow/deny durable cache до получения прав).
4. При активации NANOBASE/S17 — per-record rights check как обязательный шаг.

## 8. Ограничения

- GitHub API и web-поиск — через доступный сетевой контур; nanobase.org недоступен напрямую (зафиксировано, обойдено публикацией S10).
- Это не юридическое заключение; неоднозначные случаи помечены, а не решены.
- Проверены pinned commits; движение upstream после них не отслеживалось (для E2 репозиторий статичен с 2017).
- Environment incident: внешняя реструктуризация рабочего каталога во время исполнения привела к потере двух несоммиченных файлов; они восстановлены дословно из сессионного содержимого и закоммичены (см. event 0002). Remote branch и START commit не пострадали.
