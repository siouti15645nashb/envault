"""CLI commands for tag management."""

import click
from envault.tags import TagError, add_tag, remove_tag, list_tags, find_by_tag, all_tags
from envault.vault import VaultError

DEFAULT_VAULT = ".envault"


@click.group(name="tags")
def tags_group():
    """Manage tags on vault variables."""


@tags_group.command(name="add")
@click.argument("key")
@click.argument("tag")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_tag_add(key, tag, vault):
    """Add TAG to variable KEY."""
    try:
        add_tag(vault, key, tag)
        click.echo(f"Tag '{tag}' added to '{key}'.")
    except (TagError, VaultError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tags_group.command(name="remove")
@click.argument("key")
@click.argument("tag")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_tag_remove(key, tag, vault):
    """Remove TAG from variable KEY."""
    try:
        remove_tag(vault, key, tag)
        click.echo(f"Tag '{tag}' removed from '{key}'.")
    except (TagError, VaultError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tags_group.command(name="list")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_tag_list(key, vault):
    """List all tags on variable KEY."""
    try:
        tags = list_tags(vault, key)
        if tags:
            click.echo("  ".join(tags))
        else:
            click.echo(f"No tags on '{key}'.")
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tags_group.command(name="find")
@click.argument("tag")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_tag_find(tag, vault):
    """Find all variables with TAG."""
    try:
        keys = find_by_tag(vault, tag)
        if keys:
            for key in keys:
                click.echo(key)
        else:
            click.echo(f"No variables found with tag '{tag}'.")
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tags_group.command(name="all")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_tag_all(vault):
    """List all unique tags in the vault."""
    try:
        tags = all_tags(vault)
        if tags:
            for tag in tags:
                click.echo(tag)
        else:
            click.echo("No tags defined.")
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tags_group.command(name="rename")
@click.argument("old_tag")
@click.argument("new_tag")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_tag_rename(old_tag, new_tag, vault):
    """Rename OLD_TAG to NEW_TAG across all variables in the vault."""
    try:
        keys = find_by_tag(vault, old_tag)
        if not keys:
            click.echo(f"No variables found with tag '{old_tag}'.")
            return
        for key in keys:
            remove_tag(vault, key, old_tag)
            add_tag(vault, key, new_tag)
        click.echo(f"Renamed tag '{old_tag}' to '{new_tag}' on {len(keys)} variable(s).")
    except (TagError, VaultError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
