"""Tests for envault.env_notes and envault.cli_notes."""

import pytest
import os
from click.testing import CliRunner
from envault.env_notes import (
    NOTES_FILENAME, set_note, get_note, remove_note, list_notes, NotesError, _notes_path
)
from envault.cli_notes import notes_group


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_notes_filename_constant():
    assert NOTES_FILENAME == ".envault_notes.json"


def test_notes_path_returns_correct_path(vault_dir):
    p = _notes_path(vault_dir)
    assert p.name == NOTES_FILENAME


def test_list_notes_empty_when_no_file(vault_dir):
    assert list_notes(vault_dir) == {}


def test_set_note_creates_file(vault_dir):
    set_note(vault_dir, "DB_URL", "Primary database connection string.")
    notes_file = _notes_path(vault_dir)
    assert notes_file.exists()


def test_set_note_stores_value(vault_dir):
    set_note(vault_dir, "API_KEY", "Third-party API key.")
    assert get_note(vault_dir, "API_KEY") == "Third-party API key."


def test_get_note_returns_none_for_missing(vault_dir):
    assert get_note(vault_dir, "NONEXISTENT") is None


def test_set_note_empty_key_raises(vault_dir):
    with pytest.raises(NotesError):
        set_note(vault_dir, "", "some note")


def test_remove_note_success(vault_dir):
    set_note(vault_dir, "SECRET", "My secret.")
    remove_note(vault_dir, "SECRET")
    assert get_note(vault_dir, "SECRET") is None


def test_remove_note_nonexistent_raises(vault_dir):
    with pytest.raises(NotesError):
        remove_note(vault_dir, "MISSING")


def test_list_notes_returns_all(vault_dir):
    set_note(vault_dir, "A", "note a")
    set_note(vault_dir, "B", "note b")
    notes = list_notes(vault_dir)
    assert notes == {"A": "note a", "B": "note b"}


def test_cli_set_and_get(vault_dir, runner):
    result = runner.invoke(notes_group, ["set", "FOO", "A foo note", "--dir", vault_dir])
    assert result.exit_code == 0
    assert "Note set for 'FOO'" in result.output
    result = runner.invoke(notes_group, ["get", "FOO", "--dir", vault_dir])
    assert "A foo note" in result.output


def test_cli_list_empty(vault_dir, runner):
    result = runner.invoke(notes_group, ["list", "--dir", vault_dir])
    assert "No notes found" in result.output


def test_cli_remove_success(vault_dir, runner):
    set_note(vault_dir, "BAR", "bar note")
    result = runner.invoke(notes_group, ["remove", "BAR", "--dir", vault_dir])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_remove_missing_exits_nonzero(vault_dir, runner):
    result = runner.invoke(notes_group, ["remove", "MISSING", "--dir", vault_dir])
    assert result.exit_code != 0
