# Work Order NL3-002A — Pre-E2 technical readiness (child of NL3-002)

Статус: PLANNED (draft, ожидает dispatch; parent `NL3-002` = READY). Родитель: NL3-002 «Execute E2 component campaign», стадия NL3, issue #7. Репозиторий: rootfabric/NanoLab. Ветка при dispatch: `work/nl3-002a-pre-e2-r1` от exact fresh `main`.

## Цель

Bounded-пакет, закрывающий технические неопределённости NL3-001 **до** первой динамики E2. Прогоны динамики на данных источника в WO не входят (это следующий дочерний WO кампании NL3-002). Состав:

1. **Compatibility audit**: скрипты `Init_Hinges/` и `pro_CPU.in` (2017) против pinned engine oxDNA `00dc7fb9` (`ENGINE_ENVIRONMENT_R1`) — machine-check каждой опции input-файла против поддерживаемых опций engine; отчёт PASS/GAP по опции (`DNA2`, `salt_concentration = 0.5`, `T = 300K`, CPU/double, `2e7` steps, seed 7777, trap/forces если есть).
2. **Design→topology mapping** (gap G2): детерминированный разбор соответствия «caDNAno design strands → oxDNA topology strands»; объяснение расхождения `118 design paths vs 112 topology strands` (103 linear + 9 circular); классификация каждой ветки (нормальная трансформация / потерянная информация / открытие вопроса); machine-readable JSON-отчёт + человеческая сводка.
3. **Spring/restraint semantics** (связан с gap G3/SI): инвентаризация всех искусственных restraints/forces upstream (design JSON, `pro_CPU.in`); классификация каждого: часть физической модели / только initialization / должен быть выключен в production; явный вывод, с какими forces идёт production run E2 и где это фиксируется. Критично: hinge angle не должен удерживаться внешними spring constraints.
4. **Hinge-angle observable v1**: замороженное определение `trajectory → hinge geometry → angle(t)` **до** любых production данных: atom/base groups, построение координат, units (deg/rad конвенция), degeneracy handling (знак/2π), обработка разрыва конструкции. Источник определения — SI статьи, если доступен; иначе first-principles определение с явной пометкой открытого вопроса U (SI pinning — отдельное owner-решение). Реализация: чистые функции + CLI, stdlib-only, вход = oxDNA trajectory/topology (дайджест-гейт), выход = байт-детерминированный JSON-ряд.
5. **Structural integrity observable v1**: минимальный preregistered набор: `fraction preserved base pairs`, `strand separation` (разрыв связности), `catastrophic displacement` (порог задаётся в E2-PROTO, не здесь); требование: угол обязан сопровождаться integrity, «красивый угол развалившейся конструкции» = невалидный ран по критерию, а не результат.
6. **Synthetic cost probe**: bounded прогон engine на **синтетической** фикстуре (сгенерированной, не содержащей байтов источника) с теми же observables → измеренные wall time / memory / energy на шаг; вход в `measured resource budget` (открытое решение state.json).

Политика неизвестных значений: пороги целостности, `R_confirm`, длины прогонов, tolerances, целевой интервал угла **не назначаются** в этом WO — они freeze'ятся в `E2-PROTO-R1` после пилота и до confirmatory прогонов (Director gate).

## Классы и маршрут

Risk: `MEDIUM` (tooling + audits; научных прогонов нет, научные утверждения не публикуются, E2 остаётся NOT_RUN). Claim class: `C0_SOFTWARE_ONLY`. Маршрут: IMPLEMENTER → независимый REVIEWER → VERIFIER → Director checkpoint. Merge — Human Gate.

**G1 (права источника) не блокирует этот WO**: все разработки и тесты — на синтетических фиксстурах; реальных файлов источника tooling касаться не обязан (а если касаться — только digest-gated user-side download по exact pinned commit, без вендоринга/кэша, как в NL3-001).

## Границы

### Allowed paths
- `docs/work/WO-NL3-002A.md`
- `docs/work/executions/EX-NL3-002A-*/**`
- `docs/work/SESSION_LOG.md` (append)
- `scripts/hinge_family/**` (только аддитивные расширения; замороженные отчёты NL3-001 не менять)
- `scripts/e2/**` (новый замороженный stdlib-only пакет: compat-audit, mapping, restraints, observables, cost-probe)
- `tests/**` (новые unittest-файлы)
- `docs/research/E2_OBSERVABLES_R1.md` (новый файл: определения observables v1; существующие published-документы не трогать)

