"""Key rotation support for envault vaults."""

import json
from pathlib import Path
from typing import Optional

from envault.crypto import derive_key, generate_salt, encrypt, decrypt
from envault.vault import _load_raw, _save_raw
from envault.audit import record_event


class RotationError(Exception):
    """Raised when key rotation fails."""


def rotate_key(
    vault_path: Path,
    old_password: str,
    new_password: str,
    audit: bool = True,
) -> int:
    """Re-encrypt all variables in the vault with a new password.

    Decrypts every stored variable using *old_password*, then re-encrypts
    each value with a freshly derived key from *new_password* and a brand-new
    salt stored back into the vault file.

    Returns the number of variables that were rotated.

    Raises RotationError if decryption with the old password fails.
    """
    data = _load_raw(vault_path)

    old_salt: bytes = bytes.fromhex(data["salt"])
    old_key = derive_key(old_password, old_salt)

    # Decrypt all values with the old key first — fail fast if password wrong.
    plaintext_vars: dict[str, str] = {}
    try:
        for name, ciphertext_hex in data.get("variables", {}).items():
            plaintext_vars[name] = decrypt(old_key, bytes.fromhex(ciphertext_hex))
    except Exception as exc:
        raise RotationError(
            f"Failed to decrypt variable '{name}' with the provided old password."
        ) from exc

    # Generate new salt and derive new key.
    new_salt = generate_salt()
    new_key = derive_key(new_password, new_salt)

    # Re-encrypt everything with the new key.
    new_variables: dict[str, str] = {}
    for name, plaintext in plaintext_vars.items():
        new_variables[name] = encrypt(new_key, plaintext).hex()

    data["salt"] = new_salt.hex()
    data["variables"] = new_variables
    _save_raw(vault_path, data)

    count = len(new_variables)
    if audit:
        record_event(
            vault_path.parent,
            "rotate_key",
            {"vault": str(vault_path), "variables_rotated": count},
        )
    return count
