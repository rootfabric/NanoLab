# EX-NL5-F05-DISPATCH-PREP-R1 — summary

**WO:** `WO-NL5-F05-DISPATCH-PREP-R1` (C0-подготовительная часть F05, Issue [#86](https://github.com/rootfabric/NanoLab/issues/86), программа `NL5-CLOSE-R1` [#81])
**Роль:** `CONTROL-IMPLEMENTER`, реальная отдельная DSH-сессия `3e3c6aa5-d615-49a0-8b6a-1805d8f7431a` (dispatch proof: `dispatch/0000-DIRECTOR-DISPATCH-PROOF.md`)
**Класс:** `C0_SOFTWARE_ONLY` · risk MEDIUM · **SCIENTIFIC_RUNS = 0** · authority A **не создана** (вне scope)
**Статус:** `HANDOFF_READY` (документальная передача Director; self-accept запрещён)
**Ветка:** `work/nl5-f05-dispatch-prep-r1` от BASE `3b567ae33f247b182b2ae451d2cc4598a9e76019`

## Что сделано

1. **Recheck HG-B** (`HG_B_OWNER_DECISION_R1.json`): blob `61d1491233aeb2537f9800d6183def5b8fb0c8e0`, canonical SHA-256 `b68dd341a5671d6314da3fcf6d32fae54f88b385b7b5a631edb07b0f6f49d2c9` на main `3b567ae` — **MATCH** с D2-binding; `decision=APPROVED`; source_commit `549b687` в main.
2. **Exact F2 пересчитан независимо**: `60da9a846511265a8ac7564da088c3d74cb073f0` / tree `e565c8a6cee9e829fac14008ebc9c2ea1609931d`; protocol `48357196`/`2658ee3e`, contract `d6a9ccde`/`7e647654`, seed record `0164e0e3`/`8e844bff` — **3/3 MATCH**; F2 — предок main; рабочая копия байт-идентична F2.
3. **D2 + R/V цепочка подтверждена из первых рук**: D2 (commit `a2f7304`, в main) пинит exact F2; Reviewer(F2) **PASS** @ tip `d63eb5c088133f92ebd20501835a159cc3e4b865`; Verifier(F2) **VERIFIED** @ tip `f12d0b497cb28a2f18476ded90b4b1bd079bb414`; оба append-only, пин exact F2, **не слиты в main** (F01-F-1 подтверждён).
4. **Feasibility из frozen байт**: primary 0b/32b N=64 (n_min 52), controls 11b/53b N=10 (n_min 8); **148 fresh seed identities** (64/64/10/10; 296 — это runs = 148×2) + 4 bootstrap + 28 pool (12/12/2/2) = 180 различных identity; 41 recorded skip воспроизведены bit-exact; **296 + ≤56 ≤ 352 runs**, ≤560 h/platform, CPU-only; HG-B ↔ F2 grid equality PASS; collision-манифест: оба digest пересчитаны, независимый rescan 2102 блобов pinned tree — 176/176 accepted CLEAN, 41/41 skip подтверждены.
5. **Offline validator** (read-only, байты F2): **exit 0 — PASS / PREFREEZE_VALIDATION_PASS / FROZEN / DISPATCH_BLOCKED** (dispatch_ready=false ровно потому, что validated authority не существует — корректный fail-closed).
6. **Adversarial fail-closed preflight** (только /tmp-копии вне репо, ничего не закоммичено): 7/8 негативных кейсов отклонены (exit 3): tampered contract, tampered seed record, empty authority, authority без `r2_record`, schema v2, authority без `hg_b_record`, missing file. 1 кейс (ADV-3: prose-правка протокола вне machine-блоков) прошёл gate → finding **F05-F-1** (LOW, компенсировано: immutability F2 + authority-stage байтовая привязка протокола `canonical_sha256` в валидаторе ~L1933–1945 + exact-F2 пины R/V). Также F05-F-2/F05-F-3 (INFO).
7. **Budget ledger** (`evidence/budget-ledger-R1.json`, immutable, revision-only): потолок 352 runs (≤176/platform), 560 h/platform, CPU-only, 0 платных ресурсов, storage-оценка из фактов NL5-002 (~106 MB/run; ≤21 GB/platform верхняя граница; рекомендация ≥64 GB суммарно с резервом на superseded-попытки), pricing NOT_PRICED, stop rules STOP-1..STOP-7.
8. **Pre-launch gate список** (NO_RUN до полного набора): (1) F04 R2 ACTIVE (U1-U5 + NC-U1..U5 + review/verify + AUTHOR_U1 назначен); (2) **authority A schema v3 — следующий ОТДЕЛЬНЫЙ WO после F04** (protected writer provenance; биндинги D2 + HG-B blob + R/V exact tips + R2 record); (3) отдельное явное owner scientific launch approval (approval плана ≠ разрешение запускать 296 runs); (4) budget authorization на `budget-ledger-R1`; (5) R/V записи интегрированы в main или запинены exact tip SHA в authority A.

## Findings

| ID | Severity | Суть |
|---|---|---|
| F05-F-1 | LOW | gate не привязывает прозу протокола вне machine-блоков (ADV-3, exit 0); компенсация — authority-stage byte binding + immutable F2 + R/V exact pins |
| F05-F-2 | INFO | freeze-WO: allowlist-путь 2 фактически отсутствует в pinned tree `a9d7d07` (механически инертно: exact-path exclusion не требует существования) |
| F05-F-3 | INFO | bootstrap-статистические seed встречаются литералами в исторических PRE_DATA записях; правило коллизий покрывает только run-identity (все CLEAN) |

## Честный класс результата

`READY_WITH_OPEN_GATES` — все offline freeze-предпосылки подтверждены; dispatch реальной науки остаётся **BLOCKED by design**: R2 ACTIVE=false, AUTHOR_U1=NOT_ASSIGNED, authority A не создана, owner launch approval отсутствует. BLOCKED/INCONCLUSIVE внутри C0-prep scope — нет.

## Deliverables

- `evidence/DISPATCH_READINESS_R1.json` (+ `.md`) — machine-readable + человекочитаемое зеркало
- `evidence/budget-ledger-R1.json` — immutable budget ledger + stop rules
- `passport.json` (status `HANDOFF_READY`), `events/0001..0003`, этот `summary.md`
- 1 append-only строка в `docs/work/WORK_QUEUE.md`

## Validation

`work_cli validate` ok · `check-consistency` ok · `workflow_lint` 0 blocking · `json.tool` strict-parse OK (все новые JSON) · push non-force.
