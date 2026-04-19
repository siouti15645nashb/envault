"""Environment (dev/staging/prod) assignment for vault variables."""

import json
from pathlib import Path

ENVIRONMENT_FILENAME = ".envault_environment.json"
VALID_ENVIRONMENTS = ["development", "staging", "production", "test", "local"]


class EnvironmentError(Exception):
    pass


def _environment_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ENVIRONMENT_FILENAME


def _load_environments(vault_path: str) -> dict:
    path = _environment_path(vault_path)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_environments(vault_path: str, data: dict) -> None:
    path = _environment_path(vault_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_environment(vault_path: str, key: str, environment: str) -> None:
    if environment not in VALID_ENVIRONMENTS:
        raise EnvironmentError(
            f"Invalid environment '{environment}'. Must be one of: {VALID_ENVIRONMENTS}"
        )
    data = _load_environments(vault_path)
    data[key] = environment
    _save_environments(vault_path, data)


def get_environment(vault_path: str, key: str) -> str | None:
    data = _load_environments(vault_path)
    return data.get(key)


def remove_environment(vault_path: str, key: str) -> None:
    data = _load_environments(vault_path)
    if key not in data:
        raise EnvironmentError(f"No environment set for '{key}'")
    del data[key]
    _save_environments(vault_path, data)


def list_environments(vault_path: str) -> dict:
    return _load_environments(vault_path)
