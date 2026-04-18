import pytest
from click.testing import CliRunner
import click
from envault.cli_dependency import dependency_group
from envault.vault import init_vault
import envault.cli_dependency as cli_dep_module


def _make_main_cli():
    @click.group()
    def main():
        pass
    main.add_command(dependency_group)
    return main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def main_cli():
    return _make_main_cli()


@pytest.fixture
def vault_file(tmp_path, monkeypatch):
    vf = str(tmp_path / ".envault")
    init_vault(vf, "secret")
    monkeypatch.setattr(cli_dep_module, "VAULT_FILE", vf)
    return vf


def test_main_cli_has_dependency_command(runner, main_cli):
    result = runner.invoke(main_cli, ["--help"])
    assert "dependency" in result.output


def test_dependency_group_has_subcommands(runner, main_cli):
    result = runner.invoke(main_cli, ["dependency", "--help"])
    for cmd in ("add", "remove", "list", "check"):
        assert cmd in result.output


def test_add_and_list_roundtrip(runner, main_cli, vault_file):
    runner.invoke(main_cli, ["dependency", "add", "X", "Y"])
    result = runner.invoke(main_cli, ["dependency", "list", "X"])
    assert "Y" in result.output
