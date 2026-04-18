"""CLI commands for the vault changelog feature."""

import click
from envault.env_changelog import add_entry, get_changelog, clear_changelog


@click.group(name="changelog")
def changelog_group():
    """Manage vault changelog entries."""


@changelog_group.command(name="add")
@click.argument("key")
@click.argument("action")
@click.option("--note", default="", help="Optional note for this entry.")
@click.option("--author", default="", help="Author of the change.")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def cmd_changelog_add(key, action, note, author, vault):
    """Add a changelog entry for KEY with ACTION."""
    try:
        entry = add_entry(vault, action=action, key=key, note=note, author=author)
        click.echo(f"Logged: [{entry['timestamp']}] {action} {key}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@changelog_group.command(name="log")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def cmd_changelog_log(vault):
    """Display all changelog entries."""
    entries = get_changelog(vault)
    if not entries:
        click.echo("No changelog entries found.")
        return
    for e in entries:
        author = f" by {e['author']}" if e["author"] else ""
        note = f" — {e['note']}" if e["note"] else ""
        click.echo(f"[{e['timestamp']}] {e['action']} {e['key']}{author}{note}")


@changelog_group.command(name="clear")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
@click.confirmation_option(prompt="Clear all changelog entries?")
def cmd_changelog_clear(vault):
    """Clear all changelog entries."""
    count = clear_changelog(vault)
    click.echo(f"Cleared {count} changelog entry/entries.")
