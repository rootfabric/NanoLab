# NL2-002 — REVIEWER VERDICT (независимый review evidence-пакета E1-R2)

**Вердикт: PASS** (научное объявление статуса E1 остаётся за Director; данный вердикт — независимая проверка исполнителя).

- Рецензент: независимый fresh-агент (REVIEWER), без доступа к контексту имплементёра; только Git-факты subject-коммита и собственные воспроизведения.
- Subject: ветка `work/nl2-002-validate-e1-r1` @ **`6cc7fdef24d9d3275b5a5a8efab4dc806e7cf893`** (tree `137679f93af344d2bc7400745026e61f83d8f0b3`), base `0176098ed052ec29503ac5c353463be0cc8ea167` (main, NL2-001 ACCEPTED).
- Review-ветка: `review/nl2-002-validate-e1-r1` (worktree `C:\NanoLab\review-nl2-002`, checkout 6cc7fde).
- Дата review: 2026-09-10. Это review ПЕРЕД первым научным объявлением статуса E1 — применён максимальный уровень строгости.
- Frozen-контекст: `E1-PROTO-R1` (§3 verbatim, §5.1 observable/полоса −1.37970256144±0.15, §5.2 целостность, §9 семантика исходов, §10 запрет пост-хок исключений) + superseding `E1-PROTO-R2` (freeze `R_confirm = 3`, distinct seeds, до confirmatory кампании; наследование без изменений).

## 1. Резюме

Все шесть bounded-проверок выполнены, нарушений freeze-дисциплины, scope или честности интерпретации не обнаружено. Ключевые результаты **воспроизведены рецензентом независимо** из опубликованных blob'ов:

| Проверка | Результат |
|---|---|
| 1. Scope diff 0176098..6cc7fde | PASS — только allowed_paths; SESSION_LOG.md строго append; все forbidden-пути blob-идентичны base |
| 2. Freeze-дисциплина | PASS — freeze `f34e62c` (21:21:21+10) → campaign-START `42cb851` (21:23:45+10) → прогоны; frozen-файлы не менялись после freeze; prereg R1/R2 blob-идентичны base; 7/7 seed попарно различны (факты `log.dat`) |
| 3. Воспроизведение статистики | PASS — avg col2 ×3 + S001 кросс-чек совпали до последнего знака; mean/SD(n−1)/range пересчитаны — точное совпадение; критерий §9 MET подтверждён формально |
| 4. Протокольная чистота | PASS — verbatim-фингерпринты §3 в логах; новые run ID без переиспользований; терминал-перед-анализом; контрактные манифесты (массивы, 40-hex); digest-vs-blob 15/15; jsonschema-поверхности 15/15 |
| 5. Честность интерпретации | PASS — SD 11.5% vs пилот 5.6% явно в remaining_risks; §4-диагностика не gate и не использовалась для подгонки; campaign-level = NOT_EVALUATED; ACCEPTED не выставлен; SUPPORTED следует из данных |
| 6. Расхождения | 5 findings, все LOW/INFO, ни один не блокирующий (§3) |

Механический факт по данным: **критерий `E1-PROTO-R1` §9 на confirmatory set (S001 + C001–C003) ВЫПОЛНЕН** — T1 = PASS и все 3 T2-реплики IN_BAND, целостность §5.2 OK. Это подтверждает recommendation имплементера `SUPPORTED` как основанное именно на данных; объявление статуса E1/acceptance — Director (после VERIFIER), merge — Human Gate.

## 2. Метод и доказательства (собственные проверки рецензента)

### 2.1 Scope (проверка 1)

- `git diff --name-status 0176098..6cc7fde`: 51 файл, все внутри allowed_paths WO (`docs/work/WO-NL2-002.md`, `docs/work/executions/EX-NL2-002-R1/**`, `experiments/evidence/E1/E1-R2/**`, `docs/evidence/NL2-002/**`, `docs/work/SESSION_LOG.md`).
- `docs/work/SESSION_LOG.md` — единственный hunk, только добавление в конец (append, статусы не менялись).
- Blob-идентичность base vs subject для запрещённых поверхностей: `project/state.json`, `project/plan.json`, `PREREGISTRATION_E1_R1.md`, `PREREGISTRATION_E1_R2.md`, `ENGINE_ENVIRONMENT_R1.md`, `docs/experiments/E1_REFERENCE_REPRODUCTION.md` — все same=True; `scripts/harness/**`, `config/**`, `E1-R1/**`, `docs/evidence/NL1-002/**`, `docs/evidence/NL2-001/**`, `E0/**` в диффе отсутствуют.

