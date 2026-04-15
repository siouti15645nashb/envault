"""Rename and copy variable keys within the vault."""

from envault.vault import VaultError, _load_raw, _save_raw, get_variable, set_variable


class RenameError(Exception):
    """Raised when a rename or copy operation fails."""


def rename_variable(vault_path: str, password: str, old_key: str, new_key: str) -> None:
    """Rename a variable by moving its value to a new key and deleting the old one.

    Raises RenameError if old_key does not exist or new_key already exists.
    """
    data = _load_raw(vault_path)
    variables = data.get("variables", {})

    if old_key not in variables:
        raise RenameError(f"Variable '{old_key}' does not exist.")
    if new_key in variables:
        raise RenameError(f"Variable '{new_key}' already exists. Use --force to overwrite.")

    value = get_variable(vault_path, password, old_key)
    set_variable(vault_path, password, new_key, value)

    # Remove old key from raw data
    data = _load_raw(vault_path)
    data["variables"].pop(old_key, None)
    _save_raw(vault_path, data)


def rename_variable_force(vault_path: str, password: str, old_key: str, new_key: str) -> None:
    """Rename a variable, overwriting new_key if it already exists."""
    data = _load_raw(vault_path)
    variables = data.get("variables", {})

    if old_key not in variables:
        raise RenameError(f"Variable '{old_key}' does not exist.")

    value = get_variable(vault_path, password, old_key)
    set_variable(vault_path, password, new_key, value)

    data = _load_raw(vault_path)
    data["variables"].pop(old_key, None)
    _save_raw(vault_path, data)


def copy_variable(vault_path: str, password: str, src_key: str, dst_key: str) -> None:
    """Copy a variable's value to a new key, leaving the original intact.

    Raises RenameError if src_key does not exist or dst_key already exists.
    """
    data = _load_raw(vault_path)
    variables = data.get("variables", {})

    if src_key not in variables:
        raise RenameError(f"Variable '{src_key}' does not exist.")
    if dst_key in variables:
        raise RenameError(f"Variable '{dst_key}' already exists.")

    value = get_variable(vault_path, password, src_key)
    set_variable(vault_path, password, dst_key, value)
