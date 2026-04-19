import os
import pytest
from datetime import datetime, timedelta
from envault.env_retention import (
    RETENTION_FILENAME,
    RetentionError,
    _retention_path,
    set_retention,
    remove_retention,
    get_retention,
    list_retention,
    get_expiring_keys,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_retention_filename_constant():
    assert RETENTION_FILENAME == ".envault_retention.json"


def test_retention_path_returns_correct_path(vault_dir):
    path = _retention_path(vault_dir)
    assert path == os.path.join(vault_dir, RETENTION_FILENAME)


def test_list_retention_empty_when_no_file(vault_dir):
    assert list_retention(vault_dir) == {}


def test_set_retention_creates_file(vault_dir):
    set_retention(vault_dir, "MY_KEY", 30)
    assert os.path.exists(_retention_path(vault_dir))


def test_set_retention_stores_days(vault_dir):
    set_retention(vault_dir, "MY_KEY", 90)
    assert get_retention(vault_dir, "MY_KEY") == 90


def test_set_retention_invalid_days_raises(vault_dir):
    with pytest.raises(RetentionError):
        set_retention(vault_dir, "MY_KEY", 0)
    with pytest.raises(RetentionError):
        set_retention(vault_dir, "MY_KEY", -5)


def test_get_retention_none_when_not_set(vault_dir):
    assert get_retention(vault_dir, "MISSING") is None


def test_remove_retention_success(vault_dir):
    set_retention(vault_dir, "MY_KEY", 30)
    remove_retention(vault_dir, "MY_KEY")
    assert get_retention(vault_dir, "MY_KEY") is None


def test_remove_retention_missing_key_raises(vault_dir):
    with pytest.raises(RetentionError):
        remove_retention(vault_dir, "NONEXISTENT")


def test_list_retention_shows_all_keys(vault_dir):
    set_retention(vault_dir, "KEY_A", 10)
    set_retention(vault_dir, "KEY_B", 60)
    result = list_retention(vault_dir)
    assert result["KEY_A"] == 10
    assert result["KEY_B"] == 60


def test_get_expiring_keys_returns_expired(vault_dir):
    set_retention(vault_dir, "OLD_KEY", 30)
    old_date = (datetime.utcnow() - timedelta(days=45)).isoformat()
    created_at = {"OLD_KEY": old_date}
    expired = get_expiring_keys(vault_dir, created_at)
    assert "OLD_KEY" in expired


def test_get_expiring_keys_excludes_fresh(vault_dir):
    set_retention(vault_dir, "NEW_KEY", 30)
    recent_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
    created_at = {"NEW_KEY": recent_date}
    expired = get_expiring_keys(vault_dir, created_at)
    assert "NEW_KEY" not in expired


def test_get_expiring_keys_ignores_missing_created_at(vault_dir):
    set_retention(vault_dir, "KEY_X", 30)
    expired = get_expiring_keys(vault_dir, {})
    assert "KEY_X" not in expired
