# NL1-002 — Implementer Evidence Map

Исполнение: `EX-NL1-002-R1`. Дата: 2026-09-09. Роли: IMPLEMENTER + SCIENTIFIC_OPERATOR (одна orchestrating-сессия; независимость review/verify обеспечивается fresh-сессиями).

## Intent и классы

- Work Order: `NL1-002` — первый вертикальный E1 путь без ИИ ([WO-NL1-002](../../work/WO-NL1-002.md)).
- Risk: `HIGH`. Публикуемые классы: execution facts (C0-дисциплина текстов); campaign ceiling `C1_COMPUTATIONAL_REPRODUCTION`; campaign-level scientific_outcome = **NOT_EVALUATED** (полный критерий §9 — NL2-002).

## Exact subject

- Base SHA: `71535d00a2e729349eea2337217a2c591ed9317d` (main с ACCEPTED NL1-001, merge PR #22).
- Branch: `work/nl1-002-reference-run-r1`; START `1fa43e9`; frozen campaign subject `5c8774f`; S001 event repair `9cc83e8`.
- Engine: oxDNA `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, campaign-пересборка §3, бинарь `ffc80b1a7abe2a06bea601ac7f730e26c0e5c09c33a9e8c7c5f7a96a4848579f` (3375976 B).

## Изменённые поверхности

`docs/work/WO-NL1-002.md`, `experiments/evidence/E1/E1-R1/**`, `docs/research/PREREGISTRATION_E1_R2.md`, `docs/experiments/E1_REFERENCE_REPRODUCTION.md` (статус), `docs/evidence/NL1-002/**`, `docs/work/executions/EX-NL1-002-R1/**`, `docs/work/SESSION_LOG.md` (append). state.json/plan.json/policies не тронуты (state advance — отдельный control commit при acceptance).

## Прогоны (все COMPLETED, без исключений и скрытых retries)

| Run | Тип | Seed | Wall, s | RSS, KB | avg col2 | Δ от оракула | Band | Evidence |
|---|---|---|---|---|---|---|---|---|
| E1-R1-S001 | T1 production | −200619630 | 13.13 | 6304 | −1.39393635864 | −0.014234 | IN_BAND | да |
| E1-R1-P001 | PILOT | −473348953 | 11.08 | 6328 | −1.37730121179 | +0.002401 | IN_BAND | нет (§6.4) |
| E1-R1-P002 | PILOT | −547126645 | 11.74 | 6700 | −1.39389370430 | −0.014191 | IN_BAND | нет (§6.4) |
| E1-R1-P003 | PILOT | −1610133928 | 12.56 | 6520 | −1.38687945155 | −0.007177 | IN_BAND | нет (§6.4) |

Бюджет: суммарно ~48.5 c wall (< 1 core-hour cap). Модификаций входов: NONE (verbatim byte-exact; верификация 3 файлов на месте перед каждым прогоном). Total runs = 4; failed/excluded = 0.

## Команды / доказательства

- Frozen subject до запуска: commits `5c8774f` + `9cc83e8` (campaign.md, protocol.json, manifests, started-events; S001 started-event добавлен до запуска отдельным коммитом — пропуск в freeze-коммите зафиксирован в самом event).
- Каждый run: cp raw-blob fixture в scratch → sha256sum на месте → `/usr/bin/time -v oxDNA quick_input` → exit 0 → artifacts в Git c artifacts.manifest.json (SHA-256/size/producer).
- Анализ: `analyze_energy.sh` (один и тот же для всех прогонов; среднее колонки 2 по всем строкам + NaN/Inf check). Oracle-факт: S001 IN_BAND; полоса/оракул не менялись.
- Целостность §5.2: 1001 строка energy.dat (protocol note: 1 initial + 1000 prints), 10 конфигураций, NaN/Inf = 0, N=16/molecules=2, engine facts (v3.7 / GIT COMMIT 00dc7fb / T 0.097717) — во всех логах.

## R_confirm freeze

`E1-PROTO-R2` (superseding только §6.4): **R_confirm = 3** — SD пилота 0.00833 (5.6% полосы), все реплики IN_BAND, стоимость ~12 c/прогон. Pilot в evidence не засчитан. Полоса/критерии не менялись.

## Приёмка (самопроверка implementer'а, не acceptance)

- [x] Вертикальный путь end-to-end: preparation (fixture 4/4 + пересборка + импорт-проверки) → production T1 → анализ → архив.
- [x] Measured resources записаны per run (wall/RSS/seed).
- [x] Frozen subject запушен до первого прогона; каждый run — уникальный ID; technical outcome и scientific outcome разделены.
- [x] Campaign-level outcome: NOT_EVALUATED; claims не превышают evidence; T2 confirm — NL2-002.

## Оставшиеся риски

См. evidence-map.json remaining_risks (одна машина/сборка для всех прогонов; SD на n=3 грубая; NATIVE-привязка).

## Next action (один)

Независимый REVIEWER: проверить evidence-пакет NL1-002 (exact HEAD, frozen-before-run, дайджесты, дисциплина NOT_EVALUATED, отсутствие подгонок) → `docs/evidence/NL1-002/REVIEWER_VERDICT.md`.
