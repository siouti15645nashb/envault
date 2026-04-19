"""Tests for cli_lifecycle commands."""

import pytest
from click.testing import CliRunner
from envault.cli_lifecycle import lifecycle_group
from envault.env_lifecycle import set_lifecycle


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_lifecycle_set_success(runner, vault_dir):
    result = runner.invoke(lifecycle_group, ["set", "MY_VAR", "deprecated", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "deprecated" in result.output


def test_lifecycle_get_default(runner, vault_dir):
    result = runner.invoke(lifecycle_group, ["get", "MISSING", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "active" in result.output


def test_lifecycle_get_after_set(runner, vault_dir):
    set_lifecycle(vault_dir, "KEY", "archived")
    result = runner.invoke(lifecycle_group, ["get", "KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "archived" in result.output


def test_lifecycle_list_empty(runner, vault_dir):
    result = runner.invoke(lifecycle_group, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No lifecycle" in result.output


def test_lifecycle_list_shows_entries(runner, vault_dir):
    set_lifecycle(vault_dir, "A", "draft")
    set_lifecycle(vault_dir, "B", "retired")
    result = runner.invoke(lifecycle_group, ["list", "--vault-dir", vault_dir])
    assert "A" in result.output
    assert "draft" in result.output


def test_lifecycle_remove_success(runner, vault_dir):
    set_lifecycle(vault_dir, "KEY", "active")
    result = runner.invoke(lifecycle_group, ["remove", "KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0


def test_lifecycle_filter_returns_matching(runner, vault_dir):
    set_lifecycle(vault_dir, "X", "retired")
    set_lifecycle(vault_dir, "Y", "active")
    result = runner.invoke(lifecycle_group, ["filter", "retired", "--vault-dir", vault_dir])
    assert "X" in result.output
    assert "Y" not in result.output


def test_lifecycle_filter_empty_state(runner, vault_dir):
    result = runner.invoke(lifecycle_group, ["filter", "draft", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No variables" in result.output
