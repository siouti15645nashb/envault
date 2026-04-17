import json
import pytest
from pathlib import Path
from envault.env_required import (
    REQUIRED_FILENAME,
    RequiredError,
    mark_required,
    unmark_required,
    list_required,
    check_required,
    _required_path,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_required_filename_constant():
    assert REQUIRED_FILENAME == ".envault_required"


def test_required_path_returns_correct_path(vault_dir):
    path = _required_path(vault_dir)
    assert path == Path(vault_dir) / REQUIRED_FILENAME


def test_list_required_empty_when_no_file(vault_dir):
    assert list_required(vault_dir) == []


def test_mark_required_creates_file(vault_dir):
    mark_required(vault_dir, "API_KEY")
    assert (Path(vault_dir) / REQUIRED_FILENAME).exists()


def test_mark_required_stores_key(vault_dir):
    mark_required(vault_dir, "API_KEY")
    assert "API_KEY" in list_required(vault_dir)


def test_mark_required_idempotent(vault_dir):
    mark_required(vault_dir, "API_KEY")
    mark_required(vault_dir, "API_KEY")
    assert list_required(vault_dir).count("API_KEY") == 1


def test_mark_multiple_required(vault_dir):
    mark_required(vault_dir, "API_KEY")
    mark_required(vault_dir, "DB_URL")
    result = list_required(vault_dir)
    assert "API_KEY" in result
    assert "DB_URL" in result


def test_unmark_required_removes_key(vault_dir):
    mark_required(vault_dir, "API_KEY")
    unmark_required(vault_dir, "API_KEY")
    assert "API_KEY" not in list_required(vault_dir)


def test_unmark_required_raises_if_not_marked(vault_dir):
    with pytest.raises(RequiredError):
        unmark_required(vault_dir, "MISSING_KEY")


def test_check_required_all_present(vault_dir):
    mark_required(vault_dir, "API_KEY")
    mark_required(vault_dir, "DB_URL")
    missing = check_required(vault_dir, ["API_KEY", "DB_URL", "EXTRA"])
    assert missing == []


def test_check_required_reports_missing(vault_dir):
    mark_required(vault_dir, "API_KEY")
    mark_required(vault_dir, "DB_URL")
    missing = check_required(vault_dir, ["API_KEY"])
    assert "DB_URL" in missing


def test_check_required_empty_vault_no_required(vault_dir):
    missing = check_required(vault_dir, [])
    assert missing == []
