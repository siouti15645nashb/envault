"""Variable expiry/TTL management for envault."""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

EXPIRY_FILENAME = ".envault_expiry.json"


class ExpiryError(Exception):
    pass


def _expiry_path(vault_dir: str) -> str:
    return os.path.join(vault_dir, EXPIRY_FILENAME)


def _load_expiry(vault_dir: str) -> Dict[str, str]:
    path = _expiry_path(vault_dir)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_expiry(vault_dir: str, data: Dict[str, str]) -> None:
    with open(_expiry_path(vault_dir), "w") as f:
        json.dump(data, f, indent=2)


def set_expiry(vault_dir: str, key: str, expires_at: datetime) -> None:
    """Set an expiry datetime (UTC) for a variable."""
    data = _load_expiry(vault_dir)
    data[key] = expires_at.astimezone(timezone.utc).isoformat()
    _save_expiry(vault_dir, data)


def remove_expiry(vault_dir: str, key: str) -> None:
    """Remove expiry for a variable."""
    data = _load_expiry(vault_dir)
    if key not in data:
        raise ExpiryError(f"No expiry set for '{key}'.")
    del data[key]
    _save_expiry(vault_dir, data)


def get_expiry(vault_dir: str, key: str) -> Optional[datetime]:
    """Return expiry datetime for key, or None."""
    data = _load_expiry(vault_dir)
    if key not in data:
        return None
    return datetime.fromisoformat(data[key])


def list_expiring(vault_dir: str) -> Dict[str, datetime]:
    """Return all keys with their expiry datetimes."""
    data = _load_expiry(vault_dir)
    return {k: datetime.fromisoformat(v) for k, v in data.items()}


def get_expired(vault_dir: str) -> List[str]:
    """Return list of keys whose expiry has passed."""
    now = datetime.now(timezone.utc)
    return [
        key for key, exp in list_expiring(vault_dir).items()
        if exp <= now
    ]
