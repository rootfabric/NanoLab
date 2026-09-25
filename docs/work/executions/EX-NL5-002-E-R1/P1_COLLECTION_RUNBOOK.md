# P1 COLLECTION RUNBOOK — EX-NL5-002-E-R1, leg P1 (для сессии на DESKTOP-QNAGSTI)

Статус: P2 leg завершён и закоммичен (5ef6c1c). P1: физика по расчёту завершилась
на диске ~2026-09-21T01:30Z, но evidence не собран. Этот runbook = точная
процедура сбора. Рассчитан на свежую сессию оператора на авторской машине.

## 0. Идентификация машины (обязательно до любых действий)

```bash
hostname            # ожидается: DESKTOP-QNAGSTI
whoami              # ожидается: yurig
gcc --version | head -1   # 11.x нет — ожидается 13.3.0 (Ubuntu 24.04, WSL2)
grep PRETTY /etc/os-release   # Ubuntu 24.04.x
```

Если хоть один пункт не совпал — СТОП, вы не на P1-платформе (P1_ENVIRONMENT_MISMATCH).
Никакие данные другой машины подставлять нельзя.

## 1. Свежая ветка

```bash
cd ~/nanolab-platform-sensitivity-r1 && git -C <репо-путь> fetch origin   # или clone
git checkout work/nl5-002-e-platform-sensitivity-r1 && git pull
# этот runbook и скрипты лежат в docs/work/executions/EX-NL5-002-E-R1/
```

## 2. Техническое состояние 20 прогонов

```bash
WS=~/nanolab-platform-sensitivity-r1/P1
ls $WS/runs/                       # ожидается 20 каталогов PLATSENS-P1-{0B,32B}-S001..S010
for d in $WS/runs/PLATSENS-P1-*/; do
  r=$(basename $d); echo "$r exit=$(cat $d/exit_code*.txt 2>/dev/null | tr -dc '0-9-') stderr=$(stat -c%s $d/stderr.log 2>/dev/null)"
done | sort
ps aux | grep -c "[o]xDNA input"   # ожидается 0 — всё завершено
```

Ожидаемая картина: 20/20 exit=0, stderr 0 B, traj.dat ~114.7 MB (0b) / ~86.8 MB (32b),
у 0b — 50 кадров (`grep -c '^t =' traj.dat`), у 32b — 37.

## 3. Если есть незавершённые/ненулевые/усечённые прогоны

Политика §6 (технический retry): ID НЕ переиспользовать. Новый ID = `<старый>-R1`,
ТОТ ЖЕ frozen seed, тот же variant/steps, тот же лаунчер. Пример:

```bash
bash $WS/launch_run.sh PLATSENS-P1-32B-S004-R1 32b 601855227 150000
```

Superseded-попытки остаются в runs/ и попадают в manifest отдельным списком.
Научный outlier при exit=0 НЕ перезапускается.

## 4. Дайджесты артефактов (§8–§9)

```bash
python3 docs/work/executions/EX-NL5-002-E-R1/p1_recovery/build_run_output_digests_p1.py
# скрипт сам найдёт $WS/runs, выдаст run_output_digests_p1.json:
#   20 final ID, 0 missing, 0 duplicates, superseded отдельно
```

## 5. Packaged-анализ всех 20 финальных прогонов (§10)

```bash
bash docs/work/executions/EX-NL5-002-E-R1/p1_recovery/analyze_all_p1.sh
# только nanolab-components 0.1.1 convention/analyze_hinge.py, никакой другой analyzer
# проверка: analysis/completeness.txt — 20 строк "analyze ... exit=0"
```

## 6. Durable event (§12) + commit (§13)

Создать `docs/work/executions/EX-NL5-002-E-R1/events/0006-continuation-p1-complete.json`
по формату событий 0002–0005 (ТОЛЬКО факты исполнения: 20/20, exit-статусы,
число артефактов, число анализов, digest manifest, технические retries если были;
НАУЧНЫХ значений и вердиктов НЕ писать). Commit:

```
work(nl5-002-e): P1 complete - 20/20 runs and packaged analysis
```

Push, вернуть `P1_COMPLETE_HEAD` и `P1_COMPLETE_TREE`.

## 7. Что НЕЛЬЗЯ (frozen-границы)

- Никаких shift/CI/ratio/verdict — paired-статистика считается только после P1+P2
  и только по замороженному плану (инструмент уже подготовлен и закоммичен:
  `paired_tooling/paired_stats_platsens.py`, запускать будет оператор на outenemy).
- Raw trajectories остаются в WSL FS, в Git не добавляются.
- Протокол/сиды/окна/паспорт не менять.

## 8. Бюджет (честная запись в event)

Физика P1 уложилась в 72h-бюджет (запуск 14:32:24Z, завершение ~01:30Z 21 Sep ≈ 35h).
Просрочена административная фаза (сбор evidence) — зафиксировать фактические даты.
