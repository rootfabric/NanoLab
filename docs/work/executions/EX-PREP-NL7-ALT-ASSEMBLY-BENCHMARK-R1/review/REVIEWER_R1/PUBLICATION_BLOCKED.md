# Публикация комментария Issue #77 — БЛОКИРОВАНА правами токена (ожидаемо, подтверждено Director'ом)

Дата: 2026-10-21 UTC. ПОВТОРНАЯ одиночная попытка после указания Director'а:
  gh issue comment 77 --repo rootfabric/NanoLab --body-file review-evidence/REVIEW_PR76_R1.md
  → GraphQL: "Resource not accessible by personal access token (addComment)"; exit_code=1
Это ожидаемое поведение (у токена нет Issues:write), НЕ дефект review. Ретраев нет.
Публикацию берёт на себя Director (verdict-коммит в ветку PR #76).

--- (ниже — первоначальная диагностика) ---


Команда (как предписано mission):
  export GH_TOKEN=$(sed -n 's|https://[^:]*:\([^@]*\)@github.com.*|\1|p' ~/.git-credentials | head -1)
  gh issue comment 77 --repo rootfabric/NanoLab --body-file .../REVIEW_PR76_R1.md

Результат:
  GraphQL: "Resource not accessible by personal access token (addComment)" — exit 1
  REST fallback: gh api repos/rootfabric/NanoLab/issues/77/comments -f body=…
  → HTTP 403 {"message":"Resource not accessible by personal access token"} 

Диагностика: в ~/.git-credentials ровно один токен (fine-grained PAT, аккаунт
rootfabric). Read-операции работают (issue view, actions runs API — использованы
в этом review), но create-comment запрещён: у PAT нет разрешения Issues: write
для этого репозитория. Повышение прав из сессии невозможно.

Отчёт готов и сохранён: review-evidence/REVIEW_PR76_R1.md.
Публикация одним комментарием от имени владельца/родительского агента:
  gh issue comment 77 --repo rootfabric/NanoLab --body-file review-evidence/REVIEW_PR76_R1.md
