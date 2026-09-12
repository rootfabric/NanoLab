"""Digest helpers (stdlib-only) for digest-gated handling of external files.

Used for download-on-run verification (owner decision G1 = B): no durable
cache is allowed; every external file must be verified against preregistered
digests before use.
"""
from __future__ import annotations

import hashlib


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(data: bytes) -> str:
    """Git blob object SHA-1 of raw bytes (used by GitHub source pins)."""
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def verify_file_sha256(path, expected: str) -> dict:
    actual = sha256_file(path)
    return {"path": str(path), "expected": expected, "actual": actual, "match": actual == expected}
