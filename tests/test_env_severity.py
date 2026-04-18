import os
import pytest
from envault.env_severity import (
    SEVERITY_FILENAME, VALID_LEVELS,
    set_severity, get_severity, remove_severity,
    list_severity, get_by_level, SeverityError,
    _severity_path
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_severity_filename_constant():
    assert SEVERITY_FILENAME == ".envault_severity.json"


def test_valid_levels_constant():
    assert "low" in VALID_LEVELS
    assert "medium" in VALID_LEVELS
    assert "high" in VALID_LEVELS
    assert "critical" in VALID_LEVELS


def test_severity_path_returns_correct_path(vault_dir):
    path = _severity_path(vault_dir)
    assert path == os.path.join(vault_dir, SEVERITY_FILENAME)


def test_list_severity_empty_when_no_file(vault_dir):
    assert list_severity(vault_dir) == {}


def test_get_severity_none_when_no_file(vault_dir):
    assert get_severity(vault_dir, "MY_KEY") is None


def test_set_severity_creates_file(vault_dir):
    set_severity(vault_dir, "API_KEY", "high")
    assert os.path.exists(_severity_path(vault_dir))


def test_set_severity_stores_level(vault_dir):
    set_severity(vault_dir, "API_KEY", "critical")
    assert get_severity(vault_dir, "API_KEY") == "critical"


def test_set_severity_invalid_level_raises(vault_dir):
    with pytest.raises(SeverityError):
        set_severity(vault_dir, "API_KEY", "extreme")


def test_set_severity_overwrites_existing(vault_dir):
    set_severity(vault_dir, "API_KEY", "low")
    set_severity(vault_dir, "API_KEY", "high")
    assert get_severity(vault_dir, "API_KEY") == "high"


def test_remove_severity_deletes_entry(vault_dir):
    set_severity(vault_dir, "API_KEY", "medium")
    remove_severity(vault_dir, "API_KEY")
    assert get_severity(vault_dir, "API_KEY") is None


def test_remove_severity_nonexistent_raises(vault_dir):
    with pytest.raises(SeverityError):
        remove_severity(vault_dir, "MISSING_KEY")


def test_list_severity_returns_all(vault_dir):
    set_severity(vault_dir, "KEY_A", "low")
    set_severity(vault_dir, "KEY_B", "critical")
    data = list_severity(vault_dir)
    assert data["KEY_A"] == "low"
    assert data["KEY_B"] == "critical"


def test_get_by_level_returns_matching(vault_dir):
    set_severity(vault_dir, "KEY_A", "high")
    set_severity(vault_dir, "KEY_B", "low")
    set_severity(vault_dir, "KEY_C", "high")
    result = get_by_level(vault_dir, "high")
    assert "KEY_A" in result
    assert "KEY_C" in result
    assert "KEY_B" not in result


def test_get_by_level_invalid_raises(vault_dir):
    with pytest.raises(SeverityError):
        get_by_level(vault_dir, "unknown")
