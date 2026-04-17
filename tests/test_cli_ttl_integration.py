"""Integration tests: TTL group registered on main CLI."""

import pytest
from click.testing import CliRunner
from click import Group
import click
from envault.cli_ttl import ttl_group


def _make_main_cli():
    @click.group()
    def main():
        pass
    main.add_command(ttl_group)
    return main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def main_cli():
    return _make_main_cli()


def test_main_cli_has_ttl_command(runner, main_cli):
    result = runner.invoke(main_cli, ["--help"])
    assert "ttl" in result.output


def test_ttl_group_has_set_subcommand(runner, main_cli):
    result = runner.invoke(main_cli, ["ttl", "--help"])
    assert "set" in result.output


def test_ttl_group_has_check_subcommand(runner, main_cli):
    result = runner.invoke(main_cli, ["ttl", "--help"])
    assert "check" in result.output


def test_ttl_set_and_list_roundtrip(runner, main_cli, tmp_path):
    vault = str(tmp_path / ".envault")
    (tmp_path / ".envault").write_text('{"salt": "x", "variables": {}}')
    runner.invoke(main_cli, ["ttl", "set", "API_KEY", "7200", "--vault", vault])
    result = runner.invoke(main_cli, ["ttl", "list", "--vault", vault])
    assert "API_KEY" in result.output