### 2.2 Freeze-дисциплина (проверка 2)

Git-хронология (committer dates): START `878e1ab` 21:18:51+10 → **FREEZE `f34e62c` 21:21:21+10** (campaign.md + protocol.json + analyze_energy.sh, ровно 3 файла) → **CAMPAIGN-START `42cb851` 21:23:45+10** (только manifests + started-events C001–C003) → END_EXECUTION `63cd92d` 21:34:59 → END_ANALYSIS `bd98147` 21:37:18 → handoff `6cc7fde` 21:41:52.

- Frozen-файлы не менялись после freeze: `git diff f34e62c..6cc7fde` на campaign.md/protocol.json/analyze_energy.sh — пусто; следовательно `R_confirm = 3` и полоса были зафиксированы в subject-коммите `f34e62ca` ДО прогонов.
- Артефакты прогонов не менялись после END_EXECUTION: `git diff 63cd92d..6cc7fde` на `runs/*/artifacts/*` — пусто; END_ANALYSIS-коммит только добавляет analysis-поверхности (8 новых файлов, 0 модификаций).
- `manifest.json` и `events/0001-started.json` не менялись после campaign-START — pre-run иммутабельность соблюдена (в отличие от E1-R1, потребовавшего repair-события).
- Distinct seeds — извлечены рецензентом из `log.dat` каждого прогона (`seeding the RNG with …`): C001 −1641386734, C002 977680137, C003 −999572227, S001 −200619630, P001 −473348953, P002 −547126645, P003 −1610133928 — **7 значений попарно различны**; совпадают с опубликованными во всех поверхностях.
- Пререгистрация не менялась (см. §2.1); повторное использование пилотов P001–P003 как T2 отсутствует (confirmatory set = S001 + C001–C003).
- Пуш-время самой ранней публикации из локального Git не восстанавливается; связка «commit до прогона» подтверждается тем, что события завершения прогонов (11:29:05Z) минус wall ~11 с дают старт движка ≈11:28:54Z — после campaign-START-коммита (11:23:45Z).

### 2.3 Воспроизведение статистики (проверка 3)

`analyze_energy.sh` verified: SHA-256 blob'а `747c5216…`, git blob `77cfcc63…`, байт-в-бит идентичен E1-R1 (проверено хэшем обоих файлов, извлечённых из Git). Рецензент запустил инструмент (WSL2 bash) на байт-точных blob'ах `energy.dat` (извлечение `git cat-file blob`, бинарно-безопасное):

| Run | rows | avg col2 (воспроизведено) | Заявлено | Δ от оракула | Полоса |
|---|---:|---|---|---:|---|
| E1-R2-C001 | 1001 | −1.36722173127 | −1.36722173127 | +0.01248083017 | IN_BAND |
| E1-R2-C002 | 1001 | −1.35818087512 | −1.35818087512 | +0.02152168632 | IN_BAND |
| E1-R2-C003 | 1001 | −1.35653082817 | −1.35653082817 | +0.02317173327 | IN_BAND |
| E1-R1-S001 (кросс-чек T1) | 1001 | −1.39393635864 | −1.39393635864 | −0.01423379720 | IN_BAND |

Независимый Decimal-пересчёт средних напрямую из колонки 2 сырых байтов (без awk) даёт те же значения до 11 знаков. Агрегат (Decimal, n−1):

- mean = **−1.36896744830** (заявлено −1.36896744830 — MATCH), SD (n−1) = **0.01729656703** (MATCH), размах = **0.03740553047** (MATCH), SD/полоса = 0.1153 (11.5%).
- Пилотный SD пересчитан: 0.00832919790 — совпадает с `E1-PROTO-R2` §1.
- Целостность §5.2 подтверждена на blob'ах: 1001 строка (1 initial + 1000 prints) ×4, trajectory 10 конфигураций ×3, NaN/Inf = 0 (grep по всем energy.dat).
- **Критерий §9 формально**: T1: S001 IN_BAND (воспроизведено; provenance: SHA-256 `ff26bad5…` из artifacts.manifest E1-R1 совпадает с published blob — проверено рецензентом) **И** C001, C002, C003 ∈ IN_BAND (воспроизведено) **И** целостность OK ⇒ условие Reproduction §9 выполнено механически. Исключений нет, повторов нет (в E1-R2 нет superseded-манифестов, repair-событий и дополнительных run-каталогов).

