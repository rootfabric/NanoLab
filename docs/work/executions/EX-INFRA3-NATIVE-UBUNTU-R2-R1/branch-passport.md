# branch-passport — infra/infra3-native-ubuntu-r2-activation-r1

```text
execution_id = EX-INFRA3-NATIVE-UBUNTU-R2-R1
work_order   = WO-INFRA3-R2-ACTIVATION-R1 (child of WO-NATIVE-UBUNTU-EXECUTOR-R1 / INFRA3-003)
base         = 8205781def7179d6bdfa6eb7ab2a84d46776649c (origin/main, fresh fetch 2026-09-30)
risk / claim = MEDIUM / C0_SOFTWARE_ONLY (infrastructure tooling; НЕ научный WO)
host         = outenemy (dev host ДЛЯ C0-РАБОТЫ — разрешено policy; как scientific executor
               и как author host запрещено: OUTENEMY_ROLE = EXTERNAL_U2_ONLY)
```

## 1. Scope

Реализация R2 activation tooling (scripts/r2, config pin-файл, unit-тесты) +
execution evidence + поверхностный sync WORK_QUEUE/infra-plan. Полный scope —
`docs/work/WO-INFRA3-R2-ACTIVATION-R1.md` §2/§4.

## 2. Границы и честные статусы

- Машина U1 не выделена (`AUTHOR_U1 = NOT_ASSIGNED`,
  `R2_STATUS = WAITING_HOST / NOT_ACTIVE`); gates U1–U5 и NC-U1..U5 этим WO
  НЕ исполняются и остаются `WAITING_HOST`; fingerprint R2 не снимается.
- Никаких scientific runs; научная история, `project/state.json`,
  `project/infra-state.json` не изменяются; claim `C0_SOFTWARE_ONLY`.
- Известных схемных отклонений на стартe нет: checkpoint `INFRA3` валиден
  схемой (pattern `^(NL[0-8]|INFRA[0-7])$`, widening EX-CTRL-LINTSCHEMA-R1);
  passport без `notes` (урок MINOR-1 prior review); timestamps — машинные
  (урок MINOR-3); статус паспорта синхронизируется с терминальным событием
  (урок MINOR-5).
- Dev-хост исполнения (outenemy) используется строго как C0-среда
  (harness/docs/tooling/tests); исполняющие subcommands tooling обязаны
  отказывать на этом хосте (`BLOCKED_HOST`) — это тестируется.
