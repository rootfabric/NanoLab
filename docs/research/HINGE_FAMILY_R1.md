# HINGE_FAMILY_R1 — Регистрация семейства шарниров Shi–Castro–Arya

Идентификатор: `HINGE_FAMILY_R1`. Work Order: `NL3-001`. Исполнение: `EX-NL3-001-R1`. Ветка: `work/nl3-001-hinge-family-r1`. Дата: 2026-09-10. Статус: **регистрация опубликована; кампания E2 = NOT_RUN; научных прогонов нет**.

Этот документ фиксирует семейство конструкций «семейство → parameter space → первый экземпляр `0b`» для последующей кампании E2 ([E2_HINGE_COMPONENT](../experiments/E2_HINGE_COMPONENT.md), постановка [E2_SETUP_R1](E2_SETUP_R1.md)). Он **не** является пререгистрацией кампании: tolerances, число повторов, целевой интервал угла и пороги целостности остаются за `E2-PROTO-*` (открытые вопросы E2-SETUP-R1 §10 не закрыты здесь).

Каждая числовая позиция несёт класс данных: **REPORTED** (утверждение статьи, NanoLab не видел первоисточник напрямую), **OBSERVED** (прямо измерено в pinned-объектах источника или вычислено из них), **UNKNOWN** (неизвестно; не заполняется). Политика неизвестных значений: `UNKNOWN` не является разрешением и не заменяется правдоподобным значением.

## 1. Источник и права

```text
SOURCE      = Shi, Castro, Arya, "Conformational Dynamics of Mechanically Compliant DNA
              Nanostructures from Coarse-Grained Molecular Dynamics Simulations",
              DOI 10.1021/acsnano.7b00242 (SOURCES S16)
REPO        = gauravarya77/DNA-hinge-simulations
PIN         = commit 23fd1ff7731e9017bd776f49206dc42d70d9fe91
              tree   b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9
RIGHTS      = REDISTRIBUTION_RIGHTS = UNKNOWN → режим REFERENCE_ONLY
              (NL0-002: LICENSE отсутствует во всём pinned tree; GitHub visibility ≠ лицензия)
MODE        = user-side download by exact commit; копирование/mirror/vendor в NanoLab запрещены;
              durable private caching UNKNOWN-rights файлов — открытое owner-решение (с NL0-002)
```

R1-подтверждение (EX-NL3-001-R1): pinned commit существует, его tree совпадает с preregistered `b2d6ceb…` (полный API-перечёт дерева, не truncated); preregistered blob'ы NL0-001 (`Design_Hinges/0b.json` = `0ed4075c…`, `MD_Hinges/pro_CPU.in` = `89d76310…`) совпали бит-в-бит при повторном получении.

## 2. Семейство

Пять опубликованных вариантов [E2_SETUP_R1 §7; NL0-001]:

| Вариант | Spring layers, bases (REPORTED) | Роль в регистрации | Machine-check в R1 |
|---|---|---|---|
| `0b` | 0/24 | **первый экземпляр** (контрольный, нулевая вставка, наименьший) | да — см. §5 |
| `11b` | 11/35 | зарегистрирован, не валидирован | нет (digest-пины есть, содержимое не анализировалось) |
| `32b` | 32/56 | зарегистрирован, не валидирован | нет |
| `53b` | 53/77 | зарегистрирован, не валидирован | нет |
| `74b` | 74/84 | зарегистрирован, не валидирован | нет |

Spring layers — REPORTED из статьи через NL0-001; в R1 машинно проверяется только косвенная корроборация стороны «0» варианта `0b`: имя caDNAno-дизайна внутри файла — `0bp_6x3_v2.json` (OBSERVED). Отнесение конкретных ssDNA-участков дизайна к «spring layers» без SI статьи невозможно — см. §7 (gap G3).

