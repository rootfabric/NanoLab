"""Mechanical negative-control lint for GitHub workflows (INFRA1-002).

Encodes the machine-expressible invariants of EXECUTION-BASELINE-R1 §4/§5/§8/§9
as blocking lint rules over `.github/workflows/*.y*ml`:

  NC-1  no self-hosted runner labels (or dynamic label expressions) in runs-on
  NC-2  forbidden trust-boundary triggers (pull_request_target, workflow_run),
        external reusable-workflow calls, triggers reserved for a baseline revision
  NC-4  explicit minimal permissions block; no write grants
  NC-6  every job carries a wall-clock timeout within the declared budget bounds
  NC-7  no secrets references on the hosted route
  NOTE-3  pull_request.types must explicitly include ready_for_review
  pin   external actions pinned to a full commit SHA (baseline §9)

The reference values live in config/infra/validation-gates.v1.json; this module
only implements the checks. YAML is read with a minimal workflow-subset parser
(stdlib-only, no network, no third-party dependencies). Anything the parser
cannot understand is reported as an unparseable workflow (fail closed).

Exit codes: 0 = no violations, 1 = violations found, 2 = environment/config error.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "nanolab.infra_workflow_lint_output.v1"
DEFAULT_CONFIG = "config/infra/validation-gates.v1.json"
WORKFLOW_GLOB_PATTERNS = ("*.yml", "*.yaml")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SECRETS_REFERENCE = re.compile(r"secrets\.[A-Za-z_][A-Za-z0-9_]*")
BLOCK_SCALAR_STYLES = ("|", "|-", "|+", ">", ">-", ">+")
_BLOCK_SCALAR_STYLES = ("|", "|-", "|+", ">", ">-", ">+")
_INT_SCALAR = re.compile(r"^-?\d{1,9}$")
_FLOAT_SCALAR = re.compile(r"^-?\d{1,9}\.\d{1,9}$")


class WorkflowParseError(ValueError):
    """Raised when a workflow file does not fit the supported YAML subset."""


# --------------------------------------------------------------------------
# Minimal YAML-workflow subset parser
# --------------------------------------------------------------------------

def _strip_comment(raw: str) -> str:
    out: list[str] = []
    quote: str | None = None
    for ch in raw:
        if quote is not None:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (not out or out[-1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _split_key(content: str) -> tuple[str, bool, str]:
    quote: str | None = None
    depth = 0
    for i, ch in enumerate(content):
        if quote is not None:
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            continue
        if ch in "[{":
            depth += 1
            continue
        if ch in "]}":
            depth -= 1
            continue
        if ch == ":" and depth == 0:
            rest = content[i + 1:]
            if rest == "" or rest.startswith((" ", "\t")):
                key = content[:i].strip()
                if len(key) >= 2 and key[0] == key[-1] and key[0] in ("'", '"'):
                    key = key[1:-1]
                return key, True, rest.strip()
    return content, False, ""


def _looks_like_key(content: str) -> bool:
    key, sep, _ = _split_key(content)
    return sep and key != ""


def _split_flow_items(text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for ch in text:
        if quote is not None:
            current.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            current.append(ch)
            continue
        if ch in "[{":
            depth += 1
        if ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            items.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    tail = "".join(current).strip()
    if tail:
        items.append(tail)
    return items


def _parse_scalar(text: str) -> Any:
    text = text.strip()
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        return text[1:-1].replace("''", "'")
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1].replace('\\"', '"')
    if text in ("true", "True"):
        return True
    if text in ("false", "False"):
        return False
    if text in ("null", "~", ""):
        return None
    if _INT_SCALAR.fullmatch(text):
        return int(text)
    if _FLOAT_SCALAR.fullmatch(text):
        return float(text)
    return text


def _parse_flow(text: str) -> Any:
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        return [_parse_flow(item) for item in _split_flow_items(text[1:-1]) if item != ""]
    if text.startswith("{") and text.endswith("}"):
        result: dict[str, Any] = {}
        for item in _split_flow_items(text[1:-1]):
            if not item:
                continue
            key, sep, value = _split_key(item)
            if not sep:
                raise WorkflowParseError(f"invalid flow mapping item: {item!r}")
            result[key] = _parse_flow(value)
        return result
    return _parse_scalar(text)


class _Line:
    __slots__ = ("number", "indent", "content")

    def __init__(self, number: int, indent: int, content: str) -> None:
        self.number = number
        self.indent = indent
        self.content = content


def _content_lines(text: str) -> list[_Line]:
    lines: list[_Line] = []
    for number, raw in enumerate(text.splitlines(), 1):
        stripped_comment = _strip_comment(raw)
        if not stripped_comment.strip():
            continue
        if stripped_comment.strip() in ("---", "..."):
            continue
        content = stripped_comment.strip()
        indent = len(stripped_comment) - len(stripped_comment.lstrip(" "))
        if "\t" in stripped_comment[:indent]:
            raise WorkflowParseError(f"tab character in indentation at line {number}")
        lines.append(_Line(number, indent, content))
    return lines


def parse_workflow_yaml(text: str) -> dict[str, Any]:
    lines = _content_lines(text)
    if not lines:
        raise WorkflowParseError("empty workflow document")
    value, idx = _parse_block(lines, 0, lines[0].indent, text)
    if idx != len(lines):
        raise WorkflowParseError(f"unexpected content at line {lines[idx].number}")
    if not isinstance(value, dict):
        raise WorkflowParseError("workflow document must be a mapping")
    return value


def _parse_block(lines: list[_Line], idx: int, indent: int, source: str) -> tuple[Any, int]:
    first = lines[idx].content
    if first == "-" or first.startswith("- "):
        return _parse_sequence(lines, idx, indent, source)
    return _parse_mapping(lines, idx, indent, source)


def _raw_block_scalar(lines: list[_Line], idx: int, key_indent: int, style: str, source: str) -> tuple[str, int]:
    """Consume a verbatim block scalar (run: | scripts are lint-relevant text)."""
    raw_lines = source.splitlines()
    captured: list[tuple[int, str]] = []
    consumed = idx
    while consumed < len(lines) and lines[consumed].indent > key_indent:
        captured.append((lines[consumed].number, raw_lines[lines[consumed].number - 1].rstrip("\r\n")))
        consumed += 1
    indents = [len(text) - len(text.lstrip(" ")) for _, text in captured if text.strip()]
    common = min(indents) if indents else 0
    body = [text[common:] if text.strip() else "" for _, text in captured]
    if style.startswith(">"):
        text = " ".join(token for token in " ".join(body).split(" ") if token != "")
    else:
        text = "\n".join(body)
    if not style.endswith("-") and body:
        text += "\n"
    return text, consumed


def _parse_mapping(lines: list[_Line], idx: int, indent: int, source: str) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while idx < len(lines):
        line = lines[idx]
        if line.indent < indent:
            break
        if line.indent > indent:
            raise WorkflowParseError(f"unexpected indent at line {line.number}")
        if line.content == "-" or line.content.startswith("- "):
            break
        key, sep, inline = _split_key(line.content)
        if not sep:
            raise WorkflowParseError(f"expected 'key:' at line {line.number}")
        idx += 1
        if inline == "":
            if idx < len(lines) and lines[idx].indent > indent:
                result[key], idx = _parse_block(lines, idx, lines[idx].indent, source)
            else:
                result[key] = None
        elif inline in BLOCK_SCALAR_STYLES:
            result[key], idx = _raw_block_scalar(lines, idx, indent, inline, source)
        else:
            result[key] = _parse_flow(inline)
    return result, idx


def _parse_sequence(lines: list[_Line], idx: int, indent: int, source: str) -> tuple[list[Any], int]:
    result: list[Any] = []
    while idx < len(lines):
        line = lines[idx]
        if line.indent != indent or not (line.content == "-" or line.content.startswith("- ")):
            break
        item_text = line.content[1:].strip()
        if item_text == "":
            idx += 1
            if idx < len(lines) and lines[idx].indent > indent:
                value, idx = _parse_block(lines, idx, lines[idx].indent, source)
            else:
                value = None
            result.append(value)
        elif _looks_like_key(item_text):
            lines[idx] = _Line(line.number, indent + 2, item_text)
            value, idx = _parse_mapping(lines, idx, indent + 2, source)
            result.append(value)
        else:
            result.append(_parse_flow(item_text))
            idx += 1
    return result, idx


# --------------------------------------------------------------------------
# Lint rules
# --------------------------------------------------------------------------

def _violation(rule_id: str, negative_control: str, message: str, where: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        "rule_id": rule_id,
        "negative_control": negative_control,
        "blocking": True,
        "message": message,
    }
    if where:
        item["where"] = where
    return item


def _walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _walk_strings(key)
            yield from _walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)


def _runs_on_labels(job: dict[str, Any]) -> list[str] | None:
    value = job.get("runs-on")
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    return None


def _check_permissions(where: str, permissions: Any, policy: dict[str, Any], violations: list[dict[str, Any]]) -> None:
    if isinstance(permissions, str):
        if permissions not in ("read-all", "none"):
            violations.append(_violation("NC4_WRITE_PERMISSION", "NC-4", f"{where}: permissions value {permissions!r} is not a read-only grant", where))
        return
    if not isinstance(permissions, dict):
        violations.append(_violation("NC4_WRITE_PERMISSION", "NC-4", f"{where}: permissions must be a mapping or read-all/none", where))
        return
    forbidden = set(policy.get("forbidden_permission_levels", ["write"]))
    allowed = set(policy.get("allowed_permission_levels", ["read", "none"]))
    for scope, level in permissions.items():
        if not isinstance(level, str):
            violations.append(_violation("NC4_WRITE_PERMISSION", "NC-4", f"{where}: permissions.{scope} has a non-scalar level", where))
        elif level in forbidden:
            violations.append(_violation("NC4_WRITE_PERMISSION", "NC-4", f"{where}: permissions.{scope}: {level} grants are forbidden on this route", where))
        elif level not in allowed and level not in ("read-all",):
            violations.append(_violation("NC4_WRITE_PERMISSION", "NC-4", f"{where}: permissions.{scope}: level {level!r} is outside the allowed set {sorted(allowed)}", where))


def lint_document(doc: dict[str, Any], policy: dict[str, Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    forbidden_labels = {str(label).lower() for label in policy.get("forbidden_runner_labels", [])}
    forbidden_prefixes = tuple(str(prefix).lower() for prefix in policy.get("forbidden_runner_label_prefixes", []))
    forbidden_triggers = set(policy.get("forbidden_triggers", []))
    reserved_triggers = set(policy.get("triggers_forbidden_until_baseline_revision", []))
    timeout_policy = policy.get("job_timeout_minutes", {})
    timeout_required = bool(timeout_policy.get("required", True))
    timeout_min = int(timeout_policy.get("min", 1))
    timeout_max = int(timeout_policy.get("max", 60))

    triggers = doc.get("on")
    if isinstance(triggers, dict):
        for name in triggers:
            if name in forbidden_triggers:
                violations.append(_violation("NC2_FORBIDDEN_TRIGGER", "NC-2/NC-7", f"trigger '{name}' is FORBIDDEN_R1 (baseline section 4) and must not appear in any workflow"))
            elif name in reserved_triggers:
                violations.append(_violation("NC2_TRIGGER_NEEDS_BASELINE_REVISION", "NC-2", f"trigger '{name}' is reserved and forbidden until a new baseline revision activates it"))
        required_types = set(policy.get("pull_request_types_required", ["ready_for_review"]))
        pr = triggers.get("pull_request")
        pr_types: list[str] | None = None
        if isinstance(pr, dict) and isinstance(pr.get("types"), list) and all(isinstance(item, str) for item in pr["types"]):
            pr_types = [str(item) for item in pr["types"]]
        if pr_types is None or not required_types.issubset(set(pr_types)):
            missing = sorted(required_types - set(pr_types or []))
            violations.append(_violation("NOTE3_PR_TYPES_READY_FOR_REVIEW", "NOTE-3", f"pull_request.types must explicitly include {missing or sorted(required_types)}: draft-to-ready transitions must run validation (NOTE-3, DIRECTOR_ACCEPTANCE_R1 INFRA1-001)"))

    jobs = doc.get("jobs")
    if isinstance(jobs, dict):
        for job_id, job in jobs.items():
            if not isinstance(job, dict):
                violations.append(_violation("WORKFLOW_UNPARSEABLE", "NC-1/NC-2", f"job '{job_id}' must be a mapping"))
                continue
            where = f"job '{job_id}'"
            reusable = job.get("uses")
            if isinstance(reusable, str):
                if not reusable.startswith("./"):
                    violations.append(_violation("NC2_EXTERNAL_REUSABLE_WORKFLOW", "NC-2", f"{where}: reusable workflow calls must be local ('./...'); external: {reusable!r}"))
                continue
            steps = job.get("steps")
            has_steps = isinstance(steps, list)
            labels = _runs_on_labels(job)
            if labels is None:
                if has_steps:
                    violations.append(_violation("NC1_RUNS_ON_MISSING", "NC-1", f"{where}: missing runs-on; runner selection must be explicit"))
            else:
                for label in labels:
                    lowered = label.strip().lower()
                    if "${{" in label:
                        violations.append(_violation("NC1_DYNAMIC_RUNS_ON", "NC-1", f"{where}: dynamic runs-on expression {label!r} is forbidden; runner selection must be static and reviewable"))
                    elif lowered in forbidden_labels:
                        violations.append(_violation("NC1_SELF_HOSTED_LABEL", "NC-1", f"{where}: runs-on uses forbidden self-hosted label {label!r} (an untrusted PR route cannot select trusted nodes)"))
                    elif lowered.startswith(forbidden_prefixes):
                        violations.append(_violation("NC1_SELF_HOSTED_LABEL", "NC-1", f"{where}: runs-on uses reserved self-hosted label prefix {label!r}"))
            if timeout_required and has_steps:
                timeout = job.get("timeout-minutes")
                if timeout is None:
                    violations.append(_violation("BUDGET_TIMEOUT_REQUIRED", "NC-6", f"{where}: missing timeout-minutes; unbounded jobs are forbidden (baseline section 6)"))
                elif isinstance(timeout, bool) or not isinstance(timeout, int):
                    violations.append(_violation("BUDGET_TIMEOUT_BOUNDS", "NC-6", f"{where}: timeout-minutes must be an integer"))
                elif not timeout_min <= timeout <= timeout_max:
                    violations.append(_violation("BUDGET_TIMEOUT_BOUNDS", "NC-6", f"{where}: timeout-minutes={timeout} outside declared budget bounds [{timeout_min}, {timeout_max}]"))
            if isinstance(job.get("permissions"), (dict, str)):
                _check_permissions(where, job.get("permissions"), policy, violations)
            if has_steps:
                for step in steps:
                    if not isinstance(step, dict):
                        continue
                    uses = step.get("uses")
                    if not isinstance(uses, str) or uses.startswith("./"):
                        continue
                    if uses.startswith("docker://"):
                        ref = uses.split("@", 1)[1] if "@" in uses else ""
                        if not ref.startswith("sha256:"):
                            violations.append(_violation("PIN_ACTION_FULL_SHA", "supply-chain", f"{where}: docker action {uses!r} must be digest-pinned"))
                    elif "@" in uses:
                        ref = uses.rsplit("@", 1)[1]
                        if not HEX40.fullmatch(ref):
                            violations.append(_violation("PIN_ACTION_FULL_SHA", "supply-chain", f"{where}: action {uses!r} must be pinned to a full 40-hex commit SHA (baseline section 9)"))

    if policy.get("permissions_block_required", True):
        if doc.get("permissions") is None:
            violations.append(_violation("NC4_PERMISSIONS_BLOCK_MISSING", "NC-4", "workflow-level permissions block is required (explicit minimal permissions, baseline section 5)"))
        else:
            _check_permissions("workflow", doc.get("permissions"), policy, violations)

    if not policy.get("secrets_references_allowed", False):
        for text in _walk_strings(doc):
            match = SECRETS_REFERENCE.search(text)
            if match:
                violations.append(_violation("NC7_SECRETS_REFERENCE", "NC-7", f"secrets reference {match.group(0)!r} is forbidden: the hosted route carries no secrets in R1"))
                break
    return violations


def lint_paths(paths: list[Path], policy: dict[str, Any]) -> dict[str, Any]:
    workflows: list[dict[str, Any]] = []
    total = 0
    for path in paths:
        entry: dict[str, Any] = {"path": str(path)}
        try:
            text = path.read_text(encoding="utf-8")
            doc = parse_workflow_yaml(text)
        except (OSError, UnicodeDecodeError, WorkflowParseError) as exc:
            violation = _violation("WORKFLOW_UNPARSEABLE", "NC-1/NC-2", f"workflow does not parse with the supported YAML subset (fail closed): {exc}")
            entry.update(ok=False, violations=[dict(violation, workflow=str(path))])
            total += 1
            workflows.append(entry)
            continue
        violations = [dict(item, workflow=str(path)) for item in lint_document(doc, policy)]
        total += len(violations)
        entry.update(ok=not violations, violations=violations)
        workflows.append(entry)
    return {
        "schema": SCHEMA,
        "ok": total == 0,
        "config_revision": policy.get("revision"),
        "workflows": workflows,
        "summary": {"workflows": len(workflows), "violations": total, "blocking": total},
    }


def discover_workflow_paths(root: Path) -> list[Path]:
    directory = root / ".github" / "workflows"
    found: list[Path] = []
    for pattern in WORKFLOW_GLOB_PATTERNS:
        found.extend(sorted(directory.glob(pattern)))
    return found


def load_policy(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    policy = config.get("workflow_lint")
    if not isinstance(policy, dict):
        raise ValueError(f"{config_path}: missing 'workflow_lint' policy block")
    return dict(policy, revision=config.get("revision"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NanoLab workflow negative-control lint (NC-1..NC-7)")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--config", default=None, help=f"validation gates config (default: <root>/{DEFAULT_CONFIG})")
    parser.add_argument("--workflow", action="append", default=[], help="lint explicit workflow file(s) instead of discovery")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    config_path = Path(args.config) if args.config else root / DEFAULT_CONFIG
    try:
        policy = load_policy(config_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": SCHEMA, "ok": False, "error": f"config error: {exc}"}, indent=2))
        return 2
    if args.workflow:
        paths = [Path(item) for item in args.workflow]
    else:
        paths = discover_workflow_paths(root)
        if not paths:
            print(json.dumps({"schema": SCHEMA, "ok": False, "error": "no workflow files found under .github/workflows (fail closed)"}, indent=2))
            return 2
    report = lint_paths(paths, policy)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
