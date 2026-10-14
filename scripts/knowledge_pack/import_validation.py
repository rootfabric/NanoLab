"""Deterministic import validation for pinned oxDNA source inputs (PREP-S17).

WO-PREP-S17-R1. Validates that an audited source pair (oxDNA topology
``.top`` + configuration ``.dat``) parses with the project's strict parsers
(reused from ``hinge_family`` — no parser duplication), that the pair is
consistent (particle counts match), and that a re-import from the same bytes
yields a byte-identical canonical structural digest.

Claim ceiling: a successful import is `PINNED_IMPORT_VERIFIED` evidence about
FILE STRUCTURE only. It is not a simulation, not a reproduction, and never
`MODEL_REPRODUCED`.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from hinge_family.oxdna_conf import Configuration, ConfError
from hinge_family.oxdna_topology import Topology, TopologyError


class ImportValidationError(Exception):
    """Raised when a pinned import pair cannot be validated."""


@dataclass
class ImportPairResult:
    topology_path: str
    configuration_path: str
    topology_sha256: str
    configuration_sha256: str
    topology_size_bytes: int
    configuration_size_bytes: int
    nucleotides: int
    strand_count: int
    conf_particles: int
    conf_time: str
    conf_box: list
    counts_match: bool
    base_composition: dict
    strand_length_histogram: dict
    chain_facts: dict
    structural_digest: str
    deterministic_reimport: bool
    errors: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and self.counts_match and self.deterministic_reimport

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_structural_digest(top: Topology, conf: Configuration) -> tuple:
    """Order-stable content summary of a parsed pair.

    Independent of whitespace and of the conf header comment lines; dependent
    on the actual parsed structural content.
    """
    bases: dict = {}
    lengths: dict = {}
    current_strand: object = None
    current_len = 0
    for strand_id, base, _n3, _n5 in top.rows:
        bases[base] = bases.get(base, 0) + 1
        if strand_id != current_strand:
            if current_strand is not None:
                lengths[current_len] = lengths.get(current_len, 0) + 1
            current_strand = strand_id
            current_len = 1
        else:
            current_len += 1
    if current_strand is not None:
        lengths[current_len] = lengths.get(current_len, 0) + 1
    summary = {
        "nucleotides": top.nucleotides,
        "strand_count": top.strand_count,
        "base_composition": dict(sorted(bases.items())),
        "strand_length_histogram": {str(k): v for k, v in sorted(lengths.items())},
        "conf_particles": len(conf.particles),
        "conf_time": str(conf.time),
        "conf_box": [float(x) for x in conf.box],
    }
    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest(), summary


def import_paired(top_path: Path, conf_path: Path) -> ImportPairResult:
    """Validate one (topology, configuration) pair. Raises on hard failures."""
    top_path, conf_path = Path(top_path), Path(conf_path)
    top_bytes = top_path.read_bytes()
    conf_bytes = conf_path.read_bytes()
    top_text = top_bytes.decode("utf-8")
    conf_text = conf_bytes.decode("utf-8")

    errors: list = []
    top = conf = None
    digest1 = summary = None
    try:
        top = Topology.parse(top_text)
    except TopologyError as exc:
        errors.append(f"topology parse error: {exc}")
    try:
        conf = Configuration.parse(conf_text)
    except ConfError as exc:
        errors.append(f"configuration parse error: {exc}")

    counts_match = False
    deterministic = False
    chain_facts: dict = {}
    if top is not None and conf is not None:
        try:
            chain_facts = top.check_chain_integrity()
        except TopologyError as exc:
            errors.append(f"topology chain integrity error: {exc}")
        counts_match = top.nucleotides == len(conf.particles)
        if not counts_match:
            errors.append(
                f"count mismatch: topology declares {top.nucleotides} nucleotides, "
                f"configuration has {len(conf.particles)} particles"
            )
        digest1, summary = canonical_structural_digest(top, conf)
        # Deterministic re-import: parse the same bytes again from scratch.
        top2 = Topology.parse(top_text)
        conf2 = Configuration.parse(conf_text)
        digest2, _ = canonical_structural_digest(top2, conf2)
        deterministic = digest1 == digest2
        if not deterministic:
            errors.append("non-deterministic re-import: structural digests differ")

    return ImportPairResult(
        topology_path=str(top_path),
        configuration_path=str(conf_path),
        topology_sha256=hashlib.sha256(top_bytes).hexdigest(),
        configuration_sha256=hashlib.sha256(conf_bytes).hexdigest(),
        topology_size_bytes=len(top_bytes),
        configuration_size_bytes=len(conf_bytes),
        nucleotides=top.nucleotides if top else -1,
        strand_count=top.strand_count if top else -1,
        conf_particles=len(conf.particles) if conf else -1,
        conf_time=str(conf.time) if conf else "UNKNOWN",
        conf_box=[float(x) for x in conf.box] if conf else [],
        counts_match=counts_match,
        base_composition=summary["base_composition"] if summary else {},
        strand_length_histogram=summary["strand_length_histogram"] if summary else {},
        chain_facts=chain_facts,
        structural_digest=digest1 or "",
        deterministic_reimport=deterministic,
        errors=errors,
    )
