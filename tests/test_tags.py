"""Tests for envault/tags.py"""

import json
import pytest
from pathlib import Path
from envault.vault import init_vault, set_variable
from envault.tags import (
    TagError,
    add_tag,
    remove_tag,
    list_tags,
    find_by_tag,
    all_tags,
)


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / ".envault"
    init_vault(str(path), "password")
    set_variable(str(path), "password", "DB_HOST", "localhost")
    set_variable(str(path), "password", "DB_PORT", "5432")
    set_variable(str(path), "password", "API_KEY", "secret")
    return str(path)


def test_add_tag_success(vault_file):
    add_tag(vault_file, "DB_HOST", "database")
    assert "database" in list_tags(vault_file, "DB_HOST")


def test_add_tag_idempotent(vault_file):
    add_tag(vault_file, "DB_HOST", "database")
    add_tag(vault_file, "DB_HOST", "database")
    assert list_tags(vault_file, "DB_HOST").count("database") == 1


def test_add_tag_nonexistent_variable_raises(vault_file):
    with pytest.raises(TagError, match="MISSING"):
        add_tag(vault_file, "MISSING", "sometag")


def test_remove_tag_success(vault_file):
    add_tag(vault_file, "DB_HOST", "database")
    remove_tag(vault_file, "DB_HOST", "database")
    assert "database" not in list_tags(vault_file, "DB_HOST")


def test_remove_tag_not_present_raises(vault_file):
    with pytest.raises(TagError, match="not found"):
        remove_tag(vault_file, "DB_HOST", "nonexistent")


def test_list_tags_empty_by_default(vault_file):
    assert list_tags(vault_file, "API_KEY") == []


def test_list_tags_multiple(vault_file):
    add_tag(vault_file, "DB_HOST", "database")
    add_tag(vault_file, "DB_HOST", "production")
    tags = list_tags(vault_file, "DB_HOST")
    assert "database" in tags
    assert "production" in tags


def test_find_by_tag_returns_correct_keys(vault_file):
    add_tag(vault_file, "DB_HOST", "database")
    add_tag(vault_file, "DB_PORT", "database")
    add_tag(vault_file, "API_KEY", "api")
    result = find_by_tag(vault_file, "database")
    assert set(result) == {"DB_HOST", "DB_PORT"}


def test_find_by_tag_no_match(vault_file):
    assert find_by_tag(vault_file, "nonexistent") == []


def test_all_tags_returns_unique_sorted(vault_file):
    add_tag(vault_file, "DB_HOST", "database")
    add_tag(vault_file, "DB_PORT", "database")
    add_tag(vault_file, "API_KEY", "api")
    tags = all_tags(vault_file)
    assert tags == ["api", "database"]


def test_all_tags_empty_vault(vault_file):
    assert all_tags(vault_file) == []


def test_tags_persisted_to_disk(vault_file):
    add_tag(vault_file, "DB_HOST", "persistent")
    # Re-read via list_tags to confirm persistence
    assert "persistent" in list_tags(vault_file, "DB_HOST")
