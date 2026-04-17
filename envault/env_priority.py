"""Priority levels for environment variables."""

import json
from pathlib import Path

PRIORITY_FILENAME = ".envault_priority.json"
VALID_LEVELS = ("low", "normal", "high", "critical")


class PriorityError(Exception):
    pass


def _priority_path(vault_path: str) -> Path:
    return Path(vault_path).parent / PRIORITY_FILENAME


def _load_priorities(vault_path: str) -> dict:
    p = _priority_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(vault_path: str, data: dict) -> None:
    _priority_path(vault_path).write_text(json.dumps(data, indent=2))


def set_priority(vault_path: str, key: str, level: str) -> None:
    if level not in VALID_LEVELS:
        raise PriorityError(f"Invalid priority level '{level}'. Choose from: {', '.join(VALID_LEVELS)}")
    data = _load_priorities(vault_path)
    data[key] = level
    _save_priorities(vault_path, data)


def get_priority(vault_path: str, key: str) -> str:
    data = _load_priorities(vault_path)
    return data.get(key, "normal")


def remove_priority(vault_path: str, key: str) -> None:
    data = _load_priorities(vault_path)
    data.pop(key, None)
    _save_priorities(vault_path, data)


def list_priorities(vault_path: str) -> dict:
    return _load_priorities(vault_path)


def get_by_level(vault_path: str, level: str) -> list:
    if level not in VALID_LEVELS:
        raise PriorityError(f"Invalid priority level '{level}'.")
    data = _load_priorities(vault_path)
    return [k for k, v in data.items() if v == level]
