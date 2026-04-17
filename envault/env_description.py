"""Module for managing human-readable descriptions for vault variables."""

import json
import os
from pathlib import Path

DESCRIPTIONS_FILENAME = ".envault_descriptions.json"


class DescriptionError(Exception):
    pass


def _descriptions_path(vault_path: str) -> Path:
    return Path(vault_path).parent / DESCRIPTIONS_FILENAME


def _load_descriptions(vault_path: str) -> dict:
    path = _descriptions_path(vault_path)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_descriptions(vault_path: str, data: dict) -> None:
    path = _descriptions_path(vault_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_description(vault_path: str, key: str, description: str) -> None:
    if not key:
        raise DescriptionError("Key must not be empty.")
    if not description.strip():
        raise DescriptionError("Description must not be empty.")
    data = _load_descriptions(vault_path)
    data[key] = description.strip()
    _save_descriptions(vault_path, data)


def get_description(vault_path: str, key: str) -> str | None:
    data = _load_descriptions(vault_path)
    return data.get(key)


def remove_description(vault_path: str, key: str) -> None:
    data = _load_descriptions(vault_path)
    if key not in data:
        raise DescriptionError(f"No description found for '{key}'.")
    del data[key]
    _save_descriptions(vault_path, data)


def list_descriptions(vault_path: str) -> dict:
    return _load_descriptions(vault_path)
