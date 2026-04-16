"""Tests for envault/env_schema.py"""

import json
import os
import pytest

from envault.env_schema import (
    SCHEMA_FILENAME,
    SchemaError,
    SchemaIssue,
    define_field,
    get_schema,
    remove_field,
    validate_against_schema,
    _schema_path,
)


@pytest.fixture
def schema_dir(tmp_path):
    return str(tmp_path)


def test_schema_filename_constant():
    assert SCHEMA_FILENAME == ".envault-schema.json"


def test_schema_path_returns_correct_path(schema_dir):
    path = _schema_path(schema_dir)
    assert path == os.path.join(schema_dir, SCHEMA_FILENAME)


def test_get_schema_empty_when_no_file(schema_dir):
    assert get_schema(schema_dir) == {}


def test_define_field_creates_schema_file(schema_dir):
    define_field(schema_dir, "DATABASE_URL")
    assert os.path.exists(_schema_path(schema_dir))


def test_define_field_stores_correct_defaults(schema_dir):
    define_field(schema_dir, "DATABASE_URL")
    schema = get_schema(schema_dir)
    assert "DATABASE_URL" in schema
    assert schema["DATABASE_URL"]["type"] == "string"
    assert schema["DATABASE_URL"]["required"] is True
    assert schema["DATABASE_URL"]["default"] is None


def test_define_field_custom_values(schema_dir):
    define_field(schema_dir, "PORT", type_hint="integer", required=False, default="8080", description="App port")
    schema = get_schema(schema_dir)
    assert schema["PORT"]["type"] == "integer"
    assert schema["PORT"]["required"] is False
    assert schema["PORT"]["default"] == "8080"
    assert schema["PORT"]["description"] == "App port"


def test_define_field_invalid_type_raises(schema_dir):
    with pytest.raises(SchemaError, match="Invalid type"):
        define_field(schema_dir, "KEY", type_hint="uuid")


def test_define_field_empty_key_raises(schema_dir):
    with pytest.raises(SchemaError, match="Key must not be empty"):
        define_field(schema_dir, "")


def test_remove_field_success(schema_dir):
    define_field(schema_dir, "FOO")
    remove_field(schema_dir, "FOO")
    assert "FOO" not in get_schema(schema_dir)


def test_remove_field_nonexistent_raises(schema_dir):
    with pytest.raises(SchemaError, match="not found in schema"):
        remove_field(schema_dir, "NONEXISTENT")


def test_validate_no_issues_when_all_present(schema_dir):
    define_field(schema_dir, "DB_HOST")
    define_field(schema_dir, "PORT", type_hint="integer")
    issues = validate_against_schema(schema_dir, {"DB_HOST": "localhost", "PORT": "5432"})
    assert issues == []


def test_validate_missing_required_key(schema_dir):
    define_field(schema_dir, "SECRET_KEY", required=True)
    issues = validate_against_schema(schema_dir, {})
    assert len(issues) == 1
    assert issues[0].key == "SECRET_KEY"
    assert issues[0].severity == "error"


def test_validate_missing_key_with_default_is_warning(schema_dir):
    define_field(schema_dir, "LOG_LEVEL", required=True, default="INFO")
    issues = validate_against_schema(schema_dir, {})
    assert len(issues) == 1
    assert issues[0].severity == "warning"


def test_validate_integer_type_mismatch(schema_dir):
    define_field(schema_dir, "PORT", type_hint="integer")
    issues = validate_against_schema(schema_dir, {"PORT": "not-a-number"})
    assert any(i.key == "PORT" and i.severity == "error" for i in issues)


def test_validate_boolean_valid_values(schema_dir):
    define_field(schema_dir, "DEBUG", type_hint="boolean")
    for val in ["true", "false", "1", "0", "yes", "no"]:
        issues = validate_against_schema(schema_dir, {"DEBUG": val})
        assert issues == [], f"Expected no issues for value '{val}'"


def test_validate_boolean_invalid_value(schema_dir):
    define_field(schema_dir, "DEBUG", type_hint="boolean")
    issues = validate_against_schema(schema_dir, {"DEBUG": "maybe"})
    assert len(issues) == 1
    assert issues[0].severity == "error"


def test_validate_float_type_mismatch(schema_dir):
    define_field(schema_dir, "RATIO", type_hint="float")
    issues = validate_against_schema(schema_dir, {"RATIO": "abc"})
    assert len(issues) == 1
    assert issues[0].key == "RATIO"
