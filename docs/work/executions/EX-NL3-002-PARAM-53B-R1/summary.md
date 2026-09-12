# EX-NL3-002-PARAM-53B-R1 — Summary (IMPLEMENTER handoff)

Вариант **53b** параметрической серии E2 (WO-NL3-002-PARAM; frozen `E2_PROTO_R1` наследован без изменений, вкл. addendum §8: **steps = 150000**). scientific_outcome = **MEASURED**; интерпретаций и кросс-вариантных сравнений нет (Director после всех батчей).

## Входы (G1 = B, digest-gated, вне Git, U4 = NO после исполнения)

- `MD_Hinges/53b.top` 124872 B, blob `171fcb41…` — PASS; sha256 вычислен при первой загрузке `880d0945…` (пин NOT_VERIFIED, без претензии к реестру).
- `MD_Hinges/53b.conf` 2379246 B, blob `74fb9738…` — PASS; sha256 `42214bfd…` (аналогично).
- `MD_Hinges/pro_CPU.in` 933 B — полный пин PASS (`89d76310…` / `bd6cd418…`).
- Отклонения от pro_CPU.in — ровно протокольные (steps 150000 / seed / имена outputs / print_conf_interval 4000 / print_energy_every 100 / lastconf_file + subject 74b→53b): `evidence/PARAM-53B-S00X_deviations.json`. Все входы скопированы в каталоги ранов и byte-verified.

## Манифест рук 53b (ДО прогонов; arm-manifest-v1, байт-детерминизм ×2, sha256 `8e58eb89…`)

- Два доминирующих блока — **PASS** (threshold 0.95; ядра 1386/986; second/third ≈ 7.04 ≥ 3.0).
- **arm_a 4318 нт / arm_b 3638 нт**; coverage 7956/7956 парных = 100% (91.49% топологии 8696 нт); greedy pair graph 3978 пар.
- Угол frame 0 = **132.95°** (конвенция [0,180]).

## Runs (PARAM-53B-S001..S003; seeds 201004/202008/203012; oxDNA 00dc7fb9 CPU/double; setsid/nohup, watchdog не сработал)

| Run | exit | wall | s/step | energy строк | кадров | valid |
|---|---|---|---|---|---|---|
| S001 | 0 | 7904 s (2.20 ч) | 0.0527 | 1501/1501 | 37 | 37/37 |
| S002 | 0 | 7816 s (2.17 ч) | 0.0521 | 1501/1501 | 37 | 37/37 |
| S003 | 0 | 7656 s (2.13 ч) | 0.0510 | 1501/1501 | 37 | 37/37 |

Бюджет ≤ 3.5 ч/реплику — PASS без прерываний. Крэшей нет. Траектории вне Git (`/home/yurig/nl3-002-param-53b/runs/PARAM-53B-S00X/`), манифесты SHA-256+size+location — `evidence/s00X-artifacts.manifest.json`.

## Observables (v2 mutual-nearest frozen; reference pairs frame 0: 3256–3277)

Гейты §4 все PASS на всех кадрах: lbf_max 0.0577–0.0585 (порог 0.1078); pf_v2_min 0.980–0.985 (порог 0.50); disp_max 12.54–13.89 (порог 20.0). **0 невалидных кадров из 111.** Energy drift max_abs_total 0.0061–0.0088.

## Углы (градусы, [0,180]; валидные кадры; bootstrap 10000, seed 424242)

| Выборка | n | median | IQR | q5–q95 | CI95 median |
|---|---|---|---|---|---|
| S001 | 37 | 132.34 | [131.46, 132.99] | [131.14, 133.77] | [131.53, 132.79] |
| S002 | 37 | 131.05 | [130.58, 131.48] | [130.07, 132.02] | [130.81, 131.38] |
| S003 | 37 | 135.29 | [134.42, 135.80] | [133.23, 136.16] | [134.65, 135.74] |
| Пул | 111 | 132.36 | [131.31, 134.41] | [130.49, 135.92] | [131.78, 132.99] |

## Итог

- Execution COMPLETED: 3/3 реплик exit 0, полные 150000 шагов; digest-гейт 3/3 PASS; манифест рук PASS (два доминирующих блока).
- scientific_outcome = MEASURED; распределения зафиксированы в evidence; интерпретация/сравнение вариантов — вне этого исполнения.
- Branch `work/nl3-002-param-53b-r1` (base `bdbebfd`); state.json не менялся; merge — Human Gate.
- Next: dispatch батча 74b → батчевый REVIEWER серии (11b/32b/53b/74b) → Director.
