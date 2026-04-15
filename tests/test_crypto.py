"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt, derive_key, generate_salt, SALT_SIZE


def test_generate_salt_length():
    salt = generate_salt()
    assert len(salt) == SALT_SIZE


def test_generate_salt_is_random():
    assert generate_salt() != generate_salt()


def test_derive_key_is_deterministic():
    salt = generate_salt()
    key1 = derive_key("password", salt)
    key2 = derive_key("password", salt)
    assert key1 == key2


def test_derive_key_differs_with_different_salt():
    key1 = derive_key("password", generate_salt())
    key2 = derive_key("password", generate_salt())
    assert key1 != key2


def test_derive_key_differs_with_different_password():
    salt = generate_salt()
    key1 = derive_key("password1", salt)
    key2 = derive_key("password2", salt)
    assert key1 != key2


def test_encrypt_returns_bytes():
    result = encrypt("SECRET=abc123", "mypassword")
    assert isinstance(result, bytes)


def test_encrypt_output_longer_than_salt():
    result = encrypt("SECRET=abc123", "mypassword")
    assert len(result) > SALT_SIZE


def test_encrypt_decrypt_roundtrip():
    plaintext = "API_KEY=supersecret\nDB_PASS=hunter2"
    password = "strongpassword"
    encrypted = encrypt(plaintext, password)
    decrypted = decrypt(encrypted, password)
    assert decrypted == plaintext


def test_decrypt_wrong_password_raises():
    encrypted = encrypt("VALUE=123", "correctpassword")
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encrypted, "wrongpassword")


def test_decrypt_corrupted_data_raises():
    encrypted = encrypt("VALUE=123", "password")
    corrupted = encrypted[:SALT_SIZE] + b"\x00" * (len(encrypted) - SALT_SIZE)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(corrupted, "password")


def test_decrypt_empty_data_raises():
    with pytest.raises((ValueError, Exception)):
        decrypt(b"", "password")


def test_two_encryptions_of_same_plaintext_differ():
    plaintext = "SECRET=value"
    password = "pass"
    assert encrypt(plaintext, password) != encrypt(plaintext, password)
