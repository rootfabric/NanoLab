"""Tests for the S17 R2 recovery evidence builder (offline, synthetic files)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from knowledge_pack import s17_recovery as rec


class RecoveryToolTests(unittest.TestCase):
    def test_digests_and_confirms_byte_identity(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            a = td / "a.bin"
            b = td / "sub" / "b.bin"
            b.parent.mkdir()
            a.write_bytes(b"same-bytes")
            b.write_bytes(b"same-bytes")
            spec = {"files": [{"label": "left", "path": str(a)},
                              {"label": "right", "path": str(b)}],
                    "relations": [{"kind": "byte_identity", "left": "left", "right": "right"}]}
            out = rec.run(spec)
            self.assertEqual(out["files"]["left"]["sha256"], hashlib.sha256(b"same-bytes").hexdigest())
            self.assertEqual(out["relations"][0]["verdict"], "CONFIRMED")
            self.assertEqual(out["problems"], [])

    def test_violated_identity_is_recorded_not_hidden(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            a = td / "a.bin"; a.write_bytes(b"x")
            b = td / "b.bin"; b.write_bytes(b"y")
            out = rec.run({"files": [{"label": "l", "path": str(a)},
                                     {"label": "r", "path": str(b)}],
                           "relations": [{"kind": "byte_identity", "left": "l", "right": "r"}]})
            self.assertEqual(out["relations"][0]["verdict"], "VIOLATED")

    def test_missing_file_is_a_recorded_problem(self):
        with tempfile.TemporaryDirectory() as td:
            out = rec.run({"files": [{"label": "gone", "path": str(Path(td) / "nope.bin")}]})
            self.assertIn("error", out["files"]["gone"])
            self.assertTrue(out["problems"])

    def test_duplicate_label_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "f.bin"; f.write_bytes(b"1")
            with self.assertRaises(rec.RecoveryError):
                rec.run({"files": [{"label": "x", "path": str(f)},
                                   {"label": "x", "path": str(f)}]})

    def test_unsupported_relation_kind_rejected(self):
        with self.assertRaises(rec.RecoveryError):
            rec.run({"files": [], "relations": [{"kind": "same_length", "left": "a", "right": "b"}]})

    def test_cli_writes_evidence_and_lists_counts(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            f = td / "f.bin"; f.write_bytes(b"zz")
            spec = td / "spec.json"
            spec.write_text(json.dumps({"files": [{"label": "f", "path": str(f)}]}))
            out = td / "evidence.json"
            proc = subprocess.run([sys.executable, str(SCRIPTS / "knowledge_pack" / "s17_recovery.py"),
                                   "--input", str(spec), "--out", str(out)],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("files: 1", proc.stdout)
            blob = json.loads(out.read_text())
            self.assertEqual(blob["kind"], "s17_r2_recovery_evidence")

    def test_cli_fails_closed_on_bad_spec(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            spec = td / "spec.json"
            spec.write_text(json.dumps({"nope": True}))
            proc = subprocess.run([sys.executable, str(SCRIPTS / "knowledge_pack" / "s17_recovery.py"),
                                   "--input", str(spec), "--out", str(td / "o.json")],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 3)
            self.assertIn("FAIL-CLOSED", proc.stderr)


if __name__ == "__main__":
    unittest.main()
