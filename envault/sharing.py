"""Team sharing support for envault vaults.

Allows exporting an encrypted vault bundle (salt + ciphertext map)
and importing it on another machine using a shared passphrase.
"""

import json
import base64
from pathlib import Path

from envault.crypto import derive_key, encrypt, decrypt
from envault.vault import _load_raw, _save_raw, VAULT_FILENAME

BUNDLE_VERSION = 1


def export_bundle(passphrase: str, vault_path: Path = None) -> str:
    """Export the vault as a portable encrypted JSON bundle string.

    The bundle is re-encrypted with the given passphrase so it can be
    shared with teammates who know the passphrase.

    Returns a base64-encoded JSON string.
    """
    vault_path = vault_path or Path(VAULT_FILENAME)
    data = _load_raw(vault_path)

    salt_bytes = bytes.fromhex(data["salt"])
    key = derive_key(passphrase, salt_bytes)

    # Re-encrypt each value with the sharing key
    shared_vars = {}
    for name, ciphertext_hex in data.get("variables", {}).items():
        # Decrypt with original key, then re-encrypt with sharing key
        original_key = derive_key(passphrase, salt_bytes)
        plaintext = decrypt(original_key, bytes.fromhex(ciphertext_hex))
        shared_vars[name] = encrypt(key, plaintext).hex()

    bundle = {
        "version": BUNDLE_VERSION,
        "salt": data["salt"],
        "variables": shared_vars,
    }

    bundle_json = json.dumps(bundle)
    return base64.b64encode(bundle_json.encode()).decode()


def import_bundle(bundle_str: str, passphrase: str, vault_path: Path = None) -> list:
    """Import a vault bundle exported by a teammate.

    Decrypts the bundle using the shared passphrase and merges variables
    into the local vault. Existing variables are overwritten.

    Returns a list of imported variable names.
    """
    vault_path = vault_path or Path(VAULT_FILENAME)

    try:
        bundle_json = base64.b64decode(bundle_str.encode()).decode()
        bundle = json.loads(bundle_json)
    except Exception as exc:
        raise ValueError(f"Invalid bundle format: {exc}") from exc

    if bundle.get("version") != BUNDLE_VERSION:
        raise ValueError(
            f"Unsupported bundle version: {bundle.get('version')}"
        )

    salt_bytes = bytes.fromhex(bundle["salt"])
    key = derive_key(passphrase, salt_bytes)

    # Verify we can decrypt at least one variable (passphrase check)
    imported_names = []
    decrypted_vars = {}
    for name, ciphertext_hex in bundle.get("variables", {}).items():
        try:
            plaintext = decrypt(key, bytes.fromhex(ciphertext_hex))
        except Exception as exc:
            raise ValueError(
                f"Failed to decrypt variable '{name}': wrong passphrase?"
            ) from exc
        decrypted_vars[name] = plaintext
        imported_names.append(name)

    # Merge into local vault
    local_data = _load_raw(vault_path)
    local_salt = bytes.fromhex(local_data["salt"])
    local_key = derive_key(passphrase, local_salt)

    for name, plaintext in decrypted_vars.items():
        local_data["variables"][name] = encrypt(local_key, plaintext).hex()

    _save_raw(vault_path, local_data)
    return imported_names
