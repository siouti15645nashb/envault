"""Track the source/origin of environment variables."""

import json
from pathlib import Path

SOURCE_FILENAME = ".envault_sources.json"
VALID_SOURCES = ["manual", "dotenv", "shell", "ci", "secret_manager", "other"]


class SourceError(Exception):
    pass


def _source_path(vault_path: str) -> Path:
    return Path(vault_path).parent / SOURCE_FILENAME


def _load_sources(vault_path: str) -> dict:
    p = _source_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_sources(vault_path: str, data: dict) -> None:
    p = _source_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_source(vault_path: str, key: str, source: str) -> None:
    if source not in VALID_SOURCES:
        raise SourceError(f"Invalid source '{source}'. Must be one of: {VALID_SOURCES}")
    data = _load_sources(vault_path)
    data[key] = source
    _save_sources(vault_path, data)


def get_source(vault_path: str, key: str) -> str | None:
    data = _load_sources(vault_path)
    return data.get(key)


def remove_source(vault_path: str, key: str) -> bool:
    data = _load_sources(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_sources(vault_path, data)
    return True


def list_sources(vault_path: str) -> dict:
    return _load_sources(vault_path)
