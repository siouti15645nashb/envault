"""Tests for envault.cli_compare."""
import pytest
from click.testing import CliRunner
from envault.vault import init_vault, set_variable
from envault.cli_compare import compare_group

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_pair(tmp_path):
    a = str(tmp_path / "a.vault")
    b = str(tmp_path / "b.vault")
    init_vault(a, PASSWORD)
    init_vault(b, PASSWORD)
    set_variable(a, PASSWORD, "KEY1", "val1")
    set_variable(b, PASSWORD, "KEY1", "val1")
    set_variable(a, PASSWORD, "ONLY_A", "x")
    set_variable(b, PASSWORD, "ONLY_B", "y")
    set_variable(a, PASSWORD, "DIFF", "aaa")
    set_variable(b, PASSWORD, "DIFF", "bbb")
    return a, b


def test_compare_shows_only_in_a(runner, vault_pair):
    a, b = vault_pair
    result = runner.invoke(compare_group, ["run", a, b, "--password-a", PASSWORD, "--password-b", PASSWORD])
    assert "ONLY_A" in result.output


def test_compare_shows_only_in_b(runner, vault_pair):
    a, b = vault_pair
    result = runner.invoke(compare_group, ["run", a, b, "--password-a", PASSWORD, "--password-b", PASSWORD])
    assert "ONLY_B" in result.output


def test_compare_shows_different(runner, vault_pair):
    a, b = vault_pair
    result = runner.invoke(compare_group, ["run", a, b, "--password-a", PASSWORD, "--password-b", PASSWORD])
    assert "DIFF" in result.output


def test_compare_identical_vaults_exits_zero(runner, tmp_path):
    a = str(tmp_path / "a.vault")
    b = str(tmp_path / "b.vault")
    init_vault(a, PASSWORD)
    init_vault(b, PASSWORD)
    set_variable(a, PASSWORD, "K", "v")
    set_variable(b, PASSWORD, "K", "v")
    result = runner.invoke(compare_group, ["run", a, b, "--password-a", PASSWORD, "--password-b", PASSWORD])
    assert result.exit_code == 0
    assert "identical" in result.output


def test_compare_missing_vault_exits_nonzero(runner, tmp_path, vault_pair):
    _, b = vault_pair
    result = runner.invoke(compare_group, ["run", str(tmp_path / "nope.vault"), b, "--password-a", PASSWORD, "--password-b", PASSWORD])
    assert result.exit_code != 0
