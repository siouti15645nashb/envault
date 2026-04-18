"""Metadata management for vault variables (arbitrary key-value annotations)."""

import json
import os
from typing import Dict, Optional

METADATA_FILENAME = ".envault_metadata.json"


class MetadataError(Exception):
    pass


def _metadata_path(vault_path: str) -> str:
    return os.path.join(os.path.dirname(vault_path), METADATA_FILENAME)


def _load_metadata(vault_path: str) -> Dict[str, Dict[str, str]]:
    path = _metadata_path(vault_path)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_metadata(vault_path: str, data: Dict[str, Dict[str, str]]) -> None:
    path = _metadata_path(vault_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_metadata(vault_path: str, key: str, meta_key: str, meta_value: str) -> None:
    data = _load_metadata(vault_path)
    if key not in data:
        data[key] = {}
    data[key][meta_key] = meta_value
    _save_metadata(vault_path, data)


def get_metadata(vault_path: str, key: str) -> Dict[str, str]:
    data = _load_metadata(vault_path)
    return data.get(key, {})


def remove_metadata_key(vault_path: str, key: str, meta_key: str) -> None:
    data = _load_metadata(vault_path)
    if key not in data or meta_key not in data[key]:
        raise MetadataError(f"Metadata key '{meta_key}' not found for variable '{key}'")
    del data[key][meta_key]
    if not data[key]:
        del data[key]
    _save_metadata(vault_path, data)


def remove_all_metadata(vault_path: str, key: str) -> None:
    data = _load_metadata(vault_path)
    if key in data:
        del data[key]
        _save_metadata(vault_path, data)


def list_metadata(vault_path: str) -> Dict[str, Dict[str, str]]:
    return _load_metadata(vault_path)
