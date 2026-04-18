import pytest
from click.testing import CliRunner
from envault.cli_severity import severity_group
from envault.env_severity import set_severity


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_severity_set_success(runner, vault_dir):
    result = runner.invoke(severity_group, ["set", "API_KEY", "high", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "high" in result.output


def test_severity_get_after_set(runner, vault_dir):
    set_severity(vault_dir, "DB_PASS", "critical")
    result = runner.invoke(severity_group, ["get", "DB_PASS", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "critical" in result.output


def test_severity_get_not_set(runner, vault_dir):
    result = runner.invoke(severity_group, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No severity" in result.output


def test_severity_remove_success(runner, vault_dir):
    set_severity(vault_dir, "TOKEN", "medium")
    result = runner.invoke(severity_group, ["remove", "TOKEN", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_severity_remove_missing_fails(runner, vault_dir):
    result = runner.invoke(severity_group, ["remove", "GHOST", "--vault-dir", vault_dir])
    assert result.exit_code == 1


def test_severity_list_empty(runner, vault_dir):
    result = runner.invoke(severity_group, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No severity" in result.output


def test_severity_list_shows_entries(runner, vault_dir):
    set_severity(vault_dir, "KEY_A", "low")
    set_severity(vault_dir, "KEY_B", "high")
    result = runner.invoke(severity_group, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_severity_find_returns_matches(runner, vault_dir):
    set_severity(vault_dir, "SEC_KEY", "critical")
    set_severity(vault_dir, "LOG_LEVEL", "low")
    result = runner.invoke(severity_group, ["find", "critical", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "SEC_KEY" in result.output
    assert "LOG_LEVEL" not in result.output


def test_severity_find_no_match(runner, vault_dir):
    result = runner.invoke(severity_group, ["find", "medium", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No variables" in result.output
