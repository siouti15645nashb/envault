"""Tests for env_classification module."""

import json
import pytest
from pathlib import Path
from envault.env_classification import (
    CLASSIFICATION_FILENAME,
    VALID_LEVELS,
    ClassificationError,
    _classification_path,
    set_classification,
    get_classification,
    remove_classification,
    list_classifications,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_classification_filename_constant():
    assert CLASSIFICATION_FILENAME == ".envault_classification.json"


def test_valid_levels_includes_common():
    for level in ["public", "internal", "confidential", "secret"]:
        assert level in VALID_LEVELS


def test_classification_path_returns_correct_path(vault_dir):
    p = _classification_path(vault_dir)
    assert p.name == CLASSIFICATION_FILENAME
    assert p.parent == Path(vault_dir)


def test_list_classifications_empty_when_no_file(vault_dir):
    assert list_classifications(vault_dir) == {}


def test_set_classification_creates_file(vault_dir):
    set_classification(vault_dir, "API_KEY", "secret")
    p = Path(vault_dir) / CLASSIFICATION_FILENAME
    assert p.exists()


def test_set_classification_stores_level(vault_dir):
    set_classification(vault_dir, "API_KEY", "confidential")
    data = json.loads((Path(vault_dir) / CLASSIFICATION_FILENAME).read_text())
    assert data["API_KEY"] == "confidential"


def test_get_classification_returns_level(vault_dir):
    set_classification(vault_dir, "DB_PASS", "secret")
    assert get_classification(vault_dir, "DB_PASS") == "secret"


def test_get_classification_returns_none_when_not_set(vault_dir):
    assert get_classification(vault_dir, "MISSING") is None


def test_set_classification_invalid_level_raises(vault_dir):
    with pytest.raises(ClassificationError, match="Invalid level"):
        set_classification(vault_dir, "KEY", "top-secret")


def test_remove_classification_success(vault_dir):
    set_classification(vault_dir, "KEY", "internal")
    remove_classification(vault_dir, "KEY")
    assert get_classification(vault_dir, "KEY") is None


def test_remove_classification_not_set_raises(vault_dir):
    with pytest.raises(ClassificationError):
        remove_classification(vault_dir, "NONEXISTENT")


def test_list_classifications_returns_all(vault_dir):
    set_classification(vault_dir, "A", "public")
    set_classification(vault_dir, "B", "secret")
    result = list_classifications(vault_dir)
    assert result == {"A": "public", "B": "secret"}


def test_set_classification_overwrites_existing(vault_dir):
    set_classification(vault_dir, "KEY", "public")
    set_classification(vault_dir, "KEY", "secret")
    assert get_classification(vault_dir, "KEY") == "secret"
