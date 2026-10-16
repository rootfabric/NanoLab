# S17 Source Recovery R2 — force inputs, nucleotide ports, driver–follower topology

Work Order: `WO-PREP-S17-R2` (исполнение: EX-PREP-S17-R2, ветка `work/prep-s17-r2-r1`).
Дата: 2026-10-16. Язык отчёта — русский; идентификаторы/статусы — английские.

## 0. Резюме

R2 восстанавливает недостающие входы S17 из публичного датасета Zenodo (record 8248808,
CC-BY-4.0) ограниченным range-фетчем без скачивания архивов целиком:

- **9 из 11 не-документных content-пинов R1 подтверждены байт-в-байт из Zenodo-членов**
  (2 остальных — `input_release`, `NE_halo_dsDNA.json` — среди извлечённых R2-членов
  честно NOT_OBSERVED; их пины остаются на Nanobase-источнике R1):
  3 топологии (NE.top, nNE.top, NE_NB.top), 3 конфигурации (NE.dat, nNE.dat, NE_NB.dat),
  3 входа симуляции (input_equilibrium, input_pull, T7_force.txt) — см.
  `docs/work/executions/EX-PREP-S17-R2/evidence/s17-r2-pin-identity.json`.
- **Ранее «неизвестный» файл `polymerase_positioning.txt` найден во всех pull-прогонах**;
  Nanobase-экhibit `T7_force.txt` байт-идентичен силовому файлу **только nNE-семейства**
  (particle=8694, ref_particle=7374, stiff=0.3290, r0=8.8, PBC=1). Семейства NE/NE_NS и
  soft используют другие пары частиц (8514/14288 и 14102/13840) — все три варианта
  восстановлены и процитированы целиком в evidence.
- **r0 = 8.8 oxDNA-единиц × 0.8518 нм/ед = 7.496 нм ≈ 7.5 нм** — радиус обхвата T7RNAP
  из статьи; semantic-связка «trap ↔ полимераза» подтверждается численно.
- **Индексные порты** (get_k: [2034,6657], [4593,4411]; ss_ids.txt; arm-файлы; пары trap)
  разрешены против verified-индексных карт всех трёх дизайнов:
  `docs/research/S17_R2_PORT_MAP.json`.
- **Driver–follower MD-сборка: NOT_RECONSTRUCTED** — в полных central-directory
  перечислениях всех четырёх архивов (276+207+949+894 записей) нет ни одного
  driver/follower-каталога или файла. Receipt:
  `evidence/s17-r2-df-not-reconstructed.json`.
- Claim level остаётся **PINNED_IMPORT_VERIFIED**; научных прогонов нет (0 scientific runs).

## 1. Метод извлечения (bounded, ≤256 MiB)

Инструменты: `scripts/knowledge_pack/s17_zip_probe.py` (EOCD/ZIP64/CD-парсер, CRC),
`scripts/knowledge_pack/s17_range_fetch.py` (multi-range batch fetch, multipart-парсер),
тесты `tests/test_s17_r2_*.py` (66 offline-тестов, все зелёные).

Процедура (воспроизводимо, без raw-загрузок в Git):

1. HTTP Range → хвост архива (1–8 MiB) → EOCD/ZIP64-EOCD → central directory
   полностью (NE23 276, NE37 207, pull_release23 949, pull_release37 894 записей).
2. Для каждого целевого члена: span = [lho, lho+30+|name|+96+csize−1]; группировка в
   multi-range запросы (≤6 диапазонов и ≤1.2 MB на запрос).
3. Парсинг multipart/byteranges; проверка длины каждой части; slice → inflate →
   **CRC-32 против central directory** (fail-closed) → sha256 → manifest.
4. ZIP64: у 748 из 949 записей pull_release23 offset > 4 GiB хранится в ZIP64 extra
   (header id 0x0001), причём extra лежит **после** Info-ZIP UT/ux — требуется скан
   списка extra-полей (реализовано и в probe, и в range_fetch; покрыто тестами).

