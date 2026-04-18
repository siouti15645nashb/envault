import pytest
import json
from pathlib import Path
from envault.env_dependency import (
    DEPENDENCY_FILENAME,
    _dependency_path,
    add_dependency,
    remove_dependency,
    get_dependencies,
    list_all_dependencies,
    check_missing,
    DependencyError,
)
from envault.vault import init_vault


@pytest.fixture
def vault_file(tmp_path):
    vf = str(tmp_path / ".envault")
    init_vault(vf, "secret")
    return vf


def test_dependency_filename_constant():
    assert DEPENDENCY_FILENAME == ".envault_dependencies.json"


def test_dependency_path_returns_correct_path(vault_file):
    p = _dependency_path(vault_file)
    assert p.name == DEPENDENCY_FILENAME


def test_list_dependencies_empty_when_no_file(vault_file):
    assert list_all_dependencies(vault_file) == {}


def test_add_dependency_creates_file(vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    p = _dependency_path(vault_file)
    assert p.exists()


def test_add_dependency_stores_entry(vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    deps = get_dependencies(vault_file, "DB_URL")
    assert "DB_HOST" in deps


def test_add_dependency_idempotent(vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    deps = get_dependencies(vault_file, "DB_URL")
    assert deps.count("DB_HOST") == 1


def test_add_multiple_dependencies(vault_file):
    add_dependency(vault_file, "APP_URL", "HOST")
    add_dependency(vault_file, "APP_URL", "PORT")
    deps = get_dependencies(vault_file, "APP_URL")
    assert "HOST" in deps
    assert "PORT" in deps


def test_add_self_dependency_raises(vault_file):
    with pytest.raises(DependencyError):
        add_dependency(vault_file, "KEY", "KEY")


def test_remove_dependency(vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    remove_dependency(vault_file, "DB_URL", "DB_HOST")
    deps = get_dependencies(vault_file, "DB_URL")
    assert "DB_HOST" not in deps


def test_remove_last_dependency_cleans_key(vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    remove_dependency(vault_file, "DB_URL", "DB_HOST")
    data = list_all_dependencies(vault_file)
    assert "DB_URL" not in data


def test_check_missing_all_present(vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    result = check_missing(vault_file, ["DB_HOST", "DB_URL"])
    assert result == {}


def test_check_missing_reports_absent(vault_file):
    add_dependency(vault_file, "DB_URL", "DB_HOST")
    result = check_missing(vault_file, ["DB_URL"])
    assert "DB_URL" in result
    assert "DB_HOST" in result["DB_URL"]
