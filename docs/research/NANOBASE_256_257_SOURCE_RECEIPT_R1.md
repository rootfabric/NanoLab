# [SOURCE-75] Nanobase 256 «Narcissus» / 257 «Echo» retrieval — SOURCE_RECEIPT_R1

**Статус: `BLOCKED_SOURCE`** (см. §7 — точная причина; двухфакторная: (1) официальный источник недоступен в момент исполнения, (2) права на файлы дизайна не подтверждены — явная лицензия отсутствует).

- **Work Order:** SOURCE-75 / Issue #75 (WO-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1), независимый исполнитель `source-nanobase-r1`
- **Base:** `main @ fb3148b46a9638167168a46cb170902a4ad9e8d2` (проверено `git rev-parse HEAD` в момент старта)
- **Claim ceiling:** `C0_SOFTWARE_ONLY` — сетевое получение + метаданные; **0** научных запусков (MD/relax/simulation — нет)
- **Дата/время исполнения (UTC):** 2026-10-21, 11:51 → 14:0x (окно наблюдения)
- **Лимиты:** передача ≤ 256 MiB — израсходовано **≈ 43,0 MiB** (45 122 116 B уникальных загрузок); scratch ≤ 2 GiB — использовано **≈ 45 MB** в `source-artifacts/`; платные сервисы — 0

---

## 1. Цель и приоритеты (по заданию)

1. **Nanobase 256 «Narcissus» + 257 «Echo»** (пара Narcissus+Echo→Nemesis, Huang et al., *Nat. Nanotechnol.*, DOI `10.1038/s41565-024-01738-7`).
2. Fallback: **Nanobase 263 «moDON»** (DOI `10.1038/s41467-025-56846-2`) — только если 256/257 недоступны.

Narcissus/Echo→Nemesis **не** является отсутствующей S17 follower-структурой; задачи не смешивались. `project/state.json`, `project/plan.json`, frozen NL5 материалы — не изменялись.

## 2. Доступность официального источника (живые проверки)

| Проверка | Результат |
|---|---|
| DNS `nanobase.org` / `api.nanobase.org` | `206.207.50.88` — локальный резолвер **и** Google DoH (`dns.google/resolve`) согласны (TTL 600) |
| TCP 443/80 к `206.207.50.88` | **Connection refused (RST)** на обоих портах, каждая попытка с 11:51:09 UTC |
| Контроль связности того же хоста в тот же момент | `github.com`→200, `api.github.com`→200, `www.nature.com`→303, `web.archive.org`→200, `api.crossref.org`→200, `static-content.springer.com`→200 — отказ nanobase.org **не** является сетевой проблемой нашего контура |
| Повторные попытки | фоновый retry-цикл каждые 3 мин (лог `logs/retry_loop.log`), 0 успешных подключений за окно наблюдения |
| Историческая доступность | **2026-10-18** тот же API был доступен из этой же среды: `EX-PREP-S17-R4-SOURCE-R1` скачал 12/12 файлов записи 196 и перечислил каталог 109/109 структур ⇒ это **недавний простой/снятие сервера**, а не постоянная блокировка |
| Wayback Machine | `nanobase.org/structure/256`, `/structure/257`, `/oxdna*`, `api.nanobase.org/api/v1/structure*` — **снимков нет** (CDX `[]`); архив не содержит копий файлов 256/257 |
| Внешние vantage (check-host.net, бесплатные узлы) | результаты проверки не возвращены узлами (нет данных) — не использовано как доказательство |
| HTTP-пробы в этот прогон | `https://nanobase.org/` → curl error 7 (000); `https://api.nanobase.org/api/v1/structure/getStructureOxdnaFiles?id=256` → 000; `.../structure-files?id=256` → 000. Ответов (HTML/JSON) сервер не вернул ни по одному маршруту — в т.ч. поэтому «официальный metadata/file listing» в этом прогоне **не получен заново** (см. §3) |

