"""Static assembly preflight and fail-closed recipe enforcement (S17 R2).

WO-PREP-S17-R2 stage C. Software-only side of the driver-follower topology
question:

* ``static_preflight`` re-validates a pinned (topology, configuration) pair
  (strict parse, count agreement, chain integrity via the strict parser,
  neighbour valency, deterministic digest) — structural facts only.
* ``evaluate_recipe`` takes a declared assembly recipe and enforces the claim
  discipline: only a ``SOURCE_CONFIRMED`` recipe is ever assembled; a recipe
  backed by inference is rejected as ``BLOCKED_INFERRED_RECIPE``; a missing
  recipe yields an explicit ``NOT_RECONSTRUCTED`` receipt listing the blocked
  inputs. No link is ever invented here.
* ``assemble_from_recipe`` performs the deterministic concatenation (strand
  order + fresh contiguous strand ids + terminal-only n3/n5 rewires) and
  returns a byte-stable SHA-256 of the assembled topology text. This is a
  *static* file operation: no dynamics, relaxation or simulation is performed
  or implied.

Claim ceiling: ``ASSEMBLED_STATIC_ONLY`` refers to deterministic file-level
construction. It is never ``ASSEMBLY_VALIDATED`` and never a physics claim.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from hinge_family.oxdna_topology import Topology, TopologyError
from knowledge_pack.import_validation import import_paired
from knowledge_pack.s17_index_map import IndexMapError, index_map_digest, load_topology_verified, strand_spans

RECIPE_STATUSES = ("SOURCE_CONFIRMED", "PARTIAL_EVIDENCE", "INFERRED_CANDIDATE", "UNKNOWN")
ASSEMBLY_STATUSES = ("NOT_RECONSTRUCTED", "BLOCKED_INFERRED_RECIPE", "ASSEMBLED_STATIC_ONLY")


class AssemblyError(Exception):
    """Raised on fail-closed assembly violations."""


class PreflightResult:
    def __init__(self, topology_path: str, configuration_path: str, topology_sha256: str,
                 configuration_sha256: str, nucleotides: int, strand_count: int,
                 linear_strands: int, circular_strands: int, valency_ok: bool,
                 counts_match: bool, index_map_digest: str, structural_digest: str,
                 deterministic_reimport: bool, errors: list):
        self.topology_path = topology_path
        self.configuration_path = configuration_path
        self.topology_sha256 = topology_sha256
        self.configuration_sha256 = configuration_sha256
        self.nucleotides = nucleotides
        self.strand_count = strand_count
        self.linear_strands = linear_strands
        self.circular_strands = circular_strands
        self.valency_ok = valency_ok
        self.counts_match = counts_match
        self.index_map_digest = index_map_digest
        self.structural_digest = structural_digest
        self.deterministic_reimport = deterministic_reimport
        self.errors = errors

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return dict(self.__dict__)


def static_preflight(topology_path: Path, configuration_path: Path,
                     topology_sha256: str | None = None) -> PreflightResult:
    """Structural preflight of one pinned component (static facts only)."""
    errors: list[str] = []
    top_path, conf_path = Path(topology_path), Path(configuration_path)
    top_bytes = top_path.read_bytes()
    top_sha = hashlib.sha256(top_bytes).hexdigest()
    if topology_sha256 is not None and top_sha != topology_sha256:
        errors.append(f"topology pin mismatch: expected {topology_sha256}, got {top_sha}")
    top = None
    spans = []
    try:
        top = load_topology_verified(top_path, top_sha)
        spans = strand_spans(top)
    except (IndexMapError, TopologyError) as exc:
        errors.append(f"strict topology parse failed: {exc}")
    valency_ok = False
    counts_match = False
    map_digest = ""
    if top is not None:
        neighbours = [v for r in top.rows for v in (r[2], r[3])]
        valency_ok = all(v == -1 or 0 <= v < top.nucleotides for v in neighbours)
        if not valency_ok:
            errors.append("link valency violation: neighbour index out of bounds")
        try:
            map_digest = index_map_digest(top)
        except IndexMapError as exc:
            errors.append(f"index map failed: {exc}")
    pair = import_paired(top_path, conf_path)
    if pair.errors:
        errors.extend(pair.errors)
    counts_match = bool(pair.counts_match)
    if top is not None and not counts_match:
        errors.append("count mismatch between pinned topology and configuration")
    return PreflightResult(
        topology_path=str(top_path),
        configuration_path=str(conf_path),
        topology_sha256=top_sha,
        configuration_sha256=pair.configuration_sha256,
        nucleotides=top.nucleotides if top else -1,
        strand_count=top.strand_count if top else -1,
        linear_strands=sum(1 for s in spans if not s.circular),
        circular_strands=sum(1 for s in spans if s.circular),
        valency_ok=valency_ok,
        counts_match=counts_match,
        index_map_digest=map_digest,
        structural_digest=pair.structural_digest,
        deterministic_reimport=pair.deterministic_reimport,
        errors=errors,
    )


def _receipt(assembly_status: str, recipe, components, blocked_inputs, reason) -> dict:
    allowed = set(ASSEMBLY_STATUSES) | {"PENDING_ASSEMBLY"}
    if assembly_status not in allowed:
        raise AssemblyError(f"unknown assembly status {assembly_status}")
    return {
        "schema_version": 1,
        "kind": "s17_static_assembly_receipt",
        "assembly_status": assembly_status,
        "claim": "STATIC_FILE_OPERATION_ONLY (never ASSEMBLY_VALIDATED, never a physics claim)",
        "recipe": recipe,
        "components": components,
        "blocked_inputs": list(blocked_inputs),
        "reason": reason,
        "assembled": None,
    }


def not_reconstructed_receipt(subject: str, components: dict, blocked_inputs: list[str]) -> dict:
    """The honest fail-closed receipt for a missing source-confirmed recipe."""
    receipt = _receipt("NOT_RECONSTRUCTED", recipe=None, components=components,
                       blocked_inputs=blocked_inputs,
                       reason="no source-confirmed assembly recipe exists in any audited surface")
    receipt["subject"] = subject
    return receipt


def evaluate_recipe(recipe: dict | None, components: dict[str, dict],
                    blocked_inputs: list[str] | None = None) -> dict:
    """Enforce the recipe claim discipline; returns a fail-closed receipt.

    ``components`` maps component name -> {"nucleotides": int, "strands": int}.
    """
    blocked_inputs = blocked_inputs or []
    if not isinstance(recipe, dict) or not recipe:
        return _receipt("NOT_RECONSTRUCTED", recipe=None, components=components,
                        blocked_inputs=blocked_inputs or ["assembly recipe not found in any audited source"],
                        reason="no recipe object was supplied")
    status = recipe.get("status")
    if status not in RECIPE_STATUSES:
        return _receipt("NOT_RECONSTRUCTED", recipe=recipe, components=components,
                        blocked_inputs=blocked_inputs, reason=f"unknown recipe status {status!r}")
    if status != "SOURCE_CONFIRMED":
        return _receipt("BLOCKED_INFERRED_RECIPE", recipe=recipe, components=components,
                        blocked_inputs=blocked_inputs,
                        reason=f"recipe status {status} may never pass a production preflight")
    problems = _validate_source_confirmed_recipe(recipe, components)
    if problems:
        return _receipt("BLOCKED_INFERRED_RECIPE", recipe=recipe, components=components,
                        blocked_inputs=blocked_inputs,
                        reason="SOURCE_CONFIRMED recipe failed validation: " + "; ".join(problems))
    return _receipt("PENDING_ASSEMBLY", recipe=recipe, components=components,
                    blocked_inputs=blocked_inputs, reason=None)


def _validate_source_confirmed_recipe(recipe: dict, components: dict[str, dict]) -> list[str]:
    problems: list[str] = []
    for key in ("source_refs", "strand_order", "links"):
        if key not in recipe:
            problems.append(f"missing recipe field {key}")
    if problems:
        return problems
    if not isinstance(recipe["source_refs"], list) or not recipe["source_refs"]:
        problems.append("source_refs must be a non-empty list of pinned sources")
    order = recipe["strand_order"]
    if not isinstance(order, list) or not order:
        problems.append("strand_order must be a non-empty list")
        return problems
    counts: dict[str, int] = {}
    for item in order:
        if not (isinstance(item, dict) and set(item) == {"component", "strand_id"}
                and isinstance(item.get("strand_id"), int) and not isinstance(item.get("strand_id"), bool)):
            problems.append(f"strand_order item malformed: {item!r}")
            continue
        comp = components.get(item["component"])
        if comp is None:
            problems.append(f"strand_order references unknown component {item['component']!r}")
            continue
        if not 1 <= item["strand_id"] <= comp["strands"]:
            problems.append(f"strand_id out of bounds for component {item['component']}")
        key = f"{item['component']}:{item['strand_id']}"
        counts[key] = counts.get(key, 0) + 1
    for name, comp in components.items():
        for sid in range(1, comp["strands"] + 1):
            key = f"{name}:{sid}"
            if counts.get(key, 0) != 1:
                problems.append(f"strand {key} appears {counts.get(key, 0)} times (must be exactly 1)")
    links = recipe["links"]
    if not isinstance(links, list):
        problems.append("links must be a list")
        return problems
    for lnk in links:
        if not (isinstance(lnk, dict) and {"from_particle", "to_particle", "kind"} <= set(lnk)):
            problems.append(f"link malformed: {lnk!r}")
            continue
        if lnk["kind"] not in ("n3_n5",):
            problems.append(f"unsupported link kind {lnk['kind']!r}")
        if not lnk.get("source_ref"):
            problems.append(f"link {lnk!r} has no source_ref (invented links are forbidden)")
        for endpoint_key in ("from_particle", "to_particle"):
            spec = lnk.get(endpoint_key)
            if not (isinstance(spec, dict) and set(spec) == {"component", "particle"}
                    and isinstance(spec.get("particle"), int)):
                problems.append(f"link endpoint malformed: {spec!r}")
                continue
            comp = components.get(spec["component"])
            if comp is None or not 0 <= spec["particle"] < comp["nucleotides"]:
                problems.append(f"link endpoint out of bounds: {spec!r}")
    return problems


def _component_particle_base(order: list[dict], component_topologies: dict[str, Topology]) -> dict[str, int]:
    """Particle offset of each component = sum of nucleotides of components
    whose first occurrence in strand_order precedes its own first occurrence."""
    first_seen: dict[str, int] = {}
    for i, item in enumerate(order):
        name = item["component"]
        if name not in first_seen:
            first_seen[name] = i
    ordered_names = sorted(first_seen, key=lambda n: first_seen[n])
    base: dict[str, int] = {}
    offset = 0
    for name in ordered_names:
        base[name] = offset
        offset += component_topologies[name].nucleotides
    return base


def assemble_topology_text(recipe: dict, component_topologies: dict[str, Topology]) -> tuple[str, dict]:
    """Deterministic concatenation; returns (topology_text, fail_closed_receipt).

    When the receipt's ``assembly_status`` is not ``ASSEMBLED_STATIC_ONLY`` the
    text is the empty string and nothing was assembled.
    """
    text_parts: list[str] = []
    receipt = _assemble_impl(recipe, component_topologies, text_parts)
    return ("".join(text_parts), receipt)


def assemble_from_recipe(recipe: dict, component_topologies: dict[str, Topology]) -> dict:
    """Deterministic concatenation of a SOURCE_CONFIRMED recipe (static only)."""
    return _assemble_impl(recipe, component_topologies, None)


def _assemble_impl(recipe: dict, component_topologies: dict[str, Topology], text_out) -> dict:
    probe = evaluate_recipe(recipe, {name: {"nucleotides": t.nucleotides, "strands": t.strand_count}
                                     for name, t in component_topologies.items()})
    if probe["assembly_status"] != "PENDING_ASSEMBLY":
        return probe
    order = recipe["strand_order"]
    base = _component_particle_base(order, component_topologies)
    rows: list[tuple[int, str, int, int]] = []
    new_sid = 0
    for item in order:
        comp_name, sid = item["component"], item["strand_id"]
        top = component_topologies[comp_name]
        comp_rows = [r for r in top.rows if r[0] == sid]
        if not comp_rows:
            return _receipt("BLOCKED_INFERRED_RECIPE", recipe=recipe, components={},
                            blocked_inputs=[], reason=f"strand {comp_name}:{sid} has no rows")
        shift = base[comp_name]
        for (_s, b, n3, n5) in comp_rows:
            rows.append((new_sid, b, (n3 + shift) if n3 != -1 else -1,
                         (n5 + shift) if n5 != -1 else -1))
        new_sid += 1
    # Apply declared terminal rewires. In the .top row convention (3'->5')
    # a continuous-strand link from strand A's 5'-terminal nucleotide
    # (n5 == -1) to strand B's 3'-terminal nucleotide (n3 == -1) sets
    # A_end.n5 = B_start and B_start.n3 = A_end. Linked pieces share one
    # strand id in the assembled file (oxDNA continuity), so pieces are
    # unioned via the links and renumbered in order of first appearance.
    parent: dict[int, int] = {}

    def find(x: int) -> int:
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for lnk in recipe["links"]:
        f, t = lnk["from_particle"], lnk["to_particle"]
        fi = f["particle"] + base[f["component"]]
        ti = t["particle"] + base[t["component"]]
        sf, bf, n3f, n5f = rows[fi]
        st, bt, n3t, n5t = rows[ti]
        if n5f != -1 or n3t != -1:
            return _receipt("BLOCKED_INFERRED_RECIPE", recipe=recipe, components={},
                            blocked_inputs=[],
                            reason=f"link endpoints must be file-strand terminals (from: n5==-1, to: n3==-1): {lnk}")
        rows[fi] = (sf, bf, n3f, ti)
        rows[ti] = (st, bt, fi, n5t)
        ra, rb = find(sf), find(st)
        if ra != rb:
            parent[rb] = ra
    renumber: dict[int, int] = {}
    merged_rows: list[tuple[int, str, int, int]] = []
    for (s, b, n3, n5) in rows:
        root = find(s)
        if root not in renumber:
            renumber[root] = len(renumber) + 1
        merged_rows.append((renumber[root], b, n3, n5))
    rows = merged_rows
    # Reparse the assembled text with the strict parser (must never fail here).
    text = f"{len(rows)} {len(set(r[0] for r in rows))}\n" + "".join(
        f"{s} {b} {n3} {n5}\n" for (s, b, n3, n5) in rows)
    if text_out is not None:
        text_out.append(text)
    try:
        Topology.parse(text)
    except TopologyError as exc:
        return _receipt("BLOCKED_INFERRED_RECIPE", recipe=recipe, components={},
                        blocked_inputs=[], reason=f"assembled topology failed strict reparse: {exc}")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    receipt = _receipt("ASSEMBLED_STATIC_ONLY", recipe=recipe,
                       components={name: {"nucleotides": t.nucleotides, "strands": t.strand_count}
                                   for name, t in component_topologies.items()},
                       blocked_inputs=[], reason=None)
    receipt["assembled"] = {
        "nucleotides": len(rows),
        "strands": len(set(r[0] for r in rows)),
        "topology_text_sha256": digest,
    }
    return receipt


def topology_text(topology_path: Path) -> str:
    return Path(topology_path).read_text(encoding="utf-8")
