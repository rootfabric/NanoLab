# INFRA Security Model

NanoLab — публичный репозиторий. Self-hosted runner рассматривается как доверенный ресурс, на который **нельзя** безусловно запускать код из произвольного pull request.

## Trust zones

```text
UNTRUSTED
  public fork / external PR code
       ↓
GitHub-hosted ephemeral runner

TRUSTED CONTROL
  canonical main workflows + explicit dispatch
       ↓
self-hosted NanoLab runner

SCIENTIFIC ARTIFACTS
  raw trajectories / checkpoints / models
       ↓
separate artifact storage with digests
```

## Hard rules

1. `pull_request` jobs по умолчанию исполняются только на GitHub-hosted runners.
2. Self-hosted scientific runner не запускает код произвольного внешнего PR.
3. Scientific self-hosted job должен быть привязан к exact commit/subject и иметь bounded resource budget.
4. Runner работает без root, без интерактивных пользовательских секретов и по возможности в disposable container/workspace.
5. `GITHUB_TOKEN` — минимальные permissions; compute job по возможности read-only к repository contents.
6. Долгоживущие credentials не передаются simulation process, если это не требуется конкретным Work Order.
7. Артефакты получают SHA-256, размер, producer run ID, subject SHA и storage location.
8. Повтор job проверяет существующий run/manifest до нового вычисления.
9. Paid/cloud compute требует явного budget gate.
10. Physical lab/hardware control не подключается к этому runner без отдельного CRITICAL Work Order.

## Allowed trigger model

На ранних этапах self-hosted scientific compute разрешён только через explicit protected route, например `workflow_dispatch` из workflow, находящегося в canonical main, либо через отдельный trusted job-controller. Автоматический запуск self-hosted node на каждый public PR запрещён.

## Isolation target

Минимум INFRA2:

```text
Linux host
 └─ dedicated runner user
     └─ per-job clean workspace/container
         ├─ pinned dependencies
         ├─ bounded CPU/RAM/disk/time
         └─ no unrelated host mounts
```

Позднее допускаются ephemeral runners/VMs и отдельная compute network.
