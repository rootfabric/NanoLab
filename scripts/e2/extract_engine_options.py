"""Extract the frozen engine option registry from the pinned engine docs.

The registry is generated from ``input_options.md`` of the pinned oxDNA
checkout (engine commit 00dc7fb9...) and committed as
``scripts/e2/engine_options.json`` together with the SHA-256 of the source
document. Re-running the extractor on the same input must produce a
byte-identical registry (determinism is tested).
"""
from __future__ import annotations

import argparse
import hashlib
import re

try:
    from .canonical import canonical_json
except ImportError:  # direct script execution
    from canonical import canonical_json

KEY_LINE = re.compile(r"^\s{0,6}\[?([A-Za-z_][A-Za-z0-9_]*)\s*=")
SECTION_LINE = re.compile(r"^([^=\s][^:]*):\s*$")
HEADER_LINE = re.compile(r"^#+\s*(.+?)\s*#*$")


def extract(text: str) -> dict:
    options = {}
    section = "_root"
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        header = HEADER_LINE.match(line)
        if header and not line.startswith(" "):
            section = header.group(1)
            continue
        plain = SECTION_LINE.match(line)
        if plain and not line.startswith(" ") and "=" not in line:
            section = plain.group(1).strip()
            continue
        key = KEY_LINE.match(line)
        if key:
            name = key.group(1)
            options[name] = {
                "optional": line.lstrip().startswith("["),
                "section": section,
            }
    return options


def build_registry(md_text: str, engine_commit: str, source_name: str) -> dict:
    options = extract(md_text)
    if not options:
        raise ValueError("no options extracted from the source document")
    return {
        "schema_version": 1,
        "kind": "engine_options_registry",
        "engine": "oxDNA",
        "engine_commit": engine_commit,
        "source_file": source_name,
        "source_sha256": hashlib.sha256(md_text.encode("utf-8")).hexdigest(),
        "source_bytes": len(md_text.encode("utf-8")),
        "extraction": {
            "method": "regex-line-scan",
            "key_pattern": KEY_LINE.pattern,
            "note": "keys = '<name> = ...' lines (definition or example usage); optional = wrapped in []; section = nearest free-standing '...:' or markdown heading; keys used by the engine but absent from the documentation are handled by compat_audit.KNOWN_UNDOCUMENTED, not here",
        },
        "option_count": len(options),
        "options": options,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="extract engine option registry")
    parser.add_argument("md_path")
    parser.add_argument("--engine-commit", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    with open(args.md_path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    registry = build_registry(text, args.engine_commit, args.md_path.replace("\\", "/").split("/")[-1])
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json(registry))
    print(f"options extracted: {registry['option_count']} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
