"""Integration tests: lifecycle group registered on main CLI."""

import pytest
from click.testing import CliRunner
from click import Group
import click
from envault.cli_lifecycle import lifecycle_group


def _make_main_cli():
    @click.group()
    def main():
        pass
    main.add_command(lifecycle_group)
    return main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def main_cli():
    return _make_main_cli()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_main_cli_has_lifecycle_command(runner, main_cli):
    result = runner.invoke(main_cli, ["--help"])
    assert "lifecycle" in result.output


def test_lifecycle_set_and_get_roundtrip(runner, main_cli, vault_dir):
    result = runner.invoke(main_cli, ["lifecycle", "set", "DB_URL", "active", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    result = runner.invoke(main_cli, ["lifecycle", "get", "DB_URL", "--vault-dir", vault_dir])
    assert "active" in result.output


def test_lifecycle_filter_integration(runner, main_cli, vault_dir):
    runner.invoke(main_cli, ["lifecycle", "set", "A", "archived", "--vault-dir", vault_dir])
    runner.invoke(main_cli, ["lifecycle", "set", "B", "active", "--vault-dir", vault_dir])
    result = runner.invoke(main_cli, ["lifecycle", "filter", "archived", "--vault-dir", vault_dir])
    assert "A" in result.output
    assert "B" not in result.output
