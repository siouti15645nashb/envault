"""Tests for envault/cli_search.py."""

import pytest
from click.testing import CliRunner

from envault.vault import init_vault, set_variable
from envault.cli_search import search_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "pass")
    set_variable(path, "pass", "DB_HOST", "localhost")
    set_variable(path, "pass", "DB_PORT", "5432")
    set_variable(path, "pass", "APP_DEBUG", "true")
    return path


def test_cmd_find_returns_matches(runner, vault_file):
    result = runner.invoke(
        search_group, ["find", "DB", "--vault", vault_file, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "DB_PORT=5432" in result.output
    assert "APP_DEBUG" not in result.output


def test_cmd_find_no_match(runner, vault_file):
    result = runner.invoke(
        search_group, ["find", "MISSING", "--vault", vault_file, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "No variables matching" in result.output


def test_cmd_find_no_vault(runner, tmp_path):
    path = str(tmp_path / "missing.json")
    result = runner.invoke(
        search_group, ["find", "DB", "--vault", path, "--password", "pass"]
    )
    assert result.exit_code != 0
    assert "vault not found" in result.output.lower() or "vault not found" in (result.output + (result.exception or ""))


def test_cmd_prefix_returns_matches(runner, vault_file):
    result = runner.invoke(
        search_group, ["prefix", "APP", "--vault", vault_file, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "APP_DEBUG=true" in result.output
    assert "DB_HOST" not in result.output


def test_cmd_prefix_no_match(runner, vault_file):
    result = runner.invoke(
        search_group, ["prefix", "REDIS", "--vault", vault_file, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "No variables with prefix" in result.output


def test_cmd_prefix_no_vault(runner, tmp_path):
    path = str(tmp_path / "missing.json")
    result = runner.invoke(
        search_group, ["prefix", "APP", "--vault", path, "--password", "pass"]
    )
    assert result.exit_code != 0


def test_cmd_find_case_insensitive_default(runner, vault_file):
    result = runner.invoke(
        search_group, ["find", "db", "--vault", vault_file, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_cmd_find_case_sensitive_no_match(runner, vault_file):
    result = runner.invoke(
        search_group,
        ["find", "db", "--vault", vault_file, "--password", "pass", "--case-sensitive"],
    )
    assert result.exit_code == 0
    assert "No variables matching" in result.output


def test_cmd_prefix_case_insensitive_default(runner, vault_file):
    """Prefix search should match regardless of case by default."""
    result = runner.invoke(
        search_group, ["prefix", "app", "--vault", vault_file, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "APP_DEBUG=true" in result.output
    assert "DB_HOST" not in result.output
