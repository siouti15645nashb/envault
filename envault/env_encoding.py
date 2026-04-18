import json
from pathlib import Path

ENCODING_FILENAME = ".envault_encoding"
VALID_ENCODINGS = ["utf-8", "utf-16", "ascii", "latin-1", "utf-8-sig"]


class EncodingError(Exception):
    pass


def _encoding_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ENCODING_FILENAME


def _load_encodings(vault_dir: str) -> dict:
    path = _encoding_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_encodings(vault_dir: str, data: dict) -> None:
    path = _encoding_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_encoding(vault_dir: str, key: str, encoding: str) -> None:
    if not key:
        raise EncodingError("Key must not be empty.")
    if encoding not in VALID_ENCODINGS:
        raise EncodingError(f"Invalid encoding '{encoding}'. Valid: {VALID_ENCODINGS}")
    data = _load_encodings(vault_dir)
    data[key] = encoding
    _save_encodings(vault_dir, data)


def get_encoding(vault_dir: str, key: str) -> str | None:
    data = _load_encodings(vault_dir)
    return data.get(key)


def remove_encoding(vault_dir: str, key: str) -> bool:
    data = _load_encodings(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_encodings(vault_dir, data)
    return True


def list_encodings(vault_dir: str) -> dict:
    return _load_encodings(vault_dir)
