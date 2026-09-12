# Control Record — U-obs-1: SI retrieval + манифест рук 0b — решение R1

Статус: DECIDED (2026-09-12, Director по миссии владельца «…решение по U-obs-1 (получение SI / манифест рук 0b до E2-PROTO-R1)»).

## Факты

- Статья семейства идентифицирована: Shi, Castro, Arya — «Conformational Dynamics of Mechanically Compliant DNA Nanostructures from Coarse-Grained Molecular Dynamics Simulations», ACS Nano 11(5):4617 (2017), DOI `10.1021/acsnano.7b00242` — совпадает с pinned DOI из NL0-001.
- Автоматическая попытка digest-gated загрузки SI (2026-09-12, 2 канонических URL `pubs.acs.org/doi/suppl/10.1021/acsnano.7b00242/suppl_file/nn7b00242_si_00{1,2}.pdf`) заблокирована publisher anti-bot (ответ — HTML-челлендж ~5.7 KB вместо PDF). Обход anti-bot не предпринимался и не будет предприниматься автоматически (политика: никакого скрейпинг-уклонения).

## Decision

1. **SI-pinning откладывается**, не блокирует пилот и E2-PROTO-R1. Владелец может вручную (браузером) скачать SI и передать файл: тогда — digest-пин (SHA-256 + git-blob SHA-1), извлечение определения угла в текст решения (только факты + дайджесты; сами байты SI в Git не попадают, REFERENCE_ONLY, re-download по digest при использовании).
2. **Путь E2-PROTO-R1 (основной)**: манифест рук 0b строится **first-principles** — детерминированный вывод групп нуклеотидов из design+topology (геометрические кластеры двух жёстких плеч вдоль оси шарнира), реализуется скриптом в замороженном tooling, пререгистрируется в `E2-PROTO-R1` ДО confirmatory прогонов с явной пометкой «не из SI». Если SI появится позже — `E2_OBSERVABLES_R2` supersedes (старые данные остаются, сравнение двух определений — отдельная ревизия).
3. **Пилот не требует финального манифеста**: stability/cost/integrity + draft-proxy угол (помечен non-confirmatory).

## Открытым остаётся

U-obs-1 формально остаётся открытым до появления SI или до первого confirmatory-анализа на first-principles манифесте — тогда он закрывается решением Director в `E2-PROTO-R1` с фиксацией использованного пути.
