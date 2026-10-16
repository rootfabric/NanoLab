# WO-PREP-S17-R2 — восстановить force inputs, nucleotide ports и driver–follower topology (0 scientific runs)

Статус: **HANDOFF_COMPLETED / AWAITING REVIEW+VERIFY — IMPLEMENTED_WITH_SOURCE_GAP** (execution complete 2026-10-16: стадии A/B/D/E закрыты SOURCE_CONFIRMED-фактами; стадия C — честный fail-closed `NOT_RECONSTRUCTED` для driver–follower MD-сборки: driver/follower каталоги отсутствуют в полных CD-перечислениях всех 4 архивов; draft PR #59; merge = Human Gate). Work Order: [`WO-PREP-S17-R2`](https://github.com/rootfabric/NanoLab/issues/58) (owner authorization 2026-10-16: выполнить S17-R2 целиком — реализация, тесты, draft PR — без промежуточных подтверждений). Родитель: `WO-PREP-S17-R1` (PR #57, MERGED 2026-10-15). Маршрут: [LITERATURE_TO_MECHANISM_ROUTE_R1](../control/LITERATURE_TO_MECHANISM_ROUTE_R1.md) (merged) — будущие `MechanicalComponentSpec v1` / `AssemblySpec v1` требования; этот WO поставляет только доказательный сырой материал (index map, port map, assembly recipe), НЕ сами spec-контракты.

## Scope

- Цель: для S17 (Centola et al., leaf-spring DNA nanoengine, DOI `10.1038/s41565-023-01516-x`) восстановить и доказать **статически**: (A) source recovery недостающих входов, (B) детерминированное индексное пространство нуклеотидов для `NE`/`nNE`/`NE_NB` и истинный namespace индексов `get_k.py` `[2034,6657]`, `[4593,4411]` и `T7_force.txt` `8694`/`7374`, (C) рецепт сборки driver–follower linked topology (или честный fail-closed `NOT_RECONSTRUCTED`), (D) узкие инструменты + тесты, (E) evidence/handoff.
- Base: `main @ 513c4fa86470d939e9f9b7829e9c67c489c15a57`, tree `6d3a2132ae6ecdfed6269fe39697e8ac9bab152a` (fresh fetch 2026-10-15T23:45Z; совпадает с observed main в issue).
- Risk: **MEDIUM**, claim class: **C0_SOFTWARE_ONLY**, 0 scientific runs, 0 paid compute.
- Claim ceiling: **`PINNED_IMPORT_VERIFIED`** наследуется от R1; R2 дополнительно может доказать только **статическую точность индексов/топологии/сборочного рецепта** (source-confirmed), НЕ `MODEL_REPRODUCED` / `ASSEMBLY_VALIDATED`. Если linked topology не восстанавливается из источников — результат `IMPLEMENTED_WITH_SOURCE_GAP`; объявлять `S17_ASSEMBLY_READY` запрещено.
- Бюджет передачи: ≤ 256 MiB суммарно (HEAD/Range/remote-listing приоритетны; полные 3–21 GB Zenodo архивы НЕ скачивать); scratch disk ≤ 2 GiB; U2 `outenemy` — только source/format/structural preflight при реально доступном host, без глобальных установок и без научного моделирования.

## Allowed paths

`docs/work/WO-PREP-S17-R2.md`, `docs/work/WORK_QUEUE.md` (только append), `docs/work/executions/EX-PREP-S17-R2/**`, `docs/research/S17_SOURCE_RECOVERY_R2.md`, `docs/research/S17_R2_PORT_MAP.json`, `docs/research/S17_R2_ASSEMBLY_MANIFEST.json`, `docs/research/S17_KNOWLEDGEPACK_R2.json` (только при реально новых pins), `scripts/knowledge_pack/s17_*.py`, `tests/test_s17_r2_*.py`.

## Forbidden (без исключений)

`project/state.json`, `project/plan.json`, NL5 freeze/thresholds и любые frozen artifacts, `scripts/nl5/**`, `scripts/r2/**`, `scripts/hinge_family/**` (переиспользовать импортом можно, изменять нельзя), `scripts/e2/**`, `scripts/nl4/**`, канонический научный статус NL5/NL6, scientific oxDNA runs / E5 / новые симуляции, релаксации и pull/release, крупные архивы, direct main push, force-push, self-review/self-acceptance, claim inflation, вендоринг сырых файлов (`sulcgroup/hinges` — REFERENCE_ONLY, без лицензии; Nanobase/Zenodo raw — не вендорить).

## Non-goals (жёстко)

- Не запускать E5/NL6-001; не менять state; не «придумывать» отсутствующие молекулярные связи: всё, что не доказано источником, получает `SOURCE_CONFIRMED` / `INFERRED_CANDIDATE` / `UNVERIFIED` / `UNKNOWN` строго по доказательности; `INFERRED_CANDIDATE` не проходит production preflight.
- Не путать опубликованное экспериментальное D–F соединение (TEM) с искусственной MD-сборкой linked.top.
- 16 pN не подставлять в какие-либо расчёты без проверки единиц/источника; задача — задокументировать пространство индексов и параметры, не воспроизводить физику.

## Required outputs

1. `docs/research/S17_SOURCE_RECOVERY_R2.md` — для каждого реального входа: exact URL/version/size/SHA-256/rights/UTC retrieval; для ненайденных — `NOT_FOUND`/`BLOCKED_SOURCE` с проверенными адресами и способами разблокировки.
2. `docs/research/S17_R2_PORT_MAP.json` — детерминированный map `global nucleotide index ↔ strand ID/offset/base/linkage ↔ config particle` для NE/nNE/NE_NB (pinned digest, 0/1-based convention, chain ordering) + статус namespace для индексов анализа и trap-пары.
3. `docs/research/S17_R2_ASSEMBLY_MANIFEST.json` — assembly recipe: `SOURCE_CONFIRMED` / `PARTIAL_EVIDENCE` / `NOT_RECONSTRUCTED` (fail-closed), перечисление минимальных blocked inputs; deterministic digest любой статически воспроизведённой сборки + machine-readable receipt.
4. `scripts/knowledge_pack/s17_*.py` — narrow CLI tools, deterministic/offline-by-default; `--fetch` только explicit opt-in; KnowledgePack v1 не ломается.
5. `tests/test_s17_r2_*.py` — synthetic fixtures, offline: deterministic mapping, 0/1-ambiguity, wrong pin/variant, duplicate-sequence anchors, strand boundaries, circular strands, broken linked refs, damaged topology/config, wrong force units, invalid geometry, path traversal/ZIP-bomb/oversize, fail-closed без рецепта, rights violation.
6. `docs/work/executions/EX-PREP-S17-R2/**` — паспорт, append-only events (START → CONTINUATION → HANDOFF), evidence + evidence-map, summary; `WORK_QUEUE.md` append-запись.

## Validation

```bash
python3 -m unittest discover -s tests -t .
PYTHONPATH=scripts python3 -m harness.cli check-consistency
PYTHONPATH=scripts python3 -m harness.workflow_lint
PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-PREP-S17-R2
```

Плюс: все `tests.test_knowledge_pack*` зелёные; JSON/schema syntax; offline repeated mapping/assembly digest consistency; negative controls → deterministic FAIL; `project/state.json` и frozen NL5 artifacts byte-identical; 0 scientific runs.

## Review and handoff

Draft PR в `main` c `BASE_HEAD/BASE_TREE`, `PRODUCT_HEAD/PRODUCT_TREE`, test counts, exact input pins, blocked sources, byte budget, `NO_SCIENTIFIC_RUNS=TRUE`; затем отдельный fresh Reviewer, после repair — отдельный exact-head Verifier, затем Director/Human Gate.
