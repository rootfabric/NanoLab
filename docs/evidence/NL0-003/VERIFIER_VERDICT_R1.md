# NL0-003 — Fresh Verifier Verdict R1

Роль: `VERIFIER` (независимый, fresh; не implementer, не reviewer). Дата: 2026-09-09.
Worktree: `C:\NanoLab\verify-nl0-003`, ветка `verify/nl0-003-preregistration-r1` (создана от handoff-HEAD, без выполнения substantive work).

## Exact subjects (перепроверены фактически)

```text
BASE_SHA          = 81e299f1924e50bcff1bc5c893bccd934ef2883d   (canonical main)
START_COMMIT      = 9372b79e1406ffd2d0853bcd3c8f2232062f737c
SUBSTANTIVE_HEAD  = 9404a422166cb07efd98443a5f208f078a4ab2c4
SUBSTANTIVE_TREE  = b8b1bd992f15f9093ea4338255858e94d0bc06ad   (git cat-file -p: MATCH)
HANDOFF_COMMIT    = 6e30aee73252c0cc88545cc675633448dd3aaee5   (HEAD worktree)
REVIEWER_VERDICT  = PASS @ 36c68e15f135c9b8141a9ce86283e4a2d50c612d
                     (origin/review/nl0-003-preregistration-r1, прочитан полностью)
Work Order NL0-003 (issue #4), EX-NL0-003-R1, Risk HIGH, claim C0_SOFTWARE_ONLY
```

## VERDICT: **PASS**

## Таблица проверок

