# Director Acceptance — NL3-001 «Register hinge design family»

Дата решения: 2026-09-11. Роль: DIRECTOR научной линии NL (fresh-сессия; контексты implementer/reviewer/verifier не переиспользовались — только Git-факты и вердиктные документы). Явная авторизация владельца на Director-приёмку и merge в main получена в миссии (Human Gate открыт). Динамика в этом Work Order не запускалась — научные статусы экспериментов не затрагиваются; применяется потолок `C0_SOFTWARE_ONLY`.

## Решение

```text
NL3-001 = ACCEPTED                    # WO-уровень: регистрация семейства Shi–Castro–Arya + структурное воспроизведение первого экземпляра 0b (8/8, отчёт воспроизведён байт-в-байт F8EF3EA4…)
campaign scientific_outcome = NOT_EVALUATED   # динамики нет — кампания E2 = NOT_RUN (это NL3-002 «Execute E2»)
stage NL3 = IN_PROGRESS               # стадия открыта: NL3-001 ACCEPTED, впереди NL3-002
frontier = NL3
next_work_order = NL3-002 (READY)
experiment_status: без изменений      # E0 = RUN, E1 = RUN, E2 = NOT_RUN — конвенция execution-facts сохранена
Claim ceiling: C0_SOFTWARE_ONLY
```

## Основание — вердиктная цепочка

