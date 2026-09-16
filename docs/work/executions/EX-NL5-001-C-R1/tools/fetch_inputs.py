#!/usr/bin/env python3
"""EX-NL5-001-C-R1 input retrieval: download-on-run with mandatory digest gates.

Pins come from the FROZEN release package provenance
(releases/nanolab-components-v0.1/provenance/source-digests.json):
size + blob_sha1 are mandatory gates for every file; sha256 is additionally
verified when its registry status is CONTENT_VERIFIED (recorded as
COMPUTED_NOT_VERIFIED otherwise, G1 vocabulary). No durable cache: single
disposable run dir.

Exit codes: 0 = all gates PASS, 3 = any gate failure (fail closed).
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/gauravarya77/DNA-hinge-simulations/{commit}/{rel}"
VARIANTS = ["0b", "11b", "32b", "53b"]


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    run_dir = Path(sys.argv[2]).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    pins = json.loads(
        (repo_root / "releases/nanolab-components-v0.1/provenance/source-digests.json").read_text(encoding="utf-8")
    )
    upstream = pins["upstream"]
    report: dict = {
        "kind": "nanolab_reproduction_input_verification",
        "execution_id": "EX-NL5-001-C-R1",
        "pin_source": "releases/nanolab-components-v0.1/provenance/source-digests.json",
        "upstream": {"repository": upstream["repository"], "pinned_commit": upstream["pinned_commit"]},
        "durable_cache": False,
        "variants": {},
    }
    status = 0
    for variant in VARIANTS:
        vreport = {}
        for rel, pin in pins["variants"][variant]["files"].items():
            url = BASE.format(commit=upstream["pinned_commit"], rel=rel)
            dest = run_dir / rel.replace("/", "__")
            with urllib.request.urlopen(url, timeout=120) as resp:  # nosec - pinned HTTPS raw fetch
                data = resp.read()
            blob_sha1 = git_blob_sha1(data)
            sha256 = hashlib.sha256(data).hexdigest()
            checks = {
                "size_bytes": len(data),
                "size_expected": pin["size_bytes"],
                "size_match": len(data) == pin["size_bytes"],
                "blob_sha1": blob_sha1,
                "blob_sha1_expected": pin["blob_sha1"],
                "blob_sha1_match": blob_sha1 == pin["blob_sha1"],
                "sha256_computed": sha256,
                "sha256_status_pin": pin.get("sha256_status", "ABSENT"),
                "sha256_check": "NOT_APPLICABLE",
            }
            if pin.get("sha256_status") == "CONTENT_VERIFIED":
                checks["sha256_check"] = "PASS" if sha256 == pin["sha256"] else "FAIL"
            checks["digest_gate"] = (
                "PASS" if checks["size_match"] and checks["blob_sha1_match"] and checks["sha256_check"] != "FAIL" else "FAIL"
            )
            if checks["digest_gate"] != "PASS":
                status = 3
            dest.write_bytes(data)
            vreport[rel] = checks
        report["variants"][variant] = vreport
        print(f"variant {variant}: " + ", ".join(f"{k.split('/')[-1]}={v['digest_gate']}" for k, v in vreport.items()))
    out = run_dir / "input-download-verification.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("verification record:", out)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
