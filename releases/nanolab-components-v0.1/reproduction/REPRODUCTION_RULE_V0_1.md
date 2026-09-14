# NanoLab — Independent Reproduction Rule v0.1

Статус: **FROZEN BEFORE NL5-001-C DATA**. Создан в `WO-NL5-001-B-REPAIR-R1` после Fresh Reviewer `FIX_REQUIRED` и до любых clean-room/external reproduction результатов.

## Назначение

Правило классифицирует независимый повтор измеренной карточки DNA hinge. Оно **не** использует bootstrap CI95 исходной pooled median как prediction/tolerance interval: этот CI описывает неопределённость исходной pooled-оценки, а не диапазон будущей независимой кампании.

## Независимая единица

Независимая единица сравнения — **replica**, а не отдельный trajectory frame. Для каждого варианта исходная кампания содержит три независимых replica medians. Новая reproduction campaign также требует три fresh replicas, если отдельный Work Order заранее не объявил иной дизайн.

Для каждой кампании:

1. применяются те же frozen frame-validity gates и observable convention;
2. для каждой реплики считается median по валидным кадрам в том же measurement window;
3. campaign statistic = median трёх `per_replica_median_deg`;
4. исходный empirical reference envelope = `[min(reference replica medians), max(reference replica medians)]`.

Envelope является **описательной pre-existing межрепличной областью**, а не 95% confidence/prediction interval и не физической equivalence margin.

## Outcome

При `required_replicas = 3`:

- `MATCH`: technical execution завершён, frozen integrity/analysis применены, есть ровно/не менее трёх валидных fresh replica medians, а campaign statistic новой кампании находится внутри включительного reference envelope.
- `MISMATCH`: все fresh replica medians находятся строго по одну сторону reference envelope (все ниже `ref_min` либо все выше `ref_max`). Это operational reproduction mismatch, не автоматический физический `NOT_SUPPORTED` за пределами claim ceiling.
- `INCONCLUSIVE`: достаточных валидных fresh replicas нет, integrity/analysis не завершены, либо campaign statistic вне envelope, но нет согласованного полного directional separation.
- технический сбой (`FAILED_TECHNICAL`, digest mismatch, engine failure, budget abort) фиксируется отдельно и не превращается в scientific mismatch.

Это консервативное правило специально оставляет промежуточную область `INCONCLUSIVE`, потому что исходный reference имеет только три независимые реплики.

## Обязательные условия

- Никакого threshold tuning после просмотра NL5-001-C/NL5-002 результатов.
- Fresh seeds для независимого reproduction выбираются/замораживаются Work Order до запуска и не совпадают с reference seeds.
- Тот же variant, engine/model/protocol revision, observable convention, common window и frame-validity gates.
- Параметры comparison извлекаются из опубликованного evidence; значения bootstrap CI могут репортиться, но не используются как independent-reproduction tolerance.
- `74b` не классифицируется этим правилом, пока остаётся `NOT_MEASURED`.

## Machine implementation

`scripts/release/reproduction_rule.py`, rule id `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`.

Карточка должна публиковать reference replica medians/envelope и ссылаться на этот rule id. Старое правило «pooled median внутри bootstrap CI95» superseded и не применяется к NL5-001-C/NL5-002.
