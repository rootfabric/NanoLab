"""Design-to-topology strand mapping (pre-E2 gap G2).

Associates caDNAno design strand paths with oxDNA topology strands by length
multisets, then classifies every association:

* ``exact``  -- one design path <-> one topology strand of equal length;
* ``split``  -- one design path decomposes into several topology strands
                (its length equals the sum of a subset of topology lengths);
* ``merge``  -- several design paths form one topology strand
                (a subset of design lengths sums to one topology length);
* ``unresolved`` -- no bounded subset-sum association was found (honest gap).

Base conservation (total design bases vs topology nucleotides) is checked and
reported. Length-only association is a v1 limitation recorded in the report;
sequence-level correspondence is future work and never guessed.

All reports are byte-deterministic JSON.
"""
from __future__ import annotations

import argparse

try:
    from .canonical import canonical_json
except ImportError:
    from canonical import canonical_json

from hinge_family.cadnano_design import Design, DesignError
from hinge_family.oxdna_topology import Topology, TopologyError

SUBSET_NODE_CAP = 200_000


class MappingError(Exception):
    pass


def design_paths(design: Design) -> list:
    """Maximal routed paths per strand type -> [{kind, index, length}]."""
    result = []
    for stype in ("scaf", "stap"):
        helix = {v["num"]: v for v in design.vstrands}
        cells = set()
        for v in design.vstrands:
            for i in range(len(v["scaf"])):
                if any(x != -1 for x in v[stype][i]):
                    cells.add((v["num"], i))
        starts = sorted(c for c in cells if helix[c[0]][stype][c[1]][0] == -1)
        index = 0
        for start in starts:
            length = 0
            node = start
            while node is not None:
                length += 1
                nh, nb = helix[node[0]][stype][node[1]][2:4]
                node = (nh, nb) if nh != -1 else None
            result.append({"kind": stype, "index": index, "length": length})
            index += 1
    result.sort(key=lambda e: (-e["length"], e["kind"], e["index"]))
    return result


def topology_strands(topology: Topology) -> list:
    """Contiguous strand runs -> [{strand_id, length}], sorted like design paths."""
    rows = topology.rows
    runs = []
    current, count = rows[0][0], 0
    for sid, *_ in rows:
        if sid == current:
            count += 1
        else:
            runs.append({"strand_id": current, "length": count})
            current, count = sid, 1
    runs.append({"strand_id": current, "length": count})
    runs.sort(key=lambda e: (-e["length"], e["strand_id"]))
    return runs


def _multiset_counter(items):
    counter = {}
    for item in items:
        counter[item] = counter.get(item, 0) + 1
    return counter