### 2.4 Протокольная чистота (проверка 4)

- **Verbatim quick_input (§3 R1)**: прямая сверка входного файла с прогоном из Git невозможна (файлы upstream не вендорятся — DOWNLOAD_ON_SETUP), поэтому проверены машинные фингерпринты §3-конфигурации в опубликованных логах/выводах: `T = 20C → 0.097717`; «Simulation type not specified, using MD» (default backend); «Using randomly distributed velocities» ↔ `refresh_vel = 1`; первая строка energy.dat `t = 0.0000` ↔ `restart_step_counter = 1`; 1001 строка ↔ `steps=1e6`/`print_energy_every=1e3`; 10 конфигураций ↔ `print_conf_interval=1e5`; Total Running Time 9.93 s ↔ 1e6 steps; N=16, molecules=2. Все фингерпринты согласованы с verbatim §3; заявленные SHA-256 входов в манифестах совпадают с пинами `E1-PROTO-R1` §2.2 (сверено).
- **Run ID**: E1-R2-C001..C003 — новые, ни один не переиспользовался; в кампании нет failed/aborted/blocked прогонов; терминальное событие (`RUN_COMPLETED`) предшествует `ANALYSIS_COMPLETED` во всех трёх run; scientific_outcome отделён от технического исхода.
- **Контрактные манифесты**: artifacts.manifest — массивы с name/sha256/size_bytes/producer_run_id/subject_sha (40-hex)/storage_location/producer_command; все subject_sha = `f34e62ca…` (40-hex). `experiment_cli validate` (запущено рецензентом): 3/3 `ok=true`, 0 errors, 0 warnings; `work_cli validate EX-NL2-002-R1` → ok=true, HANDOFF_READY, без пост-терминальных коррекций; `cli check-consistency` → ok=true (state/plan не тронуты).
- **jsonschema Draft 2020-12 + FormatChecker (запущено рецензентом по config/control/harness/*.schema.v1.json)**: события эксперимента 9/9 OK, run-манифесты 3/3, artifacts-манифесты 3/3, work-события 4/4, passport 1/1 — итого все schema-головные поверхности PASS (заявление имплементера «jsonschema 15/15» точно и относится ровно к этим 15 файлам; см. F-4 о campaign evidence-map).
- **Digest-vs-blob**: все 15 записей манифестов проверены против сырых blob'ов (`git cat-file blob` + sha256sum) — **15/15 MATCH** по хэшу и размеру; плюс provenance S001 energy.dat `ff26bad5…` MATCH.

### 2.5 Честность интерпретации (проверка 5)

- **SD 11.5% vs пилот 5.6%**: отражено честно и заметно — statistics.md §2, evidence-map `remaining_risks` («SD confirmatory set вдвое выше пилотного… подтверждает, что 5.6%-оценка пилота была оптимистичной»), IMPLEMENTER_EVIDENCE §Оставшиеся риски. Согласуется с малой выборкой (n=4 vs n=3), не скрывается.
- **Диагностика §4 (ac/τ_int/Neff)**: опубликована как best-effort, НЕ gate (`statistics.md` §4, protocol.json, evidence-map); в критерий §9 не входит; рецензент подтвердил независимым пересчётом, что числа не вымышлены (ac(1) диапазон совпал точно; см. F-2 о краях диапазона τ_int/Neff) и не использовались для подгонки — полоса/оракул/критерий взяты из upstream и frozen.
- **NOT_EVALUATED**: выставлен во всех научных поверхностях пакета (campaign.md, statistics.md §5, evidence-map `claim`, analysis-события, IMPLEMENTER_EVIDENCE); ACCEPTED нигде не выставлен (упоминания «ACCEPTED» — только ссылки на статусы NL1-001/NL2-001 и явное «ACCEPTED не выставляется»).
- **SUPPORTED — не «вынужденный PASS»**: критерий §9 frozen до данных (в base-коммите и в freeze-коммите ДО прогонов); полоса — upstream `quick_compare`; seed случайны; все значения опубликованы, включая наименее благоприятную реплику C003 (|Δ|=0.0232, всё ещё в ~6.5 раза внутри полосы); повторов «до успеха» и пост-хок исключений нет (проверено по Git); recommendation явно подчиняет acceptance процедуре REVIEWER → VERIFIER → Director. Альтернативная гипотеза «подгонка под PASS» по данным Git не подтверждается.

## 3. Findings

| # | Severity | Суть | Влияние |
|---|---|---|---|
| F-1 | LOW | Пакетные timestamps событий: все три `0001-started` содержат одинаковый `timestamp_utc` 11:22:30Z (раньше campaign-START-коммита 11:23:45Z), все три `0002-run-completed` — одинаковый 11:29:05Z. Timestamp отражает время авторизации пакета событий, а не момент наступления каждого события | Не влияет ни на один frozen-критерий; freeze-before-run подтверждается Git-хронологией независимо (см. §2.2). VERIFIER/Director не должны использовать эти timestamps для восстановления по-процессной хронологии прогонов |
| F-2 | LOW | Опубликованные приблизительные диапазоны диагностики τ_int ≈ 10–60 prints и Neff ≈ 8–48 слегка занижают худший случай: независимый пересчёт рецензента (Geyer-IPS/naive-estimator по колонке 2 published blob'ов) даёт для C003 τ_int ≈ 68, Neff ≈ 7.3; ac(1) диапазон 0.59–0.83 воспроизводится точно | Диагностика явно НЕ gate (§4 R2) и на критерий §9 не влияет. Но VERIFIER/Director не должны читать «Neff ≥ 8» как гарантию: Neff для C003 может быть ниже 8 при стандартных эстиматорах |
| F-3 | INFO | Ловушка Windows-верификации: дайджесты artifacts.manifest относятся к LF-blob'ам; рабочая копия при `core.autocrlf=true` (CRLF, напр. energy.dat 50050 B вместо 49049 B) хэши НЕ совпадут. У самого имплементера метод указан верно («binary-safe git cat-file»); у рецензента первая попытка через `git archive` на Windows-пути воспроизвела эту ловушку | Рекомендация (вне этого WO): задокументировать в VERIFIER-инструкциях требование бинарно-безопасного извлечения blob'ов |
| F-4 | INFO | Campaign-level `evidence-map.json` не покрыт v1-схемой: `evidence-map.schema.v1.json` описывает work-order-уровень (checkpoint/claim_class/review_verdict/…), и принятый evidence-map E1-R1 не проходит её идентичным образом — это установленный формат экспериментных campaign-карт, а не дефект NL2-002 | Рекомендация (вне этого WO): отдельная schema для экспериментных campaign evidence-map в будущей harness-работе |
| F-5 | INFO | Эпистемическая граница Git-only review: runtime-акты «SHA-256/флаги/CMakeCache бинаря верифицированы перед кампанией» и «4/4 on-place SHA MATCH входов перед каждым прогоном» принципиально не пере-наблюдаемы из Git; косвенная поддержка — машинные фингерпринты лога (§2.4) и полное совпадение всех численных результатов при воспроизведении | Принять как документированное ограничение уровня доказательства; для E1 достаточно (данные и так воспроизведены рецензентом из published blob'ов) |

Блокирующих findings нет; path `FIX_REQUIRED`/`FAIL` не требуется.

## 4. Утверждение и claim ceiling

- Подтверждается execution-факт: критерий `E1-PROTO-R1` §9 на confirmatory set ВЫПОЛНЕН (воспроизведён рецензентом).
- Подтверждается право имплементера публиковать recommendation `SUPPORTED` для Director с campaign-level `scientific_outcome = NOT_EVALUATED`.
- Claim ceiling: `C1_COMPUTATIONAL_REPRODUCTION`. Воспроизведён upstream-оракул на одной зафиксированной машине/сборке с distinct seeds; физическая валидность oxDNA, сборка, кинетика, переносимость — вне scope (S02).
- E1 acceptance и объявление статуса E1 — **Director** (после независимого VERIFIER); merge — Human Gate.

## 5. Ограничения данного review

Review выполнен по Git-фактам subject-коммита и собственным воспроизведениям (WSL2 bash/awk для analyze_energy.sh; Python/Decimal для статистики; jsonschema Draft 2020-12). Машино-локальные акты исполнения (§F-5) не пере-наблюдаемы. Push-время campaign-START из локального Git не восстанавливается (см. §2.2 — непротиворечиво с post-commit стартом прогонов).

## 6. Next action

Независимый VERIFIER: подтвердить воспроизведение (включая бинарно-безопасную сверку дайджестов, F-3) и передать пакет в Director checkpoint для объявления статуса E1.
