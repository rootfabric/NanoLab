# EX-NL3-002-PROTO-R1 — summary (IMPLEMENTER handoff)

## Что сделано (WO NL3-002-PROTO, подготовка E2-PROTO-R1; без confirmatory-прогонов)

1. **Arm manifest (U-obs-1 first-principles путь)** — `scripts/e2/arm_manifest.py` (arm-manifest-v1): pair graph из авторского frame 0 (v2-геометрия, greedy: 3975 пар, 94.9% нуклеотидов) → дуплексные цепи по stacking-непрерывности (ковалентная связь продолжает дуплекс только если партнёры тоже ковалентны; кроссоверы исключены; 1230 цепей) → жёсткие блоки: цепи объединяются при упаковочной близости (≤ 2.5) и параллельности осей (порог детерминированно авто-выбирается из {0.85, 0.90, 0.95, 0.98} по dominance-gap правилу; выбран 0.9: блоки 1786/1664 vs 146) → два крупнейших блока = arm_a/arm_b, остатки назначены строго более ближней руке.
   - **Факты frame 0 (0b, авторский conf)**: arm_a = 4006, arm_b = 3942 нуклеотидов; не назначено 2 парных нуклеотида (1 цепь); покрытие 94.87% топологии / 99.97% парных; группы непересекаются, только парные нуклеотиды; **hinge_angle (замороженное v1 определение) = 66.89°** (факт, не подгонка; ожидание «малого угла» не подтвердилось — фиксируется как измеренное свойство авторской init-конфигурации); деривация байт-детерминированна (два прогона → идентичный canonical JSON).
   - Манифест: `evidence/arm-manifest-0b.json`; входы digest-gated (blob SHA-1 + SHA-256 PASS), скачаны во временный каталог вне Git и удалены после использования (G1=B, U4=NO durable cache).
2. **Observables v2** — `reference_pairs_v2` / `pairs_fraction_v2` / `analyse_v2` в `scripts/e2/observables.py` + `docs/research/E2_OBSERVABLES_R2.md` (статус pre-confirmatory, Director freeze pending): окно (0.05, 1.3] + антипараллельность a1 (≤ −0.3) + mutual-nearest + жадный матчинг. **Факт frame 0: 3300 пар (mutual) / 3975 (greedy) против 26–29 у v1** — v1 неадекватность устранена; все парные метрики помечены v2; v1-функции и константы R1 не изменены (reference regression). Детерминизм на frame 0: два прогона байт-идентичны.
3. **DRAFT proto-proposals** — `evidence/proto-proposals.json` (canonical): (a) θ_bonds (B-REL-2X: lbf ≤ 2×baseline 0.0539; B-REL-BASELINE-ABS-DELTA: +0.02), θ_pairs (P-V2-050 / P-V2-080 от v2-детектора), θ_disp (D-REL-BOX 20 ед. / D-REL-3X-PILOT 18.76) — все DRAFT с обоснованием от пилотных baseline; (b) steps {2e5, 1e6, 2e7} × R_confirm 3 с measured wall-прогнозами (0.052/0.060 s/step): 0.14 / 0.69 / 13.9 дней calendar, риски; (c) seeds policy (201004/202008/203012, отдельны от авторского 7777 и пилотных); (d) статистика (квантили, bootstrap-CI медианы, без optional stopping). Прогонов не было.

## Валидации

- unittest discover: **242 OK (1 skip)**, включая 11 новых (`tests/test_e2_proto.py`: v2 exact counts на парных фиксстурах, целостность→разрыв, байт-детерминизм v2 и манифеста, восстановление известных рук (twoarm 60°), негативы — усечённый conf → ConfError, count-mismatch → ошибка, single-blob → ArmManifestError).
- `harness.cli check-consistency` ok; `harness.work_cli validate` ok.
- Никакой физики; 2e7 не запускался; байты источника в Git не попадали; temp-каталог источника удалён.

## Открытые вопросы для Director-freeze (E2-PROTO-R1)

1. Режим v2 для production observables: mutual (3300) vs greedy (3975).
2. Выбор θ-вариантов по каждому гейту (см. proposals).
3. Длина confirmatory: локальные 2e5/1e6 vs отложенный 2e7 (infra-решение).
4. Принятие arm-manifest-0b.json как замороженного манифеста E2-PROTO (закрытие U-obs-1 по first-principles пути).
5. Факт для интерпретации: угол frame 0 = 66.89° при ожидании «замкнутого» шарнира; беззнаковая конвенция v1 не различает θ и 180°−θ.

## Артефакты

- Коммиты: a80c1f0 (WO + START records), d38e248 (v2 detector + R2 + тесты), 20e5bee (arm manifest + evidence + proposals) + records-коммит.
- Evidence: `docs/work/executions/EX-NL3-002-PROTO-R1/evidence/{arm-manifest-0b.json, v2-frame0.json, proto-proposals.json, source-download-verification.json, run_arm_manifest.py}`.

**Next action**: REVIEWER (fresh-сессия) на exact HEAD `work/nl3-002-proto-r1` → Director freeze E2-PROTO-R1 → confirmatory WO. Merge в main — Human Gate.
