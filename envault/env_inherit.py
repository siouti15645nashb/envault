"""Inheritance support: allow a vault to inherit variables from a parent vault."""
from __future__ import annotations

import json
import os
from pathlib import Path

INHERIT_FILENAME = ".envault_inherit"


class InheritError(Exception):
    pass


def _inherit_path(vault_path: str) -> Path:
    return Path(vault_path).parent / INHERIT_FILENAME


def _load_inherit(vault_path: str) -> dict:
    p = _inherit_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_inherit(vault_path: str, data: dict) -> None:
    p = _inherit_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_parent(vault_path: str, parent_path: str) -> None:
    """Set the parent vault path for inheritance."""
    if not os.path.exists(parent_path):
        raise InheritError(f"Parent vault not found: {parent_path}")
    data = _load_inherit(vault_path)
    data["parent"] = str(Path(parent_path).resolve())
    _save_inherit(vault_path, data)


def get_parent(vault_path: str) -> str | None:
    """Return the parent vault path, or None if not set."""
    data = _load_inherit(vault_path)
    return data.get("parent")


def remove_parent(vault_path: str) -> None:
    """Remove the parent vault reference."""
    data = _load_inherit(vault_path)
    if "parent" not in data:
        raise InheritError("No parent vault is set.")
    del data["parent"]
    _save_inherit(vault_path, data)


def resolve_variables(vault_path: str, password: str) -> dict:
    """Return merged variables: parent vars overridden by child vars."""
    from envault.vault import list_variables

    parent_path = get_parent(vault_path)
    merged = {}
    if parent_path:
        if not os.path.exists(parent_path):
            raise InheritError(f"Parent vault missing: {parent_path}")
        for key, value in list_variables(parent_path, password):
            merged[key] = value
    for key, value in list_variables(vault_path, password):
        merged[key] = value
    return merged
