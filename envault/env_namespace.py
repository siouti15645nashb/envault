"""Namespace support for grouping variables by logical prefix boundaries."""

import json
import os
from pathlib import Path

NAMESPACE_FILENAME = ".envault_namespaces.json"


class NamespaceError(Exception):
    pass


def _namespace_path(vault_dir: str) -> Path:
    return Path(vault_dir) / NAMESPACE_FILENAME


def _load_namespaces(vault_dir: str) -> dict:
    path = _namespace_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_namespaces(vault_dir: str, data: dict) -> None:
    path = _namespace_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def define_namespace(vault_dir: str, name: str, prefix: str) -> None:
    """Define a namespace with a given key prefix."""
    if not name or not name.strip():
        raise NamespaceError("Namespace name must not be empty.")
    if not prefix or not prefix.strip():
        raise NamespaceError("Namespace prefix must not be empty.")
    data = _load_namespaces(vault_dir)
    data[name] = prefix.strip().upper()
    _save_namespaces(vault_dir, data)


def remove_namespace(vault_dir: str, name: str) -> None:
    data = _load_namespaces(vault_dir)
    if name not in data:
        raise NamespaceError(f"Namespace '{name}' does not exist.")
    del data[name]
    _save_namespaces(vault_dir, data)


def list_namespaces(vault_dir: str) -> dict:
    return _load_namespaces(vault_dir)


def resolve_namespace(vault_dir: str, key: str) -> str | None:
    """Return namespace name that matches the given key's prefix, or None."""
    data = _load_namespaces(vault_dir)
    for name, prefix in data.items():
        if key.upper().startswith(prefix):
            return name
    return None


def keys_in_namespace(vault_dir: str, name: str, all_keys: list[str]) -> list[str]:
    """Filter keys belonging to the given namespace."""
    data = _load_namespaces(vault_dir)
    if name not in data:
        raise NamespaceError(f"Namespace '{name}' does not exist.")
    prefix = data[name]
    return [k for k in all_keys if k.upper().startswith(prefix)]
