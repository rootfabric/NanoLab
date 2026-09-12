"""Shared helpers for EX-NL3-002-R1 records: timestamping and canonical file writes."""
import datetime
import json
import os
import sys

REPO = r"C:\NanoLab\nl3-002-confirm"
EX = os.path.join(REPO, "docs", "work", "executions", "EX-NL3-002-R1")
sys.path.insert(0, os.path.join(REPO, "scripts"))
from e2.canonical import canonical_json  # noqa: E402


def now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_canonical(relpath: str, obj) -> str:
    path = os.path.join(EX, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as h:
        h.write(canonical_json(obj) if not isinstance(obj, str) else obj)
        h.write("\n")
    return path


def write_text(relpath: str, text: str) -> str:
    path = os.path.join(EX, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as h:
        h.write(text)
    return path


def read(relpath: str) -> str:
    with open(os.path.join(EX, relpath), "r", encoding="utf-8", newline="") as h:
        return h.read()


def stamp(relpath: str) -> None:
    """Replace \"TS\"/TIMESTAMP placeholders with the current UTC timestamp."""
    p = os.path.join(EX, relpath)
    text = open(p, "r", encoding="utf-8", newline="").read()
    ts = now_utc()
    text = text.replace('"TS"', '"' + ts + '"').replace("TIMESTAMP", ts)
    with open(p, "w", encoding="utf-8", newline="\n") as h:
        h.write(text)


if __name__ == "__main__":
    for rel in sys.argv[1:]:
        stamp(rel)
        print("stamped", rel, now_utc())
