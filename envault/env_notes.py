"""Per-variable notes/comments storage for envault."""

import json
import os
from pathlib import Path

NOTES_FILENAME = ".envault_notes.json"


class NotesError(Exception):
    pass


def _notes_path(vault_path: str) -> Path:
    return Path(vault_path).parent / NOTES_FILENAME


def _load_notes(vault_path: str) -> dict:
    path = _notes_path(vault_path)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_notes(vault_path: str, notes: dict) -> None:
    path = _notes_path(vault_path)
    with open(path, "w") as f:
        json.dump(notes, f, indent=2)


def set_note(vault_path: str, key: str, note: str) -> None:
    """Attach a note to a variable key."""
    if not key:
        raise NotesError("Key must not be empty.")
    notes = _load_notes(vault_path)
    notes[key] = note
    _save_notes(vault_path, notes)


def get_note(vault_path: str, key: str) -> str | None:
    """Return the note for a key, or None if not set."""
    notes = _load_notes(vault_path)
    return notes.get(key)


def remove_note(vault_path: str, key: str) -> None:
    """Remove the note for a key. Silently succeeds if not present."""
    notes = _load_notes(vault_path)
    if key in notes:
        del notes[key]
        _save_notes(vault_path, notes)


def list_notes(vault_path: str) -> dict:
    """Return all key->note mappings."""
    return _load_notes(vault_path)