OBSERVED-состав pinned tree (ключевой состав, R1; полный перечень поверхности — GitHub API tree `b2d6ceb…`, `truncated=false`, 33 entries, включает и не вошедшее в перечень ниже: `Design_Hinges/README.md` (268 B) и конкретное содержимое `Init_Hinges/` — README.md, `cadnano_interface.py`, `init_generator.py`, `ini_demo/*`; errata F-2, Director r1-errata): `Design_Hinges/{0b,11b,32b,53b,74b}.json`, `MD_Hinges/{0b,11b,32b,53b,74b}.{top,conf}`, `MD_Hinges/pro_CPU.in`, `MD_Hinges/pro_GPU.in`, `MD_Hinges/README.md`, `Init_Hinges/`, `MovieS1.mp4`, `README.md`. `MD_Hinges/README.md` (OBSERVED текст) описывает `.top` как input topology, `.conf` как restart-файл с координатами и скоростями equilibrated hinge, `pro_CPU.in`/`pro_GPU.in` — как входы MD.

Полный digest-реестр всех 18 зарегистрированных поверхностей — `scripts/hinge_family/source_pins.json` (заморожен): blob SHA-1 с provenance (`NL0_001_PREREGISTERED` / `R1_TREE_LISTING`), SHA-256 с provenance (`R1_CONTENT_VERIFIED` для пяти поверхностей `0b`; `NOT_VERIFIED` для остальных до их собственных процедур получения).

## 3. Parameter space

### 3.1 Параметр семейства

```text
параметр        = длина двух compliant spring layers (bases)
допустимые значения = ТОЛЬКО пять опубликованных дискретных вариантов 0b/11b/32b/53b/74b
                    (REPORTED 0/24, 11/35, 32/56, 53/77, 74/84)
правило изменения   = один параметр за раз; второй — только после проверки первого
                    (E2_SETUP_R1 SS7.2; E2_HINGE_COMPONENT)
монотонность        = НЕ предполагается; отсутствие желаемого тренда — научный результат
вне scope           = новые последовательности, интерполяции длин, «улучшенные» варианты,
                    произвольный генератор конструкций (до воспроизведения опубликованного семейства)
```

### 3.2 Условия (не назначаются здесь; воспроизводятся verbatim)

| Позиция | Значение | Класс | Источник |
|---|---|---|---|
| Движок | oxDNA2 | REPORTED (статья) + OBSERVED (`interaction_type = DNA2` в pinned `pro_CPU.in`) | NL0-001; R1 machine-confirm |
| Температура | статья: 298 K; input: `T = 300K` | REPORTED vs OBSERVED | разрешено decision rule'ом E2-SETUP-R1 §5: reproduction arm = авторские файлы verbatim (300 K), расхождение документируется рядом с каждым результатом, не «исправляется» |
| Соль | статья: 500 mM; input: `salt_concentration = 0.5` | REPORTED vs OBSERVED | соответствие `0.5` ↔ «500 mM» = ASSUMED (mol/L), подтверждается при pinning engine-документации |
| Параметризация | average-base | REPORTED | NL0-001 |
| Шаги production | input: `steps = 2e7` | OBSERVED | machine-confirm R1 |
| Backend/precision | `CPU`, `double` | OBSERVED | machine-confirm R1 |
| Прочие параметры input | `seed = 7777`, `thermostat = john`, `dt = 0.005`, `rcut = 2.0`, `external_forces = 0`, `verlet_skin = 0.05`, `refresh_vel = 1` и др. | OBSERVED | заморожены в pinned `pro_CPU.in`; интерпретации до pinning engine не переизобретаются |

OBSERVED-факт с прямым влиянием на процедуру: **pinned `pro_CPU.in` по умолчанию указывает на `topology = 74b.top`, `conf_file = 74b.conf`**, а не на `0b`. Запуск `0b` требует подстановки путей к файлам `0b` — подстановка, которую E2-SETUP-R1 §5 требует фиксировать явно; здесь она зафиксирована как обязательное документируемое отклонение процедуры от файла-по-умолчанию.

### 3.3 UNKNOWN семейства (не заполняются)