**Вывод §2:** официальный источник в момент исполнения недоступен на уровне TCP; все маршруты (сайт, API, страница структуры) возвращают не-ответ. Fallback 263 лежит на том же хосте: Data availability статьи moDON дословно — «*caDNAno files of the structure are also available on nanobase.org/structure/263*» ⇒ единая точка отказа, fallback равным образом недоступен.

## 3. Листинг файлов записей 256/257 (задокументированная ретроспектива 2026-10-18, дайджест-цепочка верифицирована)

Новый живой листинг недоступен (§2). Использованы **сырые ответы API, захваченные 2026-10-18** предыдущим исполнением (`EX-PREP-S17-R4-SOURCE-R1`), сохранённые в `prior_captures_r4/`. Цепочка сохранности: SHA-256 скопированных файлов **байт-в-байт совпали** с пинами, записанными в `docs/research/S17_R4_FOLLOWER_PROVENANCE.json` (git-tracked, коммит в main):

| Файл | URL-источник (2026-10-18) | Байт | SHA-256 | Совпадение с пином R4 |
|---|---|---|---|---|
| `prior_captures_r4/nb_all.json` | `https://api.nanobase.org/api/v1/structure/getAllPublicStructures_paginated?skip=0&take=120` | 196 987 | `4637ff04e86245401e7cdd36d83abbffb8d8712715d008b6faa039f3d38e2bf4` | **ДА** |
| `prior_captures_r4/nb_files_256.json` | `https://api.nanobase.org/api/v1/structure/structure-files?id=256` | 277 | `d086416ea6927fb63fe515ac4f3792f90b21d53f01f8162d3975462e1bc3e7bb` | (пин не публиковался; файл-листинг 196 совпал ⇒ метод верифицирован) |
| `prior_captures_r4/nb_files_257.json` | `https://api.nanobase.org/api/v1/structure/structure-files?id=257` | 267 | `c5d037a902cb19004ff7111c1a4e74370b9eefd2a04d9b9b106f82df062d5bd1` | (аналогично) |
| `prior_captures_r4/nb_files196.json` | `https://api.nanobase.org/api/v1/structure/structure-files?id=196` | 995 | `b4c4a64594b1f2ada2ac5be2e6e1eb279d54b97074c54a648346cdd849b9f6d3` | **ДА** |

Листинг файлов (из `nb_files_256/257.json`, категория `structure` у всех):

- **256 «Narcissus»:** `256/structure/N.oxview`; `256/structure/N_nanobase.json`; `256/structure/Narcissus staples p7560.xlsx`
- **257 «Echo»:** `257/structure/E.oxview`; `257/structure/E_nanobase.json`; `257/structure/Echo staples p7560.xlsx`

Метаданные записей (из `nb_all.json`): title `Narcissus`/`Echo`; type DNA; citation = Huang et al. DOI `10.1038/s41565-024-01738-7` (маппинг ID→дизайн подтверждён метаданными самой Nanobase, но это capture 2026-10-18, не живая верификация 2026-10-21); uploader Ivan Grishchuk; uploadDate 2024-09-10; lastUpdated 2025-03-10; **`licensing: ""` (пусто) у обеих записей**; statsData: n_staples 209 (N) / 218 (E); описания файлов: «cadnano file» (`N_nanobase.json` / `E_nanobase.json`), «Sequences» (xlsx), «Relaxed structure» (oxview).

Маршруты скачивания (готовые URL, использованы в `fetch_nanobase_256_257.sh`): `https://api.nanobase.org/api/v1/structure/files/256/structure/N.oxview` и т.д. (шаблон подтверждён работой на записи 196 в 2026-10-18); альтернатива с основного сайта по публичному коду (`sulcgroup/nanobase`, `main.py`: `@app.route('/file/<id>/<file_type>/<file>')`): `https://nanobase.org/file/256/structure/N.oxview`. **Ни один байт файлов дизайна в этом прогоне получен не был** (TCP refusal). Маршрут `getStructureOxdnaFiles` (упомянутый в задании) в публичном коде `sulcgroup/nanobase` (ветки `master`/`server`, коммиты 2022 г.) **отсутствует** — публичный репозиторий не отражает текущий API v1; живая проверка маршрута невозможна из-за простоя.

