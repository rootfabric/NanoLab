"""Offline tests for the real ExecutorAdapter (WO-NL4-002, EX-NL4-002-E3-MECH-R1).

No WSL, no network, no engine: only pure functions (digest gate, input
builder, candidate narrowing/replay plumbing).

F-1 fix (BATCH_REVIEWER_VERDICT.md, EX-NL4-002-E3-REVAL-R1): these five
tests were originally module-level functions, which unittest does NOT
collect — they existed but never ran (claimed "291 tests" was actually 287).
They are now collected in a TestCase subclass with real assertions, so the
suite number reflects reality.
"""
from __future__ import annotations

import os
import sys
import unittest

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


class TestRealExecutor(unittest.TestCase):
    def test_build_input_text_deviations(self):
        text, deviations = build_input_text(PRO_CPU_TEMPLATE, "11b", 202008, 50000, "e3-grid-r001")
        keys = {d["key"]: d for d in deviations}
        self.assertEqual(keys["steps"]["confirm"], "50000")
        self.assertEqual(keys["seed"]["confirm"], "202008")
        self.assertEqual(
            keys["topology"],
            {"key": "topology", "author": "74b.top", "confirm": "11b.top",
             "reason": keys["topology"]["reason"]},
        )
        self.assertEqual(keys["trajectory_file"]["confirm"], "e3-grid-r001_traj.dat")
        self.assertEqual(keys["print_conf_interval"]["confirm"], "4000")
        self.assertEqual(keys["print_energy_every"]["confirm"], "100")
        self.assertIsNone(keys["lastconf_file"]["author"])
        self.assertEqual(keys["lastconf_file"]["confirm"], "e3-grid-r001_last.dat")
        # all deviations sorted by key
        self.assertEqual(
            [d["key"] for d in deviations], sorted(d["key"] for d in deviations)
        )
        lines = dict(
            (part[0].strip(), part[1].strip())
            for line in text.splitlines()
            if "=" in line and not line.startswith("#")
            for part in [line.split("=", 1)]
        )
        self.assertEqual(lines["steps"].strip(), "50000")
        self.assertEqual(lines["seed"].strip(), "202008")
        self.assertEqual(lines["conf_file"].strip(), "11b.conf")
        self.assertEqual(lines["lastconf_file"].strip(), "e3-grid-r001_last.dat")

    def test_build_input_text_fails_closed_on_missing_key(self):
        broken = "steps = 2e7\nseed = 7777\n"
        with self.assertRaises(Exception) as ctx:
            build_input_text(broken, "0b", 1, 50000, "pfx")
        self.assertIn("missing keys", str(ctx.exception))

    def test_verify_source_bytes_gate(self):
        data = b"abcdef"
        pin = {
            "size_bytes": len(data),
            "blob_sha1": git_blob_sha1(data),
            "sha256": sha256_bytes(data),
            "sha256_provenance": "R1_CONTENT_VERIFIED",
        }
        entry = verify_source_bytes("x", data, pin)
        self.assertEqual(entry["digest_gate"], "PASS")
        self.assertTrue(entry["sha256"]["match"])
        # size mismatch fails even with correct digests of the wrong bytes
        bad = dict(pin, size_bytes=len(data) + 1)
        self.assertEqual(verify_source_bytes("x", data, bad)["digest_gate"], "FAIL")
        # blob mismatch fails
        bad = dict(pin, blob_sha1="0" * 40)
        self.assertEqual(verify_source_bytes("x", data, bad)["digest_gate"], "FAIL")
        # NOT_VERIFIED registry entry: sha256 computed, match None, gate may PASS
        partial = dict(pin, sha256=None, sha256_provenance="NOT_VERIFIED")
        entry = verify_source_bytes("x", data, partial)
        self.assertEqual(entry["digest_gate"], "PASS")
        self.assertIsNone(entry["sha256"]["match"])
        self.assertEqual(entry["sha256"]["computed"], sha256_bytes(data))

    def test_candidate_digest_matches_mock_convention(self):
        from nl4.mock_executor import _digest

        cand = {"variant": "32b", "steps": 50000, "seed": 203012}
        self.assertEqual(candidate_digest(cand), _digest(cand))

    def test_e3_space_excludes_74b(self):
        self.assertNotIn("74b", E3_VARIANTS)
        self.assertEqual(set(E3_VARIANTS), {"0b", "11b", "32b", "53b"})


if __name__ == "__main__":
    unittest.main()
