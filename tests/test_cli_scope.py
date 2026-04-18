import pytest
from click.testing import CliRunner
from envault.cli_scope import scope_group
from envault.env_scope import set_scope
from envault.vault import init_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path), "password")
    return str(tmp_path)


def test_scope_set_success(runner, vault_dir):
    result = runner.invoke(scope_group, ["set", "DB_HOST", "production", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "production" in result.output


def test_scope_set_invalid(runner, vault_dir):
    result = runner.invoke(scope_group, ["set", "KEY", "invalid_scope", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_scope_get_default(runner, vault_dir):
    result = runner.invoke(scope_group, ["get", "UNSET_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "global" in result.output


def test_scope_get_after_set(runner, vault_dir):
    set_scope(vault_dir, "API", "staging")
    result = runner.invoke(scope_group, ["get", "API", "--vault-dir", vault_dir])
    assert "staging" in result.output


def test_scope_list_empty(runner, vault_dir):
    result = runner.invoke(scope_group, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No scopes" in result.output


def test_scope_list_shows_entries(runner, vault_dir):
    set_scope(vault_dir, "X", "local")
    result = runner.invoke(scope_group, ["list", "--vault-dir", vault_dir])
    assert "X" in result.output
    assert "local" in result.output


def test_scope_remove_success(runner, vault_dir):
    set_scope(vault_dir, "Y", "development")
    result = runner.invoke(scope_group, ["remove", "Y", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_scope_filter_returns_matches(runner, vault_dir):
    set_scope(vault_dir, "A", "production")
    set_scope(vault_dir, "B", "local")
    result = runner.invoke(scope_group, ["filter", "production", "--vault-dir", vault_dir])
    assert "A" in result.output
    assert "B" not in result.output
