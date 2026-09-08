# INFRA Execution Backends

Harness выбирает executor по capability и risk, а не по удобству конкретного агента.

## Backend classes

### H0 — GitHub-hosted ephemeral

Для: Harness tests, schema validation, unit tests, lightweight CPU smoke.

Преимущества: clean VM, безопаснее для public PR, минимум обслуживания.

Не использовать как единственный источник долгоживущих scientific artifacts.

### C0 — Self-hosted CPU

Для: oxDNA CPU, build cache, analysis, PyMBAR, первые reproducible scientific jobs.

Целевая конфигурация: Linux x86_64, dedicated runner user, достаточный SSD, container isolation. Конкретные CPU/RAM требования устанавливаются измерениями INFRA2/3, а не догадкой.

### G0 — Self-hosted GPU

Для: oxDNA CUDA и последующих ML/atomistic workloads.

Требует fingerprint:

```text
GPU model
GPU UUID where available
NVIDIA driver
CUDA runtime/toolkit
container/runtime version
scientific engine commit/build flags
```

### H1 — HPC / remote scheduler

Для: большие parameter sweeps, много replicas, atomistic calculations. Подключается после единого job/evidence contract.

## Executor contract

Каждый scientific job должен получить:

```text
job_id
work_order_id
experiment_id / run_id
subject_sha
upstream refs + input SHA-256
container/environment revision
resource budget
command
expected outputs
stop conditions
```

и вернуть:

```text
execution outcome
exit code
start/end UTC
host/runner fingerprint
resource usage
stdout/stderr/log refs
artifact manifest + digests
failure classification
```

Scientific interpretation выполняется отдельно от executor.

## Fallback

```text
current disposable environment
 → hosted CI
 → protected self-hosted CPU
 → protected self-hosted GPU
 → HPC/external provider
```

Work Order может потребовать конкретный backend только при физически значимой причине (CUDA, architecture-specific validation, resource size).
