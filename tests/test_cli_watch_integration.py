"""Integration tests: cli_watch registered on main CLI."""

import pytest
from click.testing import CliRunner
import click
from envault.cli_watch import watch_group


@pytest.fixture
def main_cli():
    @click.group()
    def cli():
        pass
    cli.add_command(watch_group)
    return cli


@pytest.fixture
def runner():
    return CliRunner()


def test_main_cli_has_watch_command(runner, main_cli):
    result = runner.invoke(main_cli, ["--help"])
    assert "watch" in result.output


def test_watch_group_has_start_subcommand(runner, main_cli):
    result = runner.invoke(main_cli, ["watch", "--help"])
    assert "start" in result.output


def test_watch_start_help(runner, main_cli):
    result = runner.invoke(main_cli, ["watch", "start", "--help"])
    assert result.exit_code == 0
    assert "VAULT_PATH" in result.output
    assert "--interval" in result.output
