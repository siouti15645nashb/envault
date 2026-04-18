"""Tests for envault/env_changelog.py and envault/cli_changelog.py."""

import os
import json
import pytest
from click.testing import CliRunner
from envault.vault import init_vault
from envault.env_changelog import (
    CHANGELOG_FILENAME,
    _changelog_path,
    add_entry,
    get_changelog,
    clear_changelog,
)
from envault.cli_changelog import changelog_group


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "password")
    return path


@pytest.fixture
def runner():
    return Runner()


class Runner:
    def __init__(self):
        self._r = CliRunner()

    def invoke(self, *args, input=None):
        return self._r.invoke(changelog_group, args, input=input)


def test_changelog_filename_constant():
    assert CHANGELOG_FILENAME == ".envault_changelog.json"


def test_changelog_path_returns_correct_path(vault_file):
    expected = os.path.join(os.path.dirname(os.path.abspath(vault_file)), CHANGELOG_FILENAME)
    assert _changelog_path(vault_file) == expected


def test_get_changelog_empty_when_no_file(vault_file):
    assert get_changelog(vault_file) == []


def test_add_entry_creates_file(vault_file):
    add_entry(vault_file, action="set", key="FOO")
    assert os.path.exists(_changelog_path(vault_file))


def test_add_entry_stores_correct_fields(vault_file):
    entry = add_entry(vault_file, action="set", key="BAR", note="initial", author="alice")
    assert entry["action"] == "set"
    assert entry["key"] == "BAR"
    assert entry["note"] == "initial"
    assert entry["author"] == "alice"
    assert "timestamp" in entry


def test_add_multiple_entries(vault_file):
    add_entry(vault_file, action="set", key="A")
    add_entry(vault_file, action="delete", key="B")
    entries = get_changelog(vault_file)
    assert len(entries) == 2
    assert entries[0]["key"] == "A"
    assert entries[1]["key"] == "B"


def test_clear_changelog_returns_count(vault_file):
    add_entry(vault_file, action="set", key="X")
    add_entry(vault_file, action="set", key="Y")
    count = clear_changelog(vault_file)
    assert count == 2
    assert get_changelog(vault_file) == []


def test_cli_add_success(vault_file, runner):
    result = runner.invoke("add", "MY_KEY", "set", "--vault", vault_file)
    assert result.exit_code == 0
    assert "MY_KEY" in result.output


def test_cli_log_empty(vault_file, runner):
    result = runner.invoke("log", "--vault", vault_file)
    assert result.exit_code == 0
    assert "No changelog" in result.output


def test_cli_log_shows_entries(vault_file, runner):
    add_entry(vault_file, action="rotate", key="SECRET", author="bob")
    result = runner.invoke("log", "--vault", vault_file)
    assert "rotate" in result.output
    assert "SECRET" in result.output
    assert "bob" in result.output


def test_cli_clear_success(vault_file, runner):
    add_entry(vault_file, action="set", key="Z")
    result = runner.invoke("clear", "--vault", vault_file, input="y\n")
    assert result.exit_code == 0
    assert "Cleared 1" in result.output
