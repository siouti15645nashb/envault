"""Tests for envault/cli_visibility.py"""

import json
import pytest
from click.testing import CliRunner
from envault.cli_visibility import visibility_group
from envault.env_visibility import set_visibility


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    vf.write_text(json.dumps({"salt": "abc", "variables": {}}))
    return str(vf)


def test_visibility_set_success(runner, vault_file):
    result = runner.invoke(visibility_group, ["set", "API_KEY", "secret", "--vault", vault_file])
    assert result.exit_code == 0
    assert "secret" in result.output


def test_visibility_get_default(runner, vault_file):
    result = runner.invoke(visibility_group, ["get", "MISSING", "--vault", vault_file])
    assert result.exit_code == 0
    assert "private" in result.output


def test_visibility_get_after_set(runner, vault_file):
    set_visibility(vault_file, "TOKEN", "public")
    result = runner.invoke(visibility_group, ["get", "TOKEN", "--vault", vault_file])
    assert "public" in result.output


def test_visibility_list_empty(runner, vault_file):
    result = runner.invoke(visibility_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No visibility" in result.output


def test_visibility_list_shows_entries(runner, vault_file):
    set_visibility(vault_file, "DB_HOST", "public")
    set_visibility(vault_file, "DB_PASS", "secret")
    result = runner.invoke(visibility_group, ["list", "--vault", vault_file])
    assert "DB_HOST" in result.output
    assert "DB_PASS" in result.output


def test_visibility_remove_success(runner, vault_file):
    set_visibility(vault_file, "KEY", "secret")
    result = runner.invoke(visibility_group, ["remove", "KEY", "--vault", vault_file])
    assert result.exit_code == 0
    result2 = runner.invoke(visibility_group, ["get", "KEY", "--vault", vault_file])
    assert "private" in result2.output


def test_visibility_filter_returns_matches(runner, vault_file):
    set_visibility(vault_file, "PUB", "public")
    set_visibility(vault_file, "SEC", "secret")
    result = runner.invoke(visibility_group, ["filter", "public", "--vault", vault_file])
    assert "PUB" in result.output
    assert "SEC" not in result.output


def test_visibility_filter_no_matches(runner, vault_file):
    result = runner.invoke(visibility_group, ["filter", "secret", "--vault", vault_file])
    assert "No variables" in result.output
