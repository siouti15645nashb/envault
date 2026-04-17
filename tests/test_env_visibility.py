"""Tests for envault/env_visibility.py"""

import json
import pytest
from pathlib import Path
from envault.env_visibility import (
    VISIBILITY_FILENAME, _visibility_path, _load_visibility,
    set_visibility, get_visibility, remove_visibility,
    list_visibility, filter_by_level, VisibilityError
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    vf.write_text(json.dumps({"salt": "abc", "variables": {}}))
    return str(vf)


def test_visibility_filename_constant():
    assert VISIBILITY_FILENAME == ".envault_visibility.json"


def test_visibility_path_returns_correct_path(vault_file, tmp_path):
    p = _visibility_path(vault_file)
    assert p == tmp_path / VISIBILITY_FILENAME


def test_list_visibility_empty_when_no_file(vault_file):
    assert list_visibility(vault_file) == {}


def test_set_visibility_creates_file(vault_file, tmp_path):
    set_visibility(vault_file, "DB_HOST", "public")
    assert (tmp_path / VISIBILITY_FILENAME).exists()


def test_set_visibility_stores_level(vault_file):
    set_visibility(vault_file, "API_KEY", "secret")
    assert list_visibility(vault_file)["API_KEY"] == "secret"


def test_set_visibility_invalid_level_raises(vault_file):
    with pytest.raises(VisibilityError):
        set_visibility(vault_file, "KEY", "invisible")


def test_get_visibility_returns_default_private(vault_file):
    assert get_visibility(vault_file, "MISSING_KEY") == "private"


def test_get_visibility_returns_set_level(vault_file):
    set_visibility(vault_file, "TOKEN", "secret")
    assert get_visibility(vault_file, "TOKEN") == "secret"


def test_remove_visibility_deletes_entry(vault_file):
    set_visibility(vault_file, "DB_PASS", "secret")
    remove_visibility(vault_file, "DB_PASS")
    assert "DB_PASS" not in list_visibility(vault_file)


def test_remove_visibility_nonexistent_is_noop(vault_file):
    remove_visibility(vault_file, "NONEXISTENT")
    assert list_visibility(vault_file) == {}


def test_filter_by_level_returns_matching_keys(vault_file):
    set_visibility(vault_file, "A", "public")
    set_visibility(vault_file, "B", "secret")
    set_visibility(vault_file, "C", "public")
    result = filter_by_level(vault_file, "public")
    assert set(result) == {"A", "C"}


def test_filter_by_level_invalid_raises(vault_file):
    with pytest.raises(VisibilityError):
        filter_by_level(vault_file, "unknown")


def test_multiple_levels_stored_independently(vault_file):
    set_visibility(vault_file, "X", "public")
    set_visibility(vault_file, "Y", "private")
    set_visibility(vault_file, "Z", "secret")
    data = list_visibility(vault_file)
    assert data["X"] == "public"
    assert data["Y"] == "private"
    assert data["Z"] == "secret"
