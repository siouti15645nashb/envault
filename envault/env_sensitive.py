"""Mark variables as sensitive (masked in output)."""

import json
from pathlib import Path

SENSITIVE_FILENAME = ".envault_sensitive"


class SensitiveError(Exception):
    pass


def _sensitive_path(vault_path: str) -> Path:
    return Path(vault_path).parent / SENSITIVE_FILENAME


def _load_sensitive(vault_path: str) -> list:
    p = _sensitive_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_sensitive(vault_path: str, keys: list) -> None:
    p = _sensitive_path(vault_path)
    p.write_text(json.dumps(sorted(set(keys)), indent=2))


def mark_sensitive(vault_path: str, key: str) -> None:
    keys = _load_sensitive(vault_path)
    if key not in keys:
        keys.append(key)
    _save_sensitive(vault_path, keys)


def unmark_sensitive(vault_path: str, key: str) -> None:
    keys = _load_sensitive(vault_path)
    if key not in keys:
        raise SensitiveError(f"Key '{key}' is not marked sensitive.")
    keys.remove(key)
    _save_sensitive(vault_path, keys)


def is_sensitive(vault_path: str, key: str) -> bool:
    return key in _load_sensitive(vault_path)


def list_sensitive(vault_path: str) -> list:
    return _load_sensitive(vault_path)
