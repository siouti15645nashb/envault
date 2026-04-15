"""Tests for envault/profiles.py"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.profiles import (
    PROFILES_FILENAME,
    ProfileError,
    save_profile,
    delete_profile,
    list_profiles,
    get_profile,
    apply_profile,
    _profiles_path,
)


@pytest.fixture
def tmpdir_str(tmp_path):
    return str(tmp_path)


def test_profiles_filename_constant():
    assert PROFILES_FILENAME == ".envault_profiles.json"


def test_profiles_path_returns_correct_path(tmpdir_str):
    p = _profiles_path(tmpdir_str)
    assert p == Path(tmpdir_str) / PROFILES_FILENAME


def test_save_profile_creates_file(tmpdir_str):
    save_profile("dev", ["KEY1", "KEY2"], tmpdir_str)
    assert (Path(tmpdir_str) / PROFILES_FILENAME).exists()


def test_save_profile_stores_keys(tmpdir_str):
    save_profile("dev", ["KEY1", "KEY2"], tmpdir_str)
    keys = get_profile("dev", tmpdir_str)
    assert keys == ["KEY1", "KEY2"]


def test_save_profile_empty_name_raises(tmpdir_str):
    with pytest.raises(ProfileError):
        save_profile("", ["KEY1"], tmpdir_str)


def test_save_profile_blank_name_raises(tmpdir_str):
    with pytest.raises(ProfileError):
        save_profile("   ", ["KEY1"], tmpdir_str)


def test_save_profile_invalid_keys_raises(tmpdir_str):
    with pytest.raises(ProfileError):
        save_profile("dev", "not-a-list", tmpdir_str)


def test_save_profile_overwrites_existing(tmpdir_str):
    save_profile("dev", ["KEY1"], tmpdir_str)
    save_profile("dev", ["KEY2", "KEY3"], tmpdir_str)
    assert get_profile("dev", tmpdir_str) == ["KEY2", "KEY3"]


def test_list_profiles_empty_when_no_file(tmpdir_str):
    assert list_profiles(tmpdir_str) == []


def test_list_profiles_returns_names(tmpdir_str):
    save_profile("dev", ["A"], tmpdir_str)
    save_profile("prod", ["B"], tmpdir_str)
    names = list_profiles(tmpdir_str)
    assert "dev" in names
    assert "prod" in names


def test_delete_profile_removes_entry(tmpdir_str):
    save_profile("dev", ["KEY1"], tmpdir_str)
    delete_profile("dev", tmpdir_str)
    assert "dev" not in list_profiles(tmpdir_str)


def test_delete_profile_nonexistent_raises(tmpdir_str):
    with pytest.raises(ProfileError):
        delete_profile("ghost", tmpdir_str)


def test_get_profile_nonexistent_raises(tmpdir_str):
    with pytest.raises(ProfileError):
        get_profile("missing", tmpdir_str)


def test_apply_profile_returns_values(tmpdir_str):
    save_profile("dev", ["DB_URL", "SECRET"], tmpdir_str)
    with patch("envault.profiles.get_variable") as mock_get:
        mock_get.side_effect = lambda k, p, vp: f"value_{k}"
        result = apply_profile("dev", "password", ".envault", tmpdir_str)
    assert result == {"DB_URL": "value_DB_URL", "SECRET": "value_SECRET"}


def test_apply_profile_missing_vault_key_returns_none(tmpdir_str):
    from envault.vault import VaultError
    save_profile("dev", ["MISSING"], tmpdir_str)
    with patch("envault.profiles.get_variable") as mock_get:
        mock_get.side_effect = VaultError("not found")
        result = apply_profile("dev", "password", ".envault", tmpdir_str)
    assert result["MISSING"] is None
