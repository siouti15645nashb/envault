import pytest
import json
from pathlib import Path
from envault.env_deprecation import (
    DEPRECATION_FILENAME,
    DeprecationError,
    _deprecation_path,
    mark_deprecated,
    unmark_deprecated,
    is_deprecated,
    list_deprecated,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_deprecation_filename_constant():
    assert DEPRECATION_FILENAME == ".envault_deprecations.json"


def test_deprecation_path_returns_correct_path(vault_dir):
    p = _deprecation_path(vault_dir)
    assert p.name == DEPRECATION_FILENAME
    assert str(p).startswith(vault_dir)


def test_list_deprecated_empty_when_no_file(vault_dir):
    assert list_deprecated(vault_dir) == {}


def test_is_deprecated_false_when_no_file(vault_dir):
    assert not is_deprecated(vault_dir, "OLD_KEY")


def test_mark_deprecated_creates_file(vault_dir):
    mark_deprecated(vault_dir, "OLD_KEY")
    assert Path(vault_dir, DEPRECATION_FILENAME).exists()


def test_mark_deprecated_stores_key(vault_dir):
    mark_deprecated(vault_dir, "OLD_KEY")
    data = list_deprecated(vault_dir)
    assert "OLD_KEY" in data


def test_mark_deprecated_with_replacement(vault_dir):
    mark_deprecated(vault_dir, "OLD_KEY", replacement="NEW_KEY")
    data = list_deprecated(vault_dir)
    assert data["OLD_KEY"]["replacement"] == "NEW_KEY"


def test_mark_deprecated_without_replacement(vault_dir):
    mark_deprecated(vault_dir, "OLD_KEY")
    data = list_deprecated(vault_dir)
    assert data["OLD_KEY"]["replacement"] is None


def test_mark_deprecated_empty_key_raises(vault_dir):
    with pytest.raises(DeprecationError):
        mark_deprecated(vault_dir, "")


def test_is_deprecated_true_after_mark(vault_dir):
    mark_deprecated(vault_dir, "OLD_KEY")
    assert is_deprecated(vault_dir, "OLD_KEY")


def test_unmark_deprecated_removes_key(vault_dir):
    mark_deprecated(vault_dir, "OLD_KEY")
    unmark_deprecated(vault_dir, "OLD_KEY")
    assert not is_deprecated(vault_dir, "OLD_KEY")


def test_unmark_deprecated_nonexistent_raises(vault_dir):
    with pytest.raises(DeprecationError):
        unmark_deprecated(vault_dir, "MISSING_KEY")


def test_mark_deprecated_idempotent(vault_dir):
    mark_deprecated(vault_dir, "OLD_KEY", replacement="A")
    mark_deprecated(vault_dir, "OLD_KEY", replacement="B")
    data = list_deprecated(vault_dir)
    assert data["OLD_KEY"]["replacement"] == "B"
