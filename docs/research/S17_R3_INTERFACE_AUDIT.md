# S17 R3 — Targeted Interface Audit: DNA nanoengine driver ↔ passive follower

Work Order: `WO-PREP-S17-R3` (execution `EX-PREP-S17-R3`, branch `work/prep-s17-r3-r1`).
Дата: 2026-10-18. Язык отчёта — русский; идентификаторы/статусы — английские.

## 0. Резюме (verdict)

Молекулярный интерфейс driver–follower в S17 (Centola et al.) **восстановлен на уровне
последовательностей с статусами `SOURCE_CONFIRMED`**:

1. **Тип соединения:** ДНК-гибридизация комплементарных ssDNA-оверхэнгов — 10 уникальных
   пар (5 на каждую из двух жёстких origami-arm каждого из двух объектов). Никакой
   ковалентной сшивки, mechanical interlocking или иного типа соединения для D–F
   интерфейса в источниках нет. **D–F driver = nNE** (nicked nanoengine с
   транскрибируемой последовательностью), follower = пассивная origami аналогичной формы.
2. **Последовательности интерфейса восстановлены полностью**: 10 driver connecting ODN
   (4 с LNA-модификациями) + 10 follower connecting ODN из pinned
   `Suppl. Dataset S1 V3.docx` (sha256 байт-в-байт равен R1-пину). Машино-проверено:
   каждая пара даёт **точный 20-nt reverse-complement match**, партнерство уникально
   (второй лучший candidate ≤ 8 nt) — см.
   `docs/work/executions/EX-PREP-S17-R3/evidence/s17-r3-df-interface-recipe.json`.
3. **Структура follower НЕ опубликована**: ни topology, ни configuration, ни caDNAno
   файл follower не существует ни в одном аудитированном источнике (Nanobase 196,
   Zenodo 8248808 полные CD-перечисления, `sulcgroup/hinges`, supplementary).
   Follower известен только как список ODN (Minimal staple mix + auxiliary +
   connecting) без scaffold-схемы. Следовательно, **оригинальная S17 D–F статическая
   сборка = `NOT_RECONSTRUCTED`**; интерфейс — `SOURCE_CONFIRMED` на уровне
   последовательностей, nucleotide-index anchors в `nNE.top` — `UNKNOWN`.

Статическая сборка (`ASSEMBLED_STATIC_ONLY`), даже если бы была возможна, не является
`ASSEMBLY_VALIDATED` и не доказывает передачу движения.

## 1. Метод и границы

Targeted source audit по 8 вопросам миссии (§4) с полным pin-протоколированием. Все
загрузки — bounded: суммарно ≈ **48.3 MiB** (статья HTML 0.56 MB, supplementary PDF
13.9 MB, datasets MOESM2–9 ≈ 33.4 MB, Dataset S1 docx 0.10 MB, API calls < 0.1 MB)
из бюджета ≤ 256 MiB. Полные archive-файлы Zenodo НЕ скачивались (отрицательный
перечень R2 переиспользован). `sulcgroup/hinges` просматривался через GitHub API/raw
REFERENCE_ONLY (безлицензионный код не копировался в NanoLab).

## 2. Sources audited (pin-таблица)

