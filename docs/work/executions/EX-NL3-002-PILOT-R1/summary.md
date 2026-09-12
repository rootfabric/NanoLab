# EX-NL3-002-PILOT-R1 — summary (NL3-002-PILOT, E2 pilot, non-confirmatory)

**Класс**: C0_SOFTWARE_ONLY / scientific_outcome = NOT_EVALUATED. Это калибровочные прогоны (стоимость/стабильность/smoke observables) — НЕ научная кампания; E2 остаётся NOT_RUN; научные claim'ы не публикуются.

## Что делалось

Первые прогоны динамики на реальном первом шарнире `0b` (digest-gated download-on-run, G1=B, без durable-кэша; все 3 пина size+blob_sha1+sha256 PASS):

1. **Rate measurement** `E2-PILOT-RATE`: 500 steps, seed 101001, exit 0, wall 25.93 s (вкл. WSL startup + загрузку 8378-частичного конфига) → per-step ≤ 0.0519 s.
2. **Выбор steps** (preregistered процедура): 24000 (≈20.8 мин прогноз), print_conf_interval 400 (60 кадров), print_energy_every 100.
3. **3 реплики** (параллельные WSL-процессы), steps 24000:
   - `E2-PILOT-S001` (seed 101001): exit 0, wall 1441.16 s, 0.0600 s/step
   - `E2-PILOT-S002` (102002): exit 0, wall 1447.95 s, 0.0603 s/step
   - `E2-PILOT-S003` (103003): exit 0, wall 1449.27 s, 0.0604 s/step
4. **Analysis** (non-confirmatory, sampling; ≤15 кадров/реплика):
   - Energy: total first→last: S001 −1.1822→−1.1844, S002 −1.1845→−1.1800, S003 −1.1851→−1.1844; max|drift| ≤ 0.0056 — стабильно.
   - Integrity v1: long_bond_fraction max 0.0557/0.0553/0.0561 (уже ≈0.054 в frame 0 — свойство авторского init-конфига vs BOND_D_MAX=1.0, не динамика); displacement_max 6.25/5.53/6.95; reference pairs всего 26–29 на 8378 нуклеотидов (frozen window [0.05, 0.55]), pairs_fraction к концу 0.12/0.24/0.12.
   - DRAFT-proxy PCA угол (arm_a=[0,2132], arm_b=[2133,4265]; **DRAFT proxy, non-confirmatory, not the E2-PROTO manifest**): first/last 178.67/178.29, 178.72/178.50, 178.62/178.41 deg.
5. **Аддитив**: `scripts/e2/observables.py::reference_pairs_bucketed` (эквивалент naive, `tests/test_e2_pilot.py` 4 OK; определение observables не менялось).

## Ресурсы

Общий calendar wall ≈ 50 мин (бюджет ≤ 3 ч). Per-step ~0.06 s при 3 параллельных → 2e7 steps × 3 реплики ≈ 1e6 s engine wall на этом хосте (только budgeting для E2-PROTO-R1; 2e7 НЕ запускались).

## Чеки

work_cli validate/close ok; harness.cli check-consistency ok; unittest discover 231 OK (1 skip). Артефакты в WSL `/home/yurig/nl3-002-pilot/runs/` (вне Git), манифесты SHA-256+size в evidence/. Временные исходники источника удалены (U4=NO).

## Открытые наблюдения (вход в E2-PROTO-R1, не выводы)

- Init-конфиг автора даёт lbf≈0.054 против BOND_D_MAX=1.0 — нужен tolerance-анализ.
- Reference-pairs window [0.05, 0.55] на авторском init даёт лишь 26–29 пар — candidate для пересмотра observables-параметров в E2-PROTO freeze (до confirmatory).
- Движок 00dc7fb9 на 2017-input (0b.top/0b.conf/pro_CPU.in) работает без сбоев совместимости.

## Next

REVIEWER (fresh-сессия) на exact HEAD `work/nl3-002-pilot-r1` → Director → merge (Human Gate). После — E2-PROTO-R1 freeze и confirmatory кампания.
