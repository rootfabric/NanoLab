"""Digest-gated download of the pinned hinge source files (G1=B, no durable cache).

Downloads into a Windows temp dir OUTSIDE the repo; verifies size, git blob
SHA-1 and SHA-256 against scripts/hinge_family/source_pins.json before any
use. Prints a canonical JSON verification report (consumed by the execution
records); exits non-zero on any mismatch.
"""
import json
import os
import sys
import tempfile
import urllib.request

REPO = r"C:\NanoLab\nl3-002-pilot"
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.canonical import canonical_json
from e2.digests import git_blob_sha1, sha256_bytes

BASE = "https://raw.githubusercontent.com/gauravarya77/DNA-hinge-simulations/23fd1ff7731e9017bd776f49206dc42d70d9fe91/"
FILES = ["MD_Hinges/0b.top", "MD_Hinges/0b.conf", "MD_Hinges/pro_CPU.in"]
DEST = os.path.join(tempfile.gettempdir(), "nl3-002-pilot-src")


def main() -> int:
    with open(os.path.join(REPO, "scripts", "hinge_family", "source_pins.json"), "r", encoding="utf-8") as h:
        pins = json.load(h)
    os.makedirs(DEST, exist_ok=True)
    report = {"schema_version": 1, "kind": "e2_pilot_source_download_verification",
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
        sha_ok = sha256_bytes(data) == pin["sha256"]
        entry = {
            "local_path": local,
            "size_bytes": len(data), "size_expected": pin["size_bytes"], "size_match": size_ok,
            "blob_sha1": git_blob_sha1(data), "blob_sha1_expected": pin["blob_sha1"], "blob_sha1_match": blob_ok,
            "sha256": sha256_bytes(data), "sha256_expected": pin["sha256"], "sha256_match": sha_ok,
        }
        entry["digest_gate"] = "PASS" if (size_ok and blob_ok and sha_ok) else "FAIL"
        ok = ok and entry["digest_gate"] == "PASS"
        report["files"][name] = entry
    report["digest_gate_all"] = "PASS" if ok else "FAIL"
    out = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-PILOT-R1", "evidence", "source-download-verification.json")
    with open(out, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(report))
    print(canonical_json(report))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
