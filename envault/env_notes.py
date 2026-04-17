"""Per-variable notes/comments storage for envault."""

import json
import os
from pathlib import Path

NOTES_FILENAME = ".envault_notes.json"


class NotesError(Exception):
    pass


def _notes_path(vault_dir: str) -> Path:
    return Path(vault_dir) / NOTES_FILENAME


def _load_notes(vault_dir: str) -> dict:
    path = _notes_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_notes(vault_dir: str, notes: dict) -> None:
    path = _notes_path(vault_dir)
    with open(path, "w") as f:
        json.dump(notes, f, indent=2)


def set_note(vault_dir: str, key: str, note: str) -> None:
    """Attach a note to a variable key."""
    if not key:
        raise NotesError("Key must not be empty.")
    notes = _load_notes(vault_dir)
    notes[key] = note
    _save_notes(vault_dir, notes)


def get_note(vault_dir: str, key: str) -> str | None:
    """Return the note for a key, or None if not set."""
    return _load_notes(vault_dir).get(key)


def remove_note(vault_dir: str, key: str) -> None:
    """Remove the note for a key. Raises NotesError if not found."""
    notes = _load_notes(vault_dir)
    if key not in notes:
        raise NotesError(f"No note found for key: {key}")
    del notes[key]
    _save_notes(vault_dir, notes)


def list_notes(vault_dir: str) -> dict:
    """Return all key -> note mappings."""
    return _load_notes(vault_dir)
