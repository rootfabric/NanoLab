# NL2-001 — VERIFIER PROGRESS (verification-by-execution, раунд 2)

Независимый VERIFIER, fresh-сессия. Ветка: `verify/nl2-001-contracts-e0-r1`, субъект проверки: `work/nl2-001-contracts-e0-r1` @ `1d594f3cd6f7673307310f53393cb5680deb7696`. Метод — собственное воспроизведение (verification ≠ review); чек-лист поверхностей — §1–§5 [RE_REVIEW_R1.md](https://github.com/rootfabric/NanoLab/blob/review/nl2-001-contracts-e0-r1/docs/evidence/NL2-001/RE_REVIEW_R1.md). Промежуточный журнал; итог — `VERIFIER_VERDICT.md`.

## V1. Ancestry / scope — ВЫПОЛНЕНО

- `git merge-base --is-ancestor 15a2c9b 1d594f3` → exit 0: base `15a2c9b1b5c095e24e2e1c24afd77feef5361102` — предок проверяемого HEAD.
- `git diff --name-only 15a2c9b 1d594f3`: 815 файлов, 25689 insertions(+), 1 deletion(-); распределение: `experiments/evidence/**` 797, `docs/work/**` 9, `docs/evidence/NL2-001/**` 4, `docs/research/**` 4, `docs/experiments/E0_PIPELINE_VALIDATION.md` 1 — **все изменения только evidence-поверхности**, вне их — 0 файлов.
- Инструмент бит-в-бит base (tree-hash compare): `config` `592cddc2…`≡, `scripts` `2988ec85…`≡, `.github` `416af048…`≡, `project` `fecf726f…`≡ (base ↔ 1d594f3). `project/state.json`, `project/plan.json` не тронуты.
- Единственный не-add файл — статусная строка `docs/experiments/E0_PIPELINE_VALIDATION.md` (NOT_RUN → RUN), разрешено WO (allowed_paths, «только строка статуса»).

## V2. Контрольные прогоны E0 (собственное воспроизведение, ≥6 случаев) — ВЫПОЛНЕНО

Метод: замороженный инструмент `experiments/evidence/E0/E0-R1/tools/e0_runner.py` (бит-в-бит, см. V1) вызван на отдельном worktree `verify/nl2-001-contracts-e0-r1` @ `1d594f3`; прогоны — ТОЛЬКО в scratch (`C:\NanoLab\scratch\verify-nl2-001\`, published-поверхности не изменялись; worktree остаётся чистым). Subject E0-R4 `ce477aad1e4a125c9e881fd9f6a741ec6d2fa876`; протокол/дайджесты — `E0-R4/protocol.json` / `input_digests.json`; фикстуры материализованы runner'ом из git-блобов subject с дайджест-контролем (расхождений нет). Окружение: Python 3.11.8, jsonschema 4.22.0, git 2.53.0.windows.1 — совпадает с environment_binding протокола. Для U001 tier-2 пропущен (`--skip-tier2`: сетевой fetch — best-effort негейтящий по §11.4; в published R4 он NOT_OBTAINED).

| Кейс | Семья | Воспроизведено | Published case_record | Совпадение |
|---|---|---|---|---|
| E0-R4-U002 | UNIT | 4/4 вердикта REJECTED, вкл. подделку `0.0978` → REJECTED | то же (все REJECTED) | MATCH |
| E0-R4-N006 | NEG | битый provenance: exit 3, ok:false, errors непуст | exit 3, ok:false | MATCH |
| E0-R4-G001 | GEO | √2=1.4142135623730951 и 90° — оба query true (atol 1e-12) | то же | MATCH |
| E0-R4-S003 | STATUS | **exit 0, ok:true, separation_enforced=false → NOT_SUPPORTED (gap)** | NOT_SUPPORTED | MATCH |
| E0-R4-U001 | UNIT | T=20C→0.097717 ACCEPTED, delta=0, полоса 5e-7 | ACCEPTED (tier-1) | MATCH |
| E0-R4-POS001 | POS | 19/19 checks true (17 run-каталогов + EX + check-consistency) | 19/19 | MATCH |

Скрипт сверки (own script, `compare_case_records.py` в scratch): scientific_outcome + frozen expected + observed-ядро (exit_code/checks/verdicts/results) — **6/6 MATCH**; timestamps/durations сознательно не сравнивались (машинные). Исходы независимого воспроизведения совпали с published: **17 SUPPORTED + S003 NOT_SUPPORTED** подтверждается на выбранных 6 кейсах из 5 семей.

## V3–V7

В процессе (см. следующие коммиты): digest-vs-blob 225 записей 4 кампаний + superseded byte-equal vs `2cee872`; gap S003 прямой CLI-пробой; jsonschema/CLI-пробы (R1/R3/R4 ok; R2 — 18 fail с текстом campaign_id); пререгистрация (freeze→run хронология, tolerances R1→R4); отсутствие self-acceptance/E-статусов.
