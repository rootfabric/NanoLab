# Work Order NL3-002-PROTO — E2-PROTO-R1 preparation: arm manifest, observables v2, draft tolerances (child of NL3-002)

Статус: READY (Author: Director 2026-09-12; исполнение — fresh IMPLEMENTER-сессия). Родитель: NL3-002 «Execute E2 component campaign». Предусловия: NL3-002-PILOT выполнен и его калибровочные факты зафиксированы; G1 = B (`docs/control/E2_SOURCE_RIGHTS_G1_DECISION_R1.md`); путь U-obs-1 first-principles зафиксирован (`docs/control/E2_OBS1_SI_DECISION_R1.md`).

**Стэковая зависимость (осознанная):** база ветки `work/nl3-002-proto-r1` — `4d72ce0` (tip пилотной ветки `work/nl3-002-pilot-r1`, НЕ main). Причина: нужны пилотные evidence-файлы и bucketed-инструменты пилота для деривации манифеста и v2-детекции; до merge пилота в main перебазирование не выполняется. Факт фиксируется в паспорте.

## Цель

Подготовить все материалы для freeze `E2-PROTO-R1` (Director): (1) детерминированный first-principles манифест рук шарнира `0b` (путь U-obs-1 из решения R1); (2) ревизия base-pair детекции observables до v2 (пилот показал inadequacy v1: 26–29 пар на 8378 нуклеотидов при ожидаемых ~4000); (3) DRAFT-предложения tolerances и вариантов confirmatory длины с измеренной стоимостью. Финальный freeze (θ, steps, R_confirm, статистика) — Director; эта ветка готовит проекты, не принимает их.

## Пререгистрация подхода (до substantive work)

- **Arm manifest**: `scripts/e2/arm_manifest.py` — детерминированный вывод двух групп нуклеотидов из авторских `0b.top` + `0b.conf` (frame 0): base-pair граф (комплементарность + геометрия: окно расстояний + ориентационный критерий антипараллельности, bucketing для OO scale), объединение пар + стекинг (n3/n5-непрерывность дуплекса, исключающая кроссоверы) в дуплексные цепи, пространственная кластеризация цепей в жёсткие блоки, два крупнейших кластера = `arm_a`/`arm_b`. Выход — canonical JSON (индексы, статистика кластеров, digest входов, версия алгоритма).
- **Входы источника**: download-on-run по exact pinned commit `23fd1ff7731e9017bd776f49206dc42d70d9fe91`, digest-гейт (blob SHA-1 + SHA-256 + size) по `scripts/hinge_family/source_pins.json`, файлы во временном каталоге вне Git, удаление после использования, durable-кэш запрещён (G1=B, U4=NO).
- **Валидация манифеста**: непересечение групп, покрытие только парных нуклеотидов, coverage-отчёт; `angle(arm_a, arm_b)` на frame 0 (факт, без подгонки); два запуска → байт-идентичный JSON; синтетические фиксстуры (известные руки) восстанавливаются; негативы (усечённый conf → ошибка).
- **Observables v2**: `reference_pairs_v2` (расширенное окно + ориентационный критерий антипараллельности a1-осей + mutual-nearest + жадный детерминированный матчинг), `pairs_fraction_v2`; все v2-метрики помечены «v2»; v1-функции и константы R1 не изменяются (reference regression). Определение — в новом `docs/research/E2_OBSERVABLES_R2.md`, статус «pre-confirmatory revision, Director freeze pending». Целевой ориентир адекватности: на frame 0 авторского 0b детектируется правдоподобное число пар (>3000); точное число — факт, не подгонка.
- **Draft proposals**: `docs/work/executions/EX-NL3-002-PROTO-R1/evidence/proto-proposals.json` (canonical): (a) θ_pairs/θ_bonds/θ_disp варианты с обоснованием от пилотных baseline — относительные критерии (например lbf(t) ≤ 2×baseline frame0), все помечены DRAFT; (b) таблица confirmatory вариантов: steps ∈ {2e5, 1e6, 2e7} × R_confirm ∈ {3} с measured wall-прогнозами (0.052–0.060 s/step) и рисками; (c) seeds policy; (d) статистика (квантили, CI). Никаких прогонов.

## Классы и маршрут

Risk: `MEDIUM` (научная инфраструктура для confirmatory кампании, без самих прогонов и научных claim'ов). Claim: `C0_SOFTWARE_ONLY` / outcome NOT_EVALUATED. Маршрут: IMPLEMENTER (fresh-сессия) → REVIEWER → Director (freeze E2-PROTO-R1) → confirmatory WO. Merge — Human Gate.

## Границы

Allowed: `docs/work/WO-NL3-002-PROTO.md`, `docs/work/executions/EX-NL3-002-PROTO-R1/**`, `docs/work/SESSION_LOG.md` (append), `docs/research/E2_OBSERVABLES_R2.md` (новый), `scripts/e2/**` (аддитивно/расширяюще; v1-функции и константы R1 не ломать), `tests/**`. Forbidden: `project/**`, published docs, `experiments/**`, `.github/**`, direct push main, байты источника в Git, durable-кэш, прогоны > 500 steps, 2e7.

## Stop conditions

- Digest-гейт любого входа FAIL → BLOCKED (значения не подгоняются).
- Алгоритм деривации не даёт двух непересекающихся доминирующих кластеров на frame 0 → фиксация факта, DRAFT-статус манифеста, вопрос Director (не подгонять алгоритм под ожидание угла).
- Обнаруживается необходимость физики длиннее 500-step smoke → выходит за границы WO.

## Не входит

Confirmatory-прогоны (2e7 запрещено); freeze θ/steps/R_confirm (Director); SI retrieval (U-obs-1 путь — first-principles); изменение v1-определений; мерж пилотной ветки.

## Checkpoints

START (passport + 0001 до substantive) → CONTINUATION (манифест деривирован; v2 реализована) → END_ANALYSIS (proposals + валидации) → summary + HANDOFF_COMPLETED.
