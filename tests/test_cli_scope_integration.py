import pytest
from click.testing import CliRunner
import click
from envault.cli_scope import scope_group
from envault.vault import init_vault


def _make_main_cli():
    @click.group()
    def main():
        pass
    main.add_command(scope_group)
    return main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def main_cli():
    return _make_main_cli()


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path), "password")
    return str(tmp_path)


def test_main_cli_has_scope_command(runner, main_cli):
    result = runner.invoke(main_cli, ["scope", "--help"])
    assert result.exit_code == 0
    assert "scope" in result.output.lower()


def test_scope_set_and_get_roundtrip(runner, main_cli, vault_dir):
    runner.invoke(main_cli, ["scope", "set", "DB_URL", "staging", "--vault-dir", vault_dir])
    result = runner.invoke(main_cli, ["scope", "get", "DB_URL", "--vault-dir", vault_dir])
    assert "staging" in result.output


def test_scope_filter_via_main(runner, main_cli, vault_dir):
    runner.invoke(main_cli, ["scope", "set", "KEY1", "production", "--vault-dir", vault_dir])
    runner.invoke(main_cli, ["scope", "set", "KEY2", "local", "--vault-dir", vault_dir])
    result = runner.invoke(main_cli, ["scope", "filter", "production", "--vault-dir", vault_dir])
    assert "KEY1" in result.output
    assert "KEY2" not in result.output
