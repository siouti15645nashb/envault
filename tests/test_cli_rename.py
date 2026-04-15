"""Tests for envault/cli_rename.py."""

import pytest
from click.testing import CliRunner

from envault.vault import init_vault, set_variable, get_variable
from envault.cli_rename import rename_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    init_vault(path, "secret")
    set_variable(path, "secret", "OLD_KEY", "old_value")
    set_variable(path, "secret", "EXISTING", "exists")
    return path


def test_mv_success(runner, vault_file):
    result = runner.invoke(
        rename_group, ["mv", "OLD_KEY", "NEW_KEY", "--vault", vault_file, "--password", "secret"]
    )
    assert result.exit_code == 0
    assert "Renamed 'OLD_KEY' to 'NEW_KEY'" in result.output


def test_mv_old_key_removed(runner, vault_file):
    runner.invoke(
        rename_group, ["mv", "OLD_KEY", "NEW_KEY", "--vault", vault_file, "--password", "secret"]
    )
    assert get_variable(vault_file, "secret", "NEW_KEY") == "old_value"


def test_mv_nonexistent_key_fails(runner, vault_file):
    result = runner.invoke(
        rename_group, ["mv", "GHOST", "NEW_KEY", "--vault", vault_file, "--password", "secret"]
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_mv_destination_exists_fails(runner, vault_file):
    result = runner.invoke(
        rename_group, ["mv", "OLD_KEY", "EXISTING", "--vault", vault_file, "--password", "secret"]
    )
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_mv_force_overwrites(runner, vault_file):
    result = runner.invoke(
        rename_group,
        ["mv", "OLD_KEY", "EXISTING", "--vault", vault_file, "--password", "secret", "--force"],
    )
    assert result.exit_code == 0
    assert get_variable(vault_file, "secret", "EXISTING") == "old_value"


def test_cp_success(runner, vault_file):
    result = runner.invoke(
        rename_group, ["cp", "OLD_KEY", "COPY_KEY", "--vault", vault_file, "--password", "secret"]
    )
    assert result.exit_code == 0
    assert "Copied 'OLD_KEY' to 'COPY_KEY'" in result.output


def test_cp_original_preserved(runner, vault_file):
    runner.invoke(
        rename_group, ["cp", "OLD_KEY", "COPY_KEY", "--vault", vault_file, "--password", "secret"]
    )
    assert get_variable(vault_file, "secret", "OLD_KEY") == "old_value"
    assert get_variable(vault_file, "secret", "COPY_KEY") == "old_value"


def test_cp_destination_exists_fails(runner, vault_file):
    result = runner.invoke(
        rename_group, ["cp", "OLD_KEY", "EXISTING", "--vault", vault_file, "--password", "secret"]
    )
    assert result.exit_code == 1
    assert "already exists" in result.output
