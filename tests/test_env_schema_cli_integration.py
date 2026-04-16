import pytest
from click.testing import CliRunner
from click import Group
from envault.vault import init_vault, set_variable
from envault.env_schema_cli import schema_group
import click


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "pass")
    set_variable(path, "pass", "REQUIRED_VAR", "value")
    return path


@click.group()
def main_cli():
    pass


main_cli.add_command(schema_group)


def test_main_cli_has_schema_command(runner):
    result = runner.invoke(main_cli, ["--help"])
    assert "schema" in result.output


def test_schema_define_and_validate_roundtrip(runner, vault_file):
    result = runner.invoke(schema_group, ["define", "REQUIRED_VAR", vault_file])
    assert result.exit_code == 0

    result = runner.invoke(schema_group, ["validate", vault_file, "pass"])
    assert result.exit_code == 0


def test_schema_full_workflow(runner, vault_file):
    runner.invoke(schema_group, ["define", "REQUIRED_VAR", vault_file])
    runner.invoke(schema_group, ["define", "OPTIONAL_VAR", "--optional", vault_file])

    result = runner.invoke(schema_group, ["list", vault_file])
    assert "REQUIRED_VAR" in result.output
    assert "OPTIONAL_VAR" in result.output

    result = runner.invoke(schema_group, ["validate", vault_file, "pass"])
    assert result.exit_code == 0

    result = runner.invoke(schema_group, ["remove", "OPTIONAL_VAR", vault_file])
    assert result.exit_code == 0

    result = runner.invoke(schema_group, ["list", vault_file])
    assert "OPTIONAL_VAR" not in result.output
