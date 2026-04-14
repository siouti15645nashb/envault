"""Tests for envault/export.py — variable export formatting."""

import json
import pytest
from pathlib import Path

from envault.vault import init_vault, set_variable
from envault.export import export_variables, SUPPORTED_FORMATS


PASSWORD = "export-test-password"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / ".envault"
    init_vault(path, PASSWORD)
    set_variable(path, PASSWORD, "DB_HOST", "localhost")
    set_variable(path, PASSWORD, "DB_PORT", "5432")
    set_variable(path, PASSWORD, "API_KEY", 'abc"def')
    return path


def test_supported_formats_constant():
    assert "dotenv" in SUPPORTED_FORMATS
    assert "shell" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS


def test_export_dotenv_format(vault_file):
    output = export_variables(vault_file, PASSWORD, fmt="dotenv")
    assert 'DB_HOST="localhost"' in output
    assert 'DB_PORT="5432"' in output


def test_export_shell_format(vault_file):
    output = export_variables(vault_file, PASSWORD, fmt="shell")
    assert 'export DB_HOST="localhost"' in output
    assert 'export DB_PORT="5432"' in output


def test_export_json_format(vault_file):
    output = export_variables(vault_file, PASSWORD, fmt="json")
    data = json.loads(output)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"


def test_export_escapes_quotes_in_dotenv(vault_file):
    output = export_variables(vault_file, PASSWORD, fmt="dotenv")
    assert 'API_KEY="abc\\"def"' in output


def test_export_escapes_quotes_in_shell(vault_file):
    output = export_variables(vault_file, PASSWORD, fmt="shell")
    assert 'export API_KEY="abc\\"def"' in output


def test_export_selective_keys(vault_file):
    output = export_variables(vault_file, PASSWORD, fmt="dotenv", keys=["DB_HOST"])
    assert "DB_HOST" in output
    assert "DB_PORT" not in output


def test_export_unsupported_format_raises(vault_file):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_variables(vault_file, PASSWORD, fmt="yaml")


def test_export_empty_selection_returns_empty_string(vault_file):
    output = export_variables(vault_file, PASSWORD, fmt="dotenv", keys=[])
    assert output == ""
