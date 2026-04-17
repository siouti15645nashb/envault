"""Watch vault for changes and notify on variable modifications."""

import os
import time
import hashlib
import json
from typing import Callable, Optional

WATCH_INTERVAL = 1.0  # seconds


class WatchError(Exception):
    pass


def _file_hash(path: str) -> Optional[str]:
    """Return MD5 hash of file contents, or None if file missing."""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def _load_keys(vault_path: str, password: str) -> set:
    """Return set of variable keys from vault."""
    from envault.vault import list_variables
    return set(list_variables(vault_path, password).keys())


def watch_vault(
    vault_path: str,
    password: str,
    on_change: Callable[[str, set, set], None],
    interval: float = WATCH_INTERVAL,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Watch vault_path for changes. Calls on_change(event, added_keys, removed_keys)
    when variables are added or removed.
    """
    if not os.path.exists(vault_path):
        raise WatchError(f"Vault not found: {vault_path}")

    last_hash = _file_hash(vault_path)
    last_keys = _load_keys(vault_path, password)
    iterations = 0

    while True:
        time.sleep(interval)
        current_hash = _file_hash(vault_path)

        if current_hash != last_hash:
            current_keys = _load_keys(vault_path, password)
            added = current_keys - last_keys
            removed = last_keys - current_keys
            if added or removed:
                on_change(vault_path, added, removed)
            last_hash = current_hash
            last_keys = current_keys

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