| # | UNKNOWN | Место решения |
|---|---|---|
| U1 | Права redistribution/использования источника | владелец (контакт авторов) — открыто с NL0-002 |
| U2 | Machine-readable определение hinge angle (SI) | pre-E2 WO (получение и pinning SI) |
| U3 | Атрибуция spring layers в файлах (какие ssDNA-участки) | `E2-PROTO-*` / pre-E2 (после SI) |
| U4 | Политика durable private caching | владелец — открыто с NL0-002 |
| U5 | Совместимость `Init_Hinges/` (2017) с pinned engine `00dc7fb9` | pre-E2 compatibility audit |
| U6 | Точное соответствие «design path → topology strand» (см. G2) | pre-E2 compatibility audit (нужны авторские скрипты/последовательности) |

## 4. Первый экземпляр `0b` — выбор и дайджесты

Выбор `0b` зафиксирован постановкой E2-SETUP-R1 §2 до любых данных и не пересматривается: контрольный вариант без вставки, наименьший в семействе, естественная baseline-точка для параметрического сравнения.

Digest-реестр поверхностей `0b` (заморожен в `source_pins.json`; каждый digest верифицируется перед каждым использованием):

| Файл | Размер, B | Git blob SHA-1 | SHA-256 | Provenance |
|---|---:|---|---|---|
| `MD_Hinges/0b.top` | 120 204 | `84edad43593f1d5eb9debb9493a7bd86d743e44b` | `cd0461275e69a452cedba4586af55b1f8f6b857ab1737f374daf46c389aae01f` | blob: R1 tree-listing; sha256: R1 content-verified |
| `MD_Hinges/0b.conf` | 2 294 162 | `181373f0eb16fb90b0b8c66fe5cbf658cc6134da` | `506c41fccd45c09958c5c74399b33018bb370719a32615dd57ed588f73bfd263` | blob: R1 tree-listing; sha256: R1 content-verified |
| `Design_Hinges/0b.json` | 173 059 | `0ed4075c3a0d2f29601d35c5ce70f2df6b0be1ed` | `e855097d51d994bf0aad3d526d410b73f46c7c0355de68bb73acac0efef2abcf` | blob: **NL0-001 preregistered** (совпал); sha256: R1 content-verified |
| `MD_Hinges/pro_CPU.in` | 933 | `89d76310ce726eaec9e7acb312bd7b0fc43fa735` | `bd6cd4181403128cc67f433d6439f20509a9ade60a720017b0db763507f5e673` | blob: **NL0-001 preregistered** (совпал); sha256: R1 content-verified |
| `MD_Hinges/README.md` | 1 335 | `16b747d15c6a86300512af3f62045bd717dc406b` | `6627959e957d10a1d74d2d93f5ae1fb129441bc93496ab72cb53519b458b72bb` | blob: R1 tree-listing; sha256: R1 content-verified |

Порядок получения (разрешённая процедура, без вендоринга): user-side download по exact pinned commit (например, `raw.githubusercontent.com/gauravarya77/DNA-hinge-simulations/23fd1ff…/<path>`) в каталог **вне** любого репозитория NanoLab → сверка размера/SHA-256/blob SHA-1 с реестром → только затем использование. Файлы не коммитятся и durably не кэшируются (U4).

## 5. Структурное воспроизведение `0b` (R1, без динамики)

Инструмент: замороженный детерминированный пакет `scripts/hinge_family/` (stdlib-only): digest-гейт → строгие парсеры → структурные проверки → канонический JSON-отчёт. Запуск R1:

```text
PYTHONPATH=scripts python -m hinge_family validate --source-dir <user-dir> --report <out.json>
exit 0; отчёт: docs/work/executions/EX-NL3-001-R1/evidence/hinge-0b-structural-report.json
детерминизм: два прогона → SHA-256 отчётов совпали (F8EF3EA4…D449A5)
```

Все 8 проверок = PASS на реальных pinned-объектах. Ключевые OBSERVED-факты (полная совокупность — в отчёте):

**Топология `0b.top`**: 8378 нуклеотидов, 112 странд (103 линейных + 9 кольцевых: id 2–7, 42–44); состав A 2081 / C 2076 / G 2075 / T 2146; странд-ids идут сплошными сериями 1..112; взаимная целостность цепей n3/n5 — 0 ошибок; разложение на цепи покрывает все нуклеотиды, максимальная длина 644, минимальная 18.

