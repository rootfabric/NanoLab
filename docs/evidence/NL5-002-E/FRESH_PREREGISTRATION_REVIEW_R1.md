# NL5-002-E/FRESH_PREREGISTRATION_REVIEW_R1 — Fresh independent review of WO-NL5-002-E-R1 preregistration

```text
REVIEW_ID         = NL5-002-E/FRESH_PREREGISTRATION_REVIEW_R1
REVIEW_VERDICT    = PASS
REVIEW_DATE_UTC   = 2026-09-20T11:18:24Z (real `date -u` при записи)
REVIEWED_WO       = docs/work/WO-NL5-002-E-R1.md
REVIEWED_WO_COMMIT = 4d6542fda81084dced2578f3e008c8c8e0705a5a
                    (origin/control/nl5-002-terminal-decision-r1; exact HEAD сверен
                     `git rev-parse origin/control/nl5-002-terminal-decision-r1` после
                     свежего `git fetch origin --prune`)
REVIEWED_WO_TREE  = 7651569ac8d0e93c0cc7614cb692945ad5bd0c98
ROLE              = REVIEWER (fresh independent session; scientific preregistration review)
RISK              = HIGH (protocol/observable/analysis/claim) → Reviewer + Verifier + Director
CLAIM CEILING     = C1_COMPUTATIONAL_REPRODUCTION — не меняется этим review и не меняется
                    самим WO (изучение platform-чувствительности не поднимает claims карточек)
```

## Заявление о независимости

Данная сессия — fresh independent REVIEWER, не участвовавшая в подготовке
`WO-NL5-002-E-R1`, в кампаниях B-R1/B-R2/C/C2, в Director-решении
`DIRECTOR_DECISION_R1` и ни в одном предыдущем review/verify NL5-002. Вердикты
предыдущих агентов не наследовались; каждый факт, на который опирается этот вердикт,
проверен механически из git-объектов exact commit'а `4d6542f` (или указан ниже как
контекст без опоры на него). Verifier-проверка этого preregistration — отдельная
fresh единица и данным документом не заменяется.

## Предмет review

Preregistration-содержимое exploratory WO `WO-NL5-002-E-R1` (PLATFORM-SENSITIVITY-R1)
в состоянии freeze-before-data на exact commit `4d6542f`. Проверялись: границы научного
вопроса, гипотезы, определения платформ, frozen seed-лист, план реплик, статистический
план, decision rule, бюджеты/stop conditions, запреты (сохранение R1), внутренняя
согласованность, соответствие canonical disposition (`DIRECTOR_DECISION_R1.md`,
Дополнение 3). Это review preregistration-документа (paper check): прогонов не
выполнялось, данные не просматривались, статистический план не пересчитывался на числах.

## Checklist 1–12: проверенные факты и вердикты

### 1. Научный вопрос ограничен — PASS

Факт: раздел «Научный вопрос (один)» содержит ровно один preregistered вопрос — насколько
велика platform-зависимость распределений median-угла 0b/32b относительно intrinsic
seed-вариабельности при идентичном frozen protocol. Причинная часть («почему») явно
выведена за пределы вердикта: «Причина MISMATCH заранее НЕ заявляется. Кандидаты-механизмы
… — предмет интерпретации ПОСЛЕ данных, не часть вердикта». Вопрос exploratory: документ
прямо запрещает трактовать его как «дожать R1 до MATCH» («не пытается „дожать“ R1 до MATCH
и не пересматривает R1»). Scope creep отсутствует: variants, platforms, seeds, статистика,
бюджеты — всё заморожено в этом же документе.

### 2. H0/H1 заморожены, взаимоисключающие, измеримые — PASS

Факт: H0 = platform shift мал относительно intrinsic seed variability; H1 = systematic
shift, сравнимый или больше seed variability. Оба операционализируемы через frozen
статистический план (`shift_v`, `ratio_v`, bootstrap CI). Взаимоисключаемость: предикаты
«shift мал» и «shift сравним или больше» несовместимы по построению; отображение на
decision rule (см. п. 8) даёт непересекающиеся классы SENSITIVE (≈H1-supported) и
INSENSITIVE (≈H0-consistent), третий класс INCONCLUSIVE — честный «ни то, ни другое».
Примечание (не дефект): часть формулировки H1 в скобках «(согласованный по знаку между
0b и 32b направлениями, наблюдёнными в R1)» — контекстная ссылка на наблюдение R1, а не
дополнительный критерий вердикта; binding-критерием является только frozen decision rule
п. 3 статистического плана, который sign-consistency не требует.

