# P1_RAW_REPLAY_COMMANDS_R1 — делегированная проверка сырых P1 артефактов (EX-NL5-002-E-R1)

```text
СТАТУС: OPEN — DELEGATED RAW REPLAY (единственный непокрытый сегмент верификации)
Автор этого файла: fresh Verifier, сессия на host outenemy, HEAD c14759a3fb4c0fc4896cb1c223274cb6b6e3a847
Дата: 2026-09-26
Кому: автор P1-машины (workspace ~/nanolab-platform-sensitivity-r1/P1, DESKTOP-QNAGSTI / WSL2)
```

## 0. Зачем это нужно

Сырые P1 артефакты (траектории/энергии/последние конфигурации) лежат ТОЛЬКО на
P1-машине в WSL2 FS (`~/nanolab-platform-sensitivity-r1/P1/runs`, в Git НЕ
публиковались — см. `raw_data_location` в `run_output_digests_p1.json`). Fresh
Reviewer и fresh Verifier на outenemy проверили P1 на уровне committed-артефактов
(анализ JSON, дайджест-манифест, паринг, статистика). Осталась ровно одна
непроверенная связь: **сырой P1 прогон → committed analysis JSON**. Этот файл
содержит точные команды и ожидаемые значения, чтобы автор P1-машины закрыл её.

Результат исполнения этого файла нужно опубликовать ответом-событием
(CONTINUATION/REVIEW event) с выводом команд: построчные `OK/MISMATCH` на все
20 прогонов × 3 файла × `replica_median_deg`.

## 1. Неизменяемые пины (нарушение любого = остановка и отчёт)

```text
workspace:        ~/nanolab-platform-sensitivity-r1/P1
package:          nanolab-components 0.1.1, release_manifest sha256
                  88c1f58061f15fde44225900f0577acbf2634d3f4a75fb96a2cedca24fd1bfef
analyzer:         $PKG/convention/analyze_hinge.py (packaged; замены ЗАПРЕЩЕНЫ)
engine commit:    00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591 (CPU, DOUBLE precision)
engine binary:    sha256 363356b9789fab8e0dab314bd66f92dc0e3a7e2cb3810e24b031614cebb45058
                  (значение из run_output_digests_p1.json; сверьте со своим build)
окна (steps):     0b = 200000 (50 кадров), 32b = 150000 (37 кадров)
сид:              заморожен в WO, НЕ менять (таблица ниже); retry сохраняет сид
```

## 2. Команда packaged-анализатора (для каждого финального прогона)

Скрипт-обёртка уже committed: `docs/work/executions/EX-NL5-002-E-R1/p1_recovery/analyze_all_p1.sh`
— прогнать его на P1-машине из чекаута той же ревизии (HEAD c14759a…):

```bash
bash docs/work/executions/EX-NL5-002-E-R1/p1_recovery/analyze_all_p1.sh
```

Он делает ровно следующее на каждый прогон (workspace `WS=~/nanolab-platform-sensitivity-r1/P1`,
пакет `PKG=$WS/package`, fallback-раскладка `PKG=$WS/../package`):

```bash
RD="$WS/runs/<RUN_ID>"                    # RUN_ID = финальный ID из колонки final ниже
# обработка exit-code файла как в analyze_all_p1.sh:
if [ -f "$RD/exit_code.txt" ] && ! grep -q "EXIT_CODE:" "$RD/exit_code.txt"; then
  printf 'EXIT_CODE: %s\n' "$(tr -dc '0-9-' < "$RD/exit_code.txt")" > "$RD/exit_code_formatted.txt"
  ECF="$RD/exit_code_formatted.txt"
else
  ECF="$RD/exit_code.txt"
fi
python3 "$PKG/convention/analyze_hinge.py" run \
  --trajectory "$RD/traj.dat" --energy "$RD/energy.dat" \
  --topology "$RD/<variant>.top" --manifest "$PKG/convention/arm-manifest-<variant>.json" \
  --variant "<variant>" --run-id "<RUN_ID>" --window "<STEPS>" \
  --exit-code-file "$ECF" \
  --report "analysis/<RUN_ID>_analysis.json"
```

