"""Bounded remote-ZIP central-directory probe for pinned Zenodo archives (S17 R2).

WO-PREP-S17-R2 stage A. The S17 simulation-data record (Zenodo 8248808) is a set
of multi-GB archives; this tool recovers the *small* missing inputs
(topologies, index files, force files) without bulk download by

  1. parsing a local byte **window** of the archive tail (EOCD / ZIP64 EOCD +
     central directory) that the operator previously fetched with a HTTP Range
     request, and
  2. optionally (`--fetch`, explicit opt-in only) extracting individual entries
     over additional bounded Range requests with CRC-32 verification.

Fail-closed by design: entry names must not escape the output directory, entry
sizes are capped (zip-bomb guard), the cumulative transfer is capped (budget
guard), and every verification failure aborts with a non-zero exit status
instead of writing the file. Offline by default: without ``--fetch`` the tool
only parses local bytes and never opens a network connection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from dataclasses import dataclass, field
from pathlib import Path

# Guards (fail-closed constants; a run may only lower them, never raise).
MAX_ENTRY_UNCOMPRESSED = 8 * 1024 * 1024
MAX_ENTRIES = 100_000
MAX_NAME_LEN = 1024

_EOCD_SIG = b"PK\x05\x06"
_CEN_SIG = b"PK\x01\x02"
_LOC_SIG = b"PK\x03\x04"
_EOCD64_SIG = b"PK\x06\x06"
_EOCD64_LOC_SIG = b"PK\x06\x07"


class ZipProbeError(Exception):
    """Raised on any fail-closed condition of the probe."""


@dataclass
class ZipEntry:
    name: str
    compressed_size: int
    uncompressed_size: int
    crc32: int
    method: int
    local_header_offset: int

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class CentralDirectory:
    archive_total_size: int
    window_offset: int  # archive offset of window[0]
    entries: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "archive_total_size": self.archive_total_size,
            "window_offset": self.window_offset,
            "entry_count": len(self.entries),
            "entries": [e.as_dict() for e in self.entries],
        }


def parse_eocd(window: bytes, archive_total_size: int) -> tuple[int, int, int]:
    """Return (entries_total, cd_size, cd_offset) from EOCD or ZIP64 EOCD."""
    window_offset = archive_total_size - len(window)
    if window_offset < 0:
        raise ZipProbeError("window is larger than the declared archive size")
    i = window.rfind(_EOCD_SIG)
    if i < 0:
        raise ZipProbeError("EOCD signature not found in the provided window")
    if len(window) - i < 22:
        raise ZipProbeError("EOCD record truncated")
    (_sig, _disk, _cd_disk, _n_disk, entries_total, cd_size, cd_offset, _clen) = struct.unpack(
        "<IHHHHIIH", window[i:i + 22]
    )
    # ZIP64: a 0xFFFFFFFF marker means the real values live in the ZIP64 EOCD.
    if 0xFFFFFFFF in (entries_total, cd_size, cd_offset) or entries_total == 0xFFFF or cd_size == 0xFFFF:
        j = window.rfind(_EOCD64_SIG)
        if j < 0:
            raise ZipProbeError("ZIP64 markers present but ZIP64 EOCD record missing")
        if len(window) - j < 56:
            raise ZipProbeError("ZIP64 EOCD record truncated")
        (_sig64, _sz, _vmade, _vneed, _d1, _d2, _ed, e_total, e_cdsize, e_cdofs) = struct.unpack(
            "<IQHHIIQQQQ", window[j:j + 56]
        )
        entries_total, cd_size, cd_offset = e_total, e_cdsize, e_cdofs
    if cd_offset < window_offset:
        raise ZipProbeError("central directory starts before the fetched window")
    if cd_offset + cd_size > archive_total_size:
        raise ZipProbeError("central directory outside the declared archive bounds")
    if cd_size > len(window):
        raise ZipProbeError(
            f"central directory ({cd_size} B) is larger than the provided window ({len(window)} B); "
            "fetch a larger tail window"
        )
    return entries_total, cd_size, cd_offset


def parse_central_directory(window: bytes, archive_total_size: int, max_entries: int = MAX_ENTRIES) -> CentralDirectory:
    """Deterministically parse the central directory out of a tail window."""
    entries_total, cd_size, cd_offset = parse_eocd(window, archive_total_size)
    window_offset = archive_total_size - len(window)
    pos = cd_offset - window_offset
    cd = CentralDirectory(archive_total_size=archive_total_size, window_offset=window_offset)
    seen = 0
    while window[pos:pos + 4] == _CEN_SIG:
        if len(window) - pos < 46:
            raise ZipProbeError("central directory record truncated")
        (_sig, _vm, _vn, _fl, _mt, _md, _di, crc, csize, usize, nlen, elen, clen,
         _ds, _ia, _ea, lho) = struct.unpack("<IHHHHHHIIIHHHHHII", window[pos:pos + 46])
        if nlen > MAX_NAME_LEN:
            raise ZipProbeError(f"entry name exceeds {MAX_NAME_LEN} bytes")
        name_bytes = window[pos + 46:pos + 46 + nlen]
        if len(name_bytes) != nlen:
            raise ZipProbeError("entry name truncated")
        name = name_bytes.decode("utf-8")
        if usize == 0xFFFFFFFF or csize == 0xFFFFFFFF or lho == 0xFFFFFFFF:
            # ZIP64 extra field parse (header id 0x0001), bounded by elen.
            extra = window[pos + 46 + nlen:pos + 46 + nlen + elen]
            vals_needed = [f for f, v in (("u", usize), ("c", csize), ("o", lho)) if v == 0xFFFFFFFF]
            xoff = 0
            parsed: dict[str, int] = {}
            while xoff + 4 <= len(extra):
                hid, hsz = struct.unpack("<HH", extra[xoff:xoff + 4])
                if hid == 1:
                    body = extra[xoff + 4:xoff + 4 + hsz]
                    for k, which in enumerate(vals_needed):
                        if len(body) < 8 * (k + 1):
                            raise ZipProbeError("ZIP64 extra field truncated")
                        parsed[which] = struct.unpack("<Q", body[8 * k:8 * k + 8])[0]
                    break
                xoff += 4 + hsz
            if set(vals_needed) - set(parsed):
                raise ZipProbeError("ZIP64 sizes/offset not resolvable from extra field")
            usize = parsed.get("u", usize)
            csize = parsed.get("c", csize)
            lho = parsed.get("o", lho)
        if any(v < 0 for v in (csize, usize, lho)):
            raise ZipProbeError("negative size/offset in central directory")
        cd.entries.append(ZipEntry(name=name, compressed_size=csize, uncompressed_size=usize,
                                   crc32=crc, method=_mt, local_header_offset=lho))
        seen += 1
        if seen > max_entries:
            raise ZipProbeError(f"central directory exceeds the {max_entries}-entry safety cap")
        pos += 46 + nlen + elen + clen
    if seen == 0:
        raise ZipProbeError("no central directory records parsed from the window")
    if entries_total != seen:
        raise ZipProbeError(f"EOCD declares {entries_total} entries but {seen} records parsed")
    return cd


def safe_target_name(entry_name: str, out_root: Path) -> Path:
    """Map an archive entry name to a contained, non-clobbering output path."""
    if not entry_name or entry_name.endswith("/"):
        raise ZipProbeError(f"directory entries are not extracted: {entry_name!r}")
    if "\\" in entry_name or "\x00" in entry_name:
        raise ZipProbeError(f"entry name contains a forbidden separator: {entry_name!r}")
    candidate = (out_root / entry_name).resolve()
    root = out_root.resolve()
    if not candidate.is_relative_to(root):
        raise ZipProbeError(f"entry name escapes the output root: {entry_name!r}")
    return candidate


def parse_local_entry(window_provider, entry: ZipEntry) -> bytes:
    """Decode one entry via ``window_provider(start, end) -> bytes`` (inclusive).

    Two-phase: the local header may carry its own extra field (e.g. ZIP64
    sizes), so the data offset is only known after reading the 30-byte
    header. Verifies the local-header signature, sizes against the central
    directory, the decompressed length and the CRC-32 (fail-closed).
    """
    name_len = len(entry.name.encode("utf-8"))
    head = window_provider(entry.local_header_offset, entry.local_header_offset + 29)
    if len(head) != 30:
        raise ZipProbeError(f"{entry.name}: range provider returned a short header window")
    if head[:4] != _LOC_SIG:
        raise ZipProbeError(f"{entry.name}: local header signature mismatch")
    (_sig, _v, _f, method, _mt, _md, _crc32_hdr, csize, usize, nlen, elen) = struct.unpack(
        "<IHHHHHIIIHH", head[:30]
    )
    if nlen != name_len or method != entry.method or csize != entry.compressed_size or usize != entry.uncompressed_size:
        raise ZipProbeError(f"{entry.name}: local header disagrees with the central directory")
    if usize > MAX_ENTRY_UNCOMPRESSED:
        raise ZipProbeError(
            f"{entry.name}: uncompressed size {usize} exceeds the {MAX_ENTRY_UNCOMPRESSED}-byte safety cap"
        )
    data_start = entry.local_header_offset + 30 + nlen + elen
    data = window_provider(data_start, data_start + entry.compressed_size - 1)
    if len(data) != entry.compressed_size:
        raise ZipProbeError(f"{entry.name}: range provider returned a short data window")
    if entry.method == 8:
        data = zlib.decompress(data, -15)
    elif entry.method != 0:
        raise ZipProbeError(f"{entry.name}: unsupported compression method {entry.method}")
    if len(data) != entry.uncompressed_size:
        raise ZipProbeError(f"{entry.name}: decompressed length mismatch")
    if (zlib.crc32(data) & 0xFFFFFFFF) != entry.crc32:
        raise ZipProbeError(f"{entry.name}: CRC-32 mismatch (archive corruption)")
    return data


def build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="S17 bounded remote-ZIP central-directory probe (offline by default)")
    p.add_argument("--window", type=Path, required=True, help="local file with the fetched archive tail window")
    p.add_argument("--archive-size", type=int, required=True, help="total size of the remote archive in bytes")
    p.add_argument("--list", action="store_true", help="print the parsed central directory as JSON")
    p.add_argument("--extract", nargs="*", default=[], help="entry names to extract (requires --fetch)")
    p.add_argument("--out", type=Path, default=None, help="extraction output directory")
    p.add_argument("--url", type=str, default=None, help="archive URL (required with --fetch)")
    p.add_argument("--fetch", action="store_true", help="opt-in: perform bounded network range requests")
    p.add_argument("--max-transfer-bytes", type=int, default=256 * 1024 * 1024, help="cumulative transfer cap")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_cli().parse_args(argv)
    window = args.window.read_bytes()
    cd = parse_central_directory(window, args.archive_size)
    if args.list:
        print(json.dumps(cd.as_dict(), indent=1))
    if args.extract:
        if not (args.fetch and args.url and args.out):
            print("extraction requires --fetch, --url and --out (explicit opt-in)", file=sys.stderr)
            return 2
        # Local import keeps the default path offline-clean (no network imports).
        import subprocess

        index = {e.name: e for e in cd.entries}
        out_root = args.out
        out_root.mkdir(parents=True, exist_ok=True)
        manifest_path = out_root / "_extracted.json"
        manifest: dict = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        spent = 0
        for name in args.extract:
            if name not in index:
                print(f"FAIL {name}: not present in the central directory", file=sys.stderr)
                return 2
            entry = index[name]
            if entry.uncompressed_size > MAX_ENTRY_UNCOMPRESSED:
                print(f"FAIL {name}: entry exceeds the safety cap", file=sys.stderr)
                return 2
            target = safe_target_name(name, out_root)
            need = 30 + len(name.encode("utf-8")) + entry.compressed_size
            if spent + need > args.max_transfer_bytes:
                print(f"FAIL {name}: extraction would exceed the {args.max_transfer_bytes}-byte budget", file=sys.stderr)
                return 2
            range_target = out_root / f".range_{abs(hash(name)) % 99991}.bin"

            def provider(start: int, end: int, _name=name, _rt=range_target) -> bytes:
                nonlocal spent
                want = end - start + 1
                for attempt in range(6):
                    proc = subprocess.run(
                        ["curl", "-s", "--max-time", "420", "-r", f"{start}-{end}", "-o", str(_rt), args.url],
                        capture_output=True,
                    )
                    if proc.returncode == 0 and _rt.exists() and _rt.stat().st_size == want:
                        spent += want
                        return _rt.read_bytes()
                raise ZipProbeError(f"{_name}: range fetch failed after retries")

            data = parse_local_entry(provider, entry)
            target.write_bytes(data)
            manifest[name] = {
                "sha256": hashlib.sha256(data).hexdigest(),
                "size": len(data),
                "crc32_ok": True,
            }
            manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
            print(f"OK {name} {len(data)} B sha256={manifest[name]['sha256'][:16]}...")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ZipProbeError as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr)
        sys.exit(3)
