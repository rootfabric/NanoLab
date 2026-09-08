# Источники и границы проверки

Версия: foundation-r1 + NL0-001 source-selection update. Проверка описания инструмента или наличие публичного repository не означает проверку интеграции, всех прав или физическую валидацию. Запуски E0–E6 NanoLab по этим источникам ещё не выполнялись.

## S01 — oxDNA, oxpy и analysis tools

[Официальная документация](https://lorenzo-rovigatti.github.io/oxDNA/).

Подтверждено описание специализированной укрупнённой модели, MD/MC, CPU/CUDA-путей, внешних воздействий, Python-интерфейса и анализа. Конкретную версию, модель и совместимость выбирает NL1. Не универсальный симулятор произвольной химии.

## S02 — Границы интерпретации oxDNA

*A Primer on the oxDNA Model of DNA: When to Use it, How to Simulate it and How to Interpret the Results*.

[Статья авторов модели](https://www.frontiersin.org/journals/molecular-biosciences/articles/10.3389/fmolb.2021.693710/full), DOI: 10.3389/fmolb.2021.693710.

Основание для отдельной проверки применимости, sampling и осторожной интерпретации времени укрупнённой модели. Не даёт автоматической калибровки каждого нового устройства.

## S03 — Подготовка и моделирование оригами

*How we simulate DNA origami*.

[Авторская версия](https://arxiv.org/html/2409.13206v1), arXiv:2409.13206v1.

Подтверждены проблемы импорта/релаксации, необходимость отделять подготовительные ограничения от production и ограниченность моделирования полной самосборки. Доступность всех конкретных design-файлов из руководства ещё проверяется в NL0; приведённые в статье параметры не копируются как универсальные defaults NanoLab.

## S04 — scadnano

[Документация Python](https://scadnano-python-package.readthedocs.io/en/latest/).

Проверены описания программного дизайна и `write_oxdna_files` / `write_oxview_file`. Не проверено сохранение свойств конкретного выбранного шарнира после экспорта; это обязательный тест адаптера.

## S05 — AiiDA provenance

[Concepts](https://aiida.readthedocs.io/projects/aiida-core/en/stable/topics/provenance/concepts.html).

Основа происхождения процессов и данных. Внешняя литература, дополнительные артефакты и решения ИИ должны регистрироваться самой интеграцией.

## S06 — aiida-shell

[Официальное введение](https://aiida-shell.readthedocs.io/en/latest/).

Позволяет прототипировать запуск executable через AiiDA без предварительного написания полного специализированного плагина. Не подтверждает существования готового NanoLab–oxDNA adapter.

## S07 — PyMBAR timeseries

[Документация](https://pymbar.readthedocs.io/en/stable/timeseries.html).

Средства оценки корреляций, области после уравновешивания и эффективного размера выборки. Автоматическая эвристика не гарантирует, что траектория исследовала все медленные состояния.

## S08 — Подвижные ДНК-компоненты Sharma et al.

Sharma et al., *Characterizing the Motion of Jointed DNA Nanostructures Using a Coarse-Grained Model*.

[Издатель](https://pubs.acs.org/doi/10.1021/acsnano.7b06470), DOI: **10.1021/acsnano.7b06470**.

Подтверждены hinge/sliding/coupled joints в oxDNA и заявленное авторами хорошее согласие с experiments. В NL0-001 повторно проверена Supporting Information: публично перечислены PDF с definitions/additional simulation results и movies. Отдельный machine-readable caDNAno/oxDNA topology/config/input pack в ограниченном поиске **не найден**. Это статус `INPUT_PACK_NOT_LOCATED`, а не доказательство отсутствия данных вообще. Поэтому S08 сохранён как scientific reference, но не выбран executable E2 seed.

## S09 — Спорная двухстабильность

Wong, Doye, *The free-energy landscape of a mechanically bistable DNA origami*.

[Авторская запись и аннотация](https://arxiv.org/abs/2201.08920), DOI: 10.3390/app12125875.

Авторы сообщают один минимум для бездефектной структуры в oxDNA, несмотря на ожидавшуюся двухстабильность; возможная роль дефектов обсуждается как вопрос, не доказанная причина. Полное воспроизведение E4 остаётся будущей работой.

## S10 — NANOBASE

*Nanobase.org: a repository for DNA and RNA nanostructures*.

[Публикация](https://pmc.ncbi.nlm.nih.gov/articles/PMC8728195/), [проект](https://nanobase.org/).

Источник кандидатов конструкций. Наличие базы не означает разрешения на перераспространение конкретного deposited design; Nanobase указывает, что copyright deposited structures остаётся у авторов соответствующих публикаций.

## S11 — BoTorch / constrained optimization

[Официальная документация ограничений](https://botorch.org/docs/constraints), [архивный пример замкнутого цикла](https://archive.botorch.org/tutorials/closed_loop_botorch_only).

Подтверждена возможность ограниченной BO; для простого случая документация предлагает рассмотреть Ax. Это будущая E3 инфраструктура.

## S12 — OpenKIM

[Verification checks](https://openkim.org/browse/verification-checks/alphabetical), [Getting started](https://openkim.org/doc/overview/getting-started/).

Кандидат инфраструктуры E6. Проверка реализации потенциала не доказывает его применимость к выбранной наноструктуре.

## S13 — oxView

[Официальный репозиторий](https://github.com/sulcgroup/oxdna-viewer).

Просмотр/редактирование конструкций и траекторий; визуальная согласованность не заменяет численную/научную проверку.

## S14 — ASE

[Официальная документация](https://docs.ase-lib.org/).

Кандидат интерфейса атомистических структур и калькуляторов для следующей специализации.

## S15 — oxDNA upstream regression fixtures — выбранный E1 source

Repository: [lorenzo-rovigatti/oxDNA](https://github.com/lorenzo-rovigatti/oxDNA), pinned commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`.

В NL0-001 проверены официальные fixtures:

- `test/DNA/DSDNA8/MD` — выбран E1; topology/config/input + `quick_compare` numerical oracle;
- `test/DNA/SSDNA15/MD` — fallback;
- `examples/HAIRPIN` — более богатый, но существенно более дорогой conformational example.

Root repository license на inspected commit: GNU GPL v3. Exact paths, Git object identities и SHA-256 выбранного DSDNA8 пакета находятся в `INPUT_AVAILABILITY.md`.

NL0-002 подтвердил независимо (GitHub API на pinned commit): root `LICENSE` = полный текст GPL-3.0, blob `94a9ed024d3859793618152ea559a168bbcbb5e2`; отдельных лицензий для `test/` нет → fixtures покрыты GPLv3. Обязательные citation: Poppleton JOSS 2023, Rovigatti JCC 2015, Poppleton NAR 2020. Режим: `DOWNLOAD_ON_SETUP`; подробности — [RIGHTS_AND_REDISTRIBUTION_AUDIT.md](RIGHTS_AND_REDISTRIBUTION_AUDIT.md) §1.

NL0-003 (EX-NL0-003-R1) повторно скачал все четыре файла DSDNA8/MD на том же pinned commit: SHA-256 совпали по всем позициям с пинами `INPUT_AVAILABILITY.md`. Протокол E1 заморожен до кампании: [PREREGISTRATION_E1_R1.md](PREREGISTRATION_E1_R1.md) (`E1-PROTO-R1`, условия и критерий — verbatim из upstream `quick_input`/`quick_compare`, без выдуманных значений).

## S16 — Shi–Castro–Arya compliant DNA hinges — выбранный E2 source

Shi, Castro, Arya, *Conformational Dynamics of Mechanically Compliant DNA Nanostructures from Coarse-Grained Molecular Dynamics Simulations*, DOI **10.1021/acsnano.7b00242**.

[Статья](https://pubs.acs.org/doi/10.1021/acsnano.7b00242), [авторский simulation repository](https://github.com/gauravarya77/DNA-hinge-simulations).

NL0-001 подтвердил прямую связь статьи с repository и pinned repository commit `23fd1ff7731e9017bd776f49206dc42d70d9fe91`, tree `b2d6cebc7a33ed13e4e9c8d79fe8350ce11e82b9`. В нём реально присутствуют caDNAno designs `0b/11b/32b/53b/74b`, подготовительные scripts, pre-equilibrated `.conf`, `.top` и CPU/GPU input files. Статья сообщает oxDNA2 и параметрическое семейство compliant springs, поэтому этот источник выбран executable seed для E2.

Ограничение: в полном inspected tree отдельный `LICENSE` файл не обнаружен. Public repository visibility не считается лицензией; redistribution/use audit перед копированием — NL0-002.

NL0-002 подтвердил независимо (GitHub API, полный live-tree перечёт pinned commit): LICENSE/COPYING/NOTICE отсутствуют во всём tree; GitHub license detection пустая; репозиторий статичен с 2017-04-04; все README прочитаны — правовых statements нет. `REDISTRIBUTION_RIGHTS = UNKNOWN`; режим `REFERENCE_ONLY` + user-side download by exact commit; `MovieS1.mp4` и статья — отдельные copyright, в NanoLab не переносятся. Решение за владельцем (контакт авторов); подробности — [RIGHTS_AND_REDISTRIBUTION_AUDIT.md](RIGHTS_AND_REDISTRIBUTION_AUDIT.md) §2.

NL0-003 (EX-NL0-003-R1) подготовил постановку E2 без запуска кампании: первый шарнир `0b`, требования к определению угла/целостности из первоисточника, family допустимых изменений = пять опубликованных вариантов, decision rule для расхождения 298 K (статья) vs 300 K (pinned `pro_CPU.in`): [E2_SETUP_R1.md](E2_SETUP_R1.md). Права и зависимости E2 не изменились.

## S17 — Leaf-spring nanoengine — будущий rich benchmark

Centola et al., *A rhythmically pulsing leaf-spring DNA-origami nanoengine that drives a passive follower*, Nature Nanotechnology, article `s41565-023-01516-x`.

[Статья](https://www.nature.com/articles/s41565-023-01516-x), [Zenodo MD data](https://doi.org/10.5281/zenodo.8248808), [analysis repository](https://github.com/sulcgroup/hinges).

Статья ссылается на Nanobase structure 196 для design/starting structures, Zenodo для generated MD trajectories и `sulcgroup/hinges` для processed data/analysis. Zenodo dataset содержит десятки гигабайт, поэтому это не E1 и не первый E2, а будущий benchmark для driven/composite mechanisms.

## Как расширять реестр

Для нового источника: первичная ссылка/DOI, inspected version/ref, поддерживаемое утверждение, machine inputs, missing data, rights и связь с experiment. Не переносить цифры, лицензии или scientific claims из старого обсуждения без новой проверки.
