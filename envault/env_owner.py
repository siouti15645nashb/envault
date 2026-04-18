"""Ownership tracking for vault variables."""

import json
import os
from pathlib import Path

OWNER_FILENAME = ".envault_owners.json"


class OwnerError(Exception):
    pass


def _owner_path(vault_path: str) -> Path:
    return Path(vault_path).parent / OWNER_FILENAME


def _load_owners(vault_path: str) -> dict:
    p = _owner_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_owners(vault_path: str, data: dict) -> None:
    with open(_owner_path(vault_path), "w") as f:
        json.dump(data, f, indent=2)


def set_owner(vault_path: str, key: str, owner: str) -> None:
    """Assign an owner to a variable."""
    if not owner or not owner.strip():
        raise OwnerError("Owner must not be empty.")
    data = _load_owners(vault_path)
    data[key] = owner.strip()
    _save_owners(vault_path, data)


def get_owner(vault_path: str, key: str) -> str | None:
    """Return the owner of a variable, or None."""
    return _load_owners(vault_path).get(key)


def remove_owner(vault_path: str, key: str) -> bool:
    """Remove ownership for a variable. Returns True if removed."""
    data = _load_owners(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_owners(vault_path, data)
    return True


def list_owners(vault_path: str) -> dict:
    """Return all key -> owner mappings."""
    return dict(_load_owners(vault_path))
