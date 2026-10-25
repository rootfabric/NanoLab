# U2_READINESS_R1 — Готовность внешнего исполнителя U2 (outenemy) к приёму frozen release package (C0)

- `record_kind`: U2_READINESS_ASSESSMENT (machine-readable двойник: `U2_READINESS_R1.json`)
- `issuer_class`: EXTERNAL_PREFLIGHT_IMPLEMENTER_U2 (реальная отдельная DSH-сессия `ce662f0f-4b0d-4388-b3e0-96e018fecf94`; НЕ author U1-сессия)
- Дата: 2026-10-25 · Исполнение: `EX-NL5-F03-U2-READINESS-R1` · WO: `WO-NL5-F03-U2-READINESS-R1` · Issue #84 (программа #81)
- `claim_class`: C0_SOFTWARE_ONLY · **scientific_runs = 0** · oxDNA/MD не запускались

## 0. Пины наблюдения

```text
origin/main (fresh fetch) = 3b567ae33f247b182b2ae451d2cc4598a9e76019 (= BASE, эпоха не менялась)
FROZEN F2 HEAD            = 60da9a846511265a8ac7564da088c3d74cb073f0  (предок main: ДА)
FROZEN F2 TREE            = e565c8a6cee9e829fac14008ebc9c2ea1609931d  (пересчитан)
dispatch HEAD             = 7e1e0bce1346d1884dc314409e812f7f8e815296
```

## 1. Вердикт

```text
READINESS   = READY_FOR_DISPATCH_PREP  (C0-часть: состав пакета, пины, дайджесты, схемы — проверены)
LIVE U2 LEG = BLOCKED_NO_U2_ACCESS_FROM_SESSION  (честно; ничего не имитировалось)
```

Ограничения (явные):

1. Live-проверки на outenemy (identity/fingerprint, диск, systemd, дайджесты бинарника, репетиция пакета) из этой сессии **невозможны**: `~/.ssh/config` не существует, `outenemy` в `~/.ssh/known_hosts` отсутствует (0 вхождений). Они вынесены в чек-лист §7.
2. Все host-факты outenemy датированы 2026-10-10/11 → **STALE_BY_TIME** (14–15 дней) до live-перепроверки.
3. Просмотренная review-версия тулинга `9ded2bf7` (2026-10-11) — **не текущий main**: после ревью в main попал narrow-repair m-1 (`BLOCKED_MALFORMED_SPEC`, ветка коммита `5ce0a63`; diff `9ded2bf7..main` по `scripts/r2` — только `cli.py` 45 строк + 29 строк тестов). PASS ревью валиден **только для своего пина**; свежий Reviewer/Verifier на текущем HEAD для r2-цепочки не публиковался.
4. **U2-ready ≠ R2_ACTIVE ≠ scientific authorization**: R2 = WAITING_HOST / NOT_ACTIVE, AUTHOR_U1 = NOT_ASSIGNED, гейты U1–U5 / NC-U1..U5 не исполнялись, обе ноги кампании HARD_BLOCKED за цепочкой S→F→D/R/V→A и HUMAN_PROTECTED_WRITER.
5. Dispatch-authority запись (schema v3, lifecycle A) для реальной кампании **не существует**; prior self-tests использовали только синтетическую fixture-authority.
6. Перенесено из F01 (F01-F-1): Reviewer(F2) PASS `d63eb5c` и Verifier(F2) VERIFIED `f12d0b4` существуют append-only на своих ветках, но **не смержены в main**.

## 2. STALE-оценка существующих U2 receipts

Метод: git-анкорованные факты пересчитаны независимо сегодня; тулинг-состояние сверено `git diff` по цепочке reviewed HEAD → PR head → main; host-факты датированы и помечены STALE_BY_TIME; dispatch-цепочка сверена с dryrun-манифестом и F01 handoff.

