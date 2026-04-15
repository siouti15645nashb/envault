"""Tests for envault.rotate — key rotation."""

import json
import pytest
from pathlib import Path

from envault.vault import init_vault, set_variable, get_variable
from envault.rotate import rotate_key, RotationError


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / ".envault"
    init_vault(path, "old-password")
    return path


@pytest.fixture
def populated_vault(vault_file: Path) -> Path:
    set_variable(vault_file, "DB_URL", "postgres://localhost/db", "old-password")
    set_variable(vault_file, "API_KEY", "supersecret", "old-password")
    return vault_file


def test_rotate_key_returns_variable_count(populated_vault: Path) -> None:
    count = rotate_key(populated_vault, "old-password", "new-password", audit=False)
    assert count == 2


def test_rotate_key_empty_vault_returns_zero(vault_file: Path) -> None:
    count = rotate_key(vault_file, "old-password", "new-password", audit=False)
    assert count == 0


def test_rotated_values_readable_with_new_password(populated_vault: Path) -> None:
    rotate_key(populated_vault, "old-password", "new-password", audit=False)
    assert get_variable(populated_vault, "DB_URL", "new-password") == "postgres://localhost/db"
    assert get_variable(populated_vault, "API_KEY", "new-password") == "supersecret"


def test_old_password_fails_after_rotation(populated_vault: Path) -> None:
    rotate_key(populated_vault, "old-password", "new-password", audit=False)
    with pytest.raises(Exception):
        get_variable(populated_vault, "DB_URL", "old-password")


def test_rotate_changes_salt(populated_vault: Path) -> None:
    with open(populated_vault) as f:
        old_data = json.load(f)
    old_salt = old_data["salt"]

    rotate_key(populated_vault, "old-password", "new-password", audit=False)

    with open(populated_vault) as f:
        new_data = json.load(f)
    assert new_data["salt"] != old_salt


def test_wrong_old_password_raises_rotation_error(populated_vault: Path) -> None:
    with pytest.raises(RotationError):
        rotate_key(populated_vault, "wrong-password", "new-password", audit=False)


def test_vault_unchanged_after_failed_rotation(populated_vault: Path) -> None:
    """Vault file should not be modified if rotation fails."""
    with open(populated_vault) as f:
        original_content = f.read()

    with pytest.raises(RotationError):
        rotate_key(populated_vault, "bad-pass", "new-password", audit=False)

    with open(populated_vault) as f:
        current_content = f.read()

    assert current_content == original_content


def test_rotate_records_audit_event(populated_vault: Path) -> None:
    from envault.audit import get_log
    rotate_key(populated_vault, "old-password", "new-password", audit=True)
    log = get_log(populated_vault.parent)
    assert any(entry["event"] == "rotate_key" for entry in log)
