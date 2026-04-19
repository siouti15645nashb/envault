"""Tests for envault.env_version."""
import os
import pytest
from envault.vault import init_vault, set_variable
from envault.env_version import (
    VERSION_FILENAME,
    _version_path,
    record_version,
    get_versions,
    get_latest_version,
    clear_versions,
    list_versioned_keys,
)


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "password")
    set_variable(path, "password", "KEY", "value1")
    return path


def test_version_filename_constant():
    assert VERSION_FILENAME == ".envault_versions.json"


def test_version_path_returns_correct_path(vault_file):
    expected = os.path.join(os.path.dirname(vault_file), VERSION_FILENAME)
    assert _version_path(vault_file) == expected


def test_get_versions_empty_when_no_file(vault_file):
    assert get_versions(vault_file, "KEY") == []


def test_record_version_creates_file(vault_file):
    record_version(vault_file, "KEY", "value1")
    assert os.path.exists(_version_path(vault_file))


def test_record_version_stores_value(vault_file):
    record_version(vault_file, "KEY", "hello")
    versions = get_versions(vault_file, "KEY")
    assert len(versions) == 1
    assert versions[0]["value"] == "hello"


def test_record_version_stores_timestamp(vault_file):
    record_version(vault_file, "KEY", "hello")
    versions = get_versions(vault_file, "KEY")
    assert "timestamp" in versions[0]


def test_record_multiple_versions(vault_file):
    record_version(vault_file, "KEY", "v1")
    record_version(vault_file, "KEY", "v2")
    record_version(vault_file, "KEY", "v3")
    assert len(get_versions(vault_file, "KEY")) == 3


def test_get_latest_version_none_when_empty(vault_file):
    assert get_latest_version(vault_file, "MISSING") is None


def test_get_latest_version_returns_last(vault_file):
    record_version(vault_file, "KEY", "first")
    record_version(vault_file, "KEY", "last")
    latest = get_latest_version(vault_file, "KEY")
    assert latest["value"] == "last"


def test_clear_versions_returns_count(vault_file):
    record_version(vault_file, "KEY", "a")
    record_version(vault_file, "KEY", "b")
    removed = clear_versions(vault_file, "KEY")
    assert removed == 2


def test_clear_versions_removes_history(vault_file):
    record_version(vault_file, "KEY", "a")
    clear_versions(vault_file, "KEY")
    assert get_versions(vault_file, "KEY") == []


def test_list_versioned_keys(vault_file):
    record_version(vault_file, "ALPHA", "1")
    record_version(vault_file, "BETA", "2")
    keys = list_versioned_keys(vault_file)
    assert "ALPHA" in keys
    assert "BETA" in keys


def test_list_versioned_keys_empty_when_no_file(vault_file):
    assert list_versioned_keys(vault_file) == []
