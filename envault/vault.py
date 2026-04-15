"""Vault file management for envault.

This file is the authoritative version; it adds DEFAULT_VAULT_FILE
and preserves all existing public functions.
"""

import json
from pathlib import Path

from envault.crypto import derive_key, generate_salt, encrypt, decrypt

DEFAULT_VAULT_FILE = "envault.json"


class VaultError(Exception):
    """Raised for vault-level errors."""


def _load_raw(vault_path: Path) -> dict:
    """Load the raw JSON vault dict from disk."""
    try:
        return json.loads(vault_path.read_text())
    except FileNotFoundError:
        raise VaultError(f"Vault not found: {vault_path}")
    except json.JSONDecodeError as exc:
        raise VaultError(f"Corrupt vault: {exc}")


def _save_raw(vault_path: Path, data: dict) -> None:
    """Persist the vault dict to disk as JSON."""
    vault_path.write_text(json.dumps(data, indent=2))


def init_vault(vault_path: Path) -> None:
    """Create a new, empty vault file.

    Raises VaultError if the file already exists.
    """
    vault_path = Path(vault_path)
    if vault_path.exists():
        raise VaultError(f"Vault already exists: {vault_path}")
    salt = generate_salt().hex()
    _save_raw(vault_path, {"salt": salt, "variables": {}})


def set_variable(vault_path: Path, password: str, key: str, value: str) -> None:
    """Encrypt and store *value* under *key* in the vault."""
    data = _load_raw(Path(vault_path))
    salt = bytes.fromhex(data["salt"])
    derived = derive_key(password, salt)
    data["variables"][key] = encrypt(derived, value).hex()
    _save_raw(Path(vault_path), data)


def get_variable(vault_path: Path, password: str, key: str) -> str:
    """Decrypt and return the value stored under *key*."""
    data = _load_raw(Path(vault_path))
    if key not in data["variables"]:
        raise VaultError(f"Key not found: {key}")
    salt = bytes.fromhex(data["salt"])
    derived = derive_key(password, salt)
    return decrypt(derived, bytes.fromhex(data["variables"][key]))


def list_variables(vault_path: Path, password: str) -> dict[str, str]:
    """Return all decrypted key/value pairs from the vault."""
    data = _load_raw(Path(vault_path))
    salt = bytes.fromhex(data["salt"])
    derived = derive_key(password, salt)
    return {
        k: decrypt(derived, bytes.fromhex(v))
        for k, v in data["variables"].items()
    }


def delete_variable(vault_path: Path, key: str) -> None:
    """Remove *key* from the vault without needing the password.

    Raises VaultError if the key does not exist.
    """
    data = _load_raw(Path(vault_path))
    if key not in data["variables"]:
        raise VaultError(f"Key not found: {key}")
    del data["variables"][key]
    _save_raw(Path(vault_path), data)
