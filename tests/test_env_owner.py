"""Tests for envault.env_owner module."""

import json
import pytest
from pathlib import Path

from envault.env_owner import (
    OWNER_FILENAME,
    OwnerError,
    _owner_path,
    set_owner,
    get_owner,
    remove_owner,
    list_owners,
)
from envault.vault import init_vault


@pytest.fixture
def vault_file(tmp_path):
    vf = str(tmp_path / "vault.json")
    init_vault(vf, "password")
    return vf


def test_owner_filename_constant():
    assert OWNER_FILENAME == ".envault_owners.json"


def test_owner_path_returns_correct_path(vault_file):
    p = _owner_path(vault_file)
    assert p.name == OWNER_FILENAME
    assert p.parent == Path(vault_file).parent


def test_list_owners_empty_when_no_file(vault_file):
    assert list_owners(vault_file) == {}


def test_set_owner_creates_file(vault_file):
    set_owner(vault_file, "API_KEY", "alice")
    assert _owner_path(vault_file).exists()


def test_set_owner_stores_correct_owner(vault_file):
    set_owner(vault_file, "API_KEY", "alice")
    assert get_owner(vault_file, "API_KEY") == "alice"


def test_set_owner_overwrites_existing(vault_file):
    set_owner(vault_file, "API_KEY", "alice")
    set_owner(vault_file, "API_KEY", "bob")
    assert get_owner(vault_file, "API_KEY") == "bob"


def test_get_owner_returns_none_when_missing(vault_file):
    assert get_owner(vault_file, "MISSING") is None


def test_set_owner_empty_string_raises(vault_file):
    with pytest.raises(OwnerError):
        set_owner(vault_file, "KEY", "")


def test_set_owner_whitespace_only_raises(vault_file):
    with pytest.raises(OwnerError):
        set_owner(vault_file, "KEY", "   ")


def test_remove_owner_returns_true_when_exists(vault_file):
    set_owner(vault_file, "API_KEY", "alice")
    assert remove_owner(vault_file, "API_KEY") is True


def test_remove_owner_returns_false_when_missing(vault_file):
    assert remove_owner(vault_file, "NOPE") is False


def test_remove_owner_deletes_entry(vault_file):
    set_owner(vault_file, "API_KEY", "alice")
    remove_owner(vault_file, "API_KEY")
    assert get_owner(vault_file, "API_KEY") is None


def test_list_owners_returns_all(vault_file):
    set_owner(vault_file, "KEY_A", "alice")
    set_owner(vault_file, "KEY_B", "bob")
    result = list_owners(vault_file)
    assert result == {"KEY_A": "alice", "KEY_B": "bob"}
