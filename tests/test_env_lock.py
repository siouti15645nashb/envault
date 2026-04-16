"""Tests for envault/env_lock.py"""

import pytest
from pathlib import Path
from envault.env_lock import (
    lock_variable, unlock_variable, is_locked, get_locked,
    assert_not_locked, LockError, LOCK_FILENAME
)


@pytest.fixture
def vault_file(tmp_path):
    v = tmp_path / ".envault"
    v.write_text('{"salt": "abc", "variables": {}}')
    return str(v)


def test_lock_filename_constant():
    assert LOCK_FILENAME == ".envault.lock"


def test_is_locked_false_when_no_file(vault_file):
    assert is_locked(vault_file, "MY_KEY") is False


def test_get_locked_empty_when_no_file(vault_file):
    assert get_locked(vault_file) == []


def test_lock_variable_creates_lock_file(vault_file, tmp_path):
    lock_variable(vault_file, "API_KEY")
    lock_file = tmp_path / ".envault.lock"
    assert lock_file.exists()


def test_lock_variable_is_locked(vault_file):
    lock_variable(vault_file, "API_KEY")
    assert is_locked(vault_file, "API_KEY") is True


def test_lock_variable_idempotent(vault_file):
    lock_variable(vault_file, "API_KEY")
    lock_variable(vault_file, "API_KEY")
    assert get_locked(vault_file).count("API_KEY") == 1


def test_lock_multiple_variables(vault_file):
    lock_variable(vault_file, "KEY_A")
    lock_variable(vault_file, "KEY_B")
    locked = get_locked(vault_file)
    assert "KEY_A" in locked
    assert "KEY_B" in locked


def test_unlock_variable_success(vault_file):
    lock_variable(vault_file, "API_KEY")
    unlock_variable(vault_file, "API_KEY")
    assert is_locked(vault_file, "API_KEY") is False


def test_unlock_nonlocked_raises(vault_file):
    with pytest.raises(LockError):
        unlock_variable(vault_file, "MISSING_KEY")


def test_assert_not_locked_passes_when_unlocked(vault_file):
    assert_not_locked(vault_file, "FREE_KEY")  # should not raise


def test_assert_not_locked_raises_when_locked(vault_file):
    lock_variable(vault_file, "LOCKED_KEY")
    with pytest.raises(LockError, match="locked"):
        assert_not_locked(vault_file, "LOCKED_KEY")
