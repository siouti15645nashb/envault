"""Tests for envault/diff.py"""

import os
import pytest

from envault.diff import (
    DiffResult,
    diff_dicts,
    diff_vault_vs_dotenv,
    diff_vaults,
    parse_dotenv,
)
from envault.vault import init_vault, set_variable


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "secret")
    set_variable(path, "secret", "KEY_A", "value_a")
    set_variable(path, "secret", "KEY_B", "value_b")
    return path


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY_A=value_a\nKEY_C=value_c\n# comment\nKEY_B=different\n")
    return str(p)


# ---------------------------------------------------------------------------
# parse_dotenv
# ---------------------------------------------------------------------------

def test_parse_dotenv_basic(dotenv_file):
    result = parse_dotenv(dotenv_file)
    assert result == {"KEY_A": "value_a", "KEY_C": "value_c", "KEY_B": "different"}


def test_parse_dotenv_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_dotenv(str(tmp_path / "missing.env"))


def test_parse_dotenv_ignores_comments_and_blanks(tmp_path):
    p = tmp_path / ".env"
    p.write_text("# comment\n\nFOO=bar\n")
    assert parse_dotenv(str(p)) == {"FOO": "bar"}


# ---------------------------------------------------------------------------
# diff_dicts
# ---------------------------------------------------------------------------

def test_diff_dicts_added():
    result = diff_dicts({}, {"NEW": "1"})
    assert result.added == ["NEW"]
    assert not result.removed
    assert result.has_changes


def test_diff_dicts_removed():
    result = diff_dicts({"OLD": "1"}, {})
    assert result.removed == ["OLD"]
    assert not result.added


def test_diff_dicts_changed():
    result = diff_dicts({"K": "a"}, {"K": "b"})
    assert result.changed == ["K"]
    assert not result.unchanged


def test_diff_dicts_unchanged():
    result = diff_dicts({"K": "a"}, {"K": "a"})
    assert result.unchanged == ["K"]
    assert not result.has_changes


def test_diff_dicts_mixed():
    left = {"A": "1", "B": "2", "C": "3"}
    right = {"A": "1", "B": "changed", "D": "4"}
    result = diff_dicts(left, right)
    assert result.unchanged == ["A"]
    assert result.changed == ["B"]
    assert result.removed == ["C"]
    assert result.added == ["D"]


# ---------------------------------------------------------------------------
# diff_vault_vs_dotenv
# ---------------------------------------------------------------------------

def test_diff_vault_vs_dotenv(vault_file, dotenv_file):
    result = diff_vault_vs_dotenv(vault_file, "secret", dotenv_file)
    assert "KEY_C" in result.added
    assert "KEY_B" in result.changed
    assert "KEY_A" in result.unchanged


# ---------------------------------------------------------------------------
# diff_vaults
# ---------------------------------------------------------------------------

def test_diff_vaults(tmp_path):
    path_a = str(tmp_path / "vault_a")
    path_b = str(tmp_path / "vault_b")
    init_vault(path_a, "pw")
    init_vault(path_b, "pw")
    set_variable(path_a, "pw", "SHARED", "same")
    set_variable(path_b, "pw", "SHARED", "same")
    set_variable(path_a, "pw", "ONLY_A", "x")
    set_variable(path_b, "pw", "ONLY_B", "y")
    result = diff_vaults(path_a, "pw", path_b, "pw")
    assert "ONLY_A" in result.removed
    assert "ONLY_B" in result.added
    assert "SHARED" in result.unchanged
