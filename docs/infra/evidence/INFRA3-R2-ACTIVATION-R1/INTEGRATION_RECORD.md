# INTEGRATION_RECORD — integration/infra3-native-ubuntu-r2-activation-r1

```text
integration branch = integration/infra3-native-ubuntu-r2-activation-r1
base               = 8205781def7179d6bdfa6eb7ab2a84d46776649c (fresh origin/main)
integrated subject = infra/infra3-native-ubuntu-r2-activation-r1 @ c12b88b8b290592c5357755aa1844af007a0121e
merge              = --no-ff, без squash; история subject-ветки сохранена полностью
```

## Referenced gates (by exact SHA; review/verify branches remain verdict refs)

```text
fresh review        = review/infra3-native-ubuntu-r2-activation-r1 @ 89fdbb0 PASS
review refresh R1   = @ ec0aeb5 PASS (post-repair c12b88b; MINOR-1/2 CLOSED,
                      NOTE-1/3/4 CLOSED, NOTE-2 defer documented)
fresh verify        = verify/infra3-native-ubuntu-r2-activation-r1 @ 8e31f9f VERIFIED
                      (38 проверок; MINOR-1/2 закрытие подтверждено независимо)
```

## Статусы (честные, не меняются этим merge)

```text
gates U1-U5, NC-U1..U5 = WAITING_HOST (машина U1 не выделена)
R2_STATUS              = WAITING_HOST / NOT_ACTIVE
AUTHOR_U1              = NOT_ASSIGNED
NEW_SCIENCE без R2     = HARD_BLOCKED
outenemy               = EXTERNAL_U2_ONLY
merge в main           = Human Gate (этот integration PR)
```

## Валидация integration-HEAD (3b112f3)

```text
pytest tests/ -q          -> полный набор incl. 53 r2-теста (см. PR-описание)
check-consistency         -> ok:true
workflow_lint             -> blocking=0
work_cli validate EX-...  -> ok:true HANDOFF_READY
```

Разрешённые пути integration-merge: только содержимое subject-ветки (tree
c12b88b поверх base 8205781) + этот record. Никаких научных прогонов.
