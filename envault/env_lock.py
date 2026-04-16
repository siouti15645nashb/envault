"""Lock/unlock vault variables to prevent accidental modification."""

import json
from pathlib import Path
from typing import List

LOCK_FILENAME = ".envault.lock"


class LockError(Exception):
    pass


def _lock_path(vault_path: str) -> Path:
    return Path(vault_path).parent / LOCK_FILENAME


def _load_locked(vault_path: str) -> List[str]:
    p = _lock_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_locked(vault_path: str, keys: List[str]) -> None:
    _lock_path(vault_path).write_text(json.dumps(sorted(set(keys)), indent=2))


def lock_variable(vault_path: str, key: str) -> None:
    """Mark a variable as locked."""
    keys = _load_locked(vault_path)
    if key not in keys:
        keys.append(key)
    _save_locked(vault_path, keys)


def unlock_variable(vault_path: str, key: str) -> None:
    """Remove lock from a variable."""
    keys = _load_locked(vault_path)
    if key not in keys:
        raise LockError(f"Variable '{key}' is not locked.")
    keys.remove(key)
    _save_locked(vault_path, keys)


def is_locked(vault_path: str, key: str) -> bool:
    return key in _load_locked(vault_path)


def get_locked(vault_path: str) -> List[str]:
    return _load_locked(vault_path)


def assert_not_locked(vault_path: str, key: str) -> None:
    if is_locked(vault_path, key):
        raise LockError(f"Variable '{key}' is locked and cannot be modified.")
