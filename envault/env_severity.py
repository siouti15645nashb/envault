import json
import os
from typing import Dict, Optional

SEVERITY_FILENAME = ".envault_severity.json"
VALID_LEVELS = ["low", "medium", "high", "critical"]


class SeverityError(Exception):
    pass


def _severity_path(vault_dir: str) -> str:
    return os.path.join(vault_dir, SEVERITY_FILENAME)


def _load_severity(vault_dir: str) -> Dict[str, str]:
    path = _severity_path(vault_dir)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_severity(vault_dir: str, data: Dict[str, str]) -> None:
    path = _severity_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_severity(vault_dir: str, key: str, level: str) -> None:
    if level not in VALID_LEVELS:
        raise SeverityError(f"Invalid severity level '{level}'. Must be one of: {VALID_LEVELS}")
    data = _load_severity(vault_dir)
    data[key] = level
    _save_severity(vault_dir, data)


def get_severity(vault_dir: str, key: str) -> Optional[str]:
    data = _load_severity(vault_dir)
    return data.get(key)


def remove_severity(vault_dir: str, key: str) -> None:
    data = _load_severity(vault_dir)
    if key not in data:
        raise SeverityError(f"No severity set for '{key}'")
    del data[key]
    _save_severity(vault_dir, data)


def list_severity(vault_dir: str) -> Dict[str, str]:
    return _load_severity(vault_dir)


def get_by_level(vault_dir: str, level: str) -> list:
    if level not in VALID_LEVELS:
        raise SeverityError(f"Invalid severity level '{level}'.")
    data = _load_severity(vault_dir)
    return [k for k, v in data.items() if v == level]
