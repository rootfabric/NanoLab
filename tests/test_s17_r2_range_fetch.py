"""Offline tests for the S17 bounded multi-range fetcher (no network)."""

import struct
import unittest
import zipfile
import zlib

from knowledge_pack import s17_range_fetch as rf


def zlib_crc(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def build_zip_bytes(members: dict[str, bytes]) -> bytes:
    """Deterministic in-memory zip (deflate) with a real central directory."""
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return buf.getvalue()


class CentralDirectoryTests(unittest.TestCase):
    def test_parse_simple_zip(self):
        members = {"a/b.txt": b"hello s17", "c.bin": bytes(range(256))}
        blob = build_zip_bytes(members)
        cd = rf.parse_central_directory(blob, len(blob))
        self.assertEqual(set(cd), set(members))
        m = cd["a/b.txt"]
        self.assertEqual(m.uncompressed_size, 9)
        self.assertEqual(m.crc32, zlib_crc(b"hello s17"))
        self.assertEqual(m.method, 8)

    def test_rejects_bad_window(self):
        blob = build_zip_bytes({"x": b"y"})
        with self.assertRaises(rf.RangeFetchError):
            rf.parse_central_directory(blob[:20], len(blob))  # EOCD cut off
        # EOCD present but the central directory outside the window
        eocd = b"PK\x05\x06" + struct.pack("<IHHHHIIH", 0, 0, 0, 1, 1,
                                             len(blob), 0, 0)
        with self.assertRaises(rf.RangeFetchError):
            rf.parse_central_directory(eocd, len(blob))

    def test_zip64_cd_offset_resolution(self):
        # synth ZIP64 EOCD pointing at a CD inside the tail
        cd_record = struct.pack(rf._CD_FMT, 0x02014b50, 20, 20, 0, 0, 0, 0,
                                0, 0, 0, 4, 0, 0, 0, 0, 0, 40) + b"name"
        blob = cd_record + b"\x00" * 8
        z64 = struct.pack(rf._ZIP64_EOCD_FMT, 0x06064b50, 44, 45, 45, 0, 0,
                          1, 1, len(cd_record), 0) + b"\x00\x00\x00\x00"
        tail = blob + z64 + b"PK\x05\x06" + struct.pack("<IHHHHIIH", 0x06054b50,
                                                        0, 0, 0xFFFF, 0xFFFF,
                                                        0xFFFFFFFF, 0xFFFFFFFF, 0)
        # the blob starts at file offset (archive_size - len(tail))
        z64 = struct.pack(rf._ZIP64_EOCD_FMT, 0x06064b50, 44, 45, 45, 0, 0,
                          1, 1, len(cd_record), 10 ** 6 - len(tail)) + b"\x00\x00\x00\x00"
        tail = blob + z64 + b"PK\x05\x06" + struct.pack("<IHHHHIIH", 0x06054b50,
                                                        0, 0, 0xFFFF, 0xFFFF,
                                                        0xFFFFFFFF, 0xFFFFFFFF, 0)
        cd = rf.parse_central_directory(tail, 10 ** 6)
        self.assertIn("name", cd)
        self.assertEqual(cd["name"].local_header_offset, 40)

    def test_zip64_extra_field_scan(self):
        # extra list: UT (0x5554), ux (0x7578), then zip64 (0x0001) — the real
        # Zenodo layout; the parser must scan, not assume extra[:2].
        us, cs, lho = 12, 20, 0x1122334455
        ut = struct.pack("<HH", 0x5554, 5) + b"\x03" + b"\x00" * 4
        ux = struct.pack("<HH", 0x7578, 11) + b"\x01" + b"\x00" * 8 + b"\x00" * 2
        z64 = struct.pack("<HH", 1, 24) + struct.pack("<QQQ", us, cs, lho)
        extra = ut + ux + z64
        rec = struct.pack(rf._CD_FMT, 0x02014b50, 20, 20, 0, 0, 0, 0,
                          0, 0xFFFFFFFF, 0xFFFFFFFF, 2, len(extra), 0, 0, 0,
                          0, 0xFFFFFFFF) + b"ab" + extra
        blob = rec + b"\x00" * 8
        tail = blob + b"PK\x05\x06" + struct.pack("<IHHHHIIH", 0x06054b50,
                                                  0, 0, 1, 1, len(rec), 10 ** 6 - 0, 0)
        # cdofs must equal the blob's file offset: archive_size - len(tail)
        tail = blob + b"PK\x05\x06" + struct.pack("<IHHHHIIH", 0x06054b50,
                                                  0, 0, 1, 1, len(rec),
                                                  10 ** 6 - len(tail), 0)
        cd = rf.parse_central_directory(tail, 10 ** 6)
        m = cd["ab"]
        self.assertEqual((m.uncompressed_size, m.compressed_size, m.local_header_offset),
                         (us, cs, lho))

    def test_zip64_extra_unresolvable_rejected(self):
        extra = struct.pack("<HH", 0x5554, 0)  # only a non-zip64 extra
        rec = struct.pack(rf._CD_FMT, 0x02014b50, 20, 20, 0, 0, 0, 0,
                          0, 0xFFFFFFFF, 0xFFFFFFFF, 2, len(extra), 0, 0, 0,
                          0, 0xFFFFFFFF) + b"ab" + extra
        blob = rec + b"\x00" * 8
        tail = blob + b"PK\x05\x06" + struct.pack("<IHHHHIIH", 0x06054b50,
                                                  0, 0, 1, 1, len(rec),
                                                  10 ** 6 - (len(blob) + 26), 0)
        with self.assertRaises(rf.RangeFetchError):
            rf.parse_central_directory(tail, 10 ** 6)


class PlanAndPartTests(unittest.TestCase):
    def test_plan_groups_and_budget(self):
        members = {"a": rf.Member("a", 0, 100, 200, 8, 1000),
                   "b": rf.Member("b", 0, 100, 200, 8, 1105),
                   "c": rf.Member("c", 0, 100, 200, 8, 9000)}
        plan = rf.plan_requests(members, ["a", "b", "c"], max_ranges=6,
                                max_bytes=10_000)
        # a+b spans are adjacent-ish (1000..1205) -> one block; c separate
        self.assertLessEqual(len(plan.groups), 2)
        self.assertEqual(plan.bytes_promised, sum(b - a + 1 for g in plan.groups
                                                  for a, b in g))
        self.assertGreater(plan.bytes_promised, 0)

    def test_plan_unknown_member_rejected(self):
        members = {"a": rf.Member("a", 0, 1, 1, 0, 0)}
        with self.assertRaises(rf.RangeFetchError):
            rf.plan_requests(members, ["a", "missing"])

    def test_dir_entries_skipped(self):
        members = {"d/": rf.Member("d/", 0, 0, 0, 0, 0),
                   "d/f": rf.Member("d/f", 0, 1, 1, 0, 50)}
        plan = rf.plan_requests(members, ["d/", "d/f"])
        self.assertEqual(len(plan.groups), 1)

    def test_multipart_parse_and_validation(self):
        body = (b"--EOSMULTIPARTBOUNDARY\nContent-Range: bytes 10-13/T\n\nABCD"
                b"\n--EOSMULTIPARTBOUNDARY\nContent-Range: bytes 20-24/T\n\nXYZ"
                b"\n--EOSMULTIPARTBOUNDARY--\n")
        parts = rf.parse_multipart_byteranges(body, b"EOSMULTIPARTBOUNDARY")
        self.assertEqual(parts[10], b"ABCD")
        self.assertNotIn(20, parts)  # short payload dropped -> will be re-fetched


class ExtractTests(unittest.TestCase):
    def test_extract_members_crc_and_manifest(self):
        import tempfile, json
        from pathlib import Path
        data = b"member payload " * 10
        blob = build_zip_bytes({"dir/f.txt": data})
        cd = rf.parse_central_directory(blob, len(blob))
        m = cd["dir/f.txt"]
        # single block covering the whole entry
        blocks = {0: blob}
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            man = Path(td) / "m.json"
            res = rf.extract_members(cd, ["dir/f.txt"], blocks, out, man)
            self.assertEqual(len(res), 1)
            self.assertTrue(res[0]["crc32_ok"])
            self.assertEqual(res[0]["size"], len(data))
            saved = json.loads(man.read_text())["dir/f.txt"]
            import hashlib
            self.assertEqual(saved["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual((out / "dir__f.txt").read_bytes(), data)
            # second run is a no-op (already in manifest)
            self.assertEqual(rf.extract_members(cd, ["dir/f.txt"], blocks, out, man), [])

    def test_extract_oversize_member_rejected(self):
        import tempfile
        from pathlib import Path as P
        blob = build_zip_bytes({"big": b"x" * 64})
        cd = rf.parse_central_directory(blob, len(blob))
        cd["big"].uncompressed_size = rf.MAX_ENTRY_UNCOMPRESSED + 1
        with tempfile.TemporaryDirectory() as td:
            # R2.1 correction: the cap fires BEFORE the local-header cross-check
            # (guard moved to the top of the member loop, zip-bomb window closed);
            # pin the reason so this control cannot pass for a different error.
            with self.assertRaisesRegex(rf.RangeFetchError, "safety cap"):
                rf.extract_members(cd, ["big"], {0: blob}, P(td), P(td) / "m.json")

    def test_extract_crc_mismatch_rejected(self):
        import tempfile
        from pathlib import Path
        blob = build_zip_bytes({"f": b"data"})
        cd = rf.parse_central_directory(blob, len(blob))
        cd["f"].crc32 ^= 0xFFFF
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(rf.RangeFetchError):
                rf.extract_members(cd, ["f"], {0: blob}, Path(td), Path(td) / "m.json")


if __name__ == "__main__":
    unittest.main()
