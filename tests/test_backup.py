"""Tests for envault.backup module."""

import pytest
from pathlib import Path

from envault.backup import (
    BackupError,
    BACKUP_EXTENSION,
    create_backup,
    list_backups,
    restore_backup,
    delete_backup,
)


@pytest.fixture
def vault_file(tmp_path):
    """Create a minimal vault file for testing."""
    path = tmp_path / "envault.json"
    path.write_text('{"salt": "abc", "variables": {}}')
    return path


def test_create_backup_returns_path(vault_file):
    backup = create_backup(vault_file)
    assert isinstance(backup, Path)
    assert backup.exists()


def test_create_backup_has_correct_extension(vault_file):
    backup = create_backup(vault_file)
    assert backup.suffix == BACKUP_EXTENSION


def test_create_backup_content_matches(vault_file):
    backup = create_backup(vault_file)
    assert backup.read_text() == vault_file.read_text()


def test_create_backup_raises_if_no_vault(tmp_path):
    missing = tmp_path / "missing.json"
    with pytest.raises(BackupError, match="Vault not found"):
        create_backup(missing)


def test_list_backups_empty_when_none(vault_file):
    assert list_backups(vault_file) == []


def test_list_backups_returns_created_backups(vault_file):
    b1 = create_backup(vault_file)
    b2 = create_backup(vault_file)
    backups = list_backups(vault_file)
    assert b1 in backups
    assert b2 in backups
    assert len(backups) == 2


def test_list_backups_are_sorted(vault_file):
    create_backup(vault_file)
    create_backup(vault_file)
    backups = list_backups(vault_file)
    assert backups == sorted(backups)


def test_restore_backup_overwrites_vault(vault_file):
    backup = create_backup(vault_file)
    vault_file.write_text('{"salt": "xyz", "variables": {"A": "1"}}')
    restore_backup(backup, vault_file)
    assert vault_file.read_text() == backup.read_text()


def test_restore_backup_raises_if_missing(tmp_path, vault_file):
    missing_backup = tmp_path / "ghost.bak"
    with pytest.raises(BackupError, match="Backup not found"):
        restore_backup(missing_backup, vault_file)


def test_delete_backup_removes_file(vault_file):
    backup = create_backup(vault_file)
    assert not backup.exists()


def test_delete_backup_raises_if_missing(tmp_path):
    missing = tmp_path / "ghost.bak"
    with pytest.raises(BackupError, match="Backup not found"):
        delete_backup(missing)
