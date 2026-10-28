"""Compare immutable Git subjects; never manufacture an independent verdict."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

PUBLICATION = re.compile(r"docs/work/executions/EX-[^/]+/(?:summary\.md|review/.+\.md|events/[0-9]{4}-[a-z0-9-]+\.json)$")


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout


def resolve(root, ref):
    sha = git(root, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("invalid commit subject")
    return sha


def tree_digest(root, sha, excluded):
    rows = []
    for row in git(root, "ls-tree", "-r", "-z", sha).split(b"\0"):
        if row and row.split(b"\t", 1)[1].decode() not in excluded:
            rows.append(row)
    return hashlib.sha256(b"\0".join(sorted(rows))).hexdigest()


def compare(root: Path, base: str, head: str, publication_paths=()) -> dict:
    base, head = resolve(root, base), resolve(root, head)
    allowed = set(publication_paths)
    if len(allowed) != len(publication_paths):
        raise ValueError("duplicate publication paths")
    for path in allowed:
        if not PUBLICATION.fullmatch(path) or any(part in {".", ".."} for part in path.split("/")):
            raise ValueError("publication exclusion is not an explicit administrative file: " + path)
    fields = git(root, "diff", "--no-renames", "--name-status", "-z", base, head).decode().split("\0")
    fields = fields[:-1] if fields[-1] == "" else fields
    changes = [{"status": fields[i], "path": fields[i+1]} for i in range(0, len(fields), 2)]
    actual = {c["path"] for c in changes}
    if allowed - actual:
        raise ValueError("publication paths must be changed files, not broad exclusions")
    publication_only = bool(changes) and all(c["path"] in allowed and c["status"] in {"A", "M"} and
        ("/events/" not in c["path"] or c["status"] == "A") for c in changes)
    for path in allowed:
        entry = git(root, "ls-tree", "-z", head, "--", path)
        if not entry.startswith(b"100644 blob "):
            publication_only = False  # symlinks/executable files are not report-only
    before, after = tree_digest(root, base, allowed), tree_digest(root, head, allowed)
    equivalent = before == after and (publication_only or not changes)
    return {"ok": True, "base": base, "head": head,
            "base_tree": git(root, "rev-parse", base + "^{tree}").decode().strip(),
            "head_tree": git(root, "rev-parse", head + "^{tree}").decode().strip(),
            "changed_paths": changes, "publication_paths": sorted(allowed),
            "base_subject_digest": before, "head_subject_digest": after,
            "subject_equivalent": equivalent,
            "classification": "UNCHANGED" if not changes else "PUBLICATION_ONLY_CANDIDATE" if equivalent else "FULL_REVIEW",
            "required_action": "Independent delta review and reference existing valid subject evidence" if equivalent else "Review affected product/inputs and rerun applicable tests",
            "previous_verdict_reusable_without_review": False,
            "merge_authorized": False, "scientific_acceptance": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--base", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--publication-path", action="append", default=[])
    a = p.parse_args()
    try:
        result = compare(Path(a.root).resolve(), a.base, a.head, a.publication_path)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        result = {"ok": False, "errors": [str(exc)], "classification": "FULL_REVIEW"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
