# EXTERNAL_REPRODUCTION_REPORT_TEMPLATE_R1 (Appendix B к WO-NL5-002-A-R1)

Статус: FROZEN до dispatch фазы B (WO-NL5-002-A-R1). Заполняется внешним
исполнителем целиком; пропущенные секции помечаются `N/A` с причиной.
Язык отчёта — любой, но имена полей/классификаций сохраняются как есть.

## 1. Executor identity & independence statement

- agent/session type (что вы собой представляете);
- что было доступно как вход (полный список), что было недоступно/закрыто;
- физический хост: тот же/другой (честно); рабочая область: путь;
- пересечения с авторской средой, если известны.

## 2. Environment fingerprint

- OS/kernel; gcc/g++/make/cmake/python версии; CPU/RAM;
- способ сетевого доступа (proxy/direct), timestamp начала/конца.

## 3. Package integrity

- вывод `reproduction/reproduce.py verify` (полный);
- сверка VERSION; любые предупреждения.

## 4. Engine build provenance

- commit pin (из карточек), repo URL, где взят;
- build команды/флаги/warnings; факт double precision/CPU;
- путь сборки; затраченное время.

## 5. Upstream inputs (download-on-run)

- для каждого файла: URL/commit/путь, ожидаемый size+blob_sha1 (из пакета),
  вычисленные значения, verdict gate (PASS/FAIL), timestamp;
- подтверждение отсутствия durable-кэша.

## 6. Frozen seeds

- по вариантам 0b/11b/32b/53b: три seeds, время фиксации, проверка != reference.

## 7. Runs (12 записей)

Для каждой реплики: run ID (формат EXTERNAL-<variant>-<номер>), variant, seed,
steps, полная команда запуска, exit code, wall time, выходные файлы + sha256/size,
примечания (включая неудачные/повторные попытки — отдельными ID, без переиспользования).

## 8. Analysis

- как реализована конвенция угла; какие элементы конвенции были доступны из
  пакета, каких не хватило (`PORTABILITY_FINDING` — подробно);
- frame-validity: какие gates применены (по published данным пакета), что
  недоопределено;
- per-replica: n_valid_frames, median_deg в окне t<=150000;
- campaign statistic = median трёх per-replica medians;
- (опционально, descriptive) bootstrap CI95 10000/424242;
- всё best-effort помечается `BEST_EFFORT_NOT_CONTRACT`.

## 9. Per-card classification

| variant | campaign statistic | envelope (из карточки) | classification (MATCH/MISMATCH/INCONCLUSIVE) | примечание |
|---|---|---|---|---|
| 0b  |  |  |  |  |
| 11b |  |  |  |  |
| 32b |  |  |  |  |
| 53b |  |  |  |  |
| 74b | N/A — NOT_MEASURED/KNOWN_GAP, значения не производились | — | — |  |

## 10. Deviations

Любые отступления от шагов карточек/этого протокола: что, почему, влияние на
сравнимость. Пустая секция = «отклонений нет» (осознанно подтвердить).

## 11. Artifact manifest

JSON-массив: {path, sha256, size, producer} для всех сохранённых артефактов
(логи, конфиги, траектории, energy, analysis JSON, отчёт).

## 12. WO-level verdict self-assessment (non-binding)

Один из: `REPRODUCED | REPRODUCED_WITH_DEVIATION | INCONCLUSIVE |
FAILED_TECHNICAL | MISMATCH` + обоснование по опубликованным правилам.

## 13. Findings

Нумерованный список findings (portability/документация/интерфейс пакета),
включая friction, не повлиявший на результат.