| Receipt | Дата/пин | Статус | Обоснование |
|---|---|---|---|
| `EX-INFRA3-U2-OUTENEMY-READINESS-R1` (+8 evidence JSON: fingerprint, build, smoke, systemd, check-host, release selftest, run-u2 e2e) | 2026-10-10/11 | **HOST_STATE_STALE_BY_TIME** | Host-факты 14–15 дней стары; из этой сессии непроверяемы; каждый подлежит live-перепроверке (§7) |
| `FRESH_REVIEW_U2_READINESS_R1.{md,json}` | 2026-10-11, reviewed HEAD `9ded2bf7` / tree `520c0e92`, base `8bf7e3a` | **GIT_ANCHORED_VALID_BUT_SUPERSEDED_HEAD** | PASS неизменяем и валиден для своего subject; `9ded2bf7` — строгий предок PR head `3b6ead17` и main `3b567ae` (проверено `merge-base --is-ancestor`, оба exit 0); после ревью добавлен m-1 repair — прямой ответ на рекомендацию ревьюера, регрессий не известно, но PASS не пиннует текущий main |
| PR #55 `infra/u2-outenemy-executor-readiness-r1` | merged:true, head `3b6ead17` | GIT_ANCHORED_VALID | Смержен в текущий main |
| FROZEN_R2 package F2 | 2026-10-06 (`60da9a8`), Director record `a2f7304` | GIT_ANCHORED_VALID | F2 **предшествует** readiness-линии; identity 3/3 пересчитана сегодня (§3) |
| `docs/infra/NL5_V02_DRYRUN_MANIFEST_R1.json` | issue #65 | PARTIALLY_STALE_DISPATCH_CHAIN_VIEW | Его снимок R=MISSING/V=MISSING устарел: F01 нашёл Reviewer(F2)/Verifier(F2) тапы (append-only, не в main); A-записи по-прежнему нет → dispatch остаётся BLOCKED, направление не менялось |

**Ответ на вопрос WO** («F2 заморожены ПОСЛЕ readiness-ревью?»): **НЕТ** — F2 (2026-10-06) заморожен **ДО** ревью (2026-10-11); ревью само проверило неизменность frozen-блобов (claim 6). Новее ревью: (а) m-1 repair в main (HEAD ревью superseded), (б) 14–15 дней возможного host-дрейфа, (в) F01 handoff 2026-10-25.

## 3. Аудит frozen release package (F2) — готовность к доставке на U2

Целостность пересчитана независимо в этой сессии: для **каждого** файла, изменённого коммитом `60da9a8` (9 файлов): `git rev-parse 60da9a8:<path>` == `git rev-parse main:<path>` → **9/9 SAME**; canonical SHA-256 трёх ключевых блобов = **3/3 MATCH** с `docs/evidence/NL5-V02-FREEZE/DIRECTOR_FREEZE_R2.json`:

| Роль | Путь | GIT_BLOB_SHA1 | CANONICAL_BLOB_SHA256 |
|---|---|---|---|
| protocol | `docs/research/NANOLAB_REPRO_V0_2_FROZEN_R2.md` | `4835719622ba…482b4b222d408` | `2658ee3e0cd0…fc997c6d` |
| authoritative_contract | `…/repro-v0-2-freeze-contract-FROZEN_R2.json` | `d6a9ccde4d1d…46cf70b` | `7e6476544e82…c45b3a` |
| seed_record | `…/repro-v0-2-seed-record-FROZEN_R2.json` | `0164e0e3f5dd…21d2c76` | `8e844bff299d…7fa7e28` |

Сопутствующие артефакты F2 (frozen-gate-PASS-R2, delta-check, m1-negative-control, seed-record-identity, REPAIR_MAP_M1) — blob-SHA1 в JSON-двойнике, все SAME на main.

### Достаточность входов для независимой сборки на U2: **SUFFICIENT_WITH_TWO_PROVISIONS**

