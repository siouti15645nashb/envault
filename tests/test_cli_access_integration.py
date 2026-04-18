"""Integration test: access_group registered on a main CLI."""

import pytest
import click
from click.testing import CliRunner
from envault.cli_access import access_group
from envault.env_access import set_access


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def main_cli():
    @click.group()
    def cli():
        pass
    cli.add_command(access_group, name="access")
    return cli


def test_main_cli_has_access_command(runner, main_cli):
    result = runner.invoke(main_cli, ["--help"])
    assert "access" in result.output


def test_access_set_and_list_roundtrip(runner, main_cli, tmp_path):
    vault_dir = str(tmp_path)
    result = runner.invoke(
        main_cli,
        ["access", "set", "SECRET", "--reader", "alice", "--writer", "carol", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0

    result = runner.invoke(main_cli, ["access", "list", "--vault-dir", vault_dir])
    assert "SECRET" in result.output
    assert "alice" in result.output
    assert "carol" in result.output


def test_access_set_and_remove_roundtrip(runner, main_cli, tmp_path):
    vault_dir = str(tmp_path)
    runner.invoke(
        main_cli,
        ["access", "set", "KEY", "--reader", "bob", "--vault-dir", vault_dir]
    )
    result = runner.invoke(main_cli, ["access", "remove", "KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output

    result = runner.invoke(main_cli, ["access", "list", "--vault-dir", vault_dir])
    assert "No access entries" in result.output
