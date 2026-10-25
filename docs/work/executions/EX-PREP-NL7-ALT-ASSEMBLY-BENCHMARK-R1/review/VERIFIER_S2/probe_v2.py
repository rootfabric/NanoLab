"""VERIFIER-76-R2 independent probes of REVIEWER-76 key claims.

Own synthetic fixtures, own parameters (sequence/indices/segment lengths differ
from both the unit-test fixtures and the reviewer's probes):
  P1 (probe_v2_a): internal anchor index 7 on a 12nt strand -> must be rejected.
  P2 (probe_v2_b): two disjoint 4nt ports on opposite terminals of the same
      strand -> must be accepted (TEST_FIXTURE_STATIC_INPUTS_OK).
  P3 (probe_v2_c): same geometry with 8nt ports (overlap) -> must be rejected
      with "nucleotide already assigned".

All synthetic; 0 science; fixtures certify code mechanics only.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from knowledge_pack import alt_pair_source_gate as gate  # noqa: E402

PACK_FILE = ROOT / "docs/research/ALT_DNA_TWO_PART_SOURCE_PACK_R1.json"

SEQ_A = "TTGCAAGGCATT"  # conventional 5p->3p, 12nt (own sequence, not from tests)
COMP = {"A": "T", "T": "A", "G": "C", "C": "G"}
SEQ_B = "".join(COMP[b] for b in reversed(SEQ_A))  # full reciprocal revcomp


def write_top(path: Path, seq_5to3: str) -> None:
    rows = seq_5to3[::-1]  # file order traverses 3p->5p
    lines = [f"{len(rows)} 1"]
    for i, base in enumerate(rows):
        n3 = i - 1 if i else -1
        n5 = i + 1 if i + 1 < len(rows) else -1
        lines.append(f"1 {base} {n3} {n5}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_dat(path: Path, n: int = 12) -> None:
    lines = ["t = 0", "b = 30 30 30", "E = 0 0 0"]
    for i in range(n):
        vals = [float(i + 1), 5.0, 5.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        lines.append(" ".join(str(x) for x in vals))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def base_pair() -> dict:
    return {
        "part_a": "NARCISSUS", "part_b": "ECHO",
        "a_index": 0, "b_index": 0, "a_end": "3p", "b_end": "3p",
        "segment_a": SEQ_A[-6:], "segment_b": SEQ_B[:6],
        "kind": "NONCOVALENT_DNA_HYBRIDIZATION", "status": "SOURCE_CONFIRMED",
    }


def build(root: Path, pairs: list[dict]) -> tuple[dict, str]:
    pack = gate.parse_json_no_duplicate_keys(PACK_FILE.read_text(encoding="utf-8"))
    cand = pack["candidates"][0]
    cand["candidate_id"] = "SYNTHETIC_TWO_PART"
    cand["design_basis"] = "SYNTHETIC_FIXTURE"
    pack["selected_candidate_id"] = cand["candidate_id"]
    pack["candidates"] = [cand]
    for part, seq in zip(cand["parts"], (SEQ_A, SEQ_B)):
        pid = part["part_id"].lower()
        top, dat = root / f"{pid}.top", root / f"{pid}.dat"
        write_top(top, seq)
        write_dat(dat)
        part["topology"] = as_input(top, root)
        part["configuration"] = as_input(dat, root)
    amap = root / "ports.json"
    amap.write_text(json.dumps(
        {"kind": "two_part_dna_interface_map", "pairs": pairs}, sort_keys=True
    ), encoding="utf-8")
    cand["interface"]["anchor_map"] = as_input(amap, root)
    return pack, cand["candidate_id"]


def run(name: str, pairs: list[dict]) -> dict:
    with tempfile.TemporaryDirectory() as td:
        pack, cid = build(Path(td), pairs)
        return gate.evaluate(pack, cid, Path(td))


def main() -> int:
    ok = True

    # P1: internal anchor index 7 (correct terminal segment, wrong anchor) -> BLOCK
    r1 = run("P1", [dict(base_pair(), a_index=7)])
    got = r1["outcome"] == "BLOCKED_SOURCE" and any("internal" in x for x in r1["reasons"])
    ok &= got
    print(f"P1 nonterminal_index_7: outcome={r1['outcome']} reasons={r1['reasons']} -> {'PASS' if got else 'FAIL'}")

    # P2: two disjoint 6nt opposite-terminal ports on a 12nt strand -> ACCEPT
    # (gate enforces [ACGT]{6,120}; 6+6=12 nucleotides, indices 0-5 vs 6-11 disjoint)
    seg = 6
    p2_first = {
        "part_a": "NARCISSUS", "part_b": "ECHO",
        "a_end": "3p", "b_end": "5p", "a_index": 0, "b_index": 11,
        "segment_a": SEQ_A[-seg:], "segment_b": SEQ_B[:seg],
        "kind": "NONCOVALENT_DNA_HYBRIDIZATION", "status": "SOURCE_CONFIRMED",
    }
    p2_second = dict(p2_first, a_end="5p", b_end="3p", a_index=11, b_index=0,
                     segment_a=SEQ_A[:seg], segment_b=SEQ_B[-seg:])
    r2 = run("P2", [p2_first, p2_second])
    got = r2["outcome"] == "TEST_FIXTURE_STATIC_INPUTS_OK"
    ok &= got
    print(f"P2 disjoint_6nt_ports: outcome={r2['outcome']} reasons={r2['reasons']} -> {'PASS' if got else 'FAIL'}")

    # P3: same geometry, 8nt ports overlap -> BLOCK with 'already assigned'
    seg = 8
    p3_first = {
        "part_a": "NARCISSUS", "part_b": "ECHO",
        "a_end": "3p", "b_end": "5p", "a_index": 0, "b_index": 11,
        "segment_a": SEQ_A[-seg:], "segment_b": SEQ_B[:seg],
        "kind": "NONCOVALENT_DNA_HYBRIDIZATION", "status": "SOURCE_CONFIRMED",
    }
    p3_second = dict(p3_first, a_end="5p", b_end="3p", a_index=11, b_index=0,
                     segment_a=SEQ_A[:seg], segment_b=SEQ_B[-seg:])
    r3 = run("P3", [p3_first, p3_second])
    got = r3["outcome"] == "BLOCKED_SOURCE" and any("already assigned" in x for x in r3["reasons"])
    ok &= got
    print(f"P3 overlapping_8nt_ports: outcome={r3['outcome']} overlap={[x for x in r3['reasons'] if 'already' in x]} -> {'PASS' if got else 'FAIL'}")

    print("PROBE_RESULT:", "ALL_PASS" if ok else "FAILURE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
