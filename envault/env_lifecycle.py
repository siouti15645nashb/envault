"""Lifecycle state management for environment variables."""

import json
from pathlib import Path

LIFECYCLE_FILENAME = ".envault_lifecycle.json"
VALID_STATES = ["active", "deprecated", "archived", "draft", "retired"]


class LifecycleError(Exception):
    pass


def _lifecycle_path(vault_dir: str) -> Path:
    return Path(vault_dir) / LIFECYCLE_FILENAME


def _load_lifecycle(vault_dir: str) -> dict:
    p = _lifecycle_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_lifecycle(vault_dir: str, data: dict) -> None:
    p = _lifecycle_path(vault_dir)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_lifecycle(vault_dir: str, key: str, state: str) -> None:
    if state not in VALID_STATES:
        raise LifecycleError(f"Invalid state '{state}'. Valid: {VALID_STATES}")
    data = _load_lifecycle(vault_dir)
    data[key] = state
    _save_lifecycle(vault_dir, data)


def get_lifecycle(vault_dir: str, key: str) -> str:
    data = _load_lifecycle(vault_dir)
    return data.get(key, "active")


def remove_lifecycle(vault_dir: str, key: str) -> None:
    data = _load_lifecycle(vault_dir)
    data.pop(key, None)
    _save_lifecycle(vault_dir, data)


def list_lifecycle(vault_dir: str) -> dict:
    return _load_lifecycle(vault_dir)


def filter_by_state(vault_dir: str, state: str) -> list:
    if state not in VALID_STATES:
        raise LifecycleError(f"Invalid state '{state}'. Valid: {VALID_STATES}")
    data = _load_lifecycle(vault_dir)
    return [k for k, v in data.items() if v == state]