### Forbidden paths
- `project/state.json`, `project/plan.json` (Director gate)
- `experiments/evidence/**` (кампания E2 не стартовала)
- Любые изменения published-документов (`docs/research/PREREGISTRATION_*`, `E2_SETUP_R1`, `HINGE_FAMILY_R1`, `INPUT_AVAILABILITY`, `SOURCES`, `PROVENANCE_RECOVERY_R1`) — только superseding-ревизией отдельным WO
- `config/control/harness/**`, `scripts/harness/**`, `.github/workflows/**`, direct push `main`, force-push, history rewrite
- **Любые байты upstream-источника `DNA-hinge-simulations`** в Git: `REFERENCE_ONLY`, права UNKNOWN (`G1` — открытое owner-решение); durable-кэш запрещён до отдельного owner-решения (U4)

## Inputs / dependencies

- NL3-001 ACCEPTED: `HINGE_FAMILY_R1.md` (классы REPORTED/OBSERVED/UNKNOWN, гэпы G1–G6, U1–U6), `source_pins.json` (18/18 blob-пинов), `scripts/hinge_family/` (парсеры .top/.conf/caDNAno, детерминированные отчёты), структурное воспроизведение `0b` 8/8 PASS.
- NL1-001 ACCEPTED: pinned engine oxDNA `00dc7fb9` CPU (`ENGINE_ENVIRONMENT_R1`).
- NL0-003 ACCEPTED: `E2-SETUP-R1` — первый шарнир `0b`, decision rule 298 K (статья) vs 300 K (input).
- NL2-003 ACCEPTED: provenance-контракт (дайджесты, readback, машинные timestamps).

## Required outputs

- `scripts/e2/` — замороженный пакет с CLI и байт-детерминированными JSON-отчётами по п.1–3, 5–6 Цели.
- `scripts/e2/observables` — hinge angle + integrity (п.4–5), определение продублировано текстом в `docs/research/E2_OBSERVABLES_R1.md` с явной конвенцией единиц и групп; каждое число определения имеет класс источника (SI-pinned / first-principles + open U).
- `tests/test_e2_*.py`: детерминизм (два вызова → байт-идентичный отчёт), позитив на синтетических траекториях с аналитически известным углом (0°, 45°, 90°), негативы (тампер-байт → digest FAIL; усечённая траектория → FAIL; конструкция развалилась → integrity FAIL; NaN → FAIL).
- Execution-каталог `EX-NL3-002A-R1`: passport, events, отчёты, summary, handoff.

## Validation

- `python -m unittest discover -s tests -t .` → все зелёные (новые + существующие).
- `PYTHONPATH=scripts python -m harness.work_cli validate docs/work/executions/EX-*` → все OK.
- `PYTHONPATH=scripts python -m harness.cli check-consistency` → ok (state/plan не тронуты).
- JSON-гейт: все tracked `*.json` парсятся (кроме ровно designed-NEG-фикстур, зафиксированных CI-пинами).
- Детерминизм: два вызова каждого отчёта → байт-идентичность.
- Cost probe: числа wall time/memory получены измерением, не оценкой.

## Experiments

- None (динамика на данных источника запрещена; синтетический cost probe — технический прогон на сгенерированной фикстуре, уникальный run ID обязателен).

## Resource budget

- CPU: локально, минуты (unit-тесты + один bounded synthetic probe).
- GPU: нет. Paid services: нет.
- Network: по умолчанию не требуется; при необходимости — только бесплатное публичное чтение pinned-объектов GitHub, digest-gated.
- Storage: KB-отчёты в Git; source data в Git не попадает, кэш не создаётся.

## Stop conditions

- Любой published-чек, зелёный до изменения, становится красным → остановка, repair analysis.
- Определение угла из SI недоступно (SI не получен) → честный gap: first-principles определение с пометкой open-U, SI-pinning → отдельное owner-решение; значения не выдумываются.
- Mapping G2 оказывается неоднозначным (потеря информации) → фиксация факта и последствий, кампания не стартует до superseding-решения Director.
- Restraints оказываются частью production-физики upstream → фиксация; вопрос «повторять ли их в E2» выносится в `E2-PROTO` явно, не решается молча.

## Не входит (future WO)

- G1 owner decision + durable-cache policy (владелец; Human Gate перед кампанией).
- SI pinning (запрос к авторам / отдельное решение владельца).
- E2-PROTO freeze (после пилота, Director gate).
- Пилот/confirmatory/параметрическая кампания E2 — следующие дочерние WO родителя NL3-002.

## Checkpoints

START (этот WO + passport + 0001, commit+push до substantive) → CONTINUATION (mapping/restraints/observables по блокам) → VALIDATION (тесты + полный чек-набор) → END (события + summary + handoff).

## Completion

По завершении: exact HEAD/TREE, статусы п.1–6 (DONE/GAP), измеренный budget для пилота, открытые U с местами решения, один next action — независимый REVIEWER; после приёмки NL3-002A — решение владельца по G1 и dispatch пилота кампании.
