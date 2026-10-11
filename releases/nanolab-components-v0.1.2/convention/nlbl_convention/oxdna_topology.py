"""Strict parser and structural checks for oxDNA topology files (``.top``).

Format handled (as observed in the pinned Shi-Castro-Arya surfaces and in the
oxDNA upstream DSDNA8 fixture):

    <N> <S>                 header: nucleotide count, strand count
    <strand> <base> <n3> <n5>   x N lines, 0-based neighbour indices, -1 = none

Strands are listed contiguously from the 3'-terminal nucleotide to the 5'-
terminal nucleotide; ``n3`` points towards the strand's 3' side and ``n5``
towards the 5' side. All conventions are enforced mechanically; deviations are
errors, not warnings.
"""
from __future__ import annotations

VALID_BASES = ("A", "C", "G", "T")

class TopologyError(Exception):
    pass


class Topology:
    def __init__(self, nucleotides: int, strand_count: int, rows: list):
        self.nucleotides = nucleotides
        self.strand_count = strand_count
        self.rows = rows  # list of (strand_id, base, n3, n5)

    # ------------------------------------------------------------------ parse
    @classmethod
    def parse(cls, text: str) -> "Topology":
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            raise TopologyError("topology is empty")
        header = lines[0].split()
        if len(header) != 2:
            raise TopologyError("topology header must be '<N> <S>'")
        try:
            n, s = int(header[0]), int(header[1])
        except ValueError as exc:
            raise TopologyError(f"topology header not integers: {exc}") from exc
        if n <= 0 or s <= 0:
            raise TopologyError("topology header counts must be positive")
        body = lines[1:]
        if len(body) != n:
            raise TopologyError(f"topology declares {n} nucleotides but has {len(body)} rows")
        rows = []
        for idx, line in enumerate(body):
            parts = line.split()
            if len(parts) != 4:
                raise TopologyError(f"topology row {idx} does not have 4 columns")
            try:
                sid, n3, n5 = int(parts[0]), int(parts[2]), int(parts[3])
            except ValueError as exc:
                raise TopologyError(f"topology row {idx} has non-integer fields: {exc}") from exc
            base = parts[1]
            if base not in VALID_BASES:
                raise TopologyError(f"topology row {idx} has invalid base letter {base!r}")
            rows.append((sid, base, n3, n5))
        return cls(n, s, rows)

    @classmethod
    def from_file(cls, path) -> "Topology":
        with open(path, "r", encoding="utf-8", newline="") as handle:
            return cls.parse(handle.read())

    # ----------------------------------------------------------------- checks
    def check_chain_integrity(self) -> dict:
        """n3/n5 mutual consistency + per-strand decomposition into chains.

        Returns facts: linear/circular strand counts, per-strand lengths,
        base composition. Raises TopologyError on any inconsistency.
        """
        n = self.nucleotides
        strand_ids = [r[0] for r in self.rows]
        n3 = [r[2] for r in self.rows]
        n5 = [r[3] for r in self.rows]

        runs = []
        current, count = strand_ids[0], 1
        for sid in strand_ids[1:]:
            if sid == current:
                count += 1
            else:
                runs.append((current, count))
                current, count = sid, 1
        runs.append((current, count))
        if [r[0] for r in runs] != list(range(1, self.strand_count + 1)):
            raise TopologyError("strand ids are not contiguous runs 1..S in the file")
        if sum(r[1] for r in runs) != n:
            raise TopologyError("strand run lengths do not sum to the nucleotide count")

        for i in range(n):
            j, k = n3[i], n5[i]
            if j != -1:
                if not 0 <= j < n or n5[j] != i:
                    raise TopologyError(f"n3 link inconsistency at nucleotide {i}")
            if k != -1:
                if not 0 <= k < n or n3[k] != i:
                    raise TopologyError(f"n5 link inconsistency at nucleotide {i}")

        seen = [False] * n
        linear = []
        circular_ids = []
        i = 0
        while i < n:
            if n5[i] == -1 and not seen[i]:
                sid = strand_ids[i]
                length = 0
                j = i
                while j != -1:
                    if seen[j]:
                        raise TopologyError(f"chain revisit while walking strand {sid}")
                    seen[j] = True
                    if strand_ids[j] != sid:
                        raise TopologyError(f"chain crosses strand ids at nucleotide {j}")
                    length += 1
                    j = n3[j]
                linear.append((sid, length))
                i += 1
            else:
                i += 1
        remaining = [i for i in range(n) if not seen[i]]
        if remaining:
            circ_ids = sorted({strand_ids[i] for i in remaining})
            seen_ids = set()
            for i in remaining:
                if seen[i]:
                    continue
                sid = strand_ids[i]
                if sid in seen_ids:
                    continue
                # walk the closed loop
                start = i
                j = start
                length = 0
                while True:
                    if seen[j]:
                        raise TopologyError(f"circular strand {sid} walk left the strand")
                    seen[j] = True
                    if strand_ids[j] != sid:
                        raise TopologyError(f"circular strand {sid} walk crossed strand ids")
                    length += 1
                    j = n3[j]
                    if j == start:
                        break
                    if j == -1:
                        raise TopologyError(f"circular strand {sid} has a free end after all")
                seen_ids.add(sid)
                circular_ids.append((sid, length))
        if len(linear) + len(circular_ids) != self.strand_count:
            raise TopologyError("strand decomposition count does not match the declared strand count")

        base_counts = {}
        for _, base, _, _ in self.rows:
            base_counts[base] = base_counts.get(base, 0) + 1

        return {
            "linear_strands": len(linear),
            "circular_strands": len(circular_ids),
            "strand_lengths": sorted([length for _, length in linear] + [length for _, length in circular_ids], reverse=True),
            "circular_strand_ids": sorted(sid for sid, _ in circular_ids),
            "base_composition": dict(sorted(base_counts.items())),
        }


def topology_facts(topology: Topology) -> dict:
    """JSON-safe structural facts of a validated topology."""
    facts = topology.check_chain_integrity()
    return {
        "nucleotides": topology.nucleotides,
        "strands": topology.strand_count,
        "linear_strands": facts["linear_strands"],
        "circular_strands": facts["circular_strands"],
        "circular_strand_ids": facts["circular_strand_ids"],
        "strand_lengths_desc": facts["strand_lengths"],
        "base_composition": facts["base_composition"],
    }
