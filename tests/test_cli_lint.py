"""Tests for envault.cli_lint CLI commands."""

import pytest
from click.testing import CliRunner

from envault.cli_lint import lint_group
from envault.vault import init_vault, set_variable


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "password")
    return path


def test_lint_check_clean_vault(runner, vault_file):
    set_variable(vault_file, "password", "DATABASE_URL", "postgres://localhost")
    result = runner.invoke(
        lint_group, ["check", vault_file, "--password", "password"]
    )
    assert result.exit_code == 0
    assert "No lint issues" in result.output


def test_lint_check_bad_name_exits_nonzero(runner, vault_file):
    set_variable(vault_file, "password", "badName", "value")
    result = runner.invoke(
        lint_group, ["check", vault_file, "--password", "password"]
    )
    assert result.exit_code != 0
    assert "ERROR" in result.output
    assert "badName" in result.output


def test_lint_check_warning_exits_zero_without_strict(runner, vault_file):
    set_variable(vault_file, "password", "EMPTY_VAR", "")
    result = runner.invoke(
        lint_group, ["check", vault_file, "--password", "password"]
    )
    assert result.exit_code == 0
    assert "WARNING" in result.output


def test_lint_check_warning_exits_nonzero_with_strict(runner, vault_file):
    set_variable(vault_file, "password", "EMPTY_VAR", "")
    result = runner.invoke(
        lint_group, ["check", vault_file, "--password", "password", "--strict"]
    )
    assert result.exit_code != 0


def test_lint_check_no_vault(runner, tmp_path):
    missing = str(tmp_path / "missing")
    result = runner.invoke(
        lint_group, ["check", missing, "--password", "password"]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_lint_rules_lists_rules(runner):
    result = runner.invoke(lint_group, ["rules"])
    assert result.exit_code == 0
    assert "naming" in result.output
    assert "empty_value" in result.output
    assert "whitespace" in result.output
    assert "duplicate_prefix" in result.output


def test_lint_check_shows_error_and_warning_counts(runner, vault_file):
    set_variable(vault_file, "password", "badName", "")
    result = runner.invoke(
        lint_group, ["check", vault_file, "--password", "password"]
    )
    assert "error(s)" in result.output
    assert "warning(s)" in result.output
