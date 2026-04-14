"""Vault module for reading and writing encrypted .envault files."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import derive_key, generate_salt, encrypt, decrypt

DEFAULT_VAULT_FILE = ".envault"
ENCODING = "utf-8"


def _load_raw(vault_path: Path) -> dict:
    """Load raw JSON data from a vault file."""
    with vault_path.open("r", encoding=ENCODING) as f:
        return json.load(f)


def _save_raw(vault_path: Path, data: dict) -> None:
    """Save raw JSON data to a vault file."""
    with vault_path.open("w", encoding=ENCODING) as f:
        json.dump(data, f, indent=2)


def init_vault(password: str, vault_path: Optional[Path] = None) -> Path:
    """Initialize a new empty vault file.

    Args:
        password: Master password used to derive the encryption key.
        vault_path: Path to the vault file. Defaults to .envault in cwd.

    Returns:
        Path to the created vault file.

    Raises:
        FileExistsError: If the vault file already exists.
    """
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    if vault_path.exists():
        raise FileExistsError(f"Vault already exists at {vault_path}")

    salt = generate_salt()
    data = {
        "salt": salt.hex(),
        "variables": {}
    }
    _save_raw(vault_path, data)
    return vault_path


def set_variable(key: str, value: str, password: str, vault_path: Optional[Path] = None) -> None:
    """Encrypt and store an environment variable in the vault.

    Args:
        key: Variable name.
        value: Plain-text variable value.
        password: Master password.
        vault_path: Path to the vault file.
    """
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    data = _load_raw(vault_path)
    salt = bytes.fromhex(data["salt"])
    derived_key = derive_key(password, salt)
    encrypted = encrypt(derived_key, value.encode(ENCODING))
    data["variables"][key] = encrypted.hex()
    _save_raw(vault_path, data)


def get_variable(key: str, password: str, vault_path: Optional[Path] = None) -> str:
    """Retrieve and decrypt an environment variable from the vault.

    Args:
        key: Variable name.
        password: Master password.
        vault_path: Path to the vault file.

    Returns:
        Decrypted variable value as a string.

    Raises:
        KeyError: If the variable does not exist in the vault.
    """
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    data = _load_raw(vault_path)
    if key not in data["variables"]:
        raise KeyError(f"Variable '{key}' not found in vault.")
    salt = bytes.fromhex(data["salt"])
    derived_key = derive_key(password, salt)
    encrypted = bytes.fromhex(data["variables"][key])
    return decrypt(derived_key, encrypted).decode(ENCODING)


def list_keys(vault_path: Optional[Path] = None) -> list:
    """Return a list of all stored variable names."""
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    data = _load_raw(vault_path)
    return list(data["variables"].keys())


def delete_variable(key: str, vault_path: Optional[Path] = None) -> None:
    """Remove a variable from the vault.

    Raises:
        KeyError: If the variable does not exist.
    """
    vault_path = vault_path or Path(DEFAULT_VAULT_FILE)
    data = _load_raw(vault_path)
    if key not in data["variables"]:
        raise KeyError(f"Variable '{key}' not found in vault.")
    del data["variables"][key]
    _save_raw(vault_path, data)
