# WO-NL5-002-E-R1 — Platform sensitivity study R1 (PLATFORM-SENSITIVITY-R1)

## Статус

**FREEZE-IN-PROGRESS — preregistration content frozen as of this commit; review/verify pending.**
Owner-разрешение получено (2026-09-20): `HUMAN_GATE_PLATFORM_SENSITIVITY_PREPARATION = APPROVED`
(подготовить и после корректного preregistration freeze запустить bounded experiment).
До (1) fresh Scientific Reviewer PASS preregistration, (2) fresh Verifier PASS
preregistration и (3) Director freeze record `docs/evidence/NL5-002-E/PREREGISTRATION_FREEZE_R1.md`
ни один прогон этого WO не выполняется. Научное содержимое (вопрос, гипотезы, seeds,
статистический план, decision rule, budgets, stop conditions) после этого коммита
не меняется (freeze-before-data; любые правки = новая revision WO).

- Parent: `NL5-002` (frontier `NL5`; `NL5-002` = terminal MISMATCH, WAITING_HUMAN)
- Риск: **HIGH** (protocol/observable/analysis/claim) → требуется Reviewer + Verifier + Director
- Claim ceiling: `C1_COMPUTATIONAL_REPRODUCTION` (изучение чувствительности не поднимает claims карточек)
- Основание: verified terminal MISMATCH NL5-002-B-R2 (0b и 32b directional separation
  от frozen envelopes; 11b/53b MATCH) — `docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md`

## Научный вопрос (один)

> Почему 0b и 32b дают систематически смещённые распределения median-угла на внешней
> платформе при идентичном frozen protocol (nanolab-components 0.1.1, frozen
> `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`), и насколько велика эта platform-зависимость
> относительно intrinsic seed-вариабельности?

Это **исследовательский** WO: он не пытается «дожать» R1 до MATCH и не пересматривает
R1. Старый MISMATCH остаётся навсегда валидным результатом R1.

## Гипотезы (preregistered)

```text
H0: platform shift (медианная paired разность между платформами) мал относительно
    intrinsic seed variability внутри платформы.
H1: platform/compiler/runtime даёт systematic shift, сравнимый или больше seed
    variability (согласованный по знаку между 0b и 32b направлениями, наблюдёнными в R1).
```

Причина MISMATCH заранее НЕ заявляется. Кандидаты-механизмы (floating-point chaos,
compiler/codegen различия, BLAS/libm, окружение) — предмет интерпретации ПОСЛЕ данных,
не часть вердикта.

## Platforms

```text
P1 = author/reference environment (WSL2 Ubuntu 24.04.2, gcc 13.3.0; ENGINE_ENVIRONMENT_R1)
P2 = external environment (Ubuntu 22.04, gcc 11.4, Xeon E5-2698 v3 — платформа B-R2)
P3 = optional третья независимая Linux/compiler/runtime среда (если доступна;
     включается отдельным CONTINUATION до данных этой платформы)
```

Environment fingerprint каждой платформы фиксируется до прогонов (ОС, compiler,
версии runtime, CPU, настройки FPU если доступны).

## Variants

```text
Primary: 0b, 32b (оба показали directional separation в R1)
Controls: 11b, 53b — опционально, analysis-only, на классификацию WO-level НЕ влияют
74b — ЗАПРЕЩЁН (NOT_MEASURED / KNOWN_GAP, arm-manifest-v2 — отдельный будущий WO)
```

## Реплики и seeds (frozen в этом документе до данных)

- Minimum: **n = 8 fresh seeds / variant / platform**; целевой бюджет: **n = 10**.
- Один и тот же seed list используется на всех платформах → paired comparison.
- Seed list (int32, distinct, не равны reference 201004/202008/203012 и seed'ам B-R1/B-R2;
  сгенерирован и заморожен 2026-09-20 до любых прогонов):

```text
S001 = 1259289227
S002 = 1358106528
S003 = 1524307444
S004 = 601855227
S005 = 274288237
S006 = 972234272
S007 = 1934775205
S008 = 1747973984
S009 = 880427736
S010 = 744386736
```

- Fresh seeds обязательны: переиспользование run ID и seed'ов предыдущих кампаний
  для новых прогонов запрещено; failed run ID не переиспользуются.

## Измерения (для каждой platform × variant)

