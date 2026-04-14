"""Tests for the vault read/write module."""

import json
import pytest
from pathlib import Path

from envault.vault import (
    init_vault,
    set_variable,
    get_variable,
    list_keys,
    delete_variable,
)

PASSWORD = "super-secret-password"


@pytest.fixture
def vault_file(tmp_path):
    """Create a fresh vault in a temporary directory."""
    vault_path = tmp_path / ".envault"
    init_vault(PASSWORD, vault_path=vault_path)
    return vault_path


def test_init_vault_creates_file(tmp_path):
    vault_path = tmp_path / ".envault"
    result = init_vault(PASSWORD, vault_path=vault_path)
    assert result == vault_path
    assert vault_path.exists()


def test_init_vault_file_has_salt_and_empty_variables(tmp_path):
    vault_path = tmp_path / ".envault"
    init_vault(PASSWORD, vault_path=vault_path)
    data = json.loads(vault_path.read_text())
    assert "salt" in data
    assert data["variables"] == {}


def test_init_vault_raises_if_exists(vault_file):
    with pytest.raises(FileExistsError):
        init_vault(PASSWORD, vault_path=vault_file)


def test_set_and_get_variable(vault_file):
    set_variable("API_KEY", "my-api-key-123", PASSWORD, vault_path=vault_file)
    value = get_variable("API_KEY", PASSWORD, vault_path=vault_file)
    assert value == "my-api-key-123"


def test_set_variable_stores_encrypted_value(vault_file):
    set_variable("SECRET", "plain-text", PASSWORD, vault_path=vault_file)
    data = json.loads(vault_file.read_text())
    # Stored value must not equal the plain-text
    assert data["variables"]["SECRET"] != "plain-text"


def test_get_variable_raises_for_missing_key(vault_file):
    with pytest.raises(KeyError, match="MISSING_KEY"):
        get_variable("MISSING_KEY", PASSWORD, vault_path=vault_file)


def test_set_multiple_variables(vault_file):
    set_variable("VAR1", "value1", PASSWORD, vault_path=vault_file)
    set_variable("VAR2", "value2", PASSWORD, vault_path=vault_file)
    assert get_variable("VAR1", PASSWORD, vault_path=vault_file) == "value1"
    assert get_variable("VAR2", PASSWORD, vault_path=vault_file) == "value2"


def test_list_keys_returns_all_keys(vault_file):
    set_variable("A", "1", PASSWORD, vault_path=vault_file)
    set_variable("B", "2", PASSWORD, vault_path=vault_file)
    keys = list_keys(vault_path=vault_file)
    assert set(keys) == {"A", "B"}


def test_list_keys_empty_vault(vault_file):
    assert list_keys(vault_path=vault_file) == []


def test_delete_variable(vault_file):
    set_variable("TO_DELETE", "bye", PASSWORD, vault_path=vault_file)
    delete_variable("TO_DELETE", vault_path=vault_file)
    assert "TO_DELETE" not in list_keys(vault_path=vault_file)


def test_delete_variable_raises_for_missing_key(vault_file):
    with pytest.raises(KeyError, match="NONEXISTENT"):
        delete_variable("NONEXISTENT", vault_path=vault_file)


def test_overwrite_variable(vault_file):
    set_variable("KEY", "original", PASSWORD, vault_path=vault_file)
    set_variable("KEY", "updated", PASSWORD, vault_path=vault_file)
    assert get_variable("KEY", PASSWORD, vault_path=vault_file) == "updated"