**Конфигурация `0b.conf`**: 8378 частиц × 15 колонок; `t = 20000000` (совпадает с `steps = 2e7` — restart-файл конца авторского equilibration-прогона); NaN/Inf = 0; две ориентационные тройки — точные единичные и взаимно ортогональные (max отклонение 2.15e-07 при допуске 1e-06); все позиции внутри бокса 402.56³. Раскладка колонок: pos(3), unit(3), unit(3)⊥, две ограниченные velocity-подобные тройки — семантические метки наших чтений конвенций oxDNA, финальное подтверждение — pre-E2 engine-input check (G4).

**Дизайн `0b.json`**: 18 виртуальных хеликсов; scaffold 4266 баз + staples 4112 баз = **8378 баз == 8378 нуклеотидов топологии (точно)**; маршрутизация — 1 scaffold-путь + 117 staple-путей; двунаправленная целостность указателей — 0 ошибок на 8378 ячейках; шагов кроссоверов: scaffold 46 + staple 413 = 459.

**Кросс-чеки и наблюдения** (facts, не критерии приёмки):

| Наблюдение | Значение |
|---|---|
| Дизайн ↔ топология по числу баз | 8378 == 8378, точное совпадение (PASS-проверка) |
| Странды: дизайн vs топология | 118 путей дизайна vs 112 страндов топологии — точное соответствие НЕ декомпозировано (gap G2) |
| Длинные «связи» топологии (dist > 0.95) | 456 (все внутри одного странда) ≈ 459 шагам кроссоверов дизайна — согласуется с кодированием кроссовер-непрерывных цепей; порог 0.95 — конвенция инструмента, не характеристика источника |
| ssDNA-участки дизайна | позиции с одной страндой: 158; серии по хеликсам: {2:×16, 9:×6, 12:×6} — атрибуция к spring layers без SI невозможна (U3/G3) |
| Распределение связанных дистанций | главный пик 0.5–0.6 (4677 из 8275), вторая полоса 1.2–1.7 (440; сумма buckets «1.2»–«1.7» = 19+41+112+159+87+22; значение 448 соответствовало бы buckets ≥ 1.1, включая bucket «1.1» = 8) — OBSERVED-факт авторского pre-equilibrated файла; интерпретация вне scope R1 (errata F-1/V-1, Director r1-errata) |

## 6. Экспорт/воспроизведение: что можно и что нельзя (жёстко)

**Почему НЕ генератор.** Права источника UNKNOWN → генерация `0b` «с нуля» или из caDNAno-дизайна своими скриптами создала бы производный файл, который (а) юридически опирается на UNKNOWN-права, (б) научно был бы reconstruct, а не original — запрещено правилом NL0-001 «reconstruct ≠ original» и постановкой E2-SETUP-R1 §6: reproduction arm стартует **только** с авторских pre-equilibrated `.top`/`.conf` verbatim по exact pinned commit. Поэтому реализована digest-gated **процедура воспроизведения**, а не генератор структуры.

**Можно (разрешено без новых гейтов):**

1. User-side download отдельных файлов по exact pinned commit в каталог вне NanoLab (порядка единиц MB);
2. Digest-верификация каждого файла против `source_pins.json` (size + SHA-256 + git blob SHA-1) — обязательна перед каждым использованием;
3. Структурная валидация замороженным инструментом (топология/конфигурация/дизайн/симуляционный вход) с публикацией **канонического отчёта** в Git;
4. Публикация дайджестов, размеров, структурных фактов и библиографических ссылок (прецедент `INPUT_AVAILABILITY.md`);
5. Детерминированный повтор: два прогона инструмента на тех же байтах → байт-идентичные отчёты (проверено).

**Нельзя (запрещено этим документом):**

1. Коммитить любые байты источника (`.top`, `.conf`, `.json`, `.in`, `MovieS1.mp4`, …) в NanoLab Git — ни целиком, ни частями, ни «временно»;
2. Создавать durable-кэш UNKNOWN-rights файлов до owner-решения (U4);
3. Генерировать «0b» своими средствами и называть его исходным компонентом; выдавать reconstruct за original;
4. Подставлять числовые значения вместо UNKNOWN (угол из SI, атрибуция spring layers, соответствие дизайн↔топология);
5. Молча подменять пути в симуляционном входе (подстановка `74b` → `0b` — обязательное документируемое отклонение);
6. Править published-объекты источника; любое «исправление» = новый superseding-пин с provenance.

