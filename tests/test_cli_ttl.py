"""Tests for envault/cli_ttl.py"""

import json
import pytest
from datetime import datetime, timedelta
from click.testing import CliRunner
from envault.cli_ttl import ttl_group
from envault.env_ttl import _ttl_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / ".envault"
    p.write_text('{"salt": "abc", "variables": {}}')
    return str(p)


def test_ttl_set_success(runner, vault_file):
    result = runner.invoke(ttl_group, ["set", "MY_KEY", "3600", "--vault", vault_file])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output
    assert "expires at" in result.output


def test_ttl_set_invalid_seconds(runner, vault_file):
    result = runner.invoke(ttl_group, ["set", "MY_KEY", "0", "--vault", vault_file])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_ttl_list_empty(runner, vault_file):
    result = runner.invoke(ttl_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_ttl_list_shows_entry(runner, vault_file):
    runner.invoke(ttl_group, ["set", "FOO", "60", "--vault", vault_file])
    result = runner.invoke(ttl_group, ["list", "--vault", vault_file])
    assert "FOO" in result.output


def test_ttl_remove_success(runner, vault_file):
    runner.invoke(ttl_group, ["set", "FOO", "60", "--vault", vault_file])
    result = runner.invoke(ttl_group, ["remove", "FOO", "--vault", vault_file])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_ttl_remove_missing_key(runner, vault_file):
    result = runner.invoke(ttl_group, ["remove", "NOPE", "--vault", vault_file])
    assert result.exit_code != 0


def test_ttl_check_no_expired(runner, vault_file):
    runner.invoke(ttl_group, ["set", "KEY", "3600", "--vault", vault_file])
    result = runner.invoke(ttl_group, ["check", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No expired" in result.output


def test_ttl_check_with_expired(runner, vault_file):
    past = (datetime.utcnow() - timedelta(seconds=5)).isoformat()
    ttl_path = _ttl_path(vault_file)
    with open(ttl_path, "w") as f:
        json.dump({"OLD_KEY": past}, f)
    result = runner.invoke(ttl_group, ["check", "--vault", vault_file])
    assert result.exit_code != 0
    assert "OLD_KEY" in result.output
