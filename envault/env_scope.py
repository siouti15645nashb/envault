import json
import os
from pathlib import Path

SCOPE_FILENAME = ".envault_scopes.json"
VALID_SCOPES = ["local", "development", "staging", "production", "global"]


class ScopeError(Exception):
    pass


def _scope_path(vault_dir: str) -> Path:
    return Path(vault_dir) / SCOPE_FILENAME


def _load_scopes(vault_dir: str) -> dict:
    p = _scope_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_scopes(vault_dir: str, data: dict) -> None:
    with open(_scope_path(vault_dir), "w") as f:
        json.dump(data, f, indent=2)


def set_scope(vault_dir: str, key: str, scope: str) -> None:
    if scope not in VALID_SCOPES:
        raise ScopeError(f"Invalid scope '{scope}'. Valid: {VALID_SCOPES}")
    data = _load_scopes(vault_dir)
    data[key] = scope
    _save_scopes(vault_dir, data)


def get_scope(vault_dir: str, key: str) -> str:
    data = _load_scopes(vault_dir)
    return data.get(key, "global")


def remove_scope(vault_dir: str, key: str) -> bool:
    data = _load_scopes(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_scopes(vault_dir, data)
    return True


def list_scopes(vault_dir: str) -> dict:
    return _load_scopes(vault_dir)


def filter_by_scope(vault_dir: str, scope: str) -> list:
    if scope not in VALID_SCOPES:
        raise ScopeError(f"Invalid scope '{scope}'. Valid: {VALID_SCOPES}")
    data = _load_scopes(vault_dir)
    return [k for k, v in data.items() if v == scope]