## 4. Официально полученные артефакты этого прогона (все CC BY 4.0, включая редистрибуцию с атрибуцией)

| # | Файл | URL | HTTP | Content-Type | Байт | SHA-256 | SHA-1 |
|---|---|---|---|---|---|---|---|
| 1 | `files_pmc_vor.html` | `https://pmc.ncbi.nlm.nih.gov/articles/PMC11486656/` | 200 | text/html; charset=utf-8 | 234 539 | `da8a3e7b26ad3056ff7751d954d9c2a9e657e95b7e01c5532ec8d2cf7d6a89ae` | `dc4ef62e3b46dcb22b4fa89afc598b633d24ab28` |
| 2 | `files_si_moems1.pdf` | `https://static-content.springer.com/esm/art%3A10.1038%2Fs41565-024-01738-7/MediaObjects/41565_2024_1738_MOESM1_ESM.pdf` | 200 | application/pdf | 26 002 583 | `7b50b833f0db982c9421c67db1b13a27315b40f0ae4e25ebc7c39c7beabf219b` | `c57b6acb2c3a2601c2e42434a91efc8834ff7db3` |
| 3 | `files_si_moems5_sequences.xlsx` | `https://static-content.springer.com/esm/art%3A10.1038%2Fs41565-024-01738-7/MediaObjects/41565_2024_1738_MOESM5_ESM.xlsx` | 200 | application/octet-stream (OOXML) | 73 352 | `90c1493ea26d4b5cd7de2d487ddafe1005b0a4e4a28ccbdd3d0522076cbf008c` | `1c89a216bae13847b9496d37bef6247819e72efe` |
| 4 | `files_nature_modon_263_da.html` | `https://www.nature.com/articles/s41467-025-56846-2` | 200 | text/html; charset=utf-8 | 462 766 | `2e2c79d7a18fbaa0184c21b6c80739863daef11610ed76beda408a26944e4198` | `3bfa31307b0b4de8669efb4b517617c25011d84e` |

Это статья и SI — **не** файлы дизайна с Nanobase. Они документируют: именование Narcissus/Echo, дизайн в caDNAno, скаффолд p7560, последовательности (SI Data 2) и указатель на 263 («*caDNAno files of the structure are also available on nanobase.org/structure/263*» — Data availability статьи moDON).

## 5. RAW_RECEIPT: безвычислительный поверхностный разбор полученных данных

Никаких научных вычислений не выполнялось; только подсчёты элементов форматов:

- **SI xlsx «List of DNA sequences»** (OOXML, ZIP-контейнер): 17 записей, записей с path-traversal (`../`, абсолютные пути) — **0**; листы: `Narcissus` (254 строки), `Echo` (255), `Nemesis` (42), `multimers` (306), `lid` (339). Статус: **RAW_RECEIPT** (последовательности из официального SI, не файлы дизайна Nanobase).
- **.top/.oxview файлы 256/257: не получены** ⇒ разбор структуры нитей невозможен; вымышленные/синтетические файлы не создавались.

## 6. Права и лицензии (цитаты условий)

