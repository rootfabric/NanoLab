# Verifier Evidence — INFRA1-001 (EX-INFRA1-001-R1)

**Verifier:** independent fresh verifier (не Implementer, не Reviewer ветки; verdict формируется только по фактам Git и собственному исполнению).
**Date (UTC):** см. commit timestamps ветки `verify/infra1-hosted-ci-r1`.
**Subject:** `0ab044b87e3e296942da3307f1b1c5ed0c34f5f1` (substantive HEAD ветки `infra/infra1-hosted-ci-r1`).
**Base:** `7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de` (canonical `main`).
**Verify worktree:** `C:\NanoLab\verify-infra-1-001`, branch `verify/infra1-hosted-ci-r1`, checkout subject.
**Reviewer PASS (не является основанием для этого verdict):** `0f1c348e5de55922b7b26f2addd9413f230abd7b` на `review/infra1-hosted-ci-r1`.

Инструменты верификатора: `git version 2.53.0.windows.1`, `Python 3.11.8`, `jsonschema 4.22.0`, `PyYAML` (Mechanical check script: `scratch/verify-infra1-001/check_workflow.py`, вне репозитория).

---

## 1. Scope / subject

### 1.1 Remote-факты (ls-remote bare repo `C:\NanoLab\.git-store\repo.git`)

- `refs/heads/main` = `7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de` — совпадает с base паспорта.
- `refs/heads/infra/infra1-hosted-ci-r1` = `ff8d86a5d2e6fbf8965318990ae2fa84b38f94af`.
- `refs/heads/review/infra1-hosted-ci-r1` = `0f1c348e5de55922b7b26f2addd9413f230abd7b` (= subject + 1 review-commit).
- `verify/infra1-hosted-ci-r1` до старта верификации не существовал (создан этой верификацией).
- Subject `0ab044b` существует в репо (`git cat-file -t` → `commit`).

### 1.2 Положение subject в ветке

```
git merge-base --is-ancestor 0ab044b87e3e296942da3307f1b1c5ed0c34f5f1 ff8d86a5d2e6fbf8965318990ae2fa84b38f94af
→ exit 0 (subject — предок текущего tip ветки)
```

Tip `ff8d86a` содержит ровно 2 коммита после subject: `5a73707` «harness: record INFRA1-001 implementation and validation», `ff8d86a` «harness: complete INFRA1-001 handoff» — bookkeeping-коммиты исполнения (events 0002–0004, summary.md, обновление паспорта), не входящие в верифицируемый subject. Verdict ниже касается **subject `0ab044b`**; факты tip использованы только там, где это указано явно (§5, схемы events 0002–0004).

### 1.3 Ancestry от base

```
git merge-base --is-ancestor 7f17e9a1b9f712648e241d9eb8b0d8c9c8db93de 0ab044b87e3e296942da3307f1b1c5ed0c34f5f1
→ exit 0
```

Коммиты base..subject (ровно 3):

```
0ab044b docs(infra): document HOSTED_CI_R1 route mapping and machine config
ed2d596 ci(infra1): add hosted RC0 harness validation workflow (H0 only)
a689711 harness: start INFRA1-001 hosted CI execution
```

### 1.4 Изменённые файлы vs allowed_paths

```
git diff --name-status 7f17e9a..0ab044b
A  .github/workflows/hosted-ci.yml
A  config/infra/hosted-ci.v1.json
A  docs/infra/HOSTED_CI_R1.md
A  docs/work/executions/EX-INFRA1-001-R1/branch-passport.md
A  docs/work/executions/EX-INFRA1-001-R1/events/0001-work-order-started.json
A  docs/work/executions/EX-INFRA1-001-R1/passport.json
```

Allowed paths (`docs/work/executions/EX-INFRA1-001-R1/passport.json`): `.github/workflows/**`, `docs/infra/HOSTED_CI_R1.md`, `config/infra/hosted-ci.v1.json`, `docs/work/executions/EX-INFRA1-001-R1/**`.

| Файл | Паттерн allowed_paths | Вне scope? |
|---|---|---|
| `.github/workflows/hosted-ci.yml` | `.github/workflows/**` | нет |
| `config/infra/hosted-ci.v1.json` | `config/infra/hosted-ci.v1.json` | нет |
| `docs/infra/HOSTED_CI_R1.md` | `docs/infra/HOSTED_CI_R1.md` | нет |
| `docs/work/executions/EX-INFRA1-001-R1/*` (3 файла) | `docs/work/executions/EX-INFRA1-001-R1/**` | нет |

**6/6 файлов внутри allowed_paths; файлов вне allowed_paths — 0; удалений — 0.**

### 1.5 Неизменность state-файлов (Director gate)

```
git rev-parse 7f17e9a:project/state.json      → 66df364e01edabf15b1048a987a85e3027598b42
git rev-parse 0ab044b:project/state.json      → 66df364e01edabf15b1048a987a85e3027598b42  (идентичен)
git rev-parse 7f17e9a:project/infra-state.json → 17bb432f9e8666cacbd5b2a01c118a31591d731a
git rev-parse 0ab044b:project/infra-state.json → 17bb432f9e8666cacbd5b2a01c118a31591d731a  (идентичен)
```

`project/state.json` и `project/infra-state.json` на уровне blob идентичны base. В subject `capabilities.hosted_ci = false`, `INFRA1-001 = READY`, `next_work_order = INFRA1-001` (фронт INFRA не продвинут Implementer'ом).

### 1.6 Скан секретов

Скан добавленных строк subject-диффа (`git diff 7f17e9a..0ab044b`) по паттернам: `AKIA[0-9A-Z]{16}`, `ASIA[0-9A-Z]{16}`, `ghp_…`, `github_pat_…`, `xox…`, `sk-…`, `AIza…`, `-----BEGIN … PRIVATE KEY` → **0 совпадений**.

Дополнительный keyword-скан (`api_key|password|passwd|secret|token|credential`, без учета регистра) → 24 строки; все — декларации политики и негативные утверждения (`persist-credentials: false`, `secrets_used: []`, `secrets_in_artifacts: false`, «no secrets», owner-action о read-only GITHUB_TOKEN и т.п.). Реальных секретов/credential-материала нет. **Итог: 0 секретов.**

---

(Разделы 2–6 добавляются последующими коммитами.)