ВАЖНО о именах файлов: дайджест-манифест записывает финальную траекторию под
ключом `trajectory.dat`, а анализатор читает `traj.dat` — на P1 это один и тот
же файл прогона (114.7 MB для 0b / ~86.8 MB для 32b, `grep -c '^t ='` = 50/37).
Если в `runs/<RUN_ID>/` лежат оба имени — сверить sha256 ОБЕИХ и указать в
отчёте; ожидаются идентичные.

## 3. Проверка хэшей сырых файлов (до анализатора)

```bash
cd ~/nanolab-platform-sensitivity-r1/P1/runs
for id in <финальные ID из таблицы>; do
  sha256sum "$id/traj.dat" "$id/trajectory.dat" "$id/hinge_energy.dat" "$id/last_conf.dat" 2>/dev/null
  stat -c '%s %n' "$id/traj.dat" "$id/hinge_energy.dat" "$id/last_conf.dat" 2>/dev/null
done
```

Сверить с колонками sha256/size ниже (файлы: финальная траектория [manifest-ключ
`trajectory.dat`, на диске `traj.dat`], энергия [ключ `hinge_energy.dat`, на
диске `energy.dat`], последняя конфигурация `last_conf.dat`).

## 4. Таблица 20 финальных P1 прогонов (ожидаемые значения)

