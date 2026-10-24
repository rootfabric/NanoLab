"""Independent Reviewer probe v2 — consistent fixtures, reasons printed."""
import hashlib, json, sys, tempfile
from pathlib import Path
ROOT = Path('/home/rdpuser/NanoLab-review76')
sys.path.insert(0, str(ROOT / 'scripts'))
from knowledge_pack import alt_pair_source_gate as gate

SEQ_A = "TTGGAAACGCGT"   # 5p segment TTGGAA, 3p segment ACGCGT (self-revcomp)
SEQ_B = "TTCCAAACGCGT"   # 5p segment TTCCAA = revcomp(TTGGAA), 3p segment ACGCGT

def topology(seq12):
    rows = seq12[::-1]   # legacy rows traverse 3p->5p
    return "12 1\n" + "".join(
        f"1 {b} {i-1 if i else -1} {i+1 if i < 11 else -1}\n" for i, b in enumerate(rows))

def config(x0=1.0, box="30 30 30", a1=(1.,0.,0.), a2=(0.,0.,1.)):
    lines = ["t = 0", f"b = {box}", "E = 0 0 0"]
    for i in range(12):
        lines.append(" ".join(str(float(v)) for v in
            [x0 + i, 5.0, 5.0, *a1, *a2, 0.,0.,0., 0.,0.,0.]))
    return "\n".join(lines) + "\n"

def pair(a, b, ia, ib, ae, be, sa, sb):
    return {"part_a": a, "part_b": b, "a_index": ia, "b_index": ib,
            "a_end": ae, "b_end": be, "segment_a": sa, "segment_b": sb,
            "kind": "NONCOVALENT_DNA_HYBRIDIZATION", "status": "SOURCE_CONFIRMED"}

def amap(pairs):
    return {"kind": "two_part_dna_interface_map", "pairs": pairs}

def build(root, conf_a=None, conf_b=None, am=None):
    def put(n, t):
        p = root / n; p.write_text(t, encoding="utf-8"); return p
    def rec(p):
        d = p.read_bytes()
        return {"status": "CONTENT_VERIFIED", "path": p.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(d).hexdigest(), "size_bytes": len(d),
                "rights": "ALLOWED", "source_url": "https://example.org/f/" + p.name}
    files = [put("nar.top", topology(SEQ_A)), put("echo.top", topology(SEQ_B)),
             put("nar.dat", conf_a or config()), put("echo.dat", conf_b or config()),
             put("ports.json", json.dumps(am or amap([pair("NARCISSUS","ECHO",0,0,"3p","3p","ACGCGT","ACGCGT")])))]
    return {"schema_version": 1, "kind": "alt_dna_two_part_source_pack",
            "claim_ceiling": "BIBLIOGRAPHIC", "scientific_runs": 0, "selected_candidate_id": "FIX",
            "candidates": [{"candidate_id": "FIX", "doi": "10.9999/fake", "design_basis": "SYNTHETIC_FIXTURE",
                "paper_evidence": "SOURCE_ARTICLE_CONFIRMED", "publication_url": "https://example.org/p",
                "source_verdict": "BLOCKED_SOURCE",
                "parts": [{"part_id": "NARCISSUS", "topology": rec(files[0]), "configuration": rec(files[2])},
                          {"part_id": "ECHO", "topology": rec(files[1]), "configuration": rec(files[3])}],
                "interface": {"mechanism": "DNA_HYBRIDIZATION", "paper_status": "SOURCE_ARTICLE_CONFIRMED",
                              "anchor_map": rec(files[4]), "geometry_status": "INFERRED_CANDIDATE"},
                "reported_design_files": []}]}

tmp = Path(tempfile.mkdtemp())
def show(name, pack, expect):
    r = gate.evaluate(pack, "FIX", tmp)
    ok = "PASS" if r["outcome"] == expect else "FAIL<--UNEXPECTED"
    print(f"{name}: outcome={r['outcome']} expect={expect} => {ok}")
    if r["outcome"] != expect:
        print("   reasons:", r["reasons"][:4])

# P1: valid fixture with unwrapped PBC coordinates far outside the box -> must PASS
show("P1 unwrapped-PBC positive", build(tmp, config(x0=1000.0), config(x0=2000.0)), "TEST_FIXTURE_STATIC_INPUTS_OK")
# P2: NaN box -> BLOCK
show("P2 NaN box", build(tmp, conf_a=config(box="nan 30 30")), "BLOCKED_SOURCE")
# P3: zero-length orientation vector -> BLOCK
show("P3 zero orientation", build(tmp, conf_a=config(a1=(0.,0.,0.))), "BLOCKED_SOURCE")
# P4: A/B-swapped reuse of the same two 5p termini -> BLOCK with occupancy reason
p4 = amap([pair("NARCISSUS","ECHO",11,11,"5p","5p","TTGGAA","TTCCAA"),
           pair("ECHO","NARCISSUS",11,11,"5p","5p","TTCCAA","TTGGAA")])
r = gate.evaluate(build(tmp, am=p4), "FIX", tmp)
print("P4 A/B-swapped terminus reuse:", r["outcome"], "| occupancy reason:", any("already assigned" in x for x in r["reasons"]), "|", r["reasons"][:2])
# P5: internal (non-terminal) anchor -> BLOCK
p5 = amap([pair("NARCISSUS","ECHO",3,3,"3p","3p","ACGCGT","ACGCGT")])
r = gate.evaluate(build(tmp, am=p5), "FIX", tmp)
print("P5 internal anchor:", r["outcome"], "| internal-anchor reason:", any("internal anchor" in x for x in r["reasons"]))
# P6: correct sequence declared at the WRONG polarity -> BLOCK
p6 = amap([pair("NARCISSUS","ECHO",11,11,"3p","3p","TTGGAA","TTCCAA")])  # index 11 is 5p terminus, declared 3p
r = gate.evaluate(build(tmp, am=p6), "FIX", tmp)
print("P6 wrong polarity:", r["outcome"], "| polarity reason:", any("not a 3p strand terminus" in x for x in r["reasons"]), "|", r["reasons"][:2])
# P7: same-size digest tamper -> BLOCK
p7 = build(tmp); p7["candidates"][0]["parts"][0]["topology"]["sha256"] = "0"*64
r = gate.evaluate(p7, "FIX", tmp)
print("P7 digest tamper:", r["outcome"], "| SHA reason:", any("SHA-256 mismatch" in x for x in r["reasons"]))
# P8: rights RESTRICTED -> BLOCK
p8 = build(tmp); p8["candidates"][0]["parts"][0]["topology"]["rights"] = "RESTRICTED"
r = gate.evaluate(p8, "FIX", tmp)
print("P8 RESTRICTED rights:", r["outcome"], "| rights reason:", any("RIGHTS_NOT_CLEARED" in x for x in r["reasons"]))
# P9: non-terminal index with VALID complementary string that exists elsewhere but not at terminus -> BLOCK
p9 = amap([pair("NARCISSUS","ECHO",5,5,"3p","3p","ACGCGT","ACGCGT")])  # index 5 internal
r = gate.evaluate(build(tmp, am=p9), "FIX", tmp)
print("P9 unbound-overhang index:", r["outcome"], "| reason:", r["reasons"][:2])
