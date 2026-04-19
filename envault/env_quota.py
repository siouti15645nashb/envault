import json
from pathlib import Path

QUOTA_FILENAME = ".envault_quota.json"
DEFAULT_MAX_KEYS = 100


class QuotaError(Exception):
    pass


def _quota_path(vault_dir: str) -> Path:
    return Path(vault_dir) / QUOTA_FILENAME


def _load_quota(vault_dir: str) -> dict:
    p = _quota_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_quota(vault_dir: str, data: dict) -> None:
    p = _quota_path(vault_dir)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_quota(vault_dir: str, max_keys: int) -> None:
    if max_keys < 1:
        raise QuotaError("max_keys must be at least 1")
    data = _load_quota(vault_dir)
    data["max_keys"] = max_keys
    _save_quota(vault_dir, data)


def get_quota(vault_dir: str) -> int:
    data = _load_quota(vault_dir)
    return data.get("max_keys", DEFAULT_MAX_KEYS)


def remove_quota(vault_dir: str) -> None:
    data = _load_quota(vault_dir)
    data.pop("max_keys", None)
    _save_quota(vault_dir, data)


def check_quota(vault_dir: str, current_key_count: int) -> bool:
    """Returns True if within quota, False if exceeded."""
    return current_key_count <= get_quota(vault_dir)
