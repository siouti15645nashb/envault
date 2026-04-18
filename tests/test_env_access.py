import pytest
import json
from pathlib import Path
from envault.env_access import (
    ACCESS_FILENAME, _access_path, _load_access, set_access, get_access,
    remove_access, list_access, can_read, can_write, AccessError
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_access_filename_constant():
    assert ACCESS_FILENAME == ".envault_access.json"


def test_access_path_returns_correct_path(vault_dir):
    p = _access_path(vault_dir)
    assert p.name == ACCESS_FILENAME


def test_list_access_empty_when_no_file(vault_dir):
    assert list_access(vault_dir) == {}


def test_set_access_creates_file(vault_dir):
    set_access(vault_dir, "DB_PASS", ["alice"], ["bob"])
    assert _access_path(vault_dir).exists()


def test_set_access_stores_correct_data(vault_dir):
    set_access(vault_dir, "DB_PASS", ["alice", "carol"], ["bob"])
    entry = get_access(vault_dir, "DB_PASS")
    assert "alice" in entry["readers"]
    assert "carol" in entry["readers"]
    assert entry["writers"] == ["bob"]


def test_set_access_deduplicates(vault_dir):
    set_access(vault_dir, "KEY", ["alice", "alice"], ["bob", "bob"])
    entry = get_access(vault_dir, "KEY")
    assert entry["readers"].count("alice") == 1


def test_get_access_default_when_not_set(vault_dir):
    entry = get_access(vault_dir, "MISSING")
    assert entry == {"readers": [], "writers": []}


def test_remove_access_returns_true(vault_dir):
    set_access(vault_dir, "KEY", ["alice"], [])
    assert remove_access(vault_dir, "KEY") is True


def test_remove_access_returns_false_when_missing(vault_dir):
    assert remove_access(vault_dir, "GHOST") is False


def test_remove_access_deletes_entry(vault_dir):
    set_access(vault_dir, "KEY", ["alice"], [])
    remove_access(vault_dir, "KEY")
    assert "KEY" not in list_access(vault_dir)


def test_can_read_open_when_no_readers(vault_dir):
    assert can_read(vault_dir, "KEY", "anyone") is True


def test_can_read_allowed(vault_dir):
    set_access(vault_dir, "KEY", ["alice"], [])
    assert can_read(vault_dir, "KEY", "alice") is True


def test_can_read_denied(vault_dir):
    set_access(vault_dir, "KEY", ["alice"], [])
    assert can_read(vault_dir, "KEY", "bob") is False


def test_can_write_allowed(vault_dir):
    set_access(vault_dir, "KEY", [], ["bob"])
    assert can_write(vault_dir, "KEY", "bob") is True


def test_set_access_empty_key_raises(vault_dir):
    with pytest.raises(AccessError):
        set_access(vault_dir, "", ["alice"], [])
