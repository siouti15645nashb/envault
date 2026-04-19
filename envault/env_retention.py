import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

RETENTION_FILENAME = ".envault_retention.json"


class RetentionError(Exception):
    pass


def _retention_path(vault_dir: str) -> str:
    return os.path.join(vault_dir, RETENTION_FILENAME)


def _load_retention(vault_dir: str) -> Dict[str, int]:
    path = _retention_path(vault_dir)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_retention(vault_dir: str, data: Dict[str, int]) -> None:
    path = _retention_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_retention(vault_dir: str, key: str, days: int) -> None:
    """Set a retention period (in days) for a variable."""
    if days <= 0:
        raise RetentionError("Retention days must be a positive integer.")
    data = _load_retention(vault_dir)
    data[key] = days
    _save_retention(vault_dir, data)


def remove_retention(vault_dir: str, key: str) -> None:
    """Remove the retention policy for a variable."""
    data = _load_retention(vault_dir)
    if key not in data:
        raise RetentionError(f"No retention policy set for '{key}'.")
    del data[key]
    _save_retention(vault_dir, data)


def get_retention(vault_dir: str, key: str) -> Optional[int]:
    """Return retention days for a key, or None if not set."""
    return _load_retention(vault_dir).get(key)


def list_retention(vault_dir: str) -> Dict[str, int]:
    """Return all retention policies."""
    return _load_retention(vault_dir)


def get_expiring_keys(vault_dir: str, created_at: Dict[str, str]) -> List[str]:
    """Return keys whose retention period has elapsed based on provided creation timestamps."""
    retention = _load_retention(vault_dir)
    expired = []
    now = datetime.utcnow()
    for key, days in retention.items():
        if key in created_at:
            try:
                created = datetime.fromisoformat(created_at[key])
                if now - created > timedelta(days=days):
                    expired.append(key)
            except ValueError:
                pass
    return expired