Передача: хвосты 18.0 MiB + уникальные span-байты 10.4 MiB ≈ **28.4 MiB** уникальной
нагрузки (без учёта повторов неудачных запросов; лимит повторов ограничивает overhead).
Бюджет ≤256 MiB соблюдён с большим запасом. Научных прогонов: 0.

Ограничения сети (честно зафиксировано): zenodo.org периодически рвёт TLS (curl rc=35),
троттлит (retry-after 52–60 с, x-ratelimit-limit 133/окно) и «подвисает» после отдачи
body (лечится max-time + парсинг полного ответа через `curl -i`). Сервер склеивает
смежные range-части и иногда возвращает multipart не полностью — извлечение идёт
идемпотентными проходами до полного покрытия manifests (все 99/99 членов CRC-ok).

## 2. Байт-идентичности (SOURCE_CONFIRMED)

Происхождение каждого восстановленного входа (canonical retrieval):

| Вход | Точный источник (URL + member) | Размер, B | SHA-256 (12) | Rights | Retrieval (локальное UTC+10) |
|---|---|---|---|---|---|
| NE.top | `https://zenodo.org/api/records/8248808/files/NE37.zip/content` :: `hinge37/NE1/stiff.top` | 215,903 | 5074d559a092 | CC-BY-4.0 | 2026-10-16T09:00–13:00 |
| NE.dat | `…/NE37.zip` :: `hinge37/NE1/last_conf_trap.dat` | 3,955,400 | c73aeb86fc67 | CC-BY-4.0 | 2026-10-16T11:5x |
| nNE.top | `…/NE23.zip` :: `hinge23/nNE1/linked.top` | 215,616 | 71eca286cfc1 | CC-BY-4.0 | 2026-10-16T12:0x |
| nNE.dat | `…/NE23.zip` :: `hinge23/nNE1/last_conf_trap.dat` | 3,961,974 | b0722a5b859e | CC-BY-4.0 | 2026-10-16T12:1x |
| NE_NB.top | `…/NE23.zip` :: `hinge23/NE_NB1/hinge_correct_seq.top` | 210,225 | 5abfcbde51e7 | CC-BY-4.0 | 2026-10-16T10:4x |
| NE_NB.dat | `…/NE23.zip` :: `hinge23/NE_NB1/last_conf_trap.dat` | 3,853,788 | c802eb954750 | CC-BY-4.0 | 2026-10-16T10:4x |
| input_equilibrium | `…/NE37.zip` :: `hinge37/nNE1/input` | 959 | 822e0f493ac2 | CC-BY-4.0 | 2026-10-16T12:3x |
| input_pull | `…/pull_release37.zip` :: `pull_release37/nNE_pull1/input` | 1,018 | dc3d643908ad | CC-BY-4.0 | 2026-10-16T12:5x |
| T7_force.txt (= nNE polymerase_positioning.txt) | `…/pull_release23.zip` :: `pull_release23/nNE_pull_fine1/polymerase_positioning.txt` | 96 | 71c69b4855e4 | CC-BY-4.0 | 2026-10-16T12:4x |

Полные 64-hex sha256 — в `evidence/s17-r2-pin-identity.json` и
`evidence/s17-r2-extraction-manifest-*.json`; манифесты фиксируют sha256/size/crc32/method
(без per-member временных штампов). Пакетное извлечение шло в интервале
~00:36–03:18Z 2026-10-16 (значения в колонке выше — локальное время машины UTC+10;
в events 0002/0003 тот же сдвиг зон исправлен корректирующим event 0004).
Nanobase-пины R1 остаются вторым независимым источником тех же байтов.

Ключевые результаты (полная таблица — `evidence/s17-r2-pin-identity.json`):

