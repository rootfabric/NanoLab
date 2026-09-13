"""Offline tests for the real ExecutorAdapter (WO-NL4-002, EX-NL4-002-E3-MECH-R1).

No WSL, no network, no engine: only pure functions (digest gate, input
builder, candidate narrowing/replay plumbing).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from nl4.real_executor import (  # noqa: E402
    E3_VARIANTS,
    build_input_text,
    candidate_digest,
    verify_source_bytes,
)
from e2.digests import git_blob_sha1, sha256_bytes  # noqa: E402

PRO_CPU_TEMPLATE = """##############################
####  PROGRAM PARAMETERS  ####
##############################
backend = CPU
backend_precision = double
debug = 1
seed = 7777

steps = 2e7
interaction_type = DNA2
salt_concentration = 0.5
T = 300K

topology = 74b.top
conf_file = 74b.conf
trajectory_file = pro.dat
log_file = log2.dat
energy_file = hinge_energy.dat
print_conf_interval = 4e3
print_energy_every = 4e3
external_forces = 0
"""


def test_build_input_text_deviations():
    text, deviations = build_input_text(PRO_CPU_TEMPLATE, "11b", 202008, 50000, "e3-grid-r001")
    keys = {d["key"]: d for d in deviations}
    assert keys["steps"]["confirm"] == "50000"
    assert keys["seed"]["confirm"] == "202008"
    assert keys["topology"] == {"key": "topology", "author": "74b.top", "confirm": "11b.top",
                                "reason": keys["topology"]["reason"]}
    assert keys["trajectory_file"]["confirm"] == "e3-grid-r001_traj.dat"
    assert keys["print_conf_interval"]["confirm"] == "4000"
    assert keys["print_energy_every"]["confirm"] == "100"
    assert keys["lastconf_file"]["author"] is None
    assert keys["lastconf_file"]["confirm"] == "e3-grid-r001_last.dat"
    # all deviations sorted by key
    assert [d["key"] for d in deviations] == sorted(d["key"] for d in deviations)
    lines = dict(
        (part[0].strip(), part[1].strip())
        for line in text.splitlines()
        if "=" in line and not line.startswith("#")
        for part in [line.split("=", 1)]
    )
    assert lines["steps"].strip() == "50000"
    assert lines["seed"].strip() == "202008"
    assert lines["conf_file"].strip() == "11b.conf"
    assert lines["lastconf_file"].strip() == "e3-grid-r001_last.dat"


def test_build_input_text_fails_closed_on_missing_key():
    broken = "steps = 2e7\nseed = 7777\n"
    try:
        build_input_text(broken, "0b", 1, 50000, "pfx")
    except Exception as exc:
        assert "missing keys" in str(exc)
    else:
        raise AssertionError("expected RealExecutorError for missing template keys")


def test_verify_source_bytes_gate():
    data = b"abcdef"
    pin = {
        "size_bytes": len(data),
        "blob_sha1": git_blob_sha1(data),
        "sha256": sha256_bytes(data),
        "sha256_provenance": "R1_CONTENT_VERIFIED",
    }
    entry = verify_source_bytes("x", data, pin)
    assert entry["digest_gate"] == "PASS"
    assert entry["sha256"]["match"] is True
    # size mismatch fails even with correct digests of the wrong bytes
    bad = dict(pin, size_bytes=len(data) + 1)
    assert verify_source_bytes("x", data, bad)["digest_gate"] == "FAIL"
    # blob mismatch fails
    bad = dict(pin, blob_sha1="0" * 40)
    assert verify_source_bytes("x", data, bad)["digest_gate"] == "FAIL"
    # NOT_VERIFIED registry entry: sha256 computed, match None, gate may PASS
    partial = dict(pin, sha256=None, sha256_provenance="NOT_VERIFIED")
    entry = verify_source_bytes("x", data, partial)
    assert entry["digest_gate"] == "PASS"
    assert entry["sha256"]["match"] is None
    assert entry["sha256"]["computed"] == sha256_bytes(data)


def test_candidate_digest_matches_mock_convention():
    from nl4.mock_executor import _digest

    cand = {"variant": "32b", "steps": 50000, "seed": 203012}
    assert candidate_digest(cand) == _digest(cand)


def test_e3_space_excludes_74b():
    assert "74b" not in E3_VARIANTS
    assert set(E3_VARIANTS) == {"0b", "11b", "32b", "53b"}
