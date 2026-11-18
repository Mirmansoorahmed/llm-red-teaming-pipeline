"""Tiny, dependency-free JSON Schema validator (restricted subset).

The default `oss` profile must run with no third-party packages and no network
(requirements.md C6), so we cannot rely on the `jsonschema` package. This module
validates documents against the committed JSON Schema files using only the
subset of Draft-07 keywords our schemas use:

    type, required, enum, const, properties, additionalProperties,
    items, minItems, patternProperties, pattern, minLength, oneOf, anyOf

It is deliberately small and strict: anything it does not understand is ignored
rather than silently passed, and unknown object keys are rejected when
`additionalProperties` is false. It is NOT a general-purpose validator; it exists
only to check our own schemas.
"""

from __future__ import annotations

import re
from typing import Any

_TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


class SchemaError(ValueError):
    """Raised when a document fails validation against a schema."""


def _type_ok(value: Any, expected: str) -> bool:
    py = _TYPE_MAP[expected]
    if expected == "integer":
        # bool is a subclass of int; do not accept it as an integer.
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return isinstance(value, py)


def _check(value: Any, schema: dict, path: str, errors: list[str]) -> None:
    # type
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(value, tt) for tt in types):
            errors.append(f"{path or '<root>'}: expected type {t}, got {type(value).__name__}")
            return  # further checks are meaningless on a type mismatch

    # const / enum
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")

    # string constraints
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: string does not match pattern {schema['pattern']!r}")

    # oneOf / anyOf
    for key in ("anyOf", "oneOf"):
        if key in schema:
            matches = 0
            for sub in schema[key]:
                local: list[str] = []
                _check(value, sub, path, local)
                if not local:
                    matches += 1
            if key == "anyOf" and matches == 0:
                errors.append(f"{path}: does not match any of {key}")
            if key == "oneOf" and matches != 1:
                errors.append(f"{path}: must match exactly one of {key} (matched {matches})")

    # object
    if isinstance(value, dict) and (schema.get("type") == "object" or "properties" in schema):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path or '<root>'}: missing required property '{req}'")
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            errors.append(f"{path or '<root>'}: fewer than minProperties {schema['minProperties']}")
        props = schema.get("properties", {})
        pattern_props = schema.get("patternProperties", {})
        additional = schema.get("additionalProperties", True)
        for k, v in value.items():
            child = f"{path}.{k}" if path else k
            if k in props:
                _check(v, props[k], child, errors)
                continue
            matched = False
            for pat, subschema in pattern_props.items():
                if re.search(pat, k):
                    _check(v, subschema, child, errors)
                    matched = True
                    break
            if matched:
                continue
            if additional is False:
                errors.append(f"{path or '<root>'}: unexpected property '{k}'")
            elif isinstance(additional, dict):
                _check(v, additional, child, errors)

    # array
    if isinstance(value, list) and (schema.get("type") == "array" or "items" in schema):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: array shorter than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, item in enumerate(value):
                _check(item, item_schema, f"{path}[{i}]", errors)


def validate(document: Any, schema: dict) -> None:
    """Validate ``document`` against ``schema``; raise :class:`SchemaError` on failure."""
    errors: list[str] = []
    _check(document, schema, "", errors)
    if errors:
        raise SchemaError("; ".join(errors))
