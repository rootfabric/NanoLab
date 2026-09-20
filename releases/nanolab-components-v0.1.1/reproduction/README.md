# Reproduction interface (v0.1.1 contract)

Пакет воспроизводится ИЗ ПАКЕТА, без внутренних знаний авторского репозитория
(правило fresh environment, NL5-002).

## Порядок

1. `python3 reproduction/reproduce.py verify` — контроль целостности пакета
   (перерасчёт SHA-256 и размеров по `RELEASE_MANIFEST.json`).
2. `python3 reproduction/reproduce.py plan` — план воспроизведения по карточкам:
   engine pins, шаги, expected-значения, права.
3. Изучите опубликованную frozen конвенцию измерения: `convention/OBSERVABLE_CONVENTION_V0_1.md`;
   frozen манифесты плеч — `convention/arm-manifest-<variant>.json`;
   референс-реализация и оракул — `convention/analyze_hinge.py` (+ `convention/nlbl_convention/`).
   Обязательная самопроверка перед прогонами: `analyze_hinge.py frame0` на upstream-входах
   варианта должен в точности воспроизвести `design.angle_frame0_deg` карточки.
4. Внешний исполнитель сам выполняет шаги карточки в свежей среде:
   download-on-run upstream-входов по exact pinned commit с digest-гейтом
   (см. `RIGHTS.json` и `rights` секции карточек), сборка входов, прогоны
   движка, анализ упакованной конвенцией, численное сравнение с
   `reproduction.expected` по `tolerance_policy`. `durable_cache` запрещён.
5. Расхождение вне заявленной полосы — `REPRODUCTION_MISMATCH` (честный исход,
   сохраняется; не PASS и не скрывается).

## Важно

* `NOT_MEASURED`-карточки (например, `74b` в этом примере) не содержат
  значений для воспроизведения — выдумывать их запрещено; arm manifest для
  74b не публикуется.
* Окно анализа задаётся шагом 4 карточки (`--window`): 0b — 200000
  (basis: confirmatory 200k), 11b/32b/53b — 150000 (basis: параметрическая
  серия, общее окно).
* В v0.1.1 относительно v0.1.0 добавлена публикация frozen конвенции
  (`convention/`), URL и tarball-путь исходников движка, корневой README и
  пояснение overlay-параметров реплики. Научные значения карточек
  (expected/envelopes/пороги) не изменялись. `reproduction/reproduce.py`
  helper: stdlib-only.
