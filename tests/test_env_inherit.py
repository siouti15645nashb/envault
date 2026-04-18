"""Tests for envault.env_inherit module."""
import json
import os
import pytest
from pathlib import Path

from envault.vault import init_vault, set_variable
from envault.env_inherit import (
    INHERIT_FILENAME,
    InheritError,
    _inherit_path,
    set_parent,
    get_parent,
    remove_parent,
    resolve_variables,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_pair(tmp_path):
    parent = str(tmp_path / "parent" / "vault.json")
    child = str(tmp_path / "child" / "vault.json")
    os.makedirs(str(tmp_path / "parent"), exist_ok=True)
    os.makedirs(str(tmp_path / "child"), exist_ok=True)
    init_vault(parent, PASSWORD)
    init_vault(child, PASSWORD)
    return parent, child


def test_inherit_filename_constant():
    assert INHERIT_FILENAME == ".envault_inherit"


def test_inherit_path_returns_correct_path(tmp_path):
    vault = str(tmp_path / "vault.json")
    p = _inherit_path(vault)
    assert p == tmp_path / INHERIT_FILENAME


def test_get_parent_none_when_no_file(vault_pair):
    _, child = vault_pair
    assert get_parent(child) is None


def test_set_parent_creates_file(vault_pair):
    parent, child = vault_pair
    set_parent(child, parent)
    inherit_file = _inherit_path(child)
    assert inherit_file.exists()


def test_set_parent_stores_resolved_path(vault_pair):
    parent, child = vault_pair
    set_parent(child, parent)
    stored = get_parent(child)
    assert stored == str(Path(parent).resolve())


def test_set_parent_raises_if_parent_missing(tmp_path):
    vault = str(tmp_path / "vault.json")
    os.makedirs(str(tmp_path), exist_ok=True)
    init_vault(vault, PASSWORD)
    with pytest.raises(InheritError, match="Parent vault not found"):
        set_parent(vault, str(tmp_path / "nonexistent.json"))


def test_remove_parent_success(vault_pair):
    parent, child = vault_pair
    set_parent(child, parent)
    remove_parent(child)
    assert get_parent(child) is None


def test_remove_parent_raises_if_not_set(vault_pair):
    _, child = vault_pair
    with pytest.raises(InheritError, match="No parent vault is set"):
        remove_parent(child)


def test_resolve_variables_merges_parent_and_child(vault_pair):
    parent, child = vault_pair
    set_variable(parent, PASSWORD, "SHARED", "from_parent")
    set_variable(parent, PASSWORD, "PARENT_ONLY", "pval")
    set_variable(child, PASSWORD, "SHARED", "from_child")
    set_variable(child, PASSWORD, "CHILD_ONLY", "cval")
    set_parent(child, parent)
    result = resolve_variables(child, PASSWORD)
    assert result["SHARED"] == "from_child"
    assert result["PARENT_ONLY"] == "pval"
    assert result["CHILD_ONLY"] == "cval"


def test_resolve_variables_no_parent(vault_pair):
    _, child = vault_pair
    set_variable(child, PASSWORD, "KEY", "val")
    result = resolve_variables(child, PASSWORD)
    assert result == {"KEY": "val"}
