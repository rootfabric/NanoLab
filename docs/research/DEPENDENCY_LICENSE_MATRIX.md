# NL0-002 — Матрица зависимостей и лицензий MVP

Исполнение: `EX-NL0-002-R1`; repair `EX-NL0-002-R1-REPAIR1` зафиксировал immutable license evidence (пины проверенных лицензий: `docs/evidence/NL0-002/LICENSE_EVIDENCE_PINS_R1.md`, проверка 2026-09-08). Все статусы — первичная проверка (репозиторий/API издателя), не юридическое заключение. Ни один пакет не устанавливался и не запускался; это NL1/INFRA.

## 1. Матрица

| Component | Exact source/version | Role | Code license | Data/model license | Redistribution | Modification | Citation | Access mode | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| oxDNA / oxpy | github.com/lorenzo-rovigatti/oxDNA @ `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` (E1-пин; runtime-версию выбирает NL1) | Physics engine + Python bindings | GPL-3.0 (root LICENSE, blob `94a9ed0`, проверено GitHub API на pinned commit) | Force field — научные публикации (oxDNA1/2, RNA); параметры в коде под GPL | Сама зависимость: N/A (не перераспространяем). Копирование кода/файлов: under GPLv3 terms (preserve applicable copyright/license/no-warranty notices; provide a copy of GPLv3 when conveying covered source; corresponding-source obligations apply where relevant) | GPLv3 terms | Poppleton JOSS 2023 (10.21105/joss.04693); Rovigatti JCC 2015 (10.1002/jcc.23763) | dependency (build/install) | RIGHTS_AND_REDISTRIBUTION_AUDIT.md §1 | CLEAR |
| oxDNA analysis tools | входит в lorenzo-rovigatti/oxDNA (`analysis/`, incl. `paper_examples`) | Анализ траекторий | GPL-3.0 (та же лицензия репозитория) | — | under GPLv3 | GPLv3 terms | Poppleton NAR 2020 (10.1093/nar/gkab324) | dependency | README pinned commit | CLEAR |
| E1 fixtures (DSDNA8) | тот же repo/commit, 4 файла test/DNA/DSDNA8 | Regression oracle E1 | GPL-3.0 (покрыты root LICENSE) | — | under GPLv3 terms; preserve applicable copyright/license/no-warranty notices; provide a copy of GPLv3 when conveying covered source; corresponding-source obligations apply where relevant | GPLv3 terms | те же, что oxDNA | DOWNLOAD_ON_SETUP (метаданные в Git, загрузка по pinned commit + SHA-256) | INPUT_AVAILABILITY.md; AUDIT §1 | CLEAR |
| E2 hinge pack | github.com/gauravarya77/DNA-hinge-simulations @ `23fd1ff7731e9017bd776f49206dc42d70d9fe91` | E2 executable seed | **нет LICENSE** → UNKNOWN | designs/inputs — UNKNOWN | not established | not established | Shi–Castro–Arya, 10.1021/acsnano.7b00242 | REFERENCE_ONLY + user-side download by exact commit | AUDIT §2 | UNKNOWN → OWNER_DECISION |
| scadnano (+ python package) | github.com/UC-Davis-molecular-computing/scadnano @ `70f0e4bde70025cd43abfce1e390095f0d86625a` (checked 2026-09-08); pypi: scadnano | Программный дизайн конструкций, экспорт oxDNA | MIT (`LICENSE.txt` blob `191a099d5d32c0399669cd7b7df9aaadeeeb2331`, SHA-256 `1573dffcff6a09abe8e5369e5299377b9f43b8fa89ef9f48bcda976cabac1e15`) | — | MIT terms | MIT terms | научное использование: cite scadnano paper (Conway et al., 10.1016/j.jmb.2022.167360 рекомендуется авторами) | dependency (pip) | LICENSE_EVIDENCE_PINS_R1.md (GitHub API; blob verify byte-exact) | CLEAR |
| oxView | github.com/sulcgroup/oxdna-viewer @ `047e0bf718f315577556de2ba5a6be64dede48dc` (checked 2026-09-08) | Просмотр/редактирование конструкций и траекторий | GPL-3.0 (`LICENSE` blob `94a9ed024d3859793618152ea559a168bbcbb5e2` — тот же канонический GPLv3 blob, что у oxDNA; SHA-256 `8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903`) | — | under GPLv3 terms (см. §2 о границах) | GPLv3 terms | sulc group / oxView paper при научном использовании | dependency (web app / release) | LICENSE_EVIDENCE_PINS_R1.md | CLEAR (copyleft — учитывать при bundling) |
| PyMBAR | github.com/choderalab/pymbar @ `ed40ec3bbef03bb08938ad1a74d459b0d1ab81f7` (checked 2026-09-08); pypi: pymbar | Статистика коррелированных выборок, E4/analysis | MIT (`LICENSE` blob `9cbae2a7e0268fef2d497cf112b5f41403016c4e`, SHA-256 `b06216b25962856729369804671b10ac7daed2237597f285abc540c363c19da2`) | — | MIT terms | MIT terms | Shirts & Chodera JCP 2008 (10.1063/1.2978177) | dependency (pip) | LICENSE_EVIDENCE_PINS_R1.md | CLEAR |
| AiiDA (aiida-core) | github.com/aiidateam/aiida-core @ `8cad70e2d235f54093406d8af06359450209f49e` (checked 2026-09-08); pypi: aiida-core | Provenance/workflow orchestration | MIT (`LICENSE.txt` blob `68314cde76f81978f36fb7cb0e2ca49fa04b1aab`, SHA-256 `ff614a96e214fded6f5745709783676e46d032b5fa3a32aaaabf80020bb3f388`; GitHub repo-level detection `NOASSERTION` из-за доп. лицензионных файлов в дереве — проверенный текст LICENSE.txt = MIT, copyright EPFL/THEOS + Robert Bosch LLC) | — | MIT terms | MIT terms | aiida paper (Huber et al., 10.1107/S205225252000059X рекомендуется) | dependency (pip) | LICENSE_EVIDENCE_PINS_R1.md | CLEAR |
| aiida-shell | github.com/aiidateam/aiida-shell @ `e420c1d2cd7fc06882e538c643c5f0defa231789` (checked 2026-09-08) | Тонкий запуск внешних executable | MIT (`LICENSE.txt` blob `3985753502c0a5a4c1a4c225382b0c283ce19da3`, SHA-256 `fe6d111964cc801aac228825510d43d0bc3202fdcd4dfbeec36f4c63244b41b1`) | — | MIT terms | MIT terms | — | dependency (pip) | LICENSE_EVIDENCE_PINS_R1.md | CLEAR |
| Ax (Adaptive Experimentation) | github.com/facebook/Ax @ `778e22ffdb05fb8a0a5e8527c283d102a598f7da` (checked 2026-09-08); pypi: ax-platform | Планируемая AI/optimization зависимость (E3), НЕ часть E1 | MIT (`LICENSE` blob `b93be90515ccd0b9daedaa589e42bf5929693f1f`, SHA-256 `da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93`) | pretrained models (если используются) — отдельная проверка | MIT terms | MIT terms | ax paper при научном использовании | dependency (pip, planned) | LICENSE_EVIDENCE_PINS_R1.md | CLEAR |
| BoTorch | canonical: github.com/meta-pytorch/botorch @ `d4b9fc655034f6c6186f1cdc73398b47d3d55b7f` (checked 2026-09-08); исторический alias: pytorch/botorch → server-side redirect, тот же repository id 142940093; pypi: botorch | Байесовская оптимизация под Ax | MIT (`LICENSE` blob `b93be90515ccd0b9daedaa589e42bf5929693f1f`, SHA-256 `da6d3703ed11cbe42bd212c725957c98da23cbff1998c05fa4b3d976d1a58e93` — байтово тот же MIT-текст, что у Ax) | — | MIT terms | MIT terms | botorch paper (10.48550/arXiv.1910.07006 рекомендуется) | dependency (pip, planned) | LICENSE_EVIDENCE_PINS_R1.md | CLEAR |
| NANOBASE | nanobase.org (S10) | Поиск исходных конструкций (будущее) | сайт/софт/записи — разные режимы; copyright deposited structures у авторов публикаций | per-record | not established per-record | not established | публикация NANOBASE (S10) при использовании | REFERENCE_ONLY per record | AUDIT §4 | UNKNOWN per-record |

