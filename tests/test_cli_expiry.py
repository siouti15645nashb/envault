"""Tests for envault.cli_expiry commands."""

import os
from datetime import datetime, timezone, timedelta

import pytest
from click.testing import CliRunner

from envault.cli_expiry import expiry_group
from envault.env_expiry import set_expiry, _expiry_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    vault_file = tmp_path / ".envault.json"
    vault_file.write_text('{"salt": "abc", "variables": {}}')
    return tmp_path


def test_expiry_set_success(runner, vault_dir):
    vault = str(vault_dir / ".envault.json")
    result = runner.invoke(expiry_group, ["set", "API_KEY", "2025-12-31T00:00:00", "--vault", vault])
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_expiry_set_invalid_datetime(runner, vault_dir):
    vault = str(vault_dir / ".envault.json")
    result = runner.invoke(expiry_group, ["set", "API_KEY", "not-a-date", "--vault", vault])
    assert result.exit_code != 0


def test_expiry_set_updates_existing(runner, vault_dir):
    """Setting expiry on a key that already has one should update it."""
    vault = str(vault_dir / ".envault.json")
    vault_dir_str = str(vault_dir)
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    set_expiry(vault_dir_str, "API_KEY", dt)
    result = runner.invoke(expiry_group, ["set", "API_KEY", "2026-06-15T12:00:00", "--vault", vault])
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_expiry_remove_success(runner, vault_dir):
    vault = str(vault_dir / ".envault.json")
    vault_dir_str = str(vault_dir)
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    set_expiry(vault_dir_str, "TOKEN", dt)
    result = runner.invoke(expiry_group, ["remove", "TOKEN", "--vault", vault])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_expiry_remove_nonexistent(runner, vault_dir):
    vault = str(vault_dir / ".envault.json")
    result = runner.invoke(expiry_group, ["remove", "GHOST", "--vault", vault])
    assert result.exit_code != 0


def test_expiry_list_empty(runner, vault_dir):
    vault = str(vault_dir / ".envault.json")
    result = runner.invoke(expiry_group, ["list", "--vault", vault])
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_expiry_list_shows_entries(runner, vault_dir):
    vault = str(vault_dir / ".envault.json")
    dt = datetime(2026, 3, 1, tzinfo=timezone.utc)
    set_expiry(str(vault_dir), "DB_PASS", dt)
    result = runner.invoke(expiry_group, ["list", "--vault", vault])
    assert result.exit_code == 0
    assert "DB_PASS" in result.output


def test_expiry_check_no_expired(runner, vault_dir):
    vault = str(vault_dir / ".envault.json")
    future = datetime.now(timezone.utc) + timedelta(days=10)
    set_expiry(str(vault_dir), "SAFE_KEY", future)
    result = runner.invoke(expiry_group, ["check", "--vault", vault])
    assert result.exit_code == 0


def test_expiry_check_with_expired_exits_nonzero(runner, vault_dir):
    vault = str(vault_dir / ".envault.json")
    past = datetime.now(timezone.utc) - timedelta(days=1)
    set_expiry(str(vault_dir), "OLD_KEY", past)
    result = runner.invoke(expiry_group, ["check", "--vault", vault])
    assert result.exit_code != 0
    assert "OLD_KEY" in result.output