## 7. Гэпы R1 (честно; дисциплина S003-класса — без тихих допущений)

| # | Gap | Почему нельзя закрыть сейчас | Куда |
|---|---|---|---|
| G1 | Rights UNKNOWN | нужен явный ответ авторов/владельца | владелец (U1) |
| G2 | Соответствие «путь дизайна → странд топологии» (118 vs 112) не декомпозировано | авторская конверсия `Init_Hinges/` REFERENCE_ONLY, в дизайне нет последовательностей; реверс-инжиниринг конверсии вне scope R1 | pre-E2 compatibility audit (U6) |
| G3 | Spring layers (REPORTED 0/24) не атрибутированы к конкретным ssDNA-сериям | нужен SI/определения статьи | pre-E2 WO + `E2-PROTO-*` (U2/U3) |
| G4 | Семантика колонок 9:15 конфигурации (velocity-подобные) | наши метки — интерпретация конвенций oxDNA; проверка чтением pinned engine — вне R1 | pre-E2 engine-input check |
| G5 | SHA-256 поверхностей `11b/32b/53b/74b` | содержимое в R1 не получалось (scope = первый экземпляр `0b`) | отдельные bounded шаги pre-E2 |
| G6 | Целостность в ране (H-bonds, энергия, динамика) | прогоны динамики = NL3-002/E2 | NL3-002 |

## Errata (r1-errata, Director checkpoint)

Docs-правка от 2026-09-11 (Director; ветка `control/nl3-001-director-checkpoint-r1`) по findings независимого review (`84f71e7`, F-1/F-2) и verification (`a0687b5`, V-1) — класс LOW, точность durable-записи: на вердикты PASS, digest-реестр `source_pins.json` и published-отчёт не влияет (те заморожены и настоящей правкой не тронуты); затронут только prose этого документа:

- **F-1**: §5 «главный пик 0.5–0.6» — 4657 → **4677** (bucket «0.5» published-отчёта `hinge-0b-structural-report.json`; ошибка перепечатки prose, ни один PASS-check на этом числе не стоит).
- **F-2**: §2 «полный перечёт» → «ключевой состав»; полный перечень — GitHub API tree `b2d6ceb…` (`truncated=false`, 33 entries); вне перечня остаются `Design_Hinges/README.md` (268 B) и конкретное содержимое `Init_Hinges/`. На реестр «ровно 18 зарегистрированных поверхностей» не влияет.
- **V-1**: §5 «вторая полоса 1.2–1.7 (≈448)» → **440** с уточнением bucket-семантики (448 = buckets ≥ 1.1, включая bucket «1.1» = 8).

INFO-замечания F-3 (event 0004 перечисляет содержимое records-коммита не полностью), F-4 (CRLF-артефакт `autocrlf=true` — проверку воспроизводимости выполнять по `git cat-file`) и F-5 (два узких тест-пробела) приняты к сведению без правки; F-4/F-5 — кандидаты в pre-E2 инструментальную итерацию. Старые события не редактировались.

## 8. Связи

[WO-NL3-001](../work/WO-NL3-001.md) · [EX-NL3-001-R1](../work/executions/EX-NL3-001-R1/summary.md) · [E2_SETUP_R1](E2_SETUP_R1.md) · [REFERENCE_SELECTION](REFERENCE_SELECTION.md) · [INPUT_AVAILABILITY](INPUT_AVAILABILITY.md) · [SOURCES S16](SOURCES.md) · [RIGHTS_AND_REDISTRIBUTION_AUDIT](RIGHTS_AND_REDISTRIBUTION_AUDIT.md) · [E2_HINGE_COMPONENT](../experiments/E2_HINGE_COMPONENT.md) · [SCIENTIFIC_METHOD](../SCIENTIFIC_METHOD.md) · pins: `scripts/hinge_family/source_pins.json` · отчёт: `docs/work/executions/EX-NL3-001-R1/evidence/hinge-0b-structural-report.json`.
