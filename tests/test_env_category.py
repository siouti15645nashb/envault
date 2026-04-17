"""Tests for env_category module and CLI."""
import json
import pytest
from click.testing import CliRunner
from envault.vault import init_vault, set_variable
from envault.env_category import (
    CATEGORY_FILENAME, _category_path, set_category, remove_category,
    get_category, list_categories, find_by_category, CategoryError
)
from envault.cli_category import category_group

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    vf = str(tmp_path / ".envault")
    init_vault(vf, PASSWORD)
    set_variable(vf, PASSWORD, "API_KEY", "abc123")
    set_variable(vf, PASSWORD, "DB_URL", "postgres://localhost")
    return vf


@pytest.fixture
def runner():
    return CliRunner()


def test_category_filename_constant():
    assert CATEGORY_FILENAME == ".envault_categories.json"


def test_category_path_returns_correct_path(vault_file, tmp_path):
    p = _category_path(vault_file)
    assert p.name == CATEGORY_FILENAME
    assert p.parent == tmp_path


def test_list_categories_empty_when_no_file(vault_file):
    assert list_categories(vault_file) == {}


def test_set_category_creates_file(vault_file, tmp_path):
    set_category(vault_file, "API_KEY", "auth")
    assert (tmp_path / CATEGORY_FILENAME).exists()


def test_set_category_stores_value(vault_file):
    set_category(vault_file, "API_KEY", "auth")
    assert get_category(vault_file, "API_KEY") == "auth"


def test_set_category_nonexistent_variable_raises(vault_file):
    with pytest.raises(CategoryError):
        set_category(vault_file, "MISSING", "auth")


def test_set_category_empty_name_raises(vault_file):
    with pytest.raises(CategoryError):
        set_category(vault_file, "API_KEY", "  ")


def test_remove_category_success(vault_file):
    set_category(vault_file, "API_KEY", "auth")
    remove_category(vault_file, "API_KEY")
    assert get_category(vault_file, "API_KEY") is None


def test_remove_category_not_set_raises(vault_file):
    with pytest.raises(CategoryError):
        remove_category(vault_file, "API_KEY")


def test_find_by_category(vault_file):
    set_category(vault_file, "API_KEY", "auth")
    set_category(vault_file, "DB_URL", "database")
    assert find_by_category(vault_file, "auth") == ["API_KEY"]


def test_find_by_category_case_insensitive(vault_file):
    set_category(vault_file, "API_KEY", "Auth")
    assert find_by_category(vault_file, "auth") == ["API_KEY"]


def test_cli_set_success(runner, vault_file):
    result = runner.invoke(category_group, ["set", "API_KEY", "auth", "--vault", vault_file])
    assert result.exit_code == 0
    assert "auth" in result.output


def test_cli_list(runner, vault_file):
    set_category(vault_file, "API_KEY", "auth")
    result = runner.invoke(category_group, ["list", "--vault", vault_file])
    assert "API_KEY" in result.output
    assert "auth" in result.output


def test_cli_find(runner, vault_file):
    set_category(vault_file, "DB_URL", "database")
    result = runner.invoke(category_group, ["find", "database", "--vault", vault_file])
    assert "DB_URL" in result.output
