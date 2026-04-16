"""Copy variables between two vault files with optional overwrite support."""

from envault.vault import VaultError, _load_raw, _save_raw, get_variable, set_variable


class CopyError(Exception):
    pass


def copy_variables(src_path: str, dst_path: str, password: str, keys: list[str] | None = None, overwrite: bool = False) -> dict:
    """Copy variables from src vault to dst vault.

    Args:
        src_path: Path to source vault file.
        dst_path: Path to destination vault file.
        password: Shared password for both vaults.
        keys: List of keys to copy. If None, copies all variables.
        overwrite: If False, raises CopyError on key conflicts.

    Returns:
        dict with 'copied', 'skipped' lists.
    """
    try:
        src_data = _load_raw(src_path)
    except VaultError as e:
        raise CopyError(f"Source vault error: {e}") from e

    try:
        dst_data = _load_raw(dst_path)
    except VaultError as e:
        raise CopyError(f"Destination vault error: {e}") from e

    from envault.vault import list_variables
    src_vars = list_variables(src_path, password)

    if keys is None:
        keys = list(src_vars.keys())

    missing = [k for k in keys if k not in src_vars]
    if missing:
        raise CopyError(f"Keys not found in source vault: {', '.join(missing)}")

    dst_vars = list_variables(dst_path, password)

    copied = []
    skipped = []

    for key in keys:
        if key in dst_vars and not overwrite:
            skipped.append(key)
            continue
        set_variable(dst_path, password, key, src_vars[key])
        copied.append(key)

    return {"copied": copied, "skipped": skipped}
