"""Manage variable visibility levels (public, private, secret)."""

import json
from pathlib import Path

VISIBILITY_FILENAME = ".envault_visibility.json"
VALID_LEVELS = {"public", "private", "secret"}


class VisibilityError(Exception):
    pass


def _visibility_path(vault_path: str) -> Path:
    return Path(vault_path).parent / VISIBILITY_FILENAME


def _load_visibility(vault_path: str) -> dict:
    p = _visibility_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_visibility(vault_path: str, data: dict) -> None:
    p = _visibility_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_visibility(vault_path: str, key: str, level: str) -> None:
    if level not in VALID_LEVELS:
        raise VisibilityError(f"Invalid level '{level}'. Choose from: {', '.join(sorted(VALID_LEVELS))}")
    data = _load_visibility(vault_path)
    data[key] = level
    _save_visibility(vault_path, data)


def get_visibility(vault_path: str, key: str) -> str:
    data = _load_visibility(vault_path)
    return data.get(key, "private")


def remove_visibility(vault_path: str, key: str) -> None:
    data = _load_visibility(vault_path)
    if key in data:
        del data[key]
        _save_visibility(vault_path, data)


def list_visibility(vault_path: str) -> dict:
    return _load_visibility(vault_path)


def filter_by_level(vault_path: str, level: str) -> list:
    if level not in VALID_LEVELS:
        raise VisibilityError(f"Invalid level '{level}'.")
    data = _load_visibility(vault_path)
    return [k for k, v in data.items() if v == level]
