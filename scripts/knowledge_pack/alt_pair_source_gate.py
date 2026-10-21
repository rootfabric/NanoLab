"""Offline source-input gate for two published DNA origami parts.

Source scope: WO-PREP-NL7-ALT-ASSEMBLY-BENCHMARK-R1 / Issue #75.
This is NOT a simulation or a scientific reproducibility validator. It does not
fetch URLs or synthesize missing molecular designs. Source files are optional
until explicitly verified; missing/UNKNOWN inputs always yield BLOCKED_SOURCE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from hinge_family.oxdna_topology import Topology, TopologyError
from hinge_family.oxdna_conf import Configuration, ConfError

KIND = "alt_dna_two_part_source_pack"
CLAIM = "BIBLIOGRAPHIC"
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
DOI_RE = re.compile(r"^10\.[0-9]{4,9}/\S+$")
MAX_SOURCE_BYTES = 16 * 1024 * 1024
VALID_SOURCE_STATUSES = {"UNKNOWN", "CONTENT_VERIFIED"}
VALID_RIGHTS = {"UNKNOWN", "ALLOWED", "RESTRICTED", "FORBIDDEN"}
VALID_REPORTED = {"R4_REPORTED_NOT_BYTE_VERIFIED", "PAPER_REPORTS_FILE_NOT_FETCHED"}
VALID_INTERFACE_MECHANISMS = {
    "DNA_HYBRIDIZATION", "MODULAR_XY_SHAPE_MATCH_OR_Z_THREE_STRAND"
}
REQUIRED_INPUT_KEYS = {
    "path", "sha256", "size_bytes", "rights", "source_url", "status"
}


def parse_json_no_duplicate_keys(text: str):
    def hook(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON field: {key}")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=hook)


def _is_digest(s):
    return isinstance(s, str) and bool(SHA_RE.fullmatch(s))


def validate_manifest(pack: object) -> list[str]:
    """Reject claim inflation, invalid statuses, malformed/ambiguous source pins."""
    errors = []
    if not isinstance(pack, dict):
        return ["manifest must be an object"]
    if pack.get("schema_version") != 1 or isinstance(pack.get("schema_version"), bool):
        errors.append("schema_version must be integer 1")
    if pack.get("kind") != KIND:
        errors.append(f"kind must be {KIND}")
    if pack.get("claim_ceiling") != CLAIM:
        errors.append("only BIBLIOGRAPHIC claim is authorized for this provisional source pack")
    if pack.get("scientific_runs") != 0 or isinstance(pack.get("scientific_runs"), bool):
        errors.append("this source-only pack requires scientific_runs=0")
    candidates = pack.get("candidates")
    if not isinstance(candidates, list) or len(candidates) < 1:
        return errors + ["candidates must be a nonempty list"]
    ids = []
    for i, candidate in enumerate(candidates):
        loc = f"candidates[{i}]"
        if not isinstance(candidate, dict):
            errors.append(f"{loc}: expected object")
            continue
        cid = candidate.get("candidate_id")
        if not isinstance(cid, str) or not cid.strip():
            errors.append(f"{loc}: candidate_id required")
        else:
            ids.append(cid)
        doi = candidate.get("doi")
        if not isinstance(doi, str) or not DOI_RE.fullmatch(doi):
            errors.append(f"{loc}: exact DOI required")
        if candidate.get("design_basis") not in ("PUBLISHED_SOURCE", "SYNTHETIC_FIXTURE"):
            errors.append(f"{loc}: unexpected design_basis")
        if candidate.get("paper_evidence") != "SOURCE_ARTICLE_CONFIRMED":
            errors.append(f"{loc}: article identity must be explicitly confirmed")
        u = candidate.get("publication_url")
        if not isinstance(u, str) or not u.startswith("https://"):
            errors.append(f"{loc}: publication_url must be HTTPS")
        if candidate.get("source_verdict") != "BLOCKED_SOURCE":
            # This is a provisional input pack, not a scientific gate.
            errors.append(f"{loc}: published-source readiness must not be self-claimed")
        parts = candidate.get("parts")
        if not isinstance(parts, list) or len(parts) != 2:
            errors.append(f"{loc}: exactly two parts required")
            continue
        part_ids = [p.get("part_id") for p in parts if isinstance(p, dict)]
        if len(part_ids) != 2 or len(set(part_ids)) != 2:
            errors.append(f"{loc}: two distinct part_id values required")
        for p_idx, part in enumerate(parts):
            if not isinstance(part, dict):
                errors.append(f"{loc}.parts[{p_idx}] must be an object")
                continue
            for role in ("topology", "configuration"):
                errors.extend(_validate_input(part.get(role), f"{loc}.{part.get('part_id')}.{role}"))
        interface = candidate.get("interface")
        if not isinstance(interface, dict) or interface.get("mechanism") not in VALID_INTERFACE_MECHANISMS:
            errors.append(f"{loc}: interface mechanism is not supported")
        else:
            if interface.get("paper_status") != "SOURCE_ARTICLE_CONFIRMED":
                errors.append(f"{loc}: missing explicit paper-level interface status")
            errors.extend(_validate_input(interface.get("anchor_map"), f"{loc}.interface.anchor_map"))
            if interface.get("geometry_status") not in ("UNKNOWN", "INFERRED_CANDIDATE"):
                errors.append(f"{loc}: no verified molecular geometry exists in this source pack")
        reported = candidate.get("reported_design_files", [])
        if not isinstance(reported, list):
            errors.append(f"{loc}: reported_design_files must be a list")
        else:
            for f_idx, item in enumerate(reported):
                here = f"{loc}.reported_design_files[{f_idx}]"
                if not isinstance(item, dict):
                    errors.append(f"{here}: expected object")
                    continue
                if item.get("status") not in VALID_REPORTED:
                    errors.append(f"{here}: status cannot promote an unverified file")
                if item.get("sha256") != "UNKNOWN":
                    errors.append(f"{here}: unverified source digest must be UNKNOWN")
                if item.get("redistribution") != "UNKNOWN":
                    errors.append(f"{here}: source file rights must stay UNKNOWN until audited")
                if item.get("part_id") not in part_ids:
                    errors.append(f"{here}: invalid part reference")
    if len(ids) != len(set(ids)):
        errors.append("duplicate candidate_id")
    if pack.get("selected_candidate_id") not in ids:
        errors.append("selected_candidate_id must identify a candidate")
    return errors


def _validate_input(record: object, where: str) -> list[str]:
    if not isinstance(record, dict):
        return [f"{where}: expected input object"]
    errors = [f"{where}: missing {key}" for key in REQUIRED_INPUT_KEYS - set(record)]
    if errors:
        return errors
    status = record["status"]
    if status not in VALID_SOURCE_STATUSES:
        errors.append(f"{where}: unknown status")
    if record["rights"] not in VALID_RIGHTS:
        errors.append(f"{where}: unknown rights value")
    if status == "UNKNOWN":
        for key in ("path", "sha256", "size_bytes", "source_url"):
            if record[key] != "UNKNOWN":
                errors.append(f"{where}: status UNKNOWN must not carry concrete {key}")
        if record["rights"] != "UNKNOWN":
            errors.append(f"{where}: rights cannot be established for an unknown input")
    elif status == "CONTENT_VERIFIED":
        if not _is_digest(record["sha256"]):
            errors.append(f"{where}: CONTENT_VERIFIED requires 64-hex SHA-256")
        if not isinstance(record["size_bytes"], int) or isinstance(record["size_bytes"], bool) or not (0 < record["size_bytes"] <= MAX_SOURCE_BYTES):
            errors.append(f"{where}: invalid declared size / resource cap")
        if not isinstance(record["path"], str) or not record["path"] or record["path"] == "UNKNOWN":
            errors.append(f"{where}: CONTENT_VERIFIED requires a local relative path")
        if not isinstance(record["source_url"], str) or not record["source_url"].startswith("https://"):
            errors.append(f"{where}: source_url requires actual HTTPS origin")
    return errors


def _read_verified_file(root: Path, record: dict, role: str) -> tuple[bytes | None, str | None]:
    if record["status"] != "CONTENT_VERIFIED":
        return None, f"{role}: SOURCE_BYTES_NOT_OBSERVED"
    if record["rights"] != "ALLOWED":
        return None, f"{role}: RIGHTS_NOT_CLEARED ({record['rights']})"
    relative = Path(record["path"])
    if relative.is_absolute() or any(part in (".", "..") for part in relative.parts):
        return None, f"{role}: path traversal or absolute path"
    root = root.resolve()
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return None, f"{role}: symlink in source path"
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return None, f"{role}: missing or outside-root source file"
    if path.stat().st_size > MAX_SOURCE_BYTES:
        return None, f"{role}: file exceeds 16 MiB cap"
    data = path.read_bytes()
    if len(data) != record["size_bytes"]:
        return None, f"{role}: file size mismatch"
    if hashlib.sha256(data).hexdigest() != record["sha256"]:
        return None, f"{role}: source SHA-256 mismatch"
    return data, None


def _verified_terminal_segment(top: Topology, anchor: int, end: str, segment_length: int) -> tuple[str | None, str | None]:
    """Read actual oxDNA bases at a proven 3p/5p strand terminus, in 5p->3p order.

    Standard legacy oxDNA .top rows are indexed globally and traversed 3p->5p
    via n5, while n3 traverses in the reverse direction. A numeric index alone
    does NOT establish an exposed DNA overhang or its molecular identity.
    No unknown/placeholder base, internal index or short strand is accepted.
    The existence of a base sequence at a terminus does NOT prove it is
    unpaired or accessible; separate source evidence/review is still required.
    """
    if end not in ("3p", "5p"):
        return None, "unknown terminal direction"
    if not isinstance(anchor, int) or isinstance(anchor, bool) or anchor < 0 or anchor >= top.nucleotides:
        return None, "out-of-bounds anchor"
    sid, _base, n3, n5 = top.rows[anchor]
    if end == "3p" and n3 != -1:
        return None, "anchor is not a 3p strand terminus (internal anchor)"
    if end == "5p" and n5 != -1:
        return None, "anchor is not a 5p strand terminus (internal anchor)"
    if not isinstance(segment_length, int) or segment_length <= 0 or segment_length > top.nucleotides:
        return None, "invalid segment length"
    bases = []
    visited = set()
    cursor = anchor
    for _ in range(segment_length):
        if cursor == -1:
            return None, "exposed segment exceeds the length of this strand"
        if cursor in visited or cursor >= top.nucleotides or cursor < 0:
            return None, "circular/ambiguous or invalid terminal trace"
        visited.add(cursor)
        row_sid, base, neighbor3, neighbor5 = top.rows[cursor]
        if row_sid != sid:
            return None, "terminal trace crosses strands"
        if base not in "ACGT":
            return None, "source topology base unknown or not canonical A/C/G/T"
        bases.append(base)
        cursor = neighbor5 if end == "3p" else neighbor3
    # Traversing 3p->5p reverses the conventional sequence representation.
    return "".join(reversed(bases) if end == "3p" else bases), None


def _validate_anchor_map(data: bytes, parts: dict[str, Topology]) -> str | None:
    try:
        j = parse_json_no_duplicate_keys(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        return f"anchor map JSON invalid: {exc}"
    if not isinstance(j, dict) or j.get("kind") != "two_part_dna_interface_map":
        return "anchor map must declare two_part_dna_interface_map"
    pairs = j.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        return "anchor map has no pair records"
    used = set()
    rc = str.maketrans("ACGT", "TGCA")
    for index, p in enumerate(pairs):
        if not isinstance(p, dict) or p.get("status") != "SOURCE_CONFIRMED":
            return f"pair {index}: UNKNOWN or inferred anchor"
        if p.get("kind") != "NONCOVALENT_DNA_HYBRIDIZATION":
            return f"pair {index}: unsupported connection chemistry"
        a, b = p.get("part_a"), p.get("part_b")
        ia, ib = p.get("a_index"), p.get("b_index")
        if a not in parts or b not in parts or a == b:
            return f"pair {index}: wrong parts"
        if (not isinstance(ia, int) or isinstance(ia, bool) or ia < 0 or ia >= parts[a].nucleotides or
                not isinstance(ib, int) or isinstance(ib, bool) or ib < 0 or ib >= parts[b].nucleotides):
            return f"pair {index}: out-of-bounds anchor"
        if (a, ia, b, ib) in used:
            return f"pair {index}: duplicate anchor pair"
        used.add((a, ia, b, ib))
        sa, sb = p.get("segment_a"), p.get("segment_b")
        if not all(isinstance(s, str) and re.fullmatch(r"[ACGT]{6,120}", s) for s in (sa, sb)):
            return f"pair {index}: invalid exposed ssDNA segment"
        if sa != sb[::-1].translate(rc):
            return f"pair {index}: exposed segments are not reverse complements"
        if p.get("a_end") not in ("5p", "3p") or p.get("b_end") not in ("5p", "3p"):
            return f"pair {index}: unknown overhang terminal direction"
        # Structural provenance gate: the declared terminal segment must occur
        # at the actual nominated strand end in the digest-verified topology.
        # Pairwise reverse-complementarity is necessary but insufficient.
        for role, part, particle, terminal, declared in (
            ("part_a", a, ia, p["a_end"], sa),
            ("part_b", b, ib, p["b_end"], sb),
        ):
            observed, error = _verified_terminal_segment(parts[part], particle, terminal, len(declared))
            if error:
                return f"pair {index} {role}: {error}"
            if observed != declared:
                return (f"pair {index} {role}: declared overhang segment is not present "
                        f"at source topology {terminal} terminal (topology sequence mismatch)")
    return None


def evaluate(pack: dict, candidate_id: str, root: Path) -> dict:
    """Return deterministic C0 input-preflight receipt; never a physics claim."""
    errors = validate_manifest(pack)
    candidate = next((c for c in pack.get("candidates", []) if isinstance(c, dict)
                      and c.get("candidate_id") == candidate_id), None)
    if candidate is None:
        errors.append("candidate not found")
    result = {
        "kind": "alt_two_part_source_readiness_receipt",
        "candidate_id": candidate_id,
        "claim": "C0_INPUT_FILE_PREFLIGHT_ONLY; NO SIMULATION; NO ASSEMBLY_VALIDATED",
        "scientific_runs": 0,
        "outcome": "BLOCKED_SOURCE",
        "reasons": list(errors),
        "part_structure_sizes": {},
    }
    if errors:
        return result
    parsed = {}
    for part in candidate["parts"]:
        pid = part["part_id"]
        pieces = {}
        for role in ("topology", "configuration"):
            data, problem = _read_verified_file(root, part[role], f"{pid}.{role}")
            if problem:
                result["reasons"].append(problem)
            else:
                pieces[role] = data
        if len(pieces) != 2:
            continue
        try:
            top = Topology.parse(pieces["topology"].decode("utf-8"))
            top.check_chain_integrity()
            conf = Configuration.parse(pieces["configuration"].decode("utf-8"))
            if len(conf.particles) != top.nucleotides:
                raise ValueError("topology/configuration particle-count mismatch")
            parsed[pid] = top
            result["part_structure_sizes"][pid] = {
                "nucleotides": top.nucleotides, "strands": top.strand_count
            }
        except (UnicodeDecodeError, TopologyError, ConfError, ValueError) as exc:
            result["reasons"].append(f"{pid}: strict oxDNA structural preflight failed: {exc}")
    anchor, issue = _read_verified_file(root, candidate["interface"]["anchor_map"], "interface.anchor_map")
    if issue:
        result["reasons"].append(issue)
    elif len(parsed) == 2:
        problem = _validate_anchor_map(anchor, parsed)
        if problem:
            result["reasons"].append(problem)
    else:
        result["reasons"].append("cannot verify anchor map without both parsed components")
    if not result["reasons"]:
        result["outcome"] = (
            "TEST_FIXTURE_STATIC_INPUTS_OK" if candidate["design_basis"] == "SYNTHETIC_FIXTURE"
            else "C0_SOURCE_FILE_PREFLIGHT_OK_REVIEW_REQUIRED"
        )
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline fail-closed two-component source preflight")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    try:
        pack = parse_json_no_duplicate_keys(args.manifest.read_text(encoding="utf-8"))
        receipt = evaluate(pack, args.candidate, args.root)
    except (OSError, ValueError) as exc:
        receipt = {"outcome": "BLOCKED_INVALID_MANIFEST", "reasons": [str(exc)]}
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if receipt["outcome"] in (
        "TEST_FIXTURE_STATIC_INPUTS_OK", "C0_SOURCE_FILE_PREFLIGHT_OK_REVIEW_REQUIRED"
    ) else 2


if __name__ == "__main__":
    raise SystemExit(main())
