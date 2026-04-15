"""Integration tests wiring lint_group into the main CLI."""

import pytest
from click.testing import CliRunner

from envault.cli import cli
from envault.vault import init_vault, set_variable


@pytest.fixture(autouse=True)
def _register_lint_group():
    """Ensure lint group is attached to main CLI for integration tests."""
    from envault.cli_lint import lint_group
    if "lint" not in [cmd.name for cmd in cli.commands.values()]:
        cli.add_command(lint_group)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "password")
    return path


def test_main_cli_has_lint_command(runner):
    result = runner.invoke(cli, ["--help"])
    assert "lint" in result.output


def test_main_cli_lint_check_clean(runner, vault_file):
    set_variable(vault_file, "password", "APP_PORT", "8080")
    result = runner.invoke(
        cli, ["lint", "check", vault_file, "--password", "password"]
    )
    assert result.exit_code == 0
    assert "No lint issues" in result.output


def test_main_cli_lint_check_detects_errors(runner, vault_file):
    set_variable(vault_file, "password", "app-port", "8080")
    result = runner.invoke(
        cli, ["lint", "check", vault_file, "--password", "password"]
    )
    assert result.exit_code != 0


def test_main_cli_lint_rules(runner):
    result = runner.invoke(cli, ["lint", "rules"])
    assert result.exit_code == 0
    assert "naming" in result.output
