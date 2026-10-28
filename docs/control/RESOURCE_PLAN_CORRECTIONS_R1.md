# RESOURCE_PLAN_CORRECTIONS_R1 — дополнение к F05 / U2

C0 арифметика на опубликованных снимках; не новые замеры U1/U2 и не разрешение запускать научную кампанию. Исторические ledgers неизменны. Машинные исходники, commits и расчёты: `RESOURCE_PLAN_CORRECTIONS_R1.json`.

## P2 есть в Git

F05 R1 ошибочно утверждает отсутствие P2 wall/size. Canonical `EX-NL5-002-E-R1/evidence/p2/run_output_digests_p2.json` содержит 20 результатов: 10 × 0b (200000 шагов) и 10 × 32b (150000 шагов). Средние времена: 13.461222 и 10.168583 ч. Проекция только основных 64+64 запусков: 1512.307556 суммарных job-wall-hours; при двух идеально работающих слотах нижняя оценка elapsed = 756.153778 ч. Controls, replacements, setup и contention сюда НЕ входят.

Это условная историческая оценка, не benchmark новой Release-сборки, не пересмотр frozen statistical feasibility и не доказательство невозможности кампании. Порог контракта — **560 wall-hours/platform**, не CPU-hours. Параллельность может уменьшать elapsed, но не суммарные CPU-hours. Требуется актуальное измерение целевой сборки/профиля в отдельно разрешённом техническом scope до scientific dispatch. N/seeds/criteria/296+56<=352/560 не меняются. Не считать два слота достаточными только по более быстрому P1.

```bash
PYTHONPATH=scripts python3 -m harness.resource_plan --p2-manifest docs/work/executions/EX-NL5-002-E-R1/evidence/p2/run_output_digests_p2.json --slots 2
```

## Исправление df

При неизменных reserved blocks `df` использует `used/(used+available_unpriv)`. Минимум освобождения для target=80%: `ceil(used - 0.8*(used+available_unpriv))` с нижней границей 0. Использовать целочисленную арифметику `resource_plan.bytes_to_free`.

По снимку 26 октября: `/` требует 73,529,683,149 байт, `/mnt/gig` — 138,395,534,951 байт. Старые предложения 53,512,075,673 и 97,413,734,400 оставили бы использование около 84.29%. Повторить df непосредственно до и после разрешённого действия; рост данных меняет расчёт.

Guard применяется к выбранной одобренной native raw-файловой системе. Не требуется очистка всех mounts ради общей зелёной строки; NTFS/FUSE и shared volume автоматически пригодными не становятся. Не удалять сторонние данные, raw evidence, Docker volumes, образы, checkouts либо логи без отдельного scoped owner решения.

## Systemd и память

`systemctl is-system-running`: здоровое значение `running`; `active` — состояние отдельного unit при `is-active`. `degraded` требует полного списка отказавших units и классификации. Отказ critical executor/storage/network unit блокирует работу; посторонний desktop unit не hard gate после доказанной независимости от job. Необъяснённые отказы остаются блокирующими. Utility `service_readiness` проверяет только этот аспект, не выдаёт scientific readiness.

Сохраняются process-survival, provenance, memory/swap/storage headroom и утверждённый профиль. 32 GiB — ранее заданная рекомендация U2, альтернативный измеренный профиль требует явного утверждения; для нового U1 owner minima не отменяются. Высокий RSS vpnagentd — наблюдение, не доказанная причина launcher failure. Не перезапускать VPN/службы автоматически.

## Следующее действие

RESOURCE-R1 пересобирает план с обеими историческими платформами и явно отделяет условные оценки от актуальных измерений. Владелец выбирает U1 и scoped remediation U2; оператор выполняет разрешённые действия и публикует свежий профиль. Положительные факты не придумываются; scientific launch только по прежним R2/Human/frozen gates.
