"""Tests for envault/env_groups.py"""

import pytest
from envault.env_groups import (
    GROUPS_FILENAME,
    GroupError,
    add_to_group,
    remove_from_group,
    list_groups,
    get_group_members,
    delete_group,
    find_groups_for_key,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_groups_filename_constant():
    assert GROUPS_FILENAME == ".envault_groups.json"


def test_list_groups_empty_when_no_file(vault_dir):
    assert list_groups(vault_dir) == {}


def test_add_to_group_creates_group(vault_dir):
    add_to_group(vault_dir, "backend", "DB_HOST")
    groups = list_groups(vault_dir)
    assert "backend" in groups
    assert "DB_HOST" in groups["backend"]


def test_add_to_group_idempotent(vault_dir):
    add_to_group(vault_dir, "backend", "DB_HOST")
    add_to_group(vault_dir, "backend", "DB_HOST")
    assert list_groups(vault_dir)["backend"].count("DB_HOST") == 1


def test_add_to_group_multiple_keys(vault_dir):
    add_to_group(vault_dir, "backend", "DB_HOST")
    add_to_group(vault_dir, "backend", "DB_PORT")
    members = get_group_members(vault_dir, "backend")
    assert "DB_HOST" in members
    assert "DB_PORT" in members


def test_add_empty_group_name_raises(vault_dir):
    with pytest.raises(GroupError, match="empty"):
        add_to_group(vault_dir, "", "DB_HOST")


def test_add_empty_key_raises(vault_dir):
    with pytest.raises(GroupError, match="empty"):
        add_to_group(vault_dir, "backend", "")


def test_remove_from_group_success(vault_dir):
    add_to_group(vault_dir, "backend", "DB_HOST")
    remove_from_group(vault_dir, "backend", "DB_HOST")
    assert list_groups(vault_dir) == {}


def test_remove_nonexistent_group_raises(vault_dir):
    with pytest.raises(GroupError, match="does not exist"):
        remove_from_group(vault_dir, "ghost", "KEY")


def test_remove_nonexistent_key_raises(vault_dir):
    add_to_group(vault_dir, "backend", "DB_HOST")
    with pytest.raises(GroupError, match="not in group"):
        remove_from_group(vault_dir, "backend", "MISSING")


def test_get_group_members_success(vault_dir):
    add_to_group(vault_dir, "frontend", "API_URL")
    assert get_group_members(vault_dir, "frontend") == ["API_URL"]


def test_get_group_members_nonexistent_raises(vault_dir):
    with pytest.raises(GroupError):
        get_group_members(vault_dir, "nope")


def test_delete_group_success(vault_dir):
    add_to_group(vault_dir, "infra", "AWS_KEY")
    delete_group(vault_dir, "infra")
    assert "infra" not in list_groups(vault_dir)


def test_delete_nonexistent_group_raises(vault_dir):
    with pytest.raises(GroupError):
        delete_group(vault_dir, "missing")


def test_find_groups_for_key(vault_dir):
    add_to_group(vault_dir, "backend", "SECRET")
    add_to_group(vault_dir, "shared", "SECRET")
    add_to_group(vault_dir, "frontend", "API_URL")
    result = find_groups_for_key(vault_dir, "SECRET")
    assert set(result) == {"backend", "shared"}


def test_find_groups_for_key_not_present(vault_dir):
    add_to_group(vault_dir, "backend", "DB_HOST")
    assert find_groups_for_key(vault_dir, "UNKNOWN") == []
