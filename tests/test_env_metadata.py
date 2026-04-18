"""Tests for envault/env_metadata.py"""

import os
import pytest
from envault.env_metadata import (
    METADATA_FILENAME,
    MetadataError,
    _metadata_path,
    set_metadata,
    get_metadata,
    remove_metadata_key,
    remove_all_metadata,
    list_metadata,
)
from envault.vault import init_vault


@pytest.fixture
def vault_file(tmp_path):
    vf = str(tmp_path / ".envault")
    init_vault(vf, "password")
    return vf


def test_metadata_filename_constant():
    assert METADATA_FILENAME == ".envault_metadata.json"


def test_metadata_path_returns_correct_path(vault_file):
    expected = os.path.join(os.path.dirname(vault_file), METADATA_FILENAME)
    assert _metadata_path(vault_file) == expected


def test_list_metadata_empty_when_no_file(vault_file):
    assert list_metadata(vault_file) == {}


def test_set_metadata_creates_file(vault_file):
    set_metadata(vault_file, "MY_KEY", "owner", "alice")
    assert os.path.exists(_metadata_path(vault_file))


def test_set_metadata_stores_value(vault_file):
    set_metadata(vault_file, "MY_KEY", "owner", "alice")
    meta = get_metadata(vault_file, "MY_KEY")
    assert meta["owner"] == "alice"


def test_set_metadata_multiple_keys(vault_file):
    set_metadata(vault_file, "MY_KEY", "owner", "alice")
    set_metadata(vault_file, "MY_KEY", "team", "backend")
    meta = get_metadata(vault_file, "MY_KEY")
    assert meta["owner"] == "alice"
    assert meta["team"] == "backend"


def test_get_metadata_empty_for_unknown_key(vault_file):
    assert get_metadata(vault_file, "NONEXISTENT") == {}


def test_remove_metadata_key_success(vault_file):
    set_metadata(vault_file, "MY_KEY", "owner", "alice")
    remove_metadata_key(vault_file, "MY_KEY", "owner")
    meta = get_metadata(vault_file, "MY_KEY")
    assert "owner" not in meta


def test_remove_metadata_key_not_found_raises(vault_file):
    with pytest.raises(MetadataError):
        remove_metadata_key(vault_file, "MY_KEY", "nonexistent")


def test_remove_all_metadata(vault_file):
    set_metadata(vault_file, "MY_KEY", "owner", "alice")
    remove_all_metadata(vault_file, "MY_KEY")
    assert get_metadata(vault_file, "MY_KEY") == {}


def test_list_metadata_shows_all_vars(vault_file):
    set_metadata(vault_file, "KEY_A", "env", "prod")
    set_metadata(vault_file, "KEY_B", "env", "dev")
    all_meta = list_metadata(vault_file)
    assert "KEY_A" in all_meta
    assert "KEY_B" in all_meta
