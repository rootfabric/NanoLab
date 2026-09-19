# EX-NL5-002-C2-R1 — Summary: mechanical comparison B-R2 vs frozen contract

- Work Order: `WO-NL5-002-C2-R1` (parent `NL5-002`), ветка `work/nl5-002-c2-compare-r2-r1`, base `48c55b3`
- Subject: `work/nl5-002-b-r2-external-run-r1 @ 9556d0f6ac527db6f32518b51b6de5825a171548` (terminal ingest B-R2)
- Процедура: заморожена ДО данных (`WO-NL5-002-C2-R1.md`); все числа — из ingested packaged-convention evidence
- **WO-level verdict (binding, frozen mapping WO-NL5-002-A-R1): `MISMATCH`** — 0b и 32b directionally separated от frozen envelopes

## 1. Integrity gates кампании B-R2 (из evidence)

| gate | результат |
|---|---|
| package verify (старт кампании) | ok=true, 42 files, 0 errors (evidence/logs/verify.json) |
| upstream digest gates (size+blob_sha1) | 9/9 PASS, sha256 == published (evidence/logs/upstream_digest_gate.json) |
| frame0 oracle самопроверка | 4/4 EXACT == design.angle_frame0_deg (evidence/logs/frame0_oracle_summary.json) |
| seeds | 12 fresh seeds заморожены до прогонов, ≠ reference (evidence/seeds_frozen.json) |
| exit codes | 12/12 НАБЛЮДАЕМЫЕ = 0 (exit_code.txt; run_output_digests.json — 84 записи) |
| trajectory completeness | 0b/11b: 50 кадров (200k); 32b/53b: 37 (150k); все packaged gates exit=0 (completeness.txt) |
| engine | oxDNA 00dc7fb9, pristine tarball, CPU/double, правок исходников НЕТ (engine/build_provenance.txt) |
| budget | wall 13.8h < 48h; 20h/replica kill не достигнут; paid=0, GPU=0 |
| analysis identity (проверка C2) | analyze_hinge.py + arm-manifests ×4 + карточки ×5: sha256 == RELEASE_MANIFEST (PASS) |

## 2. Per-card механическое сравнение (recalc по frozen rule)

| карта | fresh replica medians (deg) | campaign statistic | frozen envelope | классификация (recalc) | executor | agree |
|---|---|---|---|---|---|---|
| 0b | 67.586275641 / 68.389781796 / 69.600296613 | 68.389781796 | [65.095434789, 67.236579608] | **MISMATCH** (все 3 строго выше) | MISMATCH | ✓ |
| 11b | 72.255209867 / 73.560609814 / 75.35617795 | 73.560609814 | [72.165683993, 74.533109426] | MATCH | MATCH | ✓ |
| 32b | 74.713050721 / 75.180138343 / 76.100697787 | 75.180138343 | [77.4927314, 79.877463339] | **MISMATCH** (все 3 строго ниже) | MISMATCH | ✓ |
| 53b | 130.244172898 / 132.41188514 / 136.169087714 | 132.41188514 | [131.049227687, 135.285186059] | MATCH | MATCH | ✓ |
| 74b | — | — | — | NOT_MEASURED / KNOWN_GAP (значения не производились) | N/A | ✓ |

Цепочка run→campaign (medians, exits, valid frames) консистентна для всех 12 прогонов
(`comparison.json` → `run_chain`). Machine-выкладка: `comparison.json`.

## 3. Отклонения (задокументированные, научные пороги не менялись)

- **D1** (executor): wave-1 32b/53b остановлены при смене launch-стратегии, перезапуск под новыми ID (-R), те же frozen seeds — по protocol §9; честно записано (aborted_attempts.json).
- **D2** (orchestration): потеря executor-сессии ~05:48Z; detached runs не пострадали; watcher административно перезапущен 14:03:46Z без изменения скрипта (лог в evidence/logs/).
- **D3** (executor): warnings/stderr прогонов и анализа отсутствуют.
- **N1 (окно)**: R2-протокол использует per-card окна (0b 200000; 11b/32b/53b 150000 — по карточкам/protocol_pins); A-R1 фиксировал универсальное t≤150000 (addendum §8). Применено карточное окно (= published contract и дизайн reference-кампаний). Пороги/envelope не затронуты. Помечено для Fresh Reviewer.
- **F-orch1 (packaging, вне науки)**: RELEASE_MANIFEST.json v0.1.1 пинует 7 `convention/nlbl_convention/__pycache__/*.pyc`, отсутствующих в git-дереве release → `reproduce.py verify` на fresh git-checkout падает (missing), в рабочей копии ломается после реимпорта (перегенерация .pyc). Научные поверхности не затронуты (§1, analysis identity PASS). Кандидат в bounded packaging repair (v0.1.2) — отдельное решение.
- **F1–F4 (executor)**: RIGHTS.json version 0.1.0 при VERSION 0.1.1; echo last_step в completeness.txt (dt-эвристика, информационно); proxy/git-трение → карточный tarball-путь; последний кадр 148000 при шаге 150000 (интервал печати 4000).

## 4. Вердикт и disposition

- Frozen mapping (WO-NL5-002-A-R1): `MISMATCH` — «≥1 карта MISMATCH по frozen rule (все 3 реплики строго по одну сторону envelope)». 0b: все выше; 32b: все ниже. REPRODUCED/REPRODUCED_WITH_DEVIATION недоступны (требуют 0b/32b/53b MATCH).
- Это НАУЧНЫЙ результат external reproduction: техническая цепочка и portability-repair v0.1.1 сработали (конвенция теперь самодостаточна: frame0 4/4 EXACT), но измеренные распределения 0b/32b на платформе исполнителя (Ubuntu 22.04, gcc 11.4, Xeon E5-2698 v3) вышли за узкие 3-репличные авторские envelopes. 11b впервые MATCH.
- **Пороги/envelope НЕ меняются.** Автоматический R3 не запускается (owner mission §12). Кандидат-причина для исследования (не вердикт): хаотическая чувствительность MD-траекторий к platform/FP-вариации при узком 3-репличном envelope.
- **Disposition NL5**: критерий приёмки NL5 («release package воспроизведён вне авторской среды», frozen rule) данной кампанией НЕ выполнен. NL5-002 = terminal MISMATCH; NL5 = IN_PROGRESS; `external_reproductions` остаётся 0. Решение о следующих шагах (исследовательская ветка platform-sensitivity / новая protocol revision / иное) — Human Gate.

## 5. Exact HEAD/TREE

- См. event 0003 (HANDOFF_COMPLETED). Reviewer/Verifier binds к этому subject.
