"""Tests for envault.env_check."""

import json
import os
import pytest

from envault.vault import init_vault, set_variable
from envault.env_check import check_env, EnvCheckResult


PASSWORD = "test-password"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, PASSWORD)
    set_variable(path, PASSWORD, "DB_HOST", "localhost")
    set_variable(path, PASSWORD, "DB_PORT", "5432")
    set_variable(path, PASSWORD, "API_KEY", "secret123")
    return path


def test_all_matched(vault_file):
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret123"}
    result = check_env(vault_file, PASSWORD, env)
    assert result.matched == ["API_KEY", "DB_HOST", "DB_PORT"]
    assert result.missing == []
    assert result.mismatched == []
    assert result.has_issues is False


def test_missing_key(vault_file):
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}  # API_KEY absent
    result = check_env(vault_file, PASSWORD, env)
    assert "API_KEY" in result.missing
    assert result.has_issues is True


def test_mismatched_value(vault_file):
    env = {"DB_HOST": "remotehost", "DB_PORT": "5432", "API_KEY": "secret123"}
    result = check_env(vault_file, PASSWORD, env)
    assert "DB_HOST" in result.mismatched
    assert result.has_issues is True


def test_extra_keys_not_reported_by_default(vault_file):
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret123", "EXTRA": "x"}
    result = check_env(vault_file, PASSWORD, env)
    assert result.extra == []


def test_extra_keys_reported_when_requested(vault_file):
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret123", "EXTRA": "x"}
    result = check_env(vault_file, PASSWORD, env, include_extra=True)
    assert "EXTRA" in result.extra


def test_defaults_to_os_environ(vault_file, monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("API_KEY", "secret123")
    result = check_env(vault_file, PASSWORD)  # no env kwarg
    assert result.matched == ["API_KEY", "DB_HOST", "DB_PORT"]


def test_empty_vault_no_issues(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, PASSWORD)
    result = check_env(path, PASSWORD, {"SOME_VAR": "value"})
    assert not result.has_issues
    assert result.matched == []


def test_results_are_sorted(vault_file):
    env = {}  # all missing
    result = check_env(vault_file, PASSWORD, env)
    assert result.missing == sorted(result.missing)
