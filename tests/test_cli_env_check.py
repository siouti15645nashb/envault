"""Tests for envault.cli_env_check."""

import pytest
from click.testing import CliRunner

from envault.vault import init_vault, set_variable
from envault.cli_env_check import env_check_group

PASSWORD = "test-password"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, PASSWORD)
    set_variable(path, PASSWORD, "DB_HOST", "localhost")
    set_variable(path, PASSWORD, "DB_PORT", "5432")
    return path


def invoke_env_check(runner, vault_file, extra_args=None, env=None):
    """Helper to invoke the env_check_group 'run' command with common defaults."""
    args = ["run", "--vault", vault_file, "--password", PASSWORD]
    if extra_args:
        args.extend(extra_args)
    return runner.invoke(env_check_group, args, env=env)


def test_run_all_matched(runner, vault_file):
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "ENVAULT_PASSWORD": PASSWORD}
    result = invoke_env_check(runner, vault_file, env=env)
    assert result.exit_code == 0
    assert "matched" in result.output


def test_run_missing_key(runner, vault_file):
    env = {"DB_HOST": "localhost", "ENVAULT_PASSWORD": PASSWORD}  # DB_PORT missing
    result = invoke_env_check(runner, vault_file, env=env)
    assert result.exit_code == 0  # not strict
    assert "MISSING" in result.output
    assert "DB_PORT" in result.output


def test_run_strict_exits_nonzero_on_issue(runner, vault_file):
    env = {"ENVAULT_PASSWORD": PASSWORD}
    result = invoke_env_check(runner, vault_file, extra_args=["--strict"], env=env)
    assert result.exit_code != 0


def test_run_mismatch_reported(runner, vault_file):
    env = {"DB_HOST": "wronghost", "DB_PORT": "5432", "ENVAULT_PASSWORD": PASSWORD}
    result = invoke_env_check(runner, vault_file, env=env)
    assert "MISMATCH" in result.output
    assert "DB_HOST" in result.output


def test_run_no_vault(runner, tmp_path):
    missing = str(tmp_path / "nonexistent.envault")
    result = runner.invoke(
        env_check_group, ["run", "--vault", missing, "--password", PASSWORD]
    )
    assert result.exit_code != 0


def test_show_extra_flag(runner, vault_file):
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "UNRELATED": "x", "ENVAULT_PASSWORD": PASSWORD}
    result = invoke_env_check(runner, vault_file, extra_args=["--show-extra"], env=env)
    assert "EXTRA" in result.output
    assert "UNRELATED" in result.output
