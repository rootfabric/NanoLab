# NanoLab — Experiment Harness

**Revision:** `NL-EH0-2026-09-08-R1`

Этот документ определяет, как вычислительные и будущие физические эксперименты становятся воспроизводимой историей Git.

## Campaign и Run

`Campaign` отвечает на один preregistered научный вопрос и может содержать несколько independent runs. `Run` — один frozen запуск с уникальным `run_id`.

```text
Campaign E1-R1
  ├─ E1-R1-S001
  ├─ E1-R1-S002
  └─ E1-R1-S003
```

Неудачный run нельзя перезаписывать новым запуском под тем же ID.

## Структура evidence

```text
experiments/evidence/<experiment-id>/<campaign-id>/
  campaign.md
  protocol.json
  runs/<run-id>/
    manifest.json
    events/0001-started.json
    events/0002-preparation-completed.json
    events/0003-run-checkpoint.json
    events/0004-run-completed.json
    events/0005-analysis-completed.json
    artifacts.manifest.json
    summary.md
  evidence-map.json
  review.md
```

Большие raw данные могут храниться вне Git. Digest и location остаются в `artifacts.manifest.json`.

## PRE_REGISTERED

До первой оценки результата фиксируются: scientific question, hypothesis/exploratory objective, claim ceiling, model/version/applicability, input source+digest, protocol revision, environment, observables/units, analysis method, comparison rule, exclusion rule, seed/replica policy, resource budget, stop conditions и known limitations.

Если threshold нельзя выбрать до pilot, preregistration описывает pilot procedure и момент freeze до confirmatory campaign.

## STARTED — обязательный Git checkpoint

До дорогого/долгого запуска в Git уже находятся `manifest.json`, `protocol.json`, `0001-started.json`, frozen code/analysis subject SHA, input digests, budget и stop conditions. Затем commit + non-force push.

## CONTINUATION

Новый event + commit обязателен после подготовки/relaxation/equilibration, batch independent runs, смены executor, численной проблемы, перед role handoff, после repair/restart, при существенном расходовании budget и перед analysis после завершения compute.

Для длинного единичного job почасовой heartbeat не нужен. До dispatch фиксируется внешний job/run ID; после возвращения — результат. Не создавать commits без новой информации.

## Завершение execution

Terminal execution event — один из:

```text
RUN_COMPLETED
RUN_FAILED_TECHNICAL
RUN_ABORTED
RUN_BLOCKED_ENVIRONMENT
```

Он фиксирует status/exit code, consumed resources, artifact refs/digests и failure class.

Затем analysis публикует отдельный `ANALYSIS_COMPLETED` с scientific outcome:

```text
SUPPORTED
NOT_SUPPORTED
INCONCLUSIVE
NOT_EVALUATED
INVALIDATED
```

Технический terminal event и scientific conclusion не смешиваются.

## Изменение protocol/code

Если изменился physics model, observable, analysis algorithm или acceptance criterion, старые runs не переписываются. Публикуется superseding event, создаётся новая revision/campaign и указывается допустимость reuse старых данных. Reporter/UI-only change можно документировать без rerun, если scientific computation не затронута.

## Reproducibility package

Закрытый campaign должен отвечать: что проверялось, что запускалось, на каком code/model, с какими inputs, что упало, что исключено и почему, где raw data, как проверяются artifacts, как рассчитаны observables, какой conclusion поддержан и что осталось unknown.

## Physical experiments

Будущие wet-lab/hardware experiments автоматически `CRITICAL` до отдельной domain-specific policy. Вычислительный harness не разрешает опасные, биологические, медицинские или регулируемые процедуры.
