"""Reader for the caDNAno design JSON surfaces of the hinge family.

Decoded vstrand cell semantics (verified by exhaustive bidirectional pointer
consistency on the pinned 0b design during EX-NL3-001-R1; see the R1 report):

    scaf[i] / stap[i] = [prev_helix, prev_base, next_helix, next_base]

* ``-1`` marks "no neighbour" (a path end); every other value is a coordinate
  pointing at another used cell (helix id, base index on that helix).
* A cell is *used* iff at least one of its four entries is not -1. Empty cells
  are exactly ``[-1, -1, -1, -1]``.
* Strand routing follows prev/next across helices; each maximal path is one
  covalent strand of the design.

Any pointer inconsistency is an error, never a warning.
"""
from __future__ import annotations


class DesignError(Exception):
    pass


class Design:
    def __init__(self, name: str, vstrands: list):
        self.name = name
        self.vstrands = vstrands

    @classmethod
    def parse(cls, text: str) -> "Design":
        import json

        try:
            data = json.loads(text)
        except ValueError as exc:
            raise DesignError(f"design is not valid JSON: {exc}") from exc
        if not isinstance(data, dict) or "vstrands" not in data:
            raise DesignError("design JSON must be an object with 'vstrands'")
        vstrands = data["vstrands"]
        if not isinstance(vstrands, list) or not vstrands:
            raise DesignError("design 'vstrands' must be a non-empty list")
        for v in vstrands:
            for key in ("num", "row", "col", "scaf", "stap"):
                if key not in v:
                    raise DesignError(f"vstrand missing key {key}")
            if len(v["scaf"]) != len(v["stap"]):
                raise DesignError(f"vstrand {v['num']} scaf/stap grids differ in length")
            for row in list(v["scaf"]) + list(v["stap"]):
                if not isinstance(row, list) or len(row) != 4:
                    raise DesignError(f"vstrand {v['num']} has a cell that is not a 4-list")
                if not all(isinstance(x, int) for x in row):
                    raise DesignError(f"vstrand {v['num']} has a cell with non-integer entries")
        helices = {v["num"]: v for v in vstrands}
        if len(helices) != len(vstrands):
            raise DesignError("duplicate vstrand nums")
        return cls(data.get("name", ""), vstrands)

    @classmethod
    def from_file(cls, path) -> "Design":
        with open(path, "r", encoding="utf-8", newline="") as handle:
            return cls.parse(handle.read())

    # ------------------------------------------------------------- internals
    def _used(self, vstrand, stype, i) -> bool:
        return any(x != -1 for x in vstrand[stype][i])

    def _cells(self, stype):
        cells = set()
        for v in self.vstrands:
            for i in range(len(v["scaf"])):
                if self._used(v, stype, i):
                    cells.add((v["num"], i))
        return cells

    def _check_routing(self, stype) -> dict:
        cells = self._cells(stype)
        helix = {v["num"]: v for v in self.vstrands}
        for (num, i) in cells:
            row = helix[num][stype][i]
            ph, pb, nh, nb = row
            if ph != -1:
                if ph not in helix or not 0 <= pb < len(helix[ph][stype]):
                    raise DesignError(f"{stype} cell ({num},{i}) points to an out-of-range prev coordinate")
                if (ph, pb) not in cells:
                    raise DesignError(f"{stype} cell ({num},{i}) points to an unused prev cell")
                back = helix[ph][stype][pb]
                if back[2:4] != [num, i]:
                    raise DesignError(f"{stype} cell ({num},{i}) prev link is not bidirectional")
            if nh != -1:
                if nh not in helix or not 0 <= nb < len(helix[nh][stype]):
                    raise DesignError(f"{stype} cell ({num},{i}) points to an out-of-range next coordinate")
                if (nh, nb) not in cells:
                    raise DesignError(f"{stype} cell ({num},{i}) points to an unused next cell")
                back = helix[nh][stype][nb]
                if back[0:2] != [num, i]:
                    raise DesignError(f"{stype} cell ({num},{i}) next link is not bidirectional")

        # walk maximal paths from cells without a prev pointer
        starts = sorted(c for c in cells if helix[c[0]][stype][c[1]][0] == -1)
        seen = set()
        path_lengths = []
        for start in starts:
            node = start
            length = 0
            while node is not None and node not in seen:
                seen.add(node)
                length += 1
                nh, nb = helix[node[0]][stype][node[1]][2:4]
                node = (nh, nb) if nh != -1 else None
            path_lengths.append(length)
        cyclic = len(cells) - len(seen)
        if cyclic:
            raise DesignError(f"{stype} routing contains cyclic segments ({cyclic} cells)")
        if sum(path_lengths) != len(cells):
            raise DesignError(f"{stype} path walk did not cover every used cell")
        crossover_steps = 0
        for (num, i) in sorted(cells):
            nh = helix[num][stype][i][2]
            if nh != -1 and nh != num:
                crossover_steps += 1
        used_count = len(cells)
        return {
            "cells": used_count,
            "paths": len(path_lengths),
            "path_lengths_desc": sorted(path_lengths, reverse=True),
            "crossover_steps": crossover_steps,
        }

    # ----------------------------------------------------------------- facts
    def structural_facts(self) -> dict:
        scaf = self._check_routing("scaf")
        stap = self._check_routing("stap")
        both = scaf_only = stap_only = 0
        ssdna_runs = {}
        for v in self.vstrands:
            run = 0
            for i in range(len(v["scaf"])):
                s = self._used(v, "scaf", i)
                t = self._used(v, "stap", i)
                if s and t:
                    both += 1
                    if run:
                        key = str(run)
                        ssdna_runs[key] = ssdna_runs.get(key, 0) + 1
                        run = 0
                elif s or t:
                    if s:
                        scaf_only += 1
                    if t:
                        stap_only += 1
                    run += 1
                else:
                    if run:
                        key = str(run)
                        ssdna_runs[key] = ssdna_runs.get(key, 0) + 1
                        run = 0
            if run:
                key = str(run)
                ssdna_runs[key] = ssdna_runs.get(key, 0) + 1
        return {
            "design_name": self.name,
            "virtual_helices": len(self.vstrands),
            "scaffold_bases": scaf["cells"],
            "staple_bases": stap["cells"],
            "total_bases": scaf["cells"] + stap["cells"],
            "scaffold_paths": scaf["paths"],
            "staple_paths": stap["paths"],
            "scaffold_path_lengths_desc": scaf["path_lengths_desc"],
            "staple_path_lengths_desc": stap["path_lengths_desc"],
            "crossover_steps": {"scaffold": scaf["crossover_steps"], "staple": stap["crossover_steps"]},
            "paired_positions": both,
            "single_stranded_positions": scaf_only + stap_only,
            "ssdna_run_histogram": dict(sorted(ssdna_runs.items())),
        }
