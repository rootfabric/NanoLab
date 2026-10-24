#!/usr/bin/env python3
"""VERIFIER-76-INT-R1 independent probe fixtures (own design, not Reviewer's).

Synthetic two-part oxDNA fixture pack + scenario variants in /tmp/v76_probes.
Part ALPHA: 12 nt, 6-nt 3' overhang (rows r0..r5 = ACGTAC -> observed 3p = CATGCA).
Part BETA:  12 nt, 6-nt 5' overhang (rows r6..r11 = GTACGT -> observed 5p = TGCATG).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = "/tmp/v76_probes"
SRC = os.path.expanduser("~/NanoLab-verify76")

RC = str.maketrans("ACGT", "TGCA")

def strand_rows(bases):
    """rows listed 3'->5': row0 = 3' terminus (n3=-1), last = 5' terminus (n5=-1)"""
    n = len(bases)
    rows = []
    for i, b in enumerate(bases):
        n3 = -1 if i == 0 else i - 1
        n5 = -1 if i == n - 1 else i + 1
        rows.append(f"1 {b} {n3} {n5}")
    return f"{n} 1\n" + "\n".join(rows) + "\n", n

ALPHA_BASES = "ACGTACTTGCGA"    # 3p overhang rows r0..r5 = ACGTAC
BETA_BASES = "CGATCGGTACGT"     # 5p overhang rows r6..r11 = GTACGT
SEG_A = "CATGCA"                # observed 3p of ALPHA, 5'->3' order
SEG_B = "TGCATG"                # observed 5p of BETA, 5'->3' order (rev-comp of SEG_A)
assert SEG_B == SEG_A[::-1].translate(RC)

def make_conf(n, box=(40.0, 40.0, 40.0), unwrapped=False, zero_orient=False,
              nan_box=False):
    lines = ["t = 0"]
    if nan_box:
        lines.append("b = 40.0 nan 40.0")
    else:
        lines.append("b = %s" % " ".join(repr(v) for v in box))
    lines.append("E = 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0")
    for i in range(n):
        if unwrapped:
            pos = (-5.0 + i, 3.0, 70.0 - i)   # outside the declared box (valid PBC)
        else:
            pos = (1.0 + i, 2.0, 3.0)
        o1 = (1.0, 0.0, 0.0)
        o2 = (0.0, 0.0, 0.0) if zero_orient else (0.0, 1.0, 0.0)
        vals = list(pos) + list(o1) + list(o2) + [0.0, 0.0, 0.0] + [0.1, 0.1, 0.1]
        lines.append(" ".join(repr(v) for v in vals))
    return "\n".join(lines) + "\n"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write_pack(parts_meta, anchor_meta, candidate_id="S23_NARCISSUS_ECHO",
               doi="10.9999/verifier76-synthetic-fixture",
               design_basis="SYNTHETIC_FIXTURE", dup_keys=False):
    pack = {
        "schema_version": 1,
        "kind": "alt_dna_two_part_source_pack",
        "claim_ceiling": "BIBLIOGRAPHIC",
        "scientific_runs": 0,
        "network_bytes_downloaded": 0,
        "selected_candidate_id": candidate_id,
        "evidence_date_utc": "2026-10-24",
        "candidates": [{
            "candidate_id": candidate_id,
            "design_basis": design_basis,
            "doi": doi,
            "publication_url": "https://example.org/verifier76-fixture",
            "paper_evidence": "SOURCE_ARTICLE_CONFIRMED",
            "structure_description": "VERIFIER independent synthetic two-part fixture",
            "parts": parts_meta,
            "interface": {
                "mechanism": "DNA_HYBRIDIZATION",
                "paper_status": "SOURCE_ARTICLE_CONFIRMED",
                "anchor_map": anchor_meta,
                "geometry_status": "INFERRED_CANDIDATE",
            },
            "reported_design_files": [],
            "provenance_note": "independent verifier synthetic fixture",
            "source_verdict": "BLOCKED_SOURCE",
            "next_required_input": "n/a (fixture)",
        }],
    }
    text = json.dumps(pack, indent=1)
    if dup_keys:
        text = text.replace('"claim_ceiling": "BIBLIOGRAPHIC",',
                            '"claim_ceiling": "BIBLIOGRAPHIC",\n "claim_ceiling": "BIBLIOGRAPHIC",', 1)
    return text

def rec(path_abs, status="CONTENT_VERIFIED", rights="ALLOWED", **over):
    rel = os.path.relpath(path_abs, ROOT)
    data = open(path_abs, "rb").read()
    r = {
        "status": status,
        "rights": rights,
        "sha256": sha(data),
        "size_bytes": len(data),
        "path": rel,
        "source_url": "https://example.org/verifier76-fixture/" + rel,
    }
    r.update(over)
    return r

def run_gate(pack_text, candidate):
    p = os.path.join(ROOT, "pack_under_test.json")
    open(p, "w").write(pack_text)
    r = subprocess.run(
        [sys.executable, "-m", "knowledge_pack.alt_pair_source_gate", p,
         "--candidate", candidate, "--root", ROOT],
        cwd=SRC, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": os.path.join(SRC, "scripts")})
    try:
        out = json.loads(r.stdout)
        outcome = out.get("outcome")
        reasons = out.get("reasons", [])
    except Exception:
        outcome = "UNPARSEABLE"
        reasons = [(r.stdout or "")[-200:], (r.stderr or "")[-300:]]
    return r.returncode, outcome, reasons

def pair(a="ALPHA", b="BETA", ia=0, ib=11, sa=SEG_A, sb=SEG_B,
         ae="3p", be="5p", extra=None):
    p = {"status": "SOURCE_CONFIRMED", "kind": "NONCOVALENT_DNA_HYBRIDIZATION",
         "part_a": a, "part_b": b, "a_index": ia, "b_index": ib,
         "segment_a": sa, "segment_b": sb, "a_end": ae, "b_end": be}
    if extra:
        p.update(extra)
    return p

def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    os.makedirs(ROOT)

    alpha_top_text, na = strand_rows(ALPHA_BASES)
    beta_top_text, nb = strand_rows(BETA_BASES)
    open(os.path.join(ROOT, "alpha.top"), "w").write(alpha_top_text)
    open(os.path.join(ROOT, "beta.top"), "w").write(beta_top_text)

    ANCHOR_VALID = {"kind": "two_part_dna_interface_map", "pairs": [pair()]}

    scenarios = {}

    def build(tag, conf_kw=None, anchor=None, post_mutate=None, rec_kw=None,
              pack_kw=None):
        """post_mutate(d) runs AFTER hashing -> file/pack disagree on purpose."""
        d = os.path.join(ROOT, tag)
        os.makedirs(d)
        shutil.copy(os.path.join(ROOT, "alpha.top"), d)
        shutil.copy(os.path.join(ROOT, "beta.top"), d)
        kw = dict(unwrapped=True)
        kw.update(conf_kw or {})
        open(os.path.join(d, "alpha.dat"), "w").write(make_conf(na, **kw))
        open(os.path.join(d, "beta.dat"), "w").write(make_conf(nb, **kw))
        am = anchor if anchor is not None else ANCHOR_VALID
        open(os.path.join(d, "anchor_map.json"), "w").write(json.dumps(am, indent=1))
        rk = dict(rec_kw or {})
        parts = [
            {"part_id": "ALPHA",
             "topology": rec(os.path.join(d, "alpha.top"), **rk.get("alpha.top", {})),
             "configuration": rec(os.path.join(d, "alpha.dat"), **rk.get("alpha.dat", {}))},
            {"part_id": "BETA",
             "topology": rec(os.path.join(d, "beta.top"), **rk.get("beta.top", {})),
             "configuration": rec(os.path.join(d, "beta.dat"), **rk.get("beta.dat", {}))},
        ]
        pk = dict(pack_kw or {})
        pk["parts_meta"] = parts
        pk["anchor_meta"] = rec(os.path.join(d, "anchor_map.json"), **rk.get("anchor", {}))
        pack_text = write_pack(**pk)
        if post_mutate:
            post_mutate(d, pack_text)
        return pack_text

    # ---------------- positive control: valid fixture, unwrapped PBC positions
    scenarios["P+_VALID_UNWRAPPED_PBC"] = build("p_plus")

    # ---------------- negatives
    scenarios["N01_NAN_BOX"] = build("n01", conf_kw={"nan_box": True})
    scenarios["N02_ZERO_ORIENTATION"] = build("n02", conf_kw={"zero_orient": True})

    # A/B-swapped duplicate pair reusing the same physical nucleotides
    am_swap = {"kind": "two_part_dna_interface_map",
               "pairs": [pair(), pair(a="BETA", b="ALPHA", ia=11, ib=0,
                                      sa=SEG_B, sb=SEG_A, ae="5p", be="3p")]}
    scenarios["N03_AB_SWAPPED_REUSE"] = build("n03", anchor=am_swap)

    am_internal = {"kind": "two_part_dna_interface_map",
                   "pairs": [pair(ia=5)]}   # mid-strand: n3 != -1
    scenarios["N04_INTERNAL_ANCHOR"] = build("n04", anchor=am_internal)

    am_polarity = {"kind": "two_part_dna_interface_map",
                   "pairs": [pair(ae="5p")]}   # index 0 is the 3' terminus
    scenarios["N05_WRONG_POLARITY"] = build("n05", anchor=am_polarity)

    long13 = "CATGCACGTACGT"                       # 13 nt > 12-nt strand
    am_overlong = {"kind": "two_part_dna_interface_map",
                   "pairs": [pair(sa=long13, sb=long13[::-1].translate(RC))]}
    scenarios["N06_SEGMENT_LONGER_THAN_STRAND"] = build("n06", anchor=am_overlong)

    def tamper_top(d, pack_text):
        p = os.path.join(d, "alpha.top")
        data = open(p).read()               # read BEFORE truncating write
        open(p, "w").write(data.replace(" A ", " T ", 1))  # same size
    scenarios["N07_SHA256_TAMPER"] = build("n07", post_mutate=tamper_top)

    scenarios["N08_RIGHTS_RESTRICTED"] = build(
        "n08", rec_kw={"alpha.top": {"rights": "RESTRICTED"}})
    scenarios["N09_RIGHTS_UNKNOWN_CONTENT_VERIFIED"] = build(
        "n09", rec_kw={"beta.dat": {"rights": "UNKNOWN"}})

    def grow_16mib(d, pack_text):
        with open(os.path.join(d, "alpha.top"), "ab") as fh:
            fh.write(b"x" * (16 * 1024 * 1024))
    scenarios["N10_SIZE_CAP_EXCEEDED"] = build("n10", post_mutate=grow_16mib)

    def grow_16mib_hidden(d, pack_text):
        with open(os.path.join(d, "alpha.top"), "ab") as fh:
            fh.write(b"x" * (16 * 1024 * 1024 + 1))
    scenarios["N10B_READTIME_CAP"] = build(
        "n10b", post_mutate=grow_16mib_hidden,
        rec_kw={"alpha.top": {"size_bytes": 100}})   # declared <= cap, actual > cap

    d = os.path.join(ROOT, "n11"); os.makedirs(d)
    shutil.copy(os.path.join(ROOT, "alpha.top"), d)
    shutil.copy(os.path.join(ROOT, "beta.top"), d)
    open(os.path.join(d, "alpha.dat"), "w").write(make_conf(na, unwrapped=True))
    open(os.path.join(d, "beta.dat"), "w").write(make_conf(nb, unwrapped=True))
    open(os.path.join(d, "anchor_map.json"), "w").write(json.dumps(ANCHOR_VALID, indent=1))
    parts = [
        {"part_id": "ALPHA", "topology": rec(os.path.join(d, "alpha.top")),
         "configuration": rec(os.path.join(d, "alpha.dat"))},
        {"part_id": "BETA", "topology": rec(os.path.join(d, "beta.top")),
         "configuration": rec(os.path.join(d, "beta.dat"))},
    ]
    am_rec = rec(os.path.join(d, "anchor_map.json"))
    am_rec["size_bytes"] += 1
    scenarios["N11_SIZE_MISMATCH"] = write_pack(parts, am_rec)

    d = os.path.join(ROOT, "n12"); os.makedirs(d)
    shutil.copy(os.path.join(ROOT, "alpha.top"), d)
    shutil.copy(os.path.join(ROOT, "beta.top"), d)
    open(os.path.join(d, "alpha.dat"), "w").write(make_conf(na, unwrapped=True))
    open(os.path.join(d, "beta.dat"), "w").write(make_conf(nb, unwrapped=True))
    open(os.path.join(d, "anchor_map.json"), "w").write(json.dumps(ANCHOR_VALID, indent=1))
    abs_top = rec(os.path.join(d, "alpha.top"))
    abs_top["path"] = os.path.join(d, "alpha.top")
    parts = [
        {"part_id": "ALPHA", "topology": abs_top,
         "configuration": rec(os.path.join(d, "alpha.dat"))},
        {"part_id": "BETA", "topology": rec(os.path.join(d, "beta.top")),
         "configuration": rec(os.path.join(d, "beta.dat"))},
    ]
    scenarios["N12_ABSOLUTE_PATH"] = write_pack(parts, rec(os.path.join(d, "anchor_map.json")))

    d = os.path.join(ROOT, "n13"); os.makedirs(d)
    shutil.copy(os.path.join(ROOT, "beta.top"), d)
    open(os.path.join(d, "alpha.dat"), "w").write(make_conf(na, unwrapped=True))
    open(os.path.join(d, "beta.dat"), "w").write(make_conf(nb, unwrapped=True))
    open(os.path.join(d, "anchor_map.json"), "w").write(json.dumps(ANCHOR_VALID, indent=1))
    open(os.path.join(ROOT, "outside.top"), "w").write(alpha_top_text)
    trav = {"status": "CONTENT_VERIFIED", "rights": "ALLOWED",
            "sha256": sha(alpha_top_text.encode()), "size_bytes": len(alpha_top_text),
            "path": "../outside.top", "source_url": "https://example.org/x"}
    parts = [
        {"part_id": "ALPHA", "topology": trav,
         "configuration": rec(os.path.join(d, "alpha.dat"))},
        {"part_id": "BETA", "topology": rec(os.path.join(d, "beta.top")),
         "configuration": rec(os.path.join(d, "beta.dat"))},
    ]
    scenarios["N13_DOTDOT_TRAVERSAL"] = write_pack(parts, rec(os.path.join(d, "anchor_map.json")))

    d = os.path.join(ROOT, "n14"); os.makedirs(d)
    shutil.copy(os.path.join(ROOT, "beta.top"), d)
    open(os.path.join(d, "alpha.dat"), "w").write(make_conf(na, unwrapped=True))
    open(os.path.join(d, "beta.dat"), "w").write(make_conf(nb, unwrapped=True))
    open(os.path.join(d, "anchor_map.json"), "w").write(json.dumps(ANCHOR_VALID, indent=1))
    open(os.path.join(ROOT, "real_top_for_link.top"), "w").write(alpha_top_text)
    os.symlink(os.path.join(ROOT, "real_top_for_link.top"), os.path.join(d, "alpha.top"))
    link = {"status": "CONTENT_VERIFIED", "rights": "ALLOWED",
            "sha256": sha(alpha_top_text.encode()), "size_bytes": len(alpha_top_text),
            "path": "n14/alpha.top", "source_url": "https://example.org/x"}
    parts = [
        {"part_id": "ALPHA", "topology": link,
         "configuration": rec(os.path.join(d, "alpha.dat"))},
        {"part_id": "BETA", "topology": rec(os.path.join(d, "beta.top")),
         "configuration": rec(os.path.join(d, "beta.dat"))},
    ]
    scenarios["N14_SYMLINK_IN_PATH"] = write_pack(parts, rec(os.path.join(d, "anchor_map.json")))

    scenarios["N15_DUPLICATE_JSON_KEYS"] = build("n15", pack_kw={"dup_keys": True})

    d = os.path.join(ROOT, "n16"); os.makedirs(d)
    shutil.copy(os.path.join(ROOT, "alpha.top"), d)
    shutil.copy(os.path.join(ROOT, "beta.top"), d)
    open(os.path.join(d, "alpha.dat"), "w").write(make_conf(na, unwrapped=True))
    open(os.path.join(d, "beta.dat"), "w").write(make_conf(nb, unwrapped=True))
    open(os.path.join(d, "anchor_map.json"), "w").write(json.dumps(ANCHOR_VALID, indent=1))
    parts = [
        {"part_id": "ALPHA", "topology": rec(os.path.join(d, "alpha.top")),
         "configuration": rec(os.path.join(d, "alpha.dat"))},
        {"part_id": "BETA", "topology": rec(os.path.join(d, "beta.top")),
         "configuration": rec(os.path.join(d, "beta.dat"))},
    ]
    pack_text = write_pack(parts, rec(os.path.join(d, "anchor_map.json")))
    scenarios["N16_CLAIM_INFLATION"] = pack_text.replace(
        '"claim_ceiling": "BIBLIOGRAPHIC"', '"claim_ceiling": "ASSEMBLY_VALIDATED"')

    scenarios["N17_NONDICT_ROOT"] = json.dumps([1, 2, 3])

    scenarios["N18_UNKNOWN_RIGHTS_VOCAB"] = build(
        "n18", rec_kw={"beta.top": {"rights": "MAYBE"}})

    d = os.path.join(ROOT, "n19"); os.makedirs(d)
    shutil.copy(os.path.join(ROOT, "alpha.top"), d)
    shutil.copy(os.path.join(ROOT, "beta.top"), d)
    open(os.path.join(d, "beta.dat"), "w").write(make_conf(nb, unwrapped=True))
    open(os.path.join(d, "anchor_map.json"), "w").write(json.dumps(ANCHOR_VALID, indent=1))
    phantom = {"status": "CONTENT_VERIFIED", "rights": "ALLOWED",
               "sha256": sha(b"ghost"), "size_bytes": 5,
               "path": "n19/ghost.dat", "source_url": "https://example.org/x"}
    parts = [
        {"part_id": "ALPHA", "topology": rec(os.path.join(d, "alpha.top")),
         "configuration": phantom},
        {"part_id": "BETA", "topology": rec(os.path.join(d, "beta.top")),
         "configuration": rec(os.path.join(d, "beta.dat"))},
    ]
    scenarios["N19_MISSING_FILE"] = write_pack(parts, rec(os.path.join(d, "anchor_map.json")))

    results = {}
    for tag in sorted(scenarios):
        pack_text = scenarios[tag]
        code, outcome, reasons = run_gate(pack_text, "S23_NARCISSUS_ECHO")
        results[tag] = (code, outcome, reasons[:3])
        print("%-36s exit=%d outcome=%s" % (tag, code, outcome))
        for rr in reasons[:2]:
            print("      - %s" % rr)
    print("DONE")

if __name__ == "__main__":
    main()
