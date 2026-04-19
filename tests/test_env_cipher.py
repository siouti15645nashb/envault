"""Tests for envault.env_cipher."""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.env_cipher import (
    CIPHER_FILENAME, VALID_CIPHERS, CipherError,
    _cipher_path, set_cipher, get_cipher, remove_cipher, list_ciphers
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_cipher_filename_constant():
    assert CIPHER_FILENAME == ".envault_cipher.json"


def test_valid_ciphers_includes_common():
    assert "AES-256-GCM" in VALID_CIPHERS
    assert "ChaCha20-Poly1305" in VALID_CIPHERS


def test_cipher_path_returns_correct_path(vault_dir):
    p = _cipher_path(vault_dir)
    assert p == Path(vault_dir) / CIPHER_FILENAME


def test_list_ciphers_empty_when_no_file(vault_dir):
    assert list_ciphers(vault_dir) == {}


def test_set_cipher_creates_file(vault_dir):
    set_cipher(vault_dir, "DB_PASS", "AES-256-GCM")
    assert _cipher_path(vault_dir).exists()


def test_set_cipher_stores_value(vault_dir):
    set_cipher(vault_dir, "API_KEY", "ChaCha20-Poly1305")
    data = list_ciphers(vault_dir)
    assert data["API_KEY"] == "ChaCha20-Poly1305"


def test_set_cipher_invalid_raises(vault_dir):
    with pytest.raises(CipherError, match="Invalid cipher"):
        set_cipher(vault_dir, "KEY", "BLOWFISH")


def test_get_cipher_returns_none_when_not_set(vault_dir):
    assert get_cipher(vault_dir, "MISSING") is None


def test_get_cipher_returns_value(vault_dir):
    set_cipher(vault_dir, "SECRET", "AES-256-CBC")
    assert get_cipher(vault_dir, "SECRET") == "AES-256-CBC"


def test_remove_cipher_deletes_entry(vault_dir):
    set_cipher(vault_dir, "TOKEN", "AES-256-GCM")
    remove_cipher(vault_dir, "TOKEN")
    assert get_cipher(vault_dir, "TOKEN") is None


def test_remove_cipher_nonexistent_raises(vault_dir):
    with pytest.raises(CipherError):
        remove_cipher(vault_dir, "GHOST")


def test_list_ciphers_multiple_entries(vault_dir):
    set_cipher(vault_dir, "A", "AES-256-GCM")
    set_cipher(vault_dir, "B", "AES-256-CBC")
    data = list_ciphers(vault_dir)
    assert len(data) == 2
    assert data["A"] == "AES-256-GCM"
    assert data["B"] == "AES-256-CBC"
