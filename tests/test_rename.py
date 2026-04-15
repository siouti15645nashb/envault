"""Tests for envault/rename.py."""

import os
import pytest
from click.testing import CliRunner

from envault.vault import init_vault, set_variable, get_variable, list_variables
from envault.rename import RenameError, rename_variable, rename_variable_force, copy_variable


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    init_vault(path, "password")
    set_variable(path, "password", "DB_HOST", "localhost")
    set_variable(path, "password", "DB_PORT", "5432")
    return path


def test_rename_variable_success(vault_file):
    rename_variable(vault_file, "password", "DB_HOST", "DATABASE_HOST")
    assert get_variable(vault_file, "password", "DATABASE_HOST") == "localhost"


def test_rename_removes_old_key(vault_file):
    rename_variable(vault_file, "password", "DB_HOST", "DATABASE_HOST")
    keys = list_variables(vault_file, "password")
    assert "DB_HOST" not in keys
    assert "DATABASE_HOST" in keys


def test_rename_nonexistent_key_raises(vault_file):
    with pytest.raises(RenameError, match="does not exist"):
        rename_variable(vault_file, "password", "MISSING_KEY", "NEW_KEY")


def test_rename_existing_destination_raises(vault_file):
    with pytest.raises(RenameError, match="already exists"):
        rename_variable(vault_file, "password", "DB_HOST", "DB_PORT")


def test_rename_force_overwrites_destination(vault_file):
    rename_variable_force(vault_file, "password", "DB_HOST", "DB_PORT")
    assert get_variable(vault_file, "password", "DB_PORT") == "localhost"
    keys = list_variables(vault_file, "password")
    assert "DB_HOST" not in keys


def test_rename_force_nonexistent_key_raises(vault_file):
    with pytest.raises(RenameError, match="does not exist"):
        rename_variable_force(vault_file, "password", "GHOST", "NEW")


def test_copy_variable_success(vault_file):
    copy_variable(vault_file, "password", "DB_HOST", "REPLICA_HOST")
    assert get_variable(vault_file, "password", "REPLICA_HOST") == "localhost"


def test_copy_keeps_original(vault_file):
    copy_variable(vault_file, "password", "DB_HOST", "REPLICA_HOST")
    assert get_variable(vault_file, "password", "DB_HOST") == "localhost"


def test_copy_nonexistent_key_raises(vault_file):
    with pytest.raises(RenameError, match="does not exist"):
        copy_variable(vault_file, "password", "MISSING", "DEST")


def test_copy_existing_destination_raises(vault_file):
    with pytest.raises(RenameError, match="already exists"):
        copy_variable(vault_file, "password", "DB_HOST", "DB_PORT")
