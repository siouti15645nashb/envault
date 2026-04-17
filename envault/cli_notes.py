"""CLI commands for managing per-variable notes."""

import click
from envault.env_notes import NotesError, set_note, get_note, remove_note, list_notes


@click.group(name="notes")
def notes_group():
    """Manage notes attached to variables."""


@notes_group.command(name="set")
@click.argument("key")
@click.argument("note")
@click.option("--dir", "vault_dir", default=".", show_default=True, help="Vault directory.")
def cmd_note_set(key, note, vault_dir):
    """Attach a NOTE to KEY."""
    try:
        set_note(vault_dir, key, note)
        click.echo(f"Note set for '{key}'.")
    except NotesError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@notes_group.command(name="get")
@click.argument("key")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def cmd_note_get(key, vault_dir):
    """Show the note for KEY."""
    note = get_note(vault_dir, key)
    if note is None:
        click.echo(f"No note for '{key}'.")
    else:
        click.echo(note)


@notes_group.command(name="remove")
@click.argument("key")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def cmd_note_remove(key, vault_dir):
    """Remove the note for KEY."""
    try:
        remove_note(vault_dir, key)
        click.echo(f"Note removed for '{key}'.")
    except NotesError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@notes_group.command(name="list")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def cmd_note_list(vault_dir):
    """List all notes."""
    notes = list_notes(vault_dir)
    if not notes:
        click.echo("No notes found.")
        return
    for key, note in sorted(notes.items()):
        click.echo(f"{key}: {note}")
