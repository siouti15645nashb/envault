"""Alias support: map short names to vault variable keys."""

import json
from pathlib import Path

ALIASES_FILENAME = ".envault_aliases.json"


class AliasError(Exception):
    pass


def _aliases_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ALIASES_FILENAME


def _load_aliases(vault_path: str) -> dict:
    p = _aliases_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_aliases(vault_path: str, data: dict) -> None:
    p = _aliases_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def add_alias(vault_path: str, alias: str, key: str) -> None:
    if not alias.strip():
        raise AliasError("Alias name cannot be empty.")
    if not key.strip():
        raise AliasError("Target key cannot be empty.")
    data = _load_aliases(vault_path)
    data[alias] = key
    _save_aliases(vault_path, data)


def remove_alias(vault_path: str, alias: str) -> None:
    data = _load_aliases(vault_path)
    if alias not in data:
        raise AliasError(f"Alias '{alias}' not found.")
    del data[alias]
    _save_aliases(vault_path, data)


def resolve_alias(vault_path: str, alias: str) -> str:
    data = _load_aliases(vault_path)
    if alias not in data:
        raise AliasError(f"Alias '{alias}' not found.")
    return data[alias]


def list_aliases(vault_path: str) -> dict:
    return _load_aliases(vault_path)