Достаточно (всё digest-пиновано):
- **Engine**: upstream `lorenzo-rovigatti/oxDNA` @ `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591` (GPL-3.0, DOWNLOAD_ON_SETUP); флаги Release / DOUBLE=ON / CUDA=OFF / MPI=OFF (environment_pins контракта).
- **Научные входы** (контракт = single source of truth): confirmatory seeds 0b/32b n=64 (primary), 11b/53b n=10 (control); bootstrap seeds (10000, PAIRED, `random.Random`, quantile linear); replacement pools 12/12/2/2 + курсоры `next_candidate_index`; `replacement_pool_sha256 369a63c0…`, `seed_record_r4_sha256 51a88192…`; 34 исторических исключения; integer rounding policy; `attempt_id_rule`; бюджеты (296/56/352, ≤560 ч/платформа, CPU-only).
- **Analyzer pins**: nanolab-components 0.1.0, `analyze_hinge.py` (frozen convention), quantile linear.
- **Digest-цепочка доставки**: F2 head/tree + blob-SHA1 + canonical SHA-256 → U2 может верифицировать каждый полученный байт.
- **Транспорт** репетирован: `releases/nanolab-components` (v0.1.1 на outenemy: plan 5/5 ok, ровно 7 задокументированных pyc-findings; v0.1.2 repair — PR #56, цель 0 errors) + `r2.cli run-u2` (пин хоста, обязательная schema-v3 authority, fixture ceiling, protected launch gate, append-only ledger).

Два условия (provisions):
- **P-1 (сеть/стейджинг)**: исходники engine — DOWNLOAD_ON_SETUP: нужен либо egress до pinned-коммита, либо pre-staged tree с `source_tree_sha256 = b1742ce9…22a911c`; маршрут должен быть доказан live (L-09).
- **P-2 (версия пакета)**: точный package ref (v0.1.2 по PR #56, либо v0.1.1 + 7 принятых pyc-findings) должен быть зафиксирован в будущей authority-записи — сейчас он нигде не запиннен.

## 4. Platform independence matrix

| Аспект | U1 (author) | U2 (outenemy, external) | Статус U2-фактов |
|---|---|---|---|
| OS floor (native Linux, virt=none, native fs, systemd) | UNASSIGNED | Записан 2026-10-11: Ubuntu 22.04.5, kernel 5.15.0-190, 64×E5-2698 v3 | STALE → L-01 |
| Host-role guard | `validate_native_u1` должен PASS | `check-host` → NOT_ELIGIBLE exit 2 = канонический негативный контроль; `validate_u2_host` — только для `run-u2` | STALE → L-02 (контроль ролей зашит кодом — git-анкор) |
| Engine identity | свежая сборка из `00dc7fb9` (gate U1) | кэш-сборка: binary sha256 `6effd00a…5126b78`, size 3 380 728, source_tree `b1742ce9…` | STALE → L-04 |
| Launcher | `systemd-run` (system manager) | ТОЛЬКО `systemd-run --user` (Linger=yes; system manager требует root, RC 1) | STALE → L-05 |
| Release package ingress | тот же verify | v0.1.1 репетирован (7 pyc-findings); v0.1.2 на U2 **не** репетирован | → L-08 |
| Dispatch authority | одна запись на обе ноги | отсутствие/невалидность → `BLOCKED_NO_DISPATCH_AUTHORITY` exit 3 | A-записи нет → F05 |
| Storage layout | `~/nanolab/*` (создать при выделении U1) | каталоги существуют 2026-10-11; проекция ~15 GB/нога, запас ~2×, порог 80% | STALE → L-03 |
| Windows/WSL | исключены (HISTORICAL_ONLY, decree 2026-09-27) | исключены | в силе |
| Научная граница | нога `EX-NL5-REPRO-V0-2-U1-R1` | нога `EX-NL5-REPRO-V0-2-U2-R1`; `external_reproductions=0`; U2 никогда не author | в силе; `PLATFORM_INSENSITIVE` ≠ «все платформы дают одинаковые траектории» |

Требование физической различимости машин: `physical_distinctness_required = true`.

## 5. Storage / evidence capacity инвентаризация

Источник — только существующие evidence (2026-10-10/11) и frozen-бюджеты; live-замеры из сессии невозможны.

```text
U2 layout      = ~/nanolab/{workspaces,raw,cache,tools}, owner uid 1001 (record)
Raw проекция   = ~15 GB / U2-ногу; запас ~2x; контрольный порог 80%
Engine cache   = build tree + provenance + log; binary 3 380 728 B (sha256 6effd00a…)
Бюджет кампании= confirmatory 296 + replacement cap 56 = max 352 runs; ≤560 wall-hours/платформа;
                 CPU-only; paid compute без отдельной owner-авторизации ЗАПРЕЩЁН
Git-политика   = в Git только compact evidence (JSON/MD с дайджестами); raw живёт в
                 ~/nanolab/raw/<execution-id>/<attempt-id>/ и переиспользуется только
                 через digest + provenance
```

Неизвестно из этой сессии (заполняется live L-03/L-04): фактический свободный/используемый диск, inode, реальный raw-след 352 runs, дрейф с 2026-10-11.

## 6. Raw-manifest (PROPOSED_NON_NORMATIVE), job IDs, safe paths, изоляция

**Raw-manifest**: машинно-читаемой схемы в репозитории нет; есть только prose-конвенция (WO-INFRA3-R2-ACTIVATION-R1 §2.3: path + sha256 + size + producer + retention, digest манифеста — в ledger). Предлагаемая схема (поля): `schema_version, kind='nanolab_raw_artifact_manifest', manifest_id, execution_id, attempt_id, artifact_path, artifact_sha256, artifact_size_bytes, producer (команда/бинарник + его digest + host + uid), subject_head, subject_tree, storage_location, retention (класс + срок + authority удаления), created_at_utc, scientific_outcome=NOT_EVALUATED`. Инварианты: 1 манифест на attempt; digest манифеста в append-only ledger; никакое переиспользование raw без digest+provenance; коррекции — новым манифестом со ссылкой на старый `manifest_id`. **Принятие схемы — отдельный bounded WO с fresh Reviewer + distinct Verifier**; здесь только предложение.

**Unique job IDs**: ноги кампании зарезервированы (`EX-NL5-REPRO-V0-2-U1-R1` / `…-U2-R1`, обе BLOCKED); `attempt_id = <run_base> | <run_base>-R<n>`, глобально уникальны навсегда; ledger append-only с `AttemptReuseError` на любое переиспользование (включая FAILED_TECHNICAL); pair-level one-shot replacement (R4.1 M-4), identity только из frozen-пула по курсору, никогда outcome-driven. Tooling-предохранители на U2 (`run-u2`): `BLOCKED_NO_DISPATCH_AUTHORITY` / `BLOCKED_NON_FIXTURE_SPEC` / `BLOCKED_LAUNCH_GATE_PROTECTED_WRITER` / `BLOCKED_FROZEN_CAMPAIGN_ID` / `BLOCKED_HOST_U2` / `BLOCKED_MALFORMED_SPEC` (m-1, уже в main) — все exit 3/2, fail-closed. Fixture-пространство имён отдельно (`EX-U2-TOOLING-FIXTURE-*`). **DO NOT REUSE A FAILED RUN ID.**

**Safe paths/permissions**: `run_base/raw_root/workspace` обязаны резолвиться внутри `~/nanolab/**` и не указывать на author/общие temp-локации; владелец — сервис-аккаунт U2 (record uid 1001); нет world-writable; нет root; ledger append-only; raw — write-once; запуск только `systemd-run --user`; CI и научный executor не делят lifecycle.

**Изоляция от author-данных**: U2 получает ТОЛЬКО F2 (Git, digest-пинованный), release package (git-archive export пиннованного ref) и pinned oxDNA-исходники (или digest-верифицированный staged tree). U2 НИКОГДА не получает: U1 raw/промежуточные данные, копии author-workspace, author-креденшалы. Обратно — только digest+provenance записи под независимым review; `scientific_outcome=NOT_EVALUATED` на U2-поверхностях. U1-guard не ослаблен (аддитивный diff ветки readiness, проверено review claim 5; `run` на outenemy → `BLOCKED_HOST` exit 2).

## 7. Live-чек-лист для owner/оператора U2 (обязателен до F07)

| # | Проверка | Критерий PASS | Обновляемая запись |
|---|---|---|---|
| L-01 | Свежий `r2.cli fingerprint` на outenemy; diff vs `u2-fingerprint-R1.json` (hostname=outenemy, Ubuntu 22.04.5, kernel 5.15.0-190, 64×E5-2698 v3, virt=none) | совпадение пинов либо owner-принятый и перезапинненный дрейф | dated fingerprint record |
| L-02 | `check-host` → NOT_ELIGIBLE exit 2; `r2.cli run` → BLOCKED_HOST exit 2; `validate_u2_host` проходит только в `run-u2` | все три исхода воспроизведены | dated negative-control record |
| L-03 | `df -h`/`df -i` на ФС `~/nanolab`; каталоги workspaces/raw/cache/tools; владелец=сервис-аккаунт; нет world-writable | free ≥ 2× ~15 GB; порог 80% настроен | measured capacity record (замена проекции) |
| L-04 | sha256 `~/nanolab/cache/oxdna-build-r2-u2/bin/oxDNA` == `6effd00a…5126b78`, size 3 380 728; source_tree `b1742ce9…` | дайджесты совпали; при дрейфе — пересборка из пина + новая provenance | dated engine identity record |
| L-05 | `systemctl --user is-system-running`=active; `Linger=yes`; `systemd-run --user` RC 0; отказ system manager сохранён | user-путь работает, job переживает закрытие сессии | dated systemd record |
| L-06 | Свежий checkout exact main (≥ `3b567ae`): `python3 -m unittest discover -s tests -t .` — все OK (≥631, вкл. 3 `BLOCKED_MALFORMED_SPEC`); рекомендуется свежий Reviewer/Verifier на новом head | suite зелёный на запинненном head; superseded-head gap закрыт или признан | exact-head tooling verification |
| L-07 | Репетиции гейтов `run-u2` на синтетической fixture: happy-path OK; негативы — missing authority exit 3, non-fixture exit 3, frozen campaign id exit 3, malformed spec `BLOCKED_MALFORMED_SPEC` exit 3 | все гейты fail-closed и именованные | dated run-u2 rehearsal |
| L-08 | Свежий git-archive export пиннованного package ref (v0.1.2 по PR #56) → `reproduce.py verify` = 0 errors; зафиксировать финальный package pin для authority | verify 0 errors на пиннованном ref | dated package verification + pin decision |
| L-09 | Ingress/egress: `git fetch` origin на outenemy; получение oxDNA `00dc7fb9` (fetch или digest-staged); согласованный канал возврата evidence | оба направления доказаны с дайджестами | dated connectivity record |
| L-10 | Raw-manifest pilot: одна fixture-попытка с манифестом по §6 в `~/nanolab/raw/...`; все поля заполнены, digest в ledger | схема полна, ledger связан | pilot manifest (adopt-before-campaign) |
| L-11 | `timedatectl` на outenemy: NTP активен | синхронизировано | заметка в dated readiness evidence |
| L-12 | Аттестация независимости: нет общих workspace/креденшалов/SSH-trust с author U1; физическая различимость подтверждена owner | attestation записана | owner attestation record |

## 8. Честные границы

- Ни один live-факт outenemy не проверялся и не воспроизводился в этой сессии — только датирован и классифицирован; имитации доступа нет (STOP-условие WO соблюдено).
- Git-факты пересчитаны локально из origin/fetch — это проверка целостности, а не повторная верификация host-состояния.
- Научных запусков нет; «smoke» из prior evidence — технический тест, не научное утверждение.
- Вердикт `READY_FOR_DISPATCH_PREP` относится к C0-логистике; он не активирует R2, не назначает U1, не меняет canonical state и не является научной авторизацией.

## 9. Handoff

→ **F05 authority planning**: authority-запись (schema v3, lifecycle A) должна запиннить цепочку F2 + package ref (P-2) + пины обеих платформ; L-01…L-12 должны быть зелёными до F07 при общих разрешениях. Принятие raw-manifest схемы — отдельный bounded WO (fresh Reviewer + distinct Verifier). Merge этой ветки в main — Human Gate (Director).
