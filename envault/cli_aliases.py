"""CLI commands for managing variable aliases."""

import click
from envault.env_aliases import (
    AliasError,
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
)


@click.group("alias")
def alias_group():
    """Manage variable aliases."""


@alias_group.command("add")
@click.argument("alias")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_alias_add(alias, key, vault):
    """Add an alias pointing to a vault key."""
    try:
        add_alias(vault, alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' added.")
    except AliasError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_group.command("remove")
@click.argument("alias")
@click.option("--vault", default=".envault", show_default=True)
def cmd_alias_remove(alias, vault):
    """Remove an alias."""
    try:
        remove_alias(vault, alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_group.command("resolve")
@click.argument("alias")
@click.option("--vault", default=".envault", show_default=True)
def cmd_alias_resolve(alias, vault):
    """Resolve an alias to its target key."""
    try:
        key = resolve_alias(vault, alias)
        click.echo(key)
    except AliasError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alias_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_alias_list(vault):
    """List all aliases."""
    aliases = list_aliases(vault)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, key in sorted(aliases.items()):
        click.echo(f"{alias} -> {key}")
