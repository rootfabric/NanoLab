"""Digest-gated download of the pinned 11b hinge source files for
EX-NL3-002-PARAM-11B-R1 (G1=B, no durable cache).

Downloads MD_Hinges/11b.top / MD_Hinges/11b.conf / MD_Hinges/pro_CPU.in into a
Windows temp dir OUTSIDE the repo; verifies size + git blob SHA-1 against
scripts/hinge_family/source_pins.json (mandatory gate per WO-NL3-002-PARAM).
SHA-256 pins for 11b.top/11b.conf have provenance NOT_VERIFIED (null in the
registry): the digest is computed at this first download and recorded in the
evidence as sha256_computed_at_first_download WITHOUT any claim on the registry
(registry extension is a separate control WO). pro_CPU.in carries the full pin
(size+blob_sha1+sha256, mandatory). Any mandatory mismatch -> FAIL exit 1
(BLOCKED condition per WO-NL3-002-PARAM stop rules).
"""
import json
import os
import sys
import urllib.request

REPO = r"C:\NanoLab\nl3-002-param-11b"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-PARAM-11B-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.canonical import canonical_json  # noqa: E402
from e2.digests import git_blob_sha1, sha256_bytes  # noqa: E402

BASE = "https://raw.githubusercontent.com/gauravarya77/DNA-hinge-simulations/23fd1ff7731e9017bd776f49206dc42d70d9fe91/"
FILES = ["MD_Hinges/11b.top", "MD_Hinges/11b.conf", "MD_Hinges/pro_CPU.in"]
DEST = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "nl3-002-param-11b-src")


def main() -> int:
    with open(os.path.join(REPO, "scripts", "hinge_family", "source_pins.json"), "r", encoding="utf-8") as h:
        pins = json.load(h)
    os.makedirs(DEST, exist_ok=True)
    report = {"schema_version": 1, "kind": "e2_param_source_download_verification",
              "execution_id": "EX-NL3-002-PARAM-11B-R1",
              "work_order": "NL3-002-PARAM", "protocol": "docs/research/E2_PROTO_R1.md (frozen, inherited) + docs/work/WO-NL3-002-PARAM.md",
              "download_base": BASE, "dest_dir": DEST, "durable_cache": False, "files": {}}
    ok = True
    for name in FILES:
        pin = pins["files"][name]
        url = BASE + name
        local = os.path.join(DEST, name.replace("/", "__"))
        with urllib.request.urlopen(url, timeout=120) as resp:
            data = resp.read()
        with open(local, "wb") as h:
            h.write(data)
        size_ok = len(data) == pin["size_bytes"]
        blob_ok = git_blob_sha1(data) == pin["blob_sha1"]
        entry = {
            "local_path": local,
            "size_bytes": len(data), "size_expected": pin["size_bytes"], "size_match": size_ok,
            "blob_sha1": git_blob_sha1(data), "blob_sha1_expected": pin["blob_sha1"], "blob_sha1_match": blob_ok,
        }
        if pin.get("sha256") is None:
            # NOT_VERIFIED pin: compute at first download, record as evidence, no registry claim
            entry["sha256"] = sha256_bytes(data)
            entry["sha256_pin_provenance"] = pin["sha256_provenance"]
            entry["sha256_computed_at_first_download"] = sha256_bytes(data)
            entry["sha256_gate"] = "COMPUTED_NOT_VERIFIED (recorded for future re-use; no registry claim)"
        else:
            sha_ok = sha256_bytes(data) == pin["sha256"]
            entry["sha256"] = sha256_bytes(data)
            entry["sha256_expected"] = pin["sha256"]
            entry["sha256_match"] = sha_ok
        mandatory = size_ok and blob_ok and (pin.get("sha256") is None or sha256_bytes(data) == pin["sha256"])
        entry["digest_gate"] = "PASS" if mandatory else "FAIL"
        ok = ok and mandatory
        report["files"][name] = entry
    report["digest_gate_all"] = "PASS" if ok else "FAIL"
    out = os.path.join(EX, "evidence", "source-download-verification.json")
    with open(out, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(report) + "\n")
    print(canonical_json(report))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
