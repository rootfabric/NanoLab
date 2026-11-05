# ATOMISTIC-PRODUCT-R1 — готовый инженерный кандидат

Дата: 2026-11-05. PR: https://github.com/rootfabric/NanoLab/pull/96.

## Поставленный результат

Самостоятельная P0–P6 продуктовая дорожная карта, machine product plan/state и operational tasks. P0–P3 ведут к проверенному атомистическому сценарию, приложению, ограниченному конструктору и сравнению вариантов; P4–P6 — исследования с условиями продолжения. Историческая DNA/NL линия сохранена. Старый NL5 MISMATCH не переименован в успех. В очередь добавлены потребитель, демонстрация, бюджет и остановки; неизменные blockers не требуют повторных аудитов.

Работает локальное Linux/Python приложение: параметры Cu FCC структуры → реальная BFGS-релаксация → Langevin MD через pinned ASE EMT → траектория, энергия/температура, полный byte-exact ZIP с protocol/environment/manifest. Просмотр: вращение, масштаб, playback, выбор кадра, energy plot. Реальные MD не замаскированы под mock. Протокол и источник первого запуска опубликованы до вычислений.

**Delivery: IMPLEMENTED_DEMO / READY_FOR_HUMAN_GATE. Scientific outcome: NOT_EVALUATED. P0 material validation остаётся OPEN.** P1 software delivery не является принятым material benchmark. Произвольный атомный редактор, импорт прежних расчётов, произвольные материалы и квантовая физика не реализованы. До merge этот пакет — candidate, а не canonical main acceptance.

## Проверенный subject

- Published product HEAD: `71bc62102cc36bf49b04d40d81d3070d87cccad6`.
- Published product TREE: `f86af90728797541594396ac0bef0964d9f8dd28`.
- Первый frozen adapter HEAD: `599ba8d1f089d74dc5f67a33011cba020f6df57a`, TREE `d1e1359ba0e06230aeed0197f2b548f6e9b7f1d1`.
- Canonical base: `3b567ae33f247b182b2ae451d2cc4598a9e76019`; FLOW dependency: `ddbc5cb68a5b720cbbaaadeba96f087d82d82732`.
- После product subject добавлены только delivery evidence, документация и фактические operational/product статусы; final publication требует отдельной delta verification и CI.

Локальные implementation commits в исторических child receipts обозначают реально существовавшие execution subjects. Публикация через GitHub API меняет commit author/identity; опубликованные trees побайтово сверены с локальными. Научные raw manifests привязаны к доступным published subjects, а final independent verdicts — к опубликованному product HEAD выше.

## Реальные расчёты

| Run | Проверка | Атомы / MD steps | Wall s | Raw bytes |
|---|---|---|---:|---:|
| cu-emt-demo-r1-001 | Первое исполнение CLI/adapter | 32 / 50 | 0.655380319 | 66811 |
| ui-22337abacb144a9e88191bfc167c383b | Настоящий Chromium form → API → worker → playback/export | 32 / 10 | 0.655919482 | 38678 |
| cu-emt-verifier-r1-001 | Отдельная verifier session, чистый clone, те же dependency pins | 32 / 50 | 0.655633602 | 66797 |

Итого: 3/8 attempts, 1.966933403 s/1200 s, 172286 raw bytes/2 GiB; все COMPLETED, активных reservations нет. Новых NL5/E5 runs, платного compute и изменений U1/U2 нет. Все роли использовали общий хост: это независимые software sessions, не внешнее физическое воспроизведение.

При первом расчёте релаксация сошлась за 10 шагов; finite-difference ошибка силы 7.71e-10 eV/Å при заранее заданном допуске 1e-4. Это внутренняя численная проверка той же модели, не material validation. В verifier повторе trajectory/config/relaxation/numerical-control/environment совпали побайтово; numerical series/fields совпали, ресурсные метаданные отличаются. Не заявляется побитовая переносимость на другие платформы.

## Независимые проверки

- `/root/flow_review`, Sol: исходный FLOW review FAIL, bounded repair PASS; затем broad product review FAIL с тремя конкретными замечаниями и repaired exact-subject PASS. Исходные отрицательные отчёты сохранены в `review/`.
- `/root/product_verifier`, Sol: fresh clone, пять CI-проверок, adversarial recheck, digest readback, один реальный повтор; VERIFIER PASS на published product subject.
- Implementers Sol: `/root/product_roadmap`, `/root/atomistic_backend`, `/root/atomistic_ui`, `/root/flow_repair`; coordinator `/root`. Реальные task paths получены от launcher; это не proof независимых физических хостов.

Исправления: FLOW executable→regular publication classification; полный byte-exact ZIP вместо неполного пересериализованного набора; уникальность failed run ID во всей mission, включая другие output roots/старые ledger rows/concurrency; исправлена HTML step lattice для friction default.

Полный suite: **1059 tests, OK, 1 explicit real-MD skip**; реальная MD проверена отдельно в трёх явно учтённых запусках. JSON/consistency/execution integrity/workflow security — PASS. Hosted CI на product subject: https://github.com/rootfabric/NanoLab/actions/runs/42014866243/job/127202750641 — SUCCESS.

Browser: zero page errors, реальный запуск/воспроизведение/вращение/zoom/скачивание ZIP. Отдельная mock mobile QA: 390 px без горизонтального overflow. Реальный screenshot: `evidence/ui-real.png`; GUI запуск подтверждён `evidence/http-ui.json`, protocol/config и raw в `evidence/ui-run/`. Нельзя выдавать mock QA за фактическую физику.

## Durable evidence

- CLI pilot: `examples/atomistic/runs/cu-emt-demo-r1-001/`.
- UI raw: `evidence/ui-run/`, исходный скачанный архив `evidence/result.zip`, screenshot `evidence/ui-real.png`.
- Verifier raw: `evidence/verifier-run/`; логи, baseline defects и исправления компаратора: `evidence/verifier-logs/`.
- Независимые отчёты: `review/`; общий SHA-256/size map: `artifacts.manifest.json`.

Копии evidence сохраняют исходные байты. Абсолютные scratch paths внутри исходных receipts описывают место исполнения; перечисленные здесь пути — durable Git locations этих же байтов. Initial overly strict verifier comparison full metrics bytes и mock spy counting git subprocess сохранены как ошибки проверки, исправлены без повторного MD.

## Следующее действие

Проверить final publication delta и CI, затем owner merge PR #96. Следующая содержательная задача — `ATOMISTIC-REFERENCE-PREP`: один доступный материальный эталон, независимые ожидаемые свойства и применимость потенциала. Максимум два содержательных source passes без нового факта; затем альтернативный кандидат или явный blocker. Принятые программные возможности повторно не реализовывать. Инструкция запуска: `docs/atomistic/UI.md`.
