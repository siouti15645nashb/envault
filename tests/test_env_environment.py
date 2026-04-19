"""Tests for envault/env_environment.py"""

import json
import pytest
from pathlib import Path
from envault.env_environment import (
    ENVIRONMENT_FILENAME,
    VALID_ENVIRONMENTS,
    EnvironmentError,
    _environment_path,
    set_environment,
    get_environment,
    remove_environment,
    list_environments,
)
from envault.vault import init_vault


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "password")
    return path


def test_environment_filename_constant():
    assert ENVIRONMENT_FILENAME == ".envault_environment.json"


def test_valid_environments_includes_common():
    for env in ["development", "staging", "production"]:
        assert env in VALID_ENVIRONMENTS


def test_environment_path_returns_correct_path(vault_file):
    p = _environment_path(vault_file)
    assert p.name == ENVIRONMENT_FILENAME


def test_list_environments_empty_when_no_file(vault_file):
    result = list_environments(vault_file)
    assert result == {}


def test_set_environment_creates_file(vault_file):
    set_environment(vault_file, "DB_URL", "production")
    path = _environment_path(vault_file)
    assert path.exists()


def test_set_environment_stores_value(vault_file):
    set_environment(vault_file, "API_KEY", "staging")
    result = list_environments(vault_file)
    assert result["API_KEY"] == "staging"


def test_get_environment_returns_value(vault_file):
    set_environment(vault_file, "SECRET", "development")
    assert get_environment(vault_file, "SECRET") == "development"


def test_get_environment_returns_none_when_not_set(vault_file):
    assert get_environment(vault_file, "MISSING") is None


def test_set_environment_invalid_raises(vault_file):
    with pytest.raises(EnvironmentError, match="Invalid environment"):
        set_environment(vault_file, "KEY", "unknown")


def test_remove_environment_success(vault_file):
    set_environment(vault_file, "KEY", "test")
    remove_environment(vault_file, "KEY")
    assert get_environment(vault_file, "KEY") is None


def test_remove_environment_missing_raises(vault_file):
    with pytest.raises(EnvironmentError):
        remove_environment(vault_file, "NONEXISTENT")


def test_set_environment_overwrites(vault_file):
    set_environment(vault_file, "KEY", "development")
    set_environment(vault_file, "KEY", "production")
    assert get_environment(vault_file, "KEY") == "production"
