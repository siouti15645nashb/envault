"""Read-only variable protection for envault."""

import json
from pathlib import Path

READONLY_FILENAME = ".envault_readonly"


class ReadonlyError(Exception):
    pass


def _readonly_path(vault_path: str) -> Path:
    return Path(vault_path).parent / READONLY_FILENAME


def _load_readonly(vault_path: str) -> list:
    p = _readonly_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_readonly(vault_path: str, keys: list) -> None:
    p = _readonly_path(vault_path)
    p.write_text(json.dumps(sorted(set(keys)), indent=2))


def mark_readonly(vault_path: str, key: str) -> None:
    """Mark a variable as read-only."""
    from envault.vault import list_variables
    keys = list_variables(vault_path, password="")
    # just check key exists by loading raw
    from envault.vault import _load_raw
    data = _load_raw(vault_path)
    # key existence will be validated at set-time; we just record it
    current = _load_readonly(vault_path)
    if key not in current:
        current.append(key)
    _save_readonly(vault_path, current)


def unmark_readonly(vault_path: str, key: str) -> None:
    """Remove read-only protection from a variable."""
    current = _load_readonly(vault_path)
    current = [k for k in current if k != key]
    _save_readonly(vault_path, current)


def is_readonly(vault_path: str, key: str) -> bool:
    """Return True if the variable is marked read-only."""
    return key in _load_readonly(vault_path)


def list_readonly(vault_path: str) -> list:
    """Return all read-only variable keys."""
    return _load_readonly(vault_path)


def assert_writable(vault_path: str, key: str) -> None:
    """Raise ReadonlyError if key is read-only."""
    if is_readonly(vault_path, key):
        raise ReadonlyError(f"Variable '{key}' is read-only and cannot be modified.")
