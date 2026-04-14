"""Encryption and decryption utilities for envault using Fernet symmetric encryption."""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT_SIZE = 16
ITERATIONS = 390000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt."""
    return os.urandom(SALT_SIZE)


def encrypt(plaintext: str, password: str) -> bytes:
    """
    Encrypt a plaintext string with a password.

    Returns salt + encrypted bytes concatenated.
    """
    salt = generate_salt()
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return salt + encrypted


def decrypt(data: bytes, password: str) -> str:
    """
    Decrypt data produced by `encrypt`.

    Raises ValueError on invalid password or corrupted data.
    """
    salt = data[:SALT_SIZE]
    encrypted = data[SALT_SIZE:]
    key = derive_key(password, salt)
    f = Fernet(key)
    try:
        return f.decrypt(encrypted).decode()
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid password or corrupted data.") from exc
