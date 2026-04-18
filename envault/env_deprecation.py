"""Track deprecated environment variables with optional replacement hints."""

import json
from pathlib import Path

DEPRECATION_FILENAME = ".envault_deprecations.json"


class DeprecationError(Exception):
    pass


def _deprecation_path(vault_dir: str) -> Path:
    return Path(vault_dir) / DEPRECATION_FILENAME


def _load_deprecations(vault_dir: str) -> dict:
    path = _deprecation_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_deprecations(vault_dir: str, data: dict) -> None:
    path = _deprecation_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def mark_deprecated(vault_dir: str, key: str, replacement: str = None) -> None:
    """Mark a variable as deprecated with an optional replacement key."""
    if not key:
        raise DeprecationError("Key must not be empty.")
    data = _load_deprecations(vault_dir)
    data[key] = {"replacement": replacement}
    _save_deprecations(vault_dir, data)


def unmark_deprecated(vault_dir: str, key: str) -> None:
    """Remove deprecation marking from a variable."""
    data = _load_deprecations(vault_dir)
    if key not in data:
        raise DeprecationError(f"Key '{key}' is not marked as deprecated.")
    del data[key]
    _save_deprecations(vault_dir, data)


def is_deprecated(vault_dir: str, key: str) -> bool:
    return key in _load_deprecations(vault_dir)


def list_deprecated(vault_dir: str) -> dict:
    """Return all deprecated keys with their replacement hints."""
    return _load_deprecations(vault_dir)
