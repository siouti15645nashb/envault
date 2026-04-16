"""Tests for envault.env_merge."""

import pytest
import os
from envault.vault import init_vault, set_variable, get_variable
from envault.env_merge import merge_vaults, MergeError


PASSWORD = "testpass"


@pytest.fixture
def vault_pair(tmp_path):
    src = str(tmp_path / "source.vault")
    dst = str(tmp_path / "dest.vault")
    init_vault(src, PASSWORD)
    init_vault(dst, PASSWORD)
    return src, dst


def test_merge_all_variables(vault_pair):
    src, dst = vault_pair
    set_variable(src, "FOO", "foo_val", PASSWORD)
    set_variable(src, "BAR", "bar_val", PASSWORD)
    result = merge_vaults(src, dst, PASSWORD)
    assert set(result["merged"]) == {"FOO", "BAR"}
    assert result["skipped"] == []


def test_merged_values_readable(vault_pair):
    src, dst = vault_pair
    set_variable(src, "FOO", "hello", PASSWORD)
    merge_vaults(src, dst, PASSWORD)
    assert get_variable(dst, "FOO", PASSWORD) == "hello"


def test_merge_skips_existing_without_overwrite(vault_pair):
    src, dst = vault_pair
    set_variable(src, "FOO", "new_val", PASSWORD)
    set_variable(dst, "FOO", "old_val", PASSWORD)
    result = merge_vaults(src, dst, PASSWORD)
    assert "FOO" in result["skipped"]
    assert get_variable(dst, "FOO", PASSWORD) == "old_val"


def test_merge_overwrites_when_flag_set(vault_pair):
    src, dst = vault_pair
    set_variable(src, "FOO", "new_val", PASSWORD)
    set_variable(dst, "FOO", "old_val", PASSWORD)
    result = merge_vaults(src, dst, PASSWORD, overwrite=True)
    assert "FOO" in result["merged"]
    assert get_variable(dst, "FOO", PASSWORD) == "new_val"


def test_merge_subset_of_keys(vault_pair):
    src, dst = vault_pair
    set_variable(src, "FOO", "foo_val", PASSWORD)
    set_variable(src, "BAR", "bar_val", PASSWORD)
    result = merge_vaults(src, dst, PASSWORD, keys=["FOO"])
    assert result["merged"] == ["FOO"]
    assert get_variable(dst, "FOO", PASSWORD) == "foo_val"


def test_merge_missing_key_raises(vault_pair):
    src, dst = vault_pair
    with pytest.raises(MergeError, match="not found in source"):
        merge_vaults(src, dst, PASSWORD, keys=["NONEXISTENT"])


def test_merge_invalid_source_raises(vault_pair):
    _, dst = vault_pair
    with pytest.raises(MergeError, match="Cannot load source"):
        merge_vaults("/nonexistent/path.vault", dst, PASSWORD)


def test_merge_invalid_dest_raises(vault_pair):
    src, _ = vault_pair
    with pytest.raises(MergeError, match="Cannot load destination"):
        merge_vaults(src, "/nonexistent/path.vault", PASSWORD)
