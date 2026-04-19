"""Runtime environment binding — associate vault keys with runtime targets."""

import json
from pathlib import Path

RUNTIME_FILENAME = ".envault_runtime.json"
VALID_TARGETS = ["process", "docker", "kubernetes", "lambda", "systemd", "shell"]


class RuntimeError(Exception):
    pass


def _runtime_path(vault_dir: str) -> Path:
    return Path(vault_dir) / RUNTIME_FILENAME


def _load_runtime(vault_dir: str) -> dict:
    p = _runtime_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_runtime(vault_dir: str, data: dict) -> None:
    with open(_runtime_path(vault_dir), "w") as f:
        json.dump(data, f, indent=2)


def set_runtime(vault_dir: str, key: str, target: str) -> None:
    if target not in VALID_TARGETS:
        raise RuntimeError(f"Invalid target '{target}'. Valid: {VALID_TARGETS}")
    data = _load_runtime(vault_dir)
    data[key] = target
    _save_runtime(vault_dir, data)


def get_runtime(vault_dir: str, key: str) -> str | None:
    return _load_runtime(vault_dir).get(key)


def remove_runtime(vault_dir: str, key: str) -> None:
    data = _load_runtime(vault_dir)
    if key not in data:
        raise RuntimeError(f"No runtime binding for '{key}'")
    del data[key]
    _save_runtime(vault_dir, data)


def list_runtime(vault_dir: str) -> dict:
    return _load_runtime(vault_dir)


def filter_by_target(vault_dir: str, target: str) -> list:
    return [k for k, v in _load_runtime(vault_dir).items() if v == target]
