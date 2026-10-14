# Frozen observable convention v0.1 (DNA hinge family)

Статус: **FROZEN (до данных confirmatory кампании E2, ревизия erratum R1 §2.5)**.
Этот документ вместе с `nlbl_convention/` (референс-реализация),
`arm-manifest-<variant>.json` (frozen манифесты плеч) и `analyze_hinge.py`
(CLI) образует ПОЛНОЕ опубликованное определение наблюдаемого. Внешний
воспроизводитель не нуждается в каких-либо материалах вне пакета.

## 1. Измеряемая величина

Взаимный угол плеч DNA-шарнира:

- единицы: градусы, диапазон **[0, 180]**;
- плечи: множества нуклеотидов `arm_a` / `arm_b` из frozen arm manifest
  (`convention/arm-manifest-<variant>.json`, ключ `arms`), заданы индексами
  частиц конфигурации;
- ось плеча: **первая главная компонента (PCA)** позиций нуклеотидов плеча;
  направление оси выбирается **наружу** — знак фиксируется проекцией на
  вектор от центроида плеча к центроиду противоположного плеча
  (erratum R1 §2.5);
- угол = угол между двумя направленными осями, приведённый в [0, 180];
- реализация: `nlbl_convention.observables.hinge_angle(conf, arms)`.

Самопроверка (оракул): `python3 convention/analyze_hinge.py frame0 --conf
<upstream>.conf --topology <upstream>.top --manifest
convention/arm-manifest-<v>.json` обязан дать в точности
`design.angle_frame0_deg` карточки варианта.

## 2. Detector v2 (пары) и frame-validity gates

Пары: **v2 mutual-nearest** — взаимно ближайшие нуклеотиды разных цепей с
COM-дистанцией в окне [0.9, 1.4) и антипараллельными a1 (a1·a1 < −0.3),
cross-strand; реализация `pairs_fraction_v2` / `reference_pairs_v2`.

Гейты валидности кадра (все должны выполняться):

```text
long_bond_fraction <= 0.1078   доля backbone-связей с длиной выше FENE-предела (r0+DR0 = 0.75+0.25), т.е. > 1.0
pairs_fraction_v2 >= 0.50      pairs(frame)/pairs(first frame), на v2-детекторе
displacement_max <= 20.0       max по нуклеотидам |r(t) - r(0)|
energy |drift| total           |E_tot(t) - E_tot(0)| по energy-файлу (report-level gate)
```

Ориентация частиц должна проходить `check_orientation()` (нормированные
base-vector тройки); иначе кадр невалиден.

## 3. Окно сравнения и статистика

- Окно: **t <= 150000 шагов** (общее кросс-вариантное окно; кадры печатаются
  каждые 4000 шагов: t = 4000, 8000, ..., 148000);
- per-replica: **median** угла по валидным кадрам окна;
- campaign statistic: **median трёх per-replica медиан**;
- bootstrap CI95 (10000 resamples, seed 424242, медиана) — описательный,
  **никогда не tolerance**;
- классификация карточки: `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`
  (`reproduction/REPRODUCTION_RULE_V0_1.md`; машина —
  `nlbl_convention/reproduction_rule.py`), envelope из карточки
  (`reproduction.expected.reference_replica_envelope_deg`).

## 4. Проверка воспроизводителем

```text
# оракул конвенции (обязательное точное совпадение с карточкой):
python3 convention/analyze_hinge.py frame0 --conf MD_Hinges/<v>.conf \
    --topology MD_Hinges/<v>.top --manifest convention/arm-manifest-<v>.json

# анализ реплики (gates + угол + медиана):
python3 convention/analyze_hinge.py run --trajectory <run>_traj.dat \
    --energy <run>_energy.dat --topology MD_Hinges/<v>.top \
    --manifest convention/arm-manifest-<v>.json --variant <v> \
    --seed <seed> --window 150000 --report <run>_analysis.json

# классификация карточки:
python3 convention/analyze_hinge.py campaign --card families/dna_hinge/cards/<v>.card.json \
    --variant <v> --run-jsons r1.json r2.json r3.json
```

## 5. Замороженные манифесты плеч

`arm-manifest-<v>.json` — точные копии frozen манифестов кампании E2
(0b: EX-NL3-002-PROTO-R1; 11b/32b/53b: EX-NL3-002-PARAM-*-R1), включая
происхождение (`inputs`, `algorithm`, `clustering`, `coverage`, `validation`).
Генератор для прозрачности: `convention/run_arm_manifest.py` (не является
частью протокола измерения; измерение использует опубликованные JSON).
Манифест `74b` не публикуется: карточка 74b остаётся NOT_MEASURED/KNOWN_GAP
(arm-manifest-v2 pending) до отдельной ревизии.

## 6. Права

Код и документы convention/ — собственные материалы NanoLab: код Apache-2.0,
документация CC-BY-4.0 (см. RIGHTS.json). Upstream-файлы шарнира —
REFERENCE_ONLY (download-on-run, см. карточки).
