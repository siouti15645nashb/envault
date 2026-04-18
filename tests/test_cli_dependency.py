import pytest
from click.testing import CliRunner
from envault.cli_dependency import dependency_group
from envault.vault import init_vault, set_variable
from envault.env_dependency import add_dependency
import envault.cli_dependency as cli_dep_module


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path, monkeypatch):
    vf = str(tmp_path / ".envault")
    init_vault(vf, "secret")
    monkeypatch.setattr(cli_dep_module, "VAULT_FILE", vf)
    return vf


def test_dependency_add_success(runner, vault_file):
    result = runner.invoke(dependency_group, ["add", "DB_URL", "DB_HOST"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "DB_HOST" in result.output


def test_dependency_add_self_fails(runner, vault_file):
    result = runner.invoke(dependency_group, ["add", "KEY", "KEY"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_dependency_remove_success(runner, vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    result = runner.invoke(dependency_group, ["remove", "DB_URL", "DB_HOST"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_dependency_list_empty(runner, vault_file):
    result = runner.invoke(dependency_group, ["list"])
    assert result.exit_code == 0
    assert "No dependencies" in result.output


def test_dependency_list_shows_entries(runner, vault_file):
    add_dependency(vault_file, "APP", "HOST")
    result = runner.invoke(dependency_group, ["list"])
    assert "APP" in result.output
    assert "HOST" in result.output


def test_dependency_list_single_key(runner, vault_file):
    add_dependency(vault_file, "APP", "HOST")
    result = runner.invoke(dependency_group, ["list", "APP"])
    assert "HOST" in result.output


def test_dependency_check_all_resolved(runner, vault_file):
    set_variable(vault_file, "secret", "DB_HOST", "localhost")
    set_variable(vault_file, "secret", "DB_URL", "postgres://localhost")
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    result = runner.invoke(dependency_group, ["check"], input="secret\n")
    assert result.exit_code == 0
    assert "resolved" in result.output


def test_dependency_check_missing(runner, vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    result = runner.invoke(dependency_group, ["check"], input="secret\n")
    assert result.exit_code != 0
    assert "MISSING" in result.output