| R1 pin | sha256 (12) | Zenodo-члены (байт-идентичны) |
|---|---|---|
| NE.top | 5074d559a092 | ne37:hinge37/NE1/stiff.top; pr23:NE_pull_fine1/long stiff.top; pr37:NE_pull1/stiff.top |
| NE.dat | c73aeb86fc67 | ne37:hinge37/NE1/last_conf_trap.dat |
| nNE.top | 71eca286cfc1 | ne23:hinge23/nNE1/linked.top; ne37:nNE1/linked.top; pr23:nNE_pull_fine1/linked.top; pr37:nNE_pull1/linked.top |
| nNE.dat | b0722a5b859e | ne23:hinge23/nNE1/last_conf_trap.dat |
| NE_NB.top | 5abfcbde51e7 | ne23:hinge23/NE_NB1/hinge_correct_seq.top; ne23:hinge23/NE_NS.top |
| NE_NB.dat | c802eb954750 | ne23:hinge23/NE_NB1/last_conf_trap.dat |
| input_equilibrium | 822e0f493ac2 | ne37:hinge37/nNE1/input |
| input_pull | dc3d643908ad | pr37:pull_release37/nNE_pull1/input |
| T7_force.txt | 71c69b4855e4 | 5 members: nNE/nNE_NS polymerase_positioning.txt (23C и 37C) + корень pr23 |

Наблюдения:

- `hinge23/NE_NS.top` ≡ `NE_NB.top` байт-в-байт: ось дизайна «NS» (с bridge) при
  этих байтах совпадает с NB-топологией Nanobase; NB-варианты в прогонах различаются
  только силовыми файлами/входами (NB = no-bridge run без bridge-ODN).
- nNE1/input (23 °C) ≡ pin input_equilibrium (37 °C) во всём, кроме одной строки
  `T = 37C → 23C`; nNE1/input_relax = relaxation от last_conf_trap.dat (dt=0.0003).
- Реплики 1–3 одного дизайна несут байт-идентичные статические входы (soft.top,
  soft_linked.top, pairs.txt, NE_NS1-3 stiff_no_seq.top, nNE_NS1-3 linked_no_seq.top).

## 3. Силовые входы: три семейства (SOURCE_CONFIRMED)

| Семейство | particle | ref_particle | size | = Nanobase T7_force.txt |
|---|---|---|---|---|
| nNE / nNE_NS (23C+37C) | 8694 | 7374 | 96 B | **да** |
| NE / NE_NS (23C+37C) | 8514 | 14288 | 97 B | нет |
| soft | 14102 | 13840 | 98 B | нет |

Общая структура пары во всех семействах: `particle` — 5'-терминальный нуклеотид
короткого выступающего стейпла (46/46/25 nt), `ref_particle` — середина длинной цепи
(позиция 125/183/125). Разрешение по verified-картам — в `S17_R2_PORT_MAP.json`.

Semantic-привязка к статье (16 pN между точкой присоединения полимеразы и первым
стоп-кодоном, cut-off 7.5 нм). Дословная цитата (проверено независимым Reviewer
2026-10-16 по https://www.nature.com/articles/s41565-023-01516-x, Methods,
«Closing rates were measured by running ten replicates of simulations with a
constant force of 16 pN … applied between the nucleotide where HT–T7RNAP is
covalently linked to the first nucleotide in the first stop sequence in the
dsDNA-t with a cut-off radius of T7RNAP (7.5 nm)»): r0=8.8 ед = 7.496 нм совпадает
с cut-off; прямая
проверка «пара сближена на r0 в first_conf» НЕ выполняется (в стартовых конфигурациях
пара на 18.8–52.8 нм — trap сводит её к r0 в ходе прогона). Семантика trap =
акт постоянного сближения пары до 7.5 нм. Превышение claim-потолка не допускаем:
формула силы подтверждается файлами, физическая валидация — вне R2.

## 4. Индексные порты (R2-B)

- **ss_ids.txt** (hinge23/structures/): 322 индекса (уточняет R1-оценку 319),
  только circular-скаффолд strand 1, 7 окон: 6×53 (7248–7196, 1834–1782, 1421–1369,
  1112–1060, 699–647, 412–360) + 4 (7195–7192). В границах всех трёх дизайнов
  (скаффолд 7,249 nt везде).