```text
per replica: median angle (packaged convention analyze_hinge.py — та же конвенция,
             что R1; никакой другой observable не подменяет её),
             integrity metrics (frame gates, trajectory completeness, exit code),
             energy drift, runtime
per cell (platform × variant): distribution median, IQR, q05, q95, mean, SD(n−1)
```

Главный вопрос — НЕ «MATCH старому envelope?» (этот вопрос закрыт R1), а «насколько
распределение зависит от platform?».

## Frozen статистический план (выбран ДО данных)

1. Primary (paired, seeds общие): для variant v ∈ {0b, 32b}
   `shift_v = median_i( median[P2, seed_i] − median[P1, seed_i] )`;
   bootstrap 95% CI разности (percentile, 10 000 resamples, bootstrap RNG seed
   frozen = 902107); effect size `ratio_v = |shift_v| / within_v`, где
   `within_v = median по платформам (MAD per-seed median внутри платформы)`.
2. Secondary (distributional): per variant — platform median shift, отношение IQR,
   overlap q05/q95, mean/SD; между P1..P3 если P3 включена.
3. Frozen decision rule (per variant):
   - `PLATFORM_SENSITIVE`: bootstrap 95% CI shift_v не содержит 0 **и** `ratio_v ≥ 1`;
   - `PLATFORM_INSENSITIVE`: CI содержит 0 **или** `ratio_v < 0.5`;
   - иначе `INCONCLUSIVE` (variant).
   WO-level: `PLATFORM_SENSITIVE` — если 0b И 32b sensitive; `PLATFORM_INSENSITIVE` —
   если оба insensitive; иначе `INCONCLUSIVE`.
4. Изменение этого плана после просмотра данных запрещено (иначе — новая revision WO).

## Возможные outcomes и их последствия

```text
PLATFORM_INSENSITIVE → смещение R1 требует иного объяснения (replica-level noise,
                       скрытая протокольная разница); отдельный analysis WO.
PLATFORM_SENSITIVE   → основание проектировать НОВУЮ protocol revision v0.2
                       (например distribution-based reproduction rule вместо
                       ultra-narrow n=3 envelope) — отдельный preregistration,
                       validation, versioning.
INCONCLUSIVE         → честно фиксируется; расширение только новым bounded WO.
```

## Жёсткие запреты

```text
НЕ менять NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE и threshold'ы R1;
НЕ переписывать/переклассифицировать R1 (B-R1 INCONCLUSIVE+PORTABILITY_FINDING,
  B-R2 MISMATCH) — история: v0.1 rule → MISMATCH остаётся;
НЕ добавлять replicas до MATCH и не перезапускать R3 автоматически;
НЕ заменять frozen convention analyze_hinge.py другой конвенцией;
НЕ производить значения 74b;
НЕ трактовать exit 0 как научный PASS;
platform study сам по себе НЕ закрывает NL5 и НЕ меняет NL5 acceptance (LOCKED
  до owner-решения; NL6-001 / E5 не стартуют).
```

## Бюджет и stop conditions

- Compute: CPU-only, no paid/GPU; 0b = 200k шагов, 32b = 150k шагов (окна R1);
  ~40 прогонов при n=10 × 2 variants × 2 platforms (P3 опционально +20).
- Wall: калибровка B-кампаний (~10–14 ч/replica single-thread; параллельные прогоны
  в пределах узла) — бюджет wall ≤ 72 ч на платформу.
- Stop: environment недоступна → `BLOCKED_ENVIRONMENT`; систематические technical
  failures ≥ 2 seeds в одной ячейке → честная классификация FAILED_TECHNICAL/INCONCLUSIVE,
  не «подгонка»; превышение бюджета → остановка и checkpoint.

## Выход

`EX-NL5-002-E-R1` (passport + START до прогонов; CONTINUATION по платформам;
END_EXECUTION; END_ANALYSIS с frozen-планом §статистика; REVIEW отдельным Reviewer,
VERIFY exact-head) + comparison report + evidence map. Все сырые trajectories — вне
Git с manifest SHA-256.

## Явные зависимости

- Доступ к P1 (author env) и P2 (external env) — как в B-R2; P3 — только если владелец
  предоставит. INFRA capability не требуется сверх использованных в B-R2.
- Пакет: nanolab-components 0.1.1 (или 0.1.2, если bounded packaging repair будет
  принят владельцем; научные числа пакетов byte-identical, это фиксируется digest'ами).