Пины в колонке 2 — immutable identity проверенных в этом аудите subjects (checked commit + license path + Git blob SHA-1 + SHA-256, метод и полная таблица: `LICENSE_EVIDENCE_PINS_R1.md`, проверка 2026-09-08). Runtime-пин конкретных PyPI-версий и сборки oxDNA выполняет NL1-001; он не нужен для воспроизводимости license audit, который привязан к immutable license subject.

## 2. Выводы для MVP-стека и границы GPL

Это не юридическое заключение. Ниже — рабочая классификация ситуаций распространения, чтобы не подменять анализ одной фразой «конфликт / не конфликт».

```text
AGGREGATE            = независимые работы, распространяемые рядом (отдельные репозитории/пакеты/каталоги,
                       отдельные исполняемые файлы), каждая под своей лицензией; GPL не распространяется
                       на соседние самостоятельные работы
SEPARATE_EXECUTABLE  = oxDNA/analysis tools или oxView как отдельный executable, взаимодействующий с
                       NanoLab через CLI/files/pipes — объединения кода нет; по умолчанию ближе к
                       aggregate, чем к combined work
SAME_PROCESS_BINDING = import/linking oxpy внутри процесса NanoLab — потенциальный combined/derivative
                       work вопрос; зависит от фактической интеграции и conveyance; НЕ эквивалентно
                       отдельному executable
MODIFIED_GPL_CODE    = модификация GPL-файлов и распространение изменённых версий — обязанности GPLv3
                       применимы к изменённому материалу в любом сценарии
```

