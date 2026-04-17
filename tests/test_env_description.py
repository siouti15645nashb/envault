"""Tests for env_description module and CLI."""

import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.env_description import (
    DESCRIPTIONS_FILENAME,
    DescriptionError,
    set_description,
    get_description,
    remove_description,
    list_descriptions,
    _descriptions_path,
)
from envault.cli_description import desc_group


@pytest.fixture
def vault_file(tmp_path):
    v = tmp_path / ".envault"
    v.write_text(json.dumps({"salt": "abc", "variables": {}}))
    return str(v)


@pytest.fixture
def runner():
    return CliRunner()


def test_descriptions_filename_constant():
    assert DESCRIPTIONS_FILENAME == ".envault_descriptions.json"


def test_descriptions_path_returns_correct_path(vault_file):
    p = _descriptions_path(vault_file)
    assert p.name == DESCRIPTIONS_FILENAME


def test_list_descriptions_empty_when_no_file(vault_file):
    assert list_descriptions(vault_file) == {}


def test_set_description_creates_file(vault_file):
    set_description(vault_file, "DB_HOST", "Database hostname")
    path = _descriptions_path(vault_file)
    assert path.exists()


def test_set_description_stores_value(vault_file):
    set_description(vault_file, "DB_HOST", "Database hostname")
    assert get_description(vault_file, "DB_HOST") == "Database hostname"


def test_get_description_returns_none_for_missing(vault_file):
    assert get_description(vault_file, "MISSING") is None


def test_set_description_empty_key_raises(vault_file):
    with pytest.raises(DescriptionError):
        set_description(vault_file, "", "some desc")


def test_set_description_empty_value_raises(vault_file):
    with pytest.raises(DescriptionError):
        set_description(vault_file, "KEY", "   ")


def test_remove_description_success(vault_file):
    set_description(vault_file, "KEY", "A description")
    remove_description(vault_file, "KEY")
    assert get_description(vault_file, "KEY") is None


def test_remove_description_missing_raises(vault_file):
    with pytest.raises(DescriptionError):
        remove_description(vault_file, "NONEXISTENT")


def test_list_descriptions_returns_all(vault_file):
    set_description(vault_file, "A", "Alpha")
    set_description(vault_file, "B", "Beta")
    result = list_descriptions(vault_file)
    assert result == {"A": "Alpha", "B": "Beta"}


def test_cli_desc_set_success(runner, vault_file):
    result = runner.invoke(desc_group, ["set", "MY_KEY", "My description", "--vault", vault_file])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output


def test_cli_desc_get_success(runner, vault_file):
    set_description(vault_file, "MY_KEY", "Hello world")
    result = runner.invoke(desc_group, ["get", "MY_KEY", "--vault", vault_file])
    assert result.exit_code == 0
    assert "Hello world" in result.output


def test_cli_desc_list_empty(runner, vault_file):
    result = runner.invoke(desc_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No descriptions" in result.output


def test_cli_desc_remove_missing_exits_nonzero(runner, vault_file):
    result = runner.invoke(desc_group, ["remove", "GHOST", "--vault", vault_file])
    assert result.exit_code == 1
