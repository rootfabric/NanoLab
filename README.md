# NanoLab

**Открытая AI-лаборатория проектирования и вычислительной проверки наноструктур, нанокомпонентов и, в перспективе, наномашин.**

Миссия — сделать накопленные научные знания и вычислительные инструменты доступными для одного исследователя с ИИ. Даже небольшой воспроизводимый результат, полезный другим, считается значимым вкладом: исправленный анализ, открытый протокол, надёжный компонент или честный отрицательный результат.

## Текущее состояние

```text
CURRENT FRONTIER = NL5
NL5-002 = WAITING_HUMAN (external reproduction terminal MISMATCH, verified; disposition — Human Gate)
E0 = RUN · E1 = SUPPORTED · E2 = RUN · NL4 = MVP COMPLETE · NL5-001 = ACCEPTED
```

**Научная стадия `NL5` в работе. `NL5-001` принят (2026-09-18): библиотека и release-пакет `nanolab-components 0.1.0` опубликованы — family/variant cards (0b/11b/32b/53b измерены; 74b honest gap), machine-readable schema, protocols, provenance, reproduction, rights, citation/version, детерминированный release manifest; лицензии финализированы owner-решением D2 (код Apache-2.0; документация + derived data CC-BY-4.0; сторонние права не перелицензованы). Clean release reproduction NL5-001-C: 0b/32b/53b MATCH, 11b INCONCLUSIVE, 74b NOT_MEASURED/KNOWN_GAP (frozen NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE; claim не повышен). Стадия `NL4` закрыта ранее: AI NanoLab MVP собран и верифицирован clean-room'ом; NL4-001/002/003 приняты после батчевого Reviewer; claimed-скор ИИ E3 аннулирован anti-bias re-validation (честный negative-on-advantage). Стадия `NL3`: параметрика измерена (0b 65.98° [65.67, 66.32]; 11b 73.93°; 32b 78.09°; 53b 132.36°).** Канонические статусы: [project/state.json](project/state.json), сводка приёмок: [WORK_QUEUE](docs/work/WORK_QUEUE.md). `NL5-002` исполнен (2026-09-19): внешний reproduction пакета v0.1.1 дал terminal **MISMATCH** (0b/32b вне frozen envelopes, 11b/53b MATCH; Fresh Reviewer + Verifier PASS; threshold tuning отсутствует) — NL5 acceptance не объявлен, disposition у владельца ([DIRECTOR_DECISION_R1](docs/evidence/NL5-002/DIRECTOR_DECISION_R1.md)). Карточка компонента 0b: [EX-NL3-002-SUMMARY-R1](docs/work/executions/EX-NL3-002-SUMMARY-R1/evidence/component-card-0b.md), протокол E2: [E2_PROTO_R1](docs/research/E2_PROTO_R1.md).

С 8 сентября 2026 года проект использует собственный development/experiment harness, адаптированный из `rootfabric/distributed-world-simulator`: [PROJECT_CONTROL](PROJECT_CONTROL.md), [HARNESS_CONTROL](HARNESS_CONTROL.md), [Experiment Harness](docs/control/EXPERIMENT_HARNESS_RU.md). `main` является каноническим project state; рабочие ветки обязаны сохранять начало, продолжение и завершение работы в Git.

Параллельно научной линии ведётся отдельный [INFRA track](docs/infra/README.md): safe CI → self-hosted CPU → reproducible executor → artifact store → GPU → scheduler/AiiDA → HPC. Статус: `INFRA0–INFRA1` приняты, frontier `INFRA2-001` (self-hosted CPU executor). INFRA предоставляет вычислительные возможности, но по умолчанию не является hard gate научной дорожной карты и не владеет scientific truth. Git Task Bus: пилот `BUS-SMOKE-001` завершён как `COMPLETED_SANDBOX` (не ACCEPTED); P2 production activation заблокировано до отдельного owner-решения.

