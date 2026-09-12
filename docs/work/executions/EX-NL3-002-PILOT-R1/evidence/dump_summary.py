import json
for s in ("s001", "s002", "s003"):
    d = json.load(open(f"evidence/{s}-analysis.json"))
    print(s, "ref_pairs:", d["reference_pairs_count"], "frames:", d["frames_total"], "analysed:", d["frames_analysed"],
          "E first/last:", round(d["energy"]["total_energy_first"], 4), round(d["energy"]["total_energy_last"], 4),
          "max_disp:", round(d["max_displacement"], 3),
          "pf0:", d["frames"][0]["pairs_fraction"], "pf_last:", d["frames"][-1]["pairs_fraction"],
          "lbf_last:", d["frames"][-1]["long_bond_fraction"])
