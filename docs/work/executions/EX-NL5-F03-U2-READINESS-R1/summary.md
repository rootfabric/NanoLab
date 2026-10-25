# EX-NL5-F03-U2-READINESS-R1 — Summary (U2 external readiness, C0)

- **WO:** `WO-NL5-F03-U2-READINESS-R1` · **Issue:** #84 (программа #81 `NL5-CLOSE-R1`)
- **Роль:** EXTERNAL-PREFLIGHT-IMPLEMENTER (U2) — реальная отдельная DSH-сессия `ce662f0f-4b0d-4388-b3e0-96e018fecf94` (не author U1)
- **Ветка/ворктри:** `work/nl5-f03-u2-readiness-r1` @ `/home/rdpuser/NanoLab/nl5-f03-u2-readiness`, BASE `3b567ae` (origin/main = BASE, эпоха не менялась)
- **Класс:** RISK MEDIUM · CLAIM C0_SOFTWARE_ONLY · **SCIENTIFIC_RUNS = 0**
- **Статус:** `HANDOFF_READY` (паспорт обновлён: DISPATCHED → HANDOFF_READY)

## Вердикт

```text
READINESS   = READY_FOR_DISPATCH_PREP   (C0-логистика готова к подготовке диспетчирования)
LIVE U2 LEG = BLOCKED_NO_U2_ACCESS_FROM_SESSION   (честно; ничего не имитировалось)
```

## Что сделано

1. **STALE-оценка существующих receipts** (все пересчитаны независимо, ссылки в `U2_READINESS_R1.json` § stale_assessment):
   - `EX-INFRA3-U2-OUTENEMY-READINESS-R1` host-факты (fingerprint, build, smoke, systemd, storage; 2026-10-10/11) → **HOST_STATE_STALE_BY_TIME** (14–15 дней, live-перепроверка обязательна);
   - `FRESH_REVIEW_U2_READINESS_R1.{md,json}` (PASS, 2026-10-11, reviewed `9ded2bf7`) → **GIT_ANCHORED_VALID_BUT_SUPERSEDED_HEAD**: reviewed HEAD — строгий предок PR #55 head `3b6ead17` и main `3b567ae`; после ревью в main вошёл m-1 repair (`BLOCKED_MALFORMED_SPEC`); diff ограничен `scripts/r2/cli.py` (45 строк) + `tests/test_r2_activation_tooling.py` (+29);
   - PR #55 merged:true; `NL5_V02_DRYRUN_MANIFEST_R1.json` — dispatch-снимок PARTIALLY_STALE (Reviewer(F2)/Verifier(F2) тапы существуют не в main — перенос F01-F-1; A-запись отсутствует);
   - Ответ на вопрос WO: **F2 (2026-10-06) заморожен ДО** readiness-ревью (2026-10-11), не после.
