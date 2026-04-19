"""Per-variable cipher algorithm selection for envault."""

import json
from pathlib import Path

CIPHER_FILENAME = ".envault_cipher.json"
VALID_CIPHERS = ["AES-256-GCM", "AES-256-CBC", "ChaCha20-Poly1305"]


class CipherError(Exception):
    pass


def _cipher_path(vault_dir: str) -> Path:
    return Path(vault_dir) / CIPHER_FILENAME


def _load_ciphers(vault_dir: str) -> dict:
    p = _cipher_path(vault_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_ciphers(vault_dir: str, data: dict) -> None:
    p = _cipher_path(vault_dir)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_cipher(vault_dir: str, key: str, cipher: str) -> None:
    if cipher not in VALID_CIPHERS:
        raise CipherError(f"Invalid cipher '{cipher}'. Valid: {VALID_CIPHERS}")
    data = _load_ciphers(vault_dir)
    data[key] = cipher
    _save_ciphers(vault_dir, data)


def get_cipher(vault_dir: str, key: str) -> str | None:
    return _load_ciphers(vault_dir).get(key)


def remove_cipher(vault_dir: str, key: str) -> None:
    data = _load_ciphers(vault_dir)
    if key not in data:
        raise CipherError(f"No cipher set for '{key}'")
    del data[key]
    _save_ciphers(vault_dir, data)


def list_ciphers(vault_dir: str) -> dict:
    return _load_ciphers(vault_dir)
