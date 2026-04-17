"""TTL (time-to-live) support for environment variables."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

TTL_FILENAME = ".envault_ttl.json"


class TTLError(Exception):
    pass


def _ttl_path(vault_path: str) -> str:
    return os.path.join(os.path.dirname(vault_path), TTL_FILENAME)


def _load_ttl(vault_path: str) -> Dict[str, str]:
    path = _ttl_path(vault_path)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_ttl(vault_path: str, data: Dict[str, str]) -> None:
    with open(_ttl_path(vault_path), "w") as f:
        json.dump(data, f, indent=2)


def set_ttl(vault_path: str, key: str, seconds: int) -> datetime:
    """Set a TTL for a key. Returns the expiry datetime."""
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    data = _load_ttl(vault_path)
    expiry = datetime.utcnow() + timedelta(seconds=seconds)
    data[key] = expiry.isoformat()
    _save_ttl(vault_path, data)
    return expiry


def remove_ttl(vault_path: str, key: str) -> None:
    data = _load_ttl(vault_path)
    if key not in data:
        raise TTLError(f"No TTL set for '{key}'.")
    del data[key]
    _save_ttl(vault_path, data)


def is_expired(vault_path: str, key: str) -> bool:
    data = _load_ttl(vault_path)
    if key not in data:
        return False
    return datetime.utcnow() > datetime.fromisoformat(data[key])


def list_ttl(vault_path: str) -> Dict[str, str]:
    return _load_ttl(vault_path)


def get_expired_keys(vault_path: str) -> List[str]:
    data = _load_ttl(vault_path)
    now = datetime.utcnow()
    return [k for k, v in data.items() if now > datetime.fromisoformat(v)]
