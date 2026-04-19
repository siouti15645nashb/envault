"""Classification support for vault variables."""

import json
from pathlib import Path

CLASSIFICATION_FILENAME = ".envault_classification.json"

VALID_LEVELS = ["public", "internal", "confidential", "secret"]


class ClassificationError(Exception):
    pass


def _classification_path(vault_dir: str) -> Path:
    return Path(vault_dir) / CLASSIFICATION_FILENAME


def _load_classifications(vault_dir: str) -> dict:
    p = _classification_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_classifications(vault_dir: str, data: dict) -> None:
    p = _classification_path(vault_dir)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_classification(vault_dir: str, key: str, level: str) -> None:
    if level not in VALID_LEVELS:
        raise ClassificationError(
            f"Invalid level '{level}'. Must be one of: {VALID_LEVELS}"
        )
    data = _load_classifications(vault_dir)
    data[key] = level
    _save_classifications(vault_dir, data)


def get_classification(vault_dir: str, key: str) -> str | None:
    data = _load_classifications(vault_dir)
    return data.get(key)


def remove_classification(vault_dir: str, key: str) -> None:
    data = _load_classifications(vault_dir)
    if key not in data:
        raise ClassificationError(f"No classification set for '{key}'")
    del data[key]
    _save_classifications(vault_dir, data)


def list_classifications(vault_dir: str) -> dict:
    return _load_classifications(vault_dir)
