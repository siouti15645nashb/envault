"""Tests for envault.cli_sensitive."""

import pytest
from click.testing import CliRunner
from envault.cli_sensitive import sensitive_group
from envault.env_sensitive import mark_sensitive


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    vf.write_text('{"salt": "abc", "variables": {}}')
    return str(vf)


def test_sensitive_add_success(runner, vault_file):
    result = runner.invoke(sensitive_group, ["add", "SECRET", "--vault", vault_file])
    assert result.exit_code == 0
    assert "SECRET" in result.output


def test_sensitive_list_empty(runner, vault_file):
    result = runner.invoke(sensitive_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No sensitive" in result.output


def test_sensitive_list_shows_key(runner, vault_file):
    mark_sensitive(vault_file, "API_TOKEN")
    result = runner.invoke(sensitive_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "API_TOKEN" in result.output


def test_sensitive_check_marked(runner, vault_file):
    mark_sensitive(vault_file, "DB_PASS")
    result = runner.invoke(sensitive_group, ["check", "DB_PASS", "--vault", vault_file])
    assert result.exit_code == 0
    assert "is sensitive" in result.output


def test_sensitive_check_not_marked(runner, vault_file):
    result = runner.invoke(sensitive_group, ["check", "PLAIN", "--vault", vault_file])
    assert result.exit_code == 0
    assert "not sensitive" in result.output


def test_sensitive_remove_success(runner, vault_file):
    mark_sensitive(vault_file, "OLD_KEY")
    result = runner.invoke(sensitive_group, ["remove", "OLD_KEY", "--vault", vault_file])
    assert result.exit_code == 0
    assert "Unmarked" in result.output


def test_sensitive_remove_not_marked_fails(runner, vault_file):
    result = runner.invoke(sensitive_group, ["remove", "GHOST", "--vault", vault_file])
    assert result.exit_code == 1
