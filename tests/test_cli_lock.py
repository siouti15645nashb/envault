"""Tests for envault/cli_lock.py"""

import pytest
from click.testing import CliRunner
from envault.cli_lock import lock_group
from envault.env_lock import lock_variable


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    v = tmp_path / ".envault"
    v.write_text('{"salt": "abc", "variables": {}}')
    return str(v)


def test_lock_add_success(runner, vault_file):
    result = runner.invoke(lock_group, ["add", "API_KEY", "--vault", vault_file])
    assert result.exit_code == 0
    assert "locked" in result.output


def test_lock_add_idempotent(runner, vault_file):
    runner.invoke(lock_group, ["add", "API_KEY", "--vault", vault_file])
    result = runner.invoke(lock_group, ["add", "API_KEY", "--vault", vault_file])
    assert result.exit_code == 0


def test_lock_remove_success(runner, vault_file):
    lock_variable(vault_file, "API_KEY")
    result = runner.invoke(lock_group, ["remove", "API_KEY", "--vault", vault_file])
    assert result.exit_code == 0
    assert "unlocked" in result.output


def test_lock_remove_not_locked_fails(runner, vault_file):
    result = runner.invoke(lock_group, ["remove", "MISSING", "--vault", vault_file])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_lock_list_empty(runner, vault_file):
    result = runner.invoke(lock_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No locked" in result.output


def test_lock_list_shows_locked_keys(runner, vault_file):
    lock_variable(vault_file, "DB_PASS")
    lock_variable(vault_file, "API_KEY")
    result = runner.invoke(lock_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output
    assert "API_KEY" in result.output
