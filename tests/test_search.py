"""Tests for envault/search.py."""

import os
import pytest
from click.testing import CliRunner

from envault.vault import init_vault, set_variable
from envault.search import search_variables, filter_by_prefix


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "secret")
    set_variable(path, "secret", "DB_HOST", "localhost")
    set_variable(path, "secret", "DB_PORT", "5432")
    set_variable(path, "secret", "REDIS_HOST", "127.0.0.1")
    set_variable(path, "secret", "APP_DEBUG", "true")
    set_variable(path, "secret", "APP_ENV", "production")
    return path


def test_search_returns_matching_keys(vault_file):
    results = search_variables(vault_file, "secret", "DB")
    assert "DB_HOST" in results
    assert "DB_PORT" in results
    assert "REDIS_HOST" not in results


def test_search_case_insensitive_by_default(vault_file):
    results = search_variables(vault_file, "secret", "db")
    assert "DB_HOST" in results
    assert "DB_PORT" in results


def test_search_case_sensitive(vault_file):
    results = search_variables(vault_file, "secret", "db", case_sensitive=True)
    assert len(results) == 0


def test_search_no_match_returns_empty(vault_file):
    results = search_variables(vault_file, "secret", "NONEXISTENT")
    assert results == {}


def test_search_returns_correct_values(vault_file):
    results = search_variables(vault_file, "secret", "REDIS")
    assert results["REDIS_HOST"] == "127.0.0.1"


def test_filter_by_prefix_matches(vault_file):
    results = filter_by_prefix(vault_file, "secret", "APP")
    assert "APP_DEBUG" in results
    assert "APP_ENV" in results
    assert "DB_HOST" not in results


def test_filter_by_prefix_case_insensitive(vault_file):
    results = filter_by_prefix(vault_file, "secret", "app")
    assert "APP_DEBUG" in results
    assert "APP_ENV" in results


def test_filter_by_prefix_case_sensitive(vault_file):
    results = filter_by_prefix(vault_file, "secret", "app", case_sensitive=True)
    assert len(results) == 0


def test_search_raises_if_no_vault(tmp_path):
    path = str(tmp_path / "missing.json")
    with pytest.raises(FileNotFoundError):
        search_variables(path, "secret", "DB")


def test_filter_raises_if_no_vault(tmp_path):
    path = str(tmp_path / "missing.json")
    with pytest.raises(FileNotFoundError):
        filter_by_prefix(path, "secret", "APP")