| # | Проверка | Команда (факт) | Результат |
|---|---|---|---|
| 1 | Binding: tree substantive HEAD | `git cat-file -p 9404a42…` | tree `b8b1bd99…` — MATCH |
| 1 | Handoff-дифф только terminal-артефакты | `git diff --stat 9404a42..6e30aee` | ровно 3 файла: `events/0005-handoff-completed.json`, `passport.json`, `branch-passport.md` — OK |
| 1 | subject_sha event 0005 | чтение `events/0005-handoff-completed.json` | `9404a422166cb07efd98443a5f208f078a4ab2c4` — MATCH substantive HEAD |
| 2 | Scope vs allowed_paths | `git diff --name-only 81e299f..6e30aee` | 14 путей; все внутри allowed_paths паспорта (WO, PREREGISTRATION_E1_R1, E2_SETUP_R1, SOURCES, SESSION_LOG, executions/EX-NL0-003-R1/**, evidence/NL0-003/**) — OK; `state.json`/`plan.json`/`config/`/политики в диффе отсутствуют |
| 3 | Inputs SHA-256, независимо | GitHub contents API `lorenzo-rovigatti/oxDNA` @ `00dc7fb9…`, Accept `application/vnd.github.raw`, файл на диск; `Get-FileHash -Algorithm SHA256` + `git hash-object` | `dsdna8.top` 148 B, sha256 `f1aded90…03fc4`, blob `1811af7e…` — MATCH; `init.dat` 4498 B, `0ff76d54…91a9e0`, blob `856be187…` — MATCH; `MD/quick_input` 533 B, `8935c4bc…f74a2`, blob `07eef592…` — MATCH; `MD/quick_compare` 51 B, `86a8b6ac…3ce27`, blob `74a088ec…` — MATCH (8/8: SHA-256 и blob SHA-1 по всем четырём) |
| 4 | Verbatim §3 PREREGISTRATION | побайтовое сравнение скачанного `quick_input` с блоком §3 | все 21 параметр значенийо-совпадают, включая закомментированные `#seed = 4982` и `#pt = 0.1` (последний приведён в §2.4); см. отклонение D-1 о форме блока |
| 4 | Oracle §5.1 | сравнение `quick_compare` | `ColumnAverage::energy.dat::2::-1.37970256144::0.15` — дословно MATCH |
| 4 | Таблица 2.2 (blob/size/SHA-256) | сверка с независимыми вычислениями п.3 | 4/4 строки MATCH |
| 4 | Факты §2.3 (OBSERVED) | чтение скачанных `dsdna8.top`, `init.dat` | `16 2`; цепи A C G T A C G T ×2; `t = 329197`; `b = 20 20 20`; 16 частиц — MATCH |
| 5 | Трассируемость чисел E1/E2 | проход по PREREGISTRATION_E1_R1.md и E2_SETUP_R1.md | см. раздел «Числа» ниже — нет чисел без трассировки |
| 6 | Schema/JSON | `python -m json.tool` × 9 (passport, events 0001–0005, state.json, plan.json) | все exit 0; event_type/actor_role в enum work-event.schema.v1.json; `subject_sha` 40-hex; `event_id` соответствует `^[0-9]{4}-[a-z0-9-]+$`; passport.json соответствует execution-passport.schema.v1.json, `status=HANDOFF_READY` в enum |
| 7 | Контролы | `.\CONTROL_DEVELOPMENT.ps1 -CheckConsistency`; `.\CONTROL_WORK.ps1 validate …`; `.\CONTROL_WORK.ps1 close …` | все: `ok=true`, `errors=[]`, exit 0 |
| 8 | Timeline | чтение timestamp_utc событий | 14:16 → 14:35 → 14:50 → 15:05 → 15:20 (2026-09-08) — монотонно неубывают |

## Числа: трассировка (проверка «отсутствия выдуманных значений»)

| Число | Источник | Статус |
|---|---|---|
| oracle `-1.37970256144`, полоса `0.15` | pinned `quick_compare` (byte-exact, п.3) | TRACED (upstream) |
| `#seed = 4982`, `#pt = 0.1`, все параметры §3 | pinned `quick_input` (byte-exact, п.3) | TRACED (upstream) |
| `2e7` steps, `T = 300K`, `salt_concentration = 0.5`, `DNA2`, CPU/double (`pro_CPU.in`) | REFERENCE_SELECTION.md (NL0-001, принято Director), blob `89d76310…` | TRACED (NL0-001 OBSERVED) |
| 298 K, 500 mM, average-base | REFERENCE_SELECTION.md §56 (статья Shi–Castro–Arya, REPORTED) | TRACED (NL0-001) |
| five variants `0b, 11b, 32b, 53b, 74b`; длины 0/24, 11/35, 32/56, 53/77, 74/84 bases | REFERENCE_SELECTION.md §54–55 (статья, NL0-001; в E2_SETUP_R1 явно помечено «machine-check при получении файла») | TRACED (NL0-001 REPORTED) |
| `R_pilot = 3` (E1 §6.4) | процедурная константа пилота, объявлена как процедура (не научное число и не upstream-claim), pilot не засчитывается в evidence | ДОПУСТИМО: procedural constant с явной маркировкой; `R_confirm` сознательно не назначается |
| `steps/print_energy_every = 1000`, `steps/print_conf_interval = 10` | арифметика от pinned `quick_input` | TRACED (derived) |
| wall-time/RAM E1, budget, tolerances E2, целевой угол, число повторов E2 | `ASSUMED`/не назначены/UNKNOWN с процедурами закрытия | корректно помечены |

Числа без трассировки: **не найдены**.

## Отклонения

| ID | Severity | Описание |
|---|---|---|
| D-1 | INFO (non-blocking) | Блок §3 PREREGISTRATION_E1_R1 приводит параметры в нормализованной расшифровке: опущены закомментированные строки `#debug = 1` и `#pt = 0.1` (значение `#pt` приведено в §2.4) и trailing-пробелы строк `T = 20C` / `print_energy_every = 1e3`. Документ сам явно объявляет эталоном «полный байт-точно файл» (SHA-256 спинен), а не расшифровку; значения не искажены. Рекомендация для E1-PROTO-R2: пометить блок §3 как «все параметры, включая комментарии» либо привести комментарии в блоке. |
| D-2 | INFO (non-blocking) | Зафиксированы два MINOR-наблюдения Reviewer R1 (интерпретация полосы ±0.15 под рубрикой REPORTED в §6.1; обозначение SUBSTANTIVE_HEAD в IMPLEMENTER_EVIDENCE при self-referential коммите). Не влияют на критерий; подтверждены настоящей проверкой как неточности маркировки, не значения. |
| D-3 | INFO (non-blocking) | Timeline: timestamps событий монотонны; сравнение timestamp_utc с git commit times не проводилось (известное non-blocking наблюдение NL0-002). |

Ни одно отклонение не затрагивает exact subject, hashes, verbatim-цитаты или scope.

## Факты для аудита

```text
SIMULATIONS_RUN = NONE (со стороны Verifier; E0–E6 NOT_RUN подтверждены)
THIRD_PARTY_FILES_COPIED = NONE в репозиторий (загрузки во временный каталог, удалены после хэширования)
Изменён только этот файл (docs/evidence/NL0-003/VERIFIER_VERDICT_R1.md)
ACCEPTED не выставлен; Director checkpoint proposal и merge — следующие шаги (merge — Human Gate)
```
