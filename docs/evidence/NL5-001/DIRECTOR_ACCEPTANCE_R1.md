# Director Acceptance R1 — NL5-001 «Publish validated component library»

- Дата: 2026-09-18. Authority: владелец (owner decision D2 по лицензиям 2026-09-18 + explicit mission: провести независимые локальные проверки NL5-001-D, закрыть этап и открыть NL5-002; Human Gate для merge PR #42 pre-approved для этой mission).
- Execution units: `EX-NL5-001-A-R1`, `EX-NL5-001-B-R1` (+ `EX-NL5-001-B-REPAIR-R1`), `EX-NL5-001-C-R1`, `EX-NL5-001-D-R1`.
- Risk: MEDIUM (release/rights/metadata; без научной вычислительной claim). Claim ceiling: **C0_SOFTWARE_ONLY** для пакета; научные карточки — measured-only, потолок `C1_COMPUTATIONAL_REPRODUCTION` по schema.

## 1. Цепочка исполнения NL5-001 (все звенья в canonical main)

| Звено | Subject | Независимые проверки | Merge в main |
|---|---|---|---|
| NL5-001-A: release contract R1→R1.2 | `work/nl5-001-a-release-contract-r1` @ `9cbde33` (исторический pre-amendment subject A @ 9cbde33 не принимался отдельно) | Fresh re-review в составе интеграции | `6577f8b` |
| NL5-001-B: library assembly + deterministic R1.2 builder | `work/nl5-001-b-library-assembly-r1` @ `55b0c40` | см. интеграцию | `6577f8b` |
| B Repair R1.2 (frozen reproduction rule, fail-closed manifest, evidence-sourced pins) | `repair/nl5-001-b-library-r1` @ `dc3063b` → clean integration head `a9950dc` | fresh re-review **PASS** `review/nl5-001-b-repair-r1`; exact-head verify **PASS** `verify/nl5-001-b-repair-r1`; hosted CI `35090409941` 5/5 | `6577f8b` (PR #41) |
| NL5-001-C: clean release reproduction | `work/nl5-001-c-clean-reproduction-r1` @ `b056db2` | fresh review **PASS** `review/nl5-001-c-r1` @ `96975d1` (12/12 медиан пересчитаны независимо, max Δ 4.61e-10 deg); exact-head verify **PASS** `verify/nl5-001-c-r1` @ `be61fb0` (negative controls сработали) | `bc9ad8c` |
| NL5-001-D: license finalization (owner D2) + package 0.1.0 | `control/nl5-001-d-license-r1` @ `216c01c` (tree `c9390df`) | fresh review **PASS** `review/nl5-001-d-r1` @ `11f33b7`; fresh exact-head verify **PASS** `verify/nl5-001-d-r1` @ `7609c63`; hosted CI `35336379253` и `35343292500` на exact head SUCCESS 5/5 | `3fb6dc1` (PR #42 MERGED) |

Исторический CI-fail `35336073771` (literal-newline typo в D2 builder) не скрывается: superseded исправленными subjects `50aee77` (CI `35336208105` SUCCESS, 360/360) и финальным `216c01c`.

## 2. Owner decision D2 (закрыт)

- NanoLab code: **Apache-2.0** (`LICENSE`).
- NanoLab documentation + NanoLab-owned derived data/results: **CC-BY-4.0** (`LICENSE-DOCS-DATA.md`).
- Сторонние материалы НЕ перелицензованы: E2 DNA-hinge inputs — REFERENCE_ONLY / download-on-run по pinned commit `23fd1ff7`, durable_cache FORBIDDEN, vendoring отсутствует (проверено verifier'ом, NC-4); oxDNA/GPL — upstream GPL; restricted/UNKNOWN — свои rights modes. Record: `docs/control/NL5_001_D_LICENSE_DECISION_R1.md`; матрица `docs/research/DEPENDENCY_LICENSE_MATRIX.md` синхронизирована.
- Open decision «NanoLab code/documentation/data license choice» закрыт и удалён из `project/state.json`.

## 3. Release package

- Пакет: **`nanolab-components` 0.1.0** (promoted из `0.1.0-rc0` в NL5-001-D).
- Byte-for-byte deterministic rebuild подтверждён: builder output == committed package (все 20 файлов манифеста; RIGHTS/CITATION/VERSION/RELEASE_MANIFEST/cards/protocols/reports/reproduction/provenance/schema).
- `RELEASE_MANIFEST.json` — детерминированный full-package manifest (sha256+size), negative controls на tamper сработали (NC-1, NC-3); draft/publication gate для `UNDECIDED_PENDING_OWNER_DECISION` зафиксирован (NC-2: warning-gate + contract §4 + forced finalization в builder).
- Package lint: ok, errors=[], warnings=[].

## 4. Научные результаты (сохранены, claim не повышен)

Classification по frozen `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE` (NL5-001-C, 3 fresh replicas на вариант; независимая re-check review + verify):

| Variant | Classification | Факт |
|---|---|---|
| 0b | **MATCH** | campaign stat 66.159296437° в reference envelope [65.095434789, 67.236579608] |
| 11b | **INCONCLUSIVE** | stat 75.514562357° вне envelope, но без полной directional separation — промежуточный исход сохранён честно, НЕ повышен до MATCH/PASS |
| 32b | **MATCH** | 78.096569929° в [77.4927314, 79.877463339] |
| 53b | **MATCH** | 132.575590442° в [131.049227687, 135.285186059] |
| 74b | **NOT_MEASURED / KNOWN_GAP** | детерминированный отказ arm-manifest-v1; arm-manifest-v2 — отдельный будущий bounded WO; honest gap опубликован |

Инварианты acceptance: scientific карточки, REPRODUCTION_RULE, evidence/classifications NL5-001-C, thresholds, observables, reference replica medians — не изменялись звеном D (подтверждено review+verify: diff base..HEAD пуст по scientific surfaces). Bootstrap CI — DESCRIPTIVE_ONLY, не tolerance. Это operational computational-reproduction classification, не физическая validation claim.

## 5. Post-merge canonical verification (main @ `3fb6dc1`)

- ancestry: `216c01c` — предок `main` ✓
- `python3 -m unittest discover -s tests -t .` → **Ran 360 tests, OK** (exit 0)
- `harness.cli check-consistency --root .` → ok (exit 0)
- `release.build_library_r12 check` → ok=true, problems=[] (exit 0)
- `release.card_lint package` → ok, errors=[], warnings=[] (exit 0)
- `work_cli validate EX-NL5-001-D-R1` → ok, terminal handoff (exit 0); `workflow_lint` → 0 violations (exit 0)
- hosted CI на merge commit `3fb6dc1`: RC0 hosted validation (H0) = success

## 6. State transition (этим checkpoint'ом)

```text
NL5-001: READY -> ACCEPTED
completed_tasks += NL5-001
NL5-002: PLANNED -> READY
next_work_order = NL5-002
stage NL5 = IN_PROGRESS  (НЕ ACCEPTED: требует принятый NL5-002)
external_reproductions = 0  (не меняется: NL5-001-C был clean reproduction внутри проекта, не внешний executor)
open_decisions: license choice удалён (D2 закрыт)
```

Синхронизировано: `project/state.json`, `config/control/harness/scheduler-policy.v1.json` (ревизия NL-N5-2026-09-18-R2), `docs/work/WORK_QUEUE.md`, `docs/work/SESSION_LOG.md`.

## 7. Remaining risks / deferred

- 74b arm-manifest-v2 — отдельный bounded WO (не блокирует NL5-002).
- 11b INCONCLUSIVE — интерпретация требует дополнительных реплик только через новую protocol revision; пост-hoc tuning запрещён.
- LICENSE — declaration-форма (SPDX + ссылка), полный текст Apache-2.0 рекомендуется вложить в дистрибутив пакета (замечание reviewer'а D, non-blocking).
- NC-2 gate (UNDECIDED license) — warning + contract, не hard exit; при желании усилить до hard error в будущей ревизии builder'а.

## 8. Next

**NL5-002 «Obtain external reproduction»** (READY): независимый внешний executor стартует ТОЛЬКО с опубликованного release-пакета `nanolab-components 0.1.0` (без внутренних знаний автора): fresh environment, exact package/version, команды, численные расхождения/failures/repairs. NL5 acceptance требует хотя бы одного external reproduction. NL6-001/E5 открывается только после принятого NL5-002 и закрытия NL5.
