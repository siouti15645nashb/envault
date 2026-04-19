import os
import pytest
from envault.env_timezone import (
    TIMEZONE_FILENAME,
    VALID_TIMEZONES,
    TimezoneError,
    _timezone_path,
    set_timezone,
    get_timezone,
    remove_timezone,
    list_timezones,
)
from envault.vault import init_vault


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "password")
    return path


def test_timezone_filename_constant():
    assert TIMEZONE_FILENAME == ".envault_timezone"


def test_valid_timezones_includes_common():
    assert "UTC" in VALID_TIMEZONES
    assert "America/New_York" in VALID_TIMEZONES
    assert "Europe/London" in VALID_TIMEZONES


def test_timezone_path_returns_correct_path(vault_file):
    path = _timezone_path(vault_file)
    expected_dir = os.path.dirname(os.path.abspath(vault_file))
    assert path == os.path.join(expected_dir, TIMEZONE_FILENAME)


def test_list_timezones_empty_when_no_file(vault_file):
    result = list_timezones(vault_file)
    assert result == {}


def test_get_timezone_none_when_not_set(vault_file):
    assert get_timezone(vault_file, "MY_KEY") is None


def test_set_timezone_creates_file(vault_file):
    set_timezone(vault_file, "MY_KEY", "UTC")
    path = _timezone_path(vault_file)
    assert os.path.exists(path)


def test_set_timezone_stores_value(vault_file):
    set_timezone(vault_file, "MY_KEY", "Europe/Berlin")
    assert get_timezone(vault_file, "MY_KEY") == "Europe/Berlin"


def test_set_timezone_invalid_raises(vault_file):
    with pytest.raises(TimezoneError, match="Invalid timezone"):
        set_timezone(vault_file, "MY_KEY", "Mars/Olympus")


def test_set_timezone_overwrites_existing(vault_file):
    set_timezone(vault_file, "MY_KEY", "UTC")
    set_timezone(vault_file, "MY_KEY", "Asia/Tokyo")
    assert get_timezone(vault_file, "MY_KEY") == "Asia/Tokyo"


def test_remove_timezone_success(vault_file):
    set_timezone(vault_file, "MY_KEY", "UTC")
    remove_timezone(vault_file, "MY_KEY")
    assert get_timezone(vault_file, "MY_KEY") is None


def test_remove_timezone_nonexistent_raises(vault_file):
    with pytest.raises(TimezoneError, match="No timezone set"):
        remove_timezone(vault_file, "MISSING_KEY")


def test_list_timezones_returns_all(vault_file):
    set_timezone(vault_file, "KEY_A", "UTC")
    set_timezone(vault_file, "KEY_B", "Asia/Shanghai")
    result = list_timezones(vault_file)
    assert result["KEY_A"] == "UTC"
    assert result["KEY_B"] == "Asia/Shanghai"
