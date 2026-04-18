"""Access control: restrict which users/roles can read or write a variable."""

import json
from pathlib import Path

ACCESS_FILENAME = ".envault_access.json"


class AccessError(Exception):
    pass


def _access_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ACCESS_FILENAME


def _load_access(vault_dir: str) -> dict:
    p = _access_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_access(vault_dir: str, data: dict) -> None:
    p = _access_path(vault_dir)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_access(vault_dir: str, key: str, readers: list[str], writers: list[str]) -> None:
    """Set read/write access lists for a variable key."""
    if not key:
        raise AccessError("Key must not be empty.")
    data = _load_access(vault_dir)
    data[key] = {"readers": sorted(set(readers)), "writers": sorted(set(writers))}
    _save_access(vault_dir, data)


def get_access(vault_dir: str, key: str) -> dict:
    """Return access entry for key, or empty readers/writers if not set."""
    data = _load_access(vault_dir)
    return data.get(key, {"readers": [], "writers": []})


def remove_access(vault_dir: str, key: str) -> bool:
    """Remove access entry for key. Returns True if removed, False if not found."""
    data = _load_access(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_access(vault_dir, data)
    return True


def list_access(vault_dir: str) -> dict:
    """Return all access entries."""
    return _load_access(vault_dir)


def can_read(vault_dir: str, key: str, user: str) -> bool:
    entry = get_access(vault_dir, key)
    readers = entry.get("readers", [])
    return not readers or user in readers


def can_write(vault_dir: str, key: str, user: str) -> bool:
    entry = get_access(vault_dir, key)
    writers = entry.get("writers", [])
    return not writers or user in writers
