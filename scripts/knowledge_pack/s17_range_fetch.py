#!/usr/bin/env python3
"""S17 bounded multi-range remote-ZIP member fetcher (R2 recovery evidence).

Companion to :mod:`s17_zip_probe`. The probe answers "what is in the archive"
from a small tail window; this module answers "fetch these members, cheaply":
it groups member byte-spans into a few multi-range HTTP requests (the server
returns multipart/byteranges 1:1), tolerates a server that stalls between body
end and connection close (bounded max-time + full-response parsing), and
verifies every member against its central-directory CRC-32 (fail-closed).

Network access only happens in ``iter_member_blobs`` via the injected
``http_fetch(url, range_header) -> bytes`` callable; every other function is
pure and offline-testable.

Transfer accounting: each successful range contributes exactly
``end - start + 1`` bytes; the caller sums ``bytes_promised`` for the budget.
"""

from __future__ import annotations

import hashlib
import json
import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path

_LOC_SIG = b"PK\x03\x04"
_EOCD_SIG = b"PK\x05\x06"
_ZIP64_EOCD_SIG = b"PK\x06\x06"
_CD_SIG = b"PK\x01\x02"
_EOCD_FMT = "<IHHHHIIH"
_ZIP64_EOCD_FMT = "<IQHHIIQQQQ"
_CD_FMT = "<IHHHHHHIIIHHHHHII"
_LOC_FMT = "<IHHHHHIIIHH"
MAX_ENTRY_UNCOMPRESSED = 64 * 1024 * 1024


class RangeFetchError(Exception):
    """Raised on any fail-closed condition (bad format, CRC, truncated part)."""


@dataclass
class Member:
    """One central-directory record with ZIP64-resolved sizes/offset."""

    name: str
    crc32: int
    compressed_size: int
    uncompressed_size: int
    method: int
    local_header_offset: int

    def span_for_local_read(self, extra_guess: int = 96) -> tuple[int, int]:
        """Byte span covering local header + name + extra guess + data."""
        nlen = len(self.name.encode("utf-8"))
        start = self.local_header_offset
        end = start + 30 + nlen + extra_guess + self.compressed_size - 1
        return start, end


@dataclass
class TransferPlan:
    """Groups of ranges to request, for budgeting before any I/O."""

    groups: list[list[tuple[int, int]]] = field(default_factory=list)

    @property
    def bytes_promised(self) -> int:
        return sum(b - a + 1 for g in self.groups for (a, b) in g)


def parse_central_directory(tail: bytes, archive_size: int) -> dict[str, Member]:
    """Parse the CD from a fetched tail window; resolve ZIP64 sizes/offsets.

    Fail-closed on: truncated tail, missing EOCD, CD not fully inside the
    window, entries with unresolvable 0xFFFFFFFF markers.
    """
    fs = archive_size - len(tail)
    if fs < 0:
        raise RangeFetchError("archive_size smaller than the tail window")
    i = tail.rfind(_EOCD_SIG)
    if i == -1:
        raise RangeFetchError("EOCD signature not found in tail window")
    (_, _, _, _, ntotal, cdsize, cdofs, _) = struct.unpack(_EOCD_FMT, tail[i:i + 22])
    j = tail.rfind(_ZIP64_EOCD_SIG)
    if 0xFFFFFFFF in (cdofs, cdsize) or ntotal == 0xFFFF or j != -1:
        if j == -1 or len(tail) < j + 56:
            raise RangeFetchError("ZIP64 markers present but ZIP64 EOCD record missing/truncated")
        (_, _, _, _, _, _, _, ntotal64, cdsize64, cdofs64) = struct.unpack(
            _ZIP64_EOCD_FMT, tail[j:j + 56])
        cdofs, cdsize, ntotal = cdofs64, cdsize64, ntotal64
    start = cdofs - fs
    if start < 0 or start + cdsize > len(tail):
        raise RangeFetchError(
            f"central directory [{cdofs}, {cdofs + cdsize}) not inside tail window")
    pos = start
    members: dict[str, Member] = {}
    while tail[pos:pos + 4] == _CD_SIG:
        (sig, _vm, _vn, _fl, method, _mt, _md, crc, csize, usize, nlen, elen,
         clen, _dsk, _ia, _ea, lho) = struct.unpack(_CD_FMT, tail[pos:pos + 46])
        name_bytes = tail[pos + 46:pos + 46 + nlen]
        if len(name_bytes) != nlen:
            raise RangeFetchError(f"entry name truncated at CD offset {pos}")
        name = name_bytes.decode("utf-8", "replace")
        extra = tail[pos + 46 + nlen:pos + 46 + nlen + elen]
        need = [k for k, v in (("u", usize), ("c", csize), ("o", lho)) if v == 0xFFFFFFFF]
        if need:
            # ZIP64 extra (header id 0x0001) may sit anywhere in the extra
            # list (e.g. after Info-ZIP UT/ux): scan (id, len) headers.
            fix: dict[str, int] = {}
            xoff = 0
            while xoff + 4 <= len(extra):
                hid, hsz = struct.unpack("<HH", extra[xoff:xoff + 4])
                if hid == 1:
                    body = extra[xoff + 4:xoff + 4 + hsz]
                    if len(body) < 8 * len(need):
                        raise RangeFetchError(f"{name}: ZIP64 extra truncated")
                    vals = struct.unpack("<" + "Q" * len(need), body[:8 * len(need)])
                    fix = dict(zip(need, vals))
                    break
                xoff += 4 + hsz
            if set(need) - set(fix):
                raise RangeFetchError(f"{name}: ZIP64 sizes/offset not resolvable")
            usize = fix.get("u", usize)
            csize = fix.get("c", csize)
            lho = fix.get("o", lho)
        members[name] = Member(name=name, crc32=crc, compressed_size=csize,
                               uncompressed_size=usize, method=method,
                               local_header_offset=lho)
        pos += 46 + nlen + elen + clen
    return members