```text
DEPENDENCIES_CLEAR       = 9 software dependencies: oxDNA/oxpy, oxDNA analysis tools, scadnano, oxView, PyMBAR, AiiDA, aiida-shell, Ax, BoTorch
DEPENDENCIES_RESTRICTED  = S08 article/SI/movies (publisher copyright; cite-only)
DEPENDENCIES_UNKNOWN     = DNA-hinge-simulations (E2 pack), NANOBASE per-record, sulcgroup/hinges (S17, deferred)
NOTE                     = E1 fixture (DSDNA8) — отдельная строка матрицы, тоже CLEAR; не входит в «9 software
                           dependencies», это научный вход, а не программная зависимость
```

- Все запланированные программные зависимости MVP пермиссивны (MIT), кроме oxDNA/oxpy/analysis tools и oxView — GPL-3.0. Независимые MIT/Apache-2.0 файлы и модули NanoLab могут сосуществовать с GPLv3-материалом при корректной структуре распространения (aggregate): само наличие GPL-файла рядом с пермиссивным кодом не делает пермиссивный код GPL-covered.
- Обязанности для combined covered work определяются фактической интеграцией и conveyance, а не названиями зависимостей.
- `oxDNA executable` и `oxpy binding` — не одна и та же packaging situation: запуск отдельного oxDNA/oxView процесса (SEPARATE_EXECUTABLE) и будущий same-process import/linking `oxpy` (SAME_PROCESS_BINDING) оцениваются по-разному.
- Любая будущая same-process `oxpy` integration до фиксации release-архитектуры:

```text
REQUIRES_OWNER_DECISION
REQUIRES_LEGAL_REVIEW
```

- До этого решения безопасная политика проекта:

