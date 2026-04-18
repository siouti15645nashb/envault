"""Tests for envault/cli_validation.py"""

import pytest
from click.testing import CliRunner
from envault.cli_validation import validation_group
from envault.vault import init_vault, set_variable


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "password")
    set_variable(path, "password", "PORT", "8080")
    set_variable(path, "password", "API_URL", "https://api.example.com")
    set_variable(path, "password", "EMPTY_VAR", "")
    return path


def test_validate_run_no_rules_exits_nonzero(runner, vault_file):
    result = runner.invoke(validation_group, ["run", vault_file, "password"])
    assert result.exit_code != 0
    assert "No rules specified" in result.output


def test_validate_run_all_pass(runner, vault_file):
    result = runner.invoke(validation_group, ["run", vault_file, "password", "--rule", "nonempty"])
    # EMPTY_VAR will fail
    assert "FAIL" in result.output


def test_validate_run_numeric_pass(runner, vault_file):
    result = runner.invoke(validation_group, ["run", vault_file, "password", "--rule", "numeric"])
    assert "PORT" in result.output


def test_validate_run_unknown_rule_exits_nonzero(runner, vault_file):
    result = runner.invoke(validation_group, ["run", vault_file, "password", "--rule", "fake_rule"])
    assert result.exit_code != 0
    assert "Validation error" in result.output


def test_validate_run_missing_vault_exits_nonzero(runner, tmp_path):
    path = str(tmp_path / "missing.json")
    result = runner.invoke(validation_group, ["run", path, "password", "--rule", "nonempty"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_validate_rules_lists_rules(runner):
    result = runner.invoke(validation_group, ["rules"])
    assert result.exit_code == 0
    assert "nonempty" in result.output
    assert "numeric" in result.output
    assert "url" in result.output
