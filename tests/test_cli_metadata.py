"""Tests for envault/cli_metadata.py"""

import pytest
from click.testing import CliRunner
from envault.cli_metadata import metadata_group
from envault.vault import init_vault
from envault.env_metadata import set_metadata
import os


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    vf = str(tmp_path / ".envault")
    init_vault(vf, "password")
    return vf


def test_metadata_set_success(runner, vault_file):
    result = runner.invoke(metadata_group, ["set", "MY_KEY", "owner", "alice"])
    assert result.exit_code == 0
    assert "owner=alice" in result.output


def test_metadata_get_shows_values(runner, vault_file):
    set_metadata(vault_file, "MY_KEY", "owner", "alice")
    result = runner.invoke(metadata_group, ["get", "MY_KEY"])
    assert result.exit_code == 0
    assert "owner=alice" in result.output


def test_metadata_get_empty(runner, vault_file):
    result = runner.invoke(metadata_group, ["get", "UNKNOWN"])
    assert result.exit_code == 0
    assert "No metadata" in result.output


def test_metadata_remove_success(runner, vault_file):
    set_metadata(vault_file, "MY_KEY", "owner", "alice")
    result = runner.invoke(metadata_group, ["remove", "MY_KEY", "owner"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_metadata_remove_not_found_fails(runner, vault_file):
    result = runner.invoke(metadata_group, ["remove", "MY_KEY", "nonexistent"])
    assert result.exit_code != 0


def test_metadata_clear_success(runner, vault_file):
    set_metadata(vault_file, "MY_KEY", "owner", "alice")
    result = runner.invoke(metadata_group, ["clear", "MY_KEY"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_metadata_list_empty(runner, vault_file):
    result = runner.invoke(metadata_group, ["list"])
    assert result.exit_code == 0
    assert "No metadata" in result.output


def test_metadata_list_shows_entries(runner, vault_file):
    set_metadata(vault_file, "KEY_A", "env", "prod")
    result = runner.invoke(metadata_group, ["list"])
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "env=prod" in result.output
