import pytest
import json
from pathlib import Path
from envault.env_scope import (
    SCOPE_FILENAME, VALID_SCOPES, ScopeError,
    _scope_path, set_scope, get_scope, remove_scope,
    list_scopes, filter_by_scope
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_scope_filename_constant():
    assert SCOPE_FILENAME == ".envault_scopes.json"


def test_valid_scopes_includes_common():
    for s in ["local", "development", "staging", "production", "global"]:
        assert s in VALID_SCOPES


def test_scope_path_returns_correct_path(vault_dir):
    p = _scope_path(vault_dir)
    assert p.name == SCOPE_FILENAME


def test_list_scopes_empty_when_no_file(vault_dir):
    assert list_scopes(vault_dir) == {}


def test_set_scope_creates_file(vault_dir):
    set_scope(vault_dir, "DB_HOST", "production")
    assert Path(vault_dir, SCOPE_FILENAME).exists()


def test_set_scope_stores_value(vault_dir):
    set_scope(vault_dir, "API_KEY", "staging")
    data = list_scopes(vault_dir)
    assert data["API_KEY"] == "staging"


def test_set_scope_invalid_raises(vault_dir):
    with pytest.raises(ScopeError):
        set_scope(vault_dir, "KEY", "unknown")


def test_get_scope_returns_default_global(vault_dir):
    assert get_scope(vault_dir, "MISSING") == "global"


def test_get_scope_after_set(vault_dir):
    set_scope(vault_dir, "PORT", "local")
    assert get_scope(vault_dir, "PORT") == "local"


def test_remove_scope_returns_true(vault_dir):
    set_scope(vault_dir, "KEY", "development")
    assert remove_scope(vault_dir, "KEY") is True


def test_remove_scope_deletes_entry(vault_dir):
    set_scope(vault_dir, "KEY", "development")
    remove_scope(vault_dir, "KEY")
    assert "KEY" not in list_scopes(vault_dir)


def test_remove_scope_missing_returns_false(vault_dir):
    assert remove_scope(vault_dir, "NONEXISTENT") is False


def test_filter_by_scope_returns_matching(vault_dir):
    set_scope(vault_dir, "A", "staging")
    set_scope(vault_dir, "B", "production")
    set_scope(vault_dir, "C", "staging")
    result = filter_by_scope(vault_dir, "staging")
    assert set(result) == {"A", "C"}


def test_filter_by_scope_invalid_raises(vault_dir):
    with pytest.raises(ScopeError):
        filter_by_scope(vault_dir, "badscope")


def test_filter_by_scope_empty_result(vault_dir):
    set_scope(vault_dir, "X", "local")
    assert filter_by_scope(vault_dir, "production") == []