1. **Статья Huang et al. 2024 (и её SI):** Crossref license records (обе записи, `vor` и `tdm`): `https://creativecommons.org/licenses/by/4.0`. ⇒ статья и SI-файлы — CC BY 4.0, редистрибуция с атрибуцией разрешена. **Но:** CC BY статьи не переносится автоматически на файлы дизайна, депонированные третьими лицами на Nanobase.
2. **Файлы дизайна на Nanobase (256/257):** поле `licensing` обеих записей — **пустая строка**. Официальная публикация Nanobase (Nucleic Acids Res 2022, DOI `10.1093/nar/gkab963`, PMC8728195 — сама CC BY 4.0): «*it is also possible to note if the structure is covered under any licensing or patent restrictions*» и «*Here you will find the citation and link to the original publication, plus any licensing and patent information, if provided*» — лицензирование **per-entry и опционально**; для 256/257 никакая лицензия не указана.
3. **Data availability статьи Huang** (PMC VoR, дословно): «*All data generated or analysed during this study are included in this published article and its Supplementary Information files… Cryo-EM … EMD-18538 … proteomics … PXD045825 and PXD050816. All other data can be provided by the corresponding authors on request.*» — **Nanobase не упомянут**: файлы 256/257 не являются задекларированным каналом данных статьи (в отличие от случая S17/структура 196).
4. **Загрузчик записей** (Ivan Grishchuk) не входит в авторский список статьи ⇒ депонент — не автор по публикации; наследование прав статьи на эти файлы не подтверждается ничем.
5. **Вывод (правовой):** права на редистрибуцию файлов `N.oxview`, `N_nanobase.json`, `Narcissus staples p7560.xlsx`, `E.oxview`, `E_nanobase.json`, `Echo staples p7560.xlsx` **НЕ установлены** (`RIGHTS_NOT_ESTABLISHED`). Согласуется с `docs/research/DEPENDENCY_LICENSE_MATRIX.md` (NANOBASE: REFERENCE_ONLY per record, redistribution UNKNOWN).

## 7. Итоговый статус и причина

**`BLOCKED_SOURCE`** — по совокупности двух независимых оснований:

1. **Источник недоступен.** `nanobase.org`/`api.nanobase.org` (206.207.50.88) отвечают TCP RST на 80/443 в течение всего окна исполнения (11:51→14:0x UTC; retry-цикл, лог сохранён). Ответов HTTP нет ни по одному маршруту, поэтому ни листинг, ни байты файлов 256/257 (и 263) живьём не получены. Wayback-копий файлов не существует. Скачивание возможно только после восстановления сервера: `bash source-artifacts/nanobase-256-257/fetch_nanobase_256_257.sh` (скрипт готов, бюджет-контроль встроен).
2. **Права не подтверждены.** Даже при получении байтов: per-entry лицензия пустая, статья/SI не покрывают эти депозиты (CC BY статьи ≠ лицензия файлов дизайна), загрузчик — не автор публикации. По строгому правилу задачи `SOURCE_CONFIRMED` требует байты **И** подтверждённые права — второе условие не выполнено ⇒ файлы в Git **не** помещаются, ветка `work/prep-nl7-nanobase-256-257-source-r1` **не создаётся**.

Опубликованы только: манифест (URL/дигесты/размеры), скрипт получения, квитанция и цитаты условий. Полученные байты (включая официальные CC BY артефакты статьи) остаются **вне индекса Git** в `source-artifacts/nanobase-256-257/` (untracked).

## 8. Бюджет и следованиеПравилам

- Передача: **43,03 MiB** (45 122 116 B) из 256 MiB (осн.: SI PDF 24,8 MiB, дерево GitHub-репо Nanobase 17,1 MiB для документирования маршрутов, статья/SI ~0,8 MiB, метаданные API ~1,5 MiB, прочее <1 MiB).
- Scratch: `du -sb source-artifacts/` ≈ 45 MB из 2 GiB. Zenodo-архивы и прочие multi-GB — не скачивались.
- MD/relax/simulation: 0. Платные сервисы: 0. Авторские письма: 0. `git push`: 0. Изменения main/state/plan/frozen: 0.
- ZIP-безопасность: единственный ZIP-контейнер (OOXML xlsx) проверен листингом: 0 записей с `../` или абсолютными путями; распаковка в файловую систему не выполнялась; symlink-записи отсутствуют.

## 9. Условия возобновления (resume conditions)

1. Восстановление `nanobase.org`/`api.nanobase.org` → запуск `fetch_nanobase_256_257.sh` → байты+дигесты пополнят манифест (статус по правам при пустом поле `licensing` останется `BLOCKED_SOURCE` до появления явной лицензии).
2. Явная лицензия от правообладателей на записи 256/257 (поле licensing на сайте или письменный grant через owner) → возможен пересмотр в `SOURCE_CONFIRMED` с веткой по правилам задачи.
3. Альтернативная пара с прозрачными правами (per Issue #75 §Candidate selection) — отдельное bounded решение.
