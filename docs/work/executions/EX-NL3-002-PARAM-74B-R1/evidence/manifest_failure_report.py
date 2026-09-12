"""Arm-manifest derivation failure report for EX-NL3-002-PARAM-74B-R1.

Runs the frozen arm-manifest-v1 derivation (scripts/e2/arm_manifest.py,
derive_manifest) on frame 0 of the digest-gated 74b.conf TWICE and records the
deterministic ArmManifestError ("no threshold in PARALLEL_GRID yields two
dominant rigid blocks") with the size tables. Per WO-NL3-002-PARAM per-variant
addition 2 this is the BLOCKED condition for the 74b variant (honest gap); the
other variants of the series are not affected. No runs are started.
"""
import json
import os
import re
import sys

REPO = r"C:\NanoLab\nl3-002-param-74b"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-PARAM-74B-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.arm_manifest import ArmManifestError, derive_manifest  # noqa: E402
from e2.canonical import canonical_json  # noqa: E402
from e2.digests import git_blob_sha1, sha256_bytes  # noqa: E402
from hinge_family.oxdna_conf import Configuration  # noqa: E402
from hinge_family.oxdna_topology import Topology  # noqa: E402

SRC = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "nl3-002-param-74b-src")


def parse_tables(message):
    """Extract the per-threshold size tables from the error message (top 10 per threshold)."""
    tables = {}
    for m in re.finditer(r"(\d+\.\d+): (\[[^\]]*\])", message):
        sizes = json.loads(m.group(2))
        tables[m.group(1)] = sizes[:10]
    return tables


def main() -> int:
    top_path = os.path.join(SRC, "MD_Hinges__74b.top")
    conf_path = os.path.join(SRC, "MD_Hinges__74b.conf")
    with open(top_path, "rb") as h:
        top_bytes = h.read()
    with open(conf_path, "rb") as h:
        conf_bytes = h.read()
    topology = Topology.from_file(top_path)
    topology.check_chain_integrity()
    conf = Configuration.from_file(conf_path)
    messages = []
    for attempt in (1, 2):
        try:
            derive_manifest(conf, topology)
            messages.append(None)
        except ArmManifestError as exc:
            messages.append(str(exc))
    failure = all(m is not None for m in messages)
    deterministic = messages[0] == messages[1]
    report = {
        "schema_version": 1,
        "kind": "e2_arm_manifest_derivation_failure",
        "execution_id": "EX-NL3-002-PARAM-74B-R1",
        "variant": "74b",
        "algorithm": "arm-manifest-v1 (frozen, scripts/e2/arm_manifest.py, same derivation as 0b/11b/32b/53b)",
        "inputs": {
            "MD_Hinges/74b.top": {"size_bytes": len(top_bytes), "blob_sha1": git_blob_sha1(top_bytes), "sha256": sha256_bytes(top_bytes)},
            "MD_Hinges/74b.conf": {"size_bytes": len(conf_bytes), "blob_sha1": git_blob_sha1(conf_bytes), "sha256": sha256_bytes(conf_bytes)},
        },
        "attempts": 2,
        "outcome": "FAILED_TWO_DOMINANT_BLOCKS" if failure else "UNEXPECTED",
        "error_message_head": messages[0][:200] if failure else None,
        "deterministic_identical_error": deterministic,
        "size_tables_top10_per_threshold": parse_tables(messages[0]) if failure else None,
        "rule": "WO-NL3-002-PARAM per-variant addition 2: no two dominant blocks -> BLOCKED this variant (honest gap); series continues with other variants",
        "consequence": "no simulation runs started for 74b; runs NOT_RUN; BLOCKED per stop rules",
    }
    out = os.path.join(EX, "evidence", "arm-manifest-74b-failure.json")
    with open(out, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(report) + "\n")
    print(canonical_json({k: v for k, v in report.items() if k != "size_tables_top10_per_threshold"}))
    return 0 if (failure and deterministic) else 1


if __name__ == "__main__":
    raise SystemExit(main())
