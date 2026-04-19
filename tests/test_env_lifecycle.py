"""Tests for env_lifecycle module."""

import pytest
from pathlib import Path
from envault.env_lifecycle import (
    LIFECYCLE_FILENAME, VALID_STATES,
    set_lifecycle, get_lifecycle, remove_lifecycle,
    list_lifecycle, filter_by_state, LifecycleError,
    _lifecycle_path
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_lifecycle_filename_constant():
    assert LIFECYCLE_FILENAME == ".envault_lifecycle.json"


def test_valid_states_includes_common():
    for s in ["active", "deprecated", "archived", "draft", "retired"]:
        assert s in VALID_STATES


def test_lifecycle_path_returns_correct_path(vault_dir):
    p = _lifecycle_path(vault_dir)
    assert p == Path(vault_dir) / LIFECYCLE_FILENAME


def test_list_lifecycle_empty_when_no_file(vault_dir):
    assert list_lifecycle(vault_dir) == {}


def test_set_lifecycle_creates_file(vault_dir):
    set_lifecycle(vault_dir, "MY_VAR", "active")
    assert (Path(vault_dir) / LIFECYCLE_FILENAME).exists()


def test_set_lifecycle_stores_state(vault_dir):
    set_lifecycle(vault_dir, "MY_VAR", "deprecated")
    data = list_lifecycle(vault_dir)
    assert data["MY_VAR"] == "deprecated"


def test_get_lifecycle_returns_active_by_default(vault_dir):
    assert get_lifecycle(vault_dir, "MISSING") == "active"


def test_get_lifecycle_after_set(vault_dir):
    set_lifecycle(vault_dir, "KEY", "archived")
    assert get_lifecycle(vault_dir, "KEY") == "archived"


def test_set_lifecycle_invalid_state_raises(vault_dir):
    with pytest.raises(LifecycleError):
        set_lifecycle(vault_dir, "KEY", "unknown_state")


def test_remove_lifecycle_removes_entry(vault_dir):
    set_lifecycle(vault_dir, "KEY", "draft")
    remove_lifecycle(vault_dir, "KEY")
    assert "KEY" not in list_lifecycle(vault_dir)


def test_remove_lifecycle_nonexistent_is_noop(vault_dir):
    remove_lifecycle(vault_dir, "NONEXISTENT")


def test_filter_by_state_returns_matching(vault_dir):
    set_lifecycle(vault_dir, "A", "active")
    set_lifecycle(vault_dir, "B", "retired")
    set_lifecycle(vault_dir, "C", "active")
    result = filter_by_state(vault_dir, "active")
    assert set(result) == {"A", "C"}


def test_filter_by_state_invalid_raises(vault_dir):
    with pytest.raises(LifecycleError):
        filter_by_state(vault_dir, "bogus")
