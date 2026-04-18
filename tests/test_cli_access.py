import pytest
from click.testing import CliRunner
from envault.cli_access import access_group
from envault.env_access import set_access


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_access_set_success(runner, vault_dir):
    result = runner.invoke(
        access_group, ["set", "DB_PASS", "--reader", "alice", "--writer", "bob", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "Access set for 'DB_PASS'" in result.output


def test_access_get_default(runner, vault_dir):
    result = runner.invoke(access_group, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "(all)" in result.output


def test_access_get_after_set(runner, vault_dir):
    set_access(vault_dir, "API_KEY", ["alice"], ["bob"])
    result = runner.invoke(access_group, ["get", "API_KEY", "--vault-dir", vault_dir])
    assert "alice" in result.output
    assert "bob" in result.output


def test_access_remove_success(runner, vault_dir):
    set_access(vault_dir, "KEY", ["alice"], [])
    result = runner.invoke(access_group, ["remove", "KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_access_remove_missing(runner, vault_dir):
    result = runner.invoke(access_group, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No access entry" in result.output


def test_access_list_empty(runner, vault_dir):
    result = runner.invoke(access_group, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No access entries" in result.output


def test_access_list_shows_entries(runner, vault_dir):
    set_access(vault_dir, "DB_URL", ["alice"], ["bob"])
    result = runner.invoke(access_group, ["list", "--vault-dir", vault_dir])
    assert "DB_URL" in result.output
    assert "alice" in result.output
