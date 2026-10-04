"""Rebuild the R4.1 PRE-DATA package bindings (reviewer corrections M-2/M-3).

Run from the repository root (only on the R4.1 repair branch, PRE-DATA /
NOT FROZEN; this tool changes NO scientific identity — confirmatory seeds,
replacement pools, cursors and the R3 logical digest stay untouched):

    PYTHONPATH=scripts python3 -m nl5.repro_v02_r41_package

What it does, in order:

1. Re-verifies, from the committed record + contract, that the published
   confirmatory identities and replacement pools are the bit-exact
   deterministic streams (cursor + recorded skips). Any drift aborts.
2. Runs the pinned immutable-tree collision scan (contract
   ``exclusion_tree_pin``) for every accepted confirmatory/replacement
   identity (must be CLEAN outside the exact allowlist) and for every
   recorded ``SEED_COLLISION_TREE`` skip (must show >= 1 non-allowlisted
   hit). Writes the machine-bound scan manifest with its
   ``manifest_sha256``.
3. Computes and binds the R4.1 integrity digests:
   ``replacement_pool_sha256`` (pools) and ``record_r4_sha256`` /
   ``seed_record_r4_sha256`` (full R4 record) into the record and the
   contract, plus the ``collision_scan_manifest`` path+sha256 binding and
   the null frozen-subject pins of a NOT_FROZEN candidate.

Fail-closed: any scan error (non-repository, missing pinned object,
timeout, unexpected git exit code) aborts with a non-zero exit — the
package is never silently left half-bound.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from nl5.repro_v02_seeds import (
    build_collision_scan_manifest,
    collision_manifest_digest,
    r4_record_digest,
    replacement_pool_digest,
    replay_replacement_stream,
    replay_variant_stream,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = REPO_ROOT / "docs" / "work" / "executions" / "EX-NL5-V02-PREFREEZE-HARDENING-R4" / "evidence"
RECORD_PATH = EVIDENCE / "repro-v0-2-seed-record-PRE_DATA_R4.json"
CONTRACT_PATH = EVIDENCE / "repro-v0-2-freeze-contract-PRE_DATA_R4.json"
MANIFEST_PATH = EVIDENCE / "r4-1-collision-scan-manifest-R4.json"

PAIRED_SEMANTICS = (
    "pair-level one-shot ledger (R4.1 M-4): pair_id unique; one frozen seed_identity per "
    "pair; attempt ids globally unique; author+external legs belong to the same pair; "
    "replacement ONLY for a terminal PAIR_FAILED_TECHNICAL pair; at most ONE replacement "
    "assignment per failed pair (repeat request rejected, quota/cursor untouched); the "
    "replacement consumes the next frozen pool identity in order, creates a NEW pair and "
    "schedules BOTH legs"
)
ATTEMPT_ID_RULE = (
    "<run_base> for the original pair legs; <run_base>-R<n> for retry/replacement attempts; "
    "attempt ids globally unique forever (reuse rejected); both legs of a replacement pair "
    "are scheduled by request_replacement and resolved via record_outcome"
)


def fail(message: str) -> None:
    print(f"R4.1 package rebuild FAILED (fail-closed): {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    anchor = record["anchor"]

    # 1. Safety: the published streams must replay bit-exactly before any
    #    digest is bound to them.
    for variant, stream in record["seeds"].items():
        skips = {entry["index"] for entry in record["skipped_identities"][variant]}
        replayed = replay_variant_stream(anchor, variant, record["indices_consumed"][variant], skips)
        if replayed != stream:
            fail(f"confirmatory replay drift for {variant}")
    for variant, pool in record["replacement_pools"].items():
        replayed_pool = replay_replacement_stream(
            anchor,
            variant,
            pool["start_index"],
            len(pool["seeds"]),
            pool.get("skipped") or [],
        )
        if replayed_pool != pool["seeds"]:
            fail(f"replacement pool replay drift for {variant}")
    if record["seeds"] != contract["confirmatory_seeds"]:
        fail("record/contract confirmatory drift")
    if contract["scientific_subject"]["freeze_status"] != "NOT_FROZEN":
        fail("this tool only rebinds the PRE-DATA / NOT FROZEN package")

    # 2. Pinned-tree scan manifest (accepted CLEAN + every skip proven).
    manifest = build_collision_scan_manifest(
        REPO_ROOT,
        exclusion_tree_pin=record["exclusion_tree_pin"],
        allowlist_paths=list(record["scan_context_paths_exact"]),
        confirmatory_seeds=record["seeds"],
        replacement_pools=contract["replacement"]["pools"],
        skipped_identities=record["skipped_identities"],
    )
    if manifest["manifest_sha256"] != collision_manifest_digest(manifest):
        fail("manifest digest self-check failed")
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 3. R4.1 integrity digests + bindings.
    pools_digest = replacement_pool_digest(contract["replacement"]["pools"])
    record["replacement_pool_sha256"] = pools_digest
    record["record_r4_sha256"] = r4_record_digest(record)
    RECORD_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    record_file_sha256 = hashlib.sha256(RECORD_PATH.read_bytes()).hexdigest()
    contract["scientific_subject"]["seed_record_file_sha256"] = record_file_sha256
    contract["scientific_subject"]["frozen_subject_head"] = None
    contract["scientific_subject"]["frozen_subject_tree"] = None
    contract["replacement_pool_sha256"] = pools_digest
    contract["seed_record_r4_sha256"] = record["record_r4_sha256"]
    contract["collision_scan_manifest"] = {
        "path": str(MANIFEST_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
    }
    contract["replacement"]["paired_semantics"] = PAIRED_SEMANTICS
    contract["replacement"]["attempt_id_rule"] = ATTEMPT_ID_RULE
    CONTRACT_PATH.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "replacement_pool_sha256": pools_digest,
        "record_r4_sha256": record["record_r4_sha256"],
        "record_sha256_r3_provenance": record["record_sha256"],
        "seed_record_file_sha256": record_file_sha256,
        "collision_scan_manifest": {
            "path": contract["collision_scan_manifest"]["path"],
            "sha256": contract["collision_scan_manifest"]["sha256"],
        },
        "accepted_confirmatory_scanned": sum(len(v) for v in record["seeds"].values()),
        "accepted_replacement_scanned": sum(
            len(p["seeds"]) for p in contract["replacement"]["pools"].values()
        ),
        "recorded_skips_proven": sum(len(v) for v in record["skipped_identities"].values()),
        "freeze_status": contract["scientific_subject"]["freeze_status"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
