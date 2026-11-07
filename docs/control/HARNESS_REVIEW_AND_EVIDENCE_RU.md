# NanoLab — Evidence-Driven Review

**Revision:** `FLOW-THROUGHPUT-R1`

## Единицы review

```text
COMMITS = recovery units
WORK ORDERS = execution units
EXPERIMENT RUNS = scientific execution units
EVIDENCE MAPS = review units
EXCEPTIONS = human attention units
```

## Роли

`IMPLEMENTER` пишет код/протокол; `SCIENTIFIC_OPERATOR` запускает frozen protocol; `REVIEWER` ищет ошибки design/метода/статистики; `VERIFIER` проверяет exact subject, команды, hashes и manifests; `DIRECTOR` маршрутизирует checkpoint; `HUMAN` решает gates.

Reviewer verdict: `PASS | FAIL | INSUFFICIENT_EVIDENCE`. Scientific conclusion хранится отдельно: `SUPPORTED | NOT_SUPPORTED | INCONCLUSIVE | NOT_EVALUATED | INVALIDATED`.

## Risk routing

```text
LOW      administrative-only → Implementer + automated CI (existing Human merge gate)
MEDIUM   ordinary tooling → Implementer + independent Reviewer (includes mechanical verification) + CI
HIGH     protocol/observable/analysis/topology/inputs/claim/authority/security → separate Reviewer + Verifier + Director
CRITICAL physical lab/hardware, hazardous, bio/medical, foundation, major budget → + Human
```

## Claim ladder

```text
C0 SOFTWARE_ONLY
C1 COMPUTATIONAL_REPRODUCTION
C2 COMPUTATIONAL_PREDICTION
C3 CROSS_MODEL_OR_EXTERNAL_CORRELATION
C4 PHYSICAL_EXPERIMENTAL_VALIDATION
C5 REPLICATED_PHYSICAL_VALIDATION
```

Симуляция автоматически не повышается до C4.

## Evidence Map

MEDIUM+ и scientific claims фиксируют: intent, Work Order, risk/claim, exact HEAD/TREE, changed surfaces, protocol/model revisions, inputs/digests, experiment runs, commands/exit codes, artifacts/SHA-256, observables/statistics, negative controls, failed/inconclusive runs, validation/regression, remaining risks, required fixes, review verdict, scientific conclusion и claim ceiling.

## Exact-head freshness

Для claim-affecting code reviewed HEAD должен совпадать с analyzed/frozen subject. Изменение analysis/physics code делает affected evidence stale.

## Статистика

Запрещено менять threshold после просмотра результата без новой protocol revision, исключать runs без заранее объявленного правила, путать replicas с повторным анализом одной траектории, скрывать failed/inconclusive outcomes и выдавать model confidence за physical validation.

## Provenance

Повторно используемый artifact обязан иметь `sha256`, `size`, producer run, exact subject, producer tool/command и storage location. Если raw data вне Git — manifest в Git обязателен.

## Проверка исправлений и публикаций

Применять [FLOW-THROUGHPUT-R1](FLOW_THROUGHPUT_R1.md). Тот же независимый Reviewer/Verifier может проверить чужой repair. При доказанном неизменном product/input subject новый publication SHA требует delta review, не автоматического повторного полного цикла. Новый reviewer нужен при конфликте независимости, а не просто новом коммите. C0 и Markdown сами по себе не понижают риск. `review_impact` выдаёт сравнение, а не approval.
