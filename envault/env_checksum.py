"""Checksum tracking for vault variables."""

import hashlib
import json
from pathlib import Path

CHECKSUM_FILENAME = ".envault_checksums.json"


class ChecksumError(Exception):
    pass


def _checksum_path(vault_path: str) -> Path:
    return Path(vault_path).parent / CHECKSUM_FILENAME


def _load_checksums(vault_path: str) -> dict:
    path = _checksum_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_checksums(vault_path: str, data: dict) -> None:
    path = _checksum_path(vault_path)
    path.write_text(json.dumps(data, indent=2))


def _compute(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def record_checksum(vault_path: str, key: str, value: str) -> str:
    """Compute and store a checksum for the given key's value."""
    checksums = _load_checksums(vault_path)
    digest = _compute(value)
    checksums[key] = digest
    _save_checksums(vault_path, checksums)
    return digest


def verify_checksum(vault_path: str, key: str, value: str) -> bool:
    """Return True if the stored checksum matches the given value."""
    checksums = _load_checksums(vault_path)
    if key not in checksums:
        raise ChecksumError(f"No checksum recorded for '{key}'")
    return checksums[key] == _compute(value)


def remove_checksum(vault_path: str, key: str) -> None:
    """Remove the checksum entry for a key."""
    checksums = _load_checksums(vault_path)
    checksums.pop(key, None)
    _save_checksums(vault_path, checksums)


def list_checksums(vault_path: str) -> dict:
    """Return all recorded checksums."""
    return _load_checksums(vault_path)
