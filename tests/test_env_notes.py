"""Tests for envault.env_notes module."""

import json
import os
import pytest

from envault.env_notes import (
    NOTES_FILENAME,
    NotesError,
    _notes_path,
    set_note,
    get_note,
    remove_note,
    list_notes,
)


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    vf.write_text("{}")
    return str(vf)


def test_notes_filename_constant():
    assert NOTES_FILENAME == ".envault_notes.json"


def test_notes_path_returns_correct_path(vault_file, tmp_path):
    path = _notes_path(vault_file)
    assert path == tmp_path / NOTES_FILENAME


def test_list_notes_empty_when_no_file(vault_file):
    assert list_notes(vault_file) == {}


def test_set_note_creates_file(vault_file, tmp_path):
    set_note(vault_file, "MY_KEY", "This is important")
    notes_file = tmp_path / NOTES_FILENAME
    assert notes_file.exists()


def test_set_note_stores_content(vault_file):
    set_note(vault_file, "MY_KEY", "Used for auth")
    assert get_note(vault_file, "MY_KEY") == "Used for auth"


def test_get_note_returns_none_when_missing(vault_file):
    assert get_note(vault_file, "NONEXISTENT") is None


def test_set_note_empty_key_raises(vault_file):
    with pytest.raises(NotesError):
        set_note(vault_file, "", "some note")


def test_set_note_overwrites_existing(vault_file):
    set_note(vault_file, "KEY", "old note")
    set_note(vault_file, "KEY", "new note")
    assert get_note(vault_file, "KEY") == "new note"


def test_remove_note_deletes_entry(vault_file):
    set_note(vault_file, "KEY", "some note")
    remove_note(vault_file, "KEY")
    assert get_note(vault_file, "KEY") is None


def test_remove_note_silent_if_missing(vault_file):
    # Should not raise
    remove_note(vault_file, "NONEXISTENT")


def test_list_notes_returns_all(vault_file):
    set_note(vault_file, "A", "note a")
    set_note(vault_file, "B", "note b")
    notes = list_notes(vault_file)
    assert notes == {"A": "note a", "B": "note b"}
