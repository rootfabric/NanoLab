# EX-NL5-002-A-R1 — Summary: freeze external reproduction protocol

- Work Order: `WO-NL5-002-A-R1` (parent `NL5-002`)
- Base: `main @ 48c55b3c4acdd2264527083e3072757be8bd9ada`
- Branch: `work/nl5-002-a-protocol-freeze-r1`
- Risk: MEDIUM; claim ceiling `C1_COMPUTATIONAL_REPRODUCTION`
- Status: HANDOFF_READY

## Что заморожено (до любого запуска)

| Блок | Содержание |
|---|---|
| Subject | `nanolab-components 0.1.0` @ `main 48c55b3`; sha256 пины манифеста, прав, правила, карточек (20/20 файлов) |
| Executor | fresh external session; вход = package copy + Appendix A только; внутренние материалы NanoLab / команды NL5-001-C запрещены; OS/runtime записывается |
| Seeds | 3 fresh seeds/вариант до запусков; != reference {201004, 202008, 203012} |
| Design | 12 runs (0b/11b 200k; 32b/53b 150k), upstream verbatim кроме seed, окно t<=150000, median-of-3 |
| Budget | kill 20 h/replica → FAILED_TECHNICAL; wall 48 h; no paid, no GPU |
| Classification | per-card NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE; WO-level: REPRODUCED / REPRODUCED_WITH_DEVIATION / INCONCLUSIVE / FAILED_TECHNICAL / MISMATCH (mapping в WO) |
| Repair rule | portability gap → Phase C bounded repair → package revision при необходимости → свежий внешний повтор; tolerance/envelope не меняются |
| Report | EXTERNAL_REPRO_REPORT_TEMPLATE_R1 (13 секций) |

## Validation

- Appendix A self-containedness: grep по внутренним ссылкам — 0 совпадений.
- Пины вычислены из canonical `main @ 48c55b3` (sha256sum, см. event 0002).

## Exact HEAD/TREE

- Deliverables commit: `2108ea795588c1a5f3492d3a6f4788e695a32834`
- Deliverables tree: `a83a6d5aa04b9f43fcd48bf56cadf9a584fc390b`
- Bookkeeping-записи (эта правка, evidence-map head_sha) идут отдельным commit
  поверх и содержимого deliverables не меняют.

## Open risks (предсказаны до данных; executor'у не передаются)

- R1: analysis-конвенция ссылается на internal docs, отсутствующие в пакете →
  возможный честный исход `INCONCLUSIVE + portability finding`.
- R2: у пакета нет корневого README.
- R3: кампания ~15 h wall (калибровка NL5-001-C).

## Next action (один)

Dispatch фазы B: staging вне репозитория (package copy + protocol + template,
sha256-сверка) → fresh external executor → отчёт; ingest на
`work/nl5-002-b-external-run-r1`.
