import json
import pytest
from pathlib import Path
from envault.env_namespace import (
    NAMESPACE_FILENAME,
    NamespaceError,
    define_namespace,
    remove_namespace,
    list_namespaces,
    resolve_namespace,
    keys_in_namespace,
    _namespace_path,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_namespace_filename_constant():
    assert NAMESPACE_FILENAME == ".envault_namespaces.json"


def test_namespace_path_returns_correct_path(vault_dir):
    p = _namespace_path(vault_dir)
    assert p.name == NAMESPACE_FILENAME


def test_list_namespaces_empty_when_no_file(vault_dir):
    assert list_namespaces(vault_dir) == {}


def test_define_namespace_creates_file(vault_dir):
    define_namespace(vault_dir, "app", "APP_")
    assert Path(vault_dir, NAMESPACE_FILENAME).exists()


def test_define_namespace_stores_prefix_uppercase(vault_dir):
    define_namespace(vault_dir, "db", "db_")
    ns = list_namespaces(vault_dir)
    assert ns["db"] == "DB_"


def test_define_namespace_empty_name_raises(vault_dir):
    with pytest.raises(NamespaceError, match="name"):
        define_namespace(vault_dir, "", "APP_")


def test_define_namespace_empty_prefix_raises(vault_dir):
    with pytest.raises(NamespaceError, match="prefix"):
        define_namespace(vault_dir, "app", "")


def test_remove_namespace_success(vault_dir):
    define_namespace(vault_dir, "app", "APP_")
    remove_namespace(vault_dir, "app")
    assert "app" not in list_namespaces(vault_dir)


def test_remove_namespace_nonexistent_raises(vault_dir):
    with pytest.raises(NamespaceError, match="does not exist"):
        remove_namespace(vault_dir, "missing")


def test_resolve_namespace_matches_prefix(vault_dir):
    define_namespace(vault_dir, "app", "APP_")
    assert resolve_namespace(vault_dir, "APP_SECRET") == "app"


def test_resolve_namespace_no_match_returns_none(vault_dir):
    define_namespace(vault_dir, "app", "APP_")
    assert resolve_namespace(vault_dir, "DB_HOST") is None


def test_keys_in_namespace_filters_correctly(vault_dir):
    define_namespace(vault_dir, "db", "DB_")
    keys = ["DB_HOST", "DB_PORT", "APP_KEY", "db_user"]
    result = keys_in_namespace(vault_dir, "db", keys)
    assert "DB_HOST" in result
    assert "DB_PORT" in result
    assert "APP_KEY" not in result
    assert "db_user" in result  # case-insensitive prefix match


def test_keys_in_namespace_nonexistent_namespace_raises(vault_dir):
    with pytest.raises(NamespaceError):
        keys_in_namespace(vault_dir, "ghost", ["APP_KEY"])
