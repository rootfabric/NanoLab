# ALT DNA Two-Part Source Audit R1 — первая опубликованная двухкомпонентная модель для NL7

**Work Order:** `WO-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1`; `issue #75` · **scope:** первичные источники + C0 статическая подготовка; дата 2026-10-21.

## 1. Вывод и границы

**Приоритет S23 Narcissus–Echo** как первая научно опубликованная *пара действительно различимых компонентов*. Авторы описывают две комплементарные DNA-origami половины, соединяемые гибридизацией. **Альтернативный S22 moDON** полезен для масштабируемой модульности, но в первоисточнике две соединяемые детали могут быть конфигурациями одного повторно используемого мономера. Источник S22 указывает CAD design Nanobase 263, но исходные байты недоступны на текущем исполнителе.

**Состояние source pack: `BIBLIOGRAPHIC / BLOCKED_SOURCE`, а не `PINNED_IMPORT_VERIFIED`.** Не выполнены ни один новый oxDNA расчёт, релаксация, гибридизационный эксперимент, импорт авторского топологического файла или полноценная статическая сборка двух реальных деталей. Исторический S17 source R2/R4 и frozen NL5 не меняются.

## 2. S23 — Narcissus (N), Echo (E) → Nemesis (NE)

**Первичный источник:** Huang, Jaekel, van den Boom et al., «A modular DNA origami nanocompartment for engineering a cell-free, protein unfolding and degradation pathway», *Nature Nanotechnology* (2024), DOI [10.1038/s41565-024-01738-7](https://doi.org/10.1038/s41565-024-01738-7), [открытый текст PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11486656/).

- **Подтверждено на уровне публикации:** Nemesis — полая шестигранная DNA origami призма размером около 25×41×53 нм, состоящая из двух shape-complementary половин N и E. Их соединение описывается как nucleobase hybridization на комплементарных краях (статья: *Design and assembly of the modular compartment*, Fig. 2 и Supp. Figs. 1–3). Это публикационный факт, не самостоятельная NanoLab-верификация структуры.
- **Наследуемое свидетельство R4:** merged `docs/research/S17_R4_FOLLOWER_PROVENANCE.json` указывает Nanobase 256 — `N.oxview`, `N_nanobase.json`, `Narcissus staples p7560.xlsx`; Nanobase 257 — `E.oxview`, `E_nanobase.json`, `Echo staples p7560.xlsx`. В этом execution **никакие байты файлов не получены**, SHA-256/размер/перераспределение = UNKNOWN. Перечень отмечен `R4_REPORTED_NOT_BYTE_VERIFIED`, без повышения до подтверждённой импортируемой модели.
- `.oxview` и `*_nanobase.json` ещё не равны проверенной паре oxDNA `.top/.dat` с полной геометрией, а Excel-таблица staple-нитей не даёт единственную 3D-структуру. Поэтому `port anchors`, конфигурации и точки соединения = UNKNOWN.
- **Ключевой риск именований:** S23 `NE = Nemesis` и S17 `NE = nanoengine` — совершенно разные молекулярные конструкции; смешивать исходники запрещено.

## 3. S22 — moDON (модульный monomer + соединения XY/Z)

**Первичный источник:** Weck, Heuer-Jungemann, «Fully addressable designer superstructures assembled from one single modular DNA origami», *Nature Communications* **16, 1556** (12 февраля 2025), DOI [10.1038/s41467-025-56846-2](https://doi.org/10.1038/s41467-025-56846-2). [Коррекция от 21 февраля 2025](https://doi.org/10.1038/s41467-025-57186-x) должна учитываться при интерпретации.

- **Подтверждено в статье:** moDON — DNA-origami мономер с 78-helix bundle honeycomb, комбинирует **XY-коннекторы** на reroutable scaffold и **Z-коннекторы** из трёх нитей; множество конфигураций и многокомпонентные структуры. Это не физически движущийся привод.
- Data Availability прямо называет CAD-исходники в [Nanobase structure 263](https://nanobase.org/structures/263). В Methods сообщается caDNAno 2.4.10, oxDNA 3.5.0 — **версии, использованные авторами**, не пины исполняемых NanoLab вычислений.
- Статья распространяется по CC BY 4.0, однако лицензия самой записи Nanobase и отдельных CAD/оксДНК-файлов **не доказана**; не переноси лицензию публикации на неаудированные исходники.
- Не получены: файловый реестр 263, exact CAD bytes/SHA, парные экземпляры с подтверждёнными модифицированными коннекторами, oxDNA topology/config, индексы и 3D port mapping. Статус `PAPER_REPORTS_FILE_NOT_FETCHED`.

## 4. Журнал доступности источников, не выдавать за global absence

| Surface | Observation | Вердикт |
|---|---|---|
| Nature/PMC S22 и S23 | Первичные publication pages доступны через web search; структурные и интерфейсные концепции явно опубликованы | `SOURCE_ARTICLE_CONFIRMED` (публикационный уровень) |
| Nanobase `/structures/263` | Повторная попытка открытия через текущий web инструмент: HTTP 502 (2026-10-21), динамические поля не извлечены | `SOURCE_ACCESS_BLOCKED` только на этом маршруте |
| Nanobase `/structures/256` и `/257` | Кэшированные HTML-страницы доступны, но детальные динамические метаданные отсутствуют; `Licensing Information: N/A` | `SOURCE_FILE_LICENSE_UNKNOWN`, не означает запрещённую лицензию |
| Nanobase API под `api.nanobase.org` | Прямой запрос через этот исполнитель недоступен; контейнер не имеет внешнего DNS | `NOT_VERIFIED` (не свидетельство отсутствия файла на сервере) |
| Существующий NanoLab R4 | Историческое описание конкретных файлов 256/257 в каноническом Git tree | `R4_REPORTED_NOT_BYTE_VERIFIED` в текущем WO |

**Сетевой бюджет:** 0 байт скачанных новых raw CAD/oxDNA источников; GitHub connector прочитал только JSON/код, web вернул текст страниц. Допустимый бюджет WO 256 MiB остаётся неиспользованным.

## 5. Что потребуется для настоящей пары

Чтобы повысить вход от BIBLIOGRAPHIC до уровня структурного preflight (не scientific reproduction), нужно:

1. Получить **точный официальный файловый листинг** [Nanobase 256](https://nanobase.org/structures/256) и [257](https://nanobase.org/structures/257), либо 263, подтвердить origin и права на каждую поверхность.
2. Скачать законно **обе** исходные структуры и коннекторные sequences; зафиксировать file bytes, size, SHA-256 и attribution/retention. Не собирать скачанное в Git при неизвестных правах.
3. Если авторские пары `.top/.dat` отсутствуют, конверсия oxView/caDNAno создаёт **отдельный CANDIDATE_DESIGN** с точными инструментами/версиями и собственными новыми digests; конверсия не доказывает геометрию relaxed/stable.
4. На двух топологиях подтвердить структуры/индексы и каждую пару overhang/anchor через реальный mapping. Без этого — `BLOCKED_SOURCE`.
5. После независимой приёмки [PR #73](https://github.com/rootfabric/NanoLab/pull/73) выполнить только статическую сборку с верным источником, а физическую передачу движения/нагрузки ставить отдельным NL7 scientific WO (после NL5/U1/E5).

**Исполняемый fail-closed preflight (offline):**

```bash
PYTHONPATH=scripts python3 -m knowledge_pack.alt_pair_source_gate \
  docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json \
  --candidate S23_NARCISSUS_ECHO --root .
```

На текущем pack **ожидаемый exit 2, outcome BLOCKED_SOURCE**, потому что топология/конфигурация обеих деталей и портовая карта не получены. При позже подтверждённых файлах, правах и проверенной карте функция способна выдать только `C0_SOURCE_FILE_PREFLIGHT_OK_REVIEW_REQUIRED`, не `ASSEMBLY_VALIDATED`. Положительный сценарий unit-тестов работает **исключительно на синтетической паре**.

## 6. Следующий шаг

Отдельный источник-исполнитель с доступом к Nanobase проверяет listings/файлы 256/257 (первый приоритет), затем 263; создаёт pinned evidence и не дописывает unsupported pins. R3 integration #73 и reviewer #74 — отдельные задачи, не должны мешать source-audit. Передача наружу/авторам без явного Human Gate запрещена.


## 7. Additional original-file retrieval route (not verified source data, 2026-10-21)

Upstream oxView [source index.html](https://github.com/sulcgroup/oxdna-viewer/blob/047e0bf718f315577556de2ba5a6be64dede48dc/index.html) includes a Nanobase importer using HTTPS GET endpoint:

    https://api.nanobase.org/api/v1/structure/getStructureOxdnaFiles?id=256

The same code treats a successful HTTP response as an oxDNA ZIP. This is an actionable route to probe independently for IDs 256, 257 and 263. The available web executor could not access this endpoint and produced no archive bytes, file list, SHA-256, rights evidence, or SOURCE_VERIFIED result. The endpoint may have moved or become unavailable; do not invent success.

A separate network-capable and permitted executor should record HTTP status, bytes and URL; enforce transfer/ZIP entry-size/path limits; independently inspect exact original CAD/oxDNA contents and per-file license before any CONTENT_VERIFIED/ALLOWED assertion. An archived design cannot be treated as the missing S17 follower. Current verdict stays BLOCKED_SOURCE.
