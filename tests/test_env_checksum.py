"""Tests for envault/env_checksum.py"""

import pytest
from pathlib import Path
from envault.vault import init_vault, set_variable
from envault.env_checksum import (
    CHECKSUM_FILENAME,
    _checksum_path,
    record_checksum,
    verify_checksum,
    remove_checksum,
    list_checksums,
    ChecksumError,
)


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "password")
    set_variable(path, "password", "API_KEY", "secret123")
    return path


def test_checksum_filename_constant():
    assert CHECKSUM_FILENAME == ".envault_checksums.json"


def test_checksum_path_returns_correct_path(vault_file):
    p = _checksum_path(vault_file)
    assert p.name == CHECKSUM_FILENAME
    assert p.parent == Path(vault_file).parent


def test_list_checksums_empty_when_no_file(vault_file):
    result = list_checksums(vault_file)
    assert result == {}


def test_record_checksum_creates_file(vault_file):
    record_checksum(vault_file, "API_KEY", "secret123")
    assert _checksum_path(vault_file).exists()


def test_record_checksum_returns_hex_digest(vault_file):
    digest = record_checksum(vault_file, "API_KEY", "secret123")
    assert isinstance(digest, str)
    assert len(digest) == 64  # sha256 hex


def test_record_checksum_is_deterministic(vault_file):
    d1 = record_checksum(vault_file, "API_KEY", "secret123")
    d2 = record_checksum(vault_file, "API_KEY", "secret123")
    assert d1 == d2


def test_record_checksum_differs_for_different_values(vault_file):
    d1 = record_checksum(vault_file, "API_KEY", "secret123")
    d2 = record_checksum(vault_file, "API_KEY", "other_value")
    assert d1 != d2


def test_verify_checksum_true_for_matching_value(vault_file):
    record_checksum(vault_file, "API_KEY", "secret123")
    assert verify_checksum(vault_file, "API_KEY", "secret123") is True


def test_verify_checksum_false_for_changed_value(vault_file):
    record_checksum(vault_file, "API_KEY", "secret123")
    assert verify_checksum(vault_file, "API_KEY", "tampered") is False


def test_verify_checksum_raises_if_key_missing(vault_file):
    with pytest.raises(ChecksumError, match="No checksum recorded"):
        verify_checksum(vault_file, "MISSING_KEY", "value")


def test_remove_checksum_deletes_entry(vault_file):
    record_checksum(vault_file, "API_KEY", "secret123")
    remove_checksum(vault_file, "API_KEY")
    assert "API_KEY" not in list_checksums(vault_file)


def test_remove_checksum_noop_if_missing(vault_file):
    remove_checksum(vault_file, "NONEXISTENT")  # should not raise


def test_list_checksums_shows_recorded_keys(vault_file):
    record_checksum(vault_file, "API_KEY", "secret123")
    record_checksum(vault_file, "DB_PASS", "dbpass")
    result = list_checksums(vault_file)
    assert "API_KEY" in result
    assert "DB_PASS" in result
