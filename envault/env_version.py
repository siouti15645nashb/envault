"""Variable versioning: track value history per key."""
import json
import os
from datetime import datetime, timezone

VERSION_FILENAME = ".envault_versions.json"


class VersionError(Exception):
    pass


def _version_path(vault_path: str) -> str:
    return os.path.join(os.path.dirname(vault_path), VERSION_FILENAME)


def _load_versions(vault_path: str) -> dict:
    path = _version_path(vault_path)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_versions(vault_path: str, data: dict) -> None:
    path = _version_path(vault_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def record_version(vault_path: str, key: str, value: str) -> None:
    """Append a new version entry for a key."""
    data = _load_versions(vault_path)
    if key not in data:
        data[key] = []
    data[key].append({
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save_versions(vault_path, data)


def get_versions(vault_path: str, key: str) -> list:
    """Return all recorded versions for a key."""
    data = _load_versions(vault_path)
    return data.get(key, [])


def get_latest_version(vault_path: str, key: str) -> dict | None:
    """Return the most recent version entry for a key, or None."""
    versions = get_versions(vault_path, key)
    return versions[-1] if versions else None


def clear_versions(vault_path: str, key: str) -> int:
    """Remove all version history for a key. Returns number of entries removed."""
    data = _load_versions(vault_path)
    removed = len(data.pop(key, []))
    _save_versions(vault_path, data)
    return removed


def list_versioned_keys(vault_path: str) -> list:
    """Return all keys that have version history."""
    return list(_load_versions(vault_path).keys())
