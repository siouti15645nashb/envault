"""Tests for env_template_vars interpolation module."""

import os
import pytest
from envault.vault import init_vault, set_variable
from envault.env_template_vars import (
    interpolate_value,
    interpolate_all,
    InterpolationError,
    _find_refs,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, PASSWORD)
    return path


def test_find_refs_none():
    assert _find_refs("hello world") == []


def test_find_refs_single():
    assert _find_refs("${BASE_URL}/api") == ["BASE_URL"]


def test_find_refs_multiple():
    refs = _find_refs("${PROTO}://${HOST}:${PORT}")
    assert refs == ["PROTO", "HOST", "PORT"]


def test_interpolate_value_no_refs(vault_file):
    result = interpolate_value("plain_value", vault_file, PASSWORD)
    assert result == "plain_value"


def test_interpolate_value_single_ref(vault_file):
    set_variable(vault_file, PASSWORD, "HOST", "localhost")
    result = interpolate_value("${HOST}:8080", vault_file, PASSWORD)
    assert result == "localhost:8080"


def test_interpolate_value_multiple_refs(vault_file):
    set_variable(vault_file, PASSWORD, "PROTO", "https")
    set_variable(vault_file, PASSWORD, "HOST", "example.com")
    result = interpolate_value("${PROTO}://${HOST}", vault_file, PASSWORD)
    assert result == "https://example.com"


def test_interpolate_value_nested(vault_file):
    set_variable(vault_file, PASSWORD, "HOST", "example.com")
    set_variable(vault_file, PASSWORD, "BASE_URL", "https://${HOST}")
    result = interpolate_value("${BASE_URL}/path", vault_file, PASSWORD)
    assert result == "https://example.com/path"


def test_interpolate_value_missing_ref_raises(vault_file):
    with pytest.raises(InterpolationError, match="MISSING"):
        interpolate_value("${MISSING}", vault_file, PASSWORD)


def test_interpolate_value_circular_raises(vault_file):
    set_variable(vault_file, PASSWORD, "A", "${B}")
    set_variable(vault_file, PASSWORD, "B", "${A}")
    with pytest.raises(InterpolationError, match="Circular"):
        interpolate_value("${A}", vault_file, PASSWORD)


def test_interpolate_all_returns_resolved(vault_file):
    set_variable(vault_file, PASSWORD, "HOST", "localhost")
    set_variable(vault_file, PASSWORD, "URL", "http://${HOST}")
    result = interpolate_all(vault_file, PASSWORD)
    assert result["HOST"] == "localhost"
    assert result["URL"] == "http://localhost"


def test_interpolate_all_bad_ref_returns_raw(vault_file):
    set_variable(vault_file, PASSWORD, "BAD", "${NONEXISTENT}")
    result = interpolate_all(vault_file, PASSWORD)
    assert result["BAD"] == "${NONEXISTENT}"
