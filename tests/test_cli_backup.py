"""Tests for envault.cli_backup commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_backup import backup_group
from envault.backup import create_backup


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "envault.json"
    path.write_text('{"salt": "abc", "variables": {}}')
    return path


def test_backup_create_success(runner, vault_file):
    result = runner.invoke(
        backup_group, ["create", "--vault", str(vault_file)]
    )
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_backup_create_no_vault(runner, tmp_path):
    missing = tmp_path / "missing.json"
    result = runner.invoke(
        backup_group, ["create", "--vault", str(missing)]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_backup_list_empty(runner, vault_file):
    result = runner.invoke(
        backup_group, ["list", "--vault", str(vault_file)]
    )
    assert result.exit_code == 0
    assert "No backups found" in result.output


def test_backup_list_shows_backups(runner, vault_file):
    create_backup(vault_file)
    result = runner.invoke(
        backup_group, ["list", "--vault", str(vault_file)]
    )
    assert result.exit_code == 0
    assert ".bak" in result.output


def test_backup_restore_success(runner, vault_file):
    backup = create_backup(vault_file)
    vault_file.write_text('{"salt": "changed", "variables": {}}')
    result = runner.invoke(
        backup_group,
        ["restore", str(backup), "--vault", str(vault_file), "--yes"],
    )
    assert result.exit_code == 0
    assert "restored" in result.output


def test_backup_restore_missing_backup(runner, tmp_path, vault_file):
    missing = tmp_path / "ghost.bak"
    result = runner.invoke(
        backup_group,
        ["restore", str(missing), "--vault", str(vault_file), "--yes"],
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_backup_delete_success(runner, vault_file):
    backup = create_backup(vault_file)
    result = runner.invoke(
        backup_group, ["delete", str(backup), "--yes"]
    )
    assert result.exit_code == 0
    assert "deleted" in result.output
    assert not backup.exists()


def test_backup_delete_missing(runner, tmp_path):
    missing = tmp_path / "ghost.bak"
    result = runner.invoke(
        backup_group, ["delete", str(missing), "--yes"]
    )
    assert result.exit_code != 0
    assert "Error" in result.output
