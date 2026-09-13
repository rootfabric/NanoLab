# NanoLab — Post-MVP Execution Program R1

Статус: **DRAFT CANDIDATE**, ожидает owner review; merge в `main` — Human Gate.

Этот документ — исполнительная программа (operational layer) для уже зафиксированной
стратегии [POST_MVP_DEVELOPMENT_ROUTE_R1](POST_MVP_DEVELOPMENT_ROUTE_R1.md).
Он **не меняет** стратегию, canonical state, plan, checkpoint acceptance и любые уже
принятые результаты; он декомпозирует маршрут в конкретные bounded Work Orders с
входными/выходными условиями, гейтами и метриками.

Base: `control/post-mvp-route-r1 @ e05793cc8ff03b3b1af2d81b38e39d82cd7527d6`
(PR #37). Программа становится исполнимой после merge PR #37; до этого она может
читаться как план-кандидат. Слияние — строго после #37 (stacked).

## 1. Verified исходная позиция (2026-09-14)

| Факт | Значение |
|---|---|
| Canonical frontier | `NL5`, `next_work_order = NL5-001` (`READY`) |
| MVP | `NL4 = MVP COMPLETE`, NL0–NL4 ACCEPTED |
| PR #37 (route) | draft, open, head `e05793c`, base `main @ 50318c7`, ревью нет |
| PR #16 (worktree standard) | open, non-draft, stale — требует owner-решения |
| Счётчики | `physics_runs = 35`, `ai_campaigns = 0` (семантика не определена), `external_reproductions = 0`, `paid_compute = false` |
| Открытые owner-решения | лицензия собственных материалов NanoLab; судьба PR #16 |
| INFRA frontier | `INFRA2-001 = READY` (protected self-hosted CPU runner) |
| Измеренные компоненты | DNA hinge: `0b = 65.98°`, `11b = 73.93°`, `32b = 78.09°`, `53b = 132.36°`; `74b = NOT_MEASURED` |
| Task Bus | P2 заблокирован до P1.1–P1.4 (BUS-001 не принят) |

## 2. Gate 0 — приёмка control change PR #37 (ближайший рубеж)

Ничего из программы ниже не стартует раньше закрытия Gate 0, кроме чисто
подготовительных DOC-работ (§3 contract drafting, §9 options memo), которым
разрешено готовиться параллельно без merge-конфликтов.

```text
G0.1  Fresh Reviewer на substantive subject 59815fe ветки control/post-mvp-route-r1
G0.2  Fresh exact-head Verifier на финальный PR head e05793c (+TREE)
G0.3  Human Gate: merge PR #37 в main (owner)
G0.4  Post-merge regression: fresh main, ancestry, CONTROL_DEVELOPMENT --check-consistency,
      unittest suite, отсутствие duplicate keys/статусов
```

Правило гейта: если после G0.1/G0.2 в ветку добавляются коммиты — верификация
повторяется на новом head. Реализатор не self-accept.

## 3. Track NL5-001 — component library v0.1 (первая исполняемая продуктовая задача)

Маршрут: `NL5-001-A → B → C → D`; A и часть B — DOC/CODE, без новых физических
ранов. Каждому пункту соответствует отдельный bounded WO и ветка; canonical
Work ID создаётся самим WO (suffix `A..D` — planning decomposition, как в route §4).

### NL5-001-A — Release contract + rights gate

Scope (DOC/CODE):

1. Заморозить **component card schema v0.1** (JSON Schema + lint):
   `identity` (family/variant), `source_pins` (repo/commit/paths/digests),
   `protocol_pins` (engine, options, seeds, window), `observables`
   (именованные величины + distributions + n), `integrity`, `claim_ceiling`,
   `known_gaps`, `rights_mode`, `reproduction` (команды + ожидаемые значения),
   `card_schema_version`.
2. Зафиксировать layout пакета `nanolab-components-v0.1/` из route Phase B и
   правила versioning: пакет — semver; schema — отдельная версия; карточка
   ссылается на обе.
3. Форматы `RIGHTS.json` (per-item rights mode: `OWN`, `REFERENCE_ONLY`,
   `DOWNLOAD_ON_RUN`, …), `CITATION.cff`, `RELEASE_MANIFEST.json`
   (перечень файлов + SHA-256 + происхождение каждой строки данных).
4. Reproduction interface: минимальный CLI/скрипт `reproduce` из пакета без
   внутренних знаний репозитория.
5. **License gate**: owner выбирает лицензию собственных материалов
   (options memo — §9, D2). Пакет собирается и внутри с `UNDECIDED`, но
   публичный release невозможен до решения.

DoD: schema+lint проходят CI; контракт-документ заморожен; решение по лицензии
записано в `docs/control/` отдельным owner-decision record (или явно отложено
с блокировкой только публикации, не сборки).

### NL5-001-B — Сборка библиотеки (одно семейство, измеренные варианты)

Scope (CODE, zero new physics):

1. Семейство **`dna_hinge`** с вариантами `0b / 11b / 32b / 53b` — карточки
   генерируются из существующих E2 evidence blobs (digest-linked, без
   re-measurement); каждая наблюдаемая величина ссылается на run IDs и манифесты.
2. `74b` — отдельный bounded sub-WO `arm-manifest-v2`: timebox строго мал
   (диагностика + точечный fix). Если repair выходит за границы — вариант
   публикуется честно как `KNOWN_GAP / NOT_MEASURED` и не задерживает v0.1.
3. Сборка `RELEASE_MANIFEST.json`, `RIGHTS.json`, `CITATION.cff`, `VERSION`.

DoD: 100 % карточек schema-valid; все digest в карточках совпадают с
evidence-манифестами; `74b` имеет явный статус (measured с новым evidence ИЛИ
KNOWN_GAP с durable-записью, почему repair остановлен).

### NL5-001-C — Clean-room внутреннее воспроизведение пакета

Scope (CPU-BOUND, малый): fresh environment → install → source retrieval
(download-on-run, REFERENCE_ONLY, без durable cache) → compute → численное
сравнение с карточками. Это предвнешний smoke: проверяет, что пакет
самодостаточен, до привлечения внешнего исполнителя.

DoD: reproduction report с фактическими командами, расхождениями и их
классификацией (tolerance / environment / bug); баги пакета — repair до rc.

### NL5-001-D — Review + release candidate

Reviewer (MEDIUM+) на пакет и evidence; `FIX_REQUIRED` — repair с Repair Map.
Успех → tag `v0.1.0-rc` → Human Gate на публичную публикацию (публикация
отдельно от merge кода: rc может существовать в Git до public release).

DoD: REVIEWER PASS; rc tag; зафиксированное решение owner о канале публикации
(GitHub Release / ветка / сайт) — или явное «rc only, публикация позже».

## 4. Track NL5-002 — external reproduction (закрывает NL5)

Каталожная граница NL5: **«validated component package receives external
reproduction»**.

1. **NL5-002-A protocol (DOC)**: инструкция исполнителю «с нуля»: fresh env →
   exact package/version → install → source retrieval по rights-правилам →
   compute → analysis → численное сравнение (критерии из карточек/E2
   preregistration) → отчёт об отклонениях. Исполнителю доступны только пакет
   и публичные docs, не внутренние знания автора.
2. **NL5-002-B execution**: независимый исполнитель. Если реального
   независимого исполнителя нет — `WAIT_EXTERNAL` по правилам DIRECTOR:
   не имитировать независимость вторым именем в той же сессии.
3. **NL5-002-C repair/recheck** при portability gaps (только по фактам отчёта).
4. **NL5-002-D NL5 acceptance**: Reviewer + Director record + Human Gate;
   `external_reproductions: 0 → 1` только после принятия.

Риск-правило: внешний отчёт с расхождениями — не провал, а данные; критично
только различие класса «фундаментальная непереносимость» (stop-условие route §5).

## 5. Параллельная capability-линия INFRA2 → INFRA3

Не владеет scientific truth; не закрывает NL*; не блокирует NL5.

```text
INFRA2-001 (READY)  protected self-hosted CPU runner: labels, non-root isolated
                    workspace, jobs только по разрешённому dispatch route
INFRA3-001/002      reproducible scientific executor = INFRA MVP:
                    pinned source → env → job → logs/artifacts → SHA-256 manifest
                    → Git evidence; малый E1 end-to-end без ручной настройки машины
```

Sync-точки: INFRA3 желательно готов к кампаниям NL6-001/E5 (repeatable run,
единый job contract), но E5 не ждёт INFRA дольше отдельного owner-решения.
Task Bus P2 не активируется (P1.1–P1.4 не закрыты; BUS-001 — отдельная линия).

## 6. Track NL6-001 / E5 — driven DNA component (после принятия NL5)

Отдельный **HIGH scientific WO**; Reviewer + Verifier + Director.

Preregistration `E5_PROTO_R1` замораживается до confirmatory runs:

- bounded question: воспроизводимый управляемый цикл проверенного hinge при
  явном внешнем воздействии и нагрузке, в пределах модели;
- actuation convention: тип воздействия (например, гармонический trapping на
  выбранных частицах), точка приложения, амплитуда/протокол;
- load definition и energy/input convention;
- observables: state/angle распределения по фазам цикла;
- **frozen success/failure rule** — до confirmatory данных;
- return/reversibility метрика; repeated cycles (N фиксировано в протоколе);
- integrity/failure modes; budget (CPU-окно по образцу E2 — общий бюджет
  кампании фиксируется заранее); stop conditions.

Цикл: protocol → pilot → confirmatory → analysis → review. Номенклатура:
**externally driven DNA component**; claim ceiling вычислительный; никаких
заявлений о моторе/нанороботе/автономности.

## 7. Track NL6-002 / E3-R2 — richer-space AI benchmark (после E5)

Предусловие: валидированное E5 design space
(геометрия × сила привода × точка приложения × нагрузка × условия).

Freeze-правила benchmark: одинаковый бюджет и информация у всех стратегий;
`random` и `grid` baselines обязательны; `optimization/BO` если применимо;
`LLM-guided`; стоимость LLM/compute в отчёте; **fresh-seed anti-selection-bias
revalidation победителя**; `NO_ADVANTAGE` — полноценный результат (прецедент
E3-R1: claimed advantage аннулирован revalidation).

Счётчик `ai_campaigns` инкрементируется здесь по семантике, установленной
housekeeping-задачей H2 (§9): без утверждённой семантики значение не меняется.

## 8. Track NL7 → вход в NL8

NL7-001 composition: `validated driven component + второй валидированный
элемент/интерфейс → composed mechanism`; проверяются coupling, back-reaction,
нагрузки, распространение отказов; reduced models сверяются с detailed evidence.

Условные ветви: **E4 targeted** — открывается только конкретным вопросом о
free-energy landscape/переходах из E5/NL7; **E6 atomistic/materials** — позднее
расширение либо ранний подъём только при сильном внешнем спросе (stop/branch
условия — route §5). Вход в NL8 — по лестнице:
measured structure → validated component → driven component → composed
mechanism → energy/control/cycle/failures → specialized nanomachine study.

## 9. Owner decision register + housekeeping

| ID | Решение | Когда нужно | По умолчанию |
|---|---|---|---|
| D1 | Merge PR #37 (после G0.1–G0.2) | сейчас | — |
| D2 | Лицензия собственных материалов: код (MIT / Apache-2.0), docs/data (CC BY 4.0) — options memo готовит NL5-001-A | до публичного release v0.1 | сборка идёт, публикация заблокирована |
| D3 | Судьба PR #16 (supersede/rebase/close с record) | до или сразу после G0 | отдельный housekeeping PR |
| D4 | Назначение внешнего исполнителя NL5-002 | после NL5-001-C | WAIT_EXTERNAL |
| D5 | Утверждение `E5_PROTO_R1` (бюджет, N циклов, пороги) | перед confirmatory E5 | — |
| D6 | Бюджет E3-R2 (включая LLM-токены) | перед E3-R2 | — |
| D7 | Разрешение EARLY-E6 по внешнему спросу | по спросу | E6 не активен |

Housekeeping (малые bounded WO, не блокируют друг друга):

- **H1** PR #16 disposition (D3).
- **H2** `ai_campaigns` reconciliation: сначала зафиксировать семантику счётчика
  (предложение: «число завершённых AI-strategy benchmark campaigns, исполненных
  под frozen protocol»), затем audit evidence (E3-R1 → кандидат `1`) и только
  потом изменение значения с proof-ссылками. Без audit значение остаётся `0`.
- **H3** Branch protection / required checks для `main` (control/infra WO;
  желательно до публичного release, не бесконечный блокер).

## 10. Метрики программы

| Метрика | Базовое | Целевое |
|---|---|---|
| Card schema-valid rate | — | 100 % в v0.1 |
| Digest-coverage карточек (observables ↔ evidence) | — | 100 % |
| `external_reproductions` | 0 | 1 (NL5 закрыт) |
| `physics_runs` | 35 | рост только фактическими ранами; инкремент по evidence |
| E5 | — | замороженный цикл: pilot + confirmatory + frozen-rule verdict |
| E3-R2 | — | revalidated delta победителя ИЛИ NO_ADVANTAGE (оба — успех) |
| INFRA3 | false | малый E1 end-to-end без ручной настройки машины |
| Отрицательные результаты | — | сохраняются 100 % (harness invariant) |

## 11. Риски и митигации

| Риск | Митигация |
|---|---|
| Узкое место review (Fresh Reviewer/Verifier — внешние сессии) | батчить ревью; WAIT_EXTERNAL вместо имитации |
| Затяжка license-решения | пакет собирается с `UNDECIDED`; блокируется только публикация |
| `74b` repair расползается | timebox в sub-WO; fallback `KNOWN_GAP / NOT_MEASURED` без задержки v0.1 |
| Нет внешнего исполнителя NL5-002 | WAIT_EXTERNAL, Git — durable handoff; NL6 не стартует мимо stop-правил |
| Stacked-ветка: #37 ещё не смержен | программа merge'ится строго после #37; base branch в PR — `control/post-mvp-route-r1`, retarget на `main` после G0.3 |
| Спор о счётчиках (`ai_campaigns`) | H2: семантика → audit → значение; ничего «красивого, но недоказанного» |
| Выход E5 за бюджет | общий бюджет кампании фиксируется в `E5_PROTO_R1` до запуска; stop conditions |

## 12. Стоп-условия программы (наследуют route §5)

Пересмотр маршрута — новой roadmap revision, если: внешнее воспроизведение
показало фундаментальную непереносимость MVP; права не позволяют выпустить
полезный NL5-пакет; E5 невозможно корректно поставить без нового валидированного
physics layer; появился внешний пользователь, для которого E6 даёт существенно
больший проверяемый эффект; E5/NL7 упёрся в неразрешённую state/free-energy
неоднозначность (тогда первым открывается targeted E4).

Отрицательный результат не стирает R1.

## 13. Что эта программа НЕ делает

- не меняет acceptance criteria принятых NL0–NL4 и уже исполненных кампаний;
- не активирует E4/E6 и Task Bus P2;
- не даёт INFRA права объявлять scientific PASS;
- не назначает сроков/дат — порядок и bounded scope вместо календаря;
- не подставляет недоказанные значения счётчиков;
- merge любых веток программы — Human Gate.

## 14. Ближайшая очередь

```text
NOW     G0.1 Fresh Reviewer PR #37
        G0.2 Fresh exact-head Verifier (e05793c)
        G0.3 Human Gate merge PR #37        ← owner (D1)
        (параллельно, DOC-only): NL5-001-A contract drafting; H2 ai_campaigns;
                                  D2 license options memo; H1 PR #16 disposition

NEXT    NL5-001-A release contract + rights gate      (после G0)
        NL5-001-B library assembly (+74b bounded sub-WO)
        INFRA2-001 → INFRA3 (параллельно, capability line)

THEN    NL5-001-C clean-room reproduction
        NL5-001-D review + rc + publication gate
        NL5-002-A..D external reproduction → NL5 acceptance

AFTER   NL6-001 / E5 (HIGH scientific WO, frozen protocol)
        NL6-002 / E3-R2 (richer-space benchmark)
        NL7-001 composition → NL8
```
