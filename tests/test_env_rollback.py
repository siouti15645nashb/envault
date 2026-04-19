import pytest
import os
from click.testing import CliRunner
from envault.vault import init_vault, set_variable, get_variable
from envault.env_rollback import (
    create_snapshot, list_snapshots, rollback_to, delete_snapshot,
    RollbackError, ROLLBACK_FILENAME, _rollback_path
)


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    init_vault(path, "password123")
    return path


def test_rollback_filename_constant():
    assert ROLLBACK_FILENAME == ".envault_rollback.json"


def test_rollback_path_returns_correct_path(vault_file, tmp_path):
    p = _rollback_path(vault_file)
    assert p.parent == tmp_path
    assert p.name == ROLLBACK_FILENAME


def test_list_snapshots_empty_when_no_file(vault_file):
    assert list_snapshots(vault_file) == []


def test_create_snapshot_returns_dict(vault_file):
    snap = create_snapshot(vault_file, label="initial")
    assert isinstance(snap, dict)
    assert "timestamp" in snap
    assert snap["label"] == "initial"


def test_create_snapshot_stores_variables(vault_file):
    set_variable(vault_file, "password123", "KEY", "value")
    create_snapshot(vault_file, label="with-key")
    snapshots = list_snapshots(vault_file)
    assert len(snapshots) == 1
    assert "KEY" in snapshots[0]["variables"]


def test_multiple_snapshots_accumulate(vault_file):
    create_snapshot(vault_file)
    create_snapshot(vault_file)
    assert len(list_snapshots(vault_file)) == 2


def test_rollback_to_restores_variables(vault_file):
    set_variable(vault_file, "password123", "ALPHA", "hello")
    create_snapshot(vault_file)
    set_variable(vault_file, "password123", "ALPHA", "changed")
    rollback_to(vault_file, 0, "password123")
    assert get_variable(vault_file, "password123", "ALPHA") == "hello"


def test_rollback_to_invalid_index_raises(vault_file):
    create_snapshot(vault_file)
    with pytest.raises(RollbackError):
        rollback_to(vault_file, 99, "password123")


def test_rollback_to_empty_raises(vault_file):
    with pytest.raises(RollbackError):
        rollback_to(vault_file, 0, "password123")


def test_delete_snapshot_removes_entry(vault_file):
    create_snapshot(vault_file, label="a")
    create_snapshot(vault_file, label="b")
    delete_snapshot(vault_file, 0)
    snaps = list_snapshots(vault_file)
    assert len(snaps) == 1
    assert snaps[0]["label"] == "b"


def test_delete_snapshot_invalid_index_raises(vault_file):
    create_snapshot(vault_file)
    with pytest.raises(RollbackError):
        delete_snapshot(vault_file, 5)
