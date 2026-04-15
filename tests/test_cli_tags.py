"""Tests for envault/cli_tags.py"""

import pytest
from click.testing import CliRunner
from envault.vault import init_vault, set_variable
from envault.cli_tags import tags_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / ".envault"
    init_vault(str(path), "password")
    set_variable(str(path), "password", "DB_HOST", "localhost")
    set_variable(str(path), "password", "API_KEY", "secret")
    return str(path)


def test_tag_add_success(runner, vault_file):
    result = runner.invoke(tags_group, ["add", "DB_HOST", "database", "--vault", vault_file])
    assert result.exit_code == 0
    assert "added" in result.output


def test_tag_add_missing_variable(runner, vault_file):
    result = runner.invoke(tags_group, ["add", "MISSING", "sometag", "--vault", vault_file])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_tag_remove_success(runner, vault_file):
    runner.invoke(tags_group, ["add", "DB_HOST", "database", "--vault", vault_file])
    result = runner.invoke(tags_group, ["remove", "DB_HOST", "database", "--vault", vault_file])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_tag_remove_not_present(runner, vault_file):
    result = runner.invoke(tags_group, ["remove", "DB_HOST", "ghost", "--vault", vault_file])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_tag_list_empty(runner, vault_file):
    result = runner.invoke(tags_group, ["list", "DB_HOST", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_tag_list_shows_tags(runner, vault_file):
    runner.invoke(tags_group, ["add", "DB_HOST", "database", "--vault", vault_file])
    result = runner.invoke(tags_group, ["list", "DB_HOST", "--vault", vault_file])
    assert result.exit_code == 0
    assert "database" in result.output


def test_tag_find_returns_keys(runner, vault_file):
    runner.invoke(tags_group, ["add", "DB_HOST", "infra", "--vault", vault_file])
    runner.invoke(tags_group, ["add", "API_KEY", "infra", "--vault", vault_file])
    result = runner.invoke(tags_group, ["find", "infra", "--vault", vault_file])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "API_KEY" in result.output


def test_tag_find_no_match(runner, vault_file):
    result = runner.invoke(tags_group, ["find", "ghost", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No variables" in result.output


def test_tag_all_empty(runner, vault_file):
    result = runner.invoke(tags_group, ["all", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_tag_all_lists_unique(runner, vault_file):
    runner.invoke(tags_group, ["add", "DB_HOST", "infra", "--vault", vault_file])
    runner.invoke(tags_group, ["add", "API_KEY", "api", "--vault", vault_file])
    result = runner.invoke(tags_group, ["all", "--vault", vault_file])
    assert result.exit_code == 0
    assert "api" in result.output
    assert "infra" in result.output