- **arm-файлы** (по 6,1–6,6 тыс. индексов; 20 проанализированных файлов + ss_ids.txt
  отдельно): 12 из 20 выходят за 14,011 частиц NE_NB ⇒ для NE_NB исключены по
  границам (жёсткий тест). Остальные разрешения
  против NE/nNE возможны; per-file namespace-атрибуция по выравниванию на границы
  цепей НЕубедительна (лучший счёт 73/74 для NE_NB на hinge_arm_1, но без
  независимого эталона) → фиксируем как bounds-факты + наблюдения, статус
  port-атрибуции arm-файлов — INFERRED_CANDIDATE максимум.
- **get_k arm refs** [2034,6657], [4593,4411] (и старые [2609,6336]): все шесть —
  circular-скаффолд, позиция = индекс, в NE и nNE идентично.
- **Trap-пары** разрешены в своих namespace (см. §3): nNE: 8694 = strand 28
  (46 nt), pos 45, 5'-terminal; 7374 = strand 2 (180 nt), pos 125. NE: 8514 =
  strand 27 (46 nt), pos 45, 5'-terminal; 14288 = strand 161 (238 nt), pos 183.
  soft_pull: 14102 = strand 159 (25 nt), pos 24, 5'-terminal; 13840 = strand 157
  (174 nt), pos 125.
- **Bridge-ODN порты**: UNKNOWN — во всех pinned-топологиях placeholder-последовательности
  (T7-промоутер/терминаторы отсутствуют), NE и NE_NB — разные дизайны скаффолда;
  sequence-based идентификация невозможна из доступных источников.

## 5. Driver–follower topology (R2-C): NOT_RECONSTRUCTED

Полные CD-перечисления четырёх архивов: семейства прогонов
NE/NE_NB/NE_NS/NE_NS_NB/nNE/nNE_NS/soft × {pull, release} × {fine 1–10, long} +
equilibrium-наборы (NE23/NE37). **Ни одного каталога/файла с driver/follower.**
Дополнительно: nNE_pull runs используют `linked.top` ≡ nNE.top (не «combined
engine+follower» топологию из R1-гипотезы) — R1 missing-input «linked.top build
recipe» закрыт отрицательным результатом: сборка не требуется, топология = nNE.top.
MD-сборка D–F остаётся невоспроизводимой из публичного датасета (receipt).

## 6. Ограничения и честные оговорки

- Извлечение покрывает 99 членов из 2,324 суммарных записей CD; целевые наборы
  выбраны по критериям WO (pins, force-файлы, structures, topologies, inputs).
- `polymerase_positioning.txt` в корнях архивов различается: pr23 корень = 96 B
  (nNE-вариант), pr37 корень = 97 B (NE-вариант) — корневые файлы не являются
  «глобальными».
- Retry-механика сети могла дублировать часть запросов; учёт бюджета ведётся по
  уникальным байтам (28.4 MiB) с верхней оценкой overhead.
- Тройная детерминизм-проверка реплик — наблюдение, не гарантия для всех семейств.
- Никакие статусы NL5/NL6 не изменялись; научные прогоны не выполнялись;
  raw-артефакты в Git не вендорятся (только digests/manifests).

## 7. Артефакты

- `docs/research/S17_R2_PORT_MAP.json` — индексные порты, force-пары, namespace.
- `docs/research/S17_R2_ASSEMBLY_MANIFEST.json` — семейства дизайнов, preflight, D–F.
- `docs/research/S17_KNOWLEDGEPACK_R2.json` — обновлённый knowledge pack.
- `docs/work/executions/EX-PREP-S17-R2/evidence/*` — manifests, pin-identity,
  force-variants, preflight, structures, D–F receipt (digests + цитаты ≤100 B).
- `scripts/knowledge_pack/s17_range_fetch.py`, `s17_zip_probe.py` + 66 offline-тестов.
