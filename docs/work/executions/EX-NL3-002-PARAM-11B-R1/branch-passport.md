# Branch Passport — work/nl3-002-param-11b-r1 (EX-NL3-002-PARAM-11B-R1)

- Base: `5940c8ab3f5d90169a17c423c653f4c004a6efc8` (main tip: WO-NL3-002-PARAM preregistration).
- Worktree: `C:\NanoLab\nl3-002-param-11b`.
- Work Order: NL3-002-PARAM (параметрическая серия E2, вариант 11b из четырёх); протокол — `docs/research/E2_PROTO_R1.md` (FROZEN, наследуется без изменений: steps/seeds/гейты/статистика) + per-variant добавления из `docs/work/WO-NL3-002-PARAM.md`.
- Scope: научные прогоны PARAM-11B-S001..S003 на варианте `11b` (авторские `11b.top` + `11b.conf` verbatim, download-on-run по pinned commit `23fd1ff`, digest-гейт: size + blob SHA-1 обязательны; SHA-256 пин NOT_VERIFIED → вычислить и записать в evidence при первой загрузке); манифест рук `arm-manifest-11b.json` по arm-manifest-v1 ДО прогонов (definition-before-data; нет двух доминирующих блоков → BLOCKED варианта); observables v2 mutual + integrity v1; гейты §4; статистика §6. Outcome = измеренные распределения; интерпретаций нет; acceptance — Director после review.
- Runtime: WSL Ubuntu engine `/home/yurig/nl1-002/build-oxdna-cpu/bin/oxDNA` (source commit `00dc7fb9a25bbd8cadbc7503ee2b9f38983c6591`, verified); Windows Python 3.11 для анализа/CLI; прогоны в `/home/yurig/nl3-002-param-11b/runs/PARAM-11B-S00X/` (вне Git, манифесты SHA-256/size обязательны).
- Budget: ≤ 3.5 ч wall/реплика, 3 параллельные реплики, ≤ 4 ч на вариант + анализ ≤ 1 ч.
- Роль сессии: IMPLEMENTER (fresh-сессия). Reviewer (батчевый, один на серию) и Director — отдельные сессии; merge в main — Human Gate; `project/state.json` не меняется.
