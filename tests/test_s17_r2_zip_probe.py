"""Tests for the S17 R2 bounded remote-ZIP central-directory probe.

WO-PREP-S17-R2. All fixtures are synthetic in-memory zips: no network access
happens in this module (the ``--fetch`` path is only exercised for its
fail-closed argument handling, never for actual transfers).
"""
from __future__ import annotations

import io
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from knowledge_pack import s17_zip_probe as zp


def build_zip(entries: dict[str, bytes], method: int = zipfile.ZIP_DEFLATED) -> tuple[bytes, list[tuple[str, int, int, int, int]]]:
    """Build an in-memory zip; returns (bytes, [(name, csize, usize, crc, lho)])."""
    buf = io.BytesIO()
    infos = []
    with zipfile.ZipFile(buf, "w", method) as zf:
        for name, data in entries.items():
            zi = zipfile.ZipInfo(name)
            zi.compress_type = method
            zf.writestr(zi, data)
        for zi in zf.infolist():
            infos.append((zi.filename, zi.compress_size, zi.file_size, zi.CRC, zi.header_offset))
    return buf.getvalue(), infos


def tail_window(archive: bytes, nbytes: int) -> bytes:
    return archive[-nbytes:]


class CentralDirectoryParsing(unittest.TestCase):
    def test_parses_synthetic_zip_central_directory(self):
        entries = {"run/input": b"topology = linked.top\n", "run/linked.top": b"2 1\n0 A -1 1\n1 A 0 -1\n"}
        archive, infos = build_zip(entries)
        cd = zp.parse_central_directory(tail_window(archive, 4096), len(archive))
        self.assertEqual({e.name for e in cd.entries}, set(entries))
        for (name, csize, usize, crc, lho) in infos:
            e = next(x for x in cd.entries if x.name == name)
            self.assertEqual(e.compressed_size, csize)
            self.assertEqual(e.uncompressed_size, usize)
            self.assertEqual(e.crc32, crc)
            self.assertEqual(e.local_header_offset, lho)

    def test_listing_cli_is_deterministic(self):
        entries = {"a.txt": b"hello", "d/b.txt": b"world" * 40}
        archive, _ = build_zip(entries)
        with tempfile.TemporaryDirectory() as td:
            win = Path(td) / "tail.bin"
            win.write_bytes(tail_window(archive, 8192))
            outs = []
            for _ in range(2):
                proc = subprocess.run(
                    [sys.executable, str(SCRIPTS / "knowledge_pack" / "s17_zip_probe.py"),
                     "--window", str(win), "--archive-size", str(len(archive)), "--list"],
                    capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                outs.append(proc.stdout)
            self.assertEqual(outs[0], outs[1])
            parsed = json.loads(outs[0])
            self.assertEqual(parsed["entry_count"], 2)

    def test_truncated_window_fails_closed(self):
        entries = {"a.txt": b"x" * 10}
        archive, _ = build_zip(entries)
        with self.assertRaises(zp.ZipProbeError):
            zp.parse_central_directory(tail_window(archive, 8), len(archive))

    def test_garbage_window_fails_closed(self):
        with self.assertRaises(zp.ZipProbeError):
            zp.parse_central_directory(b"\x00" * 256, 4096)

    def test_window_larger_than_archive_rejected(self):
        with self.assertRaises(zp.ZipProbeError):
            zp.parse_eocd(b"PK\x05\x06" + b"\x00" * 18, 10)

    def test_central_directory_outside_window_rejected(self):
        # Fabricate an EOCD claiming a central directory that starts before the window.
        window = bytearray(b"\x00" * 128)
        eocd = struct.pack("<IHHHHIIH", 0x06054b50, 0, 0, 1, 1, 400, 10_000_000, 0)
        window[-22:] = eocd
        with self.assertRaises(zp.ZipProbeError):
            zp.parse_central_directory(bytes(window), 10_000_500)


class Zip64Support(unittest.TestCase):
    def test_parses_zip64_eocd_markers(self):
        # Construct a minimal ZIP64 EOCD + locator + EOCD chain by hand.
        window = bytearray()
        cen = b"PK\x01\x02" + struct.pack("<HHHHHHIIIHHHHHII", 20, 20, 0, 0, 0, 0,
                                         0x12345678, 5, 5, 5, 0, 0, 0, 0, 0, 0) + b"z.txt"
        # sizes/offset patched via ZIP64 extra would go here; keep it simple:
        # declare entry with real 32-bit values, but force EOCD through ZIP64 path.
        zip64_eocd = struct.pack("<IQHHIIQQQQ", 0x06064b50, 44, 45, 45, 0, 0, 1, 1,
                                 len(cen), 1_000_000)
        loc = struct.pack("<IIQI", 0x07064b50, 0, 1, 1)
        eocd = struct.pack("<IHHHHIIH", 0x06054b50, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF,
                           0xFFFFFFFF, 0xFFFFFFFF, 0)
        window = cen + zip64_eocd + loc + eocd
        total = 1_000_000 + len(window)
        cd = zp.parse_central_directory(bytes(window), total)
        self.assertEqual(len(cd.entries), 1)
        self.assertEqual(cd.entries[0].name, "z.txt")
        self.assertEqual(cd.entries[0].uncompressed_size, 5)


class ExtractionPathSafety(unittest.TestCase):
    def test_safe_target_name_blocks_traversal(self):
        root = Path("/tmp/definitely-not-here-s17")
        for evil in ("../escape.txt", "a/../../escape.txt", "/abs/path.txt"):
            with self.assertRaises(zp.ZipProbeError):
                zp.safe_target_name(evil, root)

    def test_safe_target_name_blocks_directory_and_null_entries(self):
        root = Path("/tmp/definitely-not-here-s17")
        with self.assertRaises(zp.ZipProbeError):
            zp.safe_target_name("dir/", root)
        with self.assertRaises(zp.ZipProbeError):
            zp.safe_target_name("bad\x00name", root)

    def test_local_entry_rejects_oversized_uncompressed(self):
        e = zp.ZipEntry(name="bomb", compressed_size=4, uncompressed_size=zp.MAX_ENTRY_UNCOMPRESSED + 1,
                        crc32=0, method=0, local_header_offset=0)
        need = 30 + len(e.name) + e.compressed_size
        with self.assertRaises(zp.ZipProbeError):
            zp.parse_local_entry(lambda s, end: b"\x00" * need, e)

    @staticmethod
    def ranged(blob):
        return lambda s, e: blob[s:e + 1]

    def test_local_entry_verifies_crc_and_length(self):
        data = b"payload-bytes"
        header = struct.pack("<IHHHHHIIIHH", 0x04034b50, 20, 0, 0, 0, 0,
                             zlib_crc(data), len(data), len(data), 0, 0)
        blob = header + data
        e = zp.ZipEntry(name="", compressed_size=len(data), uncompressed_size=len(data),
                        crc32=zlib_crc(data), method=0, local_header_offset=0)
        self.assertEqual(zp.parse_local_entry(self.ranged(blob), e), data)
        bad = zp.ZipEntry(name="", compressed_size=len(data), uncompressed_size=len(data),
                          crc32=0xDEADBEEF, method=0, local_header_offset=0)
        with self.assertRaises(zp.ZipProbeError):
            zp.parse_local_entry(self.ranged(blob), bad)

    def test_local_entry_rejects_header_disagreement(self):
        data = b"abc"
        header = struct.pack("<IHHHHHIIIHH", 0x04034b50, 20, 0, 0, 0, 0, 1, 2, 3, 0, 0) + data
        e = zp.ZipEntry(name="", compressed_size=3, uncompressed_size=3, crc32=0, method=0,
                        local_header_offset=0)
        with self.assertRaises(zp.ZipProbeError):
            zp.parse_local_entry(self.ranged(header), e)

    def test_local_entry_handles_local_extra_field(self):
        # Regression: real Zenodo members carry a zip64 extra field inside the
        # LOCAL header; the data window must start after name + extra.
        data = b"true-member-bytes"
        extra = b"\x01\x00\x18\x00" + b"\x00" * 24  # header id 1, 24 B body
        header = struct.pack("<IHHHHHIIIHH", 0x04034b50, 20, 0, 0, 0, 0,
                             zlib_crc(data), len(data), len(data), 0, len(extra))
        blob = header + extra + data
        e = zp.ZipEntry(name="", compressed_size=len(data), uncompressed_size=len(data),
                        crc32=zlib_crc(data), method=0, local_header_offset=0)
        self.assertEqual(zp.parse_local_entry(self.ranged(blob), e), data)

    def test_local_entry_short_data_window_rejected(self):
        data = b"abcdef"
        header = struct.pack("<IHHHHHIIIHH", 0x04034b50, 20, 0, 0, 0, 0,
                             zlib_crc(data), len(data), len(data), 0, 0)
        blob = header + data[:-2]  # truncated archive tail
        e = zp.ZipEntry(name="", compressed_size=len(data), uncompressed_size=len(data),
                        crc32=zlib_crc(data), method=0, local_header_offset=0)
        with self.assertRaises(zp.ZipProbeError):
            zp.parse_local_entry(self.ranged(blob), e)


def zlib_crc(data: bytes) -> int:
    import zlib

    return zlib.crc32(data) & 0xFFFFFFFF


class FetchOptIn(unittest.TestCase):
    def test_extraction_without_fetch_flag_fails_closed(self):
        entries = {"a.txt": b"hi"}
        archive, _ = build_zip(entries)
        with tempfile.TemporaryDirectory() as td:
            win = Path(td) / "tail.bin"
            win.write_bytes(tail_window(archive, 4096))
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "knowledge_pack" / "s17_zip_probe.py"),
                 "--window", str(win), "--archive-size", str(len(archive)),
                 "--extract", "a.txt"],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("--fetch", proc.stderr)

    def test_extract_unknown_entry_fails_even_with_fetch(self):
        entries = {"a.txt": b"hi"}
        archive, _ = build_zip(entries)
        with tempfile.TemporaryDirectory() as td:
            win = Path(td) / "tail.bin"
            win.write_bytes(tail_window(archive, 4096))
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "knowledge_pack" / "s17_zip_probe.py"),
                 "--window", str(win), "--archive-size", str(len(archive)),
                 "--fetch", "--url", "https://invalid.invalid/x.zip",
                 "--out", str(Path(td) / "out"), "--extract", "not-there.txt"],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("not present", proc.stderr)


if __name__ == "__main__":
    unittest.main()
