"""Tests for envault.env_compare."""
import json
import pytest
from pathlib import Path
from envault.vault import init_vault, set_variable
from envault.env_compare import compare_vaults, compare_summary, CompareError

PASSWORD = "testpass"


@pytest.fixture
def vault_a(tmp_path):
    p = str(tmp_path / "a.vault")
    init_vault(p, PASSWORD)
    set_variable(p, PASSWORD, "SHARED", "same")
    set_variable(p, PASSWORD, "ONLY_A", "aval")
    set_variable(p, PASSWORD, "DIFF", "value_a")
    return p


@pytest.fixture
def vault_b(tmp_path):
    p = str(tmp_path / "b.vault")
    init_vault(p, PASSWORD)
    set_variable(p, PASSWORD, "SHARED", "same")
    set_variable(p, PASSWORD, "ONLY_B", "bval")
    set_variable(p, PASSWORD, "DIFF", "value_b")
    return p


def test_only_in_a(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert "ONLY_A" in result.only_in_a


def test_only_in_b(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert "ONLY_B" in result.only_in_b


def test_same_keys(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert "SHARED" in result.same


def test_different_keys(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert "DIFF" in result.different


def test_has_differences(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert result.has_differences()


def test_no_differences(vault_a, tmp_path):
    vault_c = str(tmp_path / "c.vault")
    init_vault(vault_c, PASSWORD)
    set_variable(vault_c, PASSWORD, "SHARED", "same")
    set_variable(vault_c, PASSWORD, "ONLY_A", "aval")
    set_variable(vault_c, PASSWORD, "DIFF", "value_a")
    result = compare_vaults(vault_a, PASSWORD, vault_c, PASSWORD)
    assert not result.has_differences()


def test_compare_summary_keys(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    summary = compare_summary(result)
    assert set(summary.keys()) == {"only_in_a", "only_in_b", "same", "different"}


def test_compare_error_bad_vault(tmp_path, vault_b):
    with pytest.raises(CompareError):
        compare_vaults(str(tmp_path / "missing.vault"), PASSWORD, vault_b, PASSWORD)
