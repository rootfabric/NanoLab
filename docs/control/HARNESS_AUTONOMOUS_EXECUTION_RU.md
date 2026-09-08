# NanoLab — автономное исполнение агентами

**Revision:** `NL-H0-AUTONOMY-2026-09-08-R1`

Внутри разрешённого Work Order агент самостоятельно выполняет доступную механическую работу и фиксирует её в Git. Человек не используется как оператор команд или переносчик логов.

Разрешено без нового подтверждения: inspect/fetch refs, scoped branch/worktree, edit allowed paths, declared dependencies в disposable env, approved tests/simulations в budget, logs/hashes/reports, in-scope repair, commit, non-force push, draft PR, evidence и review request.

Не разрешено автоматически: merge/direct push main, force-push/history rewrite, destructive deletion, architecture/foundation authority expansion, новый CRITICAL experiment, paid/expensive compute сверх budget, physical wet-lab/hardware запуск без explicit gate.

## Executor fallback

1. текущая VM/container;
2. clean local worktree/exact checkout;
3. repository-owned CI, если policy разрешает;
4. fresh isolated role;
5. настроенный внешний executor.

Отсутствие предпочтительной VM не является `HARD_BLOCKED`, если задача доступна другим разрешённым способом.

## Scientific compute

Автономность ограничена preregistered protocol и budget. Дополнительные replicas разрешены только в границах protocol. Нельзя бесконечно повторять научно отрицательный опыт до получения желаемого результата.

`HARD_BLOCKED` допустим, когда обязательная capability недоступна, fallbacks исчерпаны, scope-preserving replan отсутствует, blocker/evidence записаны в Git и указан resume condition.
