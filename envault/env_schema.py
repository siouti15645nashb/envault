"""Schema validation for vault variables (type hints, required flags, defaults)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

SCHEMA_FILENAME = ".envault-schema.json"

VALID_TYPES = {"string", "integer", "float", "boolean"}


class SchemaError(Exception):
    """Raised when schema operations fail."""


@dataclass
class SchemaIssue:
    key: str
    message: str
    severity: str = "error"  # "error" or "warning"


def _schema_path(directory: str) -> str:
    return os.path.join(directory, SCHEMA_FILENAME)


def _load_schema(directory: str) -> Dict[str, Any]:
    path = _schema_path(directory)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_schema(directory: str, schema: Dict[str, Any]) -> None:
    path = _schema_path(directory)
    with open(path, "w") as f:
        json.dump(schema, f, indent=2)


def define_field(
    directory: str,
    key: str,
    type_hint: str = "string",
    required: bool = True,
    default: Optional[str] = None,
    description: str = "",
) -> None:
    """Add or update a schema field definition."""
    if type_hint not in VALID_TYPES:
        raise SchemaError(f"Invalid type '{type_hint}'. Must be one of: {sorted(VALID_TYPES)}")
    if not key:
        raise SchemaError("Key must not be empty.")
    schema = _load_schema(directory)
    schema[key] = {
        "type": type_hint,
        "required": required,
        "default": default,
        "description": description,
    }
    _save_schema(directory, schema)


def remove_field(directory: str, key: str) -> None:
    """Remove a field from the schema."""
    schema = _load_schema(directory)
    if key not in schema:
        raise SchemaError(f"Key '{key}' not found in schema.")
    del schema[key]
    _save_schema(directory, schema)


def get_schema(directory: str) -> Dict[str, Any]:
    """Return the full schema dict."""
    return _load_schema(directory)


def validate_against_schema(directory: str, variables: Dict[str, str]) -> List[SchemaIssue]:
    """Validate a dict of variables against the schema. Returns list of issues."""
    schema = _load_schema(directory)
    issues: List[SchemaIssue] = []

    for key, field_def in schema.items():
        if key not in variables:
            if field_def.get("required", True) and field_def.get("default") is None:
                issues.append(SchemaIssue(key=key, message=f"Required key '{key}' is missing.", severity="error"))
            elif field_def.get("required", True) and field_def.get("default") is not None:
                issues.append(SchemaIssue(key=key, message=f"Key '{key}' missing but has default '{field_def['default']}'.", severity="warning"))
            continue

        value = variables[key]
        expected_type = field_def.get("type", "string")
        if expected_type == "integer":
            try:
                int(value)
            except ValueError:
                issues.append(SchemaIssue(key=key, message=f"Key '{key}' expected integer, got '{value}'.", severity="error"))
        elif expected_type == "float":
            try:
                float(value)
            except ValueError:
                issues.append(SchemaIssue(key=key, message=f"Key '{key}' expected float, got '{value}'.", severity="error"))
        elif expected_type == "boolean":
            if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
                issues.append(SchemaIssue(key=key, message=f"Key '{key}' expected boolean, got '{value}'.", severity="error"))

    return issues
