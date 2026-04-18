"""Regex pattern constraints for environment variables."""
import json
import re
from pathlib import Path

REGEX_FILENAME = ".envault_regex.json"


class RegexError(Exception):
    pass


def _regex_path(vault_path: str) -> Path:
    return Path(vault_path).parent / REGEX_FILENAME


def _load_regex(vault_path: str) -> dict:
    p = _regex_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_regex(vault_path: str, data: dict) -> None:
    _regex_path(vault_path).write_text(json.dumps(data, indent=2))


def set_pattern(vault_path: str, key: str, pattern: str) -> None:
    try:
        re.compile(pattern)
    except re.error as e:
        raise RegexError(f"Invalid regex pattern: {e}")
    data = _load_regex(vault_path)
    data[key] = pattern
    _save_regex(vault_path, data)


def remove_pattern(vault_path: str, key: str) -> None:
    data = _load_regex(vault_path)
    if key not in data:
        raise RegexError(f"No pattern defined for '{key}'")
    del data[key]
    _save_regex(vault_path, data)


def get_pattern(vault_path: str, key: str) -> str | None:
    return _load_regex(vault_path).get(key)


def list_patterns(vault_path: str) -> dict:
    return _load_regex(vault_path)


def validate_against_pattern(vault_path: str, key: str, value: str) -> bool:
    pattern = get_pattern(vault_path, key)
    if pattern is None:
        return True
    return bool(re.fullmatch(pattern, value))
