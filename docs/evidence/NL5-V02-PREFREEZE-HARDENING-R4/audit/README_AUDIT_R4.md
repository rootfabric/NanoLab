# NanoLab — focused pre-freeze audit R4 (2026-10-03)

## Scope

Это targeted module-level audit exact subject PR #48, а не полный fresh Verifier и не scientific execution. Полный repository test suite локально не воспроизводился; hosted CI проверен как отдельный GitHub fact. Научные симуляции: **0**.

```text
canonical main = 87298b36431045474d3784adf5cee8c9a64d0fc9
main tree      = db19f9dd265873f99c995aa279ae5e0c5b21c330
main CI        = 36839661671 SUCCESS
PR #48         = OPEN / DRAFT
PR head        = ce13f0e9cb9536aaffddfff0a05c9a73f0870a21
PR base        = 8205781def7179d6bdfa6eb7ab2a84d46776649c
PR CI          = 36804852475 SUCCESS
compare        = 11 ahead / 9 behind / diverged
```

## Exact audited blobs

```text
scripts/nl5/repro_v02_freeze_gate.py
  GIT_BLOB_SHA1 = 3875167709de7db89ebb0ad4c33d5722a85621aa
scripts/nl5/repro_v02_seeds.py
  GIT_BLOB_SHA1 = 81c1401c5d151202d6853cc46cdd81be0baff66a
R3 seed record
  GIT_BLOB_SHA1 = 0a8cd6ad5a6c0ccf1c70bceb4223c43339529a37
  logical record_sha256 = eb4ab3f891e17dd2b456a3870ed73b19e39d67bf51109b6cb47ca64524ce476b
```

Копии exact audited modules и R3 record лежат рядом в `source/`/audit evidence. Они не являются новой product implementation: это pinned evidence для воспроизведения старого поведения.

## Reproduced findings

**F1 — incomplete freeze contract.** Старый `freeze_consistency_gate()` возвращает `PASS` для повреждённых control seed arrays, duplicate/historical seed, stale `record_sha256`, missing bootstrap seeds и части противоречащих protocol fields при сохранённой первой cardinality-строке.

**F2 — collision scan fail-open.** `literal_tree_collision_scan()` не различает `git grep` exit 128 и настоящий no-match и сканирует изменяемый worktree вместо explicitly pinned immutable tree.

**F3 — replacement cursor ambiguity.** Текстовое правило `N+1` после deterministic skips повторно выбирает уже использованный confirmatory seed у всех четырёх вариантов R3.

**F4 — integer policy drift.** `51/64 = 79.6875%`; `60/296 = 20.27027%`. До freeze нужна одна явно определённая per-cell/paired rounding policy. Это pre-data protocol question, а не повод молча менять science criteria.

Machine-readable observations: `../audit_results_2026-10-03.json`.

## Reproduce old defect

Из этой папки:

```bash
python3 reproduce_findings.py
```

Скрипт делает только локальные deterministic checks и synthetic temporary Git fixture; сеть/oxDNA/remote writes не используются. Он предназначен для доказательства **старого дефекта до repair**. Зелёный exit этого скрипта не является acceptance R4. После ремонта новые regression tests должны ожидать rejection повреждённых inputs.

## Integrity / transport

Standalone mission source SHA-256: `7b8b4e4944d0ab380fac3831e9af833d02b55d869d8a86fa0e80f39e15f6db33`.

Standalone audit JSON source SHA-256: `58c36763f068eec398837e3802d10b42c10300c4fb9061c688e79a02fd233fd5`.

Original transport ZIP SHA-256: `fd32073510ee4878bc1c6b83f7817806616ef924e4729a21eef252e795fca429`. ZIP — только упаковка; в Git сохраняются его содержательные текстовые артефакты раздельно, чтобы они были reviewable/diffable.

## Status ceiling

```text
R3 historical review/verify = preserved
new audit readiness         = FIX_REQUIRED
candidate                  = PRE-DATA / NOT FROZEN
new scientific runs         = 0
NL5                         = IN_PROGRESS
external_reproductions      = 0
NL6-001                     = LOCKED
```
