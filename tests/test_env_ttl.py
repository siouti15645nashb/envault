"""Tests for envault/env_ttl.py"""

import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from envault.env_ttl import (
    TTL_FILENAME, TTLError, _ttl_path, set_ttl, remove_ttl,
    is_expired, list_ttl, get_expired_keys
)


@pytest.fixture
def vault_file(tmp_path):
    p = tmp_path / ".envault"
    p.write_text('{"salt": "abc", "variables": {}}')
    return str(p)


def test_ttl_filename_constant():
    assert TTL_FILENAME == ".envault_ttl.json"


def test_ttl_path_returns_correct_path(vault_file, tmp_path):
    assert _ttl_path(vault_file) == str(tmp_path / TTL_FILENAME)


def test_list_ttl_empty_when_no_file(vault_file):
    assert list_ttl(vault_file) == {}


def test_set_ttl_creates_file(vault_file, tmp_path):
    set_ttl(vault_file, "MY_KEY", 3600)
    assert (tmp_path / TTL_FILENAME).exists()


def test_set_ttl_returns_future_datetime(vault_file):
    expiry = set_ttl(vault_file, "MY_KEY", 60)
    assert expiry > datetime.utcnow()


def test_set_ttl_invalid_seconds_raises(vault_file):
    with pytest.raises(TTLError):
        set_ttl(vault_file, "MY_KEY", 0)
    with pytest.raises(TTLError):
        set_ttl(vault_file, "MY_KEY", -10)


def test_list_ttl_after_set(vault_file):
    set_ttl(vault_file, "FOO", 100)
    data = list_ttl(vault_file)
    assert "FOO" in data


def test_remove_ttl_success(vault_file):
    set_ttl(vault_file, "FOO", 100)
    remove_ttl(vault_file, "FOO")
    assert "FOO" not in list_ttl(vault_file)


def test_remove_ttl_missing_key_raises(vault_file):
    with pytest.raises(TTLError):
        remove_ttl(vault_file, "NONEXISTENT")


def test_is_expired_false_for_future(vault_file):
    set_ttl(vault_file, "KEY", 3600)
    assert is_expired(vault_file, "KEY") is False


def test_is_expired_true_for_past(vault_file):
    past = (datetime.utcnow() - timedelta(seconds=10)).isoformat()
    ttl_path = _ttl_path(vault_file)
    with open(ttl_path, "w") as f:
        json.dump({"KEY": past}, f)
    assert is_expired(vault_file, "KEY") is True


def test_is_expired_false_for_unknown_key(vault_file):
    assert is_expired(vault_file, "UNKNOWN") is False


def test_get_expired_keys(vault_file):
    past = (datetime.utcnow() - timedelta(seconds=5)).isoformat()
    future = (datetime.utcnow() + timedelta(seconds=3600)).isoformat()
    ttl_path = _ttl_path(vault_file)
    with open(ttl_path, "w") as f:
        json.dump({"OLD": past, "NEW": future}, f)
    expired = get_expired_keys(vault_file)
    assert "OLD" in expired
    assert "NEW" not in expired
