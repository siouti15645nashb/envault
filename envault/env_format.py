"""Format rules for environment variable values."""

import re
from pathlib import Path
import json

FORMAT_FILENAME = ".envault_formats.json"

SUPPORTED_FORMATS = ["uppercase", "lowercase", "alphanumeric", "url", "email", "numeric"]

FORMAT_PATTERNS = {
    "uppercase": r"^[A-Z0-9_]+$",
    "lowercase": r"^[a-z0-9_]+$",
    "alphanumeric": r"^[a-zA-Z0-9]+$",
    "url": r"^https?://.+",
    "email": r"^[^@]+@[^@]+\.[^@]+$",
    "numeric": r"^\d+(\.\d+)?$",
}


class FormatError(Exception):
    pass


def _format_path(vault_path: str) -> Path:
    return Path(vault_path).parent / FORMAT_FILENAME


def _load_formats(vault_path: str) -> dict:
    p = _format_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_formats(vault_path: str, data: dict) -> None:
    _format_path(vault_path).write_text(json.dumps(data, indent=2))


def set_format(vault_path: str, key: str, fmt: str) -> None:
    if fmt not in SUPPORTED_FORMATS:
        raise FormatError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")
    data = _load_formats(vault_path)
    data[key] = fmt
    _save_formats(vault_path, data)


def remove_format(vault_path: str, key: str) -> None:
    data = _load_formats(vault_path)
    data.pop(key, None)
    _save_formats(vault_path, data)


def get_format(vault_path: str, key: str) -> str | None:
    return _load_formats(vault_path).get(key)


def list_formats(vault_path: str) -> dict:
    return _load_formats(vault_path)


def validate_format(value: str, fmt: str) -> bool:
    pattern = FORMAT_PATTERNS.get(fmt)
    if pattern is None:
        raise FormatError(f"Unknown format: {fmt}")
    return bool(re.match(pattern, value))
