# S17 PREP Audit R1 — published leaf-spring DNA nanoengine (Centola et al. 2023) for NanoLab

**Work order:** `WO-PREP-S17-R1` · **Execution:** `EX-PREP-S17-R1` · **Claim ceiling:** `C0_SOFTWARE_ONLY`, level achieved **`PINNED_IMPORT_VERIFIED`** (file-structure import only — **не** симуляция, **не** воспроизведение, **не** `MODEL_REPRODUCED`).
**Base:** `main @ 32d3c6840341ad3954d5001235a3cc35b8ca0e01`. **Научных запусков: 0.** Маршрут Literature-to-Mechanism (PR #54) учитывается как **proposed** (ожидает Human Gate merge), не как канонический.
**Машинный контракт:** [S17_KNOWLEDGEPACK.json](S17_KNOWLEDGEPACK.json) (валидатор `scripts/knowledge_pack/contract.py`, тесты `tests/test_knowledge_pack*.py`).
**Дата аудита (UTC):** 2026-10-15; все HTTP-факты проверены живыми запросами в ходе независимого аудита.

---

## 1. Источник

**Точная публикация (проверено на nature.com):** M. Centola, E. Poppleton, S. Ray, M. Centola, R. Welty, J. Valero, N. G. Walter, P. Šulc, M. Famulok, *A rhythmically pulsing leaf-spring DNA-origami nanoengine that drives a passive follower*, **Nature Nanotechnology 19, 226–236** (выпуск 2024-02; online 2023-10-19). DOI `10.1038/s41565-023-01516-x`. **Open access, CC BY 4.0.**

Четыре аудитированных поверхности (полные инвентаризации иdigests — в KnowledgePack):

| # | Поверхность | Canonical pin | Права | Статус доступности |
|---|---|---|---|---|
| 1 | Статья | DOI `10.1038/s41565-023-01516-x`, nature.com HTTP 200 | CC BY 4.0 | Открыта, полный текст + Methods |
| 2 | Nanobase structure **196** | `https://nanobase.org/structures/196` (URL из статьи `/structure/196` → 404); API `api.nanobase.org/api/v1/structure/structure-files?id=196`; per-entry DOI **нет** | Явной лицензии нет; по условиям Nanobase copyright у авторов публикации ⇒ CC BY 4.0 практически применим (задокументированное умозаключение, не явный grant) | Открыто; все 12 файлов скачаны, SHA-256 верифицированы |
| 3 | Zenodo MD data | DOI `10.5281/zenodo.8248808` (concept `…8248807`), единственная версия 2023-08-28 | CC-BY-4.0 | Открыто; 5 файлов ≈ 46.17 GB — **не скачивались** (инвентаризация name/size/MD5 только); SHA-256 Zenodo не предоставляет |
| 4 | Analysis repo | `sulcgroup/hinges` branch `main` @ `7c8b04a654b2440e4b6bab5b0abcb7e4335824d9` (единственная ветка; 0 релизов; push 2023-03-09) | **LICENSE ОТСУТСТВУЕТ** (GitHub license null, LICENSE/COPYING нет в 83-элементном дереве) ⇒ все права сохранены, режим `REFERENCE_ONLY` | Открыто; 5 ключевых файлов скачаны и верифицированы |

Дополнительно установлено из Data availability статьи: smFRET-код `walterlab-um/rhythmically-pulsing-leaf-spring_SMCodes` (MIT), smFRET-данные U-M Deep Blue `474299762` (**HTTP 403** для скриптовых запросов — доступность UNKNOWN).

## 2. Механизм по первоисточнику (B4)

- **Driver:** leaf-spring наноинжинер ≈ 70×70×12 nm — две жёсткие origami-плечи (по 18-helix bundle), соединённые податливым шарниром с шестью ssDNA-«flexure» участками; плечи образуют листовую рессору, открывающуюся/закрывающуюся.
- **Актюация — химическое топливо, НЕ температура и НЕ follower:** dsDNA-шаблон (dsDNA-t) перекинут между плечами; HaloTag–T7 RNA-полимераза (ковалентно на одном плече через chloroalkane) транскрибирует шаблон; транскрипция подтягивает противоположное плечо → закрытие; на терминаторе полимераза отпускает шаблон → открытие; цикл повторяется (расход NTP). Температура (23/37 °C) модулирует вторичную структуру flexure и скорости, но не является драйвером.
- **Follower:** пассивная, «похожей формы» origami, соединяемая с никед-драйвером **nNE** в D–F пару (60% ± 20% образования по 199 TEM-микрографиям); design — Supplementary Dataset 1.
- **Варианты в данных:** `nNE` (никед), `NE`, `NE_NB` (dsDNA-t удалён, −332 nt), `nNE_NB`; `NS` = base pairing в flexure отключён (запрет вторичной структуры).
- **Как задано механическое воздействие в MD:** внешняя сила 16 pN между точкой крепления полимеразы и терминатором (`T7_force.txt`: `constant_trap`, particle 8694 ↔ ref 7374, stiff 0.3290, r0 8.8); pull 1e7 шагов → release 2e7 шагов. Химическое топливо в coarse-grained модели **не симулируется** — только эквивалентное внешнее усилие.
- **Anchors/ports (по опубликованным данным):** trap-привязки — нуклеотидные частицы **8694** (движущая) и **7374** (опорная) в комбинированной (linked) топологии; индексы анализа `get_k.py` — arm1 `[2034, 6657]`, arm2 `[4593, 4411]`. **Соответствие этих индексов нашим импортированным `NE.top`/`nNE.top` НЕ верифицировано** (маппинг index→structure нигде не задокументирован) ⇒ все порты в спеке ниже — `UNKNOWN`/`UNVERIFIED`, кроме trap-пар, которые относятся к **linked** (комбинированной) топологии, отсутствующей в Nanobase-наборе.
- **DOF модели:** жёсткие нуклеотиды oxDNA2 (позиция + ориентация), гибкость сосредоточена в ssDNA flexure (6 участков по 52–53 nt); наблюдаемая механика — угол между плечами и межцентровое расстояние.
- **Наблюдаемые источника:** inter-arm angle (SVD главных осей; nNE 37 °C: медиана 58.4°, диапазон 26.6–81.6°), расстояние центров плеч (×0.85 nm/ед.), равновесные распределения угла, эффективные жёсткости по equipartition (K = 0.5/var), скорости закрытия под 16 pN и переоткрытия после release, H-bond occupancy в flexure; эксперимент — скорости транскрипции, smFRET-двеллы, % образования D–F.

## 3. Импорт-валидация (B5) — выполнено

Инструмент: `scripts/knowledge_pack/import_validation.py` (строгие парсеры **переиспользованы** из `scripts/hinge_family/oxdna_topology.py` / `oxdna_conf.py`, без дублирования). Evidence: `EX-PREP-S17-R1/evidence/s17-import-validation-R1.json`.

| Пара | Nt | Стэнды | Counts | Целостность цепей | Детерминированный ре-импорт | Structural digest |
|---|---|---|---|---|---|---|
| `NE.top`+`NE.dat` (sha256 `5074d559…` / `c73aeb86…`) | 14 343 | 161 (160 linear + 1 circular: 7 249 nt M13-тип каркас) | OK | OK | OK | `2722f75fa7274180…` |
| `NE_NB.top`+`NE_NB.dat` (`5abfcbde…` / `c802eb95…`) | 14 011 | 163 | OK | OK | OK | `c34da6526fc64a17…` |
| `nNE.top`+`nNE.dat` (`71eca286…` / `b0722a5b…`) | 14 343 | 163 | OK | OK | OK | `93787ca9a8f791af…` |

Negative control: однобайтовое повреждение `NE.top` → импорт fail-closed (parse error), digest меняется. Состав оснований NE: A 4130 / C 3025 / G 3032 / T 4156. `NE.dat` — конечная конфигурация равновесия (t=1e9, box 310³) → пригодна как стартовая для будущих прогонов. **Граница:** это структурная валидация файлов; никакая симуляция/научное утверждение из неё не следует.

## 4. Предварительный MechanicalComponentSpec (черновик, НЕ контракт v1)

```text
component_id: S17-nanoengine-NE            (варианты: nNE, NE_NB — отдельные детали)
design_source: Nanobase structure 196 (pins в KnowledgePack)
topology: oxDNA_top NE.top  (14343 nt / 161 strands; каркас 7249nt circular)
configuration: NE.dat (равновесный endpoint t=1e9)
local_frame: UNVERIFIED (не задокументирован в источниках; требуется выбор и фиксация при/spec-ревизии)
ports:
  - trap_drive (particle 8694 linked-topology): UNVERIFIED для импортированных файлов
    (относится к отсутствующему linked.top; требует пересчёта индексов)
  - trap_ref (particle 7374 linked-topology): UNVERIFIED (аналогично)
  - arm1_analysis_indices [2034,6657] / arm2 [4593,4411]: UNVERIFIED соответствие NE.top
  - follower_attachment (nNE D–F interface): UNKNOWN (рецепт linked.top отсутствует)
mechanical_dofs: угол между плечами (главная), межцентровое расстояние; flexure = 6 ssDNA-петель
drive_model_in_md: внешняя сила 16 pN constant_trap (химическое топливо НЕ симулируется)
environment: oxDNA2, salt 2.0, NVT john, dt 0.003, 23/37C (37C-инпуты предоставлены)
observables: inter_arm_angle, arm_center_distance_nm, equipartition_K,
             closing_rate_16pN, flexure_hbond_occupancy (все DEFINED_IN_SOURCE),
             driver_follower_motion_transfer (PROPOSED/UNVERIFIED)
```

Жёсткое правило: никакие `UNKNOWN`/`UNVERIFIED` поля не заполняются предположениями; их закрытие — задача будущих bounded WO (index-mapping верификация, восстановление linked-topology рецепта из Zenodo-архивов при необходимости).

## 5. Недостающие входы (полный список — в KnowledgePack.missing_inputs)

Критичные для будущего E5: `polymerase_positioning.txt` (файл внешних сил для input_pull, отсутствует в Nanobase-наборе; UNKNOWN, внутри ли Zenodo zips), рецепт сборки `linked.top`/`first_conf.dat` (комбинированная driver+follower топология), точный пин версии oxDNA («late-2020», без commit/tag), 23 °C инпуты, Nanobase entry-метаданные, provenance-маппинг `driver_*/follower_*` данных, доступ к smFRET-датасету Deep Blue.

## 6. Права и ограничения использования (сводка)

1. **Можно:** скачивать по pinned URLs и верифицировать digests; публиковать ссылки, digests, производные результаты анализа с атрибуцией CC BY 4.0 (статья/Zenodo/Nanobase-структуры).
2. **Нельзя (сейчас):** вендорить в Git любые поверхности (владелец-решение требуется; pack redistribution=RESTRICTED блокирует vendoring fail-closed); переиспользовать/распространять код `sulcgroup/hinges` (нет лицензии) — только просмотр по pinned commit и независимая ре-имплементация алгоритмов.
3. **UNKNOWN:** перераспределение Nanobase-структур за пределами CC BY-вывода; Deep Blue smFRET лицензия; содержимое Zenodo zips.

## 7. Черновая граница будущего HIGH scientific WO (NL6-001 / E5) — НЕ dispatch

- **Предусловия (не сокращаются):** NL5 accepted (сейчас `NL5-002=WAITING_HUMAN`, terminal MISMATCH), U1/R2 активны (сейчас `AUTHOR_U1=NOT_ASSIGNED`, `R2=WAITING_HOST/NOT_ACTIVE`), preregistered protocol с frozen seeds/observables, fresh review + verify, HG-гейты по действующему harness.
- **Кандидатная постановка (только набросок для будущего preregistration):** равновесная характеристика импортированного NE/nNE на разрешённом научном исполнителе (angle distribution, equipartition K против статьи), затем driven-фаза (16 pN trap по T7_force-паттерну после восстановления недостающих входов), no-drive/no-load контроли, повторные циклы pull/release, integrity-чек, uncertainty; driver→follower перенос — после восстановления linked-topology рецепта.
- **Критерий успеха формулируется и замораживается ДО данных**; отрицательный/неопределённый результат сохраняется. Никакие статусные поля NL* этим WO не меняются.

## 8. Использованные команды (воспроизводимость)

```bash
# контракты и тесты
python3 -m unittest tests.test_knowledge_pack tests.test_knowledge_pack_import
# импорт-валидация (файлы — user-side pinned download; в Git НЕ хранятся)
PYTHONPATH=scripts python3 -c "from knowledge_pack.import_validation import import_paired; \
  r=import_paired('NE.top','NE.dat'); print(r.as_dict())"
# гейты ветки
python3 -m unittest discover -s tests -t .
PYTHONPATH=scripts python3 -m harness.cli check-consistency
PYTHONPATH=scripts python3 -m harness.workflow_lint
```
