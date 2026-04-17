"""Track which variables are required and validate their presence in the vault."""

import json
from pathlib import Path
from typing import List

REQUIRED_FILENAME = ".envault_required"


class RequiredError(Exception):
    pass


def _required_path(vault_dir: str) -> Path:
    return Path(vault_dir) / REQUIRED_FILENAME


def _load_required(vault_dir: str) -> List[str]:
    path = _required_path(vault_dir)
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("required", [])


def _save_required(vault_dir: str, keys: List[str]) -> None:
    path = _required_path(vault_dir)
    with open(path, "w") as f:
        json.dump({"required": sorted(set(keys))}, f, indent=2)


def mark_required(vault_dir: str, key: str) -> None:
    keys = _load_required(vault_dir)
    if key not in keys:
        keys.append(key)
    _save_required(vault_dir, keys)


def unmark_required(vault_dir: str, key: str) -> None:
    keys = _load_required(vault_dir)
    if key not in keys:
        raise RequiredError(f"Key '{key}' is not marked as required.")
    keys.remove(key)
    _save_required(vault_dir, keys)


def list_required(vault_dir: str) -> List[str]:
    return _load_required(vault_dir)


def check_required(vault_dir: str, present_keys: List[str]) -> List[str]:
    """Return list of required keys missing from present_keys."""
    required = _load_required(vault_dir)
    return [k for k in required if k not in present_keys]
