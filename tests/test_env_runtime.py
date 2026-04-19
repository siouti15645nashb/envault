"""Tests for envault.env_runtime."""

import pytest
from click.testing import CliRunner
from envault.env_runtime import (
    RUNTIME_FILENAME, VALID_TARGETS, RuntimeError,
    set_runtime, get_runtime, remove_runtime, list_runtime, filter_by_target,
    _runtime_path
)
from envault.cli_runtime import runtime_group


@pytest.fixture
def vault_dir(tmp_path):
    from envault.vault import init_vault
    init_vault(str(tmp_path), "password")
    return str(tmp_path)


def test_runtime_filename_constant():
    assert RUNTIME_FILENAME == ".envault_runtime.json"


def test_valid_targets_includes_common():
    for t in ["process", "docker", "kubernetes"]:
        assert t in VALID_TARGETS


def test_runtime_path_returns_correct_path(vault_dir, tmp_path):
    p = _runtime_path(vault_dir)
    assert p.name == RUNTIME_FILENAME
    assert str(tmp_path) in str(p)


def test_list_runtime_empty_when_no_file(vault_dir):
    assert list_runtime(vault_dir) == {}


def test_set_runtime_creates_file(vault_dir, tmp_path):
    set_runtime(vault_dir, "DB_HOST", "docker")
    assert _runtime_path(vault_dir).exists()


def test_set_runtime_stores_target(vault_dir):
    set_runtime(vault_dir, "DB_HOST", "docker")
    assert get_runtime(vault_dir, "DB_HOST") == "docker"


def test_get_runtime_none_when_not_set(vault_dir):
    assert get_runtime(vault_dir, "MISSING") is None


def test_set_runtime_invalid_target_raises(vault_dir):
    with pytest.raises(RuntimeError, match="Invalid target"):
        set_runtime(vault_dir, "KEY", "invalid_target")


def test_remove_runtime_deletes_entry(vault_dir):
    set_runtime(vault_dir, "API_KEY", "lambda")
    remove_runtime(vault_dir, "API_KEY")
    assert get_runtime(vault_dir, "API_KEY") is None


def test_remove_runtime_nonexistent_raises(vault_dir):
    with pytest.raises(RuntimeError):
        remove_runtime(vault_dir, "GHOST")


def test_filter_by_target(vault_dir):
    set_runtime(vault_dir, "DB", "docker")
    set_runtime(vault_dir, "CACHE", "docker")
    set_runtime(vault_dir, "API", "lambda")
    result = filter_by_target(vault_dir, "docker")
    assert set(result) == {"DB", "CACHE"}


def test_cli_set_success(vault_dir):
    runner = CliRunner()
    result = runner.invoke(runtime_group, ["set", "MY_KEY", "kubernetes", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "kubernetes" in result.output


def test_cli_set_invalid_target(vault_dir):
    runner = CliRunner()
    result = runner.invoke(runtime_group, ["set", "MY_KEY", "bad", "--vault-dir", vault_dir])
    assert result.exit_code != 0


def test_cli_list_empty(vault_dir):
    runner = CliRunner()
    result = runner.invoke(runtime_group, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No runtime" in result.output


def test_cli_targets_lists_all():
    runner = CliRunner()
    result = runner.invoke(runtime_group, ["targets"])
    assert result.exit_code == 0
    for t in VALID_TARGETS:
        assert t in result.output
