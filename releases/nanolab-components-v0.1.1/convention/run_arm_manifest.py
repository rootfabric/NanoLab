"""EX-NL3-002-PROTO-R1 evidence runner: 0b arm manifest + v2 detector facts.

Runs inside the execution session only. Digest-gated download-on-run of the
pinned 0b.top/0b.conf (G1 = B, no durable cache: temp dir outside Git,
deleted in ``finally``). Produces, under evidence/:

* arm-manifest-0b.json   - the derived arm manifest (canonical JSON)
* v2-frame0.json         - v2 detector counts on the author frame 0 +
                           byte-determinism check of two derivations
"""
import json
import os
import shutil
import sys
import tempfile

REPO = r"C:\NanoLab\nl3-002-proto"
sys.path.insert(0, os.path.join(REPO, "scripts"))

from e2.arm_manifest import download_and_verify, derive_manifest
from e2.canonical import canonical_json
from e2.digests import git_blob_sha1, sha256_bytes
from e2.observables import reference_pairs_v2
from hinge_family.oxdna_conf import Configuration
from hinge_family.oxdna_topology import Topology

EVIDENCE = os.path.join(
    REPO, "docs", "work", "executions", "EX-NL3-002-PROTO-R1", "evidence"
)


def main() -> int:
    tmp_dir = os.path.join(
        tempfile.gettempdir(), "nl3-002-proto-src", "run-arm-manifest"
    )
    shutil.rmtree(tmp_dir, ignore_errors=True)
    try:
        download_report = download_and_verify(dest_dir=tmp_dir)
        with open(os.path.join(EVIDENCE, "source-download-verification.json"), "w", encoding="utf-8", newline="\n") as h:
            h.write(canonical_json(download_report))
        if download_report["digest_gate_all"] != "PASS":
            print("digest gate FAIL")
            return 1
        top_path = download_report["files"]["MD_Hinges/0b.top"]["local_path"]
        conf_path = download_report["files"]["MD_Hinges/0b.conf"]["local_path"]
        with open(top_path, "rb") as h:
            top_bytes = h.read()
        with open(conf_path, "rb") as h:
            conf_bytes = h.read()
        digests = {
            "MD_Hinges/0b.top": {
                "size_bytes": len(top_bytes),
                "blob_sha1": git_blob_sha1(top_bytes),
                "sha256": sha256_bytes(top_bytes),
            },
            "MD_Hinges/0b.conf": {
                "size_bytes": len(conf_bytes),
                "blob_sha1": git_blob_sha1(conf_bytes),
                "sha256": sha256_bytes(conf_bytes),
            },
        }
        topology = Topology.from_file(top_path)
        topology.check_chain_integrity()
        conf = Configuration.from_file(conf_path)

        manifest_1 = derive_manifest(conf, topology, {"digests": digests})
        manifest_2 = derive_manifest(conf, topology, {"digests": digests})
        r1 = canonical_json(manifest_1)
        r2 = canonical_json(manifest_2)
        assert r1 == r2, "manifest derivation is not byte-deterministic"

        mutual_1 = reference_pairs_v2(conf, topology, mutual_nearest=True)
        mutual_2 = reference_pairs_v2(conf, topology, mutual_nearest=True)
        greedy = reference_pairs_v2(conf, topology, mutual_nearest=False)
        assert canonical_json(mutual_1) == canonical_json(mutual_2)
        v2_report = {
            "schema_version": 1,
            "kind": "e2_proto_v2_frame0",
            "class": "pre-confirmatory detector calibration; fact, not fitting",
            "inputs": {"digests": digests},
            "frame": {"time": conf.time, "nucleotides": topology.nucleotides},
            "v2_mutual_nearest_pairs": len(mutual_1),
            "v2_greedy_pairs": len(greedy),
            "v1_window_pairs_reference": "26-29 (EX-NL3-002-PILOT-R1, window (0.05, 0.55])",
            "detector": "v2: window (0.05, 1.3], a1 antiparallel <= -0.3, mutual-nearest + greedy",
            "determinism": {
                "mutual_two_runs_byte_identical": True,
                "manifest_two_runs_byte_identical": True,
            },
            "adequacy_gate": "v2_mutual_nearest_pairs > 3000 expected plausible for ~8378-nt origami (measured fact)",
        }
        with open(os.path.join(EVIDENCE, "arm-manifest-0b.json"), "w", encoding="utf-8", newline="\n") as h:
            h.write(r1)
        with open(os.path.join(EVIDENCE, "v2-frame0.json"), "w", encoding="utf-8", newline="\n") as h:
            h.write(canonical_json(v2_report))
        print("manifest angle frame0:", manifest_1["validation"]["hinge_angle_frame0"]["angle_deg"])
        print("arm sizes:", manifest_1["arms"]["arm_a"]["size"], manifest_1["arms"]["arm_b"]["size"])
        print("v2 mutual pairs:", len(mutual_1), "greedy pairs:", len(greedy))
        return 0
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
