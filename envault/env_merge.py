"""Merge variables from one vault into another."""

from typing import List, Optional
from envault.vault import _load_raw, _save_raw, get_variable, set_variable, list_variables, VaultError


class MergeError(Exception):
    pass


def merge_vaults(
    source_path: str,
    dest_path: str,
    password: str,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
) -> dict:
    """Merge variables from source vault into dest vault.

    Returns a dict with keys: merged, skipped, errors.
    """
    try:
        source_data = _load_raw(source_path)
    except Exception as e:
        raise MergeError(f"Cannot load source vault: {e}")

    try:
        dest_data = _load_raw(dest_path)
    except Exception as e:
        raise MergeError(f"Cannot load destination vault: {e}")

    source_vars = source_data.get("variables", {})
    dest_vars = dest_data.get("variables", {})

    if keys is not None:
        missing = [k for k in keys if k not in source_vars]
        if missing:
            raise MergeError(f"Keys not found in source vault: {', '.join(missing)}")
        to_merge = {k: source_vars[k] for k in keys}
    else:
        to_merge = dict(source_vars)

    merged = []
    skipped = []

    for key, encrypted_value in to_merge.items():
        if key in dest_vars and not overwrite:
            skipped.append(key)
            continue
        try:
            value = get_variable(source_path, key, password)
            set_variable(dest_path, key, value, password)
            merged.append(key)
        except VaultError as e:
            raise MergeError(f"Failed to merge key '{key}': {e}")

    return {"merged": merged, "skipped": skipped}
