"""Promote variables from one vault to another (e.g. staging -> production)."""

import os
from typing import Optional

from envault.vault import VaultError, get_variable, set_variable, list_variables


class PromoteError(Exception):
    """Raised when a promotion operation fails."""


def promote_variables(
    source_vault: str,
    dest_vault: str,
    password: str,
    keys: Optional[list] = None,
    overwrite: bool = False,
) -> dict:
    """Promote variables from source vault to destination vault.

    Args:
        source_vault: Path to the source .envault file.
        dest_vault: Path to the destination .envault file.
        password: Shared password for both vaults.
        keys: Specific keys to promote. If None, all keys are promoted.
        overwrite: If True, overwrite existing keys in destination.

    Returns:
        A dict with 'promoted', 'skipped', and 'failed' key lists.
    """
    if not os.path.exists(source_vault):
        raise PromoteError(f"Source vault not found: {source_vault}")
    if not os.path.exists(dest_vault):
        raise PromoteError(f"Destination vault not found: {dest_vault}")

    try:
        available_keys = list_variables(source_vault, password)
    except VaultError as e:
        raise PromoteError(f"Failed to read source vault: {e}")

    keys_to_promote = keys if keys is not None else available_keys

    result = {"promoted": [], "skipped": [], "failed": []}

    for key in keys_to_promote:
        if key not in available_keys:
            result["failed"].append({"key": key, "reason": "not found in source vault"})
            continue

        try:
            value = get_variable(source_vault, password, key)
        except VaultError as e:
            result["failed"].append({"key": key, "reason": str(e)})
            continue

        try:
            existing_keys = list_variables(dest_vault, password)
        except VaultError as e:
            raise PromoteError(f"Failed to read destination vault: {e}")

        if key in existing_keys and not overwrite:
            result["skipped"].append(key)
            continue

        try:
            set_variable(dest_vault, password, key, value)
            result["promoted"].append(key)
        except VaultError as e:
            result["failed"].append({"key": key, "reason": str(e)})

    return result
