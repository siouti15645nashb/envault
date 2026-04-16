"""Manage default values for environment variables."""

import json
from pathlib import Path
from typing import Dict, Optional

DEFAULTS_FILENAME = ".envault_defaults.json"


class DefaultsError(Exception):
    pass


def _defaults_path(vault_dir: str) -> Path:
    return Path(vault_dir) / DEFAULTS_FILENAME


def _load_defaults(vault_dir: str) -> Dict[str, str]:
    p = _defaults_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_defaults(vault_dir: str, data: Dict[str, str]) -> None:
    p = _defaults_path(vault_dir)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_default(vault_dir: str, key: str, value: str) -> None:
    """Set a default value for a variable."""
    if not key:
        raise DefaultsError("Key must not be empty.")
    defaults = _load_defaults(vault_dir)
    defaults[key] = value
    _save_defaults(vault_dir, defaults)


def remove_default(vault_dir: str, key: str) -> None:
    """Remove a default value."""
    defaults = _load_defaults(vault_dir)
    if key not in defaults:
        raise DefaultsError(f"No default set for '{key}'.")
    del defaults[key]
    _save_defaults(vault_dir, defaults)


def get_default(vault_dir: str, key: str) -> Optional[str]:
    """Return the default value for a key, or None."""
    return _load_defaults(vault_dir).get(key)


def list_defaults(vault_dir: str) -> Dict[str, str]:
    """Return all defaults."""
    return _load_defaults(vault_dir)


def apply_defaults(vault_dir: str, variables: Dict[str, str]) -> Dict[str, str]:
    """Return variables with defaults filled in for missing keys."""
    defaults = _load_defaults(vault_dir)
    result = dict(variables)
    for key, value in defaults.items():
        if key not in result:
            result[key] = value
    return result
