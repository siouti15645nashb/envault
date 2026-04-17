"""Category management for vault variables."""
import json
from pathlib import Path

CATEGORY_FILENAME = ".envault_categories.json"


class CategoryError(Exception):
    pass


def _category_path(vault_path: str) -> Path:
    return Path(vault_path).parent / CATEGORY_FILENAME


def _load_categories(vault_path: str) -> dict:
    p = _category_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_categories(vault_path: str, data: dict) -> None:
    _category_path(vault_path).write_text(json.dumps(data, indent=2))


def set_category(vault_path: str, key: str, category: str) -> None:
    from envault.vault import list_variables
    keys = list_variables(vault_path, "")
    if key not in keys:
        raise CategoryError(f"Variable '{key}' not found in vault.")
    if not category.strip():
        raise CategoryError("Category name cannot be empty.")
    data = _load_categories(vault_path)
    data[key] = category.strip()
    _save_categories(vault_path, data)


def remove_category(vault_path: str, key: str) -> None:
    data = _load_categories(vault_path)
    if key not in data:
        raise CategoryError(f"No category set for '{key}'.")
    del data[key]
    _save_categories(vault_path, data)


def get_category(vault_path: str, key: str) -> str | None:
    return _load_categories(vault_path).get(key)


def list_categories(vault_path: str) -> dict:
    return _load_categories(vault_path)


def find_by_category(vault_path: str, category: str) -> list:
    data = _load_categories(vault_path)
    return [k for k, v in data.items() if v.lower() == category.lower()]