2. **Целостность frozen release package (F2)**: 9/9 изменённых F2 файлов — blob-SHA1 идентичны на main; canonical SHA-256 protocol/contract/seed record — **3/3 MATCH** `DIRECTOR_FREEZE_R2.json`; F2 tree пересчитан `e565c8a6…`.
3. **Достаточность входов для независимой сборки на U2**: `SUFFICIENT_WITH_TWO_PROVISIONS` — P-1: маршрут engine-исходников (egress до `00dc7fb9` или digest-staged `source_tree b1742ce9…`) не доказан live; P-2: точный package ref (v0.1.2 по PR #56 vs v0.1.1 + 7 pyc-findings) не запиннен ни в одной authority-записи.
4. **Raw-manifest схема** — `PROPOSED_NON_NORMATIVE` (hash+size+producer+HEAD+storage+retention + digest в append-only ledger); принятие — отдельный bounded WO (fresh Reviewer + distinct Verifier).
5. **Unique job IDs / safe paths / изоляция**: attempt_id = `<run_base> | <run_base>-R<n>` (глобально уникальны, append-only ledger); шесть именованных fail-closed гейтов `run-u2` (`BLOCKED_NO_DISPATCH_AUTHORITY`, `BLOCKED_NON_FIXTURE_SPEC`, `BLOCKED_LAUNCH_GATE_PROTECTED_WRITER`, `BLOCKED_FROZEN_CAMPAIGN_ID`, `BLOCKED_HOST_U2`, `BLOCKED_MALFORMED_SPEC` — последний уже в main); пути только в `~/nanolab/**` (uid 1001, без root, `systemd-run --user`); U2 доставляется только F2 + package export + pinned engine source — никогда U1 raw/промежуточные/workspace/креденшалы.
6. **Матрицы и инвентаризация**: platform independence matrix (9 аспектов), storage/evidence capacity (из существующих evidence: `~/nanolab/*`, ~15 GB/нога, запас ~2×, порог 80%; live-замеры невозможны), бюджеты (296+56 ≤ 352 runs, ≤560 ч/платформа, CPU-only, paid compute запрещён).
7. **Live-чек-лист L-01…L-12** для owner/оператора U2 (обязателен до F07): fingerprint, host-role негативные контроли, df+права, дайджесты бинарника, systemd user, тулинг на текущем main (+ рекомендуется свежий R/V на новом head), репетиции run-u2, package verify v0.1.2, ingress/egress, raw-manifest pilot, NTP, attestation независимости.

## BLOCKED / INCONCLUSIVE

- **BLOCKED_NO_U2_ACCESS_FROM_SESSION**: `~/.ssh/config` не существует; `outenemy` — 0 вхождений в `~/.ssh/known_hosts`; все live-проверки хоста невозможны из этой сессии. Ничего не имитировалось (STOP-условие WO соблюдено).
- Неизвестно из сессии (INCONCLUSIVE до live): фактический диск/inode outenemy сегодня, дрейф fingerprint/systemd/бинарника, поведение v0.1.2 пакета на U2.

## Расхождения Issue #84 ↔ репозиторий

1. Issue требует «подтвердить host identity/fingerprint актуальные в момент исполнения» — из этой сессии невозможно (см. BLOCKED); делегировано чек-листом L-01/L-02.
2. Issue предполагает raw artifact ingress/egress готовым — машинно-читаемой схемы raw-manifest в репо нет (только prose-конвенция); схема предложена (non-normative).
3. «Inventory storage/evidence capacity» — в evidence существует только проекция ~15 GB (2026-10-11); измеренных значений нет и не могло быть получено.
4. Dispatch-цепочка в dryrun-манифесте (R/V MISSING) устарела: R/V тапы найдены F01, но не смержены в main (F01-F-1); A-записи нет → dispatch остаётся BLOCKED (направление не изменилось).

## Валидация (финальные прогоны)

```text
PYTHONPATH=scripts python3 -m harness.work_cli validate docs/work/executions/EX-NL5-F03-U2-READINESS-R1
PYTHONPATH=scripts python3 -m harness.cli check-consistency --root .
PYTHONPATH=scripts python3 -m harness.workflow_lint --root .
python3 -m json.tool  (каждый новый json — strict parse OK)
```

Результаты финальных прогонов зафиксированы в событии 0003 / command_refs.

## Границы

U2-ready ≠ R2_ACTIVE ≠ scientific authorization. R2 = WAITING_HOST/NOT_ACTIVE; AUTHOR_U1 = NOT_ASSIGNED; `machine_launch_authorized=false`; canonical state не менялся; frozen package не менялся; научных запусков нет. Merge в main — Human Gate (Director).

## Next action

Director: fresh Reviewer + distinct Verifier на этой ветке (особенно для raw-manifest proposal) → F05 authority planning (запиннить F2-цепочку + package ref + пины платформ) → owner/оператор U2 выполняет L-01…L-12 → F07 только при общих разрешениях.
