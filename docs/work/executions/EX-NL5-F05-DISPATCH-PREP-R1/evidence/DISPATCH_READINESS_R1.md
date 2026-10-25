# NL5-F05-DISPATCH-READINESS-R1 — готовность frozen F2 к dispatch (C0-prep)

Исполнение: `EX-NL5-F05-DISPATCH-PREP-R1` · WO `WO-NL5-F05-DISPATCH-PREP-R1` · Issue [#86](https://github.com/rootfabric/NanoLab/issues/86), программа [#81](https://github.com/rootfabric/NanoLab/issues/81) `NL5-CLOSE-R1`.
Роль: `CONTROL-IMPLEMENTER`, реальная отдельная DSH-сессия (`3e3c6aa5-d615-49a0-8b6a-1805d8f7431a`, см. `dispatch/0000-DIRECTOR-DISPATCH-PROOF.md`).
Класс: `C0_SOFTWARE_ONLY` · risk `MEDIUM` · **SCIENTIFIC_RUNS = 0** · machine-readable зеркало: `DISPATCH_READINESS_R1.json`.

## 1. Итог одной строкой

**READY_WITH_OPEN_GATES:** все offline freeze-предпосылки независимо переподтверждены по первичным Git-байтам; offline-валидатор PASS (exit 0); fail-closed поведение доказано 8 негативными тестами. Реальный запуск науки остаётся **BLOCKED by design**: R2 ACTIVE=false, AUTHOR_U1=NOT_ASSIGNED, authority A не создана (следующий отдельный WO), owner launch approval отсутствует. BLOCKED/INCONCLUSIVE по самому C0-prep scope — нет.

## 2. Recheck HG-B canonical owner record — MATCH

```bash
git rev-parse 3b567ae:docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json
# -> 61d1491233aeb2537f9800d6183def5b8fb0c8e0
git show 3b567ae:docs/evidence/NL5-ACCEPTANCE-POLICY/HG_B_OWNER_DECISION_R1.json | sha256sum
# -> b68dd341a5671d6314da3fcf6d32fae54f88b385b7b5a631edb07b0f6f49d2c9
```

`decision=APPROVED`, `record_kind=HG_B_OWNER_APPROVAL`, issuer `HUMAN_GATE_OWNER`, revision R4. Blob-идентичности равны binding'у в `DIRECTOR_FREEZE_R2.json`; source_commit `549b687` — предок main; байты идентичны на main и на HEAD ветки.

## 3. Exact F2 — пересчитано независимо (не доверяя F01)

`F2 = 60da9a846511265a8ac7564da088c3d74cb073f0`, `TREE = e565c8a6cee9e829fac14008ebc9c2ea1609931d`; F2 — предок origin/main и HEAD.

| Артефакт | GIT_BLOB_SHA1 | CANONICAL_BLOB_SHA256 | Вердикт |
|---|---|---|---|
| protocol `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` | `4835719622bae49a8e8b480536a482b4b222d408` | `2658ee3e0cd0216245f0ab63b67f73969d2d060e703e2e94819e0d93fc997c6d` | MATCH |
| contract `…/repro-v0-2-freeze-contract-FROZEN_R2.json` | `d6a9ccde4d1dadf42d1a8cd9b88faa02646cf70b` | `7e6476544e82af73d5d7e0672666ece99bf4d499a0da30645b02886bcdc45b3a` | MATCH |
| seed record `…/repro-v0-2-seed-record-FROZEN_R2.json` | `0164e0e3f5dda6dbf63174df3730b1bd921d2c76` | `8e844bff299df82bcbc5d524b5881de56190a59fc8e39a4a8bdeeddc97fa7e28` | MATCH |

Рабочая копия этих путей байт-в-байт равна F2-блобам; рабочий tree чист.

## 4. D2 + Reviewer(F2) + Verifier(F2) — подтверждено независимо

- **D2** `DIRECTOR_FREEZE_R2.json`: FREEZE, пин exact F2 HEAD/TREE; commit записи `a2f7304` (ветка `repair/nl5-v02-director-freeze-r2`) — в main.
- **Reviewer(F2)**: ветка `review/nl5-v02-frozen-r2-scientific-review-r1`, tip **`d63eb5c088133f92ebd20501835a159cc3e4b865`**; `FRESH_SCIENTIFIC_REVIEW_R2.json` @ tip: `REVIEWER_VERDICT`/`INDEPENDENT_REVIEWER`/**PASS**, pinned head/tree = F2; наследует F2; append-only (3 коммита, только добавления файлов: 557 insertions / 0 deletions).
- **Verifier(F2)**: ветка `verify/nl5-v02-frozen-r2-r1`, tip **`f12d0b497cb28a2f18476ded90b4b1bd079bb414`**; `FRESH_VERIFIER_R2.json` @ tip: `VERIFIER_VERDICT`/`INDEPENDENT_VERIFIER`/**VERIFIED**, pinned head/tree = F2; наследует F2; append-only (1 коммит, 618 insertions / 0 deletions).
- **F01-F-1 подтверждён**: оба tip НЕ слиты в main (`git merge-base --is-ancestor` → NO); main ссылается на них по exact tip SHA через `DIRECTOR_FRESH_AUDIT_R1`. Authority A обязана_BINDить записи по exact tip SHA (или по интегрированным коммитам).

## 5. Feasibility и подсчёт seed identities — подтверждено из frozen байт

- Grid: primary **0b/32b N=64** (n_min 52), controls **11b/53b N=10** (n_min 8); `ceil(0.8·N)` и `floor(0.2·N)` сходятся; grid-поиск `[40,48,64,80,96,128]`, selected 64, headroom 0.8.
- **Seed identities (точный подсчёт):** fresh **148** = 64+64+10+10 (индексы реплик с 1; 41 recorded collision-skip: 10/11/10/10); bootstrap 4; replacement pool **28** (12/12/2/2); всего **180 различных identity** (0 коллизий).
  - Замечание к формулировке: `(64+64+10+10)*2 = 296` — это число **RUNS** (2 runs на pair), а identity ровно **148**.
- Runs: **296 confirmatory** (148×2) + **≤56 replacement** (28×2) = **≤352**; **≤560 h/platform**; **CPU-only** (cuda=OFF, mpi=OFF); HG-B ↔ F2 contract — полное равенство параметров.
- Независимый replay (скрипт из /tmp, вне репо; `scripts/**` не модифицирован): регенерация всех 148+4+28 identity из anchor-алгоритма + повтор дерева коллизий (2102 текстовых блобов pinned tree `a9d7d07`) → **85/85 проверок PASS**; все 176 run-identity CLEAN вне allowlist, все 41 skip подтверждены реальными hit'ами; digest'ы collision-манифеста сходятся (file-bytes `77ef5b6a…` = binding; canonical `6966b216…` = внутренний `manifest_sha256`).

## 6. Offline validator + adversarial fail-closed preflight

**Positive** (read-only, на байтах F2):

```
PYTHONPATH=scripts python3 -m nl5.repro_v02_freeze_contract gate --contract …FROZEN_R2.json --protocol …FROZEN_R2.md --record …FROZEN_R2.json --repo-root .
# exit 0: gate=PASS, validation_stage=PREFREEZE_VALIDATION_PASS, freeze_status=FROZEN,
#         dispatch=DISPATCH_BLOCKED, dispatch_ready=false, budget 296/56/352/560h
```

**Adversarial** (только временные копии в `/tmp/f05_adv`, вне репо; ничего не закоммичено; authority A НЕ создавалась):

| # | Подмена | Exit | Результат |
|---|---|---|---|
| ADV-1 | contract `n:64→63` | 3 | FREEZE_GATE_FAIL (N, seeds length, budget derivation, protocol cross-check) |
| ADV-2 | seed record `173237241→173237242` | 3 | FREEZE_GATE_FAIL (drift + digest stale) |
| ADV-3 | protocol prose `N = 64→65` (непривязанная строка) | 0 | **не отклонён на gate-стадии** → finding **F05-F-1** |
| ADV-4 | authority `{}` | 3 | отклонён (все 20 обязательных ключей) |
| ADV-5 | authority без `r2_record` | 3 | отклонён (R2-запись обязательна) |
| ADV-6 | authority `schema_version=2` | 3 | отклонён (v1/v2 reject; fixture без allow_fixture reject) |
| ADV-7 | authority без `hg_b_record` | 3 | отклонён (HG-B — machine precondition) |
| ADV-8 | несуществующий authority-файл | 3 | отклонён (read error → fail-closed) |

**F05-F-1 (LOW, компенсировано):** `gate` машинно привязывает авторитетные декларации протокола (cardinality-строку, `machine-contract-v1`, `scan-allowlist-v1`), но не произвольную прозу. Компенсация: (а) F2 — immutable Git-коммит, blob запинен в D2 и будет пинен в authority A; (б) стадия `plan` (authority, schema v3) отвергает ЛЮБОЙ байт-дрейф протокола против `frozen_subject_binding.protocol.canonical_sha256` (код валидатора ~L1933–1945, проверено инспекцией); (в) R/V пинят exact F2.

**F05-F-2 (INFO):** формулировка freeze-WO «allowlist-пути существуют в pinned tree a9d7d07» неточна для второго пути (`…PRE_DATA_R4.json` в дереве отсутствует, `git show` → exit 128). Механически инертно: скан классифицирует hit'ы по exact-path exclusion и не требует существования allowlist-файлов в сканируемом дереве; ordered-exact binding цел, rerun PASS.

**F05-F-3 (INFO):** 4 bootstrap-статистических seed регенерируются, но их литералы встречаются в исторических PRE_DATA записях внутри pinned tree; правило коллизий покрывает только run-identity (все CLEAN). Не нарушение гейта.

## 7. Budget guard

См. `budget-ledger-R1.json` (immutable, append/revision-only): 296+≤56 ≤ **352** runs (≤176/platform), **560 h/platform**, **CPU-only**, платных ресурсов — 0/запрещено; storage: по NL5-002 факту ~106 MB/run (max 119.8; trajectory.dat ~101 MB) → оценка ≤ ~21 GB/platform (≥32 GB/platform с запасом на superseded-попытки, ≥64 GB суммарно); raw evidence — вне Git, в Git только манифесты sha256+size. Pricing: покупки не производились, облачные альтернативы NOT_PRICED (требуют отдельного owner-решения). Stop rules STOP-1..STOP-7 — внутри ledger. Небbinding planning-note: при исторических ~4.0 ч/run 176 run/platform ≈ 704 ч последовательно → cap 560 ч достижим при ≥2 параллельных слотах/платформа.

## 8. Точный список условий до launch gate (NO_RUN до полного набора)

1. **GATE-F04-R2-ACTIVE** — F04: U1 host назначен (`AUTHOR_U1 != NOT_ASSIGNED`), fingerprint frozen, гейты U1-U5 + NC-U1..U5 зелёные, независимые review+verify активации, запись `R2_ACTIVATION_RECORD`.
2. **GATE-AUTHORITY-A** — свежий `nanolab_v02_dispatch_authority` **schema v3**, созданный **отдельным следующим WO после F04** (не в этом): пин exact F2 HEAD/TREE; `frozen_subject_binding` contract/protocol/seed блобов F2; bindings D2 + HG-B blob `b68dd341…` + Reviewer(F2) PASS tip `d63eb5c…` + Verifier(F2) VERIFIED tip `f12d0b4…` (exact SHA) + R2 record; обе ноги (AUTHOR_U1/EXTERNAL_U2) authorized. **Создание authority A — следующий отдельный WO.**
3. **GATE-HG-A-LAUNCH-APPROVAL** — отдельное явное owner scientific launch approval (protected writer) именно на ЭТУ кампанию; approval на создание плана ≠ разрешение запускать 296 runs.
4. **GATE-BUDGET-AUTHORIZATION** — owner budget authorization со ссылкой на `budget-ledger-R1` (352 ceiling, 560h/platform, CPU-only, storage ≥64 GB, pricing-решения).
5. **GATE-RV-INTEGRATION-OR-PIN** — R/V записи интегрированы в main ЛИБО забинжены exact tip SHA внутри authority A (F01-F-1).

Даже при выполнении 1–5 машина каппирует свой вывод в `DISPATCH_PRECONDITIONS_RECORDED`; `DISPATCH_AUTHORIZED` существует только через внешний Human/Protected-Writer gate.

## 9. Расхождения Issue #86 ↔ репозиторий

- «unique 148 frozen seed identities» — подтверждено (148 identity; 296 — это runs). Терминологическое уточнение, не расхождение.
- R/V записи существуют и PASS/VERIFIED, но живут на неслитых ветках (F01-F-1) — учтено в GATE-5.
- Численных расхождений Issue #86 ↔ HG-B ↔ D2 ↔ F2 не найдено.

## 10. Валидация сессии

`work_cli validate` ok (`WORK_ORDER_STARTED → CONTINUATION_CHECKPOINT → HANDOFF_COMPLETED`, summary present) · `harness.cli check-consistency` ok · `workflow_lint` 0 blocking · `python3 -m json.tool` strict-parse OK для каждого нового JSON · push non-force в `origin/work/nl5-f05-dispatch-prep-r1`.
