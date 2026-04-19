import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli_quota import quota_group
from envault.vault import init_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    init_vault(str(tmp_path), "password")
    return str(tmp_path)


def test_quota_set_success(runner, vault_dir):
    result = runner.invoke(quota_group, ["set", "50", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "50" in result.output


def test_quota_set_invalid_zero(runner, vault_dir):
    result = runner.invoke(quota_group, ["set", "0", "--vault-dir", vault_dir])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_quota_get_default(runner, vault_dir):
    result = runner.invoke(quota_group, ["get", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "100" in result.output
    assert "default" in result.output


def test_quota_get_after_set(runner, vault_dir):
    runner.invoke(quota_group, ["set", "30", "--vault-dir", vault_dir])
    result = runner.invoke(quota_group, ["get", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "30" in result.output


def test_quota_remove_resets_to_default(runner, vault_dir):
    runner.invoke(quota_group, ["set", "20", "--vault-dir", vault_dir])
    result = runner.invoke(quota_group, ["remove", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    result2 = runner.invoke(quota_group, ["get", "--vault-dir", vault_dir])
    assert "100" in result2.output


def test_quota_check_within(runner, vault_dir):
    runner.invoke(quota_group, ["set", "100", "--vault-dir", vault_dir])
    result = runner.invoke(
        quota_group,
        ["check", "--vault-dir", vault_dir, "--password", "password"],
    )
    assert result.exit_code == 0
    assert "OK" in result.output
