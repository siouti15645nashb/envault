import pytest
import json
from pathlib import Path
from envault.env_quota import (
    QUOTA_FILENAME,
    DEFAULT_MAX_KEYS,
    QuotaError,
    _quota_path,
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_quota_filename_constant():
    assert QUOTA_FILENAME == ".envault_quota.json"


def test_quota_path_returns_correct_path(vault_dir):
    p = _quota_path(vault_dir)
    assert p.name == QUOTA_FILENAME
    assert str(p).startswith(vault_dir)


def test_get_quota_default_when_no_file(vault_dir):
    assert get_quota(vault_dir) == DEFAULT_MAX_KEYS


def test_set_quota_creates_file(vault_dir):
    set_quota(vault_dir, 50)
    assert Path(vault_dir, QUOTA_FILENAME).exists()


def test_set_quota_stores_value(vault_dir):
    set_quota(vault_dir, 75)
    assert get_quota(vault_dir) == 75


def test_set_quota_raises_on_zero(vault_dir):
    with pytest.raises(QuotaError):
        set_quota(vault_dir, 0)


def test_set_quota_raises_on_negative(vault_dir):
    with pytest.raises(QuotaError):
        set_quota(vault_dir, -5)


def test_remove_quota_resets_to_default(vault_dir):
    set_quota(vault_dir, 10)
    remove_quota(vault_dir)
    assert get_quota(vault_dir) == DEFAULT_MAX_KEYS


def test_remove_quota_no_file_is_safe(vault_dir):
    remove_quota(vault_dir)  # should not raise


def test_check_quota_within(vault_dir):
    set_quota(vault_dir, 10)
    assert check_quota(vault_dir, 5) is True


def test_check_quota_at_limit(vault_dir):
    set_quota(vault_dir, 10)
    assert check_quota(vault_dir, 10) is True


def test_check_quota_exceeded(vault_dir):
    set_quota(vault_dir, 10)
    assert check_quota(vault_dir, 11) is False


def test_check_quota_default_limit(vault_dir):
    assert check_quota(vault_dir, DEFAULT_MAX_KEYS) is True
    assert check_quota(vault_dir, DEFAULT_MAX_KEYS + 1) is False
