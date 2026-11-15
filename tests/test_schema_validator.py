"""Phase 0/1 — the vendored JSON Schema subset validator behaves correctly."""

import pytest

from lrtp.schema import SchemaError, validate

OBJ_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["a", "b"],
    "properties": {
        "a": {"type": "string", "enum": ["x", "y"]},
        "b": {"type": "integer"},
        "c": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    },
}


def test_valid_object_passes():
    validate({"a": "x", "b": 3, "c": ["one"]}, OBJ_SCHEMA)


def test_missing_required_fails():
    with pytest.raises(SchemaError) as e:
        validate({"a": "x"}, OBJ_SCHEMA)
    assert "missing required property 'b'" in str(e.value)


def test_bad_enum_fails():
    with pytest.raises(SchemaError):
        validate({"a": "z", "b": 1}, OBJ_SCHEMA)


def test_wrong_type_fails():
    with pytest.raises(SchemaError):
        validate({"a": "x", "b": "not-int"}, OBJ_SCHEMA)


def test_bool_is_not_integer():
    with pytest.raises(SchemaError):
        validate({"a": "x", "b": True}, OBJ_SCHEMA)


def test_additional_property_rejected():
    with pytest.raises(SchemaError):
        validate({"a": "x", "b": 1, "extra": 1}, OBJ_SCHEMA)


def test_min_items_enforced():
    with pytest.raises(SchemaError):
        validate({"a": "x", "b": 1, "c": []}, OBJ_SCHEMA)


def test_pattern_properties_and_min_properties():
    schema = {
        "type": "object",
        "minProperties": 1,
        "additionalProperties": False,
        "patternProperties": {"^(vulnerable|defended)$": {"type": "string"}},
    }
    validate({"vulnerable": "success"}, schema)
    with pytest.raises(SchemaError):
        validate({}, schema)
    with pytest.raises(SchemaError):
        validate({"unknown": "success"}, schema)
