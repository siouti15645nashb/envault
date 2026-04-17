"""Tests for envault.env_readonly."""

import json
import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.env_readonly import (
    READONLY_FILENAME,
    _readonly_path,
    mark_readonly,
    unmark_readonly,
    is_readonly,
    list_readonly,
    assert_writable,
    ReadonlyError,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, PASSWORD)
    return path


def test_readonly_filename_constant():
    assert READONLY_FILENAME == ".envault_readonly"


def test_readonly_path_returns_correct_path(vault_file):
    p = _readonly_path(vault_file)
    assert p.name == READONLY_FILENAME
    assert p.parent == Path(vault_file).parent


def test_list_readonly_empty_when_no_file(vault_file):
    assert list_readonly(vault_file) == []


def test_is_readonly_false_when_no_file(vault_file):
    assert is_readonly(vault_file, "MY_KEY") is False


def test_mark_readonly_creates_file(vault_file):
    mark_readonly(vault_file, "API_KEY")
    p = _readonly_path(vault_file)
    assert p.exists()


def test_mark_readonly_stores_key(vault_file):
    mark_readonly(vault_file, "API_KEY")
    assert "API_KEY" in list_readonly(vault_file)


def test_mark_readonly_idempotent(vault_file):
    mark_readonly(vault_file, "API_KEY")
    mark_readonly(vault_file, "API_KEY")
    assert list_readonly(vault_file).count("API_KEY") == 1


def test_is_readonly_true_after_mark(vault_file):
    mark_readonly(vault_file, "DB_URL")
    assert is_readonly(vault_file, "DB_URL") is True


def test_unmark_readonly_removes_key(vault_file):
    mark_readonly(vault_file, "SECRET")
    unmark_readonly(vault_file, "SECRET")
    assert is_readonly(vault_file, "SECRET") is False


def test_unmark_readonly_nonexistent_is_noop(vault_file):
    unmark_readonly(vault_file, "GHOST")
    assert list_readonly(vault_file) == []


def test_list_readonly_returns_sorted(vault_file):
    mark_readonly(vault_file, "Z_KEY")
    mark_readonly(vault_file, "A_KEY")
    result = list_readonly(vault_file)
    assert result == sorted(result)


def test_assert_writable_raises_for_readonly(vault_file):
    mark_readonly(vault_file, "LOCKED")
    with pytest.raises(ReadonlyError, match="LOCKED"):
        assert_writable(vault_file, "LOCKED")


def test_assert_writable_passes_for_normal_key(vault_file):
    assert_writable(vault_file, "NORMAL_KEY")  # should not raise
