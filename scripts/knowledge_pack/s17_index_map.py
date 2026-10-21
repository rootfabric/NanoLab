"""Deterministic nucleotide index-space map for pinned oxDNA topologies (S17 R2).

WO-PREP-S17-R2 stage B. For one (topology, configuration) pair this module
builds the complete, reproducible map

    global 0-based particle index  <->  (strand_id, position-in-strand, base,
    n3, n5, strand class [linear/circular], terminal flags, [base-pair neighbor
    if derivable])

and resolves a list of analysis indices (e.g. the ``sulcgroup/hinges`` arm
reference indices and the ``T7_force.txt`` trap pair) against that map. The
convention is stated explicitly: oxDNA topology rows and configuration
particles are **0-based** (``.top`` body row *i* describes particle *i*;
``-1`` neighbour means "no neighbour"). Index claims are only ever reported
relative to a pinned (digest-verified) topology file, and the caller must pass
the expected SHA-256 — a wrong pin is a hard error, never a warning.

Claim discipline: this module proves *index-space structure only*. Whether an
index corresponds to a named molecular feature (arm, port, terminator) is a
separate, externally supplied interpretation and is recorded with an explicit
status (SOURCE_CONFIRMED / INFERRED_CANDIDATE / UNVERIFIED / UNKNOWN).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from hinge_family.oxdna_topology import Topology, TopologyError

INDEX_STATUSES = ("SOURCE_CONFIRMED", "INFERRED_CANDIDATE", "UNVERIFIED", "UNKNOWN")


class IndexMapError(Exception):
    """Raised on fail-closed violations of the index-map contract."""


@dataclass(frozen=True)
class StrandSpan:
    strand_id: int
    first_index: int
    last_index: int
    length: int
    circular: bool


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_topology_verified(path: Path, expected_sha256: str) -> Topology:
    """Parse a topology only if its bytes match the pinned digest (fail-closed)."""
    data = Path(path).read_bytes()
    actual = sha256_bytes(data)
    if actual != expected_sha256:
        raise IndexMapError(
            f"topology pin mismatch for {path}: expected {expected_sha256}, got {actual}"
        )
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IndexMapError(f"topology is not valid UTF-8: {exc}") from exc
    try:
        return Topology.parse(text)
    except TopologyError as exc:
        raise IndexMapError(f"pinned topology failed strict parse: {exc}") from exc


def strand_spans(top: Topology) -> list[StrandSpan]:
    """Decompose row order into per-strand spans with circularity detection.

    A strand is circular when its last row's n5 points back to the strand's
    first row index (and the first row's n3 points to the last row index).
    """
    spans: list[StrandSpan] = []
    cur = None
    start = 0
    rows = top.rows
    for i, (sid, _base, n3, n5) in enumerate(rows):
        if sid != cur:
            if cur is not None:
                spans.append(_make_span(rows, cur, start, i - 1))
            cur = sid
            start = i
    if cur is None:
        raise IndexMapError("topology has no rows")
    spans.append(_make_span(rows, cur, start, len(rows) - 1))
    return spans


def _make_span(rows, sid: int, first: int, last: int) -> StrandSpan:
    length = last - first + 1
    circular = rows[last][3] == first and rows[first][2] == last
    return StrandSpan(strand_id=sid, first_index=first, last_index=last,
                      length=length, circular=circular)


def build_index_map(top: Topology) -> dict:
    """Full deterministic map: per-index records plus per-strand summary."""
    spans = strand_spans(top)
    span_of: dict[int, StrandSpan] = {}
    for sp in spans:
        if sp.strand_id in span_of:
            raise IndexMapError(f"duplicate non-contiguous strand id {sp.strand_id}")
        span_of[sp.strand_id] = sp
    if top.strand_count != len(spans):
        raise IndexMapError(
            f"header strand count {top.strand_count} != contiguity parse {len(spans)}"
        )
    records = []
    for i, (sid, base, n3, n5) in enumerate(top.rows):
        sp = span_of[sid]
        records.append({
            "particle": i,
            "strand_id": sid,
            "position_in_strand": i - sp.first_index,
            "base": base,
            "n3": n3,
            "n5": n5,
            "strand_circular": sp.circular,
            "is_3prime_terminal_of_file_strand": n3 == -1,
            "is_5prime_terminal_of_file_strand": n5 == -1,
        })
    return {
        "convention": "0-based particle index; .top body row i == particle i; -1 = no neighbour",
        "nucleotides": top.nucleotides,
        "strand_count": top.strand_count,
        "strands": [sp.__dict__ for sp in spans],
        "records": records,
    }


def resolve_indices(top: Topology, indices: list[int], namespace_sha256: str) -> dict:
    """Resolve concrete indices against the map with full provenance."""
    imap = build_index_map(top)
    out = []
    for idx in indices:
        if not isinstance(idx, int) or isinstance(idx, bool):
            raise IndexMapError(f"index must be a plain integer, got {idx!r}")
        if idx < 0:
            raise IndexMapError(f"negative index {idx} (space is 0-based)")
        if idx >= top.nucleotides:
            raise IndexMapError(
                f"index {idx} is out of bounds for a {top.nucleotides}-particle namespace"
            )
        rec = imap["records"][idx]
        out.append(rec)
    return {
        "namespace_sha256": namespace_sha256,
        "nucleotides": top.nucleotides,
        "convention": imap["convention"],
        "resolved": out,
    }


def index_map_digest(top: Topology) -> str:
    """Deterministic digest of the whole map (stable across re-parses)."""
    imap = build_index_map(top)
    canonical = json.dumps(imap, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def base_pair_pairs(top: Topology) -> set[tuple[int, int]]:
    """Derive (i, j) base-pair candidates from a strict oxDNA2 duplex rule.

    In oxDNA2 *topologies* produced by the standard converters, a duplex
    nucleotide i (with both neighbours set) is paired to a nucleotide j such
    that i is j's "strand-opposite" — this cannot be proven from the .top
    alone for arbitrary files, so this helper only supports the conservative
    structural fact used by the S17 preflight: pairs are derived from the
    paired .dat geometry externally. Kept out of claims: this module never
    asserts pairing.
    """
    raise NotImplementedError(
        "base pairing is not derivable from a bare oxDNA .top; supply the "
        "configuration and use geometric preflight instead"
    )
