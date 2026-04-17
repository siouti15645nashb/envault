"""CLI commands for managing sensitive variable flags."""

import click
from envault.env_sensitive import (
    mark_sensitive,
    unmark_sensitive,
    is_sensitive,
    list_sensitive,
    SensitiveError,
)


@click.group(name="sensitive")
def sensitive_group():
    """Manage sensitive (masked) variable flags."""


@sensitive_group.command(name="add")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_sensitive_add(key, vault):
    """Mark a variable as sensitive."""
    try:
        mark_sensitive(vault, key)
        click.echo(f"Marked '{key}' as sensitive.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@sensitive_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_sensitive_remove(key, vault):
    """Unmark a variable as sensitive."""
    try:
        unmark_sensitive(vault, key)
        click.echo(f"Unmarked '{key}' as sensitive.")
    except SensitiveError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@sensitive_group.command(name="check")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_sensitive_check(key, vault):
    """Check if a variable is marked sensitive."""
    if is_sensitive(vault, key):
        click.echo(f"'{key}' is sensitive.")
    else:
        click.echo(f"'{key}' is not sensitive.")


@sensitive_group.command(name="list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_sensitive_list(vault):
    """List all sensitive variables."""
    keys = list_sensitive(vault)
    if not keys:
        click.echo("No sensitive variables.")
    else:
        for k in keys:
            click.echo(k)
