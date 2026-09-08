# INFRA — дорожная карта вычислительной инфраструктуры NanoLab

**Назначение:** развивать вычислительную и CI-инфраструктуру параллельно научной линии, не подменяя `NL0–NL8` и не создавая вторую научную roadmap.

## Лестница

```text
INFRA0  Control + security baseline
   ↓
INFRA1  Safe hosted CI for pull requests
   ↓
INFRA2  Protected self-hosted CPU runner
   ↓
INFRA3  Reproducible scientific executor        ← INFRA MVP
   ↓
INFRA4  Artifact store / cache / provenance
   ↓
INFRA5  GPU/CUDA scientific runner
   ↓
INFRA6  Queue, quotas, scheduler, AiiDA bridge
   ↓
INFRA7  Multi-node / HPC / external-lab compute federation
```

## Этапы

| Этап | Результат | Проверяемая граница |
|---|---|---|
| **INFRA0** | Threat model, runner trust model, branch/dispatch policy, resource classes | Публичный PR не может произвольно выполнить код на личном runner; human gates и allowed triggers описаны машинно/документально |
| **INFRA1** | GitHub-hosted CI для безопасных PR checks | На PR автоматически выполняются Harness/schema/unit checks на ephemeral hosted runner; нет доступа к self-hosted scientific node |
| **INFRA2** | Self-hosted Linux CPU node | Runner зарегистрирован с отдельными labels; работает non-root/isolated workspace; scientific jobs запускаются только разрешённым dispatch route |
| **INFRA3** | Reproducible Scientific Executor | Pinned source → exact environment → job → logs/artifacts → SHA-256 manifest → Git evidence. Малый E1 можно выполнить end-to-end без ручной настройки машины |
| **INFRA4** | Durable artifact storage | Raw trajectories могут жить вне Git; manifest содержит digest/size/producer/subject/storage; retention и cache не разрушают provenance |
| **INFRA5** | GPU/CUDA runner | Exact CUDA/driver/toolchain fingerprint; oxDNA GPU smoke; CPU/GPU comparison protocol; E2-scale jobs получают bounded GPU executor |
| **INFRA6** | Scheduler / quotas / provenance orchestration | Очередь, budgets, cancellation, duplicate detection, AiiDA или эквивалентный process/provenance bridge; AI не может бесконтрольно расходовать compute |
| **INFRA7** | Scale-out federation | Подключение нескольких nodes/HPC/cloud/external institutional compute через единый job contract без переноса scientific truth в инфраструктуру |

## INFRA MVP

**INFRA3 считается первым полезным инфраструктурным продуктом.** Его acceptance scenario:

```text
canonical NanoLab subject
    ↓
pinned upstream oxDNA commit + input SHA-256
    ↓
clean isolated Linux environment
    ↓
reproducible build
    ↓
small E1 job
    ↓
exit/log/resource capture
    ↓
artifact manifest + SHA-256
    ↓
Harness Experiment/Work evidence
```

Сам факт успешного job не является научным PASS; scientific acceptance остаётся в Experiment Harness.

## Связь с научной дорожной картой

- `NL0`: INFRA не требуется.
- `NL1`: может использовать INFRA3, но локальный/другой разрешённый executor остаётся fallback.
- `NL2`: INFRA4 сильно улучшает provenance и повторяемость.
- `NL3 / E2`: INFRA5 желателен для больших hinge campaigns, но конкретный Work Order решает, является ли GPU обязательным.
- `NL4`: INFRA6 нужен, когда AI начинает планировать множество runs и требуется бюджетирование/очередь.
- `NL5+`: INFRA7 полезен для внешнего воспроизведения и нескольких compute providers.

**Запрещено:** объявлять scientific checkpoint принятым только потому, что инфраструктура зелёная.

## Ветвление

Каждый этап развивается отдельной bounded веткой:

```text
infra/infra0-security-control-r1
infra/infra1-hosted-ci-r1
infra/infra2-self-hosted-cpu-r1
infra/infra3-reproducible-executor-r1
infra/infra4-artifact-store-r1
infra/infra5-gpu-runner-r1
infra/infra6-scheduler-aiida-r1
infra/infra7-compute-federation-r1
```

После accepted merge следующая крупная стадия начинается от свежего canonical `main`, а не бесконечно поверх старой infra-ветки.
