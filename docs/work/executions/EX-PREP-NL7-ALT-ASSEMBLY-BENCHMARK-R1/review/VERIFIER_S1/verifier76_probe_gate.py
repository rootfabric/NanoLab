"""VERIFIER-76 independent probes of knowledge_pack.alt_pair_source_gate.

Written independently (not copied from review-evidence/probe_adhoc.py).
Synthetic fixtures only; 0 science; offline.
  P-NEG-1: non-terminal anchor index must be rejected (fail-closed).
  P-POS-1: valid disjoint terminal segments must be accepted to the
           preflight-only outcome (never a science pass).
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path("/home/rdpuser/NanoLab/verify-pr76-r1")
sys.path.insert(0, str(ROOT / "scripts"))
from knowledge_pack import alt_pair_source_gate as gate  # noqa: E402

PACK_FILE = ROOT / "docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json"


def as_input(path: Path, root: Path) -> dict:
    data = path.read_bytes()
    return {
        "status": "CONTENT_VERIFIED",
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "rights": "ALLOWED",
        "source_url": "https://example.org/fixture/" + path.name,
    }


def make_topology(seg_5p_to_3p: str) -> str:
    """12nt linear strand, one chain, file order 3p->5p (legacy oxDNA body).

    The declared 5p->3p terminal segment must be written reversed into the
    file order so that reading the first six rows back 5p->3p yields it.
    """
    tail = "TTGGAA"
    bases = seg_5p_to_3p[::-1] + tail
    rows = []
    for i, base in enumerate(bases):
        n3 = i - 1 if i > 0 else -1
        n5 = i + 1 if i + 1 < len(bases) else -1
        rows.append(f"1 {base} {n3} {n5}")
    return f"{len(bases)} 1\n" + "\n".join(rows) + "\n"


def make_config(n: int = 12) -> str:
    lines = ["t = 0", "b = 30 30 30", "E = 0 0 0"]
    for i in range(n):
        lines.append(" ".join(str(x) for x in [
            float(i + 1), 5.0, 5.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    return "\n".join(lines) + "\n"


def base_pack(root: Path, a_seg: str, b_seg: str) -> dict:
    pack = gate.parse_json_no_duplicate_keys(PACK_FILE.read_text(encoding="utf-8"))
    cand = pack["candidates"][0]
    cand["candidate_id"] = "VERIFIER76_SYNTHETIC"
    cand["design_basis"] = "SYNTHETIC_FIXTURE"
    pack["selected_candidate_id"] = cand["candidate_id"]
    pack["candidates"] = [cand]
    for part in cand["parts"]:
        pid = part["part_id"].lower()
        seg = a_seg if pid == "narcissus" else b_seg
        top = root / f"{pid}.top"
        conf = root / f"{pid}.dat"
        top.write_text(make_topology(seg), encoding="utf-8")
        conf.write_text(make_config(), encoding="utf-8")
        part["topology"] = as_input(top, root)
        part["configuration"] = as_input(conf, root)
    return pack, cand


def anchor_pair(a_index: int, b_index: int) -> dict:
    return {
        "kind": "two_part_dna_interface_map",
        "pairs": [{
            "part_a": "NARCISSUS", "part_b": "ECHO",
            "a_index": a_index, "b_index": b_index,
            "a_end": "3p", "b_end": "3p",
            "segment_a": "ACGTAC", "segment_b": "GTACGT",
            "kind": "NONCOVALENT_DNA_HYBRIDIZATION",
            "status": "SOURCE_CONFIRMED",
        }],
    }


def run_case(name: str, a_index: int, b_index: int, expect_outcome: str) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pack, cand = base_pack(root, "ACGTAC", "GTACGT")
        amap = root / "ports.json"
        amap.write_text(json.dumps(anchor_pair(a_index, b_index), sort_keys=True), encoding="utf-8")
        cand["interface"]["anchor_map"] = as_input(amap, root)
        errs = gate.validate_manifest(pack)
        result = gate.evaluate(pack, cand["candidate_id"], root)
        ok = result["outcome"] == expect_outcome
        print(f"[{name}] expect={expect_outcome} got={result['outcome']} -> {'PASS' if ok else 'FAIL'}")
        print(f"  reasons: {result['reasons'][:3]}")
        print(f"  manifest_errors: {errs[:2]} scientific_runs: {result['scientific_runs']}")
        return ok


if __name__ == "__main__":
    results = [
        run_case("P-NEG-1 non-terminal a_index=2", 2, 0, "BLOCKED_SOURCE"),
        run_case("P-NEG-2 non-terminal b_index=3", 0, 3, "BLOCKED_SOURCE"),
        run_case("P-POS-1 disjoint terminal ports", 0, 0, "TEST_FIXTURE_STATIC_INPUTS_OK"),
    ]
    print("SUMMARY:", sum(results), "/", len(results), "probes behaved as expected")
    sys.exit(0 if all(results) else 1)