## К чему идём

```text
Воспроизводимый эксперимент
  → структура с измеренными свойствами
  → компонент с заданной функцией
  → управляемый механизм
  → система с энергоснабжением и обратной связью
  → специализированная наномашина
```

Наноэлектроника, новые материалы и более эффективные вычислительные системы — долгосрочные направления. Они не теряются при выборе первого MVP. Мы не обещаем универсального наноробота, гарантированной изготовимости или конкретного срока достижения этих целей.

## Первый полезный продукт

**DNA Nanomechanics Lab:** взять проверенную конструкцию ДНК-шарнира, изменять ограниченный набор параметров, вычислять распределение угла раскрытия и сохранность структуры, сравнивать варианты и выдавать воспроизводимый отчёт.

ИИ организует исследование. Физические движки считают. Отдельные проверки решают, что результат действительно позволяет утверждать. Сначала эталон воспроизводится без ИИ, затем измеряется вклад агента относительно простых алгоритмов.

Планируемая первая связка: **scadnano → oxDNA/oxpy → oxDNA analysis tools/PyMBAR → oxView**, с **AiiDA/aiida-shell** для исполнения и происхождения данных. Для выбора следующего опыта рассматриваются **Ax/BoTorch**. Это план интеграции, не готовая поставка; основания и ограничения находятся в [реестре источников](docs/research/SOURCES.md).

## Навигация

| Документ | Назначение |
|---|---|
| [VISION](docs/VISION.md) | Миссия, дальняя цель и измеримый вклад |
| [ROADMAP](docs/ROADMAP.md) | NL0–NL8, зависимости и условия завершения |
| [INFRA ROADMAP](docs/infra/ROADMAP.md) | Параллельная вычислительная линия INFRA0–INFRA7 |
| [MVP](docs/MVP.md) | Первый пользовательский сценарий и приёмка |
| [PROJECT CONTROL](PROJECT_CONTROL.md) | Каноническое состояние, ветвление и control invariants |
| [HARNESS CONTROL](HARNESS_CONTROL.md) | Короткая точка входа для агентов |
| [EXPERIMENT HARNESS](docs/control/EXPERIMENT_HARNESS_RU.md) | Начало/продолжение/завершение научных запусков и evidence |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Ядро, адаптеры, ИИ и будущие расширения |
| [EXPERIMENTS](docs/experiments/README.md) | E0–E6: контрольные опыты и исследования |
| [WORK QUEUE](docs/work/WORK_QUEUE.md) | Очередь ограниченных заданий |
| [AGENT START](docs/work/AGENT_START.md) | С чего начинать следующему агенту |
| [INDEX](docs/INDEX.md) | Полная карта документации |

## Harness commands

Linux/macOS:

```bash
./CONTROL_DEVELOPMENT.sh --check-consistency
./CONTROL_DEVELOPMENT.sh --overview
./CONTROL_DEVELOPMENT.sh --drive
./CONTROL_EXPERIMENT.sh validate experiments/evidence/E1/<campaign>/runs/<run>
```

Windows PowerShell:

```powershell
.\CONTROL_DEVELOPMENT.ps1 -CheckConsistency
.\CONTROL_DEVELOPMENT.ps1 -Overview
.\CONTROL_DEVELOPMENT.ps1 -Drive
.\CONTROL_EXPERIMENT.ps1 validate experiments/evidence/E1/<campaign>/runs/<run>
```

## Правило качества

Успешный запуск программы ≠ научная достоверность. Совпадение моделей ≠ экспериментальное подтверждение. Красивая анимация ≠ работающая наномашина. Отрицательный результат сохраняется наравне с положительным.

Правила участия: [CONTRIBUTING](CONTRIBUTING.md), правила агентов: [AGENTS](AGENTS.md). Лицензия собственного проекта ещё требует решения владельца: [LICENSE_POLICY](LICENSE_POLICY.md).