def _find_subset(total: int, pool: list) -> list:
    """Exact subset-sum over a multiset pool (list of (value, count)).
    Returns chosen values list (sorted ascending) or None. Bounded DFS."""
    nodes = [0]
    pool = sorted(pool)

    def dfs(pos: int, remaining: int, chosen: list):
        if nodes[0] > SUBSET_NODE_CAP:
            return None
        nodes[0] += 1
        if remaining == 0:
            return list(chosen)
        if pos >= len(pool) or pool[pos][0] > remaining:
            return None
        value, count = pool[pos]
        take_max = min(count, remaining // value)
        for take in range(take_max, -1, -1):
            if take:
                chosen.extend([value] * take)
            rest = dfs(pos + 1, remaining - take * value, chosen)
            if rest is not None:
                return rest
            if take:
                del chosen[-take:]
        return None

    return dfs(0, total, [])


def _remove_values(counter: dict, values: list) -> None:
    for v in values:
        counter[v] -= 1
        if counter[v] == 0:
            del counter[v]


def associate(design_lengths: list, topology_lengths: list) -> dict:
    """Deterministic length-multiset association."""
    d_counter = _multiset_counter(design_lengths)
    t_counter = _multiset_counter(topology_lengths)

    exact = []
    for value in sorted(d_counter):
        common = min(d_counter[value], t_counter.get(value, 0))
        if common:
            exact.append({"length": value, "count": common})
            d_counter[value] -= common
            t_counter[value] -= common
            if d_counter[value] == 0:
                del d_counter[value]
            if t_counter.get(value, 0) == 0:
                t_counter.pop(value, None)

    d_pool = sorted((v, c) for v, c in d_counter.items())
    t_pool = sorted((v, c) for v, c in t_counter.items())

    split_groups = []
    for value in sorted(d_counter, reverse=True):
        if d_counter.get(value, 0) <= 0:
            continue
        found = _find_subset(value, t_pool)
        if found:
            split_groups.append({"design_length": value, "topology_lengths": found})
            _remove_values(d_counter, [value])
            _remove_values(t_counter, found)
            t_pool = sorted((v, c) for v, c in t_counter.items())

    merge_groups = []
    for value in sorted(t_counter, reverse=True):
        if t_counter.get(value, 0) <= 0:
            continue
        found = _find_subset(value, d_pool)
        if found:
            merge_groups.append({"topology_length": value, "design_lengths": found})
            _remove_values(t_counter, [value])
            _remove_values(d_counter, found)
            d_pool = sorted((v, c) for v, c in d_counter.items())

    unresolved_design = sorted(d_counter.elements()) if hasattr(d_counter, "elements") else sorted(
        v for v, c in d_counter.items() for _ in range(c)
    )
    unresolved_topology = sorted(
        v for v, c in t_counter.items() for _ in range(c)
    )

    if unresolved_design or unresolved_topology:
        status = "PARTIAL_ASSOCIATION"
    elif split_groups or merge_groups:
        status = "FULLY_ASSOCIATED_WITH_TRANSFORMATIONS"
    else:
        status = "FULLY_ASSOCIATED_ONE_TO_ONE"
    return {
        "exact": exact,
        "split_groups": split_groups,
        "merge_groups": merge_groups,
        "unresolved_design_lengths": unresolved_design,
        "unresolved_topology_lengths": unresolved_topology,
        "status": status,
    }


def map_design_to_topology(design: Design, topology: Topology) -> dict:
    paths = design_paths(design)
    strands = topology_strands(topology)
    facts = design.structural_facts()
    top_facts = topology.check_chain_integrity()
    total_design = sum(p["length"] for p in paths)
    total_topology = sum(s["length"] for s in strands)
    association = associate([p["length"] for p in paths], [s["length"] for s in strands])
    if total_design != total_topology:
        conservation = {
            "status": "CONSERVATION_VIOLATION",
            "design_bases": total_design,
            "topology_nucleotides": total_topology,
        }
    else:
        conservation = {
            "status": "CONSERVED",
            "total": total_design,
        }
    return {
        "schema_version": 1,
        "kind": "design_topology_mapping",
        "design": {
            "name": design.name,
            "virtual_helices": facts["virtual_helices"],
            "scaffold_paths": facts["scaffold_paths"],
            "staple_paths": facts["staple_paths"],
            "paths_total": facts["scaffold_paths"] + facts["staple_paths"],
            "total_bases": facts["total_bases"],
        },
        "topology": {
            "strands": topology.strand_count,
            "nucleotides": topology.nucleotides,
            "linear_strands": top_facts["linear_strands"],
            "circular_strands": top_facts["circular_strands"],
        },
        "design_path_lengths": [p["length"] for p in paths],
        "topology_strand_lengths": [s["length"] for s in strands],
        "base_conservation": conservation,
        "association": association,
        "limitations": [
            "v1 associates by length multisets only; sequence-level correspondence is not asserted",
            "split/merge classification answers the count transformation (118 -> 112 class of gaps); per-base identity is out of scope",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="map caDNAno design paths to oxDNA topology strands")
    parser.add_argument("design_json")
    parser.add_argument("topology_path")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    design = Design.from_file(args.design_json)
    topology = Topology.from_file(args.topology_path)
    report = map_design_to_topology(design, topology)
    rendered = canonical_json(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
