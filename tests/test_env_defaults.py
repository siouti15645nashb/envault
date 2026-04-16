"""Tests for envault.env_defaults."""

import pytest
from envault.env_defaults import (
    DEFAULTS_FILENAME,
    DefaultsError,
    set_default,
    remove_default,
    get_default,
    list_defaults,
    apply_defaults,
    _defaults_path,
)


@pytest.fixture
def tmpdir_str(tmp_path):
    return str(tmp_path)


def test_defaults_filename_constant():
    assert DEFAULTS_FILENAME == ".envault_defaults.json"


def test_defaults_path_returns_correct_path(tmpdir_str):
    p = _defaults_path(tmpdir_str)
    assert p.name == DEFAULTS_FILENAME


def test_list_defaults_empty_when_no_file(tmpdir_str):
    assert list_defaults(tmpdir_str) == {}


def test_set_default_creates_file(tmpdir_str):
    set_default(tmpdir_str, "API_URL", "http://localhost")
    assert _defaults_path(tmpdir_str).exists()


def test_set_default_stores_value(tmpdir_str):
    set_default(tmpdir_str, "API_URL", "http://localhost")
    assert get_default(tmpdir_str, "API_URL") == "http://localhost"


def test_set_default_empty_key_raises(tmpdir_str):
    with pytest.raises(DefaultsError):
        set_default(tmpdir_str, "", "value")


def test_get_default_missing_key_returns_none(tmpdir_str):
    assert get_default(tmpdir_str, "MISSING") is None


def test_remove_default_success(tmpdir_str):
    set_default(tmpdir_str, "KEY", "val")
    remove_default(tmpdir_str, "KEY")
    assert get_default(tmpdir_str, "KEY") is None


def test_remove_default_nonexistent_raises(tmpdir_str):
    with pytest.raises(DefaultsError):
        remove_default(tmpdir_str, "GHOST")


def test_list_defaults_returns_all(tmpdir_str):
    set_default(tmpdir_str, "A", "1")
    set_default(tmpdir_str, "B", "2")
    result = list_defaults(tmpdir_str)
    assert result == {"A": "1", "B": "2"}


def test_apply_defaults_fills_missing(tmpdir_str):
    set_default(tmpdir_str, "DB_HOST", "localhost")
    result = apply_defaults(tmpdir_str, {"API_KEY": "abc"})
    assert result["DB_HOST"] == "localhost"
    assert result["API_KEY"] == "abc"


def test_apply_defaults_does_not_override_existing(tmpdir_str):
    set_default(tmpdir_str, "DB_HOST", "localhost")
    result = apply_defaults(tmpdir_str, {"DB_HOST": "prod-server"})
    assert result["DB_HOST"] == "prod-server"
