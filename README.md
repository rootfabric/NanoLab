# NanoLab

**Открытая AI-лаборатория проектирования и вычислительной проверки наноструктур, нанокомпонентов и, в перспективе, наномашин.**

Миссия — сделать накопленные научные знания и вычислительные инструменты доступными для одного исследователя с ИИ. Даже небольшой воспроизводимый результат, полезный другим, считается значимым вкладом: исправленный анализ, открытый протокол, надёжный компонент или честный отрицательный результат.

## Текущее состояние

Ближайший продукт — **ограниченная атомистическая лаборатория P0–P3**: один материал/модель → структура → реальная релаксация и короткая MD → траектория/метрики → сохранение и сравнение вариантов. Первый инженерный сценарий строится на **ASE EMT Cu**; это демонстрация программы с реальным расчётом, `SOFTWARE_DEMONSTRATION / NOT_SCIENTIFICALLY_VALIDATED`. **P0 OPEN, принятых P-стадий нет**: требуется независимый material reference, а не только успешный запуск.

Атомистическая разработка идёт независимо от DNA NL5. Историческая научная линия сохранена: NL0–NL4 и NL5-001 приняты, frontier NL5; внешнее v0.1 воспроизведение завершилось terminal MISMATCH, `external_reproductions=0`. Новые NL5/E5 scientific runs требуют прежних U1/U2/R2/launch gates. S17 follower остаётся NOT_RECONSTRUCTED; static/synthetic assembly не доказывает передачу движения.

**Что делать сейчас:** [P0–P6 roadmap](docs/ROADMAP.md), [product plan](project/product-plan.json), [product state](project/product-state.json), [текущая очередь](docs/work/CURRENT_QUEUE.md). `harness.cli drive` показывает atomistic C0 preparation рядом с отдельным NL5 gate. Карточки не разрешают запуск; узкая инженерная проверка регулируется [mission WO](docs/work/WO-ATOMISTIC-PRODUCT-R1.md): до 4096 atoms, 2000 MD steps/run, 8 actual pilot runs, 20 минут compute и 2 GiB суммарно в disposable Linux. Это не разрешение будущей material campaign.

Лицензии собственного кода и материалов: Apache-2.0 для кода, CC-BY-4.0 для документации/derived data; права сторонних источников проверяются отдельно. INFRA предоставляет capability; production Task Bus не активирован этой работой.

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

**Atomistic Lab:** создать небольшую поддерживаемую структуру одного материала, выполнить реальный расчёт, просмотреть движение атомов и численные метрики, сохранить inputs/trajectory/manifest. Сначала — один проверяемый reference P0 и законченный сценарий P1; затем ограниченный конструктор P2 и сравнение вариантов P3. P4–P6 — условные исследования функции компонента, двухкомпонентной системы и специализированного механизма.

ИИ организует работу; физический adapter считает; независимая validation ограничивает выводы. EMT Cu не выдаётся за validated EAM или доказанные свойства материала. Старый DNA Nanomechanics Lab и его научная история сохранены как отдельная специализация: scadnano → oxDNA/oxpy → analysis/PyMBAR → oxView. AiiDA/aiida-shell и Ax/BoTorch подключаются по потребности работающего сценария.

## Запуск atomistic demo

После установки isolated venv с pinned atomistic dependencies:

```bash
PYTHONPATH=scripts .venv-atomistic/bin/python -m atomistic.web --port 8765 --output-root atomistic-runs
```

Открыть `http://127.0.0.1:8765`: Cu/ASE_EMT_Cu, fcc cuboid → relaxation/MD → trajectory playback/метрики → JSON/ZIP export. Это engineering demo с real adapter; до интеграционных evidence статус — candidate. Изменения формы должны оставаться в общей mission budget; restart браузера/сервера его не обнуляет.

CLI того же сценария:

```bash
PYTHONPATH=scripts .venv-atomistic/bin/python -m atomistic.cli run --config examples/atomistic/cu-demo.json --output-root atomistic-runs --run-id unique-run-id
```

Для каждого фактического запуска нужен новый run ID и свободный остаток общего бюджета. P1 software demo может поставляться с `NOT_SCIENTIFICALLY_VALIDATED`, пока P0 material reference остаётся OPEN; работающий сценарий не переписывается только из-за этого научного пробела.

## Навигация

| Документ | Назначение |
|---|---|
| [VISION](docs/VISION.md) | Миссия, дальняя цель и измеримый вклад |
| [ROADMAP](docs/ROADMAP.md) | Product P0–P6 и сохранённая DNA линия NL0–NL8 |
| [INFRA ROADMAP](docs/infra/ROADMAP.md) | Параллельная вычислительная линия INFRA0–INFRA7 |
| [MVP](docs/MVP.md) | Исторический DNA MVP и его критерии |
| [PROJECT CONTROL](PROJECT_CONTROL.md) | Каноническое состояние, ветвление и control invariants |
| [HARNESS CONTROL](HARNESS_CONTROL.md) | Короткая точка входа для агентов |
| [EXPERIMENT HARNESS](docs/control/EXPERIMENT_HARNESS_RU.md) | Начало/продолжение/завершение научных запусков и evidence |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Ядро, адаптеры, ИИ и будущие расширения |
| [EXPERIMENTS](docs/experiments/README.md) | E0–E6: контрольные опыты и исследования |
| [CURRENT QUEUE](docs/work/CURRENT_QUEUE.md) | Доступные software задачи и условия возврата |
| [WORK QUEUE](docs/work/WORK_QUEUE.md) | Историческая очередь и evidence |
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

Правила участия: [CONTRIBUTING](CONTRIBUTING.md), правила агентов: [AGENTS](AGENTS.md). Права и принятые лицензионные решения: [LICENSE_POLICY](LICENSE_POLICY.md).
