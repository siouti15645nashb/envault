"""Backup and restore support for envault vaults."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

BACKUP_EXTENSION = ".bak"
BACKUP_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


class BackupError(Exception):
    """Raised when a backup or restore operation fails."""


def _backup_filename(vault_path: Path, timestamp: str) -> Path:
    """Return a timestamped backup filename next to the vault."""
    name = f"{vault_path.stem}_{timestamp}{BACKUP_EXTENSION}"
    return vault_path.parent / name


def create_backup(vault_path: Path) -> Path:
    """Copy the vault file to a timestamped backup.

    Returns the path of the created backup file.
    Raises BackupError if the vault does not exist.
    """
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise BackupError(f"Vault not found: {vault_path}")

    timestamp = datetime.utcnow().strftime(BACKUP_TIMESTAMP_FORMAT)
    backup_path = _backup_filename(vault_path, timestamp)
    shutil.copy2(vault_path, backup_path)
    return backup_path


def list_backups(vault_path: Path) -> list[Path]:
    """Return a sorted list of backup files for the given vault."""
    vault_path = Path(vault_path)
    parent = vault_path.parent
    stem = vault_path.stem
    backups = sorted(
        p for p in parent.glob(f"{stem}_*{BACKUP_EXTENSION}")
    )
    return backups


def restore_backup(backup_path: Path, vault_path: Path) -> None:
    """Overwrite the vault with the contents of a backup file.

    Raises BackupError if the backup does not exist.
    """
    backup_path = Path(backup_path)
    vault_path = Path(vault_path)
    if not backup_path.exists():
        raise BackupError(f"Backup not found: {backup_path}")
    shutil.copy2(backup_path, vault_path)


def delete_backup(backup_path: Path) -> None:
    """Delete a single backup file.

    Raises BackupError if the file does not exist.
    """
    backup_path = Path(backup_path)
    if not backup_path.exists():
        raise BackupError(f"Backup not found: {backup_path}")
    backup_path.unlink()