| slot | final attempt | seed | variant | steps | trajectory.dat sha256 | size | hinge_energy.dat sha256 | size | last_conf.dat sha256 | size | ожид. replica_median_deg |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `PLATSENS-P1-0B-S001` | `PLATSENS-P1-0B-S001` | 1259289227 | 0b | 200000 | `07b2a08c322142b1768363baa567e382e8fb3e65a27d74e580e64e796ac93852` | 114715377 | `d5a719abfe655606dd8c6748a124ed0de29a482f51994558aa03f42831af1ab0` | 98049 | `78a1cd7d99c609e7b68ec5aeec149f51f3a749b685a93989ba5b1fb8827a602c` | 2293667 | 67.070882863 |
| `PLATSENS-P1-0B-S002` | `PLATSENS-P1-0B-S002` | 1358106528 | 0b | 200000 | `e0665e9d526fc9e1cdc520803fd431f7e5a3acdad095608fbddcd0b9306f8042` | 114713124 | `d497f66e5608f9c71cf11ba483ec65276f6fe2feebb6a7477f38bac5920868cc` | 98049 | `85be7afa967416d04202730b9c067b4a10aa5b927d49587ff444373c6d9eb6b6` | 2294632 | 65.413594877 |
| `PLATSENS-P1-0B-S003` | `PLATSENS-P1-0B-S003` | 1524307444 | 0b | 200000 | `1064c2931cb31fdee835e1d7696720558a7d387ba5c2766bbe994156661685ba` | 114689001 | `4e327476c99a1420891fbc62163d97751d43a5fcbf0d62a489ad887168b78e8d` | 98049 | `486bd3c03fb18ba47731623a0bac5f3671a4988d5ef25cc5e508b25a64770f37` | 2294034 | 68.744738874 |
| `PLATSENS-P1-0B-S004` | `PLATSENS-P1-0B-S004` | 601855227 | 0b | 200000 | `ccc6e0a58b435f43563f63e40a66c2919edfc98b95c64d4eeee320bc9ba5bb0f` | 114694252 | `0706e1bf0006bec5aeeb744580b038acc801007023e62e036ce74defe549f220` | 98049 | `5ea92c6e81619540c7ae85d5f947ecb68ea82e1ca2d7a50e33dc0da25a495094` | 2293536 | 66.246738850 |
| `PLATSENS-P1-0B-S005` | `PLATSENS-P1-0B-S005` | 274288237 | 0b | 200000 | `54cae6f81f6ce81dfcf92d57d4e5bdceb2082f2e3a57e7d69ac8dc1e42d10d26` | 114673948 | `b9a4b98827206e4cec12b8f1262aa1f35614ee2cc459bf857e5e69f59addceb5` | 98049 | `ac34c1e51dd10db1488b67f9110fe7b4beb95c6546451bffbdea6bc67c68607a` | 2293811 | 63.825786126 |
| `PLATSENS-P1-0B-S006` | `PLATSENS-P1-0B-S006` | 972234272 | 0b | 200000 | `510891af944cea32a93dce8e8fae19e2eeae5564d05cae1029e0df64af3d564a` | 114698416 | `006c187b714b7f92cef3fd8dfa93de6a9cd601ae59a927e8699b0ddfbc92eaa1` | 98049 | `6414f2a411b5bdc34f4be430f0bf29a0fd09b68a83f182c925f8d81f24bcef46` | 2293157 | 67.141783719 |
| `PLATSENS-P1-0B-S007` | `PLATSENS-P1-0B-S007` | 1934775205 | 0b | 200000 | `9b30dfc958fed62268e4cb063b4651efc2f06f2680a6361fffa4155cda886369` | 114708519 | `bb598c45a0701ac372909d9ae473e09c0934793ddd638f239205af39b89e430a` | 98049 | `b88ac50775a3020c62e4a7b9b3dd65203573f1f1365ecc41e74c03d26689476f` | 2293944 | 66.922485192 |
| `PLATSENS-P1-0B-S008` | `PLATSENS-P1-0B-S008` | 1747973984 | 0b | 200000 | `68ece6bdf9961c7c9e38d0a4f9c3b99aafb63260d2fdf3f82e0c736befd2ec61` | 114689227 | `6c7fb368fe083a4d25521d16bddc41664ab23444bfec248539c0fd2fd2e95435` | 98049 | `ca8df360f11eff5f308df6a5f4666a866c010d645210c324692d0554134a00be` | 2293898 | 67.615802220 |
| `PLATSENS-P1-0B-S009` | `PLATSENS-P1-0B-S009-R21` | 880427736 | 0b | 200000 | `b6bc8b7d4c90b2b98006bf91dde36f606bc036b830928832f1bf95314d46deaf` | 114687930 | `3917721f8e5a4171d9b8234431a5d1dbad346efcb34a9a091a2781bc54683450` | 98049 | `984393cd927ace5571ba7bb15335a3f02fb49d99c31c8546337e4734e553d29f` | 2293474 | 64.939909073 |
| `PLATSENS-P1-0B-S010` | `PLATSENS-P1-0B-S010-R14` | 744386736 | 0b | 200000 | `ca8ac0f9c15920d9af4deac0311eb7e474402ddb8076e99eeadc1b3af3a93535` | 114691501 | `70b1a30d026ccaf8f335014120a47abe09a5ed2d34355a4d0d982f2350cea315` | 98049 | `efac139e7532563ee256a8314efa4389b81c71723ec9f32e653c8b3cf67bce41` | 2293334 | 63.799736969 |
| `PLATSENS-P1-32B-S001` | `PLATSENS-P1-32B-S001-R14` | 1259289227 | 32b | 150000 | `03f27e852666283f8d73a404229172365b0d230ef564036e9366877fb8e362aa` | 86775703 | `83356ace1d93090e1d462a08d141589574719e6a23f698ff2ea07459b02e45e4` | 73549 | `7876e2d62370a08c9cca574ee5b6740fa44a89415153fe8b594410ed13649439` | 2345871 | 74.892180555 |
| `PLATSENS-P1-32B-S002` | `PLATSENS-P1-32B-S002-R13` | 1358106528 | 32b | 150000 | `6cbe20dcdf9fb2e2d4a686b73ee14492da98f19885e5179137ee422ba3cd02d9` | 86774364 | `bbe7d17500bf17461f9d9d30d3776b8c465615c36dd7ca0b09e1227224303ff5` | 73549 | `b2d1bfd0d1114ed702198b2d49f4f17a5a11ac51c606dd7be33283af92656b84` | 2345023 | 75.624640833 |
| `PLATSENS-P1-32B-S003` | `PLATSENS-P1-32B-S003-R13` | 1524307444 | 32b | 150000 | `ae6ad10a2951b494617d6d700c6714ad227d519ca0555043c2d190c018c98734` | 86767598 | `5e394916fc37a7b7a76b9a4f47228c8cbd5c63c53e54f583a1ef12efb2706254` | 73549 | `620f6c75a4036b6c46f2b96a61e0970eb31076b853e4cbca8e200e9ad20e0ab2` | 2345064 | 78.504573777 |
| `PLATSENS-P1-32B-S004` | `PLATSENS-P1-32B-S004-R13` | 601855227 | 32b | 150000 | `3c194ad9a25e085d7ce85d0ef96488a1495dc41bef313d30b47ab4fccd13c13a` | 86770713 | `ad9942f9281588690d47cf8a31030d0e6c7ad7cb27a75e65878390d66cbdde2b` | 73549 | `19fdfe44283e72c5d98d776da9c475eef049f75cec44c66faa4b893c63fbebaf` | 2345159 | 74.818110405 |
| `PLATSENS-P1-32B-S005` | `PLATSENS-P1-32B-S005-R13` | 274288237 | 32b | 150000 | `abbf68b689b6577fd575b07471161e6c8aca36982c987d1616161b1086a6260d` | 86776887 | `73d6e959a2d66bf7c961a13bff5483b2ff1af46387dba4f7e686c25f2b7f27b9` | 73549 | `bb37d7dafb1d594ea54dffb66acaa963a61e03a644f50da7b5786015eb0852cc` | 2344748 | 79.110521774 |
| `PLATSENS-P1-32B-S006` | `PLATSENS-P1-32B-S006-R13` | 972234272 | 32b | 150000 | `6bce6a0004cd5b7d15f2ee364d8509c7729a2478ca48dc943fc256aed640f2df` | 86776226 | `01aae493f7c0232ac1161eeb3019433e810494d497cc2112f365cd13edea61fb` | 73549 | `b42bcb389268a79d2e537b9382aae3159f6986f929a3b7be930d3bafbc78aaac` | 2344817 | 78.263485501 |
| `PLATSENS-P1-32B-S007` | `PLATSENS-P1-32B-S007` | 1934775205 | 32b | 150000 | `dd03339871d1c7e2da12e76e71fa64f341c34dabec9dbf778121705c2373aa65` | 86769781 | `e5fdec4d4c729e1841f027dbe0809d10bba84f4822bbe1a78612a61612c347e8` | 73549 | `c60405807b18ae20d03cf5d20818f71a9afbfec0501623a14251fe4f67b4ef5e` | 2345289 | 74.398740326 |
| `PLATSENS-P1-32B-S008` | `PLATSENS-P1-32B-S008` | 1747973984 | 32b | 150000 | `2fad14f04a6ce7beaa751350adc25b936eae8dc98c65e6c05b70dc75973c16ee` | 86776209 | `fc6afeb1958e0a28f53b9df8d932f3c8e5eaede9a401e59e790fbfa1f06502c1` | 73549 | `1ed7aaee47af1c1c50284217dcc75ffc2ebafdb990f0e6ce9301657a616d2f74` | 2345551 | 75.859814341 |
| `PLATSENS-P1-32B-S009` | `PLATSENS-P1-32B-S009` | 880427736 | 32b | 150000 | `01b9af36d18bc2eb5d369b9ef350cc5c2a829b54fb69431c474b311fa276e0fc` | 86773334 | `652a642a446df629407bb16e278be258c0cd16f226ed35b31be92eee2c3c3b0c` | 73549 | `d63d1dd95bdf42e211d011e6ebe36568ca4f95faf0c800ab659283decfc971f0` | 2344924 | 76.227108343 |
| `PLATSENS-P1-32B-S010` | `PLATSENS-P1-32B-S010` | 744386736 | 32b | 150000 | `c41d491700b4b17042e13e0eb11c4438ce0948c7dd547d9445205c07976c69dc` | 86763958 | `1326d1052041346860d2d6b6514755c432cbcd0de09dd090a0eb2b3a36d6febe` | 73549 | `3311354c338ac8e5aac591264dc51430ca5efb08bcc975d674e17a08852d2c22` | 2344833 | 77.417657026 |
## 5. Критерий закрытия делегированного шага

1. sha256+size всех 3×20 файлов совпали с таблицей (или расхождение
   `traj.dat`/`trajectory.dat` объяснено и оба хэша опубликованы).
2. Перегенерированный packaged-анализатором `replica_median_deg` совпал
   bit-exact со значением из таблицы (и с committed
   `evidence/p1/analysis/<final>_analysis.json`) на всех 20 прогонах.
3. Всё это опубликовано событием в Git (append-only) с сырым выводом команд.

До этого шага статус P1-лега: верифицировано на уровне committed-артефактов;
raw→median воспроизведение — ДЕЛЕГИРОВАНО (настоящий файл).