### 3. Определения платформ конкретны и проверяемы — PASS

Факт (из WO): P1 = author/reference environment WSL2 Ubuntu 24.04.2, gcc 13.3.0
(`ENGINE_ENVIRONMENT_R1`); P2 = Ubuntu 22.04, gcc 11.4, Xeon E5-2698 v3 — платформа B-R2;
P3 = optional третья независимая Linux/compiler/runtime среда, включается отдельным
CONTINUATION до данных этой платформы. Требование fingerprint: «Environment fingerprint
каждой платформы фиксируется до прогонов (ОС, compiler, версии runtime, CPU, настройки
FPU если доступны)». Перекрёстная сверка с git: `ENGINE_ENVIRONMENT_R1` = «WSL2 Ubuntu
24.04.2, gcc 13.3.0, cmake 3.31.6 user-local» (`docs/work/WORK_QUEUE.md`, NL1-001
ACCEPTED); P2 подтверждена артефактами B-R2
`docs/work/executions/EX-NL5-002-B-R2/evidence/env/environment_fingerprint.txt`
(«Intel(R) Xeon(R) CPU E5-2698 v3», «gcc (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0»).
Требование fingerprint до прогонов согласуется с практикой B-R2, где такой файл
публиковался.

### 4. Seed-лист заморожен, перекрытия отсутствуют — PASS (пересчитано независимо)

Факт: 10 seeds S001..S010, сгенерированы и заморожены 2026-09-20 до любых прогонов.
Независимый механический пересчёт (python, этот review):

```text
S001=1259289227 S002=1358106528 S003=1524307444 S004=601855227 S005=274288237
S006=972234272  S007=1934775205 S008=1747973984 S009=880427736  S010=744386736

count = 10; distinct = 10/10 (все различны)
все > 0; все < 2^31 (max 1934775205 < 2147483647) → валидные положительные int32
overlap c reference {201004,202008,203012}:            ПУСТО
overlap c B-R1 {510101,520202,530303}:                 ПУСТО
overlap c B-R2 {174329,285637,396421,410273,507283,520931,618457,638257,729613,741953,852607,963541}: ПУСТО
overlap c E3/E3-reval {201004,202008,203012,204016,205020,206024}: ПУСТО
итоговое пересечение со всеми историческими множествами: ПУСТО
```

Исторические множества взяты из evidence-файлов в git, а не из текста миссии:
`docs/work/executions/EX-NL5-002-B-R1/evidence/frozen_seeds.json` (все 4 варианта =
{510101,520202,530303}), `docs/work/executions/EX-NL5-002-B-R2/evidence/seeds_frozen.json`
(0b={410273,520931,638257}, 32b={174329,285637,396421}, 53b={507283,618457,729613},
11b={741953,852607,963541}); E3/E3-reval/revalidation seeds 201004/202008/203012 +
204016/205020 (+206024 из NL4-003 revalidation) подтверждены
`docs/work/executions/EX-NL4-002-E3-REVAL-R1/` и `docs/work/WORK_QUEUE.md`.
Fresh-seed требование явно зафиксировано: «переиспользование run ID и seed'ов предыдущих
кампаний для новых прогонов запрещено; failed run ID не переиспользуются».

### 5. Реплики: n≥8, цель n=10, paired design — PASS

Факт: «Minimum: n = 8 fresh seeds / variant / platform; целевой бюджет: n = 10»; «Один и
тот же seed list используется на всех платформах → paired comparison». Минимум n=8 на
cell (platform × variant), одинаковый frozen список на всех платформах — paired-план
(разности per-seed) корректен; требование миссии выполнено.

### 6. Bootstrap-план конкретен — PASS

Факт (§Frozen статистический план, п.1): primary = paired
`shift_v = median_i( median[P2, seed_i] − median[P1, seed_i] )` для v ∈ {0b, 32b};
bootstrap 95% CI разности, percentile method, 10 000 resamples, bootstrap RNG seed
frozen = 902107. Все четыре параметра (метод, уровень, число ресемплирований, RNG seed)
зафиксированы до данных. Значение 902107 не пересекается с историческими seed-множествами
(п.4) и не является engine-seed — отдельный статистический RNG.

### 7. Effect-size rule вычислим — PASS (с оговоркой-рекомендацией)

Факт: `ratio_v = |shift_v| / within_v`, где `within_v = median по платформам (MAD per-seed
median внутри платформы)`. Для двух платформ `within_v = (MAD_P1 + MAD_P2)/2` (медиана
двух значений); при включении P3 — медиана трёх. Все входы (per-seed medians, попарные
разности, внутриплатформенные MAD) вычислимы из frozen плана измерений; определение
однозначно задаёт классификацию при `within_v > 0`. Оговорка (→ ограничения): документ не
уточняет (а) конвенцию MAD (raw median(|x−median|) vs scaled ×1.4826) и (б) вырожденный
случай `within_v = 0` (все per-seed medians внутри обеих платформ идентичны — вероятность
нулевая для непрерывных измерений, но формально не определена; 0/0 при ещё и `shift_v=0`).
Оба пункта рекомендуется зафиксировать точной формулой в passport `EX-NL5-002-E-R1` на
START (до данных) — это не меняет freeze-before-data и не требует новой revision WO,
поскольку выбор конвенции фиксируется до любых прогонов.

### 8. Согласованность decision rule (критический пункт) — PASS (доказано)

Формализация frozen правила per variant. Обозначим A = «bootstrap 95% CI shift_v не
содержит 0», R = `ratio_v` (R ≥ 0 по построению). Тогда:

```text
SENSITIVE     = A ∧ (R ≥ 1)
INSENSITIVE   = ¬A ∨ (R < 0.5)
иначе         = INCONCLUSIVE
```

Теорема 1 (взаимная исключённость). SENSITIVE ∧ INSENSITIVE
= (A ∧ R≥1) ∧ (¬A ∨ R<0.5)
= (A ∧ R≥1 ∧ ¬A) ∨ (A ∧ R≥1 ∧ R<0.5)
= ∅ ∨ ∅ = ∅,
поскольку A ∧ ¬A = ∅ и (R ≥ 1) ∧ (R < 0.5) = ∅. Оба статуса никогда не выполняются
одновременно. (Дополнительно проверено механическим перебором 26 граничных случаев,
включая R ∈ {0.4999, 0.5, 0.5001, 0.9999, 1.0, 1.0001}: совпадений нет.)

Теорема 2 (полное разбиение). Для любой пары (A, R) ровно один класс:
1. ¬A (CI содержит 0)                → INSENSITIVE  (первая дизъюнкция);
2. A ∧ R < 0.5                       → INSENSITIVE  (вторая дизъюнкция);
3. A ∧ 0.5 ≤ R < 1                   → INCONCLUSIVE (не SENSITIVE, т.к. R<1;
                                        не INSENSITIVE, т.к. A и R≥0.5);
4. A ∧ R ≥ 1                         → SENSITIVE.
INCONCLUSIVE возникает в точности тогда, когда CI исключает 0, а эффект лежит в
серой зоне 0.5 ≤ ratio < 1. Границы согласованы: R = 1 → SENSITIVE (не INCONCLUSIVE);
R = 0.5 → INCONCLUSIVE (не INSENSITIVE); оба порога включены в классы ровно один раз.

WO-level агрегация: «PLATFORM_SENSITIVE — если 0b И 32b sensitive; PLATFORM_INSENSITIVE —
если оба insensitive; иначе INCONCLUSIVE». Каждый variant попадает ровно в один из трёх
классов, поэтому правило — тотальная функция на 3×3 = 9 комбинациях (проверено
механически): S+S → PLATFORM_SENSITIVE (1 комбинация); I+I → PLATFORM_INSENSITIVE
(1 комбинация); остальные 7 комбинаций (включая смешанную S+I) → INCONCLUSIVE.
Двусмысленностей нет.

Контроли и 74b: «Controls: 11b, 53b — опционально, analysis-only, на классификацию
WO-level НЕ влияют»; primary и decision rule определены только для v ∈ {0b, 32b};
WO-level агрегация использует только эти два варианта — контроли не могут изменить
вердикт. 74b: «ЗАПРЕЩЁН (NOT_MEASURED / KNOWN_GAP, arm-manifest-v2 — отдельный будущий
WO)» и в запретах «НЕ производить значения 74b» — воспроизводится дважды, запрещён
однозначно.

### 9. Бюджеты и stop conditions ограничены и честны — PASS

Факт: CPU-only, no paid/GPU; окна шагов 0b = 200k, 32b = 150k — сверены с evidence R1
(B-R2: «окна по карточкам 0b 200000/11b-32b-53b 150000»,
`EX-NL5-002-B-R2/events/0001-external-executor-r2-dispatched.json`; подтверждено
`window_steps` в analysis-артефактах B-R2). Объём ~40 прогонов = n=10 × 2 variants ×
2 platforms (арифметика верна; P3 опционально +20 — арифметика верна). Wall ≤ 72 ч на
платформу при калибровке B-R2 (~10–14 ч/replica single-thread, 13.8 h wall на 12 реплик
с параллелизмом) — бюджет реалистичен и ограничен. Stop conditions: environment
недоступна → BLOCKED_ENVIRONMENT; ≥2 seeds систематически падают в одной ячейке →
честная классификация FAILED_TECHNICAL/INCONCLUSIVE без «подгонки»; превышение бюджета →
остановка и checkpoint. Все три исхода честные (не принуждают MATCH), технический
terminal event отделён от научного вывода согласно EXPERIMENT_HARNESS_RU.md.

### 10. Отсутствие ретроактивной реинтерпретации R1 — PASS

Факт: (а) «Старый MISMATCH остаётся навсегда валидным результатом R1»; (б) запреты
дословно: «НЕ менять NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE и threshold'ы R1», «НЕ
переписывать/переклассифицировать R1 (B-R1 INCONCLUSIVE+PORTABILITY_FINDING, B-R2
MISMATCH)», «НЕ добавлять replicas до MATCH и не перезапускать R3 автоматически», «НЕ
производить значения 74b», «platform study сам по себе НЕ закрывает NL5 и НЕ меняет NL5
acceptance». Parent-строка фиксирует NL5-002 = terminal MISMATCH, WAITING_HUMAN —
идентично canonical disposition. Frozen envelope R1 не упоминается как объект изменения
ни в одной секции.

### 11. Внутренняя согласованность документа — PASS

Факт: variants-список согласован между секциями (Primary 0b/32b — те же варианты в
статистическом плане и в вопросе; controls 11b/53b analysis-only; 74b запрещён);
бюджетная арифметика сходится (~40 = 10 × 2 × 2; P3 +20); выход `EX-NL5-002-E-R1`
соответствует WO id и требует passport + START до прогонов + CONTINUATION по платформам +
END_EXECUTION/END_ANALYSIS + отдельные REVIEW/VERIFY — совпадает с обязательными
checkpoint'ами EXPERIMENT_HARNESS_RU.md; WO id/parent/claim ceiling согласованы
(WO-NL5-002-E-R1, parent NL5-002 terminal MISMATCH, C1). Противоречий между секциями не
обнаружено. WO соответствует PRE_REGISTERED-перечню EXPERIMENT_HARNESS_RU.md: question,
hypotheses, claim ceiling, environment, observables/units, analysis method, comparison
rule, seed/replica policy, resource budget, stop conditions — присутствуют; exclusion
rule представлен через stop conditions/integrity metrics; известные ограничения — в
«Явные зависимости» и «Возможные outcomes».

### 12. Соответствие canonical disposition (DIRECTOR_DECISION_R1, Дополнение 3) — PASS

Факт: `docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md` @4d6542f, Дополнение 3, фиксирует
`HUMAN_GATE_PLATFORM_SENSITIVITY_PREPARATION = APPROVED` и выбранную владельцем
последовательность: «fresh Scientific Reviewer preregistration → fresh Verifier
preregistration → Director freeze record docs/evidence/NL5-002-E/PREREGISTRATION_FREEZE_R1.md
→ только затем возможные прогоны (P1/P2, n≥8; 74b запрещён); v0.1 envelope и R1 MISMATCH
не пересматриваются этим WO». WO дословно воспроизводит эту последовательность в секции
«Статус» (review → verify → Director freeze → прогоны) и те же запреты. Противоречий
WO с canonical disposition нет: WO ничего не закрывает, NL5 acceptance не объявляет,
NL6-001/E5 не трогает, P3 оставлен открытому вопросу владельца (совпадает с «открытые
вопросы» Дополнения 3). Отмечу: данный документ и есть первый шаг этой
owner-утверждённой последовательности.

## Negative/boundary проверки

- Добавление реплик после просмотра данных: НЕ допускается. Seed/replica policy заморожена
  в документе до данных («frozen в этом документе до данных»), запрет «НЕ добавлять
  replicas до MATCH», план п.4: «Изменение этого плана после просмотра данных запрещено
  (иначе — новая revision WO)». Цель n=10 фиксирована заранее; механизм «добавим ещё
  seeds, если не понравится CI» отсутствует.
- Изменение статистического плана после данных: НЕ допускается — явный запрет п.4
  frozen статистического плана + секция «Статус» (научное содержимое после этого коммита
  не меняется; любые правки = новая revision WO). Согласуется с HARNESS_REVIEW_AND_EVIDENCE_RU.md
  («Запрещено менять threshold после просмотра результата без новой protocol revision»).
- Секция «Возможные outcomes и их последствия» vs decision rule: согласованы один-в-один —
  три исхода (PLATFORM_SENSITIVE / PLATFORM_INSENSITIVE / INCONCLUSIVE) с последствиями
  (основа для НОВОЙ protocol revision v0.2 через отдельный preregistration / иное
  объяснение через отдельный analysis WO / честная фиксация и расширение только новым
  bounded WO) не добавляют четвёртого класса и не подменяют критериев; в частности
  SENSITIVE ведёт только к проектированию новой ревизии протокола, а не к признанию
  воспроизведения.

## Ограничения и оставшиеся риски

1. Конвенция MAD не pinned в тексте WO (raw vs ×1.4826) — влияет на пороги ratio 0.5/1.
   Рекомендация: зафиксировать точную формулу (и поведение при within_v = 0) в passport
   EX-NL5-002-E-R1 на START, до данных.
2. Вырожденный случай `within_v = 0` (включая 0/0) не определён — вероятность нулевая для
   непрерывных измерений, но формальную конвенцию стоит задать заранее (та же
   рекомендация, что в п.1).
3. P3 (опциональная третья платформа) — availability не решена (явный открытый вопрос
   владельца в Дополнении 3); WO корректно допускает работу без P3 и требует отдельного
   CONTINUATION до данных P3.
4. P1 (author env) доступ предполагается «как в B-R2», но фактически прогоны NL5-002
   выполнялись только на P2; подтверждение доступности P1 — обязательный пункт при
   dispatch (иначе stop condition BLOCKED_ENVIRONMENT по frozen правилу).
5. При частичном исполнении (например, 8 из 10 seeds на одной платформе) подмножество
   пар для paired-анализа в тексте не детализировано; подмножество должно быть
   документировано в CONTINUATION до анализа (механизм freeze-before-data это покрывает,
   но явно зафиксировать правило — гигиена).
6. H1 содержит контекстную отсылку к знаковой согласованности 0b/32b из R1, не
   превращённую в критерий вердикта; интерпретатор должен читать binding-критерием только
   frozen decision rule (см. п.2 checklist).
Все пункты — рекомендации/риски уровня исполнения, не дефекты замороженного научного
содержимого; ни один не делает план некорректным или допускающим post-hoc манипуляцию.

## Вердикт

```text
REVIEW_VERDICT = PASS
```

Все 12 пунктов checklist выполнены; критическая согласованность decision rule доказана
аналитически и подтверждена механическим перебором; seed-перекрытия отсутствуют
(пересчитано независимо из evidence-файлов git); ретроактивная реинтерпретация R1
исключена текстом документа; WO согласован с canonical disposition NL5-002.
Допустимые следующие шаги по owner-последовательности: fresh Verifier preregistration →
Director freeze record `docs/evidence/NL5-002-E/PREREGISTRATION_FREEZE_R1.md` →
только затем прогоны EX-NL5-002-E-R1. Claim ceiling C1_COMPUTATIONAL_REPRODUCTION —
без изменений.
