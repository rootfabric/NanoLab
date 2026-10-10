# nanolab-components 0.1.2

Проверенная библиотека DNA-нанокомпонентов (семейство compliant DNA hinge,
Shi–Castro–Arya) с опубликованным контрактом воспроизведения.

## Быстрый старт

```text
python3 reproduction/reproduce.py verify   # целостность пакета (20+ файлов)
python3 reproduction/reproduce.py plan     # план по карточкам
```

Далее — `reproduction/README.md` (полный порядок) и
`convention/OBSERVABLE_CONVENTION_V0_1.md` (frozen конвенция измерения с
оракулом `convention/analyze_hinge.py frame0`).

## Состав

- `families/dna_hinge/cards/*.card.json` — карточки вариантов
  (0b/11b/32b/53b MEASURED; 74b NOT_MEASURED/KNOWN_GAP);
- `convention/` — frozen observable convention: спецификация, референс-реализация
  (`nlbl_convention/`, stdlib-only), frozen arm-манифесты, CLI-анализатор
  (frame0-оракул / анализ реплики / классификация кампании);
- `reproduction/` — контракт воспроизведения: правило
  `NANOLAB_REPRO_V0_1_REPLICA_ENVELOPE`, helper `reproduce.py` (verify/plan);
- `reports/`, `provenance/` — опубликованные evidence-производные и digest-пины
  upstream-источников;
- `schema/` — схемы карточки/прав/манифеста; `RIGHTS.json`, `CITATION.cff`.

## Права

Код пакета Apache-2.0; документация и производные данные NanoLab CC-BY-4.0;
upstream-файлы шарнира не включены (REFERENCE_ONLY, download-on-run по exact
pinned commit; см. `RIGHTS.json` и карточки). Движок oxDNA — сторонний проект;
источники: https://github.com/lorenzo-rovigatti/oxDNA (пин — в карточках).

## История ревизий

- **0.1.0** — первый публичный релиз (NL5-001).
- **0.1.1** — repair по portability findings внешнего воспроизведения NL5-002-B-R1
  (verdikt INCONCLUSIVE): опубликована frozen конвенция измерения
  (`convention/`: arm manifests, референс-реализация, оракул, спецификация),
  добавлены URL/tarball-путь движка, корневой README, пояснение overlay
  `print_energy_every=100`. Научные значения карточек
  (expected/envelopes/пороги) не изменялись.
- **0.1.2** — packaging-only repair (WO-NL5-V012-PACKAGING-PYC-REPAIR-R1,
  мотив — контракт R2 gate U2): из `RELEASE_MANIFEST.json` исключены 7
  сгенерированных CPython-артефактов `__pycache__/*.pyc`, ошибочно попавших в
  манифест v0.1.1 и ломавших fail-closed проверку `reproduce.py verify` на
  любой свежей копии пакета. Научные файлы (convention/, карточки, RIGHTS,
  схемы, протоколы) байт-в-байт идентичны 0.1.1; намерение фиксировано
  регрессионным тестом фильтра в `release.card_lint`.
