"""Tests for envault.env_expiry module."""

import json
import os
from datetime import datetime, timezone, timedelta

import pytest

from envault.env_expiry import (
    EXPIRY_FILENAME, ExpiryError, set_expiry, remove_expiry,
    get_expiry, list_expiring, get_expired, _expiry_path,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_expiry_filename_constant():
    assert EXPIRY_FILENAME == ".envault_expiry.json"


def test_expiry_path_returns_correct_path(vault_dir):
    path = _expiry_path(vault_dir)
    assert path == os.path.join(vault_dir, EXPIRY_FILENAME)


def test_list_expiring_empty_when_no_file(vault_dir):
    assert list_expiring(vault_dir) == {}


def test_set_expiry_creates_file(vault_dir):
    dt = datetime(2025, 12, 31, tzinfo=timezone.utc)
    set_expiry(vault_dir, "API_KEY", dt)
    assert os.path.exists(_expiry_path(vault_dir))


def test_set_expiry_stores_correct_value(vault_dir):
    dt = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    set_expiry(vault_dir, "TOKEN", dt)
    result = get_expiry(vault_dir, "TOKEN")
    assert result is not None
    assert result.year == 2025
    assert result.month == 6
    assert result.day == 15


def test_get_expiry_returns_none_when_not_set(vault_dir):
    assert get_expiry(vault_dir, "MISSING_KEY") is None


def test_remove_expiry_deletes_entry(vault_dir):
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    set_expiry(vault_dir, "DB_PASS", dt)
    remove_expiry(vault_dir, "DB_PASS")
    assert get_expiry(vault_dir, "DB_PASS") is None


def test_remove_expiry_raises_if_not_set(vault_dir):
    with pytest.raises(ExpiryError):
        remove_expiry(vault_dir, "NONEXISTENT")


def test_list_expiring_returns_all_entries(vault_dir):
    dt1 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    dt2 = datetime(2026, 6, 1, tzinfo=timezone.utc)
    set_expiry(vault_dir, "KEY_A", dt1)
    set_expiry(vault_dir, "KEY_B", dt2)
    entries = list_expiring(vault_dir)
    assert "KEY_A" in entries
    assert "KEY_B" in entries


def test_get_expired_returns_past_keys(vault_dir):
    past = datetime.now(timezone.utc) - timedelta(days=1)
    future = datetime.now(timezone.utc) + timedelta(days=1)
    set_expiry(vault_dir, "OLD_KEY", past)
    set_expiry(vault_dir, "NEW_KEY", future)
    expired = get_expired(vault_dir)
    assert "OLD_KEY" in expired
    assert "NEW_KEY" not in expired


def test_get_expired_empty_when_none_expired(vault_dir):
    future = datetime.now(timezone.utc) + timedelta(days=30)
    set_expiry(vault_dir, "FUTURE_KEY", future)
    assert get_expired(vault_dir) == []