def plan_requests(members: dict[str, Member], names: list[str],
                  max_ranges: int = 6, max_bytes: int = 1_200_000,
                  extra_guess: int = 96) -> TransferPlan:
    """Group member spans into requests bounded by range count and bytes.

    Non-overlapping member spans are merged into contiguous blocks; blocks
    are then packed into requests. Raises if a member is unknown.
    """
    spans = []
    for n in names:
        m = members.get(n)
        if m is None:
            raise RangeFetchError(f"member not in central directory: {n}")
        if m.name.endswith("/"):
            continue  # directory stub: nothing to fetch
        spans.append((*m.span_for_local_read(extra_guess), n))
    spans.sort()
    blocks: list[list] = []
    for s, e, n in spans:
        if blocks and s <= blocks[-1][1] + 1:
            blocks[-1][1] = max(blocks[-1][1], e)
            blocks[-1][2].append((s, n))
        else:
            blocks.append([s, e, [(s, n)]])
    plan = TransferPlan()
    cur: list[tuple[int, int]] = []
    cur_bytes = 0
    for bs, be, _ in blocks:
        size = be - bs + 1
        if cur and (len(cur) >= max_ranges or cur_bytes + size > max_bytes):
            plan.groups.append(cur)
            cur, cur_bytes = [], 0
        cur.append((bs, be))
        cur_bytes += size
    if cur:
        plan.groups.append(cur)
    return plan


def parse_multipart_byteranges(body: bytes, boundary: bytes) -> dict[int, bytes]:
    """Parse a multipart/byteranges response body into {range_start: data}.

    Validates each part's declared length against its payload; parts with a
    length mismatch are dropped (the caller re-requests them).
    """
    parts: dict[int, bytes] = {}
    for chunk in body.split(b"--" + boundary):
        idx = chunk.find(b"ontent-Range")
        if idx == -1:
            continue
        head, _, payload = chunk.partition(b"\n\n")
        cr = [ln for ln in head.split(b"\n") if b"ontent-Range" in ln][0]
        spec = cr.split(b":", 1)[1].strip()
        a_s, b_s = spec.split()[1].split(b"/")[0].split(b"-")
        a, b = int(a_s), int(b_s)
        if payload.endswith(b"\n"):
            payload = payload[:-1]
        if len(payload) == b - a + 1:
            parts[a] = payload
    return parts


def extract_members(members: dict[str, Member], names: list[str],
                    blocks_data: dict[int, bytes], outdir: Path,
                    manifest_path: Path) -> list[dict]:
    """Slice, inflate, CRC-verify and persist members from fetched blocks.

    ``blocks_data`` maps block start -> raw bytes (from the response parts).
    Writes each member as ``<name with / ->__>`` and appends to the manifest.
    Returns per-member digests; raises on CRC or length mismatch.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    results = []
    for name in names:
        m = members.get(name)
        if m is None or name.endswith("/") or name in manifest:
            continue
        blob, blob_start = None, None
        for a in sorted(blocks_data):
            if a <= m.local_header_offset <= a + len(blocks_data[a]):
                blob, blob_start = blocks_data[a], a
                break
        if blob is None:
            raise RangeFetchError(f"{name}: no fetched block covers its offset")
        off = m.local_header_offset - blob_start
        if off + 30 > len(blob) or blob[off:off + 4] != _LOC_SIG:
            raise RangeFetchError(f"{name}: bad local header at {m.local_header_offset}")
        (_sig, _v, _f, method, _mt, _md, _crc_hdr, csize, usize, nlen, elen) = \
            struct.unpack(_LOC_FMT, blob[off:off + 30])
        if (method, csize, usize, nlen) != (m.method, m.compressed_size,
                                            m.uncompressed_size,
                                            len(m.name.encode("utf-8"))):
            raise RangeFetchError(f"{name}: local header disagrees with central directory")
        data_start = off + 30 + nlen + elen
        data = blob[data_start:data_start + csize]
        if len(data) != csize:
            raise RangeFetchError(f"{name}: truncated data window")
        if method == 8:
            data = zlib.decompress(data, -15)
        elif method != 0:
            raise RangeFetchError(f"{name}: unsupported compression method {method}")
        if len(data) != m.uncompressed_size:
            raise RangeFetchError(f"{name}: decompressed length mismatch")
        if (zlib.crc32(data) & 0xFFFFFFFF) != m.crc32:
            raise RangeFetchError(f"{name}: CRC-32 mismatch")
        safe = name.replace("/", "__")
        (outdir / safe).write_bytes(data)
        manifest[name] = dict(sha256=hashlib.sha256(data).hexdigest(),
                              size=len(data), crc32_ok=True, method=method,
                              usize=m.uncompressed_size)
        manifest_path.write_text(json.dumps(manifest, indent=1))
        results.append(manifest[name])
    return results
