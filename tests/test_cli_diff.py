"""Tests for envault/cli_diff.py"""

import pytest
from click.testing import CliRunner

from envault.cli_diff import diff_group
from envault.vault import init_vault, set_variable


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "secret")
    set_variable(path, "secret", "ALPHA", "one")
    set_variable(path, "secret", "BETA", "two")
    return path


@pytest.fixture
def dotenv_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("ALPHA=one\nBETA=changed\nGAMMA=new\n")
    return str(p)


# ---------------------------------------------------------------------------
# cmd_diff_dotenv
# ---------------------------------------------------------------------------

def test_diff_dotenv_shows_added(runner, vault_file, dotenv_file):
    result = runner.invoke(
        diff_group, ["dotenv", vault_file, dotenv_file, "--password", "secret"]
    )
    assert result.exit_code == 0
    assert "+ GAMMA" in result.output


def test_diff_dotenv_shows_changed(runner, vault_file, dotenv_file):
    result = runner.invoke(
        diff_group, ["dotenv", vault_file, dotenv_file, "--password", "secret"]
    )
    assert result.exit_code == 0
    assert "~ BETA" in result.output


def test_diff_dotenv_no_changes(runner, tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "pw")
    set_variable(path, "pw", "X", "1")
    dotenv = tmp_path / ".env"
    dotenv.write_text("X=1\n")
    result = runner.invoke(
        diff_group, ["dotenv", path, str(dotenv), "--password", "pw"]
    )
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_diff_dotenv_missing_dotenv(runner, vault_file, tmp_path):
    missing = str(tmp_path / "missing.env")
    result = runner.invoke(
        diff_group, ["dotenv", vault_file, missing, "--password", "secret"]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_diff_dotenv_show_unchanged(runner, vault_file, dotenv_file):
    result = runner.invoke(
        diff_group,
        ["dotenv", vault_file, dotenv_file, "--password", "secret", "--show-unchanged"]
    )
    assert result.exit_code == 0
    assert "ALPHA" in result.output


# ---------------------------------------------------------------------------
# cmd_diff_vaults
# ---------------------------------------------------------------------------

def test_diff_vaults_detects_differences(runner, tmp_path):
    a = str(tmp_path / "a")
    b = str(tmp_path / "b")
    init_vault(a, "pw")
    init_vault(b, "pw")
    set_variable(a, "pw", "ONLY_A", "x")
    set_variable(b, "pw", "ONLY_B", "y")
    result = runner.invoke(
        diff_group,
        ["vaults", a, b, "--password-a", "pw", "--password-b", "pw"]
    )
    assert result.exit_code == 0
    assert "- ONLY_A" in result.output
    assert "+ ONLY_B" in result.output


def test_diff_vaults_identical(runner, tmp_path):
    a = str(tmp_path / "a")
    b = str(tmp_path / "b")
    init_vault(a, "pw")
    init_vault(b, "pw")
    set_variable(a, "pw", "KEY", "val")
    set_variable(b, "pw", "KEY", "val")
    result = runner.invoke(
        diff_group,
        ["vaults", a, b, "--password-a", "pw", "--password-b", "pw"]
    )
    assert result.exit_code == 0
    assert "No differences" in result.output
