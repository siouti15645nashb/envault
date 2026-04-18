"""Tests for envault/env_source.py"""

import json
import pytest
from pathlib import Path
from envault.env_source import (
    SOURCE_FILENAME,
    VALID_SOURCES,
    SourceError,
    _source_path,
    set_source,
    get_source,
    remove_source,
    list_sources,
)
from envault.vault import init_vault


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "password")
    return path


def test_source_filename_constant():
    assert SOURCE_FILENAME == ".envault_sources.json"


def test_valid_sources_constant():
    assert "manual" in VALID_SOURCES
    assert "dotenv" in VALID_SOURCES
    assert "ci" in VALID_SOURCES


def test_source_path_returns_correct_path(vault_file):
    p = _source_path(vault_file)
    assert p.name == SOURCE_FILENAME
    assert p.parent == Path(vault_file).parent


def test_list_sources_empty_when_no_file(vault_file):
    assert list_sources(vault_file) == {}


def test_set_source_creates_file(vault_file):
    set_source(vault_file, "API_KEY", "manual")
    p = _source_path(vault_file)
    assert p.exists()


def test_set_source_stores_value(vault_file):
    set_source(vault_file, "DB_URL", "dotenv")
    data = list_sources(vault_file)
    assert data["DB_URL"] == "dotenv"


def test_get_source_returns_value(vault_file):
    set_source(vault_file, "TOKEN", "ci")
    assert get_source(vault_file, "TOKEN") == "ci"


def test_get_source_returns_none_when_not_set(vault_file):
    assert get_source(vault_file, "MISSING") is None


def test_set_source_invalid_raises(vault_file):
    with pytest.raises(SourceError):
        set_source(vault_file, "KEY", "invalid_source")


def test_remove_source_returns_true(vault_file):
    set_source(vault_file, "KEY", "manual")
    assert remove_source(vault_file, "KEY") is True


def test_remove_source_deletes_entry(vault_file):
    set_source(vault_file, "KEY", "shell")
    remove_source(vault_file, "KEY")
    assert get_source(vault_file, "KEY") is None


def test_remove_source_returns_false_if_missing(vault_file):
    assert remove_source(vault_file, "NONEXISTENT") is False


def test_list_sources_returns_all(vault_file):
    set_source(vault_file, "A", "manual")
    set_source(vault_file, "B", "ci")
    data = list_sources(vault_file)
    assert data["A"] == "manual"
    assert data["B"] == "ci"
