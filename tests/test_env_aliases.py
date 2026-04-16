"""Tests for envault.env_aliases and cli_aliases."""

import pytest
from click.testing import CliRunner
from envault.env_aliases import (
    ALIASES_FILENAME,
    AliasError,
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
)
from envault.cli_aliases import alias_group


@pytest.fixture
def vault_file(tmp_path):
    v = tmp_path / ".envault"
    v.write_text('{"salt": "abc", "variables": {}}')
    return str(v)


@pytest.fixture
def runner():
    return CliRunner()


def test_aliases_filename_constant():
    assert ALIASES_FILENAME == ".envault_aliases.json"


def test_list_aliases_empty_when_no_file(vault_file):
    assert list_aliases(vault_file) == {}


def test_add_alias_creates_entry(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    assert list_aliases(vault_file)["db"] == "DATABASE_URL"


def test_add_alias_empty_name_raises(vault_file):
    with pytest.raises(AliasError):
        add_alias(vault_file, "", "DATABASE_URL")


def test_add_alias_empty_key_raises(vault_file):
    with pytest.raises(AliasError):
        add_alias(vault_file, "db", "")


def test_resolve_alias_returns_key(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    assert resolve_alias(vault_file, "db") == "DATABASE_URL"


def test_resolve_missing_alias_raises(vault_file):
    with pytest.raises(AliasError):
        resolve_alias(vault_file, "missing")


def test_remove_alias_success(vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    remove_alias(vault_file, "db")
    assert "db" not in list_aliases(vault_file)


def test_remove_missing_alias_raises(vault_file):
    with pytest.raises(AliasError):
        remove_alias(vault_file, "nope")


def test_cli_alias_add_success(runner, vault_file):
    result = runner.invoke(alias_group, ["add", "db", "DATABASE_URL", "--vault", vault_file])
    assert result.exit_code == 0
    assert "db" in result.output


def test_cli_alias_list(runner, vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    result = runner.invoke(alias_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "db -> DATABASE_URL" in result.output


def test_cli_alias_resolve(runner, vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    result = runner.invoke(alias_group, ["resolve", "db", "--vault", vault_file])
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output


def test_cli_alias_remove(runner, vault_file):
    add_alias(vault_file, "db", "DATABASE_URL")
    result = runner.invoke(alias_group, ["remove", "db", "--vault", vault_file])
    assert result.exit_code == 0
    assert list_aliases(vault_file) == {}
