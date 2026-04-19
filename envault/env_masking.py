import json
import os

MASKING_FILENAME = ".envault_masking.json"
MASK_CHAR = "*"
DEFAULT_VISIBLE_CHARS = 4


class MaskingError(Exception):
    pass


def _masking_path(vault_dir: str) -> str:
    return os.path.join(vault_dir, MASKING_FILENAME)


def _load_masking(vault_dir: str) -> dict:
    path = _masking_path(vault_dir)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_masking(vault_dir: str, data: dict) -> None:
    path = _masking_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def enable_masking(vault_dir: str, key: str, visible_chars: int = DEFAULT_VISIBLE_CHARS) -> None:
    data = _load_masking(vault_dir)
    data[key] = {"masked": True, "visible_chars": visible_chars}
    _save_masking(vault_dir, data)


def disable_masking(vault_dir: str, key: str) -> None:
    data = _load_masking(vault_dir)
    if key in data:
        del data[key]
        _save_masking(vault_dir, data)


def is_masked(vault_dir: str, key: str) -> bool:
    data = _load_masking(vault_dir)
    return data.get(key, {}).get("masked", False)


def mask_value(value: str, visible_chars: int = DEFAULT_VISIBLE_CHARS) -> str:
    if len(value) <= visible_chars:
        return MASK_CHAR * len(value)
    return value[:visible_chars] + MASK_CHAR * (len(value) - visible_chars)


def get_display_value(vault_dir: str, key: str, value: str) -> str:
    data = _load_masking(vault_dir)
    entry = data.get(key)
    if entry and entry.get("masked", False):
        visible = entry.get("visible_chars", DEFAULT_VISIBLE_CHARS)
        return mask_value(value, visible)
    return value


def list_masked(vault_dir: str) -> list:
    data = _load_masking(vault_dir)
    return [k for k, v in data.items() if v.get("masked", False)]
