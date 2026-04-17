"""Tests for envault.env_priority module."""

import pytest
from click.testing import CliRunner
from envault.vault import init_vault, set_variable
from envault.env_priority import (
    PRIORITY_FILENAME, _priority_path, set_priority, get_priority,
    remove_priority, list_priorities, get_by_level, PriorityError
)
from envault.cli_priority import priority_group


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "secret")
    set_variable(path, "secret", "DB_URL", "postgres://localhost/db")
    set_variable(path, "secret", "API_KEY", "abc123")
    return path


def test_priority_filename_constant():
    assert PRIORITY_FILENAME == ".envault_priority.json"


def test_priority_path_returns_correct_path(vault_file, tmp_path):
    p = _priority_path(vault_file)
    assert p.name == PRIORITY_FILENAME
    assert p.parent == tmp_path


def test_list_priorities_empty_when_no_file(vault_file):
    assert list_priorities(vault_file) == {}


def test_set_priority_creates_file(vault_file, tmp_path):
    set_priority(vault_file, "DB_URL", "high")
    assert (tmp_path / PRIORITY_FILENAME).exists()


def test_set_priority_stores_level(vault_file):
    set_priority(vault_file, "DB_URL", "critical")
    assert get_priority(vault_file, "DB_URL") == "critical"


def test_get_priority_default_is_normal(vault_file):
    assert get_priority(vault_file, "MISSING_KEY") == "normal"


def test_set_priority_invalid_level_raises(vault_file):
    with pytest.raises(PriorityError):
        set_priority(vault_file, "DB_URL", "urgent")


def test_remove_priority(vault_file):
    set_priority(vault_file, "API_KEY", "high")
    remove_priority(vault_file, "API_KEY")
    assert get_priority(vault_file, "API_KEY") == "normal"


def test_remove_priority_nonexistent_key_is_noop(vault_file):
    remove_priority(vault_file, "NONEXISTENT")


def test_get_by_level_returns_matching_keys(vault_file):
    set_priority(vault_file, "DB_URL", "high")
    set_priority(vault_file, "API_KEY", "low")
    result = get_by_level(vault_file, "high")
    assert result == ["DB_URL"]


def test_get_by_level_invalid_raises(vault_file):
    with pytest.raises(PriorityError):
        get_by_level(vault_file, "extreme")


def test_cli_set_and_list(vault_file):
    runner = CliRunner()
    result = runner.invoke(priority_group, ["set", "DB_URL", "critical", "--vault", vault_file])
    assert result.exit_code == 0
    assert "critical" in result.output
    result = runner.invoke(priority_group, ["list", "--vault", vault_file])
    assert "DB_URL" in result.output
    assert "critical" in result.output


def test_cli_find(vault_file):
    runner = CliRunner()
    runner.invoke(priority_group, ["set", "API_KEY", "high", "--vault", vault_file])
    result = runner.invoke(priority_group, ["find", "high", "--vault", vault_file])
    assert "API_KEY" in result.output
