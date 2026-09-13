"""Minimal JSON Schema (draft 2020-12 subset) executor, stdlib-only.

Purpose: execute the normative NanoLab release schemas
(``schemas/components/component-card.v1.json``,
``schemas/release/rights.v1.json``,
``schemas/release/release-manifest.v1.json``) without third-party
dependencies. Hosted CI runs the unittest gate on a bare Python
installation, so ``jsonschema`` and similar packages are not available
there and MUST NOT be imported by release tooling.

Supported keywords (subset):
    $schema, $id, title, description, default, examples   (annotations, no-op)
    type, const, enum, pattern, minLength, minItems, maxItems,
    minimum, maximum, items, properties, required,
    additionalProperties, allOf

Anything else found in a schema is a HARD ERROR (fail-closed), never
silently ignored: an unenforced constraint must not look enforced.

Not supported (and therefore forbidden in our schemas): if/then/else,
oneOf/anyOf/not, $ref, $defs, dependencies/dependentRequired,
patternProperties, propertyNames, contains, uniqueItems, multipleOf,
minProperties/maxProperties, exclusive*/format. Cross-field rules that
cannot be expressed in this subset are enforced as explicit semantic
checks in :mod:`release.card_lint` and documented in
``docs/release/RELEASE_CONTRACT_V0_1.md``.
"""

from __future__ import annotations

import re
from typing import Any

NO_OP_KEYWORDS = frozenset({"$schema", "$id", "$comment", "title", "description", "default", "examples"})
SUPPORTED_KEYWORDS = frozenset(
    {
        "type",
        "const",
        "enum",
        "pattern",
        "minLength",
        "minItems",
        "maxItems",
        "minimum",
        "maximum",
        "items",
        "properties",
        "required",
        "additionalProperties",
        "allOf",
    }
)


class SchemaError(Exception):
    """Raised when a schema uses a keyword this executor does not support."""


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _json_equal(left: Any, right: Any) -> bool:
    """JSON equality with a bool/int guard (True != 1, False != 0)."""
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(_json_equal(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_json_equal(a, b) for a, b in zip(left, right))
    return left == right


def _check_type(instance: Any, expected: Any, path: str, errors: list[str]) -> None:
    names = [expected] if isinstance(expected, str) else list(expected)
    for name in names:
        if name == "object" and isinstance(instance, dict):
            return
        if name == "array" and isinstance(instance, list):
            return
        if name == "string" and isinstance(instance, str):
            return
        if name == "boolean" and isinstance(instance, bool):
            return
        if name == "integer" and isinstance(instance, int) and not isinstance(instance, bool):
            return
        if name == "number" and _is_number(instance):
            return
        if name == "null" and instance is None:
            return
    errors.append(f"{path}: expected type {'/'.join(names)}, got {type(instance).__name__}")


def _validate_schema(instance: Any, schema: Any, path: str, errors: list[str]) -> None:
    if not isinstance(schema, dict):
        if schema is True or schema is False:
            if schema is False:
                errors.append(f"{path}: schema forbids any value (false)")
            return
        raise SchemaError(f"{path}: schema must be an object or boolean, got {type(schema).__name__}")

    unknown = sorted(set(schema) - SUPPORTED_KEYWORDS - NO_OP_KEYWORDS)
    if unknown:
        raise SchemaError(
            f"{path}: unsupported schema keyword(s) {unknown}; this executor is fail-closed, "
            "extend release.mini_schema explicitly if the keyword is genuinely needed"
        )

    if "type" in schema:
        _check_type(instance, schema["type"], path, errors)

    if "const" in schema and not _json_equal(instance, schema["const"]):
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema:
        if not any(_json_equal(instance, option) for option in schema["enum"]):
            errors.append(f"{path}: value {instance!r} not in enum {schema['enum']!r}")

    if isinstance(instance, str):
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: string {instance!r} does not match pattern {schema['pattern']!r}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength={schema['minLength']}")
    elif "pattern" in schema or "minLength" in schema:
        # String-only keywords are no-ops for non-strings by spec; a type
        # mismatch (if any) has already been recorded above.
        pass

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: array shorter than minItems={schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: array longer than maxItems={schema['maxItems']}")
        if "items" in schema:
            for index, element in enumerate(instance):
                _validate_schema(element, schema["items"], f"{path}[{index}]", errors)

    if _is_number(instance):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: value {instance} below minimum={schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: value {instance} above maximum={schema['maximum']}")

    if isinstance(instance, dict):
        if "required" in schema:
            for key in schema["required"]:
                if key not in instance:
                    errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if key in instance:
                _validate_schema(instance[key], subschema, f"{path}.{key}", errors)
        if "additionalProperties" in schema:
            extra = set(instance) - set(properties)
            extra_rule = schema["additionalProperties"]
            if extra_rule is False:
                if extra:
                    errors.append(f"{path}: unexpected additional property/ies {sorted(extra)!r}")
            else:
                for key in sorted(extra):
                    _validate_schema(instance[key], extra_rule, f"{path}.{key}", errors)

    if "allOf" in schema:
        for subschema in schema["allOf"]:
            _validate_schema(instance, subschema, path, errors)


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate ``instance`` against ``schema``; return a list of error strings."""
    errors: list[str] = []
    _validate_schema(instance, schema, path, errors)
    return errors


def lint_schema(schema: Any, path: str = "$") -> list[str]:
    """Check a schema document itself (fail-closed keyword scan, no instance).

    Walks the full schema tree regardless of any instance shape, so
    unsupported keywords are caught even in branches a given document
    would not reach. Run this before :func:`validate`.
    """
    errors: list[str] = []

    def walk(node: Any, where: str) -> None:
        if node is True or node is False:
            return
        if not isinstance(node, dict):
            errors.append(f"{where}: schema must be an object or boolean, got {type(node).__name__}")
            return
        unknown = sorted(set(node) - SUPPORTED_KEYWORDS - NO_OP_KEYWORDS)
        if unknown:
            errors.append(
                f"{where}: unsupported schema keyword(s) {unknown}; this executor is fail-closed, "
                "extend release.mini_schema explicitly if the keyword is genuinely needed"
            )
        for key in ("items", "additionalProperties"):
            if isinstance(node.get(key), dict):
                walk(node[key], f"{where}.{key}")
        for key, subschema in (node.get("properties") or {}).items():
            walk(subschema, f"{where}.properties.{key}")
        for index, subschema in enumerate(node.get("allOf") or []):
            walk(subschema, f"{where}.allOf[{index}]")

    walk(schema, path)
    return errors
