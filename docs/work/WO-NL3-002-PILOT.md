# Work Order NL3-002-PILOT — E2 pilot: 0b × 1–3, bounded, non-confirmatory (child of NL3-002)

Статус: READY (draft, Author: Director 2026-09-12). Родитель: NL3-002 «Execute E2 component campaign», issue #7. Предусловия: NL3-002A ACCEPTED (`docs/evidence/NL3-002A/DIRECTOR_ACCEPTANCE_R1.md`), G1 = B (`docs/control/E2_SOURCE_RIGHTS_G1_DECISION_R1.md`), U-obs-1 путь зафиксирован (`docs/control/E2_OBS1_SI_DECISION_R1.md`). Ветка: `work/nl3-002-pilot-r1` от свежего main.

## Цель

Первые прогоны динамики на реальном первом шарнире `0b` — **исключительно** калибровочные: измерение стоимости (per-step wall time), стабильности (энергетический трек, целостность), smoke observables. Никаких научных исходов: campaign-level scientific_outcome = NOT_EVALUATED; результаты питона — вход в `E2-PROTO-R1` (tolerances, длины, R_confirm, пороги), после которого встанут confirmatory прогоны.

## Пререгистрация пилота (этот WO = preregistration; изменений после запуска не делать)

- **Runs**: `E2-PILOT-S001`, `E2-PILOT-S002`, `E2-PILOT-S003` — 3 реплики, seeds `101001`, `102002`, `103003` (отличны от авторского 7777; документируемое решение).
- **Subject**: авторские файлы `0b.top` + `0b.conf` verbatim, download-on-run по exact pinned commit `23fd1ff7731e9017bd776f49206dc42d70d9fe91`, digest-гейт по `source_pins.json` перед каждым использованием, файлы вне Git, durable-кэш запрещён (U4 = NO), после завершения execution — удаление.
- **Input**: ключи из `pro_CPU.in` verbatim (`DNA2`, `salt 0.5`, `T 300K`, CPU, double; `external_forces = 0` остаётся), отклонения — только: `steps` → bounded пилотное значение (см. процедуру), `seed` → per-replica, имена output-файлов per-run. Каждое отклонение от авторского input фиксируется в манифесте рана.
- **Процедура бюджета**: сначала 500-step проба → измеренный per-step cost → выбор `steps` так, чтобы engine wall ≤ ~25 мин/реплику (жёсткий минимум 2000 шагов; общий бюджет пилота ≤ 3 ч wall). Реплики — параллельные WSL-процессы (3 шт.), если память позволяет.
- **Observables (non-confirmatory)**: (a) energy trace из `energy.dat`; (b) integrity v1 (bonded long-bond fraction + displacement vs frame 0; pairs — на подвыборке кадров bucketed-алгоритмом при необходимости); (c) DRAFT-proxy угол: PCA между половинами скаффолда (arm_a = scaffold нуклеотиды [0, 2132], arm_b = [2133, 4265]) — явно помечен DRAFT, НЕ манифест E2-PROTO.
- **Output-артефакты**: trajectory/energy/lastconf — вне Git; в Git — манифесты ранов (input digest, SHA-256 + size всех артефактов, location), CSV/JSON-трейсы метрик, сводка стоимости.

## Классы и маршрут

Risk: `MEDIUM` (первые прогоны динамики, но калибровочные, без научных claim'ов). Claim: `C0_SOFTWARE_ONLY` / outcome NOT_EVALUATED. Маршрут: IMPLEMENTER (fresh-сессия) → REVIEWER → Director. Merge — Human Gate.

## Границы

Allowed: `docs/work/WO-NL3-002-PILOT.md`, `docs/work/executions/EX-NL3-002-PILOT-R1/**`, `docs/work/SESSION_LOG.md` (append), `docs/experiments/E2_HINGE_COMPONENT.md` (только если нужна пометка pilot), `scripts/e2/**` (аддитивно: bucketed pairs при необходимости — с equivalence-тестом), `tests/**`, `experiments/evidence/E2/**` (только pilot-манифесты/трейсы, если схема evidence это требует — иначе execution-каталог). Forbidden: `project/state.json`, `project/plan.json`, published-документы, `.github/**`, direct push main, байты источника в Git, durable-кэш, confirmatory-объёмы (2e7 steps НЕ запускать).

## Stop conditions

- Digest-гейт любого входа FAIL → BLOCKED (значения не подгоняются).
- Движок падает на всех репликах → BLOCKED с сохранёнными логами (совместимость 2017-pipeline vs pinned engine — честный gap, кандидат в superseding-решение).
- Выход за бюджет 3 ч wall → ран прерывается, факт фиксируется (это тоже результат калибровки).

## Не входит

E2-PROTO-R1 freeze; confirmatory/параметрическая кампания; SI retrieval (см. U-obs-1 решение); Init_Hinges scan (может быть выполнен попутно тем же download-on-run, но не блокирует).

## Checkpoints

START (passport + 0001 до substantive) → CONTINUATION (rate measurement + выбор steps; каждый ран) → END_EXECUTION (манифесты артефактов) → END_ANALYSIS (трейсы/сводка) → summary + HANDOFF.
