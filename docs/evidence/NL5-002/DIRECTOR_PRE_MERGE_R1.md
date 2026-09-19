# DIRECTOR_PRE_MERGE_R1 — NL5-002 integration candidate (MISMATCH terminal)

Дата: 2026-09-19 (authoritative `date -u` при публикации). Роль: DIRECTOR.

## Что это за merge

Integration candidate `integration/nl5-002-r1` публикует durable evidence цепочки
NL5-002 «Obtain external reproduction» (mission §17). Merge СОДЕРЖИТ только
execution surfaces; canonical state (`project/state.json`: `NL5-002 = READY`,
`external_reproductions = 0`, frontier `NL5`) этим merge НЕ меняется.

## Состав (все от base 48c55b3c4acdd2264527083e3072757be8bd9ada)

| поверхность | HEAD | содержимое |
|---|---|---|
| work/nl5-002-a-protocol-freeze-r1 | a41c4502 | frozen protocol WO-NL5-002-A-R1 + Appendices + EX-NL5-002-A-R1 |
| work/nl5-002-b-external-run-r1 | 10b4deb8 | B-R1: честный terminal INCONCLUSIVE + PORTABILITY_FINDING |
| work/nl5-002-c-compare-repair-r1 | a1ba5173 | bounded repair: releases/nanolab-components-v0.1.1 (научные числа byte-identical v0.1.0) + WO/EX-NL5-002-C-R1 |
| work/nl5-002-b-r2-external-run-r1 | a8dfe8c | B-R2: dispatch/recovery/terminal + ingested evidence (отчёт, analysis, digests) |
| work/nl5-002-c2-compare-r2-r1 | b0aff56 | C2: механическое сравнение, binding WO-level **MISMATCH** |
| review/nl5-002-r1 | be945f1 | FRESH_REVIEW_R1: **PASS** (независимый пересчёт из per-frame 4/4) |
| verify/nl5-002-r1 | 4116468 | FRESH_VERIFY_R1: **PASS** (воспроизведение из raw 0.00e+00; 84/84 digests; NC-1/NC-2/NC-3) |

## Gates (mission §18)

```text
Reviewer PASS            = да (review/nl5-002-r1 @ be945f1)
Verifier PASS            = да (verify/nl5-002-r1 @ 4116468)
REVIEWED_HEAD == VERIFIED_HEAD == live HEAD = да, 5/5 (drift NONE)
exact-head hosted CI     = см. PR этого HEAD (требуется success до merge)
Director pre-merge PASS  = да (этот документ; condition ниже)
```

## Director pre-merge assessment

- Научный исход зафиксирован честно: WO-level **MISMATCH** (0b, 32b directionally
  separated от frozen envelopes; 11b, 53b MATCH; 74b NOT_MEASURED).
  Threshold tuning отсутствует (envelopes byte-identical v0.1.0→v0.1.1);
  B-R1 и MISMATCH сохранены как negative/positive научные факты.
- Merge публикует evidence (включая negative results) — это не повышает claims и
  не меняет canonical state. Claim ceiling всей цепочки: C1_COMPUTATIONAL_REPRODUCTION.
- **NL5 acceptance НЕ объявляется**: критерий NL5 («release package воспроизведён
  вне авторской среды» по frozen rule) данной кампанией не выполнен. State
  transition (mission §21) не применяется.
- Disposition (mission §12): MISMATCH сохраняется; автоматический R3 не запускается;
  выбор следующего шага (исследовательский WO platform-sensitivity / новая protocol
  revision через Human Gate / optional bounded packaging repair v0.1.2 для
  pyc/RIGHTS-metadata findings) — **Human Gate**.

## Известные findings (не блокируют merge)

FR-1..FR-6 (review, LOW/INFO) и F-orch1/F1–F4 — packaging/документация/процесс;
научные поверхности и классификацию не затрагивают. Полные списки — в
FRESH_REVIEW_R1.md / FRESH_VERIFY_R1.md / C2 summary.md.