1. **Implementation**: `work/nl3-001-hinge-family-r1` @ `d01ff03` (base `5fbd6d5` — предок; handoff-пакет EX-NL3-001-R1, паспорт HANDOFF_READY, события 0001→0004, state/plan до checkpoint не тронуты). Поставлено: `docs/research/HINGE_FAMILY_R1.md` — регистрация «семейство → parameter space → первый экземпляр `0b`» с классами REPORTED/OBSERVED/UNKNOWN, UNKNOWN-таблицей U1–U6, гэпами G1–G6 и жёсткими правилами можно/нельзя (REFERENCE_ONLY: ни одного байта источника в Git, вендоринг/durable-кэш/генерация-как-оригинала запрещены); `scripts/hinge_family/` — замороженный детерминированный stdlib-only инструмент: `source_pins.json` (18 pinned-поверхностей: blob SHA-1 с provenance NL0-001-preregistered/R1-tree-listing, SHA-256 content-verified для пяти поверхностей `0b`, NOT_VERIFIED для остальных — контракт «null ⇔ NOT_VERIFIED» enforced), fail-closed парсеры oxDNA `.top`/`.conf` и caDNAno-дизайна, machine-confirm sim-input E2-SETUP-R1 §5, канонический байт-детерминированный JSON-отчёт; структурное воспроизведение `0b` 8/8 PASS на реальных pinned-объектах (user-side download по exact pinned commit вне Git): 4266+4112 = **8378 баз дизайна == 8378 нуклеотидов топологии (точно)**, 112 странд (103 linear + 9 circular), 8378 частиц × 15 колонок, `t = 2e7`, ориентации точные (2.15e-07 ≤ 1e-06); детерминизм — два прогона байт-идентичны (`F8EF3EA4…D449A5`); `tests/test_hinge_family.py` 22 unittest (полный набор 160 OK).
2. **Independent REVIEWER = PASS** (`review/nl3-001-hinge-family-r1` @ `84f71e7`): bounded scope `5fbd6d5..d01ff03` = ровно 23 файла, 0 violations (вендоренных байтов источника нет; SESSION_LOG строго append; state/plan blob-идентичны base); 6 preregistered blob'ов NL0-001 совпали бит-в-бит; все 18 blob SHA-1 + размеры сверены с GitHub API tree `b2d6ceb…` (`truncated=false`, 33 entries) — **0 mismatches** (это же подтверждает «полный API-перечёт, не truncated»); SHA-256 пяти поверхностей `0b` воспроизведены собственным user-side download; 8/8 §4–§5 воспроизведено, отчёт **байт-в-байт** равен опубликованному (`F8EF3EA4…`); 60 инвариантов published-артефактов пересчитаны (8378 = 8378, Σ гистограммы = 8275, scaffold+staples и др.); UNKNOWN/REPORTED/OBSERVED-дисциплина и G1–G6 честны; self-acceptance отсутствует. Errata: **F-1** (LOW: §5 «4657» против published bucket «0.5» = 4677), **F-2** (LOW: «полный перечёт» §2 не исчерпывающий); INFO F-3/F-4/F-5.
3. **Independent VERIFIER = PASS** (`verify/nl3-001-hinge-family-r1` @ `a0687b5`; машинный журнал VERIFIER_VERIFICATION_LOG_R1.md): всё перепроверено независимо — собственный user-side download по exact commit `23fd1ff…` (scratch вне репозиториев), digest-гейт PASS, `python -m hinge_family validate` exit 0 ×2, 8/8; отчёт **байт-в-байт равен git-blob'у** published-отчёта (проверка по `git cat-file`; worktree-копия `14DFA702…` — CRLF-артефакт `autocrlf=true`, F-4 учтён); 18/18 пинов — 0 mismatches; **34/34 инварианта** из собственного воспроизведённого отчёта; тесты 22/22 + 160/160; harness-набор зелёный: `work_cli` **15/15** EX OK (EX-NL3-001-R1 ok, HANDOFF_READY, терминал последний), `check-consistency` ok, JSON-гейт 721 tracked / unparseable ровно 2 pinned NEG (sha256 = CI-пинам), workflow lint 0 violations, `verify-digests` E1-R1/E1-R2/E0-R4 ok (0 mismatch); errata F-1/F-2 независимо подтверждены; новая **V-1** (LOW, класс errata F-1): §5 «вторая полоса 1.2–1.7 (≈448)» — строго по артефакту **440** (сумма buckets 1.2–1.7 = 19+41+112+159+87+22); 448 = buckets ≥ 1.1.
4. **Роли независимы**: implementer, reviewer, verifier — три разные fresh-сессии; ACCEPTED до настоящего решения в пакете отсутствовал (review PASS не является accept'ом, verifier PASS не повышает статус); merge — Human Gate, разрешён владельцем в этой миссии.

## Errata (закрыты до checkpoint, errata-коммит `eedbe27`, метка r1-errata)

Prose-правка одного документа `docs/research/HINGE_FAMILY_R1.md` (все — LOW, точность durable-записи; ни один PASS-check, факт или вывод не опирается на исправленные числа; замороженные поверхности — `source_pins.json` и published-отчёт — не тронуты; старые события не редактировались):

- **F-1**: §5 главный пик 0.5–0.6: 4657 → **4677** (bucket «0.5» published-отчёта; ошибка перепечатки).
- **F-2**: §2 «полный перечёт» → «ключевой состав»; полный перечень — GitHub API tree `b2d6ceb…` (33 entries, `truncated=false`), вне перечня остаются `Design_Hinges/README.md` (268 B) и конкретное содержимое `Init_Hinges/` (README.md, `cadnano_interface.py`, `init_generator.py`, `ini_demo/*`); на реестр «ровно 18 зарегистрированных поверхностей» не влияет.
- **V-1**: §5 вторая полоса 1.2–1.7: «≈448» → **440** с уточнением bucket-семантики (448 = buckets ≥ 1.1, включая bucket «1.1» = 8).
- INFO F-3 (event 0004 перечисляет содержимое records-коммита не полностью), F-4 (CRLF-артефакт `autocrlf=true` — воспроизводимость проверять по `git cat-file`), F-5 (два узких тест-пробела: digest-гейт для пина с `sha256: null`, слабая substring-проверка wall-clock) — приняты к сведению; F-4/F-5 — кандидаты в pre-E2 инструментальную итерацию, не ремонт R1.

## Ограничения, переносимые явно (не входят в ACCEPT)

1. **Без динамики**: принятое — регистрация семейства + структурное воспроизведение `0b`. Интегральность рана (H-bonds, энергия, динамика, hinge angle) — **NL3-002 / E2** (gap G6); кампания E2 = `NOT_RUN`, campaign-level `scientific_outcome = NOT_EVALUATED`.
2. **Права источника остаются UNKNOWN**: G1/U1 (redistribution/использование) — открытое owner decision с NL0-002, настоящим ACCEPT'ом не закрывается; режим REFERENCE_ONLY, запрет вендоринга и durable-кэша (U4) сохраняются в силе. Прогон E2 на данных источника может требовать owner decision — вопрос подлежит явной фиксации при dispatch NL3-002.
3. **Pre-E2 гэпы** (HINGE_FAMILY_R1 §7): G2 (соответствие «путь дизайна → странд топологии», 118 vs 112 — не декомпозировано), G3 (атрибуция spring layers — нужен SI), G4 (семантика колонок 9:15 конфигурации — engine-input check), G5 (SHA-256 поверхностей `11b–74b`) — собственные bounded шаги pre-E2, не закрыты этим решением.
4. **Процедурные требования E2-SETUP-R1 сохраняются**: подстановка `74b.top/74b.conf` → `0b` — обязательное документируемое отклонение от pinned-умолчания `pro_CPU.in`; 298 K (статья) vs 300 K (input) закрыт decision rule'ом E2-SETUP-R1 §5 (reproduction arm = авторские файлы verbatim); tolerances, число повторов и целевой интервал угла — `E2-PROTO-*` после пилота, до confirmatory прогонов.

## Checkpoint-ветка и интеграция

`control/nl3-001-director-checkpoint-r1` от `d01ff03`; влиты merge-коммитами: `review/nl3-001-hinge-family-r1` @ `84f71e7` (merge `db27407`) и `verify/nl3-001-hinge-family-r1` @ `a0687b5` (merge `05778c0`) — конфликтов нет (множества файлов вердиктных веток непересекаются: `REVIEWER_VERDICT.md` vs `VERIFIER_VERDICT.md` + `VERIFIER_VERIFICATION_LOG_R1.md`). Errata-коммит `eedbe27`. Свежий `origin/main` слит после fetch: `5fbd6d5` уже является предком `d01ff03` — дрейфа нет (merge «Already up to date», свежесть подтверждена повторным fetch'ем перед push). Старые события всех EX-* не тронуты.

## Изменения состояния проекта (этот checkpoint-коммит)

- `project/state.json`: NL3-001 = ACCEPTED; `completed_tasks` += NL3-001; `next_work_order` = NL3-002; `task_status.NL3-001` = ACCEPTED; `task_status.NL3-002` = READY; `stage_status.NL3` = IN_PROGRESS (стадия продолжается); `frontier` = NL3 — без изменений; `experiment_status` — **без изменений** (E0 = RUN, E1 = RUN, E2 = NOT_RUN); `execution.physics_runs` = 7 — без изменений (научных прогонов не было).
- `config/control/harness/scheduler-policy.v1.json`: `next_work_order` → NL3-002, notes обновлены (dispatch-оговорки NL3-002).
- `docs/work/WORK_QUEUE.md`: строка NL3-001 → ACCEPTED; шапка — разрешён старт NL3-002 с dispatch-оговорками.
- `docs/work/SESSION_LOG.md`: настоящая запись (append; старые записи не редактировались).
- `docs/evidence/NL3-001/DIRECTOR_ACCEPTANCE_R1.md`: настоящий durable acceptance record.

## Условия, с которыми принято

- ACCEPT относится к subject `d01ff03`, errata-коммиту `eedbe27` (prose-only) и вердиктной цепочке `84f71e7` (REVIEWER PASS) → `a0687b5` (VERIFIER PASS); любое изменение заявленных поверхностей в будущем — новая ревизия, а не редактирование.
- WO-уровень ACCEPT не объявляет научных исходов: campaign-level `NOT_EVALUATED`, потолок `C0_SOFTWARE_ONLY`; статусы E0/E1/E2 и `physics_runs` не менялись; динамика — впереди (NL3-002).
- UNKNOWN-права источника (G1/U1) и политика durable-кэша (U4) остаются открытыми owner decisions; REFERENCE_ONLY-дисциплина источника не ослабляется этим решением.

## Следующее действие

`NL3-002` «Execute E2 component campaign» (READY, scheduler priority; depends_on NL3-001 — выполнено). Постановка: первый шарнир `0b`; динамика по `E2-SETUP-R1` + decision rule. Обязательно зафиксировать при dispatch WO:

1. **Runtime E2 setup из артефактов NL3-001**: digest-gated user-side download по exact pinned commit (`source_pins.json` — сверьте size/SHA-256/blob перед каждым использованием), подстановка `74b` → `0b` как обязательное документируемое отклонение, sim-input machine-confirm (DNA2/0.5/300K/2e7/CPU/double; seed 7777 и OBSERVED-набор §3.2), structural pre-check тем же инструментом перед запуском динамики.
2. **Права источника G1**: E2 data — REFERENCE_ONLY / REDISTRIBUTION_RIGHTS = UNKNOWN; прогон E2 на данных источника может требовать owner decision (контакт авторов / явная лицензия / замена seed-источника по матрице NL0-002) — вопрос фиксируется явно в постановке NL3-002 **до** запуска кампании; durable-кэш (U4) — отдельное owner решение.
3. **Пререгистрация до confirmatory прогонов**: tolerances, число повторов, пороги целостности рана (G6) и целевой интервал угла — `E2-PROTO-*` после пилота; «DO NOT CHANGE ACCEPTANCE CRITERIA AFTER SEEING RESULTS» действует.
