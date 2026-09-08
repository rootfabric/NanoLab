# NanoLab

**Открытая AI-лаборатория проектирования и вычислительной проверки наноструктур, нанокомпонентов и, в перспективе, наномашин.**

Миссия — сделать накопленные научные знания и вычислительные инструменты доступными для одного исследователя с ИИ. Даже небольшой воспроизводимый результат, полезный другим, считается значимым вкладом: исправленный анализ, открытый протокол, надёжный компонент или честный отрицательный результат.

## Текущее состояние

**Документальный фундамент создан. Научный runtime, интеграции и эксперименты пока не реализованы и не проверены.** Наличие плана не означает закрытия NL0–NL8. Канонические статусы: [project/state.json](project/state.json). Следующая работа: [NL0-001 — отбор воспроизводимого эталона](docs/work/WO-NL0-001.md).

С 8 сентября 2026 года проект использует собственный development/experiment harness, адаптированный из `rootfabric/distributed-world-simulator`: [PROJECT_CONTROL](PROJECT_CONTROL.md), [HARNESS_CONTROL](HARNESS_CONTROL.md), [Experiment Harness](docs/control/EXPERIMENT_HARNESS_RU.md). `main` является каноническим project state; рабочие ветки обязаны сохранять начало, продолжение и завершение работы в Git.

Параллельно научной линии запланирован отдельный [INFRA track](docs/infra/README.md): safe CI → self-hosted CPU → reproducible executor → artifact store → GPU → scheduler/AiiDA → HPC. INFRA предоставляет вычислительные возможности, но по умолчанию не является hard gate научной дорожной карты и не владеет scientific truth.

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