| Источник | URL / DOI | Версия / SHA-256 | Права |
|---|---|---|---|
| Основная статья | [10.1038/s41565-023-01516-x](https://www.nature.com/articles/s41565-023-01516-x) | HTML fetch 2026-10-18, `e6f49f5d4d272db6…` (страница VoR, license CC BY 4.0) | CC BY 4.0 |
| Supplementary Information (SI PDF) | `…/41565_2023_1516_MOESM1_ESM.pdf` | `66074e7d0c07139e…`, 13,861,585 B | CC BY 4.0 |
| Suppl. Dataset S1 (ODN-списки) | Nanobase `…/196/expProtocol/Suppl.%20Dataset%20S1%20V3.docx` | `dc3cc6c53a9a1166…`, 101,900 B — **байт-в-байт равен R1-пину** | CC BY 4.0 |
| Suppl. Dataset S1 (PDF-версия) | `…/41565_2023_1516_MOESM4_ESM.pdf` | `04793a32c8f02587…`, 386,233 B (то же содержание, другой формат) | CC BY 4.0 |
| Suppl. constructs glossary I–X | `…/MOESM6_ESM.pdf` | `8887c18c95a36c87…` | CC BY 4.0 |
| Suppl. figures (incl. S5) | `…/MOESM5_ESM.pdf` | `dae20e281294ffa1…` | CC BY 4.0 |
| Suppl. angle datasets (xlsx, sheets "Figure 6 f, g", "Figure 6 h") | `…/MOESM7_ESM.xlsx` | `a9d0024419b59542…` | CC BY 4.0 |
| caDNAno design (Nanobase) | `…/196/structure/NE_halo_dsDNA.json` | `8cbc247002158dc4…` — **байт-в-байт равен R1-пину** | CC BY 4.0 (by Nanobase terms) |
| Analysis repo | `sulcgroup/hinges` @ `7c8b04a654b2440e4b6bab5b0abcb7e4335824d9` (tree через GitHub API, `fb5ef0d2c8017c8f…` ответа) | **NO LICENSE — REFERENCE_ONLY** | all rights reserved |
| Zenodo record 8248808 | `10.5281/zenodo.8248808` | полные CD-перечисления из R2 (4 архива, 2,324 записи); новых загрузок архивов нет | CC-BY-4.0 |

Скачанные файлы хранились только как временные материалы аудита (в Git не вендорятся);
в evidence попадают только digests и цитаты ≤ 100 B.

## 3. Восстановленный интерфейс (главные результаты)

### 3.1 Механизм соединения — `SOURCE_CONFIRMED`

Методы статьи, раздел **"Assembly of the D–F system"** (дословно, проверено по fetched HTML):

> "We added five unique ssDNA overhangs to the axial extremities of each origami arm of
> both D and F (Fig. 6a–c, pink). Each of these in total ten ssDNA sequences in D allow
> for the hybridization of only the complementary ten ssDNA sequences on F to form the
> rhomboid-shaped heterodimer D–F (Fig. 6c–e); formation of the homodimers D–D or F–F is
> impeded due to the non-complementarity of the sequences (Supplementary Fig. 5a,b).
> To strengthen the connection between D and F, three LNA modifications were included in
> two of the overhanging sequences on each D arm that connect to F (Supplementary Fig. 5b,
> red). The purified driver and follower origami were combined equimolarly without further
> dilution and incubated at 30 °C over 2 h…"

Fact table:

| # | Факт | Статус | Локация доказательства |
|---|---|---|---|
| F1 | Соединение = гибридизация 10 комплементарных ssDNA-оверхэнговых пар; гомодимеры исключены некомплементарностью | `SOURCE_CONFIRMED` | Article Methods "Assembly of the D–F system"; Fig. 6a–c caption |
| F2 | По 5 оверхэнгов на каждую из двух arm, в **осевых оконечностях** arm у обоих объектов | `SOURCE_CONFIRMED` | Methods + Fig. 6 caption ("axial extremities", "Five ssDNA overhangs (red arrows)…on each arm") |
| F3 | 4 driver-ODN несут по 3 LNA (2 оверхэнга на каждую D-arm); запись `(L#)` в Dataset S1 | `SOURCE_CONFIRMED` | Methods (цитата выше) + Dataset S1 `*-con-D-LNA` (ровно 4 последовательности, по 3 `(LX)`) |
| F4 | D–F гетеродимер ромбовидный; сборка equimolar, 30 °C, 2 h; connecting ODN добавляются при сборке origami в 2× эквивалентах к прочим стейплам | `SOURCE_CONFIRMED` | Methods; SI Methods "Assembly of the DNA origami" (стр. 9 SI PDF) |
| F5 | Yield корректного D–F дуплекса 60% ± 20% (199 TEM micrographs, n = 2,718) | `SOURCE_CONFIRMED` | Article §"An nNE driver can transfer…"; SI Methods "Evaluation of the yield…" (стр. 12); Ext. Data Fig. 8a; Suppl. Dataset S5 |
| F6 | Driver = nNE ("we coupled the nNE to a similarly shaped, but passive 'follower'"); follower варианты: F (rigid, dsDNA hinge), F-soft-hinge, F-ss-hinge | `SOURCE_CONFIRMED` | Article §Fig. 6 + Dataset S1 sections "Driver" (содержит "Transcribable sequence for the nNE"), "Follower", "Soft-hinge Follower", "Single-strand-hinge Follower" |
| F7 | Передаваемая степень свободы = интерармный угол ромбоидного димера: без транскрипции медиана 64.73°, с транскрипцией 51.66° (n = 1,074/1,190; P = 8×10⁻⁶⁴) | `SOURCE_CONFIRMED` | Fig. 6f,g; данные — MOESM7.xlsx sheet "Figure 6 f, g" |
| F8 | Скорость транскрипции D–F ≈ 1.10–1.16× от D (Fig. 6h); интерпретация — Suppl. Text 7 | `SOURCE_CONFIRMED` | Fig. 6h caption + SI Suppl. Text 7 |
| F9 | Ориентация сборки: "it is necessary to flip one of the two units upside down to be able to join the structures"; helix-нумерация 0–17 эквивалентна в обоих объектах | `SOURCE_CONFIRMED` (текст caption) | SI Suppl. Fig. S5a caption |
| F10 | Connecting ODN — это стейплы оверхэнгов, добавляемые при сборке каждого origami (не отдельные bridge-олиги пост-фактум) | `INFERRED_CANDIDATE` | SI Methods "Driver and Follower origami were assembled by adding twice the amount of the connecting ODN compared to the other staples" — формулировка о добавлении при сборке; прямая схема каждого стейпла — только bitmap Suppl. Fig. S5b |

### 3.2 Машино-проверенная карта 10 пар — последовательности `SOURCE_CONFIRMED`, привязка к helix/индексам см. §3.3

Источник последовательностей: Dataset S1 (sha256 `dc3cc6c5…` = R1 pin), разделы
"Connecting ODN for the Driver" (10 ODN) и "Connecting ODN for the Follower" (10 ODN;
идентичны для F, F-soft-hinge, F-ss-hinge — проверено построчным сравнением секций).

Детерминированная проверка (offline-скрипт, документирован в recipe JSON): для всех
10×10 комбинаций driver×follower ODN вычислен максимальный точный reverse-complement
match по полным LNA-stripped последовательностям. Результат — совершенное паросочетание:
**каждая из 10 пар — точный 20-nt match, партнерство строго уникально** (второй лучший
кандидат 6–8 nt). Полные последовательности, offsets, концы оверхэнгов:
`evidence/s17-r3-df-interface-recipe.json`. Сводка:

| # | Driver ODN (overhang end) | Follower ODN (overhang end) | Match |
|---|---|---|---|
| 1 | HI-MC-163-con-D-LNA (3′) | Hi-MC-173-con-replica (3′) | 20/20 |
| 2 | Hi-MC-165-con-D-LNA (3′) | Hi-MC-174-con-replica (3′) | 20/20 |
| 3 | Hi-MC-174-con-D-LNA (3′) | Hi-MC-165-con-replica (3′) | 20/20 |
| 4 | Hi-MC-173-con-D-LNA (3′) | HI-MC-163-con-replica (3′) | 20/20 |
| 5 | HI-MC-172-con-driver (3′) | Hi-MC-164-con-replica (3′) | 20/20 |
| 6 | Hi-MC-151-con-drive (3′) | Hi-MC-149-con-replica (3′) | 20/20 |
| 7 | Hi-MC-153-con-drive (5′) | Hi-MC-89-con-replica (5′) | 20/20 |
| 8 | Hi-MC-89-con-drive (5′) | Hi-MC-153-con-replica (5′) | 20/20 |
| 9 | Hi-MC-149-con-drive (3′) | Hi-MC-151-con-replica (3′) | 20/20 |
| 10 | Hi-MC-164-con-driver (3′) | HI-MC-172-con-replica (3′) | 20/20 |

Наблюдения (не претендуют на статус выше `INFERRED_CANDIDATE`):

- Кросс-нумерация пар (151↔149, 153↔89, 172↔164, 163↔173, 165↔174) объясняет, почему
  R2 не нашёл bridge-ODN по same-number matching: пары комплементарны «через один».
- D-89/F-89 разделяют идентичный 48-nt сегмент тела стейпла, D-153/F-153 — идентичный
  35-nt 3′-сегмент (следствие «similarly shaped» follower: тела части стейплов
  совпадают). Это согласуется с F10, но само по себе не является доказательством.
- Отсутствие same-number комплементарности исключает D–D/F–F гомодимеризацию по этим
  парам — независимое подтверждение цитируемого в F1 утверждения.

### 3.3 Что осталось UNKNOWN после полного разрешения последовательностей

| Вопрос | Статус | Причина / путь закрытия |
|---|---|---|
| Nucleotide-index anchors connecting-ODN в `nNE.top` (какие частицы несут оверхэнги) | `UNKNOWN` | Все pinned-топологии несут placeholder-последовательности (R2); sequence-localization невозможна. Путь: запросить у авторов caDNAno-файл nNE-драйвера **с** connecting ODN или exact scaffold coordinate map |
| Per-ODN helix/arm assignment (какой ODN на какой helix 0–17) | `INFERRED_CANDIDATE` | Читается только с bitmap Suppl. Fig. S5a; машиночитаемой таблицы нет |
| Точная 3D-ориентация каждого порта (векторы осей, «flip upside down» в координатах) | `UNKNOWN` | Нет координат follower и нет annotated design driver с оверхэнгами; есть только качественный текст F9 |
| Топология/конфигурация follower (F, F-soft-hinge, F-ss-hinge) | `NOT_RECONSTRUCTED` | Файлов не существует в аудитированных источниках (см. §3.4); есть только ODN-списки (Minimal staple mix не полон без схемы scaffold-маршрутизации) |
| Термодинамика/кинетика гибридизации 10 пар (CG, времена) | `UNKNOWN` | Не опубликованы; вне claim-потолка R3 |
| Экспериментальные данные, ограничивающие интерфейс | есть (F5–F7) | TEM yield 60%±20%, угловые распределения, скорость транскрипции — количественные ограничения на результат сборки, не на координаты портов |

### 3.4 Driver–follower структура: отрицательные результаты (переиспользованы + расширены)

- Zenodo 8248808: полные CD-перечисления всех 4 архивов (276+207+949+894 записи) не
  содержат ни одного driver/follower каталога или файла (R2 receipt, re-verified без
  новых загрузок).
- `sulcgroup/hinges` @ `7c8b04a6`: файлы `data/driver_data.txt`, `data/follower_data.txt`,
  `data/driver_pull16_fine_data.txt`, `data/driver_release_fine_data.txt`,
  `data/driver_NB_release_fine_data.txt`, `data/follower_pull16_fine_data.txt`,
  `data/follower_release_fine_data.txt`, `data/follower_NB_release_fine_data.txt` —
  **обработанные угловые временные ряды** (одно число на колонку), НЕ структуры
  (проверено чтением заголовков на pinned commit; REFERENCE_ONLY).
- Nanobase 196: полный 12-файловый набор не содержит follower structure/design.
- Supplementary: follower задан только ODN-списками (Dataset S1); caDNAno-design
  (NE_halo_dsDNA.json, R1 pin) **не содержит ни одного connecting-сегмента**
  (проверено подстрочным поиском всех 10 driver overhang-сегментов в файле — 0/10),
  т.е. это дизайн движка без D–F оверхэнгов.
- Внутренний bridge-ODN механизм движка (dsDNA-t/транскрипционный шаблон, promoter,
  HT-T7RNAP attachment) — **отдельный** интерфейс внутри D; R2-вывод «bridge-ODN ports
  UNKNOWN» относится к нему и не смешивается с D–F connecting ODN.

## 4. Ответы на 8 вопросов миссии (сводно)

1. **Как driver соединяется с follower:** гибридизация 10 комплементарных ssDNA
   оверхэнговых пар (5 на arm), сформированных connecting ODN-стейплами — F1–F2.
2. **Тип взаимодействия:** DNA hybridization (non-covalent); LNA-стабилизация 4
   driver-оверхэнгов — F1, F3. Ковалентных связей/interlocking нет.
3. **Нити и последовательности интерфейса:** 20 ODN (10 driver + 10 follower),
   полные последовательности в recipe JSON — `SOURCE_CONFIRMED`.
4. **Ориентация и геометрия соединения:** осевые оконечности arm; ромбовидный
   гетеродимер; один объект нужно «flip upside down»; helix-нумерация 0–17
   эквивалентна — F2, F9. Точные векторы — UNKNOWN.
5. **Механическая DOF, передающая движение:** интерармный угол (pulsation) D,
   передающийся углу ромбоидного D–F димера; сдвиг медианы 64.73°→51.66° под
   транскрипцией — F6, F7.
6. **Исходная структура follower:** отсутствует — только ODN-списки трёх вариантов
   (F, F-soft-hinge, F-ss-hinge); топология/конфигурация NOT_RECONSTRUCTED (§3.4).
7. **Экспериментальные данные для ограничения интерфейса:** TEM yield 60%±20%;
   угловые распределения (Dataset S4/MOESM7); скорость транскрипции D–F vs D — F5–F8.
8. **Подтверждено vs гипотеза:** §3.1–3.3 (подтверждено: механизм, последовательности,
   пары, протокол, yield; гипотеза/UNKNOWN: индексные якоря, helix-привязка, 3D
   ориентация, follower-структура, термодинамика).

## 5. Вопросы авторам (draft, НЕ отправляется — требуется owner approval)

1. Можете ли вы опубликовать caDNAno/scadnano-дизайн nNE driver **с** connecting ODN и
   follower (F, F-soft-hinge, F-ss-hinge), либо scaffold-coordinate map connecting ODN?
2. Подтвердите, какие из 10 connecting ODN относятся к какой arm/helix (0–17) —
   машиночитаемую таблицу вместо Suppl. Fig. 5a bitmap.
3. Подтвердите ориентацию (5′/3′) каждого оверхэнга и «flip» преобразование для сборки
   D–F в координатах design.
4. Опубликованы ли где-либо .top/.dat или oxDNA/caDNAno файлы follower? (Во всех
   аудитированных поверхностях их нет.)
5. Внутренняя терминология: «connecting ODN» добавляются при сборке каждого origami
   (SI Methods) — верно ли, что D–F пост-сборка не использует отдельных bridge-олигов?
6. Temperatурный протокол сборки D–F (30 °C 2 h) — использовался ли annealing ramp
   для соединения (Fig. 6c упоминает «thermal annealing overnight»)?

Контакт-план: через corresponding author (M. Famulok) / GitHub issues репозиториев
`sulcgroup/hinges`, `walterlab-um/rhythmically-pulsing-leaf-spring_SMCodes`. Отправка —
только после явного разрешения владельца (без external messages из этой сессии).

## 6. Бюджет и следы

Сетевая передача аудита: **≈48.3 MiB** уникальных байтов (список в
`evidence/s17-r3-fetch-manifest.json`); научных прогонов 0; raw-файлы в Git не
вендорятся; статусы NL5/NL6 не изменялись.