```text
DOWNLOAD_ON_SETUP   — GPL-компоненты не хранятся в Git NanoLab, скачиваются на setup
NO_VENDORING_YET    — GPL-код не вендорится в дерево NanoLab
```

- Если будущий MVP распространяется как bundle, включающий oxView или иные GPL-компоненты, — соответствующие части остаются under GPLv3 terms; обязанности (preserve applicable notices, provide license copy, corresponding source where relevant) применяются к conveyed GPL-материалу.
- Ax/BoTorch — planned только; в E1 не входит (подтверждает формулировку NL0-001).
- `VENDOR_NOT_RECOMMENDED` для GPL-кода в дереве NanoLab — консервативная проектная политика до решения владельца/legal review, а не утверждение о юридической невозможности; режим доступа — pip/build/dependency.

## 3. Варианты лицензии NanoLab (решение за владельцем, агент не назначает)

| Option | Код | Ключевые последствия |
|---|---|---|
| A | Apache-2.0 | Pemissive + явный patent grant; NOTICE-обязанности; совместима с MIT/GPL-стеком; удобна для будущих коммерческих/промышленных переиспользований; чуть тяжелее в сопровождении (NOTICE) |
| B | MIT | Максимально простая permissive, без явного patent grant; экосистемно привычна (все MIT-зависимости); минимальный friction для вклада |
| C | GPL-3.0-or-later | Copyleft: производные NanoLab-кода обязаны открываться под GPL; сильнейшая гарантия открытости производных; совместима с oxDNA/oxView (тот же класс); может отпугнуть часть промышленных пользователей |

Документация (отдельно от кода): CC BY 4.0 (свободное переиспользование с атрибуцией — удобнее для научной документации) либо CC BY-SA 4.0 (share-alike для производных документов). Данные/научные артефакты NanoLab — третий, отдельный класс; режим выбирается вместе с решением о публикации benchmark-пакетов (зависит и от прав E2).

Принципиально: **лицензия NanoLab ≠ лицензии сторонних научных входов**. Собственная лицензия не легализует ни E2-файлы (UNKNOWN), ни S08-материалы (ACS copyright), ни NANOBASE-записи. Выбор permissive Option A/B не запрещает вендоринг GPLv3-fixtures автоматически и не разрешает его автоматически: вендоринг — архитектурное решение (`REQUIRES_OWNER_DECISION`, при нестандартной структуре — `REQUIRES_LEGAL_REVIEW`); текущая безопасная политика — `NO_VENDORING_YET`.

Рекомендация (не решение): Apache-2.0 (A) для кода + CC BY 4.0 для документации — лучший баланс patent-grant/permissiveness для заявленной миссии; окончательный выбор — владелец.

## 4. Citation policy (научная атрибуция; отдельно от license obligations)

Научное цитирование — академическая обязанность; она не заменяет, не отменяет и не расширяет условия лицензий.

- oxDNA stack: три DOI из README (код/CUDA/analysis tools).
- Shi–Castro–Arya: 10.1021/acsnano.7b00242 при любом использовании hinge-пакета.
- PyMBAR: 10.1063/1.2978177 (при использовании MBAR).
- scadnano/AiiDA/Ax/BoTorch: paper-citation по документации проектов при научном использовании.

### 4.1 License obligations (GPLv3, нейтральная сводка)

Если в будущем состоится conveyance GPLv3-материала (fixtures/oxDNA/oxView) со стороны NanoLab, применяются — без привязки к отдельному генерическому файлу NOTICE:

- preserve applicable copyright/license/no-warranty notices в соответствующих файлах;
- provide a copy of GPLv3 when conveying covered source;
- corresponding-source obligations применяются там, где уместно (выбранный способ object-code conveyance определяет их объём).

Отдельный standalone `NOTICE`-файл сам по себе не является определяющей обязанностью GPLv3. Решение о наличии такого файла в репозитории NanoLab связано с выбором собственной лицензии (у Apache-2.0 — собственные NOTICE-требования) и практикой атрибуции, а не с GPLv3 по умолчанию.
