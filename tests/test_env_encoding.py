import pytest
import json
from pathlib import Path
from envault.env_encoding import (
    ENCODING_FILENAME,
    VALID_ENCODINGS,
    EncodingError,
    _encoding_path,
    set_encoding,
    get_encoding,
    remove_encoding,
    list_encodings,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_encoding_filename_constant():
    assert ENCODING_FILENAME == ".envault_encoding"


def test_valid_encodings_includes_common():
    assert "utf-8" in VALID_ENCODINGS
    assert "ascii" in VALID_ENCODINGS


def test_encoding_path_returns_correct_path(vault_dir):
    p = _encoding_path(vault_dir)
    assert p == Path(vault_dir) / ENCODING_FILENAME


def test_list_encodings_empty_when_no_file(vault_dir):
    assert list_encodings(vault_dir) == {}


def test_set_encoding_creates_file(vault_dir):
    set_encoding(vault_dir, "API_KEY", "utf-8")
    assert _encoding_path(vault_dir).exists()


def test_set_encoding_stores_value(vault_dir):
    set_encoding(vault_dir, "API_KEY", "utf-16")
    data = list_encodings(vault_dir)
    assert data["API_KEY"] == "utf-16"


def test_get_encoding_returns_value(vault_dir):
    set_encoding(vault_dir, "TOKEN", "ascii")
    assert get_encoding(vault_dir, "TOKEN") == "ascii"


def test_get_encoding_returns_none_when_not_set(vault_dir):
    assert get_encoding(vault_dir, "MISSING") is None


def test_set_encoding_invalid_raises(vault_dir):
    with pytest.raises(EncodingError):
        set_encoding(vault_dir, "KEY", "utf-99")


def test_set_encoding_empty_key_raises(vault_dir):
    with pytest.raises(EncodingError):
        set_encoding(vault_dir, "", "utf-8")


def test_remove_encoding_success(vault_dir):
    set_encoding(vault_dir, "KEY", "utf-8")
    result = remove_encoding(vault_dir, "KEY")
    assert result is True
    assert get_encoding(vault_dir, "KEY") is None


def test_remove_encoding_missing_returns_false(vault_dir):
    result = remove_encoding(vault_dir, "NONEXISTENT")
    assert result is False


def test_list_encodings_multiple(vault_dir):
    set_encoding(vault_dir, "A", "utf-8")
    set_encoding(vault_dir, "B", "ascii")
    data = list_encodings(vault_dir)
    assert data == {"A": "utf-8", "B": "ascii"}
