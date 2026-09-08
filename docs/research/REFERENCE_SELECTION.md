# NL0-001 — Выбор воспроизводимых эталонов E1/E2

Статус: **IMPLEMENTER RECOMMENDATION / REVIEW REQUIRED**. Исполнение: `EX-NL0-001-R1`. Научные симуляции в этой работе не запускались.

## Решение

```text
E1_SELECTED = oxDNA upstream DSDNA8 / MD quick regression fixture
E2_SELECTED = Shi–Castro–Arya DNA hinge family (0b, 11b, 32b, 53b, 74b)
S08_STATUS  = useful scientific reference, machine-input pack not located in inspected sources
```

E1 выбран как максимально маленький, полностью определённый и уже имеющий upstream numerical oracle пример. E2 выбран не по зрелищности, а потому что публикация и авторский GitHub-пакет дают семейство из пяти шарниров, caDNAno designs, pre-equilibrated oxDNA configurations/topologies, CPU/GPU inputs и подготовительные скрипты.

## E1 — проверенные кандидаты

| Кандидат | Доступные входы | Предзаданный reference output | Стоимость/сложность | Решение |
|---|---|---|---|---|
| **A. DSDNA8 / MD** | `dsdna8.top`, `init.dat`, `MD/quick_input` | `MD/quick_compare`: average energy column 2 = `-1.37970256144`, tolerance `0.15` | 16 nucleotides, 2 strands, CPU, `1e6` steps | **SELECTED** |
| B. SSDNA15 / MD | `ssdna15.top`, `init.dat`, `quick_input` | two `ColumnAverage` checks in `quick_compare` | 15-nt single strand, CPU, `1e6` steps | READY fallback |
| C. HAIRPIN | topology/config, VMMC input, forces, run script, documentation | rich example/docs, but no equivalent tiny quick-regression oracle selected here | CPU VMMC, input requests `1e8` steps | useful later; too heavy for first E1 |

Все три находятся в официальном `lorenzo-rovigatti/oxDNA` и были проверены на pinned upstream commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`.

### Почему DSDNA8

Его задача в E1 — не доказать экспериментальную достоверность oxDNA, а доказать первый воспроизводимый NanoLab physical-model execution path: точные input → зафиксированный engine/model environment → run → quantitative upstream comparison → evidence. Это минимизирует число неизвестных до E2.

`quick_input` задаёт CPU backend, `1e6` steps, thermostat `john`, `T = 20C`, `dt = 0.005`, topology/configuration и интервалы вывода. `quick_compare` уже задаёт критерий upstream, поэтому NanoLab не будет изобретать threshold после просмотра результата.

### E1 claim ceiling

До внешнего физического сопоставления этот эталон допускает максимум `C1_COMPUTATIONAL_REPRODUCTION`. Успешный quick regression не является C4 physical validation.

## E2 — исходная проверка S08

S08: Sharma et al., *Characterizing the Motion of Jointed DNA Nanostructures Using a Coarse-Grained Model*, DOI `10.1021/acsnano.7b06470`.

**REPORTED:** статья изучает archetypal hinge/sliding joints и более сложные coupled joints в oxDNA и сообщает generally good agreement с experiment.

**OBSERVED IN SOURCE INSPECTION:** ACS Supporting Information перечисляет PDF с определениями углов/extensions и additional simulation results, а также movies. В проверенных ACS/author/search surfaces не найден отдельный machine-readable pack с caDNAno design, oxDNA topology/configuration и simulation input, достаточный для точного первого E2 без реконструкции.

**UNKNOWN:** существует ли такой пакет на неиндексируемом/непроверенном ресурсе или может быть предоставлен авторами.

Вывод: S08 остаётся хорошим научным reference, но **не выбран исполняемым E2 seed** в R1.

## E2 — выбранное семейство шарниров

Shi, Castro, Arya, *Conformational Dynamics of Mechanically Compliant DNA Nanostructures from Coarse-Grained Molecular Dynamics Simulations*, DOI `10.1021/acsnano.7b00242`.

### REPORTED в статье

- используется `oxDNA2`;
- исследуются пять hinge variants: `0b`, `11b`, `32b`, `53b`, `74b`;
- длины двух spring layers меняются между вариантами: 0/24, 11/35, 32/56, 53/77 и 74/84 bases;
- reported production conditions включают 298 K и 500 mM monovalent salt; используется average-base parametrization;
- анализируется hinge angle distribution/conformational dynamics;
- статья прямо указывает GitHub repository с simulation codes and data.

### OBSERVED в авторском GitHub

Pinned repository: `gauravarya77/DNA-hinge-simulations@23fd1ff7731e9017bd776f49206dc42d70d9fe91`.

В tree реально присутствуют:

```text
Design_Hinges/
  0b.json 11b.json 32b.json 53b.json 74b.json

Init_Hinges/
  cadnano_interface.py
  init_generator.py
  ini_demo/...

MD_Hinges/
  0b.top  0b.conf
  11b.top 11b.conf
  32b.top 32b.conf
  53b.top 53b.conf
  74b.top 74b.conf
  pro_CPU.in
  pro_GPU.in
```

Авторский README прямо описывает Design_Hinges как caDNAno designs, Init_Hinges как подготовку relaxed configurations, а MD_Hinges как inputs + pre-equilibrated structures для oxDNA MD.

`pro_CPU.in` в pinned tree задаёт `interaction_type = DNA2`, `salt_concentration = 0.5`, `T = 300K`, CPU/double и `2e7` steps. Различие 298 K в статье и 300 K в repository input должно быть **явно разрешено в NL0-003**, а не замолчано.

### Почему это хороший E2

Параметрическое семейство уже существует и соответствует нашей будущей задаче: проверять, как изменение compliant spring region влияет на распределение hinge angle. Мы можем сначала воспроизвести опубликованный variant, затем разрешить NanoLab изменять один строго определённый design parameter.

### E2 blockers до запуска

1. В pinned Git tree не обнаружен отдельный `LICENSE` файл. Public GitHub visibility не означает право перераспространять файлы. NL0-002 должен установить условия использования/redistribution до копирования upstream data в NanoLab.
2. NL0-003 должен зафиксировать конкретный первый hinge, observable definition, preparation/equilibration path и statistical acceptance procedure.
3. Старые scripts 2017 года требуют compatibility audit с выбранной современной oxDNA version; нельзя считать их автоматически executable сегодня.
4. Ни одна симуляция этого семейства NanoLab ещё не выполнялась.

## Дополнительный резервный E2 reference

Centola et al., *A rhythmically pulsing leaf-spring DNA-origami nanoengine that drives a passive follower* предоставляет особенно богатый reproducibility trail: Nanobase structure 196, Zenodo MD data (`10.5281/zenodo.8248808`) и public `sulcgroup/hinges` analysis repository. Это сильный будущий benchmark для driven/composite mechanics, но он сложнее выбранного семейства простых hinges и потому не должен вытеснять первый E2.

## Следующее действие

После независимого review NL0-001:

1. **NL0-002:** лицензии/redistribution audit для oxDNA fixture и `DNA-hinge-simulations`.
2. **NL0-003:** preregister E1 DSDNA8 exact protocol; отдельно оформить E2 first-hinge/observable protocol без запуска кампании.

NL0 целиком этим Work Order не закрывается.
