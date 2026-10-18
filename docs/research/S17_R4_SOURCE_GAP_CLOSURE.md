# S17 R4 — Source Gap Closure: follower-компонент (G1–G4, G6)

Work Order: `WO-PREP-S17-R4-SOURCE-R1` (execution `EX-PREP-S17-R4-SOURCE-R1`, ветка `work/prep-s17-r4-source-r1`).
Дата: 2026-10-18. Язык отчёта — русский; идентификаторы/статусы — английские.
Дополняет: [S17_R3_SOURCE_GAPS.md](https://github.com/rootfabric/NanoLab/blob/main/docs/research/S17_R3_SOURCE_GAPS.md) (git `2cf8297f10ab5ec98b8c8023ff76b39d92ef398b`), [S17_R3_INTERFACE_AUDIT.md](https://github.com/rootfabric/NanoLab/blob/main/docs/research/S17_R3_INTERFACE_AUDIT.md).

## 0. Резюме (verdict)

Оригинальные design-файлы follower (G1) **не существуют ни в одной публичной поверхности** — это
зафиксировано как `BLOCKED_SOURCE` с полной негативной evidenc-машиной
([S17_R4_FOLLOWER_PROVENANCE.json](S17_R4_FOLLOWER_PROVENANCE.json)). Взамен R4 даёт:

1. **Полный pin официального перечня data-поверхностей** (Data availability statement, PMC VoR):
   статья называет ровно три репозитория — Deep Blue Data (smFRET), Nanobase 196 («original design
   file and the edited oxDNA structures»), Zenodo 8248808 (trajectories). Follower design не
   упоминается нигде.
2. **Полная инвентаризация Nanobase**: 109/109 публичных структур перечислены через API —
   follower-записи не существует; в записи 196 ровно 12 файлов, описания явно говорят
   «Cadnano file for the **body** of the NE».
3. **Первая машиночитаемая (в проекте) карта портов** `S17_R4_PORT_CANDIDATES.json`: все 10 пар —
   последовательности `SOURCE_CONFIRMED` (переиспользован R3-recipe), **per-ODN helix/arm
   assignment оцифрован с bitmap Suppl. Fig. S5b** (стр. 19 SI PDF, pin `66074e7d…`) со статусом
   `INFERRED_CANDIDATE` и явными источниками неопределённости; nucleotide-index anchors — `UNKNOWN`;
   3D-ориентация — `UNKNOWN`.
4. **Черновик вопросов авторам** (§5) — расширен по сравнению с R3 конкретными вопросами
   оцифровки; НЕ отправлен (отправка — отдельное решение владельца).
5. Workflow test vehicle (не S17 follower): Nanobase 256/257 (Narcissus/Echo) — опубликованная
   двухкомпонентная система с полными design-файлами обеих половин.

Научных прогонов: **0**. Сеть: **≈20.7 MiB** уникальных загрузок (бюджет ≤256 MiB). Сырые
сторонние файлы в репозиторий не вендорятся (только digests/urls/цитаты ≤100 B).

## 1. Матрица закрытия гэпов

| Gap | Было (R3) | Стало (R4) | Статус | Evidence | Что осталось |
|---|---|---|---|---|---|
| **G1** структура follower (topology/config/caDNAno F, F-soft-hinge, F-ss-hinge) | `NOT_RECONSTRUCTED` | оригинальные файлы **не найдены**; негативное evidence расширено на 10 поверхностей (см. §2) | **`BLOCKED_SOURCE`** | `S17_R4_FOLLOWER_PROVENANCE.json` (verdict + blocked_source_receipt; digests: Nanobase listing `b4c4a645…`, catalog `4637ff04…`, PMC `ead50002…`, Zenodo API `5d26ec0a…`) | существование файлов не исключено только в: Deep Blue 474299762 (Cloudflare-блок из песочницы; по статье это smFRET-данные — низкая вероятность), bioRxiv DC1 (HTTP 403; preprint устарел относительно SI), частные материалы авторов |
| **G2** nucleotide-index anchors connecting-ODN в `nNE.top` | `UNKNOWN` | **не изменился**: все pinned-топологии несут placeholder-последовательности (R2); sequence-localization невозможна; author caDNAno с connecting ODN не найден (см. G1) | **`UNKNOWN`** | R2 pin-таблица (git `26c4cd51`); негативное evidence G1 | то же, что G1: caDNAno/scadnano файл nNE **с** connecting ODN от авторов либо scaffold-coordinate map; после этого индексы восстанавливаются детерминированно (`s17_index_map`) |
| **G3** per-ODN helix/arm assignment | `INFERRED_CANDIDATE` (bitmap, без оцифровки) | **частично закрыт**: все 10 driver-side и все 10 follower-side позиций оцифрованы с Suppl. Fig. S5b и записаны машиночитаемо | **`INFERRED_CANDIDATE`** (те же рамки, но теперь с конкретикой и явными источниками неопределённости) | `S17_R4_PORT_CANDIDATES.json` (pairs[].driver_hop/follower_hop.helix_arm_assignment; figure pin `66074e7d…` p.19) | подтверждение авторов (bitmap скрывает задние helices 18HB; leader-line'ы цепляются за границы кружков; follower нарисован «flip upside down»); 2 задания для авторов в §5 (Q2, Q7) |
| **G4** точная 3D-ориентация портов | `UNKNOWN` | **не изменился**: bitmap даёт только круговую схему (front view), без масштаба/координат; «flip upside down» остаётся качественным текстом | **`UNKNOWN`** | caption Suppl. Fig. S5a/b (цитата в `S17_R4_PORT_CANDIDATES.json` → conventions) | координаты портов восстанавливаются только из design-файлов (G1) или оцифровки с масштабом; после G1+G2 закрывается геометрической проверкой |
| **G6** molecule-level связь «trap ↔ полимераза» с оверхэнгами в одном дизайне | force-пары 8694/7374 `SOURCE_CONFIRMED`; координатная связь — зависимость от G2 | **не изменился** по существу; добавлен pin движковой caDNAno-карты (MOESM5: handle полимеразы «helix 15 → helix 20 на inner face» рядом с транскрибируемой последовательностью) — качественная якорная точка для будущей координатной связки | **`SOURCE_CONFIRMED` (force-пары) + `UNKNOWN` (координаты, = G2)** | MOESM5 pin `dae20e28…` (стр. 1, подпись к карте) + R2 `S17_R2_PORT_MAP.json` | как G2 — из design-файлов; качественный anchor (h15→h20) уже pinned |

Вне scope R4 (как и в R3): **G5** термодинамика/кинетика 10 пар гибридизации — не опубликованы,
закрытие вне claim-потолка PREP (отдельный научный WO после NL6/E5 разблокировки).

## 2. Негативное evidence по G1 (что искали, что отсутствовало)

Полная машина — `blocked_source_receipt` в
[S17_R4_FOLLOWER_PROVENANCE.json](S17_R4_FOLLOWER_PROVENANCE.json). Кратко:

| Поверхность | Запрос/метод | Результат |
|---|---|---|
| Статья (PMC VoR `ead50002…`) | чтение Data/Code availability | ровно 3 репозитория; follower design не упомянут |
| Nanobase 196 (`b4c4a645…`) | `structure-files?id=196` | 12 файлов, 0 follower; «Cadnano file for the body of the NE» |
| Nanobase каталог (`4637ff04…`) | 109/109 структур + keyword scan (engine/follower/leaf/hinge/rotor/Centola/Famulok/Poppleton/Sulc/driver) | follower-записи нет |
| Zenodo 8248808 (`5d26ec0a…`) | API metadata + переиспользование R2-перечислений 4 архивов (2,324 записи) | без новых версий и related id; 0 follower-членов |
| Zenodo поиск (`c22d3c43…`) | leaf-spring OR nanoengine OR hinges (1,685 hits) | кроме 8248808 — нерелевантно |
| `sulcgroup/hinges` @ `7c8b04a6` (`fb5ef0d2…`) | полное дерево 83 записи, ветка main одна, README | только analysis-скрипты и обработанные углы; 0 design-файлов; README → Google Drive raw trajectories (не перечислим из песочницы; содержание presumed driver-only, `UNVERIFIED`) |
| `walterlab-um/…_SMCodes` (`1f0e12c0…`) | полное дерево 26 файлов, MIT | MATLAB smFRET analysis; 0 design-файлов |
| GitHub repo/user search + web sequence search | `nanoengine origami` (0), 29+25 репо Poppleton/sulcgroup, уникальные 20-mer'ы оверхэнгов, «con-replica»/«con-D-LNA» | ничего; GitHub CODE search недоступен без токена (ограничение зафиксировано) |
| Deep Blue 474299762 | concern/catalog/OAI | Cloudflare JS challenge из песочницы; contents `UNVERIFIED` (по статье — smFRET data) |
| bioRxiv `2021.12.22.473833` | full.pdf, DC1 media-1.pdf | HTTP 403; preprint устарел относительно SI; minor open item |

Позитивные side-результаты для других строк: Dataset S1 и оба SI-PDF перепроверены байт-в-байт
2026-10-18 (`dc3cc6c5…`, `66074e7d…`, `dae20e28…` — идентичны R1/R3-пинам); entry 196 metadata
(депонент Erik Poppleton, lastUpdated 2025-03-10) зафиксирована; MOESM5 опознан как движковая
caDNAno-карта + soft/ss-hinge варианты (поддержка F10).

## 3. Candidate-реконструкция: что можно и чего нельзя

- Построен **только** hypothesis-only «follower interface map» (helix-уровень, 10 ODN) —
  `S17_R4_PORT_CANDIDATES.json → candidate_following_interface_map`, везде помечен
  `CANDIDATE_DESIGN / HYPOTHESIS`.
- **Fabricированный oxDNA `.top`/`.dat` follower НЕ создавался**: без scaffold-маршрутизации
  (Dataset S1 содержит только список стейплов, а «Minimal staple mix» не полон без схемы) любая
  сборка была бы фикцией, претендующей на научный статус — это запрещено (`SCIENTIFIC CLAIM MUST
  NOT EXCEED EVIDENCE`).
- Альтернативный **workflow test vehicle** (явно НЕ S17 follower): Nanobase **256/257
  (Narcissus/Echo)** — опубликованная двухкомпонентная система (две половины-призмы,
  соединяемые гибридизацией по комплементарным интерфейсам; Huang et al. 2024) с **полными**
  design-файлами обеих компонент (oxview + caDNAno-json + staples xlsx). Годится для будущей
  обкатки two-component import/assembly tooling; требует собственного bounded WO (файлы в R4 не
  скачивались).

## 4. Бюджет и дисциплина

- Сеть: ≈20.7 MiB уникальных загрузок из ≤256 MiB (все targeted; multi-GB архивы Zenodo не
  качались — переиспользованы R2-перечисления central directory).
- Научных прогонов: 0. Платных сервисов: 0. Сообщений авторам/внешним: 0.
- В репозиторий вендорятся только digests/urls/цитаты ≤100 B; страницы SI рендерились в /tmp
  (scratch), в Git не попадают.

## 5. Вопросы авторам (DRAFT — НЕ ОТПРАВЛЕНЫ; отправка только с явного разрешения владельца)

Базовый список R3 (§5 аудита) остаётся в силе; R4 добавляет конкретику и два новых вопроса (Q7–Q8).
Контакт-план: corresponding author (M. Famulok) либо issues репозиториев `sulcgroup/hinges`
(безлицензионный — только по явному разрешению владельца) / `walterlab-um/…_SMCodes` (MIT).

1. Можете ли вы опубликовать caDNAno/scadnano/oxview-дизайн follower (**F**, **F-soft-hinge**,
   **F-ss-hinge**) и caDNAno nNE **с** connecting ODN (или scaffold-coordinate map connecting
   ODN)? В аудитированных поверхностях (Nanobase, Zenodo, GitHub, SI) их нет.
2. Подтвердите helix/arm assignment из нашей оцифровки Suppl. Fig. 5b (таблица в
   `S17_R4_PORT_CANDIDATES.json`): driver — 149@h0, 173@h1, 172@h3, 174@h5, 153@h5-6 (верх) /
   89@h17, 165@h6, 164@h7, 163@h9-10, 151@h12 (низ); follower — 151r@h11-12, 163r@h10, 164r@h9,
   165r@h6, 89r@h17 (верх) / 153r@h5, 174r@h4, 172r@h3, 173r@h1-2, 149r@h11 (низ). Верно ли это,
   и на каких helices сидят оверхэнги, скрытые за front view (задние helices 18HB)?
3. Подтвердите 5′/3′ ориентацию каждого оверхэнга в координатах дизайна и «flip upside down»
   преобразование (вектор/ось) для сборки D–F.
4. Пара 7 (153↔89r) и пара 8 (89↔153r): на рисунке 5b они выглядят зеркально «не по шаблону»
   остальных пар (5-6↔17 и 17↔5 вместо h↔11−h). Это особенность геометрии или условность
   рисунка?
5. Вfollower-паре 2 (165↔174r) нарисованный 5′-квадрат 174r находится на выступающем конце,
   хотя по Dataset S1 оверхэнг 174r — 3′-концевой. Следствие ли это «flip»-отрисовки? Где
   фактически сидит 3′-оверхэнг 174r?
6. Внутренняя терминология: «connecting ODN» добавляются при сборке каждого origami (SI Methods,
   2× эквивалент) — верно ли, что отдельные bridge-олиги при D–F пост-сборке не используются?
7. Есть ли maшиночитаемые версии Suppl. Fig. 5a/5b (caDNAno/scadnano-файл, из которого сделан
   рисунок), и планирует ли группа депозит их в Nanobase (например, отдельной записью)?
8. Опубликованы ли где-либо (включяя not-indexed surfaces: учебные материалы, тезисы M. Centola /
   M. Centola (hs), приложения грантов) oxDNA `.top`/`.dat` follower или его caDNAno-дизайн?

## 6. Следующие действия (одно)

Owner decision: (a) разрешить отправку §5 авторам (после чего отдельный bounded WO на импорт
полученных design-файлов), либо (b) направить PREP-S17 на workflow-обкатку на альтернативном
test vehicle (Nanobase 256/257), не смешивая её с S17 follower claims.
