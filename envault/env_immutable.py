import json
from pathlib import Path

IMMUTABLE_FILENAME = ".envault_immutable.json"


class ImmutableError(Exception):
    pass


def _immutable_path(vault_path: str) -> Path:
    return Path(vault_path).parent / IMMUTABLE_FILENAME


def _load_immutable(vault_path: str) -> list:
    p = _immutable_path(vault_path)
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)


def _save_immutable(vault_path: str, keys: list) -> None:
    p = _immutable_path(vault_path)
    with open(p, "w") as f:
        json.dump(sorted(set(keys)), f, indent=2)


def mark_immutable(vault_path: str, key: str) -> None:
    keys = _load_immutable(vault_path)
    if key not in keys:
        keys.append(key)
    _save_immutable(vault_path, keys)


def unmark_immutable(vault_path: str, key: str) -> None:
    keys = _load_immutable(vault_path)
    if key not in keys:
        raise ImmutableError(f"Key '{key}' is not marked as immutable.")
    keys.remove(key)
    _save_immutable(vault_path, keys)


def is_immutable(vault_path: str, key: str) -> bool:
    return key in _load_immutable(vault_path)


def list_immutable(vault_path: str) -> list:
    return _load_immutable(vault_path)
