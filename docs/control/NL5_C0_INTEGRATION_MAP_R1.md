# NL5_C0_INTEGRATION_MAP_R1 — согласованная интеграция верифицированных C0-веток

Director record (2026-10-26T03:18:12Z). Программа NL5-CLOSE-R1 (#81). **Слияние в main остаётся
Human Gate** — эта карта только предлагает согласованный порядок и ожидания.

## Верифицированные subjects (exact, пины держатся на 2026-10-25)

| # | Ветка | HEAD | Верификация |
|---|---|---|---|
| 1 | work/nl5-f01-frozen-audit-r1 | c7c5be6edbcdb5a304705ff6d53863fa735d7d0c | Director-приёмка (документальная; RV по Issue #82 не требуется — без кода/контрактов) |
| 2 | work/nl5-f02-u1-host-r1 | 9b24f93 (c38ad68 + Director addendum U1-spec) | REVIEW PASS + VERIFIED (на c38ad68; addendum — Director control commit) |
| 3 | work/nl5-f03-u2-readiness-r1 | 1831585fa70169c4e473acfe38e9603e45cfe22c | REVIEW PASS + VERIFIED (включая addendum 0004) |
| 4 | work/nl5-f05-dispatch-prep-r1 | 4c9d8fd30300a2f48504d1b914693f0a66bb3555 | REVIEW PASS + VERIFIED |
| 5 | review/nl5-c0-batch-f02-f03-f05-r1 | 906d55dffebb606570bb6ff6b3cd17778d314202 | REVIEWER PASS evidence |
| 6 | verify/nl5-c0-batch-f02-f03-f05-r1 | 9be1964b7860853931fa69d70c8f42a7f053b536 | VERIFIER VERIFIED evidence |

## Предлагаемый порядок merge (каждый шаг = отдельное решение HG владельца)

1. F01 → 2. F02 → 3. F03 → 4. F05 → 5. review → 6. verify.

## Ожидаемые конфликты и их разрешение

- **docs/work/WORK_QUEUE.md**: 6 append-записей (по одной на ветку, у F03 — плюс
  blank-separator). Разрешение: механическая конкатенация в порядке merge, 0
  deletions существующих строк; любые правки — только как новые строки.
- Прочие пути не пересекаются (каждая ветка трогает только свой execution dir +
  свой WO-файл; dispatch-записи Director'а в каждой ветке уникальны).

## Правила

- Merge выполняет владелец (или явно делегированный protected writer) — не
  Director самовольно.
- Если последующие контракты (authority A WO после F04, U2_INFRA_OPERATOR WO)
  ссылаются на evidence по exact-веткам/tips, интеграция НЕ обязательна до их
  старта: ссылки по exact HEAD валидны и без merge.
- Любой новый коммит на subjects после этого документа НЕ инвалидирует карту,
  но требует обновления пинов до merge.

## Вне scope

- Слияние FROZEN_R2-путей не требуется (frozen-файлы уже в main, интегральны).
- Canonical state (project/*.json) в этих ветках не менялся — обновление
  канонических статусов НЕ входит в интеграцию C0.
