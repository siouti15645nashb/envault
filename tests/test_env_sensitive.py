"""Tests for envault.env_sensitive."""

import pytest
from pathlib import Path
from envault.env_sensitive import (
    SENSITIVE_FILENAME,
    mark_sensitive,
    unmark_sensitive,
    is_sensitive,
    list_sensitive,
    SensitiveError,
    _sensitive_path,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    vf.write_text('{"salt": "abc", "variables": {}}')
    return str(vf)


def test_sensitive_filename_constant():
    assert SENSITIVE_FILENAME == ".envault_sensitive"


def test_sensitive_path_returns_correct_path(vault_file):
    p = _sensitive_path(vault_file)
    assert p.name == SENSITIVE_FILENAME


def test_list_sensitive_empty_when_no_file(vault_file):
    assert list_sensitive(vault_file) == []


def test_mark_sensitive_creates_file(vault_file):
    mark_sensitive(vault_file, "SECRET_KEY")
    p = _sensitive_path(vault_file)
    assert p.exists()


def test_mark_sensitive_stores_key(vault_file):
    mark_sensitive(vault_file, "SECRET_KEY")
    assert "SECRET_KEY" in list_sensitive(vault_file)


def test_mark_sensitive_idempotent(vault_file):
    mark_sensitive(vault_file, "SECRET_KEY")
    mark_sensitive(vault_file, "SECRET_KEY")
    assert list_sensitive(vault_file).count("SECRET_KEY") == 1


def test_is_sensitive_true_after_mark(vault_file):
    mark_sensitive(vault_file, "DB_PASS")
    assert is_sensitive(vault_file, "DB_PASS") is True


def test_is_sensitive_false_when_not_marked(vault_file):
    assert is_sensitive(vault_file, "DB_PASS") is False


def test_unmark_sensitive_removes_key(vault_file):
    mark_sensitive(vault_file, "API_KEY")
    unmark_sensitive(vault_file, "API_KEY")
    assert is_sensitive(vault_file, "API_KEY") is False


def test_unmark_sensitive_raises_if_not_marked(vault_file):
    with pytest.raises(SensitiveError):
        unmark_sensitive(vault_file, "MISSING")


def test_list_sensitive_sorted(vault_file):
    mark_sensitive(vault_file, "Z_KEY")
    mark_sensitive(vault_file, "A_KEY")
    keys = list_sensitive(vault_file)
    assert keys == sorted(keys)
