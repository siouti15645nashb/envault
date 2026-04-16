"""Tests for envault.env_copy module."""

import json
import pytest
from pathlib import Path

from envault.vault import init_vault, set_variable, get_variable
from envault.env_copy import copy_variables, CopyError

PASSWORD = "test-password"


@pytest.fixture
def vault_pair(tmp_path):
    src = str(tmp_path / "src.vault")
    dst = str(tmp_path / "dst.vault")
    init_vault(src, PASSWORD)
    init_vault(dst, PASSWORD)
    set_variable(src, PASSWORD, "KEY_A", "alpha")
    set_variable(src, PASSWORD, "KEY_B", "beta")
    return src, dst


def test_copy_all_variables(vault_pair):
    src, dst = vault_pair
    result = copy_variables(src, dst, PASSWORD)
    assert set(result["copied"]) == {"KEY_A", "KEY_B"}
    assert result["skipped"] == []


def test_copied_values_readable(vault_pair):
    src, dst = vault_pair
    copy_variables(src, dst, PASSWORD)
    assert get_variable(dst, PASSWORD, "KEY_A") == "alpha"
    assert get_variable(dst, PASSWORD, "KEY_B") == "beta"


def test_copy_subset_of_keys(vault_pair):
    src, dst = vault_pair
    result = copy_variables(src, dst, PASSWORD, keys=["KEY_A"])
    assert result["copied"] == ["KEY_A"]
    assert result["skipped"] == []


def test_copy_skips_existing_without_overwrite(vault_pair):
    src, dst = vault_pair
    set_variable(dst, PASSWORD, "KEY_A", "original")
    result = copy_variables(src, dst, PASSWORD, keys=["KEY_A"])
    assert result["skipped"] == ["KEY_A"]
    assert get_variable(dst, PASSWORD, "KEY_A") == "original"


def test_copy_overwrites_when_flag_set(vault_pair):
    src, dst = vault_pair
    set_variable(dst, PASSWORD, "KEY_A", "original")
    result = copy_variables(src, dst, PASSWORD, keys=["KEY_A"], overwrite=True)
    assert result["copied"] == ["KEY_A"]
    assert get_variable(dst, PASSWORD, "KEY_A") == "alpha"


def test_copy_missing_key_raises(vault_pair):
    src, dst = vault_pair
    with pytest.raises(CopyError, match="Keys not found"):
        copy_variables(src, dst, PASSWORD, keys=["NONEXISTENT"])


def test_copy_invalid_src_raises(tmp_path):
    dst = str(tmp_path / "dst.vault")
    init_vault(dst, PASSWORD)
    with pytest.raises(CopyError, match="Source vault error"):
        copy_variables(str(tmp_path / "missing.vault"), dst, PASSWORD)


def test_copy_invalid_dst_raises(tmp_path):
    src = str(tmp_path / "src.vault")
    init_vault(src, PASSWORD)
    with pytest.raises(CopyError, match="Destination vault error"):
        copy_variables(src, str(tmp_path / "missing.vault"), PASSWORD)
